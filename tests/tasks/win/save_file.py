#!/usr/bin/python
# -*- coding:utf-8 -*-
# ****** SETTINGS START (DO NOT TOUCH) ******
# PRESET TYPE: PY
# PRESET ICON: save_file.png
# PRESET NAME: Clean Unknown Plugins
# PRESET COLOR: 0,168,120
# DESCRIPTION: 不要なプラグインの削除＋シーン保存
# BACKUP FILE: Yes
# SAVEAS FILE: No
# SAVE FILE: Yes
# OPEN AS: open
# ****** SETTINGS END (DO NOT TOUCH) ******

import os
from puzzle2.PzLog import PzLog

TASK_NAME = "SaveFile"

def main(event={}, context={}):
    data = event.get("data", {})
    update_context = {}
    logger = context.get("logger")
    if not logger:
        logger = PzLog().logger


    header = u"file saved to: {}".format(data["path"])
    logger.debug(header)
    logger.details.add_detail("file saved to: {}".format(data["path"]))
    print("|RESULT| file saved to: {}".format(data))

    update_context["{}.update_context_test".format(TASK_NAME)] = TASK_NAME
    return {"return_code": 0, "update_context_data": update_context}

if __name__ == "__main__":
    event = {"data": {"path": "A"}}

    main(event)