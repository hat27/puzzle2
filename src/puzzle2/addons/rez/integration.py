import os
import importlib
import traceback

import sys
sys.path.append("/Users/goh/Documents/repo/puzzle2/src")
ADDON_PATH = None
import puzzle2.pz_env as pz_env

try:
    reload
except NameError:
    if hasattr(importlib, "reload"):
        # for py3.4+
        from importlib import reload

def close_event():
    global ADDON_PATH
    try:
        addon = importlib.import_module(ADDON_PATH)
    except ImportError:
        return False
    addon.close_event()
    return True

def get_command(**kwargs):
    def _get_app_path(program_path=None):
        program_path = "rez-env"
        return program_path

    def _get_addon(app):
        global ADDON_PATH
        script_root = pz_env.get_puzzle_path()
        path = "{}/addons/customs/{}".format(script_root, app)
        print('>>>>', path)
        if os.path.exists(path):
            ADDON_PATH = "puzzle2.addons.customs.{}.integration".format(app)
        ADDON_PATH = "puzzle2.addons.{}.integration".format(app)
        print('>>>>', ADDON_PATH)
        try:
            addon = importlib.import_module(ADDON_PATH)
            reload(addon)
            return addon

        except ImportError:
            print(traceback.format_exc())
            return False

    rez_path = _get_app_path(kwargs.get("program_path", None))
    if not rez_path:
        return False
    
    rez_request = kwargs["rez_request"]

    app = kwargs.get("app")

    addon = _get_addon(app)
    if not addon:
        return False
    
    cmd = "{} {}".format(rez_path, rez_request)
    if app:
        cmd += " -- {}".format(app)
        script = addon.get_command(**kwargs)
        if script:
            cmd += " {}".format(script)

    if "command" in kwargs:
        cmd += kwargs["command"]
    
    return cmd

if __name__ == "__main__":
    data = {"app": "mayapy", 
            "rez_package": "projectA", 
            "rez_request": "maya puzzle2",
            "script_path": "xxxxx.py",
            "launcher": "rez"}
    
    print(get_command(**data))