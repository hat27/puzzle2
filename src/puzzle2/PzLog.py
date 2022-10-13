# -*- coding: utf8 -*-

import os
import sys
import copy

if sys.version.startswith("2"):
    import ConfigParser
else:
    import configparser

import logging.config
from logging import getLogger, DEBUG, INFO, WARNING, ERROR, CRITICAL

from . import pz_env as pz_env

# CRITICAL = 50
# ERROR = 40
# WARNING = 30
# INFO = 20
# DEBUG = 10
SUCCESS = 100  # Custom
RESULT = 101  # Custom
ALERT = 102  # Custom
FLAG = 103  # Custom
NOTICE = 104  # Custom
logging.addLevelName(SUCCESS, 'SUCCESS')
logging.addLevelName(RESULT, 'RESULT')
logging.addLevelName(ALERT, 'ALERT')
logging.addLevelName(FLAG, 'FLAG')
logging.addLevelName(NOTICE, 'NOTICE')


class Details(object):
    def __init__(self):
        self._header = {}
        self._details = {}
        self.order = []
        self.index = 0
        self.name = ""

    def set_name(self, name):
        self.name = "{} {}".format(self.index, name)
        self.order.append(self.name)

        self.index += 1
    
    def add_detail(self, text):
        self._details.setdefault(self.name, []).append(text)
    
    def set_header(self, return_code, text):
        self._header[self.name] = {"return_code": return_code, 
                                   "header": text}

    def update_code(self, return_code):
        self._header[self.name]["return_code"] = return_code

    def get_header(self):
        return [self._header.get(name, name) for name in self.order]

    def get_return_codes(self):
        codes = []
        for name in self.order:
            codes.append(self._header[name]["return_code"])

        return codes

    def get_details(self, key=None):
        if key:
            return self._details[key]
        else:
            details = []
            for name in self.order:
                details.append(self._details[name])

        return details

    def get_all(self):
        all_ = []
        for name in self.order:
            data = {}
            if name in self._header:
                data = copy.deepcopy(self._header[name])

            if name in self._details:
                data["details"] = self._details[name]

            all_.append(data)
        
        return all_
    
    def clear(self):
        self._header = {}
        self._details = {}
        self.order = []
        self.name = ""
        self.index = 0

# TODO: 将来的にPzLoggerとPzLogを統合する事を検討


class PzLogger(logging.Logger):
    super(logging.Logger)
    details = Details()
    ui = None

    def __init__(
        self,
        *args,
        **kwargs
    ):
        logging.Logger.__init__(self, *args, **kwargs)
        # with this pattern, it's rarely necessary to propagate the| error up to parent
        self.ui = kwargs.get("ui", None)

    def set_ui(self, ui):
        """
        Set ui to additionally reflect changes to when using logging.
        """
        self.ui = ui

    def update_ui(self, msg, level_name, ui=None, skip_ui_update=False, **kwargs):
        """
        Update the UI via view update function provided in the ui object,
        e.g., ui.success(), ui.result()
        The function name must match level name.

        Args:
            msg (str): Message to show in UI.
            level_name (str): Level name which should be the same as UI update function name.
            ui (ui object, optional): If updating a different UI than the one specified on init(), pass it here.
            skip_ui_update (bool, optional): Skip ui update if specified in the logging function parameter.
        """
        ui = ui if ui else self.ui
        if ui and (not skip_ui_update) and hasattr(ui, level_name):
            # Get the view update function provided in the ui object, e.g., ui.success(), ui.result()
            ui_update_function = getattr(ui, level_name)
            ui_update_function(msg, self.name)  # Pass message and logger name.

    # -----------------------------------------------------------------------------
    # For all logging functions below, pass "skip_ui_update=True" to skip ui update.
    # -----------------------------------------------------------------------------
    def success(self, msg, *args, **kwargs):
        # CUSTOM OUTPUT
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)
            self.update_ui(msg, "success", **kwargs)

    def result(self, msg, *args, **kwargs):
        # CUSTOM OUTPUT
        if self.isEnabledFor(RESULT):
            self._log(RESULT, msg, args, **kwargs)
            self.update_ui(msg, "result", **kwargs)

    def alert(self, msg, *args, **kwargs):
        # CUSTOM OUTPUT
        if self.isEnabledFor(ALERT):
            self._log(ALERT, msg, args, **kwargs)
            self.update_ui(msg, "alert", **kwargs)

    def flag(self, msg, *args, **kwargs):
        # CUSTOM OUTPUT
        if self.isEnabledFor(FLAG):
            self._log(FLAG, msg, args, **kwargs)
            self.update_ui(msg, "flag", **kwargs)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)
            self.update_ui(msg, "critical", **kwargs)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)
            self.update_ui(msg, "error", **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)
            self.update_ui(msg, "warning", **kwargs)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)
            self.update_ui(msg, "info", **kwargs)

    def notice(self, msg, *args, **kwargs):
        if self.isEnabledFor(NOTICE):
            self._log(NOTICE, msg, args, **kwargs)
            self.update_ui(msg, "notice", **kwargs)

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, **kwargs)
            self.update_ui(msg, "debug", **kwargs)


