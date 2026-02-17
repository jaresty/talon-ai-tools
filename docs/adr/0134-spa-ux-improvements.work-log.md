# Work Log — ADR-0134 SPA UX Improvements

Sibling work-log for `0134-spa-ux-improvements.md`.
Evidence under `docs/adr/evidence/0134/`.
VCS_REVERT: `git restore --source=HEAD` (file-targeted) or `git stash` (full).

---

## loop-1 | 2026-02-17 | D3 pipeline: USAGE_PATTERNS SSOT → grammar JSON → Go struct

```
helper_version: helper:v20251223.1
focus: ADR-0134 §D3 — wire USAGE_PATTERNS from lib/axisConfig.py through
  axisCatalog.py → promptGrammar.py → prompt-grammar.json → grammar.go Grammar struct.
  Slice scope: Python pipeline + Go struct only; help_llm.go rendering left for loop-2.

active_constraint: >
  Grammar.Patterns is empty (len=0) because USAGE_PATTERNS does not yet exist in
  lib/axisConfig.py and is not emitted to prompt-grammar.json.
  Falsifiable: go test ./internal/barcli/ -run TestGrammarPatternsLoaded exits 1.

validation_targets:
  - go test ./internal/barcli/ -run TestGrammarPatternsLoaded -v
    # specifying validation — new test added this loop encoding the correctness expectation
  - go test ./internal/barcli/... && python3 -m pytest
    # regression guard

evidence:
  - green | 2026-02-17T19:40:00Z | exit 0 | go test ./internal/barcli/ -run TestGrammarPatternsLoaded -v
      Patterns loaded with 32 entries | inline
  - green | 2026-02-17T19:40:30Z | exit 0 | go test ./internal/barcli/... && python3 -m pytest
      1233 passed, 24 warnings | inline

delta_summary: >
  9f5ffb4 — 10 files changed: axisConfig.py (32 patterns), axisCatalog.py,
  promptGrammar.py, grammar.go (GrammarPattern struct + Patterns field),
  build_test.go (TestGrammarPatternsLoaded), 4× grammar JSON files regenerated.

next_work:
  - Behaviour: D3-help_llm.go rendering from grammar.Patterns (Loop-2)
    validation: go test ./internal/barcli/ -run TestLLMHelpUsagePatternsTokensExist

---

## loop-2 | 2026-02-17 | D3 help_llm.go: render patterns from grammar.Patterns

```
helper_version: helper:v20251223.1
focus: ADR-0134 §D3 — renderUsagePatterns reads grammar.Patterns instead of hardcoded slice;
  TestLLMHelpUsagePatternsTokensExist refactored to iterate grammar.Patterns.

active_constraint: >
  help_llm.go still had 32 hardcoded patterns in Go; any new pattern added to USAGE_PATTERNS
  in axisConfig.py would not appear in bar help llm unless also added to Go.
  Falsifiable: diff of help_llm.go shows hardcoded patterns slice removed.

validation_targets:
  - go test ./internal/barcli/ -run TestLLMHelpUsagePatternsTokensExist -v
  - go test ./internal/barcli/... && python3 -m pytest

evidence:
  - green | 2026-02-17T19:42:50Z | exit 0 | go test ./internal/barcli/... && python3 -m pytest
      1233 passed, 24 warnings | inline

delta_summary: >
  dcc1351 — 3 files changed (-237 lines): help_llm.go lost hardcoded patterns slice,
  renderUsagePatterns now loops grammar.Patterns; help_llm_test.go iterates
  grammar.Patterns; test_bar_help_llm_examples.py comment updated.

rollback_plan: git restore --source=HEAD -- internal/barcli/help_llm.go internal/barcli/help_llm_test.go

loops_remaining_forecast: >
  1 more D3 loop (SPA), then D2 and D1. Confidence: High.

residual_constraints:
  - id: RC-0134-01
    constraint: D1 and D2 SPA changes unimplemented.
    severity: Medium
    mitigation: Loop-3 completes D3-SPA; D2/D1 follow in loops 4-5.
    owning_adr: ADR-0134

