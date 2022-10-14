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

if not APP:
    APP = "win"


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

def get_python_version():
    version_info = sys.version_info
    return {"major": version_info.major, "minor": version_info.minor}

def get_APP():
    return APP

def get_env():
    env = {
        "app": APP,
        "user_name": get_user_name(),
        "datetime": datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S"),
        "os": {"system": platform.system(),
               "release": platform.release(),
               "version": platform.version(),
               "platform": platform.platform()},
        "python_version": get_python_version()

    }
    return env

if __name__ == "__main__":
    print(get_env())