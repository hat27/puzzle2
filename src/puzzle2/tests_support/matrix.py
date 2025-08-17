"""Centralized app/version matrix for tests.

Allows one place to manage which DCC apps and versions are exercised by tests.
Supports simple overrides via environment variables:

- PUZZLE_TEST_APPS: semicolon-separated pairs like
    mayapy:2024;mayabatch:2024;mobupy:2024;houdini:20.5.654

- PUZZLE_TEST_MATRIX_JSON: JSON string mapping app->list of versions, e.g.
    {"mayapy":["2024"], "houdini":["20.5.654"]}

If both are provided, PUZZLE_TEST_MATRIX_JSON takes precedence.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Sequence, Tuple


DEFAULT_MATRIX: Dict[str, List[str]] = {
    "mayapy": ["2024"],
    "mayabatch": ["2024"],
    "mobupy": ["2024"],
    "motionbuilder": ["2024"],
    "houdini": ["20.5.654"],
}


def _parse_env_matrix() -> Dict[str, List[str]] | None:
    raw_json = os.environ.get("PUZZLE_TEST_MATRIX_JSON")
    if raw_json:
        try:
            data = json.loads(raw_json)
            # Normalize to list of strings
            return {str(k): [str(vv) for vv in (v or [])] for k, v in data.items()}
        except Exception:
            pass

    raw_pairs = os.environ.get("PUZZLE_TEST_APPS")
    if raw_pairs:
        matrix: Dict[str, List[str]] = {}
        for part in raw_pairs.split(";"):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                app, ver = part.split(":", 1)
            else:
                app, ver = part, ""
            app = app.strip()
            ver = ver.strip()
            if not app:
                continue
            matrix.setdefault(app, [])
            if ver:
                matrix[app].append(ver)
        if matrix:
            return matrix
    return None


def build_cases(matrix: Dict[str, Sequence[str]] | None = None) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Build (app, version) pairs and pytest ids from a matrix mapping.

    Returns:
        CASES: list of (app, version)
        IDS:   list of readable ids like "mayapy-2024"
    """
    src = _parse_env_matrix() or matrix or DEFAULT_MATRIX
    cases: List[Tuple[str, str]] = []
    ids: List[str] = []
    for app, versions in src.items():
        for v in versions:
            cases.append((app, v))
            ids.append(f"{app}-{v}")
    return cases, ids


CASES, IDS = build_cases()

__all__ = ["DEFAULT_MATRIX", "build_cases", "CASES", "IDS"]
