# -*- coding: utf8 -*-

import os
import json
import codecs
try:
    import yaml
except BaseException:
    pass


def read(path):
    """
    :type path: read file (.json, .yml)
    :param path:
    :return: info, data
    """
    info, data = False, False
    if path.endswith(".yml"):
        with codecs.open(path, "r", "utf8") as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
            return data["info"], data["data"]

    elif path.endswith(".json"):
        with codecs.open(path, "r", encoding="utf8") as f:
            data = json.load(f)
            return data["info"], data["data"]

    return info, data


def save(path, data, tool_name="", category="", version=""):
    """
    :param path: save path (.json, .yml)
    :param data:  save data
    :param tool_name:  info
    :param category:  info
    :param version:  info
    :return:  bool
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    info_data = {"info": {"name": tool_name,
                          "category": category,
                          "version": version},
                 "data": data}

    if path.endswith(".yml"):
        f = codecs.open(path, "w", "utf8")
        f.write(yaml.safe_dump(info_data,
                               default_flow_style=False,
                               encoding='utf-8',
                               allow_unicode=True))
        f.close()
        return True

    elif path.endswith(".json"):
        try:
            json.dump(info_data, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=4)
        except BaseException:
            json.dump(info_data, open(path, "w"), "utf8", indent=4)

        return True

    return False

