import os
import time
import pprint
import pytest
from importlib import import_module as _imp_for_matrix

# Defer puzzle2 imports inside functions to avoid static resolver warnings

# DCC 実行を伴うため、明示的にゲート（1/true/yes/on のみ有効）
_RUN_DCC = os.getenv("PUZZLE_RUN_DCC_TESTS", "").strip().lower() in ("1", "true", "yes", "on")
if not _RUN_DCC:
    pytest.skip(
        "DCC tests are opt-in. Set PUZZLE_RUN_DCC_TESTS=1 to enable.",
        allow_module_level=True,
    )
TESTS_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "tests_data")

def _jobs_dir(name: str) -> str:
    return os.path.normpath(os.path.join(TESTS_DATA, "jobs_local", name))


def _tasks_root() -> str:
    return os.path.normpath(os.path.join(TESTS_DATA))


def _wait_for_file(path: str, timeout: int = 300, interval: float = 5.0) -> bool:
    """Wait until a file exists and is non-empty.

    Returns True when the condition is met within timeout; otherwise False.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                return True
        except Exception:
            # ignore transient filesystem errors and retry
            pass
        time.sleep(interval)
    return False


def _run_one(app: str, version: str, tmp_path, file_mode: bool = False):
    from importlib import import_module as _imp
    run_process = _imp("puzzle2.run_process").run_process
    pz_config = _imp("puzzle2.pz_config")
    command_data = {
        "version": version,
    "module_directory_path": _tasks_root(),
    # isolate each run under a unique temporary directory
    "job_directory": os.fspath(tmp_path / f"{app}_{version}"),
        "close_app": True,
    }

    if file_mode:
        command_data["task_set_path"] = os.path.normpath(os.path.join(TESTS_DATA, "win", "task_set.yml"))
        command_data["data_path"] = os.path.normpath(os.path.join(TESTS_DATA, "win", "data.json"))
    else:
        command_data["task_set"] = [
            {"step": "pre", "tasks": [{"module": "tasks.win.open_file"}]},
            {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
        ]
        command_data["data_set"] = {
            "pre": {"open_path": "somewhere"},
            "main": [{"name": "nameA"}, {"name": "namessB"}],
        }

    # ensure the temp job directory exists (run_process will also create if missing)
    os.makedirs(command_data["job_directory"], exist_ok=True)
    result_path = os.path.join(command_data["job_directory"], "results.json")
    if os.path.exists(result_path):
        os.remove(result_path)  # clean up previous results

    command, job_directory = run_process(app, **command_data)

    if not command:
        # App not installed or command couldn't be built
        pytest.skip(f"DCC not available or command could not be built for {app} {version}")

    std_path = os.path.join(job_directory, "std.txt")
    debug = {"result_path": result_path, "job_directory": job_directory}
    if os.path.exists(std_path):
        try:
            with open(std_path, "r", encoding="utf-8", errors="ignore") as f:
                debug["std_tail"] = f.read()[-1000:]
        except Exception:
            pass
    pprint.pprint(debug)
    # Wait for worker to produce results.json (useful when external process like Deadline writes it)

    if not _wait_for_file(result_path, timeout=int(os.environ.get("PUZZLE_RESULTS_TIMEOUT", 300)), interval=5.0):
        pytest.fail(
            f"results.json not found within timeout: {result_path}\n"
            f"job_directory={job_directory}\n"
            f"std_tail={debug.get('std_tail','<none>')}"
        )

    _, data = pz_config.read(result_path)
    return [l["return_code"] for l in data["results"]]


_matrix = _imp_for_matrix("tests.support.matrix")
@pytest.mark.parametrize("app,version", _matrix.CASES, ids=_matrix.IDS)
def test_batch_matrix(tmp_path, app, version):
    rc = _run_one(app, version, tmp_path, file_mode=False)
    assert rc == [0, 0, 0], f"job failed for {app} {version}"
