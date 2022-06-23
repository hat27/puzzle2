# -*- coding: utf8 -*-

import os

import logging.config
from logging import getLogger, DEBUG, INFO, CRITICAL, ERROR

from . import pz_env as pz_env


class PzLog(object):
    def __init__(self, name=None, new=False, **args):
        u"""
        ログのクラス
        :param name: log名
        :param new: ハンドラを全部削除してから新たに作成
        :param args:
        :param clear: logファイルの削除
        :param use_default_config: 設定ファイルの初期化(log.template)
        """
        if name is None:
            name = "unknown"

        self.template = pz_env.get_log_template()
        self.log_directory = args.get("log_directory", pz_env.get_log_directory())

        self.name = name
        self.log_path = "{}/{}.log".format(self.log_directory, self.name)
        self.config_path = "{}/config/{}.conf".format(self.log_directory, self.name)

        if new:
            self.remove_handler()

        if args.get("clear", False):
            os.remove(self.log_path)

        replace_text = {"$NAME": self.name,
                                "$SAVEFILE": self.log_path}

        self.removed = False
        if args.get("use_default_config", False):
            if os.path.exists(self.config_path):
                try:
                    os.remove(self.config_path)
                    print("removed: {}".format(self.config_path))
                    self.removed = True
                except:
                    pass

        if not os.path.exists(self.config_path):
            self.get_log_config(replace_text)

        logging.config.fileConfig(self.config_path)
        self.logger = getLogger(self.name)
        level = args.get("logger_level", "debug")
        if level == "debug":
            self.logger.setLevel(DEBUG)
        elif level == "info":
            self.logger.setLevel(INFO)
        elif level == "error":
            self.logger.setLevel(ERROR)
        elif level == "critical":
            self.logger.setLevel(CRITICAL)

        self.logger.propagate = False

    def get_log_config(self, replace_log_config):
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
