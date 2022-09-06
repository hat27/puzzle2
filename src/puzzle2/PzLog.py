# -*- coding: utf8 -*-

import os
import sys

if sys.version.startswith("2"):
    import ConfigParser
else:
    import configparser

import logging.config
from logging import getLogger, DEBUG, INFO, CRITICAL, ERROR

from . import pz_env as pz_env

CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
SUCCESS = 100  # Custom
RESULT = 101  # Custom
ALERT = 102  # Custom
logging.addLevelName(SUCCESS, 'SUCCESS')
logging.addLevelName(RESULT, 'RESULT')
logging.addLevelName(ALERT, 'ALERT')

class Details(list):
    def get_header(self):
        return [l["header"] for l in self]
    
    def get_details(self, key=None):
        if key:
            return [l["details"] for l in self if l["name"] == key if "details" in l]
        return [l["details"] for l in self if "details" in l]

    def get_all(self):
        return self
    
class PzLogger(logging.Logger):
    super(logging.Logger)
    details = Details()

    def success(self, msg, *args, **kwargs):
        # CUSTOM OUTPUT
        if self.isEnabledFor(SUCCESS):
            self._log(SUCCESS, msg, args, **kwargs)

            if "ui" in kwargs:
                ui = kwargs["ui"]
                ui.success(msg, self.name)

    def result(self, msg, *args, **kwargs):
        # CUSTOM OUTPUT
        if self.isEnabledFor(RESULT):
            self._log(RESULT, msg, args, **kwargs)

            if "ui" in kwargs:
                ui = kwargs["ui"]
                ui.result(msg, self.name)

    def alert(self, msg, *args, **kwargs):
        # CUSTOM OUTPUT
        if self.isEnabledFor(ALERT):
            self._log(ALERT, msg, args, **kwargs)

            if "ui" in kwargs:
                ui = kwargs["ui"]
                ui.alert(msg, self.name)

    def critical(self, msg, *args, **kwargs):
        if self.isEnabledFor(CRITICAL):
            self._log(CRITICAL, msg, args, **kwargs)

            if "ui" in kwargs:
                ui = kwargs["ui"]
                ui.critical(msg, self.name)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(ERROR):
            self._log(ERROR, msg, args, **kwargs)

            if "ui" in kwargs:
                ui = kwargs["ui"]
                ui.error(msg, self.name)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

            if "ui" in kwargs:
                ui = kwargs["ui"]
                ui.warning(msg, self.name)

    def info(self, msg, *args, **kwargs):
        if self.isEnabledFor(INFO):
            self._log(INFO, msg, args, **kwargs)

            if "ui" in kwargs:
                ui = kwargs["ui"]
                ui.info(msg, self.name)

    def debug(self, msg, *args, **kwargs):
        if self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, args, **kwargs)

            if "ui" in kwargs:
                ui = kwargs["ui"]
                ui.debug(msg, self.name)


# Set PzLogger as the default Class to be called when using getLogger()
logging.setLoggerClass(PzLogger)


# log.success('Hello World')
# log.updateUI('Hello World')


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
        """
        if name is None:
            name = "unknown"

        self.template = pz_env.get_log_template()
        self.log_directory = kwargs.get("log_directory", pz_env.get_log_directory("Pzlog"))

        self.name = name
        self.log_path = "{}/{}.log".format(self.log_directory, self.name)
        self.config_path = "{}/config/{}.conf".format(self.log_directory, self.name)

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
                    print("removed: {}".format(self.config_path))
                    self.removed = True
                except BaseException:
                    pass

        if not os.path.exists(self.config_path):
            # Create a new config file from the template config file
            replace_text = {"$NAME": self.name}
            self.create_log_config_file(replace_text)
            print("log config path:", self.config_path)
            update_config = {"loggers": {
                "keys": "root, {}".format(self.name)
            },
                "handler_file_handler": {
                "args": "('{}', 'D')".format(self.log_path)
            }
            }

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

        print("config file:", self.config_path)
        logging.config.fileConfig(self.config_path)
        self.logger = getLogger(self.name)
        # self.logger = PzLogger(self.name)

        self.logger.propagate = False

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
                print("close: {}".format(handler))
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
            ini = ConfigParser.ConfigParser()
            ini.read(config_path)

            for k, v in update_config.items():
                print(k, v)
                if k in ini.sections():
                    for k2, v2 in v.items():
                        if ini.get(k, k2):
                            ini.set(k, k2, v2)
        else:
            ini = configparser.ConfigParser()
            ini.read(config_path, "utf-8")

            for k, v in update_config.items():
                if k in ini:
                    for k2, v2 in v.items():
                        if k2 in ini[k]:
                            ini[k][k2] = v2

        print(config_path)
        with open(config_path, "w") as f:
            ini.write(f)
