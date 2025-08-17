import os

def close_event():
    from pyfbsdk import FBApplication
    FBApplication().FileExit()
    return True

def get_command(**kwargs):
    def _get_app_path(version, program_directory=None):
        program_directory = program_directory or os.environ["PROGRAMFILES"].replace("\\", "/")
        path = r"{}/Autodesk/MotionBuilder {}/bin/x64/motionbuilder.exe".format(program_directory, version)
        return os.path.normpath(path)

    version = kwargs["version"]
    script_path = kwargs["script_path"]
    app_path = _get_app_path(version, kwargs.get("program_directory", None))

    # Verify executable exists
    if not os.path.exists(app_path):
        return False

    if "launcher" in kwargs:
        return r' -suspendMessages -g 50 50 "{}"'.format(app_path, script_path)
    else:
        return r'"{}" -suspendMessages -g 50 50 "{}"'.format(app_path, script_path)

def add_env(**kwargs):
    version = kwargs["version"]
    env = {}
    if version == "2022":
        env["MOTIONBUILDER_PLUGIN_PATH"] = "C:/Program Files/Autodesk/MotionBuilder {}/bin/x64/plugins".format(version)

    return env
