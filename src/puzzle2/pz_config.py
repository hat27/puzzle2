# -*- coding: utf8 -*-
import sys
import os
import json
import codecs

try:
    import yaml
except BaseException:
    import traceback
    traceback.print_exc()


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
                data = yaml.load(f, Loader=yaml.SafeLoader)
            elif path.endswith(".json"):
                data = json.load(f, "utf8")
    else:
        with codecs.open(path, "r", "utf8") as f:
            if path.endswith(".yml"):
                data = yaml.load(f, Loader=yaml.SafeLoader)
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

    if extend_info:
        info_data["info"].update(extend_info)

    if sys.version_info.major == 2:
        with codecs.open(path, "w") as f:
            if path.endswith(".yml"):
                yaml.dump(info_data, f, default_flow_style=False, allow_unicode=True)
            elif path.endswith(".json"):
                json.dump(info_data, f, indent=4, ensure_ascii=False)
    elif sys.version_info.major == 3:
        with codecs.open(path, "w", "utf8") as f:
            if path.endswith(".yml"):
                try:  # PyYaml 5.1 - Keep current order
                    yaml.dump(info_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                except BaseException:
                    yaml.dump(info_data, f, default_flow_style=False, allow_unicode=True)
            elif path.endswith(".json"):
                json.dump(info_data, f, indent=4, ensure_ascii=False)

        return True

    return False


def create(path, file_data={}):
    """
    Create settings .yml or .json file from the file_data
    """
    info_data = file_data.get("info", {})
    tool_name = info_data.get("name", "")
    category = info_data.get("category", "")
    version = info_data.get("version", "")
    data = file_data.get("data", {})

    return save(path, data, tool_name, category, version)
