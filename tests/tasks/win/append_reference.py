# -*-coding: utf8-*-
import os
import copy
from puzzle2.PzLog import PzLog

TASK_NAME = "append_reference"

def main(event={}, context={}):
    data = event["data"]
    print("append reference: {}".format(data["name"]))
    key = "{}.update_context_test".format(TASK_NAME)
    update_context = {}
    if key in context:
        update_context[key] = copy.deepcopy(context[key])
        update_context[key].append(data["name"])
    else:
        update_context = {key: [data["name"]]}
    return {"return_code": 0, "update_context": update_context}

if __name__ == "__main__":
    event = {"data": {"add": 1}}
    main(event)
