## Talon AI Tools – Agent Notes

- Run tests with `python3 -m pytest` from the repo root.
- Avoid using the bare `pytest` command; it may not be available in all environments.

### Tests and the Talon runtime

- Do **not** rely on tests running inside the Talon process; tests should be executed via `python3 -m pytest` from this repo, not by Talon’s module loader.
- When adding new tests under `_tests/`, follow the existing `bootstrap` pattern so imports and assertions are skipped in the Talon runtime:
  - Try to import and call `bootstrap` from the repo root.
  - If `bootstrap` is available, run real imports and tests.
  - If `bootstrap` is unavailable (Talon runtime), define a small placeholder `unittest.TestCase` with a single `@unittest.skip` test method so Talon can import the file safely without executing the real test logic.
- Use the pattern from `_tests/test_request_log_axis_filter.py` or `_tests/test_history_query.py` as a reference when creating new tests.

