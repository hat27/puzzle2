#!/usr/bin/python
# -*- coding:utf-8 -*-
# ****** SETTINGS START (DO NOT TOUCH) ******
# PRESET TYPE: PY
# PRESET ICON: change_frame.png
# PRESET NAME: Clean Unknown Plugins
# PRESET COLOR: 0,168,120
# DESCRIPTION: フレーム変更
# BACKUP FILE: Yes
# SAVEAS FILE: No
# SAVE FILE: Yes
# OPEN AS: open
# ****** SETTINGS END (DO NOT TOUCH) ******

import time

TASK_NAME = "export_file"
from puzzle2.PzLog import PzLog

def main(event={}, context={}):
    data = event.get("data", {})
    task = event.get("task", {})
    data_globals = event.get("data_globals", {})
    logger = context.get("logger")    
    if not logger:
        logger = PzLog().logger


    return_code = 0

    logger.debug("export: {}".format(data["name"]))
    logger.details.add_detail("test details")
    
    data_globals.setdefault("{}.export_names".format(TASK_NAME), []).append(data["name"])

    return {"return_code": return_code, "data_globals": data_globals}

if __name__ == "__main__":
    # data
    data = {"name": "ABC"}

    # from previus task
    event = {"data": data}

    main(event)

