import os
import sys

puzzle_directory = os.environ.get("PUZZLE_DIRECTORY", "")
if puzzle_directory != "":
    sys.path.insert(0, puzzle_directory)

sys.path.insert(0, puzzle_directory)
app = os.environ.get("PUZZLE_APP", "")

from puzzle2.PuzzleBatch import PuzzleBatch

if "mayapy" in app:
    import maya.standalone 
    maya.standalone.initialize(name="python")
    __STANDALONE__ = True
else:
    __STANDALONE__ = False

batch = PuzzleBatch()
batch.start()

if __STANDALONE__:
    try:
        maya.standalone.uninitialize()
    except:
        pass
    os._exit(0)