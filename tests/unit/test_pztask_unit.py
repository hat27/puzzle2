import os
import sys

import pytest

# Ensure src is importable (handled by tests/conftest.py), and add tests_data to sys.path for tasks.*
BASE = os.path.dirname(os.path.abspath(__file__))
TESTS_DATA = os.path.normpath(os.path.join(BASE, "..", "tests_data"))
if TESTS_DATA not in sys.path:
    sys.path.insert(0, TESTS_DATA)

_puzzle2 = pytest.importorskip("puzzle2")
from importlib import import_module
PzTask = import_module("puzzle2.PzTask").PzTask  # noqa: E402
mock = import_module("tasks.win.mock")  # noqa: E402


def test_key_required():
    data = {}
    pz_task = PzTask(module=mock, data=data)
    response = pz_task.execute()
    assert response["return_code"] == 5

    data = {"name": "nameA"}
    pz_task = PzTask(module=mock, data=data)
    response = pz_task.execute()
    assert response["return_code"] == 0


def test_data_key_replace():
    data = {"new_name": "nameB"}
    task = {"data_key_replace": {"name": "new_name"}}

    pz_task = PzTask(module=mock, task=task, data=data)
    assert pz_task.data["name"] == data["new_name"]


def test_data_key_replace_from_other_task():
    data = {"name": "nameA"}
    task = {"data_key_replace": {"name": "context.new_name"}}

    context = {"new_name": "nameB"}
    pz_task = PzTask(module=mock, task=task, data=data, context=context)
    assert pz_task.data["name"] == context["new_name"]


def test_conditions():
    data = {"name": "nameA", "category": "ch"}
    task = {"conditions": [{"category": "ch"}]}

    pz_task = PzTask(module=mock, task=task, data=data)
    assert pz_task.return_code == 0

    data = {"name": "nameA", "category": "prop"}
    task = {"conditions": [{"category": "ch"}]}

    pz_task = PzTask(module=mock, task=task, data=data)
    assert pz_task.return_code == 2

    data = {"name": "nameA", "category": "ch"}
    task = {"conditions": [{"category": "ch", "name": "nameA"}]}

    pz_task = PzTask(module=mock, task=task, data=data)
    assert pz_task.return_code == 0

    data = {"name": "nameA", "category": "ch"}
    task = {"conditions": [{"category": "ch", "name": "nameB"}]}

    pz_task = PzTask(module=mock, task=task, data=data)
    assert pz_task.return_code == 2
