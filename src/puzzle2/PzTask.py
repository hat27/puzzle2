# -*- coding: utf8 -*-

import copy
from . import PzLog


class PzTask(object):
    def __init__(self, **args):
        self.task = args.get("task", {})

        self.data = copy.deepcopy(args.get("data", {}))
        self.data_piped = args.get("data_piped", {})

        self.logger = args.get("logger", False)
        self.module = args.get("module", False)
        self.return_code = 0
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

        self.name = self.task.get("name", "untitled")
        if not self.logger:
            log = PzLog.PzLog()
            self.logger = log.logger

        if "inputs" in self.task:
            """
            startwith @: check it from data_piped
            """
            for k, v in self.task["inputs"].items():
                if v.startswith("@"):
                    if v[1:] in self.data_piped:
                        self.data[k] = self.data_piped[v[1:]]

                elif v in self.data:
                    self.data[k] = self.data[v]
                    del self.data[v]

        self.header = self.task.get("name", "")
        self.details = []

        comment = self.task.get("comment", "")
        if comment != u"":
            self.details = [u"【{}】\n{}\n".format(comment, self.task["module"])]

        self.skip = False
        if "conditions" in self.task:
            for condition in self.task["conditions"]:
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

        # Use self.data_piped by default.
        # Only use optional data_piped if provided, such as executing this instance several times.
        data_piped = data_piped if data_piped else self.data_piped

        if self.skip:
            self.logger.debug("task skipped")
            self.logger.details.append({"name": self.name,
                                        "header": "skipped: {}".format(self.name),
                                        "return_code": 2,
                                        "comment": self.task.get("comment", "")})
            response = {"return_code": 2, "data_piped": data_piped}
        else:
            event = {"task": self.task, "data": self.data, "data_piped": data_piped}
            context = {"logger": self.logger}
            response = self.module.execute(event, context)
        return response
