import os
import sys

# Ensure src is importable
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(BASE, "..", "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
_puzzle2 = pytest.importorskip("puzzle2")
from importlib import import_module
pz_config = import_module("puzzle2.pz_config")  # noqa: E402


def test_config_json_roundtrip(tmp_path):
    p = tmp_path / "sample.json"
    data = {"info": {"a": 1}, "data": {"x": 2}}
    pz_config.save(str(p), data, "unit", "json")

    info, d = pz_config.read(str(p))
    assert d["data"]["x"] == 2
