from __future__ import print_function
from __future__ import unicode_literals

import os
import sys
import traceback
import importlib

from . import Puzzle
from . import pz_env as pz_env
from . import pz_config as pz_config

try:
    reload
except BaseException:
    if hasattr(importlib, "reload"):
        # for py3.4+
        from importlib import reload


class PuzzleBatch(Puzzle.Puzzle):
    def __init__(self, name="puzzle", **kwargs):
        self.name = kwargs.get("name", name)
        kwargs["log_directory"] = kwargs.get("log_directory", pz_env.get_log_directory())
        kwargs["name"] = self.name
        super(PuzzleBatch, self).__init__(**kwargs)

    def start(self, task_set_path, data_path, context_path, **kwargs):
        """
        task_set_type:
          multi: multi task set in one file
          single: single task set in one file(required: keys)
        """
        def _get(name, default, kwargs):
            if name in kwargs:
                return kwargs[name]
            elif name in os.environ:
                return os.environ[name]
            return default
        self.result_path = kwargs["result_path"]
        task_set_type = kwargs.get("task_set_type", "single")  # multi task set in one file
        keys = kwargs.get("keys")
        app = kwargs.get("app", "")

        module_directory_path = kwargs.get("module_directory_path")

        if module_directory_path:
            for each in [l for l in module_directory_path.split(";") if l != ""]:
                # Prepend to avoid conflicts with similarly named top-level packages (e.g., 'tasks')
                norm_each = os.path.normpath(each)
                normalized_paths = [os.path.normpath(p) for p in sys.path]
                if norm_each not in normalized_paths:
                    sys.path.insert(0, norm_each)
        _, data = pz_config.read(data_path)
        _, pz_data = pz_config.read(task_set_path)
        if context_path:
            _, context_data = pz_config.read(context_path)
        else:
            context_data = None

        messages = []
        headers = []
        if task_set_type == "single":
            self.play(pz_data, data, context_data)
            headers.extend(self.logger.details.order)
            messages.extend(self.logger.details.get_all())
        else:
            keys = [key.strip() for key in keys.split(";") if key != ""]

            # varidate
            for key in keys:
                if not key in pz_data:
                    raise Exception("key: {} is not found in task set".format(key))
            
            for key in keys:
                self.play(pz_data[key], data, context_data)
                headers.extend(self.logger.details.order)
                messages.extend(self.logger.details.get_all())
                context_data = self.context

        self.close_event(app, messages, kwargs.get("close_app", True))
        return headers, messages, self.context

    def close_event(self, app, messages, close_app):
        def _close():
            flg = True
            # Skip when app is not specified
            if not app:
                return True
            try:
                addon = importlib.import_module("puzzle2.addons.{}.integration".format(app))
                reload(addon)
            except ImportError:
                # Addon for the specified app is not available; skip closing quietly
                return False
            
            if hasattr(addon, "close_event"):
                flg = addon.close_event()

            return flg

        if self.result_path:
            pz_config.save(self.result_path, messages)

        if close_app:
            print("close")
            _close()

