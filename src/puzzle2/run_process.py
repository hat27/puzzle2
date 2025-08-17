
import os
import datetime
import traceback
import subprocess
import importlib

from . import pz_env as pz_env
from . import pz_config as pz_config
from .PzLog import PzLog

try:
    reload
except NameError:
    if hasattr(importlib, "reload"):
        # for py3.4+
        from importlib import reload


def run_process(app, **kwargs):
    """
    app like: maya, mayapy, motionbuilder, mobupy, 3dsmax, 3dsmaxpy
    version like: 2016, 2017, 2018, 2019+

    job_directory: job file to give to batch_kicker.py
    """
    def _get_script_path(script, app):
        if script is None:
            script_root = pz_env.get_puzzle_path()
            script_path = "{}/addons/{}/batch_kicker.py".format(script_root, app)
            if not os.path.exists(script_path):
                script_path = "{}/batch_kicker.py".format(script_root)

        return os.path.normpath(script_path) if os.path.exists(script_path) else False
    
    def _get_addon(app, launcher):
        """
        check customs addon then check defaults
        """
        if launcher:
            app = launcher
        script_root = pz_env.get_puzzle_path()
        path = "{}/addons/customs/{}".format(script_root, app)
        if os.path.exists(path):
            addon_path = "puzzle2.addons.customs.{}.integration".format(app)
        else:
            # Fallback to the built-in addon path
            addon_path = "puzzle2.addons.{}.integration".format(app)

        try:
            addon = importlib.import_module(addon_path)
            try:
                # Reload only if it's a real module; tolerate monkeypatched objects
                reload(addon)
            except Exception:
                pass
            return addon

        except ImportError:
            # print(traceback.format_exc())
            return False

    kwargs["app"] = app
    kwargs.setdefault("puzzle_directory", os.path.dirname(pz_env.get_puzzle_path()))
    kwargs.setdefault("log_name", "puzzle")

    """
    like rez
    """
    addon = _get_addon(app, kwargs.get("launcher", False))
    if not addon:
        # Logging will be initialized later once job_directory is known; early exit here
        return False, False
    kwargs["script_path"] = _get_script_path(kwargs.get("script_path", None), app)
    if not kwargs["script_path"]:
        return False, False

    if "start_signal" in kwargs:
        kwargs["start_signal"].emit()

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    job_directory = "{}/{}".format(pz_env.get_temp_directory(subdir="puzzle/jobs"), now)
    job_directory = kwargs.get("job_directory", job_directory)
    # Ensure the job directory exists before writing artifacts
    if not os.path.exists(job_directory):
        os.makedirs(job_directory, exist_ok=True)

    # Initialize a launcher-scoped logger writing alongside job logs
    log_directory = kwargs.get("log_directory", job_directory)
    base_log_name = kwargs.get("log_name", "puzzle")
    launcher_log_name = f"{base_log_name}_launcher"
    _Log = PzLog(name=launcher_log_name, log_directory=log_directory, new=True)
    _logger = _Log.logger
    _logger.info("run_process: start app=%s", app)

    if isinstance(kwargs.get("task_set"), list):
        kwargs["task_set_path"] = "{}/tasks.json".format(job_directory)
        pz_config.save(kwargs["task_set_path"], kwargs["task_set"])
        _logger.debug("wrote task_set to %s", kwargs["task_set_path"])
        kwargs["task_set_type"] = "single"

    if isinstance(kwargs.get("data_set"), dict):
        kwargs["data_path"] = "{}/data.json".format(job_directory)
        pz_config.save(kwargs["data_path"], kwargs["data_set"])
        _logger.debug("wrote data_set to %s", kwargs["data_path"])
    
    if isinstance(kwargs.get("context"), dict):
        kwargs["context_path"] = "{}/context.json".format(job_directory)
        keys = list(kwargs["context"].keys())
        for key in keys:
            if key.startswith("_"):
                del kwargs["context"][key]
            elif key == "logger":
                del kwargs["context"][key]
        pz_config.save(kwargs["context_path"], kwargs["context"])
        _logger.debug("wrote context to %s", kwargs["context_path"])
    if "data_path" not in kwargs or "task_set_path" not in kwargs:
        _logger.critical("data_path or task_set_path missing in kwargs")
        raise ValueError("data_path or task_set_path is not defined")

    env_data = {
                "app": app,
                "puzzle_directory": kwargs["puzzle_directory"],
                "log_name": kwargs.get("log_name", "puzzle"),
                "log_directory": kwargs.get("log_directory", job_directory),
                "keys": kwargs.get("keys", ""),
                "script_path": kwargs["script_path"],
                "task_set": kwargs.get("task_set", False),
                "data_set": kwargs.get("data_set", False),
                "module_directory_path": kwargs.get("module_directory_path", False),
                "module_name": kwargs.get("module_name", False),
                "module_path": kwargs.get("module_path", False),
                "close_app": kwargs.get("close_app", False), 
                "sys_path": kwargs.get("sys_path", False)
                }

    env_data["result_path"] = kwargs.get("result_path", "{}/results.json".format(job_directory))
    
    env_copy = os.environ.copy()
    # Avoid creating .pyc / __pycache__ in spawned processes
    env_copy["PYTHONDONTWRITEBYTECODE"] = "1"
    if hasattr(addon, "add_env"):
        for k, v in addon.add_env(**kwargs).items():
            env_data[k] = str(v)

    job_path = "{}/config.json".format(job_directory)
    pz_config.save(job_path, 
                  {"env": env_data, 
                   "data_path": kwargs["data_path"], 
                   "task_set_path": kwargs["task_set_path"], 
                   "context_path": kwargs.get("context_path", None)})
    _logger.info("job config written: %s", job_path)

    env_copy["PUZZLE_JOB_PATH"] = job_path
    kwargs["job_path"] = job_path
    command = addon.get_command(**kwargs)
    if not command:
        _logger.error("Failed to resolve command for app=%s version=%s", app, kwargs.get("version", ""))
        return False, job_directory
    _logger.debug("BATCH COMMAND %s", command)
    if kwargs.get("bat_file"):
        bat = ""
        for k, v in env_copy.items():
            if k.startswith("PUZZLE_"):
                bat += "SET {}={}\n".format(k, v)

        bat += command

        # create bat file
        if not os.path.exists(os.path.dirname(kwargs["bat_file"])):
            os.makedirs(os.path.dirname(kwargs["bat_file"]))

        with open(kwargs["bat_file"], "w") as f:
            f.write(bat)
        _logger.info("bat file created: %s", kwargs["bat_file"])

    if kwargs.get("bat_start"):
        if kwargs.get("bat_start", False):
            # return bat file path when bat_start flag is False
            return kwargs["bat_file"], job_directory
        else:
            command = kwargs["bat_file"]
    _logger.info("command: %s", command)
    _logger.info("log directory: %s", env_data["log_directory"]) 
    _logger.info("config directory: %s", os.path.dirname(job_path))
    process = subprocess.Popen(command,
                               env=env_copy,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=False)
    
    results = process.communicate()

    if results[1]:
        with open("{}/std.txt".format(job_directory), "w") as f:
            f.write("{}\n{}".format(str(results[0]), str(results[1])))
        try:
            _logger.error("stderr captured; see std.txt in job directory")
        except Exception:
            pass

    if "end_signal" in kwargs:
        kwargs["end_signal"].emit(kwargs)

    process.stdout.close()
    process.stderr.close()

    try:
        _logger.info("run_process: done (returncode=%s)", getattr(process, "returncode", None))
    except Exception:
        pass
    return command, job_directory
