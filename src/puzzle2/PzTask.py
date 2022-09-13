# -*- coding: utf8 -*-

import copy
import traceback

from . import PzLog


class PzTask(object):
    def __init__(self, **args):
        self.task = args.get("task", {})

        self.data = copy.deepcopy(args.get("data", {}))
        self.data_globals = args.get("data_globals", {})

        self.context = args.get("context", {})
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
         4: module import error
        """
        self.task.setdefault("name", "untitled")
        self.name = self.task["name"]

        if not self.logger:
            log = PzLog.PzLog()
            self.logger = log.logger

        self.context.setdefault("logger", self.logger)

        #if "logger" in self.context:
        #    self.context["logger"] = self.logger
        # print(self.logger.handlers)

        if "inputs" in self.task:
            """
            if startswith "data." or no prefix search from data, 
            else startswith "globals." seach from data_globals
            """
            for k, v in self.task["inputs"].items():
                if v.startswith("globals."):
                    name = v.replace("globals.", "")
                    if name in self.data_globals:
                        self.data[k] = self.data_globals[name]
                else:
                    name = v.replace("data.", "")
                    if name in self.data:
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

    def execute(self, data_globals={}):
        """
         --------------------
         response return_code
         --------------------
         0: Success
         1: Error
         2: Skipped
         3: Task stopped
         4: module import error
        """

        # Use self.data_globals by default.
        # Only use optional data_globals if provided, such as executing this instance several times.
        data_globals = data_globals if data_globals else self.data_globals

        response = {}
        if self.skip:
            self.logger.debug("task skipped")
            self.logger.details.set_header(2, "skipped: {}".format(self.name))

            response = {"return_code": 2, "data_globals": data_globals}
        else:
            event = {"task": self.task, "data": self.data, "data_globals": data_globals}

            # set default header
            self.context = {"logger": self.logger}
            response = self.module.main(event, self.context)

            if response is None:
                response = {"status_code": 0, "data_globals": data_globals}

        return response
