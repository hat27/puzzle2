# -*-coding: utf8-*-
import os

def main(event={}, context={}):
    try:
        import maya.cmds as cmds
    except Exception:
        return {"return_code": 4}

    data = event.get("data", {})
    mov_path = data.get("mov_path")
    if mov_path:
        os.makedirs(os.path.dirname(mov_path), exist_ok=True)
        open(mov_path, "w").close()
    return {"return_code": 0}
