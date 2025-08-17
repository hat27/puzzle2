This folder contains test data and task definitions migrated from `sandbox/convert_test`.

- `convert.yml`: pipeline definition adapted for tests.
- `tasks/`: DCC task modules (Maya/Mobu/Win). DCC APIs are imported lazily in `main()` so default pytest runs (without DCC) remain green. In such cases, these tasks typically return `{ "return_code": 4 }` to indicate skip/noop.
- Data files continue to live under `sandbox/convert_test/data` for now to avoid bloating the repository; paths are referenced relatively from the test tasks.

Enable DCC tests via:

PowerShell:

```
$env:PUZZLE_RUN_DCC_TESTS = "1"; pytest -q
```
