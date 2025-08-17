from puzzle2.PzLog import PzLog

TASK_NAME = "varidate"

def main(event={}, context={}):
    """

    """

    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    if data["test"] == "fail":
        logger.error("Test failed")
        return {"return_code": 1}
    else:
        logger.info("Test passed")
        return {"return_code": 0}

if __name__ == "__main__":
    data = {"": ""}
    main(event={"data": data})