# -*- coding: utf8 -*-

import os
import sys
import datetime
import platform

TEMP_PATH = os.environ["TEMP"].split(";")[0].replace("\\", "/")
APP = False

try:
    import maya.cmds
    APP = "maya"
except BaseException:
    pass

try:
    from pyfbsdk import FBSystem
    APP = "mobu"

except BaseException:
    pass

try:
    import pymxs
    APP = "3dsmax"

except BaseException:
    pass

if not APP:
    APP = "win"


def get_puzzle_path():
    return os.path.normpath(os.path.join(__file__, "../")).replace("\\", "/")

def get_puzzle_module_path():
    return os.path.dirname(get_puzzle_path()).replace("\\", "/")

def get_log_template():
    return "{}/log.template".format(get_puzzle_path())

def get_temp_directory(subdir=""):
    path = "%s/%s" % (TEMP_PATH, subdir)
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except BaseException:  # Dir is created between the os.path.isdir and the os.makedirs calls
            if not os.path.isdir(path):
                raise
    if path.endswith("/"):
        path = path[:-1]
    return path


def get_log_directory(modulename="puzzle"):
    return get_temp_directory("{}/log".format(modulename))


def get_user_name():
    if "PUZZLE_USERNAME" in os.environ:
        return os.environ["PUZZLE_USERNAME"]
    return os.environ.get("USERNAME", "unknown")


def get_python_version():
    version_info = sys.version_info
    return {"major": version_info.major, "minor": version_info.minor}


def get_APP():
    return APP


def get_env():
    env = {
        "_app_": APP,
        "_user_name_": get_user_name(),
        "_datetime_": datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S"),
        "_os_": {"system": platform.system(),
                 "release": platform.release(),
                 "version": platform.version(),
                 "platform": platform.platform()},
        "_python_version_": get_python_version()

    }
    return env