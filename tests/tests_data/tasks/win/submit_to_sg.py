from puzzle2.PzLog import PzLog

TASK_NAME = "submit_to_sg"
DATA_KEY_REQUIRED = ["shot_code", "assets"]

def main(event={}, context={}):
    """
    submit to shotgrid mook

    key required from data:
        shot_code: str
        assets: list
    """

    data = event.get("data", {})
    task = event.get("task", {})

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    return_code = 0

    logger.debug("submit: {}".format(data["shot_code"], data["assets"]))

    return {"return_code": return_code}


if __name__ == "__main__":
    data = {"shot_code": "ep000_s000_c000", "assets": []}
    main(event={"data": data})