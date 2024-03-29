import unittest
import os
import sys

from puzzle2.Puzzle import Puzzle

module_path = os.path.normpath(os.path.join(__file__, "../../../"))
sys.path.append(module_path)

# set debug if you want to see log detail
LOGGER_LEVEL = "DEBUG"


class PuzzleTestAndTutorial(unittest.TestCase):
    def setUp(self):
        print("")
        self.puzzle = Puzzle(logger_level=LOGGER_LEVEL, new=True, reset_template=True)

    def test_simple(self):
        """
        tasks are all OK.
        """
        print("test_simple")

        steps = [{"step": "pre", "tasks": [{"module": "tasks.win.open_file"}]},
                 {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]}]
        
        data = {"pre": {"open_path": "somewhere"}, 
                "main": [{"name": "nameA"}, {"name": "nameB"}]}
        
        self.puzzle.play(steps, data)

        self.assertEqual(self.puzzle.logger.details.get_return_codes(), [0, 0, 0])

    def test_task_failed_but_keep_running(self):
        """
        there are error but tasks keep running
        """


        print("test_task_failed_but_keep_running")


        steps = [{"step": "pre", 
                  "tasks": [
                            {"module": "tasks.win.open_file"}
                           ]
                 },
                 {"step": "main", 
                  "tasks": [
                            {"module": "tasks.win.export_file"}
                           ]
                }]
        
        data = {"pre": {"path": "somewhere"},  # "open_path" is required but not exists.
                "main": [{"name": "nameA"}, {"name": "nameB"}]}

        self.puzzle.play(steps, data)
        self.assertEqual(self.puzzle.logger.details.get_return_codes(), [5, 0, 0])

    def test_task_failed_then_stopped(self):
        """
        there are error and break_on_exceptions key exists.
        tasks stopped.
        """

        print("test_task_failed_then_stopped")


        steps = [{"step": "pre", "tasks": [{"module": "tasks.win.open_file", "break_on_exceptions": True}]},
                 {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]}]
        
        data = {"pre": {"path": "somewhere"},  # "open_path" is requeired but not exists.then task stopped.
                "main": [{"name": "nameA"}, {"name": "nameB"}]}

        self.puzzle.play(steps, data)
        self.assertEqual(self.puzzle.logger.details.get_return_codes(), [5])

    def test_task_failed_stop_but_closure_is_executed(self):
        """
        there are error and break_on_exceptions key exists.
        tasks stopped.
        but special step "closure" will executed.
        """

        print("test_task_failed_stop_but_closure_is_executed")


        steps = [{"step": "pre", "tasks": [{"module": "tasks.win.open_file", "break_on_exceptions": True}]}, # stop here
                 {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},                           # skip(with no return code)
                 {"step": "closure", "tasks": [{"module": "tasks.win.revert"}]}]                             # closure runs
        
        data = {"pre": {"path": "somewhere"}, 
                "main": [{"name": "nameA"}, {"name": "nameB"}],
                "common": {"revert": {"a": 1}}}
       
        self.puzzle.play(steps, data)
        self.assertEqual(self.puzzle.logger.details.get_return_codes(), [5, 0])

    def test_init_flow(self):
        """
        sometime we want generate data from current scene
        "init" key is special step for that case.
        """

        print("test_init_flow")

        steps = [{"step": "init", "tasks": [{"module": "tasks.win.open_file"}, 
                                           {"module": "tasks.win.get_from_scene"}]}, # generate main data
                 {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]}]

        data = {"init": {"open_path": "somewhere"}} # data override by "get_from_scene" context
        # add 3 main data inside "init"
        # task runs 2(init) + 3(main) times.runturn_code must be five 0

        self.puzzle.play(steps, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0, 0, 0, 0, 0], return_codes)

    def test_update_data_and_use_it_in_other_task(self):
        """
        when we want to export different name from first.
        set data_key_replace key to task. then use key to at 'export_file'.

        IMPORTANT:
            if step is loop. context[data] value will overrided.
            list will replace all.
            dict will updated.
            if we want to use context[data] at next step, we can add to list but we must
            get value from context[data] then add it to them.

            this is closly breaking rules. but it depend on us.
            check export_file script.
        """

        print("test_update_data_and_use_it_in_other_task")
        steps = [{"step": "pre", 
                  "tasks": [{"module": "tasks.win.open_file", "break_on_exceptions": True}]},
                 {"step": "main",
                  "tasks": [{"module": "tasks.win.import_file"}, 
                            {"module": "tasks.win.rename_namespace"},       # rename
                            {"module": "tasks.win.export_file",             # use new name
                            "data_key_replace": {
                                "name": "context.rename_namespace.new_name"
                                }                                           # then add name to the list
                            }
                           ]
                }, 
                {"step": "post", 
                 "tasks": [{"module": "tasks.win.submit_to_sg", 
                          "data_key_replace": {
                            "assets": "context.export_file.export_names"
                          }}]
                }]
        
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
       
        self.puzzle.play(steps, data)
        # self.puzzle.context["rename_namespace.new_name"] will overrided in the loop, 
        # so we only could get the last one.
        self.assertEqual(self.puzzle.context["rename_namespace.new_name"], "nameB_01")
        
        # when we need to get all values from loop.we have to use trick in scripts.
        # but it possible.
        export_names = self.puzzle.context["export_file.export_names"]
        self.assertEqual(["nameA_01", "nameB_01"], export_names)

    def test_data_defaults(self):
        """
        we can add default values at task setting
        in this case, data is blank but default sets 100.
        result is 100
        """

        print("test_data_defaults")

        steps = [{"step": "main", "tasks": [{"module": "tasks.win.add_specified_data", 
                                             "data_defaults": {"add": 100}
                                             }]
                 }]
        
        data = {"main": {}}

        self.puzzle.play(steps, data)
        self.assertEqual(self.puzzle.context["add_specified_data.add"], 100)

        """
        if we have add key in data.
        result is 200
        """
        data = {"main": {"add": 200}}

        self.puzzle.play(steps, data)
        self.assertEqual(self.puzzle.context["add_specified_data.add"], 200)

    def test_data_override(self):
        """
        we can add override values at task setting
        in this case, data is blank but override value is 100.
        result is 100
        """

        print("test_data_override")

        steps = [{"step": "main", "tasks": [{"module": "tasks.win.add_specified_data", 
                                             "data_override": {"add": 100}
                                            }]
                 }]
        
        data = {"main": {}}

        self.puzzle.play(steps, data)
        self.assertEqual(self.puzzle.context["add_specified_data.add"], 100)

        """
        if we have add key in data.
        but override exists. result is 100
        """
        data = {"main": {"add": 50}}

        self.puzzle.play(steps, data)
        self.assertEqual(self.puzzle.context["add_specified_data.add"], 100)

