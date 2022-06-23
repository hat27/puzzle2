#-*-coding: utf8 -*-
import os
import sys
import json

app = os.environ.get("__PUZZLE_APP__", "")

if "mayapy" in app:
    import maya.standalone 
    maya.standalone.initialize(name="python")
    __STANDALONE__ = True
else:
    __STANDALONE__ = False

sys.path.append(os.environ["__PUZZLE_PATH__"])
from puzzle.Puzzle import Puzzle

x = Puzzle(file_mode=True)
#results = x.play_as_file_mode()

if __STANDALONE__:
    try:
        maya.standalone.uninitialize()
    except:
        pass
    os._exit(0)
    print("END")

