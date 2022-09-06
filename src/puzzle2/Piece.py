# -*- coding: utf8 -*-

import copy
from . import PzLog


class Piece(object):
    def __init__(self, **args):
        self.data = copy.deepcopy(args.get("data", {}))
        self.data_piped = args.get("data_piped", {})
        self.settings = args.get("settings", {})
        self.logger = args.get("logger", False)
        self.module = args.get("module", False)
        """
         1: successed
         0: failed
        -1: skip
        -2: task stopped
        -3: piece name not exists
        """
        self.result_type = 1
        if not self.logger:
            log = PzLog.PzLog()
            self.logger = log.logger

        if "inputs" in self.settings:
            """
            startwith @: check it from data_piped
            """
            for k, v in self.settings["inputs"].items():
                if v.startswith("@"):
                    if v[1:] in self.data_piped:
                        self.data[k] = self.data_piped[v[1:]]

                elif v in self.data:
                    self.data[k] = self.data[v]
                    del self.data[v]

        self.header = self.settings["name"]
        self.details = []

        comment = self.settings.get("comment", "")
        if comment != u"":
            self.details = [u"【{}】\n{}\n".format(comment, self.settings["module"])]

        self.skip = False
        if "conditions" in self.settings:
            for condition in self.settings["conditions"]:
                for k, v in condition.items():
                    if k not in self.data:
                        self.skip = True
                        break
                    if isinstance(v, list):
                        if not self.data[k] in v:
                            self.skip = True
                    else:
                        if v != self.data[k]:
                            self.skip = True

    def execute(self, data_piped={}):
        if self.skip:
            self.logger.debug("task skipped")
            self.header += ":skipped"
        else:
            # self.module.settings = self.settings
            # self.module.data = self.data
            data_piped = self.module.execute(settings=self.settings, data=self.data, data_piped=self.data_piped, logger=self.logger)

        return data_piped
