import os

def close_event():
    return True

def get_command(**kwargs):
    def _get_app_path(version, program_directory=None):
        path = False
        program_directory = program_directory or os.environ["PROGRAMFILES"].replace("\\", "/")
        path = "{}/Autodesk/Maya{}/bin/mayapy.exe".format(program_directory, version)
        return path

    version = kwargs.get("version", "")
    script_path = kwargs.get("script_path", "")
    app_path = _get_app_path(version, kwargs.get("program_directory", None))
    if not app_path or not os.path.exists(app_path):
        return False

    # Keep API consistent with other addons: return a quoted string command
    if "launcher" in kwargs:
        return r'"{}"'.format(script_path)
    else:
        print(r'mayapy::: "{}" "{}"'.format(app_path, script_path))
        return r'"{}" "{}"'.format(app_path, script_path)