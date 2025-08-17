import os
import pytest
from puzzle2.Puzzle import Puzzle

# Opt-in gate: only run when PUZZLE_RUN_DCC_TESTS is one of 1/true/yes/on
_RUN_DCC = os.getenv("PUZZLE_RUN_DCC_TESTS", "").strip().lower() in ("1", "true", "yes", "on")
if not _RUN_DCC:
    pytest.skip(
        "Opt-in: requires Deadline client and repo plugin configured.",
        allow_module_level=True,
    )

TESTS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.normpath(os.path.join(TESTS_DIR, "..", "..", ".."))
TESTS_DATA = os.path.normpath(os.path.join(PROJECT_ROOT, "tests", "tests_data"))


def test_pipe_simple():
    p = Puzzle("pipeTest", new=True)

    steps = [
        {"step": "pre", "tasks": [{"module": "tasks.win.open_file"}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
        {"step": "pipe",
         "pipe": {"app": "mayapy", "version": "2024"},
         "sys_path": TESTS_DATA,
         "tasks": [
             {"step": "pipe.pre",
              "tasks": [
                  {"module": "tasks.win.open_file",
                   "data_key_replace": {"open_path": "context.OpenFile.update_context_test"}}
              ]}
         ]},
    ]

    data = {
        "pre": {"open_path": "somewhere"},
        "common": {"A": 123},
        "main": [{"name": "nameA"}, {"name": "nameB"}],
        "pipe.pre": {"open_path": "A"},
    }

    p.play(steps, data)
    print(p.logger.details.get_return_codes())
    assert p.logger.details.get_return_codes() == [0, 0, 0, 0]


def test_pipe_complex():
    p = Puzzle("pipeTest", new=True)

    steps = [
        {"step": "pre", "tasks": [{"module": "tasks.win.open_file"}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
        {"step": "pipe",
         "pipe": {"app": "mayapy", "version": "2024"},
         "sys_path": TESTS_DATA,
         "tasks": [
             {"step": "pipe.pre",
              "tasks": [
                  {"module": "tasks.win.open_file",
                   "data_key_replace": {"open_path": "context.OpenFile.update_context_test"}}
              ]}
         ]},
        {"step": "pipe2",
         "pipe": {"app": "motionbuilder", "version": "2024"},
         "close_app": True,
         "sys_path": TESTS_DATA,
         "tasks": [
             {"step": "pipe.main",
              "tasks": [
                  {"module": "tasks.win.open_file"}
              ]}
         ]},
    ]

    data = {
        "pre": {"open_path": "somewhere"},
        "common": {"A": 123},
        "main": [{"name": "nameA"}, {"name": "nameB"}],
        "pipe.pre": {"open_path": "A"},
        "pipe.main": {"open_path": "B"},
    }

    p.play(steps, data)
    print(p.logger.details.get_return_codes())
    assert p.logger.details.get_return_codes() == [0, 0, 0, 0, 0]
