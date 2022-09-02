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

import os

_PIECE_NAME_ = "ChangeFrame"
piece_data = {}
data = {}
header = ""
details = []
result_type = 0

def execute(pipe_args={}, **kwargs):
    global header
    global details
    global result_type

    logger = kwargs["logger"]

    if logger:
        logger.info("frame is: {}".format(data["frame"]))

    frame = data["frame"] + 100
    pipe_args["frame"] = frame
    print(piece_data)
    if logger:
        logger.info("set frame to: {}".format(frame))
        logger.debug("set frame to: {}".format(frame))
    details.append("change frame to {}".format(frame))

    header = "test"

    print(pipe_args.get("a", "not exists"))

    result_type = 1
    pipe_args["TEST"] = 14253647
    return pipe_args


if __name__ == "__main__":
    # from config file
    piece_data = {"a": 2, "paint": {"frame": "@frame"}}

    # data
    data = {"frame": 156789}

    # from previus job
    pass_data = {"frame": 10}

    execute(logger=None)
    print(header)
