import os

def get_app_path(version, program_directory=None):
    path = False
    program_directory = program_directory or os.environ["PROGRAMFILES"].replace("\\", "/")
    path = "{}/Autodesk/Maya{}/bin/mayabatch.exe".format(program_directory, version)
    return path

def close_event():
    return True

def get_command(**kwargs):
    version = kwargs["version"]
    script_path = kwargs["script_path"]
    app_path = get_app_path(version, kwargs.get("program_directory", None))
    if not app_path:
        return False

    if "launcher" in kwargs:
        return r''' -command "python(\\"execfile('{}')\\");"'''.format(app_path, script_path)
    else:
        return r'''"{}" -command "python(\\"execfile('{}')\\");"'''.format(app_path, script_path)
