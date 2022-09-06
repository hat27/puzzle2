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

PIECE_NAME = "ChangeFrame"
header = "test"
# result_type = 0


def execute(settings={}, data={}, data_piped={}, logger=None, **kwargs):

    if logger:
        logger.info("frame is: {}".format(data["frame"]))

    frame = data["frame"] + 100
    data_piped["frame"] = frame
    print(settings)
    if logger:
        logger.info("set frame to: {}".format(frame))
        logger.debug("set frame to: {}".format(frame))

    logger.details.append("change frame to {}".format(frame))

    header = "test"

    print(data_piped.get("a", "not exists"))

    # logger.error("ERROR occured!")
    # logger.warning("Oops, something is wrong...")
    # logger.success(ui, "FINISHED!")
    # logger.updateUI(ui, "Updated!", level="RESULT")

    data_piped["TEST"] = 14253647
    return data_piped


if __name__ == "__main__":
    # from config file
    settings = {"a": 2, "paint": {"frame": "@frame"}}

    # data
    data = {"frame": 156789}

    # from previus job
    piped_data = {"frame": 10}

    execute(logger=None)
    print(header)
