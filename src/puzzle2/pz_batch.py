# -*-coding: utf8 -*-
from puzzle2.Puzzle import Puzzle
import os
import sys
import json

app = os.environ.get("PUZZLE_APP", "")

if "mayapy" in app:
    import maya.standalone
    maya.standalone.initialize(name="python")
    __STANDALONE__ = True
else:
    __STANDALONE__ = False

sys.path.append(os.environ["PUZZLE_PATH"])

x = Puzzle(file_mode=True)
#results = x.play_as_file_mode()

if __STANDALONE__:
    try:
        maya.standalone.uninitialize()
    except BaseException:
        pass
    os._exit(0)
    print("END")
