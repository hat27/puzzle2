from puzzle2.PzLog import PzLog

TASK_NAME = "mock"

DATA_KEY_REQUIRED = ["name"]

def main(event={}, context={}):
    """
    this is for testing

    key required from data:
        name: something
    """

    data = event.get("data", {})
    task = event.get("task", {})
    update_context = {}

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    logger.debug(data["name"])

    update_context["{}.new_name".format(TASK_NAME)] = "new_name"

    return {"return_code": return_code, "update_context_data": update_context}


if __name__ == "__main__":
    data = {"name": "something"}
    main(event={"data": data})