from puzzle2.PzLog import PzLog

TASK_NAME = "rename_namespace"
DATA_KEY_REQUIRED = ["name"]

def main(event={}, context={}):
    """
    rename namespace from a to b

    key required from data:
        name: str
    """

    data = event.get("data", {})
    task = event.get("task", {})
    data_globals = event.get("data_globals", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    new_name = "{}_01".format(data["name"])

    logger.debug("new name: {}".format(new_name))

    data_globals["{}.new_name".format(TASK_NAME)] = new_name

    return {"return_code": return_code, "data_globals": data_globals}


if __name__ == "__main__":
    data = {"name": "str"}
    main(event={"data": data})