class PuzzleTest(unittest.TestCase):
    def setUp(self):
        print("")
        self.puzzle = Puzzle(logger_level=LOGGER_LEVEL, new=True, reset_template=True)

    def test_skip_flow(self):
        """
        if every thing skipped
        what happend to context[_data]?
        set 'main' at get_from_scene.
        it will pass through every task till last.
        """

        print("test_skip_flow")

        steps = [{"step": "pre", 
                  "tasks": [
                            {"module": "tasks.win.get_from_scene"}  # {"main": [{"name": "a"}, {"name": "b"}, {"name": "c"}]}
                           ]
                 },
                 {"step": "main", 
                  "tasks": [
                            {"module": "tasks.win.import_file", 
                             "conditions": [{"test": ""}]}, 
                            {"module": "tasks.win.rename_namespace", 
                             "conditions": [{"test": ""}]}, 
                            {"module": "tasks.win.export_file", 
                             "conditions": [{"test": ""}], 
                             "data_key_replace": {
                                 "name": "context.rename_namespace.new_name"
                                 }
                            }
                        ]
                }, 
                {"step": "post", "tasks": [{"module": "tasks.win.submit_to_sg", 
                          "conditions": [{"test": ""}],
                          "data_key_replace": {
                            "assets": "context.export_file.export_names"
                          }}] 
                }]
        
        data = {}

        self.puzzle.play(steps, data)

        names = [l["name"] for l in self.puzzle.context["main"]]
        self.assertEqual("a,b,c", ",".join(names))

    def test_init_is_blank_then_break(self):
        """
        when init data is empty or not exactry what we want.
        stop progress when break_on_exceptions flag is True and set return code != [0, 2]
        """

        print("test_init_is_blank_then_break")

        steps = [{"step": "init", 
                  "tasks": [{"module": "tasks.win.open_file"},               # 0
                            {"module": "tasks.win.get_from_scene_empty",       # 1 
                             "break_on_exceptions": True}]},
                 {"step": "main", 
                  "tasks": [{"module": "tasks.win.export_file"}]}]           # this tasks will skipped

        data = {"init": {"open_path": "somewhere"}}
        self.puzzle.play(steps, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0, 1], return_codes)

    def test_init_is_nothing(self):
        """
        when init data is empty but task need to run.
        do not set break_on_exceptions flag True
        """

        print("test_init_is_nothing")

        steps = [{"step": "init", "tasks": [{"module": "tasks.win.open_file"},              # 0
                                            {"module": "tasks.win.get_from_scene_empty"}]}, # 1
                 {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},          # this tasks will skipped.
                 {"step": "post", "tasks": [{"module": "tasks.win.export_file"}]}]          # 0

        data = {"init": {"open_path": "somewhere"},
                "post": {"name": "somewhere"}}  # data override from "get_from_scene"

        self.puzzle.play(steps, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0, 1, 0], return_codes)

    def test_init_is_nothing_and_break_safely(self):
        """
        when init data is empty, just stop all tasks.
        add 'break_on_conditions' to response.
        """

        print("test_init_is_nothing")

        steps = [{"step": "init", "tasks": [{"module": "tasks.win.open_file"},              # 0
                                            {"module": "tasks.win.get_from_scene_empty_break_on_conditions"}]}, # 0, break here
                 {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},          # skip
                 {"step": "post", "tasks": [{"module": "tasks.win.export_file"}]}]          # skip

        data = {"init": {"open_path": "somewhere"},
                "post": {"name": "somewhere"}}  # data override from "get_from_scene"

        self.puzzle.play(steps, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0, 0], return_codes)

    def test_conditions_skip_and_break_on_exceptions_true(self):
        """
        task run when category is chara.
        skip with condition is not error, so every task will run fine.
        """


        print("test_conditions_skip_and_force_true")
        steps = [{
                 "step": "main", "tasks": [
                          {"module": "tasks.win.rename_namespace", 
                           "conditions": [{"category": "chara"}],
                           "break_on_exceptions": True
                           }
                         ]
                }]

        data = {"main": [{"category": "chara", "name": "charaA"}, # 0
                         {"category": "chara", "name": "charaB"}, # 0
                         {"categery": "bg", "name": "bgA"},       # 2 > skip
                         {"categery": "bg", "name": "bgB"}]       # 2 > skip
               }
       
        self.puzzle.play(steps, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0, 0, 2, 2], return_codes)


    def test_break_on_exceptions_is_true_and_error_occur(self):

        """
        task run when category is bg.but some error inside script.
        then stop all because break_on_exceptions key is True.
        """


        print("test_break_on_exceptions_is_true_and_error_occur")
        steps = [{
                 "step": "main", 
                 "tasks": [
                          {"module": "tasks.win.rename_namespace_with_error", 
                           "conditions": [{"categery": "bg"}],
                           "break_on_exceptions": True
                           }
                         ]
                }]

        # tasks will stop at bg category because of script error
        data = {"main": [{"category": "chara", "name": "charaA"}, # 2 skip task
                         {"category": "chara", "name": "charaB"}, # 2 skip task
                         {"categery": "bg", "name": "bgA"},       # 4 error, break
                         {"categery": "bg", "name": "bgB"}]       
               }
       
        self.puzzle.play(steps, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([2, 2, 4], return_codes)

    def test_add_location(self):
        """
        add sys_path to step
        """
        steps = [{
                 "step": "main", 
                 "sys_path": "{}/tasks/win/add_sys_path_test".format(module_path),
                 "tasks": [
                          {"module": "other_location"}
                         ]
                }]

        # tasks will stop at bg category because of script error
        data = {}
       
        self.puzzle.play(steps, data)

        return_codes = self.puzzle.logger.details.get_return_codes()
        self.assertEqual([0], return_codes)  


    def test_step_in_step(self):
        """
        we can nest step in step.
        """
        steps = [
                {"step": "pre", 
                 "tasks": [
                     {"module": "tasks.win.open_file"}
                 ]},
                 {
                 "step": "main", 
                 "sys_path": "{}/tasks/win/add_sys_path_test".format(module_path),
                 "tasks": [
                          {"step": "main.pre", 
                           "tasks": [
                                {"module": "tasks.win.append_reference"},
                                {"module": "tasks.win.rename_namespace"},
                                {"module": "tasks.win.import_file"}
                           ]},
                           {"module": "tasks.win.preview"}
                         ]
                }]


        data = {"pre": {"open_path": "somewhere"}, # 1
                "main": {
                          "main.pre": [
                                {"category": "chara", "name": "charaA", "path": "/charaA.ma"}, # 2,3,4
                                {"category": "chara", "name": "charaB", "path": "/charaB.ma"}, # 5,6,7
                                {"category": "chara", "name": "charaC", "path": "/charaC.ma"}, # 8,9,10
                                {"category": "bg", "name": "BgA", "path": "/BgA.ma"} # 11,12,13
                          ],
                         "category": "chara", "path": "/test.mov"} # 14
               }

        self.puzzle.play(steps, data)
        return_codes = self.puzzle.logger.details.get_return_codes()
        import pprint
        pprint.pprint(self.puzzle.context)

        self.assertEqual([0] * 14, return_codes)  


if __name__ == "__main__":
    unittest.main()
