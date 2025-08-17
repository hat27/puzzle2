import os
import sys
import json

try:
    import maya.standalone
    maya.standalone.initialize("python")    
except:
    pass
class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        return str(o)

def main(path=None):
    # Resolve config path
    if not path:
        if "PUZZLE_JOB_PATH" in os.environ:
            path = os.environ["PUZZLE_JOB_PATH"]
        else:
            root = sys.argv[-1]
            path = "{}/config.json".format(root)
            if not os.path.exists(path):
                raise Exception("No config.json found in {}".format(root))

    # Load job config
    if sys.version_info.major == 2:
        with open(path, "r") as f:
            js_data = json.load(f)["data"]
    else:
        with open(path, "r", encoding="utf8") as f:
            js_data = json.load(f)["data"]

    # Prepare sys.path for puzzle2 and optional extras
    puzzle_directory = js_data["env"]["puzzle_directory"]
    if puzzle_directory not in [p.replace("\\", "/") for p in sys.path]:
        sys.path.insert(0, puzzle_directory)
    if "sys_path" in js_data["env"] and js_data["env"]["sys_path"]:
        for sys_path in [l for l in js_data["env"]["sys_path"].split(";") if l != ""]:
            if sys_path not in [p.replace("\\", "/") for p in sys.path]:
                sys.path.append(sys_path)

    # Now we can import internal modules
    import puzzle2.pz_env as pz_env
    from puzzle2.PuzzleBatch import PuzzleBatch
    from puzzle2.PzLog import PzLog

    # Initialize PzLog early to capture batch_kicker lifecycle
    log_directory = js_data["env"].get("log_directory", pz_env.get_log_directory())
    log_name = js_data["env"].get("log_name", "puzzle")
    Log = PzLog(name=log_name, log_directory=log_directory, new=True)
    logger = Log.logger
    logger.info("batch_kicker: start")
    logger.debug("config path: {}".format(path))

    # Run batch
    # Pass the underlying logging.Logger to avoid wrapper mismatch
    batch = PuzzleBatch(log_directory=log_directory, name=log_name, logger=logger)
    headers, results, context = batch.start(
        js_data["task_set_path"],
        js_data["data_path"],
        js_data.get("context_path", None),
        **js_data["env"]
    )

    # Write results
    result_path = js_data["env"]["result_path"]
    if not os.path.exists(os.path.dirname(result_path)):
        os.makedirs(os.path.dirname(result_path))

    result_data = {
        "info": {},
        "data": {"headers": headers, "results": results, "context": context},
    }
    if sys.version_info.major == 2:
        with open(result_path, "w") as f:
            json.dump(result_data, f, indent=4, cls=CustomEncoder)
    else:
        with open(result_path, "w", encoding="utf8") as f:
            json.dump(result_data, f, indent=4, cls=CustomEncoder)

    logger.info("batch_kicker: done -> {}".format(result_path))


if __name__ in ["__main__", "__builtin__", "builtins"]:
    main()

