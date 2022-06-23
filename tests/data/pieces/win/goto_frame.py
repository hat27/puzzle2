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
from puzzle2.Piece import Piece

_PIECE_NAME_ = "GotoFrame"

class GotoFrame(Piece):
    def __init__(self, **args):
        super(GotoFrame, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self, pipe_args={}):
        self.header = "goto frame"
        self.logger.debug("goto frame to: {}".format(self.data["frame"]))

        return self.pass_data
