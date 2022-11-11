import os

def close_event():
    return True

def get_command(**kwargs):
    def _get_app_path(version, program_directory=None):
        program_directory = program_directory or os.environ["PROGRAMFILES"].replace("\\", "/")
        path = r"{}/Autodesk/MotionBuilder {}/bin/x64/mobupy.exe".format(program_directory, version)
        return os.path.normpath(path)

    version = kwargs["version"]
    script_path = kwargs["script_path"]
    app_path = _get_app_path(version, kwargs.get("program_directory", None))

    if "launcher" in kwargs:
        return r' "{}"'.format(app_path, script_path)
    else:
        return r'"{}" "{}"'.format(app_path, script_path)

