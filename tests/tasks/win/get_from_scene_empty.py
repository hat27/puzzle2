# -*-coding: utf8-*-
import os
from puzzle2.PzLog import PzLog

PIECE_NAME = "get_from_scene"

def main(event={}, context={}):
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    data_globals = event.get("data_globals", {})
    data_globals["main"] = []

    logger.debug("add data: {}".format(data_globals))
    if len(data_globals["main"]) == 0:
        return {"return_code": 1, "data_globals": data_globals}
    else:
        return {"return_code": 0, "data_globals": data_globals}


if __name__ == "__main__":
    event = {"data": {"open_path": "A"}}
    print(main(event))