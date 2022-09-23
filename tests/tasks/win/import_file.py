from puzzle2.PzLog import PzLog

TASK_NAME = "import_file"
DATA_KEY_REQUIRED = ["path"]

def main(event={}, context={}):
    """
    import file from somewhare

    key required from data:
        path: str
    """

    data = event.get("data", {})
    task = event.get("task", {})
    data_globals = event.get("data_globals", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    return {"return_code": return_code, "data_globals": data_globals}


if __name__ == "__main__":
    data = {"path": "str"}
    main(event={"data": data})