# Set PzLogger as the default Class to be called when using getLogger()
logging.setLoggerClass(PzLogger)

# log.success('Hello World')


class PzLog(object):
    def __init__(self, name=None, new=False, **kwargs):
        """
        Custom Logging with utility functions
        and custom output functions for lighting up the UI of Puzzle and MayaBatcher.

        :param name: Log name
        :param new: Remove previous handlers for self.name on init
        :param kwargs:
        :param clear: Delete the previous log file
        :param use_default_config: Reset log.template file
        :param logger_level: Logger level
        :param log_directory: Dir for log files
        :param log_filename: Filename excluding extension to be used for .log and .conf files
        """
        if name is None:
            name = "unknown"

        self.template = pz_env.get_log_template()
        self.log_directory = kwargs.get("log_directory", pz_env.get_log_directory("Pzlog"))
        self.name = name
        self.filename = kwargs.get("log_filename", name)  # Filename for log and config files
        self.log_path = "{}/{}.log".format(self.log_directory, self.filename)  # Log file path
        self.config_path = "{}/config/{}.conf".format(self.log_directory, self.filename)  # Config file path

        if new:
            # Remove all existing handlers for self.name
            self.remove_handlers()
            kwargs["use_default_config"] = True

        if kwargs.get("clear", False):
            # Delete previous log file if exists
            os.remove(self.log_path)

        self.removed = False
        if kwargs.get("use_default_config", False):
            # Reset logging config file if specified
            if os.path.exists(self.config_path):
                try:
                    os.remove(self.config_path)
                    # print("removed: {}".format(self.config_path))
                    self.removed = True
                except BaseException:
                    pass

        if not os.path.exists(self.config_path):
            # Create a new config file from the template config file
            replace_text = {"$NAME": self.name}
            self.create_log_config_file(replace_text)
            # print("log config path:", self.config_path)
            update_config = {}
            update_config["loggers"] = {"keys": "root, {}".format(self.name)}
            update_config["handler_file_handler"] = {"args": "('{}', 'D')".format(self.log_path)}  # TimedRotatingFileHandler

            update_config.setdefault("handler_stream_handler", {})
            update_config.setdefault("logger_root", {})
            update_config.setdefault("logger_{}".format(self.name), {})

            if "logger_level" in kwargs:
                update_config["handler_stream_handler"]["level"] = kwargs["logger_level"].upper()
                update_config["handler_file_handler"]["level"] = kwargs["logger_level"].upper()

            if "stream_handler_level" in kwargs:
                update_config["handler_stream_handler"]["level"] = kwargs["stream_handler_level"].upper()

            if "file_handler_level" in kwargs:
                update_config["handler_file_handler"]["level"] = kwargs["file_handler_level"].upper()

            self.update_config_file(self.config_path, update_config)

        # print("config file:", self.config_path)
        logging.config.fileConfig(self.config_path)
        self.logger = getLogger(self.name)
        # self.logger = PzLogger(self.name)

        self.logger.propagate = False

    # TODO: Check - .templateファイル内の文字変数の置換はConfigParserのdefault機能で代替可能？
    def create_log_config_file(self, replace_log_config):
        """ Create a new log config file from the template file.
        For any changes, use replace_log_config (key: new_val)
        """
        def _replace(w, replace_log_config_):
            for k, v in replace_log_config_.items():
                if k in w:
                    return w.replace(k, v)
            return w

        if not os.path.exists(os.path.dirname(self.config_path)):
            os.makedirs(os.path.dirname(self.config_path))

        with open(self.template, "r") as tx:
            tx_s = tx.read().split("\n")
            tx = open(self.config_path, "w")
            new = [_replace(l, replace_log_config) for l in tx_s]
            tx.write("\n".join(new))
            tx.close()

    def remove_handlers(self):
        """ Remove all handlers attached to self.name
        """
        previous_logger = getLogger(self.name)
        for handler in previous_logger.handlers[::-1]:
            if hasattr(handler, "close"):
                # print("close: {}".format(handler))
                handler.close()
            try:
                self.logger.removeHandler(handler)
            except BaseException:
                pass

    def update_config_file(self, config_path, update_config):
        """ Update a logging config file located at config_path
            for keys/vals in update_config dict.
        """
        if sys.version.startswith("2"):
            ini = ConfigParser.RawConfigParser()  # Use RawConfigParser when accessing line with %(var)s
            ini.read(config_path)

            for k, v in update_config.items():
                if k in ini.sections():
                    for k2, v2 in v.items():
                        if ini.get(k, k2):
                            ini.set(k, k2, v2)
        else:
            ini = configparser.RawConfigParser()
            ini.read(config_path, "utf-8")

            for k, v in update_config.items():
                if k in ini:
                    for k2, v2 in v.items():
                        if k2 in ini[k]:
                            ini[k][k2] = v2

        # print(config_path)
        with open(config_path, "w") as f:
            ini.write(f)
