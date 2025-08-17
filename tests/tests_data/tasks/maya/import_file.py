# -*-coding: utf8-*-
import os

def main(event={}, context={}):
    try:
        import maya.cmds as cmds
    except Exception:
        return {"return_code": 4}

    data = event.get("data", {})
    if path := data.get("import_path"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        cmds.file(
            path,
            i=True,
            type="mayaAscii",
            ignoreVersion=True,
            ra=True,
            mergeNamespacesOnClash=False,
            namespace=data.get("namespace", "ns"),
            options="v=0;p=17;f=0",
            pr=True,
        )
    return {"return_code": 0}
