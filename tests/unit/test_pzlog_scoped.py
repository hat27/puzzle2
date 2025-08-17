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
PzLog = import_module("puzzle2.PzLog").PzLog  # noqa: E402
_pz_config = import_module("puzzle2.pz_config")  # noqa: E402


def test_pzlog_uses_json_template_when_yaml_unavailable(tmp_path, monkeypatch):
    # Force YAML unavailable switch YAML_AVAILABLE to False
    monkeypatch.setattr(_pz_config, "YAML_AVAILABLE", False, raising=False)

    log_dir = tmp_path / "logs"
    log = PzLog("unittest", new=True, log_directory=str(log_dir))
    # Write something
    log.logger.info("hello")

    # Config should be created as JSON and log file should exist
    cfg = log.config_path
    assert cfg.endswith(".json")
    assert os.path.isfile(cfg)
    assert os.path.isfile(log.log_path)


def test_pzlog_no_global_side_effects(tmp_path):
    log_dir = tmp_path / "logs"
    import logging
    root_before = logging.getLogger(__name__).handlers[:]

    log = PzLog("scoped", new=True, log_directory=str(log_dir))

    root_mid = logging.getLogger(__name__).handlers[:]

    # Emitting logs shouldn't alter other loggers' handlers
    log.logger.info("hello")
    root_after = logging.getLogger(__name__).handlers[:]
    assert root_before == root_mid
    assert root_before == root_after


def test_pzlog_propagate_false(tmp_path):
    log_dir = tmp_path / "logs"
    log = PzLog("prop", new=True, log_directory=str(log_dir))
    assert log.logger.propagate is False


# ---- Ported and adapted from legacy tests/src/win/_test_PzLog.py ----

def _get_handler(logger, name):
    for h in logger.handlers:
        if getattr(h, "name", None) == name:
            return h
    return None


def test_pzlog_reset_template_uses_default_and_stream_debug(tmp_path):
    import logging
    log_dir = tmp_path / "logs"
    log = PzLog("test_default", reset_template=True, new=True, log_directory=str(log_dir))

    # Default template file name can be YAML or JSON depending on environment
    base = os.path.basename(getattr(log, "base_template_path", ""))
    assert base in ("log.template.yml", "log.template.json")

    stream = _get_handler(log.logger, "stream_handler")
    assert stream is not None
    # Validate level matches template's configured level
    _, cfg = _pz_config.read(log.base_template_path)
    tmpl_level = cfg.get("handlers", {}).get("stream_handler", {}).get("level", "DEBUG")
    expected = getattr(logging, str(tmpl_level).upper(), logging.DEBUG)
    assert stream.level == expected


def test_pzlog_use_existing_template_override_level(tmp_path):
    import logging
    log_dir = tmp_path / "logs"
    logA = PzLog("test2", log_directory=str(log_dir))

    # Modify EXISTING CONFIG (not global template): set stream level to CRITICAL
    info, cfg = _pz_config.read(logA.config_path)
    # Ensure nested keys exist before update
    handlers = cfg.setdefault("handlers", {})
    handlers.setdefault("stream_handler", {})
    handlers["stream_handler"]["level"] = "CRITICAL"
    _pz_config.save(logA.config_path, cfg, {})

    # New logger with same name should pick updated template
    logB = PzLog("test2", new=True, reset_template=False, log_directory=str(log_dir))

    base = os.path.basename(getattr(logB, "base_template_path", ""))
    # base_template_path points to the existing config for this name
    assert os.path.basename(logB.base_template_path).startswith("test2")

    streamA = _get_handler(logA.logger, "stream_handler")
    streamB = _get_handler(logB.logger, "stream_handler")
    assert streamA is not None and streamB is not None
    assert streamA.level == logging.CRITICAL
    assert streamB.level == logging.CRITICAL


def test_pzlog_add_date_to_log_name_keeps_default_template(tmp_path):
    import logging
    log_dir = tmp_path / "logs"
    _ = PzLog("test3", add_date_to_log_name=True, log_directory=str(log_dir))
    logB = PzLog("test3", new=True, reset_template=False, add_date_to_log_name=True, log_directory=str(log_dir))

    base = os.path.basename(getattr(logB, "base_template_path", ""))
    # When date is embedded in log name, default template is used
    assert base in ("log.template.yml", "log.template.json")

    streamB = _get_handler(logB.logger, "stream_handler")
    assert streamB is not None
    # Validate level matches template's configured level
    _, cfg = _pz_config.read(logB.base_template_path)
    tmpl_level = cfg.get("handlers", {}).get("stream_handler", {}).get("level", "DEBUG")
    expected = getattr(logging, str(tmpl_level).upper(), logging.DEBUG)
    assert streamB.level == expected


