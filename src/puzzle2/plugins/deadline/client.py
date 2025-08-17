"""
Lightweight Deadline submission client for puzzle2.

Use from tools/UX code to submit a puzzle2 job to Deadline without duplicating
pytest boilerplate. It writes Job/Plugin Info files (UTF-16LE by default),
resolves deadlinecommand, submits, and returns a structured result.

Note: waiting/polling for result files should be handled by the caller.
"""

import os
import shutil
import tempfile
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple


@dataclass
class SubmissionResult:
    """Submission outcome and useful paths/metadata."""

    job_info_path: Path
    plugin_info_path: Path
    result_path: Path
    completed: subprocess.CompletedProcess
    job_id: Optional[str] = None


def _norm_posix(p: str) -> str:
    """Normalize path to posix style for Plugin Info values."""
    return Path(p).as_posix()


def resolve_deadline_command() -> Optional[str]:
    """Resolve path to `deadlinecommand` executable.

    Resolution order:
    1) DEADLINE_COMMAND env var (file or folder containing deadlinecommand.exe)
    2) shutil.which("deadlinecommand(.exe)")
    3) Common Program Files locations (Windows)
    """
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


essential_job_keys = ("Plugin", "Name")
essential_plugin_keys = ("App", "Version", "ModulePath", "TaskPath", "DataPath", "ResultPath")


def _write_info_file(path: Path, lines: Dict[str, str], encoding: str = "utf-16le") -> None:
    """Write Deadline .job-style key=value lines with the specified encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(f"{k}={v}\n" for k, v in lines.items())
    path.write_text(content, encoding=encoding)


def _default_paths(temp_dir: Optional[Path], app: str) -> Tuple[Path, Path]:
    base = Path(temp_dir) if temp_dir else Path(tempfile.mkdtemp(prefix=f"puzzle2_deadline_{app}_"))
    return base / f"job_info_{app}.job", base / f"plugin_info_{app}.job"


def submit(
    *,
    app: str,
    version: str,
    module_path: str,
    task_path: str,
    data_path: str,
    result_path: str,
    sys_path: Optional[str] = None,
    job_name: Optional[str] = None,
    deadline_cmd: Optional[str] = None,
    temp_dir: Optional[str] = None,
    encoding: str = "utf-16le",
    job_info_extras: Optional[Dict[str, str]] = None,
    plugin_info_extras: Optional[Dict[str, str]] = None,
    env: Optional[Dict[str, str]] = None,
) -> SubmissionResult:
    """Submit a puzzle2 job to Deadline.

    Minimal required args map to the puzzle2 Deadline plugin fields.
    """
    dl_cmd = deadline_cmd or resolve_deadline_command()
    if not dl_cmd:
        raise FileNotFoundError("deadlinecommand not found. Set DEADLINE_COMMAND or install Deadline client.")

    job_info_path, plugin_info_path = _default_paths(Path(temp_dir) if temp_dir else None, app)

    # Job Info (minimal)
    job_lines = {
        "Plugin": "puzzle2",
        "Name": job_name or f"Puzzle2 Submit [{app}]",
    }
    if job_info_extras:
        job_lines.update(job_info_extras)
    _write_info_file(job_info_path, job_lines, encoding=encoding)

    # Plugin Info
    plugin_lines = {
        "App": app,
        "Version": version,
        "ModulePath": _norm_posix(module_path),
        "TaskPath": _norm_posix(task_path),
        "DataPath": _norm_posix(data_path),
        "ResultPath": _norm_posix(result_path),
    }
    if sys_path:
        plugin_lines["SysPath"] = _norm_posix(sys_path)
    if plugin_info_extras:
        plugin_lines.update(plugin_info_extras)
    _write_info_file(plugin_info_path, plugin_lines, encoding=encoding)

    # Submit
    completed = subprocess.run(
        [dl_cmd, str(job_info_path), str(plugin_info_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
        env=({**os.environ, **env} if env else None),
    )

    # Try to extract JobID if present in output (best-effort)
    job_id: Optional[str] = None
    out = completed.stdout or ""
    for line in out.splitlines():
        s = line.strip().lower()
        if s.startswith("jobid="):
            job_id = line.split("=", 1)[-1].strip()
            break
        if s.startswith("job id:"):
            job_id = line.split(":", 1)[-1].strip()
            break

    return SubmissionResult(
        job_info_path=job_info_path,
        plugin_info_path=plugin_info_path,
        result_path=Path(result_path),
        completed=completed,
        job_id=job_id,
    )


__all__ = [
    "SubmissionResult",
    "resolve_deadline_command",
    "submit",
]
