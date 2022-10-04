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
        there are error and break_on_exceptions key exists.
        tasks stopped.
        """
        print("")
        print("test_task_failed_then_stopped")

        tasks = {"pre": [{"module": "tasks.win.open_file", "break_on_exceptions": True}],
                 "main": [{"module": "tasks.win.export_file"}]}
        
        data = {"pre": {"path": "somewhere"}, 
                "main": [{"name": "nameA"}, {"name": "nameB"}]}

       
        self.puzzle.play(tasks, data)

        self.assertEqual(self.puzzle.logger.details.get_return_codes(), [5])

    def test_task_failed_stop_but_closure_is_executed(self):
        """
        there are error and break_on_exceptions key exists.
        tasks stopped.
        but special step "closure" will executed.
        sometime, closere data will generate inside other tasks.
        so, I add dummy data to 'common'.
        """
        print("")
        print("test_task_failed_stop_but_closure_is_executed")

        tasks = {"pre": [{"module": "tasks.win.open_file", "break_on_exceptions": True}],
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
        # add 3 main data inside "init"
        # task runs 2(init) + 3(main) times.runturn_code must be five 0
       
        self.puzzle.play(tasks, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0, 0, 0, 0, 0], return_codes)        

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
        tasks = {"pre": [{"module": "tasks.win.open_file", "break_on_exceptions": True}],
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
    def setUp(self):
        self.puzzle = Puzzle(logger_level=LOGGER_LEVEL, new=True)

    def test_skip_flow(self):
        """
        if every thing skipped?
        what happend to data_globals?
        set 'main' at get_from_scene.
        it will pass through every task till last.
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

    def test_init_is_blank_then_break(self):
        """
        when init data is empty or not exactry what we want.
        stop progress when force flag is True and set return code != [0, 2]
        """
        print("test_init_is_blank_then_break")
        tasks = {"init": [{"module": "tasks.win.open_file"},              # 0
                          {"module": "tasks.win.get_from_scene_empty",    # 1 
                           "force": True}],
                 "main": [{"module": "tasks.win.export_file"}]}           # this tasks were skipped

        data = {"init": {"open_path": "somewhere"}}       
        self.puzzle.play(tasks, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0, 1], return_codes)

    def test_init_is_nothing(self):
        """
        when init data is empty but task need to run.
        do not set force flag True
        """
        print("test_init_is_nothing")
        tasks = {"init": [{"module": "tasks.win.open_file"},             # 0
                          {"module": "tasks.win.get_from_scene_empty"}], # 1
                 "main": [{"module": "tasks.win.export_file"}],          # this tasks were skipped.
                 "post": [{"module": "tasks.win.export_file"}]}          # 0

        data = {"init": {"open_path": "somewhere"}, 
                "post": {"name": "somewhere"}} # data override from "get_from_scene"
       
        self.puzzle.play(tasks, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0, 1, 0], return_codes)

    def test_conditions_skip_and_force_true(self):
        """
        task run when category is chara.
        skip with condition is not error, so every task will run fine.
        """
        print("")
        print("test_conditions_skip_and_force_true")
        tasks = {
                 "main": [
                          {"module": "tasks.win.rename_namespace", 
                           "conditions": [{"category": "chara"}],
                           "force": True
                           }
                         ]
                }

        data = {"main": [{"category": "chara", "name": "charaA"}, # 0
                         {"category": "chara", "name": "charaB"}, # 0
                         {"categery": "bg", "name": "bgA"}, # 2 > skip
                         {"categery": "bg", "name": "bgB"}] # 2 > skip
               }
       
        self.puzzle.play(tasks, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0, 0, 2, 2], return_codes)

    def test_conditions_skip_and_force_true_and_error_occur(self):
        """
        task run when category is bg.but some error inside script.
        then stop all because force key is True.
        """
        print("")
        print("test_conditions_skip_and_force_true_and_error_occur")
        tasks = {
                 "main": [
                          {"module": "tasks.win.rename_namespace_with_error", 
                           "conditions": [{"categery": "bg"}],
                           "force": True
                           }
                         ]
                }

        # tasks will stop at bg category because of script error
        data = {"main": [{"category": "chara", "name": "charaA"}, # 2 skip task
                         {"category": "chara", "name": "charaB"}, # 2 skip task
                         {"categery": "bg", "name": "bgA"}, # 4 error
                         {"categery": "bg", "name": "bgB"}]
               }
       
        self.puzzle.play(tasks, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([2, 2, 4], return_codes)

if __name__ == "__main__":
    unittest.main()
