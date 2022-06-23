#-*- coding: utf8 -*-

import os
import sys

module_path = os.path.normpath(os.path.join(__file__, "../../../tests/"))
print(__file__)
print(module_path)
if not module_path in sys.path:
  sys.path.append(module_path)
  print("ADD", module_path)

sys.dont_write_bytecode = True

import puzzle2.pz_env as env
from puzzle2.Puzzle import Puzzle

print(sys.path)
all_pieces = {
             "test_piece":{
                           "primary": [
                                       {
                                        "name": "open_file",
                                        "description": "this script is for open file",
                                        "piece": "data.pieces.win.open_file",
                                        "paint": {
                                                  "open_path": "maya_open_path"
                                                 }
                                       }                          
                                      ],
                            "main": [
                                       {
                                        "name": "change frame",
                                        "description": "change frame to xx",
                                        "piece": "data.pieces.win.change_frame",
                                        "paint": {
                                                  "frame": "start_frame"
                                                 }
                                       },
                                       {
                                        "name": "goto frame",
                                        "description": "goto frame to xx",
                                        "piece": "data.pieces.win.goto_frame",
                                        "filters": [
                                                    {
                                                      "do_flg": 1
                                                    }
                                        ],
                                        "paint": {
                                                  "frame": "@frame"
                                                 }
                                       },
                                       {
                                        "name": "change frame",
                                        "description": "change frame to xx",
                                        "piece": "data.pieces.win.change_frame",
                                        "paint": {
                                                  "frame": "end_frame"
                                                 }
                                       },
                                       {
                                        "name": "goto frame",
                                        "description": "goto frame to xx",
                                        "piece": "data.pieces.win.goto_frame",
                                        "filters": [
                                                    {
                                                      "do_flg": 1
                                                    }
                                        ],
                                        "paint": {
                                                  "frame": "@frame"
                                                 }
                                       }
                                      ],
                            "post": [
                                      {
                                        "name": "save file",
                                        "description": "save file to",
                                        "piece": "data.pieces.win.save_file",
                                        "paint": {
                                                  "path": "save_path"
                                                 }
                                       }
                                    ]
                            }
              }

data = {
        "primary": {
                    "maya_open_path": None
                   }, 

        "main": [
                 {
                  "start_frame": 1,
                  "end_frame": 1000,
                  "do_flg": 1
                 },
                 {
                  "start_frame": 500,
                  "end_frame": 5000,
                  "do_flg": 0
                 }

                ],

        "post": {
                 "save_path": "D:/project/c001.ma"
                }

       }

root = env.get_temp_directory("sample")
import json
json.dump({"data": data, "info": {}}, open("{}/data.json".format(root), "w", encoding="utf8"), indent=4)
json.dump({"data": all_pieces, "info": {}}, open("{}/all_pieces.json".format(root), "w", encoding="utf8"), indent=4)
os.environ["__PUZZLE_FILE_MODE__"] = "True"
os.environ["__ALL_PIECES_PATH__"] = "%s/all_pieces.json" % root
os.environ["__PUZZLE_DATA_PATH__"] = "%s/data.json" % root
os.environ["__PIECES_KEYS__"] = "test_piece"

x = Puzzle("log_to_temp_path", update_log_config=True)
results = x.play_as_file_mode()
print("")
import pprint
print("RESULTS:")
print(len(results))
for result in results:
  print(result)

