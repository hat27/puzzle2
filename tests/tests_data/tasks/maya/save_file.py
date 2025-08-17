# -*-coding: utf8-*-

def main(event={}, context={}):
    try:
        import maya.cmds as cmds
    except Exception:
        return {"return_code": 4}

    data = event.get("data", {})
    if save := data.get("save_path"):
        cmds.file(rename=save)
        cmds.file(save=True, type="mayaAscii")
    return {"return_code": 0}
