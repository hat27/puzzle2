# -*- coding: utf8 -*-

import os

_TEMP_PATH_ = os.environ["TEMP"].split(";")[0].replace("\\", "/")
_PLATFORM_ = False
try:
    import maya.cmds
    _PLATFORM_ = "maya"
except:
    pass

try:
    from pyfbsdk import FBSystem
    _PLATFORM_ = "mobu"
except:
    pass

if not _PLATFORM_:
    _PLATFORM_ = "win"


def get_log_template():
    return os.path.normpath(os.path.join(__file__, "../log.template")).replace("\\", "/")


def get_temp_directory(relative=""):
    path = "%s/puzzle/%s" % (_TEMP_PATH_, relative)
    if not os.path.exists(path):
        os.makedirs(path)
    if path.endswith("/"):
        path = path[:-1]
    return path


def get_log_directory():
    return get_temp_directory("log")


def get_user_name():
    if "PUZZLE_USERNAME" in os.environ:
        return os.environ["PUZZLE_USERNAME"]
    return os.environ["USERNAME"]


def get_platform():
    return _PLATFORM_