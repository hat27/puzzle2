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
from . import Piece

try:
    reload
except NameError:
    if hasattr(importlib, "reload"):
        # for py3.4+
        from importlib import reload


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

        pieces_directory = kwargs.get("pieces_directory", False)
        if pieces_directory:
            if pieces_directory not in sys.path:
                sys.path.append(pieces_directory)

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

    def force_close(self):
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

    def play_as_file_mode(self):
        pz_path = os.environ["ALL_PIECES_PATH"]
        keys = os.environ["PIECES_KEYS"]
        data_path = os.environ["PUZZLE_DATA_PATH"]
        pass_path = os.environ.get("PUZZLE_PASS_PATH", "")
        pieces_directory = os.environ.get("PUZZLE_TASKS", False)
        if pieces_directory:
            if pieces_directory not in sys.path:
                sys.path.append(pieces_directory)

        info, data = pz_config.read(data_path)
        pz_info, pz_data = pz_config.read(pz_path)

        if pass_path != "":
            pass_info, data_piped = pz_config.read(pass_path)
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

    def close_event(self, messages):
        message_path = os.environ.get("PUZZLE_MESSAGE_OUTPUT", False)
        if message_path:
            pz_config.save(message_path, messages)

        if os.environ.get("PUZZLE_CLOSE_APP", False):
            self.force_close()

    def play(self, pieces, data, data_piped):
        """
         1: successed
         0: failed
        -1: skipped
        -2: task stopped
        -3: piece name not exists
        """
        def _execute_task(task_settings, task_data, data_piped):
            def _execute(task_settings, task_data, data_piped, module, logger):
                if not logger:
                    logger = self.logger
                piece = Piece.Piece(module=module,
                                    settings=task_settings,
                                    data=task_data,
                                    data_piped=data_piped,
                                    logger=logger)

                data_piped = piece.execute()
                return piece.result_type, piece.header, piece.details, data_piped

            task_name = task_settings["module"]
            header = ""
            detail = ""
            try:
                self.logger.debug(task_name)
                mod = importlib.import_module(task_name)
                reload(mod)
                if hasattr(mod, "PIECE_NAME"):
                    result_type, header, details, data_piped = _execute(task_settings, task_data, data_piped, mod, self.logger)
                else:
                    return -3, data_piped, header, detail

                inp = datetime.datetime.now()
                # if mod.skip:
                #     return -1, data_piped, "skipped", detail

                self.logger.debug("{}\n".format(datetime.datetime.now() - inp))
                return result_type, data_piped, header, details

            except BaseException:
                self.logger.debug(traceback.format_exc())
                return 0, data_piped, header, traceback.format_exc()

        def _execute_step(_task_settings, _task_data, _common, _step, _data_piped):
            if isinstance(_task_data, list):
                _messages = []
                _flg = True
                if len(_task_data) == 0 and len(_common) > 0:
                    _task_data = [_common]

                for i, d in enumerate(_task_data):
                    if self.break_:
                        return -2, _data_piped, u"puzzle task stopped"

                    _flg, _data_piped, _message = _execute_step(_task_settings=_task_settings,
                                                                _task_data=d,
                                                                _common=_common,
                                                                _step=_step,
                                                                _data_piped=_data_piped)

                    _messages.extend(_message)
                    if not _flg:
                        self.break_ = True

                return _flg, _data_piped, _messages
            else:
                _messages = []
                temp_common = copy.deepcopy(common)
                temp_common.update(_task_data)
                _task_data = temp_common
                for _task_settings in pieces.get(_step, []):
                    if self.break_:
                        _message = [-2,
                                    _task_settings.get("name", ""),
                                    _task_settings.get("comment", ""),
                                    u"puzzle task stopped",
                                    u"puzzle task stopped"]

                        _messages.append(_message)
                        return False, _data_piped, _messages

                    _flg, _data_piped, _header, _detail = _execute_task(task_settings=_task_settings,
                                                                        task_data=_task_data,
                                                                        data_piped=_data_piped)

                    if _header is not None:
                        _message = [_flg,
                                    _task_settings.get("name", ""),
                                    _task_settings.get("comment", ""),
                                    _header,
                                    _detail]

                        _messages.append(_message)
                    if not _flg:
                        self.break_ = True
                        return _flg, _data_piped, _messages

                return True, _data_piped, _messages

        self.break_ = False
        inp = datetime.datetime.now()
        messages = []
        self.logger.debug("start\n")
        common = data.get("common", {})
        for step in self.order:
            if step not in pieces:
                self.logger.debug("")
                continue

            data.setdefault(step, {})
            self.logger.debug("{}:".format(step))
            flg, self.data_piped, message = _execute_step(_task_settings=pieces[step],
                                                          _task_data=data[step],
                                                          _common=common,
                                                          _step=step,
                                                          _data_piped=self.data_piped)

            if isinstance(message, list):
                messages.extend(message)
            else:
                messages.append(message)

            self.logger.debug("")

        if "finally" in pieces:
            self.break_ = False
            self.data_piped["messages"] = messages
            flg, self.data_piped, message = _execute_step(_task_settings=pieces["finally"],
                                                          _task_data={},
                                                          _common=common,
                                                          _step="finally",
                                                          _data_piped=self.data_piped)

        self.logger.debug("takes: %s" % str(datetime.datetime.now() - inp))
        self.close_event(messages)

        return messages


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
        bat += "SET ALL_PIECES_PATH={}\n".format(str(kwargs["piece_path"]))
        bat += "SET PUZZLE_LOGGER_NAME={}\n".format(str(kwargs["log_name"]))
        bat += "SET PUZZLE_LOGGER_DIRECTORY={}\n".format(str(kwargs.get("log_directory", False)))
        bat += "SET PIECES_KEYS={}\n".format(str(kwargs["keys"]))
        bat += "SET PUZZLE_APP={}\n".format(str(app))
        bat += "SET PUZZLE_PATH={}\n".format(str(kwargs["sys_path"]))
        bat += "SET PUZZLE_TASKS={}\n".format(str(kwargs["task_path"]))
        bat += "SET PUZZLE_MESSAGE_OUTPUT={}\n".format(str(kwargs["message_output"]))
        if "pass_path" in kwargs:
            bat += "SET PUZZLE_PASS_PATH={}\n".format(str(kwargs["pass_path"]))

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
        env_copy["ALL_PIECES_PATH"] = str(kwargs["piece_path"])
        env_copy["PUZZLE_LOGGER_NAME"] = str(kwargs["log_name"])
        env_copy["PUZZLE_LOGGER_DIRECTORY"] = str(kwargs.get("log_directory", False))
        env_copy["PIECES_KEYS"] = str(kwargs["keys"])
        env_copy["PUZZLE_APP"] = str(app)
        env_copy["PUZZLE_PATH"] = str(kwargs["sys_path"])
        env_copy["PUZZLE_TASKS"] = str(kwargs["task_path"])
        env_copy["PUZZLE_MESSAGE_OUTPUT"] = str(kwargs["message_output"])
        if "pass_path" in kwargs:
            env_copy["PUZZLE_PASS_PATH"] = str(kwargs["pass_path"])

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
