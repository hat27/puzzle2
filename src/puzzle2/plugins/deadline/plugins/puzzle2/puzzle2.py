#!/usr/bin/env python3
import os
import datetime
import json

from Deadline.Plugins import DeadlinePlugin, PluginType
from Deadline.Scripting import ClientUtils, RepositoryUtils

# puzzle2 imports (PluginPreLoad should have appended PuzzleDirectory/TaskDirectory to sys.path)
from puzzle2 import pz_env as _pz_env  # noqa: E402
from puzzle2 import pz_config as _pz_config  # noqa: E402


def GetDeadlinePlugin():
    return Puzzle2Plugin()


def CleanupDeadlinePlugin(deadlinePlugin):
    deadlinePlugin.Cleanup()


class Puzzle2Plugin(DeadlinePlugin):
    def __init__(self):
        super(Puzzle2Plugin, self).__init__()
        self.InitializeProcessCallback += self.InitializeProcess
        self.RenderExecutableCallback += self.RenderExecutable
        self.RenderArgumentCallback += self.RenderArgument

    def Cleanup(self):
        del self.InitializeProcessCallback
        del self.RenderExecutableCallback
        del self.RenderArgumentCallback

    def InitializeProcess(self):
        self.SingleFramesOnly = True
        self.PluginType = PluginType.Simple
        # Avoid creating .pyc / __pycache__ on workers
        self.SetEnvironmentVariable("PYTHONDONTWRITEBYTECODE", "1")

    # ---------------- Internal helpers ----------------
    def _build_job_config(self, app):
        """Create job directory and config.json for puzzle2 batch_kicker.
        Returns (job_directory, job_path, script_path).
        """
        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        job_root = self.GetConfigEntryWithDefault("JobDirectory", None)
        if not job_root:
            job_root = os.path.join(os.path.expanduser("~"), "puzzle2_jobs")
        job_directory = os.path.join(job_root, now)
        try:
            if not os.path.isdir(job_directory):
                os.makedirs(job_directory)
        except Exception:
            pass

        # Inputs from Plugin Info
        sys_path = self.GetPluginInfoEntryWithDefault("SysPath", "")
        module_dir = self.GetPluginInfoEntryWithDefault("ModulePath", "")
        task_path = self.GetPluginInfoEntryWithDefault("TaskPath", "")
        data_path = self.GetPluginInfoEntryWithDefault("DataPath", "")
        result_path = self.GetPluginInfoEntryWithDefault("ResultPath", os.path.join(job_directory, "results.json"))

        # Compute batch_kicker path inside puzzle2 package
        script_path = os.path.normpath(os.path.join(_pz_env.get_puzzle_path(), "batch_kicker.py"))

        env_data = {
            "app": app,
            "puzzle_directory": os.path.dirname(_pz_env.get_puzzle_path()),
            "log_name": "puzzle",
            "log_directory": job_directory.replace("\\", "/"),
            "keys": "",
            "script_path": script_path.replace("\\", "/"),
            "module_directory_path": module_dir.replace("\\", "/") if module_dir else False,
            "module_name": False,
            "module_path": False,
            "close_app": True,
            "sys_path": sys_path if sys_path else False,
        }
        env_data["result_path"] = result_path.replace("\\", "/")

        job_path = os.path.join(job_directory, "config.json")
        payload = {
            "env": env_data,
            "data_path": data_path.replace("\\", "/") if data_path else None,
            "task_set_path": task_path.replace("\\", "/") if task_path else None,
            "context_path": None,
        }
        _pz_config.save(job_path.replace("\\", "/"), payload, "puzzle2", "deadline")
        return job_directory, job_path, script_path

    def _get_app_plugin_name_and_keys(self, app):
        """Map puzzle2 'app' to Deadline Application Plugin and the config key patterns.
        Returns (pluginName, keyBase, altKeyBase) where keyBase is typical 'RenderExecutable'.
        altKeyBase may be an alternative like 'HythonExecutable'.
        """
        app = (app or "").lower()
        if app in ("maya", "mayabatch", "mayaexe"):
            return ("MayaBatch", "RenderExecutable", None)
        if app in ("3dsmax", "3dsmaxpy"):
            return ("3dsmax", "RenderExecutable", None)
        if app in ("houdini", "hython"):
            return ("Houdini", "RenderExecutable", "HythonExecutable")
        # For python-runner variants (mayapy/mobupy), we usually keep addon-provided exe
        return (None, None, None)

    def _resolve_exe_from_app_plugin(self, app, version):
        """Try to read the executable path from Deadline's Application Plugin config.
        Supports version-specific keys like RenderExecutable_2024.
        """
        pluginName, keyBase, altKeyBase = self._get_app_plugin_name_and_keys(app)
        if not pluginName or not keyBase:
            return None
        try:
            cfg = RepositoryUtils.GetPluginConfig(pluginName, None)
        except Exception:
            return None

        # Version-specific key takes precedence
        candidates = []
        if version:
            candidates.append("%s_%s" % (keyBase, str(version)))
            if altKeyBase:
                candidates.append("%s_%s" % (altKeyBase, str(version)))
        candidates.append(keyBase)
        if altKeyBase:
            candidates.append(altKeyBase)

        for key in candidates:
            try:
                exe = cfg.GetConfigEntryWithDefault(key, None)
            except Exception:
                exe = None
            if exe and os.path.isfile(exe):
                return exe
        return None

    def _split_command(self, command):
        """Naive split of a quoted command string into (exe, args).
        Assumes Windows-style quoting for the first token.
        """
        cmd = command.strip()
        exe = cmd
        args = ""
        if not cmd:
            return "", ""
        if cmd[0] == '"':
            # find closing quote
            idx = cmd.find('"', 1)
            while idx != -1 and idx + 1 < len(cmd) and cmd[idx + 1] != ' ':
                idx = cmd.find('"', idx + 1)
            if idx != -1:
                exe = cmd[1:idx]
                args = cmd[idx + 1:].lstrip()
            else:
                exe = cmd.strip('"')
                args = ""
        else:
            parts = cmd.split(" ", 1)
            exe = parts[0]
            args = parts[1] if len(parts) > 1 else ""
        return exe, args

    # ---------------- Deadline callbacks ----------------
    def RenderExecutable(self):
        app = self.GetPluginInfoEntryWithDefault("App", "")
        version = self.GetPluginInfoEntryWithDefault("Version", "")

        # Prepare job config and environment for batch_kicker
        job_directory, job_path, script_path = self._build_job_config(app)
        self.SetEnvironmentVariable("PUZZLE_JOB_PATH", job_path.replace("\\", "/"))

        # Build command via addon first, then overlay exe from App Plugin if available
        try:
            addon = __import__("puzzle2.addons.%s.integration" % app, fromlist=["integration"])  # type: ignore
        except Exception as e:
            self.FailRender("Failed to import addon for app '%s': %s" % (app, e))
            return None

        # Minimal kwargs for command construction
        kwargs = {
            "job_path": job_path.replace("\\", "/"),
            "version": version,
            "script_path": script_path.replace("\\", "/"),
        }
        command = addon.get_command(**kwargs)
        if not command:
            self.FailRender("Failed to build command for app '%s' version '%s'" % (app, version))
            return None

        exe_from_cmd, args = self._split_command(command)
        exe_from_app = self._resolve_exe_from_app_plugin(app, version)

        # Decide which executable to use
        use_app_plugin_path = self.GetConfigEntryWithDefault("UseAppPluginPath", "True")
        use_app_plugin_path = str(use_app_plugin_path).strip().lower() in ("true", "1", "yes", "on")
        if use_app_plugin_path and exe_from_app:
            self._cached_args = args
            return exe_from_app
        # fallback to addon-provided exe
        self._cached_args = args
        return exe_from_cmd

    def RenderArgument(self):
        # Use cached args from RenderExecutable
        return self._cached_args if hasattr(self, "_cached_args") else ""
