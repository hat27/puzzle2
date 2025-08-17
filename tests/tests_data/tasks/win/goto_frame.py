#!/usr/bin/python
# -*- coding:utf-8 -*-
# ****** SETTINGS START (DO NOT TOUCH) ******
# PRESET TYPE: PY
# PRESET ICON: goto_frame.png
# PRESET NAME: Clean Unknown Plugins
# PRESET COLOR: 0,168,120
# DESCRIPTION: フレーム移動
# BACKUP FILE: Yes
# SAVEAS FILE: No
# SAVE FILE: Yes
# OPEN AS: open
# ****** SETTINGS END (DO NOT TOUCH) ******

import os
from puzzle2.PzLog import PzLog

PIECE_NAME = "GotoFrame"

def main(event={}, context={}):
    status = 1
    logger = context.get("logger", PzLog().logger)
    logger.debug("test")

    return {"return_code": status}

if __name__ == "__main__":
    main()