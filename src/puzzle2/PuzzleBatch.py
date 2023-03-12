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
        self.name = kwargs.get("name", name)
        kwargs["log_directory"] = kwargs.get("log_directory", pz_env.get_log_directory())
        kwargs["name"] = self.name
        super(PuzzleBatch, self).__init__(**kwargs)

    def start(self, task_set_path, data_path, **kwargs):
        """
        task_set_type:
          multi: multi task set in one file
          single: single task set in one file(required: keys)
        """
        def _get(name, default, kwargs):
            if name in kwargs:
                return kwargs[name]
            elif name in os.environ:
                return os.environ[name]
            return default
        
        self.result_path = kwargs["result_path"]
        task_set_type = kwargs.get("task_set_type", "single") #multi task set in one file
        keys = kwargs.get("keys")
        app = kwargs.get("app", "")

        if "mayapy" in app:
            import maya.standalone
            maya.standalone.initialize()


        context_path = _get("PUZZLE_CONTEXT_PATH", "", kwargs)
        module_directory_path = kwargs.get("module_directory_path")

        if module_directory_path:
            for each in [l for l in module_directory_path.split(";") if l != ""]:
                if each not in sys.path:
                    sys.path.append(each)

        _, data = pz_config.read(data_path)
        _, pz_data = pz_config.read(task_set_path)

        if context_path != "":
            _, context_data = pz_config.read(context_path)
        else:
            context_data = None
        
        messages = []
        if task_set_type == "single":
            self.play(pz_data, data, context_data)
            messages.extend(self.logger.details.get_all())
        else:
            keys = [key.strip() for key in keys.split(";") if key != ""]

            # varidate
            for key in keys:
                if not key in pz_data:
                    raise Exception("key: {} is not found in task set".format(key))
            
            for key in keys:
                self.play(pz_data[key], data, context_data)
                messages.extend(self.logger.details.get_all())
                context_data = self.context

        self.close_event(app, messages, kwargs.get("close_app", True))
        return messages

    def close_event(self, app, messages, close_app):
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
        if "mayapy" in app:
            maya.standalone.uninitialize()

        if close_app:
            print("close")
            _close()

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
    like rez
    """
    addon = _get_addon(app, kwargs.get("launcher", False))
    print(addon)
    if not addon:
        return False
    
    kwargs["script_path"] = _get_script_path(kwargs.get("script_path", None), app)
    if not kwargs["script_path"]:
        return False

    if "start_signal" in kwargs:
        kwargs["start_signal"].emit()


    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    job_directory = "{}/{}".format(pz_env.get_temp_directory(subdir="puzzle/jobs"), now)

    job_directory = kwargs.get("job_directory", job_directory)

    if isinstance(kwargs.get("task_set"), list):
        kwargs["task_set_path"] = "{}/tasks.json".format(job_directory)
        pz_config.save(kwargs["task_set_path"], kwargs["task_set"])
        kwargs["task_set_type"] = "single"

    if isinstance(kwargs.get("data"), dict):
        kwargs["data_path"] = "{}/data.json".format(job_directory)
        pz_config.save(kwargs["data_path"], kwargs["data"])

    env_data = {
                "app": app,
                "puzzle_directory": kwargs["puzzle_directory"],
                "log_name": kwargs.get("log_name", "puzzle"),
                "log_directory": kwargs.get("log_directory", job_directory),
                "keys": kwargs.get("keys", ""),
                "script_path": kwargs["script_path"],
                "task_set": kwargs.get("task_set", False),
                "data": kwargs.get("data", False),
                "module_directory_path": kwargs.get("module_directory_path", False),
                "module_name": kwargs.get("module_name", False),
                "module_path": kwargs.get("module_path", False),
                "close_app": kwargs.get("close_app", False), 
                "sys_path": kwargs.get("sys_path", False)
                }

    if "context_path" in kwargs:
        env_data["context_path"] = kwargs["context_path"]

    env_data["result_path"] = kwargs.get("result_path", "{}/results.json".format(job_directory))
    
    env_copy = os.environ.copy()
    if hasattr(addon, "add_env"):
        for k, v in addon.add_env(**kwargs).items():
            env_data[k] = str(v)

    job_path = "{}/config.json".format(job_directory)
    pz_config.save(job_path, 
                  {"env": env_data, 
                   "data_path": kwargs["data_path"], 
                   "task_set_path": kwargs["task_set_path"]})

    env_copy["PUZZLE_JOB_PATH"] = job_path
    kwargs["job_path"] = job_path
    command = addon.get_command(**kwargs)

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

    if kwargs.get("bat_file"):
        if kwargs.get("bat_start", False):
            # return bat file path when bat_start flag is False
            return kwargs["bat_file"], job_directory
        else:
            command = kwargs["bat_file"]

    print("command          : {}".format(command))
    print("log directory    : {}".format(env_data["log_directory"]))
    print("config directory : {}".format(os.path.dirname(job_path)))
    print("")
    process = subprocess.Popen(command, 
                               env=env_copy, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               shell=False)
    
    results = process.communicate()

    if results[1] != "":
        with open("{}/std.txt".format(job_directory), "w") as f:
            f.write("{}\n{}".format(str(results[0]), str(results[1])))

    if "end_signal" in kwargs:
        kwargs["end_signal"].emit(kwargs)

    process.stdout.close()
    process.stderr.close()

    return command, job_directory
