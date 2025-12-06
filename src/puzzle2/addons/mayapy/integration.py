import os
import puzzle2.pz_env as pz_env

def close_event():
    return True

def get_command(**kwargs):
    def _get_app_path(version, program_directory=None):
        path = False
        env = pz_env.get_env()
        if env["_os_"]["system"] == "Darwin":
            path = "/Applications/Autodesk/maya{}/Maya.app/Contents/bin/mayapy".format(version)
        elif env["_os_"]["system"] == "Linux":
            path = "/usr/autodesk/maya{}/bin/mayapy".format(version)
        else:
            program_directory = program_directory or os.environ["PROGRAMFILES"].replace("\\", "/")
            path = "{}/Autodesk/Maya{}/bin/mayapy.exe".format(program_directory, version)
        return path

    version = kwargs.get("version", "")
    script_path = kwargs.get("script_path", "")
    app_path = _get_app_path(version, kwargs.get("program_directory", None))
 

    # Keep API consistent with other addons: return a quoted string command
    if "launcher" in kwargs:
        return r'"{}"'.format(script_path)
    else:
        print("----------------", app_path)
        if not app_path or not os.path.exists(app_path):
            return False
        return r'"{}" "{}"'.format(app_path, script_path)