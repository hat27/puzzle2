# -*-coding: utf8-*-
"""Import FBX animation and save Maya scene.
"""

def main(event={}, context={}):
    data = event.get("data", {})
    try:
        import maya.cmds as cmds
    except Exception:
        return {"return_code": 4}

    # Ensure FBX plugin
    if not cmds.pluginInfo("fbxmaya", q=True, l=True):
        try:
            cmds.loadPlugin("fbxmaya")
        except Exception:
            pass

    # Reference asset then import FBX if provided
    if data.get("asset_path"):
        cmds.file(
            data["asset_path"], r=True, gl=False, lrd="all", iv=True, force=True, namespace=data.get("namespace", "ns")
        )

    if (path := data.get("fbx_path")) and path.lower().endswith(".fbx"):
        cmds.file(
            path,
            i=True,
            type="FBX",
            ignoreVersion=True,
            ra=True,
            mergeNamespacesOnClash=False,
            options="v=0;",
            pr=True,
        )

    if save := data.get("save_path"):
        import os

        os.makedirs(os.path.dirname(save), exist_ok=True)
        cmds.file(rename=save)
        cmds.file(save=True, type="mayaAscii")

    return {"return_code": 0}