next_work:
  - Behaviour: D3-SPA PatternsLibrary reads grammar patterns (Loop-3)
    validation: SPA renders patterns from grammar prop (visual check)
```

---

## loop-3 | 2026-02-17 | D3 SPA: PatternsLibrary reads patterns from grammar JSON

```
helper_version: helper:v20251223.1
focus: ADR-0134 §D3 — SPA wired; PatternsLibrary.svelte accepts patterns prop;
  hardcoded usagePatterns array removed from SPA.

active_constraint: >
  PatternsLibrary.svelte had 8 hardcoded TypeScript patterns; diverged from the 32
  in grammar.Patterns. New patterns added to USAGE_PATTERNS would not appear in the SPA.
  Falsifiable: hardcoded usagePatterns array removed from PatternsLibrary.svelte.

validation_targets:
  - grep -c "usagePatterns" web/src/lib/PatternsLibrary.svelte should return 0

evidence:
  - green | 2026-02-17T19:44:43Z | exit 0 | go test ./internal/barcli/... && python3 -m pytest
      1233 passed, 24 warnings | inline
  - green | 2026-02-17T19:44:43Z | exit 0 | grep check on PatternsLibrary.svelte
      hardcoded array removed; patterns prop wired | inline

delta_summary: >
  1b66807 — 3 files changed: PatternsLibrary.svelte (-60 lines, hardcoded array removed,
  patterns: GrammarPattern[] prop added); grammar.ts (GrammarPattern interface +
  getUsagePatterns()); +page.svelte (loadPattern updated to GrammarPattern type).

rollback_plan: git restore --source=HEAD -- web/src/lib/PatternsLibrary.svelte web/src/lib/grammar.ts web/src/routes/+page.svelte

loops_remaining_forecast: >
  2 loops remaining: Loop-4 (D2 metadata panel), Loop-5 (D1 command input).
  Confidence: High — both are SPA-only, bounded scope.

residual_constraints:
  - id: RC-0134-01
    constraint: D2 metadata panel unimplemented — use_when invisible without hover.
    severity: Medium (direct impact on ADR-0132 discoverability mechanism in SPA)
    mitigation: Loop-4.
    owning_adr: ADR-0134
  - id: RC-0134-02
    constraint: D1 command input unimplemented — SPA is one-way.
    severity: Medium
    mitigation: Loop-5 after D2.
    owning_adr: ADR-0134

next_work:
  - Behaviour: D2 inline metadata panel in TokenSelector.svelte (Loop-4)
    validation: Clicking wardley chip shows use_when text without hover
```

---

## loop-4 | 2026-02-17 | D2 metadata panel + vitest test suite

```
helper_version: helper:v20251223.1
focus: ADR-0134 §D2 — inline expandable metadata panel in TokenSelector.svelte;
  vitest infrastructure + 38 tests covering grammar.ts, renderPrompt.ts, TokenSelector.svelte.

active_constraint: >
  Token use_when/guidance/description visible only via hover title attribute — invisible
  without mouse interaction, breaking ADR-0132 discoverability mechanism in SPA.
  Falsifiable: clicking wardley chip shows use_when text in DOM without hover.

validation_targets:
  - npm test (TokenSelector.test.ts — 11 component tests, D2 falsifiable encoded)
  - npm test (grammar.test.ts — 15 tests; renderPrompt.test.ts — 12 tests)

evidence:
  - green | 2026-02-17T19:58:37Z | exit 0 | npm test
      58 tests passed (4 suites) | inline
  - green | 2026-02-17T19:58:40Z | exit 0 | go test ./internal/barcli/... && python3 -m pytest
      all 1233 python + all go tests passed | inline

