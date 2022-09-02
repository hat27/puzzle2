#-*- coding: utf8 -*-

import os
import sys


module_path = os.path.normpath(os.path.join(__file__, "../../../"))
if not module_path in sys.path:
  sys.path.append(module_path)

sys.dont_write_bytecode = True

print(module_path)
from puzzle2.Puzzle import Puzzle, execute_command

pieces = {
            "main": 
                      [{
                       "name": "reference chara",
                       "description": "reference chara assets",
                       "piece": "tests.data.pieces.win.change_frame",
                       "paint": {
                        "frame": "TEST"
                        }
                       },
                       {
                       "name": "reference chara",
                       "description": "reference chara assets",
                       "piece": "tests.data.pieces.win.change_frame",
                       "paint": {
                                "frame": "@TEST"
                                }
                       }
                      ]
        }

data = {
        "main": [
                 {
                  "asset_type": "chara",
                  "namespace": "A",
                  "asset_path": "D:/project/A.ma",
                  "frame": 100,
                  "TEST": 1550, 
                  "fbx_path":  "D:/project/c001_A.fbx"
                 }
                ]
       }


os.environ["__PUZZLE_PATH__"] = module_path
x = Puzzle("sample", new=True, update_log_config=True)
results = x.play(pieces, data, {})
for result in results:
  print(result)
