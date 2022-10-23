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

TASK_NAME = "ChangeFrame"
from puzzle2.PzLog import PzLog

def main(event={}, context={}):
    data = event.get("data", {})
    task = event.get("task", {})
    update_context = {}
    logger = context.get("logger")    
    if not logger:
        logger = PzLog().logger
    return_code = 0

    logger.info("frame is: {}".format(data["frame"]))

    frame = data["frame"] + 100
    update_context["frame"] = frame
    update_context["XXXXX"] = "abcde"

    logger.info("set frame to: {}(info)".format(frame))
    logger.debug("set frame to: {}(debug)".format(frame))

    logger.details.add_detail("test details")
    logger.details.set_header(0, "change frame to: {}".format(frame))

    # logger.error("ERROR occured!")
    # logger.warning("Oops, something is wrong...")
    # logger.success(ui, "FINISHED!")
    # logger.updateUI(ui, "Updated!", level="RESULT")

    update_context["{}.data_globals_test".format(TASK_NAME)] = TASK_NAME
    return {"return_code": return_code, "update_context_data": update_context}

if __name__ == "__main__":
    # from config file
    task = {"name": "hoge", "a": 2, "paint": {"frame": "@frame"}}

    # data
    data = {"frame": 156789}

    # from previus task

    event = {"task": task, "data": data}

    main(event)
