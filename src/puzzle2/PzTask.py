# -*- coding: utf8 -*-

import copy
import time
import traceback

from . import PzLog
class PzTask(object):
    def __init__(self, **args):
        self.task = args.get("task", {})

        self.data = copy.deepcopy(args.get("data", {}))
        self.context = args.get("context", {})
        self.logger = self.context.get("logger")
        self.module = args.get("module", False)

        self.return_code = 0
        """
         --------------------
         response return_code
         --------------------
         0: Success
         1: Error
         2: Skipped
         3: Break
         4: Module import error
         5: Required key does not exist
        """
        self.task.setdefault("name", "untitled")
        self.name = self.task["name"]

        if not self.logger:
            log = PzLog.PzLog()
            self.logger = log.logger
            self.context.setdefault("logger", self.logger)

        # if "logger" in self.context:
        #    self.context["logger"] = self.logger
        # print(self.logger.handlers)
        
        for k, v in self.task.get("data_defaults", {}).items():
            self.data.setdefault(k, v)


            """
            if startswith "data." or no prefix search from data,
            else startswith "context." seach from context.data
            """
        for k, v in self.task.get("data_key_replace", {}).items():
            if v.startswith("context."):
                name = v.replace("context.", "")
                if name in self.context:
                    self.data[k] = self.context[name]
            else:
                name = v.replace("data.", "")
                if name in self.data:
                    self.data[k] = self.data[v]
                    del self.data[v]

        self.header = self.task["name"]
        self.skip = False

        for condition in self.task.get("conditions", []):
            for k, v in condition.items():
                d = self.context if k.startswith("context.") else self.data
                attr_name = k.replace("context.", "").replace("data.", "")
                if attr_name not in d:
                    self.skip = True
                    self.return_code = 2
                    break
                if isinstance(v, list):
                    if d[attr_name] not in v:
                        self.skip = True
                        self.return_code = 2
                else:
                    if v != d[attr_name]:
                        self.skip = True
                        self.return_code = 2

        for k, v in self.task.get("data_override", {}).items():
            self.data[k] = v

        if hasattr(self.module, "DATA_KEY_REQUIRED") and not self.skip:
            data_key_required = list(set(self.module.DATA_KEY_REQUIRED) - set(self.data.keys()))
            if len(data_key_required) > 0:
                data_key_required_text = ", ".join(data_key_required)
                self.logger.critical("required key is not exists in 'data': {}".format(data_key_required_text))
                self.logger.details.add_detail("required key is not exists in 'data': {}".format(data_key_required_text))
                self.skip = True
                self.return_code = 5

    def execute(self, context_data={}):
        """
         --------------------
         response return_code
         --------------------
         0: Success
         1: Error
         2: Skipped
         3: Task stopped
         4: module import error
         5: require key is not exists
        """

        # Use self.context[_data] by default.
        # Only use optional context_data if provided, such as executing this instance several times.
        if context_data:
            self.context = context_data

        response = {}
        start_time = time.time()
        if self.skip:
            self.logger.debug("task skipped")
            self.logger.details.set_header(self.return_code, "skipped: {}".format(self.name))
            response = {"return_code": self.return_code}
        else:
            event = {"task": self.task, "data": self.data}

            response = self.module.main(event, self.context)
            if response is None:
                response = {"return_code": self.return_code}

        response.setdefault("return_code", self.return_code)
        self.logger.debug("return_code: {}".format(response["return_code"]))
        self.logger.details.set_execution_time(time.time() - start_time)

        if hasattr(self.module, "DATA_KEY_REQUIRED"):
            required = {}
            for key in self.module.DATA_KEY_REQUIRED:
                if key in self.data:
                    if key in self.data:
                        required[key] = self.data[key]
            self.logger.details.set_data_required(required)

        return response
