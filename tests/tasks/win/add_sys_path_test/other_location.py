from puzzle2.PzLog import PzLog

TASK_NAME = "other_location"

def main(event={}, context={}):
    data = event.get("data", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    return {"return_code": return_code}


if __name__ == "__main__":
    data = {"": ""}
    main(event={"data": data})