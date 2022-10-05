# -*-coding: utf8-*-
import os
from puzzle2.PzLog import PzLog

PIECE_NAME = "add_specified_data"

def main(event={}, context={}):
    data = event["data"]
    data_globals = event.get("data_globals", {})
    data_globals["{}.add".format(PIECE_NAME)] = data["add"]

if __name__ == "__main__":
    event = {"data": {"add": 1}}
    main(event)
