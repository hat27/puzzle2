#!/usr/bin/python
# -*- coding:utf-8 -*-
# ****** SETTINGS START (DO NOT TOUCH) ******
# PRESET TYPE: PY
# PRESET ICON: open_file.png
# PRESET NAME: Clean Unknown Plugins
# PRESET COLOR: 0,168,120
# DESCRIPTION: ファイルを開く
# BACKUP FILE: Yes
# SAVEAS FILE: No
# SAVE FILE: Yes
# OPEN AS: open
# ****** SETTINGS END (DO NOT TOUCH) ******

import os
from puzzle2.Piece import Piece

_PIECE_NAME_ = "OpenFile"

class OpenFile(Piece):
    def __init__(self, **args):
        super(OpenFile, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self, pipe_args={}):
        self.header = "file open job"
        if self.data["open_path"] is None:
            self.logger.debug("open new")
            self.header = u"file opened: new"
            self.details.append("file opened: new")
            print("|RESULT| file opened: new")

        elif os.path.exists(self.data["open_path"]):
            self.header = u"file opened: {}".format(self.data["open_path"])
            self.logger.debug(self.header)
            self.details.append("file opened: {}".format(self.data["open_path"]))
            print("|RESULT| file opened: new")

        else:
            self.header = u"file opened: new"
            self.logger.debug(self.header)
            self.details.append("file opened: new")
            print("|RESULT| file opened: new")
        
        self.result_type = "successed"

        return self.pass_data
