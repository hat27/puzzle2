#!/usr/bin/python
# -*- coding:utf-8 -*-
# ****** SETTINGS START (DO NOT TOUCH) ******
# PRESET TYPE: PY
# PRESET ICON: open_file.png
# PRESET NAME: Clean Unknown Plugins
# PRESET COLOR: 0,168,120
# DESCRIPTION: ファイルを開く
# BACKUP FILE: Yes
# SAVEAS FILE: No
# SAVE FILE: Yes
# OPEN AS: open
# ****** SETTINGS END (DO NOT TOUCH) ******

import os
from puzzle2.PzLog import PzLog

TASK_NAME = "OpenFile"
DATA_KEY_REQUIRED = ["open_path"]

def main(event={}, context={}):
    data = event.get("data", {})
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    task = event.get("task", {})
    update_context = {}

    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger

    header = ""

    if data["open_path"] is None:
        logger.debug("open new")
        header = u"file opened: new"
        logger.details.add_detail("file opened: new")
        # print("|RESULT| file opened: new")

    elif os.path.exists(data["open_path"]):
        header = u"file opened: {}".format(data["open_path"])
        logger.debug(header)
        logger.details.add_detail("file opened: {}".format(data["open_path"]))
        # print("|RESULT| file opened: new")

    else:
        header = u"file opened: new"
        logger.debug(header)
        logger.details.add_detail("file opened: new")
        # print("|RESULT| file opened: new")
    
    logger.details.set_header(0, "open file successed")
    logger.debug("done.")

    update_context["{}.update_context_test".format(TASK_NAME)] = TASK_NAME
    return {"return_code": 0, "update_context_data": update_context}

if __name__ == "__main__":
    event = {"data": {"open_path": "A"}}
    main(event)