from puzzle2.PzLog import PzLog

TASK_NAME = "rename_namespace"
DATA_KEY_REQUIRED = ["name"]

def main(event={}, context={}):
    """
    this script will be error
    """
    return {"return_code": return_code, "data_globals": data_globals}


if __name__ == "__main__":
    data = {"name": "str"}
    main(event={"data": data})