from __future__ import print_function
from __future__ import unicode_literals

import os
import sys

import copy
import datetime
import traceback
import importlib
import subprocess

from . import PzLog
from . import pz_env as pz_env
from . import pz_config as pz_config
from .PzTask import PzTask

try:
    reload
except NameError:
    if hasattr(importlib, "reload"):
        # for py3.4+
        from importlib import reload


# RETURN_SUCCESS = 0
# RETURN_ERROR = 1
# RETURN_SKIPPED = 2
# RETURN_TASK_STOPPED = 3
# RETURN_PIECE_NOT_FOUND = 4

class Puzzle(object):
    def __init__(self, name="puzzle", **kwargs):
        """
        :type name: unicode

        :param name: log name
        :param kwargs[use_default_config]:  use_default_config
        :param logger:  if logger in kwargs, use it
        :param logger_level: default log level
        :param file_handler_level: override file handler level
        :param stream_handler_level: override stream handler level
        """
        self.break_ = False

        log_directory = kwargs.get("log_directory", pz_env.get_log_directory())
        self.name = name

        if "log_directory" in kwargs:
            del kwargs["log_directory"]

        if not kwargs.get("logger", False):
            self.Log = PzLog.PzLog(name=self.name,
                                   log_directory=log_directory,
                                   **kwargs)

            self.logger = self.Log.logger
            self.logger.uuid = 1000
        else:
            self.logger = kwargs["logger"]

        for handler in self.logger.handlers[::-1]:
            if hasattr(handler, "baseFilename"):
                self.logger.debug("baseFilename: {}".format(handler.baseFilename))

        task_directory = kwargs.get("task_directory", False)
        if task_directory:
            if task_directory not in sys.path:
                sys.path.append(task_directory)

    def execute_step(self, tasks, data, common, step):
        """
        when data is list, same tasks run for each.

        response: {return_code: int, data_globals: dict}

        return: {return_code: int, data_globals: dict}
        """
        if isinstance(data, list):
            flg = True
            if len(data) == 0 and len(common) > 0:
                data = [common]
            for i, d in enumerate(data):
                if self.break_:
                    # return_code = 3
                    self.logger.debug("break: {}".format(step))
                    # self.logger.details.update_code(return_code)
                    return

                self.execute_step(tasks=tasks,
                                data=d,
                                common=common,
                                step=step)
        else:
            """
            "common" is special keyword.
            we can use them everywhere
            """
            temp_common = copy.deepcopy(common)
            temp_common.update(data)
            data = temp_common

            for task in tasks:
                if self.break_:
                    self.logger.debug("break: {}".format(task.get("name")))
                    return

                if "step" in task:
                    if task["step"] not in data:
                        continue

                    self.execute_step(tasks=task["tasks"], 
                                      data=data.get(task["step"], {}), 
                                      common=common, 
                                      step=task["step"])

                else:
                    response = self.execute_task(task=task,
                                                data=data
                                                )

                    # Rest of the pipeline tasks will be skipped when
                    # 1. break_on_exceptions is set to TRUE
                    # 2. Exceptions (return flags 1,3,4,5) are caught through return_code
                    break_on_exceptions = task.get("break_on_exceptions", False)
                    if response.get("return_code", 0) not in [0, 2] and break_on_exceptions:
                        self.break_ = True
                        self.logger.debug("break on exceptions")
                        break

                    if response.get("break_on_conditions") == True:
                        self.break_ = True
                        self.logger.debug("break on conditions")
                        break

    def execute_task(self, task, data):
        module_path = task["module"]
        task.setdefault("name", module_path.split(".")[-1])

        # initialize details log
        self.logger.details.set_name(task["name"])
        self.logger.details.set_header(0, "successed: {}".format(task["name"]))
        if "comment" in task and task["comment"] != "":
            self.logger.details.add_detail(task["comment"])

        self.logger.info("module: {}".format(module_path))
        try:
            module_ = importlib.import_module(module_path)
            reload(module_)

        except BaseException:
            error = traceback.format_exc()
            self.logger.critical(error)
            self.logger.details.set_header(4, "import error: {}.py".format(module_path.split(".")[-1]))
            self.logger.details.add_detail(error)
            return {"return_code": 4}

        inp = datetime.datetime.now()

        try:
            response = self.execute(task, data, module_)

        except BaseException:
            error = traceback.format_exc()
            self.logger.critical(error)
            self.logger.details.add_detail(error)
            self.logger.details.set_header(4, "execute error: {}.py".format(module_path.split(".")[-1]))
            return {"return_code": 4}

        self.logger.info("task takes: {}\n".format(datetime.datetime.now() - inp))  # TODO: Check?
        if response is None:
            response = {"return_code": 0}

        self.logger.details.update_code(response["return_code"])
        return response

    def execute(self, task, data, module):
        task = PzTask(module=module,
                        task=task,
                        data=data,
                        context=self.context)

        response = task.execute()  # {"return_code": A, "data_globals": B}

        if "update_context" in response:
            for key, value in response["update_context"].items():
                if isinstance(value, dict):
                    self.context.setdefault(key, {})
                    self.context[key].update(value)
                # elif isinstance(value, list):
                #     self.context.setdefault(key, []).extend(value)
                else:
                    self.context[key] = value

        return response

    def play(self, steps, data_set, default_context={}):
        """
         --------------------
         response return_code
         --------------------
         0: Success
         1: Error
         2: Skipped
         3: Break
         4: Module import error/ traceback error
         5: Required key does not exist
        """
        def _append_sys_path(path):
            if os.path.normpath(path) not in [os.path.normpath(l) for l in sys.path]:
                sys.path.append(os.path.normpath(path))


        # initialize
        self.logger.details.clear()
        self.context = pz_env.get_env()
        self.context.setdefault("logger", self.logger)

        for k, v in (default_context or {}).items():
            self.context[k] = v

        self.break_ = False
        inp = datetime.datetime.now()
        order = [l["step"] for l in steps]
        self.logger.info("- tasks start: {} -\n".format(", ".join(order)))
        common = data_set.get("common", {})
        if steps[0]["step"] == "init":
            """
            this special step can override data inside process
            if you want to grab some thing from scene, you can use this.
            maybe this step will start from "open_file" task
            then "grab_something_from_scene" task for override data.
            different from data_globals is this step can override loop data
            and it is not possible from using default data_globals flow.

            WARNING:
                step data is list type.it will be replace for now.
                if you want to set specific key, use common key to make it happen.

            """
            now = datetime.datetime.now()
            self.logger.debug("- init start -")

            self.execute_step(tasks=steps[0]["tasks"],
                          data=data_set.get("init", {}),
                          common=common,
                          step="init")

            for key, value in self.context.items():
                if key.startswith("_") or key == "logger":
                    continue
                if key in data_set:
                    if isinstance(value, list):
                        data_set[key] = value
                    else:
                        data_set[key].update(value)
                else:
                    data_set[key] = value

            self.logger.info("- init takes: {} -\n\n".format(datetime.datetime.now() - now))
        common = data_set.get("common", {})

        for step in steps:
            step_name = step["step"]
            if step_name in ["init", "closure"]:
                continue

            if self.break_:
                self.logger.debug("break: {}".format(step_name))
                break

            [_append_sys_path(l) for l in step.get("sys_path", "").split(";") if l != ""]

            now = datetime.datetime.now()
            data_set.setdefault(step_name, {})
            self.logger.debug("- {} start - {}".format(step_name, step.get("comment", "")))

            self.execute_step(tasks=step["tasks"],
                          data=data_set[step_name],
                          common=common,
                          step=step_name)

            self.logger.info("- {} takes: {}-\n".format(step_name, datetime.datetime.now() - now))

        if steps[-1]["step"] == "closure":
            self.break_ = False
            self.logger.debug("- closure start - {}".format(steps[-1].get("comment", "")))
            now = datetime.datetime.now()
            self.execute_step(tasks=steps[-1]["tasks"],
                          data=data_set.get("closure", {}),
                          common=common,
                          step="closure")

            self.logger.info("-closure takes: {}-\n".format(datetime.datetime.now() - now))

        self.logger.info("- done: {} -\n\n".format(datetime.datetime.now() - inp))
