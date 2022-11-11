from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import datetime
import traceback
import subprocess
import importlib

from . import Puzzle
from . import pz_env as pz_env
from . import pz_config as pz_config

try:
    reload
except BaseException:
    if hasattr(importlib, "reload"):
        # for py3.4+
        from importlib import reload


class PuzzleBatch(Puzzle.Puzzle):
    def __init__(self, name="puzzle", **kwargs):
        log_directory = os.environ.get("PUZZLE_LOGGER_DIRECTORY", pz_env.get_log_directory())
        self.name = os.environ.get("PUZZLE_LOGGER_NAME", name)
        kwargs["log_directory"] = log_directory
        kwargs["name"] = self.name
        super(PuzzleBatch, self).__init__(**kwargs)

        self.result_path = os.environ.get("PUZZLE_RESULT", False)

    def start(self):
        pz_path = os.environ["PUZZLE_ALL_TASKS_PATH"]
        keys = os.environ["PUZZLE_TASK_KEYS"]
        data_path = os.environ["PUZZLE_DATA_PATH"]
        app = os.environ["PUZZLE_APP"]
        context_path = os.environ.get("PUZZLE_CONTEXT_PATH", "")
        tasks_directory = os.environ.get("PUZZLE_MODULE_DIRECTORY", False)
        if tasks_directory:
            if tasks_directory not in sys.path:
                sys.path.append(tasks_directory)

        info, data = pz_config.read(data_path)
        pz_info, pz_data = pz_config.read(pz_path)

        if context_path != "":
            pass_info, context_data = pz_config.read(context_path)
        else:
            context_data = None
        keys = [key.strip() for key in keys.split(";") if key != ""]
        messages = []
        for key in keys:
            self.play(pz_data[key], data, context_data)
            messages.extend(self.logger.details.get_all())
            context_data = self.context

        self.close_event(app, messages)
        return messages

    def close_event(self, app, messages):
        def _close():
            flg = True

            try:
                addon = importlib.import_module("puzzle2.addons.{}.integration".format(app))
                reload(addon)
            except ImportError:
                print(traceback.format_exc())
                return False
            
            if hasattr(addon, "close_event"):
                flg = addon.close_event()

            return flg

        if self.result_path:
            pz_config.save(self.result_path, messages)
        
        if os.environ.get("PUZZLE_CLOSE_APP", "False") == "True":
            print("close")
            _close()

def run_process(app, **kwargs):
    """
    app: maya, mayapy, motionbuilder, mobupy, 3dsmax, 3dsmaxpy
    version: 2016, 2017, 2018, 2019+
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
        addon_path = "puzzle2.addons.{}.integration".format(app)

        try:
            addon = importlib.import_module(addon_path)
            reload(addon)
            return addon

        except ImportError:
            print(traceback.format_exc())
            return False

    kwargs["app"] = app
    kwargs.setdefault("puzzle_directory", os.path.dirname(pz_env.get_puzzle_path()))
    kwargs.setdefault("log_name", "puzzle")

    """
    like rez, ecosystem
    """
    addon = _get_addon(app, kwargs.get("launcher", False))
    if not addon:
        return False
    
    kwargs["script_path"] = _get_script_path(kwargs.get("script_path", None), app)
    if not kwargs["script_path"]:
        return False

    if "start_signal" in kwargs:
        kwargs["start_signal"].emit()

    command = addon.get_command(**kwargs)

    now = datetime.datetime.now().strftime("%H%M%S")
    if kwargs.get("tasks", list):
        kwargs["piece_path"] = "{}/{}_tasks.json".format(pz_env.get_temp_directory(subdir="puzzle/tasks"), now)
        pz_config.save(kwargs["piece_path"], kwargs["tasks"])

    if kwargs.get("data", dict):
        kwargs["data_path"] = "{}/{}_data.json".format(pz_env.get_temp_directory(subdir="puzzle/data"), now)
        pz_config.save(kwargs["data_path"], kwargs["data"])

    env_copy = os.environ.copy()
    env_copy["PUZZLE_DATA_PATH"] = str(kwargs["data_path"])
    env_copy["PUZZLE_ALL_TASKS_PATH"] = str(kwargs["piece_path"])
    env_copy["PUZZLE_LOGGER_NAME"] = str(kwargs.get("log_name", "puzzle"))
    env_copy["PUZZLE_LOGGER_DIRECTORY"] = str(kwargs.get("log_directory", False))
    env_copy["PUZZLE_TASK_KEYS"] = str(kwargs["keys"])
    env_copy["PUZZLE_APP"] = str(app)
    env_copy["PUZZLE_DIRECTORY"] = str(kwargs["puzzle_directory"])
    env_copy["PUZZLE_MODULE_DIRECTORY"] = str(kwargs["module_directory_path"])
    env_copy["PUZZLE_CLOSE_APP"] = str(kwargs["close_app"])
    
    if hasattr(addon, "add_env"):
        for k, v in addon.add_env(**kwargs).items():
            env_copy[k] = str(v)

    if "context_path" in kwargs:
        env_copy["PUZZLE_CONTEXT_PATH"] = str(kwargs["context_path"])

    if "result" in kwargs:
        env_copy["PUZZLE_RESULT"] = str(kwargs["result"])

    if "standalone_python" in kwargs:
        env_copy["PUZZLE_STANDALONE_PYTHON"] = str(kwargs["standalone_python"])

    if not kwargs.get("bat_file"):
        process = subprocess.Popen(command, env=env_copy, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        results = process.communicate()
        # for r in results:
        #     try:
        #         print(r)
        #     except BaseException:
        #         print("failed")

        if "end_signal" in kwargs:
            kwargs["end_signal"].emit(kwargs)
        process.stdout.close()
        process.stderr.close()

    else:
        bat = ""
        for k, v in env_copy.items():
            if k.startswith("PUZZLE_"):
                bat += "SET {}={}\n".format(k, v)

        bat += command

        if not os.path.exists(os.path.dirname(kwargs["bat_file"])):
            os.makedirs(os.path.dirname(kwargs["bat_file"]))
        tx = open(kwargs["bat_file"], "w")
        tx.write(bat)
        tx.close()

        if kwargs.get("bat_start", False):
            process = subprocess.Popen(kwargs["bat_file"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            results = process.communicate()
            # for r in results:
            #     try:
            #         print(r)
            #     except BaseException:
            #         print("failed")

            if "end_signal" in kwargs:
                kwargs["end_signal"].emit(kwargs)
            process.stdout.close()
            process.stderr.close()
    return command
