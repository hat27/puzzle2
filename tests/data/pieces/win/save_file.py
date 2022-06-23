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
from puzzle2.Piece import Piece

_PIECE_NAME_ = "SaveFile"

class SaveFile(Piece):
    def __init__(self, **args):
        super(SaveFile, self).__init__(**args)
        self.name = _PIECE_NAME_

    def execute(self, pipe_args={}):
        self.header = "file save"

        self.header = u"file saved to: {}".format(self.data["path"])
        self.logger.debug(self.header)
        self.details.append("file saved to: {}".format(self.data["path"]))
        print("|RESULT| file saved to: {}".format(self.data))

        self.result_type = "successed"

        return self.pass_data
