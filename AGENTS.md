## Talon AI Tools – Agent Notes

- Run tests with `python3 -m pytest` from the repo root.
- Avoid using the bare `pytest` command; it may not be available in all environments.

### Surface-specific usage hints

- Keep CLI completion/help wording distinct from Talon canvases. Showing CLI syntax (for example, `method=steps`) inside Talon UI overlays confuses operators; prefer higher-level phrasing there and reserve shorthand tutorials for CLI outputs/docs.

### Tests and the Talon runtime

- Do **not** rely on tests running inside the Talon process; tests should be executed via `python3 -m pytest` from this repo, not by Talon’s module loader.
- When adding new tests under `_tests/`, follow the existing `bootstrap` pattern so imports and assertions are skipped in the Talon runtime:
  - Try to import and call `bootstrap` from the repo root.
  - If `bootstrap` is available, run real imports and tests.
  - If `bootstrap` is unavailable (Talon runtime), define a small placeholder `unittest.TestCase` with a single `@unittest.skip` test method so Talon can import the file safely without executing the real test logic.
- Use the pattern from `_tests/test_request_log_axis_filter.py` or `_tests/test_history_query.py` as a reference when creating new tests.

### Churn × Complexity Concordance ADR helper

- Use `python3 .claude/skills/churn-concordance-adr-helper/scripts/churn-git-log-stat.py` (`CHURN_LOG_COMMAND`) to capture the `git log --stat` fixture. It reads:
  - `LINE_CHURN_SINCE` (default `"90 days ago"`).
  - `LINE_CHURN_SCOPE` (comma-separated prefixes; default `"lib/,GPT/,copilot/,tests/"`).
  - `LINE_CHURN_OUTPUT` (default `tmp/churn-scan/git-log-stat.txt`).
- Use `python3 .claude/skills/churn-concordance-adr-helper/scripts/line-churn-heatmap.py` (`HEATMAP_COMMAND`) to produce the statement-level heatmap JSON. It shares the same `LINE_CHURN_SINCE`, `LINE_CHURN_SCOPE`, and `LINE_CHURN_OUTPUT` env vars and also reads:
  - `LINE_CHURN_LIMIT` (default `200`).
- `make churn-scan` runs both helpers sequentially with the defaults, writing artifacts to `tmp/churn-scan/git-log-stat.txt` and `tmp/churn-scan/line-hotspots.json`.
- Override the environment variables as needed to change the commit window, scoped paths, limits, or artifact locations so ADR runs stay reproducible.

