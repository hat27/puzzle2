import os
import json
import datetime

def test_batch_kicker_runs_locally(tmp_path):
    """Run batch_kicker.main in-process (no DCC) using tasks.win.* and verify results.json."""
    repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
    src_dir = os.path.join(repo_root, "src")
    tests_data_dir = os.path.join(repo_root, "tests", "tests_data")
    # Ensure imports work inside the test
    import sys
    if src_dir not in [p.replace('\\', '/') for p in sys.path]:
        sys.path.insert(0, src_dir)
    if tests_data_dir not in [p.replace('\\', '/') for p in sys.path]:
        sys.path.insert(0, tests_data_dir)

    import importlib
    pz_config = importlib.import_module("puzzle2.pz_config")
    batch_kicker = importlib.import_module("puzzle2.batch_kicker")

    # Job directory under tests_data/jobs_local
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    job_dir = os.path.join(tests_data_dir, "jobs_local", f"local_{now}")
    os.makedirs(job_dir, exist_ok=True)

    # Simple task and data: use win tasks that don't require DCC
    task_set = [
        {"step": "pre", "tasks": [{"name": "open", "module": "tasks.win.open_file"}]},
        {"step": "main", "tasks": [{"name": "export", "module": "tasks.win.export_file"}]},
    ]
    data_set = {
        "pre": {"open_path": None},
        "main": [{"name": "ItemA"}, {"name": "ItemB"}],
    }

    # Write artifacts expected by batch_kicker
    task_set_path = os.path.join(job_dir, "tasks.json")
    data_path = os.path.join(job_dir, "data.json")
    result_path = os.path.join(job_dir, "results.json")
    pz_config.save(task_set_path, task_set)
    pz_config.save(data_path, data_set)

    env = {
        "app": "",  # pure python
        "puzzle_directory": src_dir.replace("\\", "/"),
        "log_name": "puzzle",
        "log_directory": job_dir.replace("\\", "/"),
        "keys": "",
        "script_path": os.path.join(src_dir, "puzzle2", "batch_kicker.py").replace("\\", "/"),
        "task_set": True,
        "data_set": True,
        "module_directory_path": tests_data_dir.replace("\\", "/"),
        "close_app": True,
        "sys_path": "",
        "result_path": result_path.replace("\\", "/"),
    }

    config_path = os.path.join(job_dir, "config.json")
    pz_config.save(
        config_path,
        {"env": env, "data_path": data_path.replace("\\", "/"), "task_set_path": task_set_path.replace("\\", "/"), "context_path": None},
    )

    # Execute in-process
    batch_kicker.main(config_path)

    assert os.path.exists(result_path), "results.json was not created"
    with open(result_path, "r", encoding="utf8") as f:
        result = json.load(f)
    data = result.get("data", {})
    results = data.get("results", [])
    assert len(results) >= 2, f"unexpected results length: {len(results)}"
    assert all("return_code" in r for r in results)
