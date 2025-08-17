# Tests layout

This folder is organized for CI (GitHub Actions) and local DCC testing.

- test_data/      # Shared fixtures and sample JSON/YAML used by tests
- unit/           # Fast, automation-friendly unit tests (no DCC)
- integration/    # End-to-end flows without launching DCCs
- dcc/
  - houdini/      # Houdini-specific tests (run with hython)
  - maya/         # Maya-specific tests (mayabatch/mayapy)
  - pipe/         # Cross-DCC pipeline tests

CI should run `tests/unit` and `tests/integration` only.
`tests/dcc` require installed DCCs and are opt-in.
