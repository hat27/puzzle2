import os
import sys
import json

def main(path=None):
    if path:
        pass
    else:
        path = os.environ["PUZZLE_JOB_PATH"]

    js_data = {}
    if sys.version_info.major == 2:
        with open(path, "r") as f:
            js_data = json.load(f)["data"]
    else:
        with open(path, "r", encoding="utf8") as f:
            js_data = json.load(f)["data"]

    puzzle_directory = js_data["env"]["puzzle_directory"]
    sys.path.insert(0, puzzle_directory)
    if "sys_path" in js_data["env"]:
        for sys_path in [l for l in js_data["env"]["sys_path"].split(";") if l != ""]:
            sys.path.append(sys_path)

    import puzzle2.pz_env as pz_env
    from puzzle2.PuzzleBatch import PuzzleBatch

    log_directory = js_data["env"].get("log_directory", pz_env.get_log_directory())
    log_name = js_data["env"].get("log_name", "puzzle")
    batch = PuzzleBatch(log_directory=log_directory, 
                        name=log_name)

    batch.start(js_data["task_set_path"],
                js_data["data_path"],
                **js_data["env"])


if __name__ in ["__main__", "__builtin__", "builtins"]:
    main()

