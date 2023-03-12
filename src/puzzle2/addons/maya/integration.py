import os
import traceback

def get_app_path(version, root_path=None):
    path = False
    root_path = root_path or os.environ["PROGRAMFILES"].replace("\\", "/")
    path = "{}/Autodesk/Maya{}/bin/maya.exe".format(root_path, version)
    return path if os.path.exists(path) else False

def close_event():
    import maya.mel as mm
    try:
        mm.eval('scriptJob -cf "busy" "quit -f -ec 0";')
        flg = True
    except BaseException:
        print(traceback.format_exc())
        flg = False

def get_command(version, **kwargs):
    app_path = get_app_path(version, kwargs.get("root_path", None))
    if not app_path:
        return False

    puzzle_directory = kwargs["puzzle_directory"]
    job_path = kwargs["job_path"]

    cmd = '{} -command '.format(app_path)
    cmd += '"python(\\\"import sys;import os;sys.path.append(\\\\\\"{}\\\\\\");'.format(puzzle_directory)
    if "sys_path" in kwargs:
        for path in [l for l in kwargs["sys_path"].split(";") if l != ""]:
            cmd += 'sys.path.append(\\\\\\"{}\\\\\\");'.format(path)
    cmd += 'import puzzle2.batch_kicker as batch_kicker;batch_kicker.main(\\\\\\"{}\\\\\\");'.format(job_path)
    cmd += 'x.start()\\\");'
    return cmd