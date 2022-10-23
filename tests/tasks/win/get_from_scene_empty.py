# -*-coding: utf8-*-
import os
from puzzle2.PzLog import PzLog

PIECE_NAME = "get_from_scene"

def main(event={}, context={}):
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    update_context = {}
    update_context["main"] = []

    logger.debug("add data: {}".format(update_context))
    if len(update_context["main"]) == 0:
        return {"return_code": 1, "update_context_data": update_context}
    else:
        return {"return_code": 0, "update_context_data": update_context}


if __name__ == "__main__":
    event = {"data": {"open_path": "A"}}
    print(main(event))