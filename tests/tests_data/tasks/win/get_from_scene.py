# -*-coding: utf8-*-
import os
from puzzle2.PzLog import PzLog

PIECE_NAME = "get_from_scene"

def main(event={}, context={}):
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    update_context = {}
    update_context["main"] = [{"name": "a", "category": "ch"}, 
                              {"name": "b", "category": "ch"}, 
                              {"name": "c", "category": "prop"}]

    logger.debug("add data: {}".format(update_context))

    return {"return_code": 0, "update_context": update_context}


if __name__ == "__main__":
    event = {"data": {"open_path": "A"}}
    main(event)