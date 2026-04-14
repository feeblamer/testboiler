# Plan

## Goal

Bring the current `testboiler` prototype to a working MVP that matches the actual repository state and no longer promises features that do not exist.

## Implementation

1. Standardize the project name around `testboiler`.
2. Add a real console entry point for the CLI.
3. Keep only `init`, `run`, and `venv` commands.
4. Make `run` respect `framework.pytest` and `framework.unittest` from `quickboiler.cfg`.
5. Keep `sitecustomize.py`, but make it safe when YAML support is unavailable or the config still contains the placeholder value.
6. Replace hardcoded `requests` example tests with neutral template files.
7. Remove `main.py` because it is unrelated to the CLI workflow.
8. Update template files and documentation to reflect the real MVP.

## Verification

1. Check `python -m testboiler --help`.
2. Verify `testboiler init` copies the current template into a temporary directory.
3. Verify `testboiler run` works with enabled frameworks and fails clearly on invalid config.
4. Run repository tests to confirm the neutral test templates still pass discovery.
