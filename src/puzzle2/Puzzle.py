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

    def close_event(self):
        def _force_close():
            flg = True
            message = "force close"

            try:
                import maya.cmds as cmds
                import maya.mel as mel
                mode = "maya"
            except BaseException:
                mode = "win"
            if mode == "maya":
                try:
                    mel.eval('scriptJob -cf "busy" "quit -f -ec 0";')
                    message = u"file app close: maya"
                    flg = True
                except BaseException:
                    message = u"file app close failed: maya"
                    flg = False

            return flg, message

        message_path = os.environ.get("PUZZLE_MESSAGE_OUTPUT", False)
        if message_path:
            pz_config.save(message_path, self.logger.details.get_all())

        if os.environ.get("PUZZLE_CLOSE_APP", False):
            _force_close()

    def play(self, tasks, data_set):
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
        def _execute_step(tasks, data, common, step):
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
                
                    _execute_step(tasks=tasks,
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

                    response = _execute_task(task=task,
                                             data=data
                                             )

                    # Rest of the pipeline tasks will be skipped when
                    # 1. break_on_exceptions is set to TRUE
                    # 2. Exceptions (return flags 1,3,4,5) are caught through return_code
                    break_on_exceptions = task.get("break_on_exceptions", False)
                    if response.get("return_code", 0) not in [0, 2] and break_on_exceptions:
                        self.break_ = True
                        self.logger.debug("set break: True")
                        break

        def _execute_task(task, data):
            def _execute(task, data, module):
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
                        elif isinstance(value, list):
                            self.context.setdefault(key, []).extend(value)
                        else:
                            self.context[key] = value

                return response

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
                response = _execute(task, data, module_)

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

        # initialize
        self.logger.details.clear()
        self.context = pz_env.get_env()
        self.context["logger"] = self.logger
        self.break_ = False

        inp = datetime.datetime.now()
        order = [l["step"] for l in tasks]
        self.logger.info("- tasks start: {} -\n".format(", ".join(order)))
        common = data_set.get("common", {})
        if tasks[0]["step"] == "init":
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

            _execute_step(tasks=tasks[0]["tasks"],
                          data=data_set.get("init", {}),
                          common=common,
                          step="init")

            for key, value in self.context.items():
                if key in data_set:
                    if isinstance(data_set[key], list):
                        data_set[key] = value
                    else:
                        data_set[key].update(value)
                else:
                    data_set[key] = value
            
            self.logger.info("- init takes: {} -\n\n".format(datetime.datetime.now() - now))

        for task in tasks:
            step = task["step"]
            if step in ["init", "closure"]:
                continue

            if self.break_:
                self.logger.debug("break: {}".format(step))
                break

            now = datetime.datetime.now()
            data_set.setdefault(step, {})
            self.logger.debug("- {} start -".format(step))

            _execute_step(tasks=task["tasks"],
                          data=data_set[step],
                          common=common,
                          step=step)
            
            self.logger.info("- {} takes: {} -\n\n".format(step, datetime.datetime.now() - now))

        if tasks[-1]["step"] == "closure":
            self.break_ = False
            self.logger.debug("- closure start -")
            now = datetime.datetime.now()
            _execute_step(tasks=tasks[-1]["tasks"],
                          data=data_set.get("closure", {}),
                          common=common,
                          step="closure")
            
            self.logger.info("-closure takes: {}-\n\n".format(datetime.datetime.now() - now))

        self.logger.info("- done: {} -".format(datetime.datetime.now() - inp))
        self.close_event()
