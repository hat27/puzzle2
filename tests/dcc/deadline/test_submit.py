import os
import sys
import json
import uuid
import tempfile
import shutil
import time
import pytest

# Opt-in gate: only run when PUZZLE_RUN_DCC_TESTS is one of 1/true/yes/on
_RUN_DCC = os.getenv("PUZZLE_RUN_DCC_TESTS", "").strip().lower() in ("1", "true", "yes", "on")
if not _RUN_DCC:
    pytest.skip(
        "Opt-in: requires Deadline client and repo plugin configured.",
        allow_module_level=True,
    )

# Defer imports of puzzle2 modules inside tests to avoid static resolver warnings

def _resolve_deadline_command():
    cand = os.environ.get("DEADLINE_COMMAND")
    if cand:
        cand = cand.strip().strip('"')
        cand = os.path.normpath(os.path.expandvars(os.path.expanduser(cand)))
        if os.path.isfile(cand):
            return cand
        guess = os.path.join(cand, "deadlinecommand.exe")
        if os.path.isfile(guess):
            return guess
    for name in ("deadlinecommand.exe", "deadlinecommand"):
        path = shutil.which(name)
        if path:
            return path
    program_files = os.environ.get("ProgramFiles", r"C:\\Program Files")
    candidates = [
        os.path.join(program_files, "Thinkbox", "Deadline10", "bin", "deadlinecommand.exe"),
        os.path.join(program_files, "Thinkbox", "Deadline", "bin", "deadlinecommand.exe"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None


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


from importlib import import_module as _imp_for_matrix
_matrix = _imp_for_matrix("tests.support.matrix")
@pytest.mark.parametrize("app,version", _matrix.CASES, ids=_matrix.IDS)
def test_deadline_submit(tmp_path, app, version):
    dl_cmd = _resolve_deadline_command()
    if not dl_cmd:
        pytest.skip("deadlinecommand not found")
    
    if app in ["maya", "motionbuilder"]:
        return pytest.skip("the app requires GUI")

    # Build minimal job/plugin info files
    job_info = tmp_path / f"job_info_{app}.job"
    plugin_info = tmp_path / f"plugin_info_{app}.job"

    # Minimal Job Info (UTF-16LE)
    job_info.write_text(f"Plugin=puzzle2\nName=Puzzle2.deadline.test_submit [{app}]\n", encoding="utf-16le")

    # Use local tests dir as module path; requires local Worker for true end-to-end
    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    tests_root = os.path.join(repo_root, "tests")

    # Prepare task/data JSON under temp shared dir
    out_dir = tmp_path / f"shared_{app}"
    out_dir.mkdir(parents=True, exist_ok=True)
    task_path = out_dir / "task_set.json"
    data_path = out_dir / "data.json"
    result_path = out_dir / "results.json"

    task_set = [
        {"step": "pre", "tasks": [{"module": "tasks.win.open_file"}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
    ]
    data_set = {"pre": {"open_path": None}, "main": [{"name": "A"}]}

    task_path.write_text(json.dumps({"info": {}, "data": task_set}, ensure_ascii=False, indent=2), encoding="utf-8")
    data_path.write_text(json.dumps({"info": {}, "data": data_set}, ensure_ascii=False, indent=2), encoding="utf-8")

    module_path = tests_root.replace("\\", "/")

    # Write plugin info (UTF-16LE)
    lines = []
    lines.append(f"App={app}\n")
    lines.append(f"Version={version}\n")
    # Add ModulePath (for tasks.*) and SysPath (extra sys.path entries) for the new plugin
    lines.append(f"ModulePath={module_path}/tests_data\n")
    lines.append(f"SysPath={module_path}\n")
    lines.append(f"TaskPath={task_path.as_posix()}\n")
    lines.append(f"DataPath={data_path.as_posix()}\n")
    lines.append(f"ResultPath={result_path.as_posix()}\n")
    plugin_info.write_text("".join(lines), encoding="utf-16le")

    # Submit; since this depends on external infra, just assert the command returns something
    import subprocess
    print(" ".join([dl_cmd, str(job_info), str(plugin_info)]))
    proc = subprocess.run([dl_cmd, str(job_info), str(plugin_info)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
    # We don't fail the test on non-zero; only verify execution path works and then wait for results
    assert proc.stdout is not None

    # Wait for worker to produce results.json if a Worker picks the job
    timeout = int(os.environ.get("PUZZLE_DEADLINE_TIMEOUT", os.environ.get("PUZZLE_RESULTS_TIMEOUT", 3000)))
    print(timeout)
    if not _wait_for_file(str(result_path), timeout=timeout, interval=5.0):
        pytest.fail(
            "results.json not found within timeout after Deadline submission\n"
            f"deadlinecommand={dl_cmd}\n"
            f"job_info={job_info}\n"
            f"plugin_info={plugin_info}\n"
            f"result_path={result_path}\n"
            f"stdout_tail={proc.stdout[-1000:] if proc.stdout else '<none>'}\n"
            f"stderr_tail={proc.stderr[-1000:] if proc.stderr else '<none>'}"
        )
    else:
        from importlib import import_module as _imp
        pz_config = _imp("puzzle2.pz_config")
        _, data = pz_config.read(result_path.as_posix())
        assert [l["return_code"] for l in data["results"]] == [0, 0]


@pytest.mark.parametrize("app,version", _matrix.CASES, ids=_matrix.IDS)
def test_submit_via_client(tmp_path, app, version):
    """Same smoke test as above, but using the puzzle2 Deadline client API."""
    # Import client lazily to avoid static import resolution issues in linters
    from importlib import import_module

    # Prepare minimal task/data under a temp shared directory
    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    tests_root = os.path.join(repo_root, "tests")
    module_path = os.path.join(tests_root, "tests_data")

    out_dir = tmp_path / f"client_shared_{app}"
    out_dir.mkdir(parents=True, exist_ok=True)
    task_path = out_dir / "task_set.json"
    data_path = out_dir / "data.json"
    result_path = out_dir / "results.json"

    job_name = f"Puzzle2.deadline.test_submit_via_client [{app}]"

    task_set = [
        {"step": "pre", "tasks": [{"module": "tasks.win.open_file"}]},
        {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]},
    ]
    data_set = {"pre": {"open_path": None}, "main": [{"name": "A"}]}

    task_path.write_text(json.dumps({"info": {}, "data": task_set}, ensure_ascii=False, indent=2), encoding="utf-8")
    data_path.write_text(json.dumps({"info": {}, "data": data_set}, ensure_ascii=False, indent=2), encoding="utf-8")

    # Submit via client; if Deadline is not installed, skip
    try:
        dl_submit = import_module("puzzle2.plugins.deadline.client").submit
        res = dl_submit(
            app=app,
            job_name=job_name,
            version=version,
            module_path=module_path,
            sys_path=tests_root,
            task_path=task_path.as_posix(),
            data_path=data_path.as_posix(),
            result_path=result_path.as_posix(),
        )
    except FileNotFoundError:
        pytest.skip("deadlinecommand not found")

    # Ensure command executed
    assert res.completed.stdout is not None

    # Wait for worker to produce results.json if a Worker picks the job
    timeout = int(os.environ.get("PUZZLE_DEADLINE_TIMEOUT", os.environ.get("PUZZLE_RESULTS_TIMEOUT", 3000)))
    if not _wait_for_file(str(result_path), timeout=timeout, interval=5.0):
        pytest.fail(
            "results.json not found within timeout after Deadline submission (client)\n"
            f"job_info={res.job_info_path}\n"
            f"plugin_info={res.plugin_info_path}\n"
            f"result_path={result_path}\n"
            f"stdout_tail={res.completed.stdout[-1000:] if res.completed.stdout else '<none>'}\n"
            f"stderr_tail={res.completed.stderr[-1000:] if res.completed.stderr else '<none>'}"
        )
    else:
        from importlib import import_module as _imp
        pz_config = _imp("puzzle2.pz_config")
        _, data = pz_config.read(result_path.as_posix())
        assert [l["return_code"] for l in data["results"]] == [0, 0]

