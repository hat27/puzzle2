import os

def close_event():
    try:
        import MaxPlus
        MaxPlus.Core.EvalMAXScript("quitMAX quiet:true")
    except:
        pass
    return True

def get_command(**kwargs):
    def _get_app_path(version, program_directory=None):
        path = False
        program_directory = program_directory or os.environ["PROGRAMFILES"].replace("\\", "/")
        path = "{}/Autodesk/3ds Max {}/3dsmax.exe".format(program_directory, version)
        return path

    version = kwargs.get("version", "")
    script_path = kwargs.get("script_path", "")
    app_path = _get_app_path(version, kwargs.get("program_directory", None))
    if not app_path:
        return False

    if "launcher" in kwargs:
        return r'"{}"'.format(script_path)
    else:
        return r'"{}" "{}"'.format(app_path, script_path)