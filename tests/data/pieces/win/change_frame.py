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
from puzzle2.Piece import Piece

_PIECE_NAME_ = "ChangeFrame"

class ChangeFrame(Piece):
    def __init__(self, **args):
        super(ChangeFrame, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self, pipe_args={}):
        self.header = "file open job"
        self.logger.info("frame is: {}".format(self.data["frame"]))
        frame = self.data["frame"] + 100
        self.pass_data["frame"] = frame
        self.result_type = "successed"
        self.logger.info("set frame to: {}".format(frame))
        self.logger.debug("set frame to: {}".format(frame))
        self.details.append("change frame to {}".format(frame))

        print(self.piece_data.get("a", "not exists"))

        return self.pass_data


if __name__ == "__main__":
    # from config
    piece = {"a": 2, "paint": {"frame": "@frame"}}

    # data
    data = {"frame": 1}

    # from previus job
    pass_data = {"frame": 10}
    x = ChangeFrame(data=data)
    x.execute()

    x = ChangeFrame(piece_data=piece, data=data)
    x.execute()

    x = ChangeFrame(piece_data=piece, data=data, pass_data=pass_data)
    x.execute()    