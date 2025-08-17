import os
import sys
import json
import tempfile

import pytest

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

# Ensure src is importable
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", "..", "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

_puzzle2 = pytest.importorskip("puzzle2")
from importlib import import_module
pz_config = import_module("puzzle2.pz_config")  # noqa: E402
run_process = import_module("puzzle2.run_process").run_process  # noqa: E402


def test_run_process_saves_job_files_without_dcc(monkeypatch, tmp_path):
    # Prepare fake addon for a dummy DCC so we don't launch real apps
    class DummyAddon:
        @staticmethod
        def get_command(**kwargs):
            # Return a shell that exits with 0
            if os.name == "nt":
                return ["cmd.exe", "/C", "exit", "0"]
            return ["/bin/sh", "-lc", "exit 0"]

        @staticmethod
        def add_env(**kwargs):
            return {}

    # Monkeypatch importlib to return DummyAddon for a specific app
    import importlib

    def fake_import(name, *a, **k):
        if name.endswith("puzzle2.addons.dummy.integration"):
            return DummyAddon
        return real_import(name, *a, **k)

    real_import = importlib.import_module
    monkeypatch.setattr(importlib, "import_module", fake_import)

    # Create minimal inputs
    job_dir = tmp_path / "job"
    task_set = [{"step": "pre", "tasks": [{"module": "tasks.win.open_file"}]},
                {"step": "main", "tasks": [{"module": "tasks.win.export_file"}]}]
    data_set = {"pre": {"open_path": "x"}, "main": [{"name": "A"}]}

    command, job_directory = run_process(
        "dummy",
        task_set=task_set,
        data_set=data_set,
        job_directory=str(job_dir),
    )

    assert command, "Command should be returned"
    assert os.path.isdir(job_directory)

    config_path = os.path.join(job_directory, "config.json")
    tasks_path = os.path.join(job_directory, "tasks.json")
    data_path = os.path.join(job_directory, "data.json")

    assert os.path.isfile(config_path)
    assert os.path.isfile(tasks_path)
    assert os.path.isfile(data_path)

    # Validate the config shape
    info, cfg = pz_config.read(config_path)
    assert "env" in cfg and "data_path" in cfg and "task_set_path" in cfg
