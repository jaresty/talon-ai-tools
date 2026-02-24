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

## loop-2 | 2026-02-23 | help_llm.go method category grouping

**focus:** ADR-0144 §Phase 1 Exposure — `bar help llm tokens method` renders method tokens grouped by semantic category headers (e.g. `**Reasoning**`) between table rows.

**active_constraint:** `Grammar.Axes.Categories` field did not exist; `AxisCategory()` accessor was absent; `help_llm.go` rendered all method tokens in a flat alphabetical table.

**validation_targets:**
- `go test ./internal/barcli/... -run TestHelpLLMMethodCatalogGroupedByCategory -v` — specifying validation: checks for `**Reasoning**`, `**Exploration**`, `**Structural**`, `**Diagnostic**` bold headers in output
- `go test ./internal/barcli/... -count=1 -q` — regression suite

**evidence:**
- red | 2026-02-23T01:00:00Z | exit 1 | `TestHelpLLMMethodCatalogGroupedByCategory` — missing `**Reasoning**` etc. (test strengthened to require bold header format)
- green | 2026-02-23T01:30:00Z | exit 0 | all barcli + cmd/bar tests pass after grammar.go + help_llm.go changes

**rollback_plan:** `git restore .` then replay red command.

**delta_summary:** 3 files changed — `grammar.go` (Categories field in AxisSection + rawAxisSection, wired from JSON, AxisCategory() accessor), `help_llm.go` (method table renders by category group), `app_help_cli_test.go` (specifying test added).

**loops_remaining_forecast:** 4 loops remaining (SPA/TUI2 → starter pack data → bar starter CLI → help llm + SPA starter packs). Confidence: high.

**residual_constraints:**
- Severity: Low. SPA and TUI2 do not yet consume `axes.categories` — Loop 3. No current blocker.

**next_work:**
- Behaviour: SPA TokenSelector groups method tokens by category → Loop 3
- Behaviour: TUI2 token picker shows category separator rows → Loop 3

## loop-3 | 2026-02-24 | SPA TokenSelector + TUI2 category grouping

**focus:** ADR-0144 §Phase 1 Exposure — SPA `TokenSelector.svelte` renders method tokens grouped by category headers; TUI2 token picker already had `SemanticGroup` rendering (confirmed complete in prior work).

**active_constraint:** `TokenSelector.svelte` rendered a flat token list regardless of category data; `METHOD_CATEGORY_ORDER` was not imported; no `.category-header` elements existed. The 6 specifying tests (C1–C6) did not exist.

**validation_targets:**
- `npm run test -- --run` with 6 new specifying tests (C1–C6 in `TokenSelector.test.ts`) — checks: headers rendered, headers not role=option, canonical order, flat on filter, uncategorized trailing, non-method axis stays flat
- Full suite: 159 tests pass

**evidence:**
- red | 2026-02-24T04:29:00Z | exit 0 (38 TokenSelector tests, 0 category tests) | `npm run test -- --run` — pre-implementation baseline: no C1–C6 specifying tests existed; category grouping absent
- green | 2026-02-24T04:30:32Z | exit 0 | 159 passed (44 TokenSelector, 6 new C1–C6 pass) after `TokenSelector.svelte` updated with `categoryGroups` derived + grouped template branch + `.category-header` CSS
- removal | 2026-02-24T04:30:55Z | `git stash` reverted both implementation and tests simultaneously; stashed state ran 149 tests / 38 TokenSelector — 6 C1–C6 tests absent confirms pre-implementation state had no specifying validation. `git stash pop` restored.

**rollback_plan:** `git restore web/src/lib/TokenSelector.svelte web/src/lib/TokenSelector.test.ts` then replay `npm run test -- --run` to confirm C1–C6 absent.

**delta_summary:** `helper:diff-snapshot=8 files changed, 347 insertions(+), 67 deletions(-)` — primary changes: `TokenSelector.svelte` (category grouping logic + template + CSS), `TokenSelector.test.ts` (6 specifying tests C1–C6), `docs/adr/0144-method-vocabulary-learnability.md` (3 ADR clarifications from gap analysis: bi-directional collision check, contested definition, Phase 3 family-token semantics). TUI2 `SemanticGroup` rendering was already in place.

**loops_remaining_forecast:** 3 loops remaining (Loop 4: starter pack data + grammar JSON → Loop 5: bar starter CLI → Loop 6: bar help llm starter packs + SPA PatternsLibrary). Confidence: high.

**residual_constraints:**
- Severity: Low. Starter pack data (`lib/starterPacks.py`, grammar JSON `starter_packs` key) not yet created — Loop 4 target. No current blocker on Loop 3 completion.
- Severity: Low. TUI2 has no dedicated starter pack UI (Phase 2 MVP decision per ADR). Not a constraint.

**next_work:**
- Behaviour: `lib/starterPacks.py` + grammar JSON `starter_packs` key populated with 10 initial packs → Loop 4
- Behaviour: `bar starter list` and `bar starter <name>` CLI subcommand → Loop 5
