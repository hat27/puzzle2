# -*-coding: utf8-*-
"""MotionBuilder: export selected to FBX.
Lazy import pyfbsdk to avoid import error outside of Mobu.
"""
import os

def main(event={}, context={}):
    try:
        from pyfbsdk import (
            FBApplication,
            FBComponentList,
            FBFindObjectsByName,
            FBModelList,
            FBFbxOptions,
        )
    except Exception:
        return {"return_code": 4}

    data = event.get("data", {})
    # Deselect all
    model_list = FBModelList()
    # FBGetSelectedModels(model_list)  # Selecting via name below
    component = FBComponentList()
    model_name = f"{data.get('namespace') + ':' if data.get('namespace') else ''}{data.get('name')}"
    FBFindObjectsByName(str(model_name), component, True, True)
    for model in component:
        model.Selected = True

    save_option = FBFbxOptions(False)
    save_option.SetAll(save_option.kFBElementActionSave, True)
    save_option.EmbedMedia = False
    save_option.SaveSelectedModelsOnly = True
    save_option.ShowFileDialog = False
    save_option.ShowOptionsDialog = False

    path = str(data.get("export_path"))
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        FBApplication().FileSave(path, save_option)
    return {"return_code": 0}
