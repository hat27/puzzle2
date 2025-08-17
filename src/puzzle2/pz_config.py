# -*- coding: utf8 -*-
import sys
import os
import json
import codecs

YAML_AVAILABLE = False
try:
    import yaml  # type: ignore
    YAML_AVAILABLE = True
except BaseException:
    yaml = None  # Fallback when PyYAML is not available

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        return str(o)

def read(path):
    """
    :type path: read file (.json, .yml)
    :param path:
    :return: info, data
    """
    data = {}
    if sys.version_info.major == 2:
        with codecs.open(path, "r") as f:
            if path.endswith(".yml"):
                if YAML_AVAILABLE and yaml is not None:
                    data = yaml.load(f, Loader=yaml.SafeLoader)
                else:
                    raise RuntimeError("YAML support is not available; cannot read .yml: {}".format(path))
            elif path.endswith(".json"):
                data = json.load(f, "utf8")
    else:
        with codecs.open(path, "r", "utf8") as f:
            if path.endswith(".yml"):
                if YAML_AVAILABLE and yaml is not None:
                    data = yaml.load(f, Loader=yaml.SafeLoader)
                else:
                    raise RuntimeError("YAML support is not available; cannot read .yml: {}".format(path))
            elif path.endswith(".json"):
                data = json.load(f)

    return data.get("info", {}), data.get("data", {})


def save(path, data, tool_name="", category="", version="", extend_info={}):
    """
    :param path: save path (.json, .yml)
    :param data:  save data
    :param tool_name:  info
    :param category:  info
    :param version:  info
    :return:  bool
    """
    if not os.path.isdir(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except BaseException:  # Dir is created between the os.path.isdir and the os.makedirs calls
            if not os.path.isdir(os.path.dirname(path)):
                raise

    info_data = {"info": {"name": tool_name,
                          "category": category,
                          "version": version},
                 "data": data}

    info_data["info"].update(extend_info)
    if sys.version_info.major == 2:
        with codecs.open(path, "w") as f:
            if path.endswith(".yml"):
                if not YAML_AVAILABLE or yaml is None:
                    raise RuntimeError("YAML support is not available; cannot write .yml: {}".format(path))
                yaml.dump(info_data, f, default_flow_style=False, allow_unicode=True)
            elif path.endswith(".json"):
                json.dump(info_data, f, indent=4, ensure_ascii=False, cls=CustomEncoder)
    elif sys.version_info.major == 3:
        with codecs.open(path, "w", "utf8") as f:
            if path.endswith(".yml"):
                if not YAML_AVAILABLE or yaml is None:
                    raise RuntimeError("YAML support is not available; cannot write .yml: {}".format(path))
                yaml.dump(info_data, f, default_flow_style=False, allow_unicode=True)
            elif path.endswith(".json"):
                json.dump(info_data, f, indent=4, ensure_ascii=False, cls=CustomEncoder)

        return True

    return False

