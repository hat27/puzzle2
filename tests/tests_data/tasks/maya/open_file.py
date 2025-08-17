# -*-coding: utf8-*-
"""
Maya task: open a new scene or open an existing path.
This module is imported by Maya runtime; keep imports lazy to avoid ImportError during normal pytest runs.
"""

import os

DATA_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "sandbox", "convert_test")).replace("\\", "/")


def main(event={}, context={}):
    data = event.get("data", {})
    try:
        import maya.cmds as cmds  # lazy import
    except Exception:
        # Not in Maya; indicate skip/noop
        return {"return_code": 4}

    if data.get("new"):
        cmds.file(new=True, force=True)
    else:
        path = data.get("open_path") or os.path.join(DATA_ROOT, "data", "asset_cube.ma")
        cmds.file(path, open=True, force=True)

    return {"return_code": 0}
