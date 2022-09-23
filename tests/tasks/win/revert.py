from puzzle2.PzLog import PzLog

TASK_NAME = "revert"
DATA_KEY_REQUIRED = ["revert"]

def main(event={}, context={}):
    """
    this task set to closere and revert things

    key required from data:
        revert: dict
    """

    data = event.get("data", {})
    task = event.get("task", {})
    data_globals = event.get("data_globals", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    for k, v in data["revert"].items():
        logger.debug("{}: {}".format(k, v))

    return {"return_code": return_code, "data_globals": data_globals}


if __name__ == "__main__":
    data = {"revert": {"a": "b"}}
    main(event={"data": data})