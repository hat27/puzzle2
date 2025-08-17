# -*-coding: utf8-*-
import os
from puzzle2.PzLog import PzLog

TASK_NAME = "preview"

def main(event={}, context={}):
    data = event["data"]
    print("preview: {}".format(data["path"]))
    return {"return_code": 0}

if __name__ == "__main__":
    event = {"data": {"add": 1, "path": "C:/"}}
    main(event)
