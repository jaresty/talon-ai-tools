# ADR-0144 Work Log: Method Vocabulary Learnability

**helper_version:** helper:v20251223.1

<!-- loops appended below -->

## loop-1 | 2026-02-23 | AXIS_KEY_TO_CATEGORY + full pipeline to grammar JSON

**focus:** ADR-0144 §Phase 1 — add `AXIS_KEY_TO_CATEGORY` for all 60 method tokens, wire through `axisCatalog.py` → `promptGrammar.py` → `prompt-grammar.json`, update `generate_axis_config.py` so regen stays in sync.

**active_constraint:** `axis_key_to_category_map` did not exist; the regen script did not emit `AXIS_KEY_TO_CATEGORY`, causing the regen parity test to fail once the constant was added manually.

**validation_targets:**
- `python3 -c "from lib.axisConfig import axis_key_to_category_map"` — accessor importable
- `python3 -m pytest _tests/ -x -q` — all 1239 tests pass including regen parity

**evidence:**
- red | 2026-02-23T00:00:00Z | exit 1 | `python3 -c "from lib.axisConfig import axis_key_to_category_map"` — ImportError
- green | 2026-02-23T00:30:00Z | exit 0 | 1239 passed after generate_axis_config.py + axisConfig.py + axisCatalog.py + promptGrammar.py updated

**rollback_plan:** `git restore .` then replay red command to confirm failure returns.

**delta_summary:** 5 files changed — `lib/axisConfig.py` (AXIS_KEY_TO_CATEGORY + accessor), `lib/axisCatalog.py` (axis_category wired), `lib/promptGrammar.py` (categories written to JSON), `scripts/tools/generate_axis_config.py` (emits constant + helper), grammar JSONs regenerated.

**loops_remaining_forecast:** 5 loops remaining (help_llm Go rendering → SPA/TUI2 → starter pack data → bar starter CLI → help llm + SPA starter packs section). Confidence: high.

**residual_constraints:**
- Severity: Low. Grammar JSON `axes.categories` is not yet read by any Go or SPA consumer — those are Loop 2 and 3. No blocking dependency.

**next_work:**
- Behaviour: `bar help llm` renders method tokens grouped by category headers → Loop 2
- Behaviour: SPA and TUI2 token pickers show category separators → Loop 3
