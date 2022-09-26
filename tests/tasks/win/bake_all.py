from puzzle2.PzLog import PzLog

TASK_NAME = "bake_all"
DATA_KEY_REQUIRED = ["assets"]

def main(event={}, context={}):
    """
    bake all assets

    key required from data:
        assets: list
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
    data = {"assets": [{"name": "a"}, {"name": "b"}]}
    main(event={"data": data})