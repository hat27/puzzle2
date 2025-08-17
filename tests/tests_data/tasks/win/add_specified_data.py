# -*-coding: utf8-*-
import os
from puzzle2.PzLog import PzLog

PIECE_NAME = "add_specified_data"

def main(event={}, context={}):
    data = event["data"]
    update_context = {}
    update_context["{}.add".format(PIECE_NAME)] = data["add"]
    return {"update_context": update_context}

if __name__ == "__main__":
    event = {"data": {"add": 1}}
    main(event)
