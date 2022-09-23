# -*-coding: utf8-*-
import os
from puzzle2.PzLog import PzLog

PIECE_NAME = "get_from_scene"

def main(event={}, context={}):
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    data_globals = event.get("data_globals", {})
    data_globals["main"] = [{"name": "a", "category": "ch"}, 
                            {"name": "b", "category": "ch"}, 
                            {"name": "c", "category": "prop"}]

    logger.debug("add data: {}".format(data_globals))

    return {"return_code": 0, "data_globals": data_globals}


if __name__ == "__main__":
    event = {"data": {"open_path": "A"}}
    main(event)