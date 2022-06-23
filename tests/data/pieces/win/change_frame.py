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
        frame = self.data["frame"] + 100
        self.pass_data["frame"] = frame
        self.result_type = "successed"
        self.logger.debug("set frame to: {}".format(frame))

        return self.pass_data
