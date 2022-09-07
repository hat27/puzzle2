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

PIECE_NAME = "ChangeFrame"


def execute(task={}, data={}, data_piped={}, logger=None, **kwargs):

    if logger:
        logger.info("frame is: {}".format(data["frame"]))

    frame = data["frame"] + 100
    data_piped["frame"] = frame

    if logger:
        logger.info("set frame to: {}".format(frame))
        logger.debug("set frame to: {}".format(frame))

        logger.details.append({"details": "change frame to {}".format(frame),
                               "name": task.get("name", "untitled"),
                               "header": "set frame task",
                               "status": 1,
                               "comment": task.get("comment")})

    # logger.error("ERROR occured!")
    # logger.warning("Oops, something is wrong...")
    # logger.success(ui, "FINISHED!")
    # logger.updateUI(ui, "Updated!", level="RESULT")

    data_piped["TEST"] = 14253647
    status = 1
    return {"status_code": status, "data_piped": data_piped}


if __name__ == "__main__":
    # from config file
    task = {"a": 2, "paint": {"frame": "@frame"}}

    # data
    data = {"frame": 156789}

    # from previus task
    data_piped = {"frame": 10}

    execute(task, data, data_piped, logger=None)
