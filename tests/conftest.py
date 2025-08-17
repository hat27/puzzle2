"""Pytest configuration for test pathing and bytecode suppression."""
import os
import sys

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(THIS_DIR, '..'))

# 1) Ensure the project 'src' directory is importable for tests
SRC_DIR = os.path.join(PROJECT_ROOT, 'src')
if SRC_DIR not in [p.replace('\\', '/') for p in sys.path]:
    sys.path.insert(0, SRC_DIR)

# 2) Ensure test fixture modules (e.g., tasks.win.*) under tests/tests_data are importable
TESTS_DATA_DIR = os.path.join(THIS_DIR, 'tests_data')
if TESTS_DATA_DIR not in [p.replace('\\', '/') for p in sys.path]:
    sys.path.insert(0, TESTS_DATA_DIR)

# Avoid creating .pyc / __pycache__ during test runs
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
try:
    import sys as _sys
    _sys.dont_write_bytecode = True
except Exception:
    pass
