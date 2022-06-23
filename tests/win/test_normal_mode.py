#-*- coding: utf8 -*-

import os
import sys


module_path = os.path.normpath(os.path.join(__file__, "../../../tests/"))
if not module_path in sys.path:
  sys.path.append(module_path)

sys.dont_write_bytecode = True


from puzzle2.Puzzle import Puzzle

pieces = {
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

x = Puzzle("sample", new=True, update_log_config=True)
results = x.play(pieces, data, {})

for result in results:
  print(result)