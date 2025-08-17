# -*- coding: utf8 -*-

import os
import sys
import copy
import glob
import datetime
import logging.config
from logging import getLogger, DEBUG, INFO, WARNING, ERROR, CRITICAL

from . import pz_env as pz_env
from . import pz_config as pz_config

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
        self._meta_data = {}
        self.order = []
        self.index = 0
        self.name = ""

    def set_name(self, name):
        self.name = "{} {}".format(self.index, name)
        self.order.append(self.name)
        self._meta_data[self.name] = {}
        self.index += 1
        return self.index - 1, self.name

    def add_detail(self, text):
        self._details.setdefault(self.name, []).append(text)

    def set_header(self, return_code, text):
        self._header[self.name] = {"return_code": return_code,
                                   "header": text}
    
    def set_data_location(self, location):
        if self.name in self._meta_data:
            self._meta_data[self.name]["location"] = location

    def set_data_required(self, required):
        if self.name in self._meta_data:
            self._meta_data[self.name]["required"] = required

    def set_execution_time(self, execution_time):
        if self.name in self._meta_data:
            self._meta_data[self.name]["execution_time"] = execution_time

    def update_code(self, return_code):
        self._header[self.name]["return_code"] = return_code
    
    def get_header(self):
        return [self._header.get(name, name) for name in self.order]

    def get_return_codes(self):
        codes = []
        for name in self.order:
            codes.append(self._header[name]["return_code"])

        return codes

    def get_details(self, name):
        data = copy.deepcopy(self._header[name])
        if name in self._details:
            data["details"] = self._details[name]
        if name in self._meta_data:
            data["meta_data"] = self._meta_data[name]
        return data

        return details

    def get_all(self):
        all_ = []
        for name in self.order:
            data = {}
            if name in self._header:
                data = copy.deepcopy(self._header[name])

            if name in self._details:
                data["details"] = self._details[name]
            
            if name in self._meta_data:
                data["meta_data"] = self._meta_data[name]

            all_.append(data)

        return all_
    
    def add_data_set(self, headers, results, location):
        for header, result in zip(headers, results):
            self.add_data(header, result, location)
    
    def add_data(self, header, result, location={}):
        header_name = " ".join(header.split(" ")[1:])
        self.set_name(header_name)
        self.set_header(result["return_code"], result["header"])
        for detail in result.get("details", []):
            self.add_detail(detail)
        
        self.set_data_required(result.get("meta_data", {}).get("required", {}))
        self.set_execution_time(result.get("meta_data", {}).get("execution_time", 0.0))
        self.set_data_location(location)

    def clear(self):
        self._header = {}
        self._details = {}
        self._data_required = {}
        self._execution_time = {}
        self.order = []
        self.name = ""
        self.index = 0

# TODO: 将来的にPzLoggerとPzLogを統合する事を検討


class PzLogger(logging.Logger):
    super(logging.Logger)
    ui = None

    def __init__(
        self,
        *args,
        **kwargs
    ):
        logging.Logger.__init__(self, *args, **kwargs)
        # with this pattern, it's rarely necessary to propagate the| error up to parent
        self.ui = kwargs.get("ui", None)
        self.details = Details()

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


# Note: Avoid setting a global LoggerClass to prevent process-wide side effects.
# If you need a PzLogger instance, PzLog will construct one locally.
# log.success('Hello World')


