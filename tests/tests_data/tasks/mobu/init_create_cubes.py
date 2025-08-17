# -*-coding: utf8-*-
"""MotionBuilder: create sample cubes and update context with per-item paths."""

import os
import random

def main(event={}, context={}):
    try:
        from pyfbsdk import FBModelCube, FBSystem, FBPlayerControl, FBTime
    except Exception:
        return {"return_code": 4}

    data_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "sandbox", "convert_test", "data")).replace("\\", "/")

    def add_trs(model, xyz, frame):
        t = FBTime(0, 0, 0, frame)
        model.Translation.SetAnimated(True)
        for i, v in enumerate(xyz):
            if v is not None:
                model.Translation.GetAnimationNode().Nodes[i].FCurve.KeyAdd(t, v)

    # Build synthetic scene
    model_name = "model"
    models = []
    main = []
    for i in range(3):
        namespace = f"Cube{i:02d}"
        cube = FBModelCube(f"{namespace}:{model_name}")
        cube.Show = True
        for j in range(3):
            add_trs(cube, [random.randint(0, 10) for _ in range(3)], j * 10)
        models.append(cube.Name)
        main.append({
            "namespace": namespace,
            "name": model_name,
            "export_fbx_path": f"{data_root}/{namespace}_export.fbx",
            "asset_save_path": f"{data_root}/{namespace}_import.ma",
        })

    post = {
        "save_path": f"{data_root}/result_file.ma",
        "mov_path": f"{data_root}/result_file.mov",
    }

    FBPlayerControl().LoopStop = FBTime(0, 0, 0, 30)
    FBSystem().Scene.Evaluate()

    update_context = {"main": main, "pre": {"models": models}, "post": post}
    return {"update_context": update_context, "return_code": 0}
