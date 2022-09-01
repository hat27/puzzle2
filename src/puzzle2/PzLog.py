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


class PzLog(object):
    def __init__(self, name=None, new=False, **kwargs):
        u"""
        ログのクラス
        :param name: log名
        :param new: ハンドラを全部削除してから新たに作成
        :param kwargs:
        :param clear: logファイルの削除
        :param use_default_config: 設定ファイルの初期化(log.template)
        :param logger_level: loggerのレベル
        """
        if name is None:
            name = "unknown"

        self.template = pz_env.get_log_template()
        self.log_directory = kwargs.get("log_directory", pz_env.get_log_directory())

        self.name = name
        self.log_path = "{}/{}.log".format(self.log_directory, self.name)
        self.config_path = "{}/config/{}.conf".format(self.log_directory, self.name)

        if new:
            self.remove_handler()
            kwargs["use_default_config"] = True

        if kwargs.get("clear", False):
            os.remove(self.log_path)

        self.removed = False
        if kwargs.get("use_default_config", False):
            if os.path.exists(self.config_path):
                try:
                    os.remove(self.config_path)
                    print("removed: {}".format(self.config_path))
                    self.removed = True
                except:
                    pass

        if not os.path.exists(self.config_path):
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

        self.logger.propagate = False

    def create_log_config_file(self, replace_log_config):
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

    def remove_handler(self):
        previous_logger = getLogger(self.name)
        for handler in previous_logger.handlers[::-1]:
            if hasattr(handler, "close"):
                print("close: {}".format(handler))
                handler.close()
            try:
                self.logger.removeHandler(handler)
            except:
                pass
    
    def update_config_file(self, config_path, update_config):
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