class PzLog(object):
    def __init__(self, name=None, new=False, **kwargs):
        """
        Custom Logging with utility functions
        and custom output functions for lighting up the UI of Puzzle and MayaBatcher.

        :param name: Log name
        :param new: If logger was already exists, Remove previous handlers for self.name on init
        :param kwargs:
        :param clear: Delete the previous log file
        :param reset_template: Reset log.template file # old arg name is "set_default_config"
        :param logger_level: Logger level. stream handler only. file handler is always DEBUG(or depends on log.template.yml)
        :param log_directory: Dir for log files
        :param log_filename: Filename excluding extension to be used for .log and .conf files
        :param template_file: Path to custom .template file to be used for logging config
        :param ignore_namespace: ignore namespace to logger name.default logger is name.puzzle
        :param max_log_count: Max number of log files to keep. default is 0 (no limit)
        :param add_date_to_log_name: Add date to log file name. default is False
        :param user_name: Add user to log file name. default is False

        log_directory/log_filename.log
        log_directory/config/log_filename.

        """
        if name is None:
            name = "unknown"

        template_path = kwargs.get("template_file", pz_env.get_log_template())
        # If YAML isn't available but a YAML template was chosen, switch to JSON template
        try:
            from . import pz_config as _pz_config
            if template_path.endswith('.yml') and (not getattr(_pz_config, 'YAML_AVAILABLE', False)):
                template_path = pz_env.get_log_template_json()
        except BaseException:
            pass

        self.log_directory = kwargs.get("log_directory", pz_env.get_log_directory("Pzlog"))
        self.base_template_path = None

        if kwargs.get("namespace", True):
            self.name = "puzzle.{}".format(name)
        else:
            self.name = name

        reset_template = kwargs.get("reset_template", False)
        if "use_default_config" in kwargs:
            # old arg name
            reset_template = kwargs["use_default_config"]

        handler_levels = {k.replace("_level", ""): v for (k, v) in kwargs.items() if k.endswith("_level")}
        if self.name in self.get_loggers().keys():
            if new:
                self.remove_handlers()
            else:
                self.logger = logging.getLogger(self.name)
                self.change_handler_levels(**handler_levels)
                return

        config_name = name
        self.filename = kwargs.get("log_filename", name)  # Filename for log and config files
        if kwargs.get("add_date_to_log_name", False):
            self.filename = "{}_{}".format(datetime.datetime.now().strftime("%Y%m%d"), self.filename)
            reset_template = True

        user_name = kwargs.get("user_name", False)
        if user_name:
            f, ext = os.path.splitext(self.filename)
            self.filename = "{}_{}{}".format(f, user_name, ext)
            config_name = "{}_{}".format(config_name, user_name)

        self.log_path = "{}/{}.log".format(self.log_directory, self.filename)  # Log file path
        self.config_path = "{}/config/{}.json".format(self.log_directory, config_name)  # Config file path

        if kwargs.get("clear", False):
            # Delete previous log file if exists
            if os.path.exists(self.log_path):
                os.remove(self.log_path)

        max_log_count = kwargs.get("max_log_count", 0)
        if max_log_count > 0:
            directory = os.path.dirname(self.log_path)
            if os.path.exists(directory):
                pattern_name = name
                if user_name:
                    pattern_name = "{}_{}".format(name, user_name)
                if kwargs.get("add_date_to_log_name", False):
                    pattern_name = "*_{}".format(pattern_name)
                
                pattern = "{}/{}.log".format(directory, pattern_name)
                log_files = glob.glob(pattern)
                log_files.sort(key=os.path.getmtime)
                if len(log_files) > max_log_count:
                    for log_file in log_files[:-max_log_count]:
                        os.remove(log_file)

        self.removed = False
        if reset_template:
            # Reset logging config file if specified
            if os.path.exists(self.config_path):
                try:
                    os.remove(self.config_path)
                    self.removed = True
                except BaseException:
                    import traceback
                    traceback.print_exc()

        if not os.path.exists(self.config_path):
            # Create a new config file from the template config file
            append_loggers = {
                self.name: {
                    "level": kwargs.get("logger_level", "DEBUG"),
                    "handlers": kwargs.get("handlers", ["stream_handler", "file_handler"])
                }
            }

            append_handers = {
                "file_handler": {
                    "filename": self.log_path
                }
            }

            # Use the selected base template path (YAML or JSON depending on availability)
            self.base_template_path = template_path
        else:
            self.base_template_path = self.config_path
            append_handers = {}
            append_loggers = {}

        config_data = self.create_log_config_file(append_handers, append_loggers)

        # Build a scoped logger from config without applying global dictConfig
        self.logger = self._build_logger_from_config(config_data)
        self.change_handler_levels(**handler_levels)

        # check: propagate is always False
        self.logger.propagate = False
    
    def change_handler_levels(self, **kwargs):
        for k, v in kwargs.items():
            for handler in self.logger.handlers:
                if handler.name == k:
                    handler.setLevel(v)
                    break

    def get_loggers(self):
        return logging.Logger.manager.loggerDict

    def create_log_config_file(self, handers={}, loggers={}):
        # Read template (do not create template directory)
        info, data = pz_config.read(self.base_template_path)

        data.setdefault("handlers", {})
        for k, v in handers.items():
            for k2, v2 in v.items():
                data["handlers"].setdefault(k, {})
                data["handlers"][k][k2] = v2

        data.setdefault("loggers", {})
        for k, v in loggers.items():
            for k2, v2 in v.items():
                data["loggers"].setdefault(k, {})
                data["loggers"][k][k2] = v2

        pz_config.save(self.config_path, data, "pzLog", "template")

        return data

    def _build_logger_from_config(self, config_data):
        """
        Build and configure only this logger from the given config dict
        without applying global logging.config.dictConfig.
        Supports the common fields used by puzzle templates
        (formatters, stream_handler, file_handler, levels, handlers list).
        """
        # Resolve target logger config (fallback to root-like defaults if missing)
        logger_name = self.name
        loggers_cfg = config_data.get("loggers", {})
        logger_cfg = loggers_cfg.get(logger_name, {})

        # Create or get a PzLogger instance without changing the global LoggerClass
        mgr = logging.Logger.manager
        existing = mgr.loggerDict.get(logger_name)
        if isinstance(existing, PzLogger):
            logger = existing
        else:
            logger = PzLogger(logger_name)
            mgr.loggerDict[logger_name] = logger

        # Ensure directory for file handler exists when needed
        def _ensure_dir(path):
            d = os.path.dirname(path)
            if d and not os.path.isdir(d):
                try:
                    os.makedirs(d)
                except BaseException:
                    if not os.path.isdir(d):
                        raise

        # Build formatters
        fmts_cfg = config_data.get("formatters", {})
        formatters = {}
        for fname, fcfg in fmts_cfg.items():
            fmt = fcfg.get("format")
            datefmt = fcfg.get("datefmt")
            try:
                formatters[fname] = logging.Formatter(fmt=fmt, datefmt=datefmt)
            except Exception:
                # Fallback minimal formatter
                formatters[fname] = logging.Formatter(fmt)

        # Build handlers registry but only instantiate those referenced by our logger
        wanted_handlers = logger_cfg.get("handlers") or []
        handlers_cfg = config_data.get("handlers", {})
        built_handlers = {}
        for hname in wanted_handlers:
            hcfg = handlers_cfg.get(hname)
            if not hcfg:
                continue
            hclass = hcfg.get("class", "")
            level = hcfg.get("level", "DEBUG")
            formatter_name = hcfg.get("formatter")

            handler = None
            if hclass.endswith("StreamHandler"):
                stream_target = hcfg.get("stream", "ext://sys.stdout")
                stream = sys.stdout if "stdout" in stream_target else sys.stderr
                handler = logging.StreamHandler(stream)
            elif hclass.endswith("FileHandler"):
                filename = hcfg.get("filename", self.log_path)
                mode = hcfg.get("mode", "a")
                _ensure_dir(filename)
                handler = logging.FileHandler(filename, mode=mode, encoding="utf-8")

            if handler is None:
                # Unsupported handler class; skip quietly to avoid global changes
                continue

            # Name the handler so change_handler_levels can find it
            try:
                handler.set_name(hname)
            except AttributeError:
                handler.name = hname  # older Python fallback

            # Level and formatter
            try:
                handler.setLevel(getattr(logging, level.upper(), logging.DEBUG))
            except Exception:
                handler.setLevel(logging.DEBUG)

            if formatter_name and formatter_name in formatters:
                handler.setFormatter(formatters[formatter_name])

            built_handlers[hname] = handler

        # Apply handlers to logger (reset if we've removed template previously or asked new=True upstream)
        # Remove only handlers attached to this logger instance
        for h in list(logger.handlers):
            try:
                logger.removeHandler(h)
            except Exception:
                pass

        for hname in wanted_handlers:
            if hname in built_handlers:
                logger.addHandler(built_handlers[hname])

        # Level and propagate
        level_name = logger_cfg.get("level", "DEBUG")
        try:
            logger.setLevel(getattr(logging, level_name.upper(), logging.DEBUG))
        except Exception:
            logger.setLevel(logging.DEBUG)
        logger.propagate = False

        return logger

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
    
    def __del__(self):
        self.remove_handlers()