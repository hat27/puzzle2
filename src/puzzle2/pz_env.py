# -*- coding: utf8 -*-

import os

TEMP_PATH = os.environ["TEMP"].split(";")[0].replace("\\", "/")
PLATFORM = False
try:
    import maya.cmds
    PLATFORM = "maya"
except BaseException:
    pass

try:
    from pyfbsdk import FBSystem
    PLATFORM = "mobu"
except BaseException:
    pass

if not PLATFORM:
    PLATFORM = "win"


def get_log_template():
    return os.path.normpath(os.path.join(__file__, "../log.template")).replace("\\", "/")


def get_temp_directory(subdir=""):
    path = "%s/%s" % (TEMP_PATH, subdir)
    if not os.path.exists(path):
        os.makedirs(path)
    if path.endswith("/"):
        path = path[:-1]
    return path


def get_log_directory(modulename="puzzle"):
    return get_temp_directory("{}/log".format(modulename))


def get_user_name():
    if "PUZZLE_USERNAME" in os.environ:
        return os.environ["PUZZLE_USERNAME"]
    return os.environ["USERNAME"]


def get_platform():
    return PLATFORM
