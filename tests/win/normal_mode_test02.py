#-*- coding: utf8 -*-

import os
from re import L
import sys


module_path = os.path.normpath(os.path.join(__file__, "../../../"))
if not module_path in sys.path:
  sys.path.append(module_path)

sys.dont_write_bytecode = True

from puzzle2.Puzzle import Puzzle, execute_command

tasks = {
            "pre": 
                      [{
                       "name": "reference chara",
                       "description": "reference chara assets",
                       "module": "tests.data.tasks.win.change_frame",
                       "force": True,
                       "inputs": {
                        "frame": "TEST"
                        }
                       },
                       {
                       "name": "reference chara02",
                       "description": "reference chara assets",
                       "module": "tests.data.tasks.win.change_frame",
                       "inputs": {
                                "frame": "globals.TEST"
                                }
                       }
                      ],
            "main": 
                      [{
                       "name": "reference chara03",
                       "description": "reference chara assets",
                       "module": "tests.data.tasks.win.change_frame",
                       "conditions": [{"category": "ch"}]
                       },
                       {
                       "name": "reference chara04",
                       "description": "reference chara assets",
                       "module": "tests.data.tasks.win.change_frame",
                       "inputs": {
                                "frame": "globals.TEST"
                                }
                       }
                      ]

        }

data = {
        "pre": 
                 {
                  "asset_type": "chara",
                  "namespace": "A",
                  "asset_path": "D:/project/A.ma",
                  "frame": 100,
                  "TEST": 1550, 
                  "fbx_path":  "D:/project/c001_A.fbx"
                 }
                ,
        "main": [
                 {
                  "asset_type": "chara",
                  "namespace": "A",
                  "asset_path": "D:/project/A.ma",
                  "frame": 100,
                  "TEST": 1550, 
                  "fbx_path":  "D:/project/c001_A.fbx",
                  "category": "chs"
                 }
                ]                
       }


os.environ["__PUZZLE_PATH__"] = module_path
x = Puzzle("sample", new=True, update_log_config=True)
results = x.play(tasks, data)
import pprint
print("header:")
pprint.pprint(x.logger.details.get_header())

print("all:")
pprint.pprint(x.logger.details.get_all())
