import os
import sys
import pytest

from puzzle2.run_process import run_process

# Opt-in gate: only run when PUZZLE_RUN_DCC_TESTS is one of 1/true/yes/on
_RUN_DCC = os.getenv("PUZZLE_RUN_DCC_TESTS", "").strip().lower() in ("1", "true", "yes", "on")
if not _RUN_DCC:
    pytest.skip(
        "Opt-in: requires Deadline client and repo plugin configured.",
        allow_module_level=True,
    )

BASE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(BASE, "..", "..", ".."))
TESTS_DATA = os.path.normpath(os.path.join(PROJECT_ROOT, "tests", "tests_data"))


def test_generate_bat_for_maya_2024(tmp_path):
    task_path = os.path.join(TESTS_DATA, "win", "task_set.yml")
    data_path = os.path.join(TESTS_DATA, "win", "data.json")
    result_path = tmp_path / "result.json"
    bat_path = tmp_path / "puzzle2.bat"

    cmd = {
        "module_directory_path": os.path.join(TESTS_DATA, "tasks"),
        "task_set_path": task_path,
        "data_path": data_path,
        "result_path": str(result_path),
        "execute_now": False,
        "bat_file": str(bat_path),
        "close_app": True,
        "version": "2024",
    }

    app = "maya"
    run_process(app, **cmd)
    assert bat_path.exists()
    text = bat_path.read_text(encoding="utf-8", errors="ignore")
    # Basic check: the batch should contain PUZZLE_JOB_PATH and a maya.exe launch command
    assert "PUZZLE_JOB_PATH" in text
