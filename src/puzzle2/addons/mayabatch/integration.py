import os


def get_app_path(version, program_directory=None):
    program_directory = program_directory or os.environ["PROGRAMFILES"].replace("\\", "/")
    if int(version) >= 2022:
        path = "{}/Autodesk/Maya{}/bin/maya.exe".format(program_directory, version)
    else:
        path = "{}/Autodesk/Maya{}/bin/mayabatch.exe".format(program_directory, version)
        
    
    return path if os.path.exists(path) else False


def close_event():
    try:
        import maya.cmds as cmds
        cmds.quit(force=True, exitCode=0)
        return True
    except Exception:
        return False


def get_command(**kwargs):
    version = kwargs["version"]
    script_path = kwargs["script_path"]
    app_path = get_app_path(version, kwargs.get("program_directory", None))
    if not app_path:
        return False

    # Use Python 3 compatible execution (Maya 2022+): runpy.run_path with __main__
    py_expr = (
        r"import runpy; "
        r"runpy.run_path(\\\"{}\\\", run_name=\\\"__main__\\\")".format(script_path.replace("\\", "/"))
    )

    if "launcher" in kwargs:
        # When launched via another launcher (e.g., rez), omit the app path here
        return ' -command "python("{}\");"'.format(py_expr)
    else:
        if int(version) >= 2022:
            return '"{}" -batch -command "python(\\"{}\\");"'.format(app_path, py_expr)
        else:
            return '"{}" -command "mayabatch -c \'{}\';"'.format(app_path, py_expr)