def test_pzlog_log_filename_contains_date_and_name(tmp_path):
    import datetime
    log_dir = tmp_path / "logs"
    log = PzLog("test1", add_date_to_log_name=True, log_directory=str(log_dir))

    today = datetime.datetime.now().strftime("%Y%m%d")
    file_h = _get_handler(log.logger, "file_handler")
    # file_handler may not exist in some minimal configs; skip if absent
    if file_h is None:
        pytest.skip("file_handler not configured; skip filename assertion")
    base = os.path.basename(getattr(file_h, "baseFilename", ""))
    assert base == f"{today}_test1.log"


def test_pzlog_log_filename_contains_date_name_user(tmp_path):
    import datetime
    log_dir = tmp_path / "logs"
    log = PzLog("test4", add_date_to_log_name=True, user_name="name", log_directory=str(log_dir))

    today = datetime.datetime.now().strftime("%Y%m%d")
    file_h = _get_handler(log.logger, "file_handler")
    if file_h is None:
        pytest.skip("file_handler not configured; skip filename assertion")
    base = os.path.basename(getattr(file_h, "baseFilename", ""))
    assert base == f"{today}_test4_name.log"


def test_pzlog_update_level(tmp_path):
    import logging
    log_dir = tmp_path / "logs"
    log = PzLog("test4", file_handler_level="CRITICAL", stream_handler_level="CRITICAL", log_directory=str(log_dir))
    for h in log.logger.handlers:
        assert h.level == logging.CRITICAL


def test_pzlog_details_api(tmp_path):
    log_dir = tmp_path / "logs"
    log = PzLog("test5", log_directory=str(log_dir))
    logger = log.logger

    logger.details.set_name("task_name1")
    name1 = logger.details.name

    logger.details.add_detail("test1")
    logger.details.add_detail("test2")
    logger.details.add_detail("test3")
    logger.details.set_header(0, "first task")

    logger.details.set_name("task_name2")
    name2 = logger.details.name
    logger.details.add_detail("test4")
    logger.details.add_detail("test5")
    logger.details.add_detail("test6")
    logger.details.set_header(1, "secound task")

    d1 = logger.details.get_details(name1)
    d2 = logger.details.get_details(name2)
    assert d1["details"] == ["test1", "test2", "test3"]
    assert d2["details"] == ["test4", "test5", "test6"]

    assert logger.details.get_return_codes() == [0, 1]

    assert logger.details.get_all() == [
        {"return_code": 0, "header": "first task", "details": ["test1", "test2", "test3"], "meta_data": {}},
        {"return_code": 1, "header": "secound task", "details": ["test4", "test5", "test6"], "meta_data": {}}
    ]

    logger.details.clear()
    assert logger.details.get_header() == []
    assert logger.details.get_all() == []


def test_pzlog_namespace_flag(tmp_path):
    log_dir = tmp_path / "logs"
    # Default: namespace True -> name is prefixed with 'puzzle.'
    log_ns = PzLog("ns_test", new=True, log_directory=str(log_dir))
    assert log_ns.logger.name == "puzzle.ns_test"

    # namespace False -> no prefix
    log_raw = PzLog("ns_test2", new=True, log_directory=str(log_dir), namespace=False)
    assert log_raw.logger.name == "ns_test2"


def test_pzlog_change_handler_levels_override(tmp_path):
    import logging
    log_dir = tmp_path / "logs"
    log = PzLog(
        "levels",
        new=True,
        log_directory=str(log_dir),
        stream_handler_level="ERROR",
        file_handler_level="WARNING",
    )
    sh = _get_handler(log.logger, "stream_handler")
    fh = _get_handler(log.logger, "file_handler")
    # Handlers may be absent depending on template; skip if missing
    if sh is not None:
        assert sh.level == logging.ERROR
    if fh is not None:
        assert fh.level == logging.WARNING

def test_pzlog_details_add_data_and_set(tmp_path):
    log_dir = tmp_path / "logs"
    log = PzLog("details_add", new=True, log_directory=str(log_dir))
    det = log.logger.details

    # add_data
    det.add_data("0 taskA", {"return_code": 0, "header": "A", "details": ["a1", "a2"], "meta_data": {"required": {"x": 1}, "execution_time": 0.1}}, location={"p": 1})
    # add_data_set
    headers = ["1 taskB", "2 taskC"]
    results = [
        {"return_code": 1, "header": "B", "details": ["b1"], "meta_data": {"required": {"y": 2}, "execution_time": 0.2}},
        {"return_code": 2, "header": "C", "details": ["c1", "c2"], "meta_data": {"required": {"z": 3}, "execution_time": 0.3}},
    ]
    det.add_data_set(headers, results, location={"q": 9})

    all_ = det.get_all()
    # Three entries added
    assert len(all_) == 3
    # First entry details
    assert all_[0]["header"] == "A"
    assert all_[0]["return_code"] == 0
    assert all_[0]["details"] == ["a1", "a2"]
    # Return codes order
    assert det.get_return_codes() == [0, 1, 2]
