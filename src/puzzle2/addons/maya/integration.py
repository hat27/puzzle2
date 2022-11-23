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
    log_name = kwargs["log_name"]

    cmd = '{} -command '.format(app_path)
    cmd += '"python(\\\"import sys;import os;sys.path.append(\\\\\\"{}\\\\\\");'.format(puzzle_directory)
    cmd += 'from puzzle2.PuzzleBatch import PuzzleBatch;x=PuzzleBatch(\\\\\\"{}\\\\\\");'.format(log_name)
    cmd += 'x.start()\\\");'
    return cmd