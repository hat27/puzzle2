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
    update_context = {}

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0
    logger.debug("revert run")
    for k, v in data.get("revert", {}).items():
        logger.debug("{}: {}".format(k, v))

    return {"return_code": return_code, "update_context_data": update_context}


if __name__ == "__main__":
    data = {"revert": {"a": "b"}}
    main(event={"data": data})