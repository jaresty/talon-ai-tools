# ADR-0154 Work Log

## Loop History

---

## Loop 1: 2026-03-06

**helper_version:** helper:v20260227.1

**focus:** T-1 — Migrate `_STATIC_PROMPT_GUIDANCE` and `_STATIC_PROMPT_USE_WHEN` in `staticPromptConfig.py` to nested structure with `definition`, `heuristics`, `distinctions` fields per ADR-0154 schema.

**active_constraint:** None — baseline established and passed.

**validation_targets:**
- `python3 -m pytest _tests/test_prompt_grammar_export.py -v`
- `python3 -m pytest _tests/ -x -q` (full test suite)

**evidence:**
- red | 2026-03-06T00:00:00Z | N/A | Baseline — tests pass before changes
- green | 2026-03-06T00:30:00Z | exit 0 | python3 -m pytest _tests/ -x -q → 1298 passed
- green | 2026-03-06T00:30:00Z | exit 0 | make bar-grammar-update → grammar regenerated with $schema: "prompt-metadata/v2" and tasks.metadata

**rollback_plan:** `git restore --source=HEAD lib/staticPromptConfig.py lib/axisCatalog.py lib/promptGrammar.py && make bar-grammar-update`

**delta_summary:** helper:diff-snapshot=5 files changed — lib/staticPromptConfig.py (new TaskMetadata TypedDict + _TASK_METADATA dict + task_metadata() accessor), lib/axisCatalog.py (import + wire task_metadata), lib/promptGrammar.py (handle metadata + $schema field), grammar JSONs regenerated.

**loops_remaining_forecast:** 3 loops remaining:
- T-2: Update consumers (SPA, TUI, CLI) to read new metadata fields
- T-3: Add JSON schema validation
- T-4: Document migration completion

**residual_constraints:** None

**next_work:** T-2 — Update consumers to read structured metadata fields
