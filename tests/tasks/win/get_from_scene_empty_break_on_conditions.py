# -*-coding: utf8-*-
import os
from puzzle2.PzLog import PzLog

PIECE_NAME = "get_from_scene_empty_break_on_conditions"

def main(event={}, context={}):
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    update_context = {}
    return {"return_code": 0, "update_context": update_context, "break_on_conditions": True}


if __name__ == "__main__":
    event = {"data": {"open_path": "A"}}
    print(main(event))