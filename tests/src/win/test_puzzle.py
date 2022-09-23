import unittest
import os
import sys

from puzzle2.Puzzle import Puzzle

module_path = os.path.normpath(os.path.join(__file__, "../../../"))
sys.path.append(module_path)

# set debug if you want to see log detail
LOGGER_LEVEL = "critical"

class PuzzleTestAndTutorial(unittest.TestCase):
    def setUp(self):
        self.puzzle = Puzzle(logger_level=LOGGER_LEVEL, new=True)

    def test_simple(self):
        """
        tasks are all OK.
        """
        print("")
        print("test_simple")

        tasks = {"pre": [{"module": "tasks.win.open_file"}],
                 "main": [{"module": "tasks.win.export_file"}]}
        
        data = {"pre": {"open_path": "somewhere"}, 
                "main": [{"name": "nameA"}, {"name": "nameB"}]}

        
        self.puzzle.play(tasks, data)

        self.assertEqual(self.puzzle.logger.details.get_return_codes(), [0, 0, 0])

    def test_task_failed_but_keep_running(self):
        """
        there are error but tasks keep running
        """

        print("")
        print("test_task_failed_but_keep_running")

        tasks = {"pre": [{"module": "tasks.win.open_file"}],
                 "main": [{"module": "tasks.win.export_file"}]}
        
        data = {"pre": {"path": "somewhere"}, 
                "main": [{"name": "nameA"}, {"name": "nameB"}]}

       
        self.puzzle.play(tasks, data)

        self.assertEqual(self.puzzle.logger.details.get_return_codes(), [5, 0, 0])

    def test_task_failed_then_stopped(self):
        """
        there are error and force key exists.
        tasks stopped.
        """
        print("")
        print("test_task_failed_then_stopped")

        tasks = {"pre": [{"module": "tasks.win.open_file", "force": True}],
                 "main": [{"module": "tasks.win.export_file"}]}
        
        data = {"pre": {"path": "somewhere"}, 
                "main": [{"name": "nameA"}, {"name": "nameB"}]}

       
        self.puzzle.play(tasks, data)

        self.assertEqual(self.puzzle.logger.details.get_return_codes(), [5])

    def test_task_failed_stop_but_closure_is_executed(self):
        """
        there are error and force key exists.
        tasks stopped.
        but special step "closure" will executed.
        sometime, closere data will generate inside other tasks.
        so, I add dummy data to 'common'.
        """
        print("")
        print("test_task_failed_stop_but_closure_is_executed")

        tasks = {"pre": [{"module": "tasks.win.open_file", "force": True}],
                 "main": [{"module": "tasks.win.export_file"}], 
                 "closure": [{"module": "tasks.win.revert"}]}
        
        data = {"pre": {"path": "somewhere"}, 
                "main": [{"name": "nameA"}, {"name": "nameB"}], 
                "common": {"revert": {"attrA": 10, "attrB": 20}}}

       
        self.puzzle.play(tasks, data)

        self.assertEqual(self.puzzle.logger.details.get_return_codes(), [5, 0])

    def test_init_flow(self):
        """
        sometime we want generate data from opening scene
        "init" key is special step for that case.
        """
        print("")
        print("test_init_flow")
        tasks = {"init": [{"module": "tasks.win.open_file"}, 
                          {"module": "tasks.win.get_from_scene"}],
                 "main": [{"module": "tasks.win.export_file"}]}

        data = {"init": {"open_path": "somewhere"}} # data override from "get_from_scene"

       
        self.puzzle.play(tasks, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
       
        self.assertEqual(set([0]), set(return_codes))        

    def test_import_and_rename_and_export(self):
        """
        when we want to export different name from first.
        set data_inputs key to task. then add key to before 'export_file'.

        IMPORTANT:
        if step is loop. data_globals value will overrided.
        if we want to use data_globals at next step, we must set value as list( or maybe dict)
        this is closly breaking rules. but it depend on us.
        """
        print("")
        print("test_import_and_rename_and_export")
        tasks = {"pre": [{"module": "tasks.win.open_file", "force": True}],
                 "main": [{"module": "tasks.win.import_file"}, 
                          {"module": "tasks.win.rename_namespace"}, 
                          {"module": "tasks.win.export_file", 
                           "data_inputs": {
                                "name": "globals.rename_namespace.new_name"
                           }}], 
                "post": [{"module": "tasks.win.submit_to_sg", 
                          "data_inputs": {
                            "assets": "globals.export_file.export_names"
                          }}] 
                }
        
        data = {"pre": {"open_path": "somewhere"}, 
                "main": [{"name": "nameA", "path": "somewhere a"}, 
                         {"name": "nameB", "path": "somewhere b"}], 
                "common": {
                    "shot_code": "ep000_s000_c000",
                    "fps": 24,
                    "start_frame": 101,
                    "end_frame": 200
                    }
                }

       
        self.puzzle.play(tasks, data)
        return_codes = self.puzzle.logger.details.get_return_codes()

        self.assertEqual(set([0]), set(return_codes))

    def test_change_order(self):
        """
        we can change order(default: pre, main, post).
        design free for your tasks
        """
        print("")
        print("test_change_order")
        tasks = {
                 "pre": [{"module": "tasks.win.open_file"}, 
                         {"module": "tasks.win.bake_all"}],
                 "main": [{"module": "tasks.win.export_file"}], 
                 "pre2": [{"module": "tasks.win.open_file"}], 
                 "main2": [{"module": "tasks.win.import_file", 
                            "data_inputs": {
                                "path": "import_path"
                            }}], 
                 "post2": [{"module": "tasks.win.save_file", 
                            "data_inputs": {
                                "path": "save_path"
                            }}], 
                 "closure": [{"module": "tasks.win.submit_to_sg"}]}

        data = {"pre": {"open_path": "somewhere", "assets": ["a", "b"]}, 
                "main": [{"name": "a", "export_path": "somewhere_exp1"}, {"name": "b", "export_path": "somewhere_exp2"}], 
                "pre2": {"open_path": "somewhere2"},
                "main2": [{"name": "a", "import_path": "somewhere_exp1"}, {"name": "b", "import_path": "somewhere_exp2"}], 
                "post2": {"save_path": "somewhere"}, 
                "closure": {"assets": [], "shot_code": "ep000_s000_c000"}}

        self.puzzle.order = ["pre", "main", "pre2", "main2", "post2"]
        self.puzzle.play(tasks, data)
        
        # revert for other task.
        self.puzzle.order = ["pre", "main", "post"]

        return_codes = self.puzzle.logger.details.get_return_codes()
       
        self.assertEqual(set([0]), set(return_codes))


class PuzzleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.puzzle = Puzzle(logger_level=LOGGER_LEVEL, new=True)

    def test_skip_flow(self):
        """
        if every thing skipped?
        what happend to data_globals?
        set 'main' from get_from_scene.
        it will pass through every task and 
        """
        print("")
        print("test_skip_flow")
        tasks = {"pre": [{"module": "tasks.win.get_from_scene"}],
                 "main": [{"module": "tasks.win.import_file", 
                           "conditions": [{"test": ""}]}, 
                          {"module": "tasks.win.rename_namespace", 
                           "conditions": [{"test": ""}]}, 
                          {"module": "tasks.win.export_file", 
                           "conditions": [{"test": ""}], 
                           "data_inputs": {
                                "name": "globals.rename_namespace.new_name"
                           }}], 
                "post": [{"module": "tasks.win.submit_to_sg", 
                          "conditions": [{"test": ""}],
                          "data_inputs": {
                            "assets": "globals.export_file.export_names"
                          }}] 
                }
        
        data = {}

       
        self.puzzle.play(tasks, data)

        names = [l["name"] for l in self.puzzle.data_globals["main"]]
        self.assertEqual("a,b,c", ",".join(names))


if __name__ == "__main__":
    unittest.main()
