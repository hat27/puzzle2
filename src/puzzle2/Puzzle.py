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
    def __init__(self, name="puzzle", file_mode=False, **kwargs):
        """
        :type name: unicode
        :type file_mode: bool

        :param name: log name
        :param file_mode:  use environ to run
        :param kwargs[use_default_config]:  use_default_config
        :param logger:  if logger in kwargs, use it
        :param logger_level: default log level
        :param file_handler_level: override file handler level
        :param stream_handler_level: override stream handler level
        """
        self.file_mode = file_mode
        self.break_ = False
        self.data_piped = {}
        if self.file_mode:
            log_directory = os.environ.get("PUZZLE_LOGGER_DIRECTORY", pz_env.get_log_directory())
            self.name = os.environ.get("PUZZLE_LOGGER_NAME", name)
        else:
            log_directory = kwargs.get("log_directory", pz_env.get_log_directory())
            self.name = name

        if "log_directory" in kwargs:
            del kwargs["log_directory"]

        self.order = kwargs.get("order", ["primary", "main", "post"])

        if not kwargs.get("logger", False):
            self.Log = PzLog.PzLog(name=self.name,
                                   log_directory=log_directory,
                                   **kwargs)

            self.logger = self.Log.logger
        else:
            self.logger = kwargs["logger"]

        for handler in self.logger.handlers[::-1]:
            if hasattr(handler, "baseFilename"):
                self.logger.debug("baseFilename: {}".format(handler.baseFilename))

        task_directory = kwargs.get("task_directory", False)
        if task_directory:
            if task_directory not in sys.path:
                sys.path.append(task_directory)

        if self.file_mode:
            self.play_as_file_mode()
            self.logger.debug("puzzle: file mode")
        else:
            self.logger.debug("puzzle: normal mode")

    @staticmethod
    def is_file_mode():
        if os.environ.get("PUZZLE_FILE_MODE", False):
            return True
        return False

    def set_order(self, order):
        self.order = order

    def play_as_file_mode(self):
        pz_path = os.environ["ALL_TASKS_PATH"]
        keys = os.environ["TASK_KEYS"]
        data_path = os.environ["PUZZLE_DATA_PATH"]
        pipe_path = os.environ.get("PUZZLE_PIPE_PATH", "")
        pieces_directory = os.environ.get("PUZZLE_TASKS", False)
        if pieces_directory:
            if pieces_directory not in sys.path:
                sys.path.append(pieces_directory)

        info, data = pz_config.read(data_path)
        pz_info, pz_data = pz_config.read(pz_path)

        if pipe_path != "":
            pass_info, data_piped = pz_config.read(pipe_path)
        else:
            data_piped = None
        keys = [l.strip() for l in keys.split(";") if l != ""]
        messages = []
        for key in keys:
            message = self.play(pz_data[key],
                                data,
                                data_piped)

            messages.extend(message)

        for message in messages:
            if not message[0]:
                self.close_event(messages)
                break

        return messages

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
         3: Task stopped
         4: PIECE_NAME not found
        """
        def _execute_step(tasks, data, common, step, response):
            """
            when data is list, same tasks run for each.
            """
            if isinstance(data, list):
                flg = True
                if len(data) == 0 and len(common) > 0:
                    data = [common]

                for i, d in enumerate(data):
                    if self.break_:
                        response["return_code"] = 3
                        return response

                    response = _execute_step(tasks=tasks,
                                             data=d,
                                             common=common,
                                             step=step,
                                             response=response)

                return response
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
                        return response

                    response = _execute_task(task=task,
                                             data=data,
                                             data_piped=response["data_piped"])

                    if response["return_code"] and task.get("force"):  # TODO: check
                        self.break_ = True
                        return response

                return response

        def _execute_task(task, data, data_piped):
            def _execute(task, data, data_piped, module, logger):
                if not logger:
                    logger = self.logger
                task = PzTask(module=module,
                              task=task,
                              data=data,
                              data_piped=data_piped,
                              logger=logger)

                response = task.execute()  # {"return_code": A, "data_piped": B}
                return response

            module_path = task["module"]
            try:
                self.logger.debug(module_path)
                module_ = importlib.import_module(module_path)
                reload(module_)
                if hasattr(module_, "PIECE_NAME"):
                    response = _execute(task, data, data_piped, module_, self.logger)
                else:
                    return {"return_code": 4, "data_piped": data_piped}

                inp = datetime.datetime.now()
                # if mod.skip:
                #     return 2, data_piped, "skipped", detail

                self.logger.debug("{}\n".format(datetime.datetime.now() - inp))
                return response

            except BaseException:
                self.logger.debug(traceback.format_exc())
                self.logger.details.append({"details": traceback.format_exc(),
                                            "name": task.get("name"),
                                            "header": "task failed by error",
                                            "return_code": 1,
                                            "comment": task.get("comment")})
                return {"return_code": 1, "data_piped": data_piped}

        """
        break when flg is not 1 and force in task settings
        """
        self.logger.details.clear()
        self.break_ = False
        inp = datetime.datetime.now()
        self.logger.debug("start\n")
        common = data_set.get("common", {})
        for step in self.order:
            if step not in tasks:
                self.logger.debug("")
                continue

            data_set.setdefault(step, {})
            self.logger.debug("{}:".format(step))
            response = {"return_code": 0, "data_piped": self.data_piped}
            self.data_piped = _execute_step(tasks=tasks[step],
                                            data=data_set[step],
                                            common=common,
                                            step=step,
                                            response=response)

        if "finally" in tasks:
            self.break_ = False
            self.data_piped = _execute_step(tasks=tasks["finally"],
                                            data={},
                                            common=common,
                                            step="finally",
                                            response=response)

        self.logger.debug("takes: {}".format(datetime.datetime.now() - inp))
        self.close_event()


def execute_command(app, **kwargs):
    def _get_script(script_):
        if script_ is None:
            script_ = os.path.dirname(__file__)
            script_ = "{}/pz_batch.py".format(script_.replace("\\", "/"))
        else:
            script_ = script_.replace("/", "\\")

        return script_

    if "start_signal" in kwargs:
        kwargs["start_signal"].emit()

    script = _get_script(kwargs.get("script", None))
    if app.endswith("mayapy.exe"):
        cmd = r'"{}" "{}"'.format(app.replace("/", "\\"), script.replace("/", "\\"))

    elif app.endswith("mayabatch.exe") or app.endswith("maya.exe"):
        cmd = r'''"{}" -command "python(\\"execfile('{}')\\");"'''.format(app, script)

    elif app.endswith("motionbuilder.exe"):
        cmd = r'"{}" -suspendMessages -g 50 50 "{}"'.format(app.replace("/", "\\"), script.replace("/", "\\"))

    elif app.endswith("3dsmax.exe"):
        cmd = r'"{}" -U PythonHost {}'.format(app.replace("/", "\\"), script.replace("/", "\\"))

    elif app.endswith("3dsmaxpy.exe"):
        cmd = r'"{}" "{}"'.format(app.replace("/", "\\"), script.replace("/", "\\"))

    elif app.endswith("maya.exe"):
        sys_path = kwargs.get("sys_path", False)
        if not sys_path:
            return False
        sys_path = sys_path.replace("\\", "/")
        log_name = kwargs.get("log_name", "puzzle")

        cmd = '"{}" -command '.format(app)
        cmd += '"python(\\\"import sys;import os;sys.path.append(\\\\\\"{}\\\\\\");'.format(sys_path)
        cmd += 'from puzzle.Puzzle import Puzzle;x=Puzzle(\\\\\\"{}\\\\\\", '.format(log_name)
        cmd += 'file_mode=True)\\\");"'
    else:
        print("return: False")
        return False
    if kwargs.get("bat_file", False):
        bat = "SET PUZZLE_FILE_MODE=True\n"
        bat += "SET PUZZLE_DATA_PATH={}\n".format(str(kwargs["data_path"]))
        bat += "SET ALL_TASKS_PATH={}\n".format(str(kwargs["piece_path"]))
        bat += "SET PUZZLE_LOGGER_NAME={}\n".format(str(kwargs["log_name"]))
        bat += "SET PUZZLE_LOGGER_DIRECTORY={}\n".format(str(kwargs.get("log_directory", False)))
        bat += "SET TASK_KEYS={}\n".format(str(kwargs["keys"]))
        bat += "SET PUZZLE_APP={}\n".format(str(app))
        bat += "SET PUZZLE_PATH={}\n".format(str(kwargs["sys_path"]))
        bat += "SET PUZZLE_TASKS={}\n".format(str(kwargs["task_path"]))
        bat += "SET PUZZLE_MESSAGE_OUTPUT={}\n".format(str(kwargs["message_output"]))
        if "pipe_path" in kwargs:
            bat += "SET PUZZLE_PIPE_PATH={}\n".format(str(kwargs["pipe_path"]))

        if "order" in kwargs:
            bat += "SET PUZZLE_ORDER={}\n".format(str(kwargs["order"]))

        if "result" in kwargs:
            bat += "SET PUZZLE_RESULT={}\n".format(str(kwargs["result"]))

        bat += "SET PUZZLE_CLOSE_APP=True\n"
        if "standalone_python" in kwargs:
            bat += "SET PUZZLE_STANDALONE_PYTHON={}\n".format(str(kwargs["standalone_python"]))
        bat += cmd

        if not os.path.exists(os.path.dirname(kwargs["bat_file"])):
            os.makedirs(os.path.dirname(kwargs["bat_file"]))
        tx = open(kwargs["bat_file"], "w")
        tx.write(bat)
        tx.close()

        if kwargs.get("bat_start", False):
            res = subprocess.Popen(kwargs["bat_file"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False).communicate()
            for r in res:
                print(r)

    else:
        env_copy = os.environ.copy()
        env_copy["PUZZLE_FILE_MODE"] = "True"
        env_copy["PUZZLE_DATA_PATH"] = str(kwargs["data_path"])
        env_copy["ALL_TASKS_PATH"] = str(kwargs["piece_path"])
        env_copy["PUZZLE_LOGGER_NAME"] = str(kwargs["log_name"])
        env_copy["PUZZLE_LOGGER_DIRECTORY"] = str(kwargs.get("log_directory", False))
        env_copy["TASK_KEYS"] = str(kwargs["keys"])
        env_copy["PUZZLE_APP"] = str(app)
        env_copy["PUZZLE_PATH"] = str(kwargs["sys_path"])
        env_copy["PUZZLE_TASKS"] = str(kwargs["task_path"])
        env_copy["PUZZLE_MESSAGE_OUTPUT"] = str(kwargs["message_output"])
        if "pipe_path" in kwargs:
            env_copy["PUZZLE_PIPE_PATH"] = str(kwargs["pipe_path"])

        if "order" in kwargs:
            env_copy["PUZZLE_ORDER"] = str(kwargs["order"])

        if "result" in kwargs:
            env_copy["PUZZLE_RESULT"] = str(kwargs["result"])

        env_copy["PUZZLE_CLOSE_APP"] = "True"
        if "standalone_python" in kwargs:
            env_copy["PUZZLE_STANDALONE_PYTHON"] = str(kwargs["standalone_python"])

        res = subprocess.Popen(cmd, env=env_copy, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False).communicate()
        for r in res:
            try:
                print(r)
            except BaseException:
                print("failed")

    if "end_signal" in kwargs:
        kwargs["end_signal"].emit(kwargs)

    return cmd