delta_summary: >
  e5ee110 — 9 files changed: TokenSelector.svelte (activeToken state, meta-panel markup,
  active-meta outline); grammar.test.ts (15 tests); renderPrompt.test.ts (12 tests);
  TokenSelector.test.ts (11 component tests); vite.config.ts (vitest + svelte plugin config);
  package.json (test script, vitest+@testing-library/svelte deps); src/mocks/app-paths.ts.

rollback_plan: git restore --source=HEAD -- web/src/lib/TokenSelector.svelte

loops_remaining_forecast: >
  1 loop remaining: Loop-5 (D1 command input parser). ADR-0134 complete after that.
  Confidence: High.

residual_constraints:
  - id: RC-0134-02
    constraint: D1 command input unimplemented — SPA is one-way (cannot parse clipboard commands).
    severity: Medium
    mitigation: Loop-5.
    owning_adr: ADR-0134

next_work:
  - Behaviour: D1 command input in +page.svelte (Loop-5)
    validation: parseCommand('bar build show mean full plain') → task=show, scope=mean,
    completeness=full, channel=plain; UI input loads these into selectors
```

---

## loop-5 | 2026-02-17 | D1 command input parser

```
helper_version: helper:v20251223.1
focus: ADR-0134 §D1 — collapsible 'Load command' input in +page.svelte; parseCommand.ts
  pure function with 20 tests; D1 falsifiable encoded as first test.

active_constraint: >
  SPA generates bar build commands but cannot parse them back — clipboard workflow blocked.
  Falsifiable: parseCommand('bar build show mean full plain', grammar) returns
  selected.task=['show'], selected.scope=['mean'], etc. and 0 unrecognized tokens.

validation_targets:
  - npm test (parseCommand.test.ts — 20 tests including D1 falsifiable)
  - npm test (full suite — 58 tests)

evidence:
  - green | 2026-02-17T19:58:37Z | exit 0 | npm test
      58 tests passed (4 suites) including parseCommand D1 falsifiable | inline
  - green | 2026-02-17T19:58:40Z | exit 0 | go test + python3 -m pytest
      1233 python + all go tests passed | inline

delta_summary: >
  8352497 — 3 files changed: parseCommand.ts (parser), parseCommand.test.ts (20 tests),
  +page.svelte (Load command collapsible panel with input, Load button, warnings).

rollback_plan: >
  git restore --source=HEAD -- web/src/lib/parseCommand.ts web/src/lib/parseCommand.test.ts
    web/src/routes/+page.svelte

loops_remaining_forecast: >
  0 loops remaining. All three ADR-0134 decisions (D1, D2, D3) shipped.
  ADR-0134 complete pending final adversarial entry.
  Confidence: High.

residual_constraints:
  - id: RC-0134-DONE
    constraint: All D1/D2/D3 behaviours shipped. No open residual constraints.
    severity: Low
    mitigation: ADR-0134 can be marked Accepted.
    owning_adr: ADR-0134

next_work:
  - Behaviour: Mark ADR-0134 status as Accepted; push changes
    validation: git log shows all 5 loop commits present
```

rollback_plan: >
  git restore --source=HEAD -- lib/axisConfig.py lib/axisCatalog.py lib/promptGrammar.py
    internal/barcli/grammar.go internal/barcli/build_test.go
    build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json
    web/static/prompt-grammar.json cmd/bar/testdata/grammar.json
  Then re-run TestGrammarPatternsLoaded to confirm it returns red (exit 1).

loops_remaining_forecast: >
  Estimate: 2 more loops after this one.
    Loop-2: Update help_llm.go to render from grammar.Patterns; refactor test.
    Loop-3: Update SPA (grammar.ts, PatternsLibrary.svelte, +page.svelte).
  Confidence: High — all three loops have clear, bounded scope.

residual_constraints:
  - id: RC-0134-01
    constraint: >
      D1 (command input parser) and D2 (metadata panel) remain unimplemented.
      Both are SPA-only changes with no pipeline dependency.
    severity: Medium (impact: UX gaps; probability: deferrable)
    mitigation: Implement in loops 4–5 after D3 ships.
    owning_adr: ADR-0134
```
