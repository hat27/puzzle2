import os
import sys

import pytest

# conftest already adds src/ and tests/tests_data to sys.path
from importlib import import_module
Puzzle = import_module("puzzle2.Puzzle").Puzzle  # noqa: E402


def _add_path(*parts):
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "tests_data", *parts))


def test_simple():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "pre", "tasks": [{"module": "tasks.win.open_file"}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
    ]
    data = {"pre": {"open_path": "somewhere"}, "main": [{"name": "nameA"}, {"name": "nameB"}]}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [0, 0, 0]


def test_task_failed_but_keep_running():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "pre", "tasks": [{"module": "tasks.win.open_file"}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
    ]
    # open_file needs open_path; give wrong key to cause 5, but continue
    data = {"pre": {"path": "somewhere"}, "main": [{"name": "nameA"}, {"name": "nameB"}]}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [5, 0, 0]


def test_task_failed_then_stopped():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "pre", "tasks": [{"module": "tasks.win.open_file", "break_on_exceptions": True}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
    ]
    data = {"pre": {"path": "somewhere"}, "main": [{"name": "nameA"}, {"name": "nameB"}]}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [5]


def test_task_failed_stop_but_closure_is_executed():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "pre", "tasks": [{"module": "tasks.win.open_file", "break_on_exceptions": True}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
        {"step": "closure", "tasks": [{"module": "tasks.win.revert"}]},
    ]
    data = {"pre": {"path": "somewhere"}, "main": [{"name": "nameA"}, {"name": "nameB"}], "common": {"revert": {"a": 1}}}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [5, 0]


def test_init_flow():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "init", "tasks": [{"module": "tasks.win.open_file"}, {"module": "tasks.win.get_from_scene"}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
    ]
    data = {"init": {"open_path": "somewhere"}}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [0, 0, 0, 0, 0]


def test_update_data_and_use_it_in_other_task():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "pre", "tasks": [{"module": "tasks.win.open_file", "break_on_exceptions": True}]},
        {"step": "main", "tasks": [
            {"module": "tasks.win.import_file"},
            {"module": "tasks.win.rename_namespace"},
            {"module": "tasks.win.export_file", "data_key_replace": {"name": "context.rename_namespace.new_name"}},
        ]},
        {"step": "post", "tasks": [
            {"module": "tasks.win.submit_to_sg", "data_key_replace": {"assets": "context.export_file.export_names"}},
        ]},
    ]
    data = {
        "pre": {"open_path": "somewhere"},
        "main": [{"name": "nameA", "path": "somewhere a"}, {"name": "nameB", "path": "somewhere b"}],
        "common": {"shot_code": "ep000_s000_c000", "fps": 24, "start_frame": 101, "end_frame": 200},
    }
    p.play(steps, data)
    assert p.context["rename_namespace.new_name"] == "nameB_01"
    assert p.context["export_file.export_names"] == ["nameA_01", "nameB_01"]


def test_data_defaults_and_override():
    p = Puzzle("puzzle", new=True)
    steps = [{"step": "main", "tasks": [{"module": "tasks.win.add_specified_data", "data_defaults": {"add": 100}}]}]
    data = {"main": {}}
    p.play(steps, data)
    assert p.context["add_specified_data.add"] == 100

    data = {"main": {"add": 200}}
    p.play(steps, data)
    assert p.context["add_specified_data.add"] == 200

    # override
    p2 = Puzzle("puzzle2", new=True)
    steps2 = [{"step": "main", "tasks": [{"module": "tasks.win.add_specified_data", "data_override": {"add": 100}}]}]
    p2.play(steps2, {"main": {}})
    assert p2.context["add_specified_data.add"] == 100
    p2.play(steps2, {"main": {"add": 50}})
    assert p2.context["add_specified_data.add"] == 100


def test_skip_flow():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "pre", "tasks": [{"module": "tasks.win.get_from_scene"}]},
        {"step": "main", "tasks": [
            {"module": "tasks.win.import_file", "conditions": [{"test": ""}]},
            {"module": "tasks.win.rename_namespace", "conditions": [{"test": ""}]},
            {"module": "tasks.win.export_file", "conditions": [{"test": ""}], "data_key_replace": {"name": "context.rename_namespace.new_name"}},
        ]},
        {"step": "post", "tasks": [{"module": "tasks.win.submit_to_sg", "conditions": [{"test": ""}], "data_key_replace": {"assets": "context.export_file.export_names"}}]},
    ]
    data = {}
    p.play(steps, data)
    names = [l["name"] for l in p.context["main"]]
    assert ",".join(names) == "a,b,c"


def test_init_is_blank_then_break():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "init", "tasks": [{"module": "tasks.win.open_file"}, {"module": "tasks.win.get_from_scene_empty", "break_on_exceptions": True}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
    ]
    data = {"init": {"open_path": "somewhere"}}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [0, 1]


def test_init_is_nothing():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "init", "tasks": [{"module": "tasks.win.open_file"}, {"module": "tasks.win.get_from_scene_empty"}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
        {"step": "post", "tasks": [{"module": "tasks.win.export_file"}]},
    ]
    data = {"init": {"open_path": "somewhere"}, "post": {"name": "somewhere"}}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [0, 1, 0]


def test_init_is_nothing_and_break_safely():
    p = Puzzle("puzzle", new=True)
    steps = [
        {"step": "init", "tasks": [{"module": "tasks.win.open_file"}, {"module": "tasks.win.get_from_scene_empty_break_on_conditions"}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
        {"step": "post", "tasks": [{"module": "tasks.win.export_file"}]},
    ]
    data = {"init": {"open_path": "somewhere"}, "post": {"name": "somewhere"}}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [0, 0]


def test_conditions_skip_and_break_on_exceptions_true():
    p = Puzzle("puzzle", new=True)
    steps = [{"step": "main", "tasks": [{"module": "tasks.win.rename_namespace", "conditions": [{"category": "chara"}], "break_on_exceptions": True}]}]
    data = {"main": [{"category": "chara", "name": "charaA"}, {"category": "chara", "name": "charaB"}, {"categery": "bg", "name": "bgA"}, {"categery": "bg", "name": "bgB"}]}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [0, 0, 2, 2]


def test_break_on_exceptions_is_true_and_error_occur():
    p = Puzzle("puzzle", new=True)
    steps = [{"step": "main", "tasks": [{"module": "tasks.win.rename_namespace_with_error", "conditions": [{"categery": "bg"}], "break_on_exceptions": True}]}]
    data = {"main": [{"category": "chara", "name": "charaA"}, {"category": "chara", "name": "charaB"}, {"categery": "bg", "name": "bgA"}, {"categery": "bg", "name": "bgB"}]}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [2, 2, 4]


def test_add_location():
    p = Puzzle("puzzle", new=True)
    add_path = _add_path("tasks", "win", "add_sys_path_test")
    steps = [{"step": "main", "sys_path": add_path, "tasks": [{"module": "other_location"}]}]
    data = {"main": {}}
    p.play(steps, data)
    assert p.logger.details.get_return_codes() == [0]
