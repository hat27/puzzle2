import os
import importlib
import traceback

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
        program_path = "rez"
        return program_path

    def _get_addon(app):
        global ADDON_PATH
        script_root = pz_env.get_puzzle_path()
        path = "{}/addons/customs/{}".format(script_root, app)
        if os.path.exists(path):
            ADDON_PATH = "puzzle2.addons.customs.{}.integration".format(app)
        ADDON_PATH = "puzzle2.addons.{}.integration".format(app)

        try:
            addon = importlib.import_module(ADDON_PATH)
            reload(addon)
            return addon

        except ImportError:
            print(traceback.format_exc())
            return False

    app_path = _get_app_path(kwargs.get("program_path", None))
    if not app_path:
        return False
    
    rez_package = kwargs["rez_package"]
    rez_version = kwargs["rez_version"]

    app = kwargs["app"]
    app_package = kwargs["app_package"]

    addon = _get_addon(app)
    if not addon:
        return False

    cmd = addon.get_command(**kwargs)
    return "{} env {}-{} {} -- {} {}".format(app_path, rez_package, rez_version, app_package, app, cmd)


if __name__ == "__main__":
    data = {"app": "mayapy", 
            "rez_package": "projectA", 
            "rez_version": "1.0.0", 
            "app_package": "maya", 
            "script_path": "xxxxx.py",
            "launcher": "rez"}
    
    print(get_command(**data))