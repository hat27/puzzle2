# -*-coding: utf8-*-
"""Create a cube and save asset path into context (Maya).
Lazy-import Maya modules so tests without Maya don't crash.
"""
import os

DATA_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "sandbox", "convert_test")).replace("\\", "/")


def main(event={}, context={}):
    try:
        import maya.cmds as cmds  # lazy import
    except Exception:
        return {"return_code": 4}

    asset_path = f"{DATA_ROOT}/data/asset_cube.ma"
    if not os.path.exists(asset_path):
        cmds.polyCube(name="model")
        cmds.file(rename=asset_path)
        cmds.file(save=True, type="mayaAscii")

    update_context = {"create_cube.asset_path": asset_path}
    return {"return_code": 0, "update_context": update_context}
