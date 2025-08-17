Puzzle2

Puzzle2 is a lightweight task runner/orchestrator for DCC applications (Maya, MotionBuilder, Houdini, etc.). It standardizes batch execution, logging, environment handoff, and integrates with Deadline.

Docs
- Website: https://hat27.github.io/puzzle2/

Quick install
- From source (editable):
	- pip install -e .

Core pieces
- puzzle2.Puzzle: Orchestrates steps and tasks with structured results.
- puzzle2.run_process: Resolves and launches DCC commands in batch/headless mode and writes artifacts under a job directory.
- puzzle2.PzLog: Scoped logger with JSON/YAML template support, handler-level control, and a Details API for structured results.
- puzzle2.plugins.deadline: Thin client for building Job/Plugin info and submitting via deadlinecommand.

Running tests (opt-in DCC/Deadline)
- DCC and Deadline tests are opt-in and gated by an environment variable. Only the following values enable them: 1, true, yes, on (case-insensitive). Any other value or unset disables them.
	- Example (PowerShell):
		- $env:PUZZLE_RUN_DCC_TESTS = "1"
- You can control which app/version pairs are used via environment variables:
	- PUZZLE_TEST_MATRIX_JSON: JSON string overriding the entire matrix
		- Example:
			- $env:PUZZLE_TEST_MATRIX_JSON = '{"mayapy":["2024"],"houdini":["20.5.654"]}'
	- PUZZLE_TEST_APPS: Semicolon-separated pairs app:version (no spaces)
		- Example:
			- $env:PUZZLE_TEST_APPS = "mayapy:2024;houdini:20.5.654"

Deadline client usage
- Minimal example to submit a job that executes tests/tasks on a Worker:
- Python:
	- from puzzle2.plugins.deadline import client
	- res = client.submit(
			app="mayapy",
			job_name="Puzzle2 Example",
			version="2024",
			module_path="<path to tests_data or your tasks>",
			sys_path="<additional sys.path entry>",
			task_path="<task_set.json or .yml converted to JSON>",
			data_path="<data.json>",
			result_path="<shared results.json>",
		)
	- print(res.completed.stdout)

Notes
- CI should keep PUZZLE_RUN_DCC_TESTS disabled by default to avoid external dependency on installed DCCs and a Deadline farm. Opt-in per job when infrastructure is available.
- PzLog selects a YAML or JSON template automatically depending on availability; handlers are scoped to avoid global logging side effects.
