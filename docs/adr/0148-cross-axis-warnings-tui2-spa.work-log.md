# ADR-0148 Work Log: Cross-Axis Composition Warnings in TUI2 and SPA

EVIDENCE_ROOT: docs/adr/evidence/0148
ARTEFACT_LOG: docs/adr/evidence/0148/loop-N.md
VCS_REVERT: git restore --source=HEAD

---

## Loop 1 — Phase 1a: Coverage expansion data (2026-02-27)

```yaml
helper_version: helper:v20251223.1
focus: >
  ADR-0148 Phase 1a — Add Tier 1 + Tier 2 entries to CROSS_AXIS_COMPOSITION in
  lib/axisConfig.py; run make bar-grammar-update; verify renderCrossAxisComposition
  picks up new entries via dev binary.
active_constraint: >
  CROSS_AXIS_COMPOSITION has no entries for presenterm, html.task, adr.completeness,
  codetour.audience, gherkin.completeness, or sync.task — the Tier 1/2 tokens required
  by ADR-0148 Part D. The constraint is falsifiable: `go build -o /tmp/bar-new
  ./cmd/bar/main.go && /tmp/bar-new help llm | grep presenterm` exits 0 but produces no
  output. Alternative candidate: implement TUI2 display first (Phase 1b) — lower
  expected value because display code is only useful once data exists; data is a strict
  prerequisite. EV: Impact=H (all three surfaces need the data), Probability=H
  (deterministic add), TimeSensitivity=H (blocks Phases 1b, 1c, 2). Product=27.
validation_targets:
  - T-1a: go build -o /tmp/bar-new ./cmd/bar/main.go && /tmp/bar-new help llm | grep -A5 presenterm
  - T-1b: go test ./internal/barcli/ -run TestLLMHelp (regression guard)
evidence:
  - red   | 2026-02-27T00:00:00Z | exit 0 but empty output | /tmp/bar-new help llm | grep presenterm
      helper:diff-snapshot=0 files changed
      presenterm not in CROSS_AXIS_COMPOSITION; grep returns empty | inline
  - green | see evidence/0148/loop-1.md
rollback_plan: git restore --source=HEAD lib/axisConfig.py; go build -o /tmp/bar-new ./cmd/bar/main.go && /tmp/bar-new help llm | grep presenterm  (should return empty again)
delta_summary: >
  Added adr.task.cautionary(sim), adr.completeness, codetour.audience,
  gherkin.completeness, sync.task (Tier 1) and presenterm.task, presenterm.completeness,
  html.task (Tier 2) to CROSS_AXIS_COMPOSITION. make bar-grammar-update regenerated
  all grammar JSON artefacts. Rung: data added → grammar regenerated → dev binary
  verified.
loops_remaining_forecast: >
  4 loops remaining: 1b (TUI2 meta sections), 1c (TUI2 chip prefix),
  2 (SPA + prose cleanup). Confidence: high — each loop has clear scope and
  established validation paths.
residual_constraints:
  - TUI2 display (Phase 1b): not started; data now available. Severity: M.
      Monitoring: addressed in Loop 2.
  - SPA display (Phase 2): not started; blocked on Phase 1b. Severity: M.
  - Prose cleanup (Part C): not started; blocked on Phase 2 meta panel rendering
      being verified. Severity: L. Monitoring: addressed in Loop 4.
next_work:
  - Behaviour T-1b: TUI2 always-on meta sections for channel/form tokens (Phase 1b).
      Validation: extend TUI2 smoke fixture and run go test ./internal/barcli/ -run TestTUI2Smoke.
```

---

## Loop 2 — Phase 1b: TUI2 always-on cross-axis meta sections (2026-02-27)

```yaml
helper_version: helper:v20251223.1
focus: >
  ADR-0148 Phase 1b — Add always-on cross-axis meta sections to TUI2 token
  browser. Direction A: when a channel/form token is focused, render natural
  partners (cyan) and cautionary partners (amber) in the meta pane. Direction B:
  when a task/completeness token is focused, check active channel/form selections
  and render caution lines per active token.
active_constraint: >
  TUI2 renders no cross-axis composition sections in the meta pane — browsing
  shellscript shows no "✓ Natural task:" or "⚠ Caution:" lines. Falsifiable:
  `go test ./internal/bartui2/ -run TestCrossAxisCompositionDirectionA` exits 1
  with "no output matching". Alternative: ship SPA first — lower EV because TUI2
  is used by bar CLI users directly; TUI2 is the higher-impact surface.
  EV: Impact=H (primary interactive surface), Probability=H, TimeSensitivity=H
  (Phase 1c chip prefix depends on this). Product=27.
validation_targets:
  - T-2a: go test ./internal/bartui2/ -run TestCrossAxisCompositionDirectionA
  - T-2b: go test ./internal/bartui2/ -run TestCrossAxisCompositionDirectionB
  - T-2c: go test ./... (full regression)
evidence:
  NOTE: Loops 2 and 3 were implemented and committed in the same session. Evidence
  was captured at implementation time and is not re-verifiable without branch surgery.
  Commit d997e48 (2026-02-27T08:37:16-08:00) is the green artefact.
  - red   | ~2026-02-27T08:30:00-08:00 | exit 1, 2 ADR-0148 specifying tests fail |
      go test ./internal/bartui2/ -run TestCrossAxisCompositionDirection
      specifying tests (TestCrossAxisCompositionDirectionA/B) written before impl | inline
  - green | 2026-02-27T08:37:16-08:00 | commit d997e48 | exit 0, PASS (2/2 tests) |
      go test ./internal/bartui2/ -run TestCrossAxisCompositionDirection
      CrossAxisCompositionFor wired in tui2.go; meta section rendering added;
      description capped at 2 lines when sections non-empty; paneHeight < 12 guard | commit
  - removal | ~2026-02-27T08:37:00-08:00 | revert impl → 2 fail → restore → 2 pass | inline
rollback_plan: >
  git restore --source=HEAD internal/barcli/tui2.go internal/bartui2/program.go;
  go test ./internal/bartui2/ -run TestCrossAxisCompositionDirection (should fail)
delta_summary: >
  internal/barcli/tui2.go: renderCrossAxisSections(); integrated into meta pane;
  description capped at 2 lines when sections non-empty; paneHeight < 12 guard.
  internal/bartui2/program.go: CrossAxisCompositionFor callback wired via
  grammar accessor. Two specifying tests added to internal/bartui2/program_test.go
  (lines 2634, 2681). Commit d997e48.
loops_remaining_forecast: >
  2 loops remaining: 1c (TUI2 chip prefix column), 4 (SPA + prose cleanup).
  Confidence: high.
residual_constraints:
  - TUI2 chip prefix (Phase 1c): not started; depends on Phase 1b now done. Severity: M.
  - SPA display (Phase 2): not started. Severity: M.
  - Prose cleanup (Part C): not started. Severity: L.
next_work:
  - Behaviour T-1c: TUI2 chip traffic light prefix column for task/completeness axes.
      Validation: go test ./internal/bartui2/ -run TestCrossAxisChipPrefixColumn.
```

---

## Loop 3 — Phase 1c: TUI2 chip traffic light prefix column (2026-02-27)

```yaml
helper_version: helper:v20251223.1
focus: >
  ADR-0148 Phase 1c — Add 1-char prefix column to TUI2 completion rows for task
  and completeness axes. When a channel/form token is active, each row shows
  ✓ (natural), ⚠ (cautionary), or space (neutral). Prefix column always present
  when showPrefixColumn to prevent layout shift. Audience axis excluded.
  Disabled when paneHeight < 12 (same threshold as meta sections).
active_constraint: >
  TUI2 completion rows for task/completeness show no traffic-light prefix when a
  channel/form token is active. Falsifiable: `go test ./internal/bartui2/ -run
  TestCrossAxisChipPrefixColumn` exits 1. Alternative: skip prefix and rely on
  meta sections only — lower EV because prefix gives at-a-glance signal without
  requiring selection. EV: Impact=M, Probability=H, TimeSensitivity=M. Product=18.
validation_targets:
  - T-3a: go test ./internal/bartui2/ -run TestCrossAxisChipPrefixColumn
  - T-3b: go test ./... (full regression)
evidence:
  NOTE: Loop 3 was implemented and committed in the same session as Loop 2. Evidence
  captured at implementation time. Commit 288d43e (2026-02-27T08:39:13-08:00) is
  the green artefact.
  - red   | ~2026-02-27T08:38:00-08:00 | exit 1, FAIL TestCrossAxisChipPrefixColumn |
      go test ./internal/bartui2/ -run TestCrossAxisChipPrefixColumn
      specifying test written before impl | inline
  - green | 2026-02-27T08:39:13-08:00 | commit 288d43e | exit 0, PASS (1/1 test) |
      go test ./internal/bartui2/ -run TestCrossAxisChipPrefixColumn
      chipState() added; prefix column rendered; cautionary overrides natural;
      showPrefixColumn guard prevents layout shift | commit
  - removal | ~2026-02-27T08:39:00-08:00 | revert impl → 1 fail → restore → 1 pass | inline
rollback_plan: >
  git restore --source=HEAD internal/bartui2/program.go;
  go test ./internal/bartui2/ -run TestCrossAxisChipPrefixColumn (should fail)
delta_summary: >
  internal/bartui2/program.go: chipState() iterates active channel/form selections;
  cautionary overrides natural when multiple active tokens conflict; prefix column
  (1 char) added to completion row render; showPrefixColumn guard prevents layout
  shift. Scope: task + completeness only; audience excluded per ADR-0148 §Chip scope.
  One specifying test added to internal/bartui2/program_test.go (line 2728).
  Commit 288d43e.
loops_remaining_forecast: >
  1 loop remaining: Loop 4 (SPA always-on meta panel + guidance prose cleanup).
  Confidence: high.
residual_constraints:
  - SPA display (Phase 2): not started. Severity: M.
  - Prose cleanup (Part C): not started; lower priority, addressed in Loop 4. Severity: L.
next_work:
  - Behaviour T-2/T-3: SPA always-on meta panel (direction A) + chip traffic lights
      (direction B) + Part C guidance prose cleanup.
      Validation: npx vitest run src/lib/TokenSelector.test.ts
```

---

## Loop 4 — Phase 2: SPA always-on meta panel + Part C guidance prose cleanup (2026-02-27)

```yaml
helper_version: helper:v20251223.1
focus: >
  ADR-0148 Phase 2 (T-2 + T-3) and Part C — Three deliverables in one loop:
  (A) SPA always-on meta panel: when a channel/form token is focused show "Works
  well with" (natural partners) and "Caution" (cautionary partners with warning
  text) sections; (B) SPA chip traffic lights: chip--natural / chip--cautionary
  CSS classes on task/completeness chips based on active channel/form selections;
  (C) Part C guidance prose cleanup: remove cross-axis content from
  AXIS_KEY_TO_GUIDANCE for tokens whose cross-axis info now lives in
  CROSS_AXIS_COMPOSITION (adr, code, codetour, html, shellscript channel entries;
  max completeness trailing clause; commit form trailing clause).
active_constraint: >
  SPA shows no cross-axis meta panel sections or chip traffic lights — browsing
  shellscript in the axis selector shows no "Works well with" or "Caution"
  sections; selecting shellscript and browsing task shows no chip colour coding.
  Falsifiable: `npx vitest run src/lib/TokenSelector.test.ts` exits 1 with 4
  ADR-0148 specifying test failures. Alternative: ship TUI2-only and defer SPA —
  lower EV because SPA is the web-facing surface used by new users.
  EV: Impact=H, Probability=H, TimeSensitivity=M. Product=24.
validation_targets:
  - T-4a: npx vitest run src/lib/TokenSelector.test.ts (8 new ADR-0148 tests)
  - T-4b: npx vitest run (219 SPA tests full regression)
  - T-4c: go test ./internal/barcli/ (Go regression after Part C + grammar regen)
evidence:
  - red   | 2026-02-27T19:37:39Z | exit 1, 4 ADR-0148 tests fail (57 pass) |
      cd web && npx vitest run src/lib/TokenSelector.test.ts
      FAIL: "meta panel shows 'Works well with' section for channel token with natural data"
      FAIL: "meta panel shows 'Caution' section for channel token with cautionary data"
      FAIL: "task chips show chip--cautionary class when shellscript is active"
      FAIL: "task chips show chip--natural class for natural tokens when shellscript is active"
      (verified by: git stash -- src/lib/TokenSelector.svelte src/lib/grammar.ts
       src/routes/+page.svelte; run tests; git stash pop) | inline
  - green | 2026-02-27T19:37:43Z | exit 0, 61/61 pass |
      cd web && npx vitest run src/lib/TokenSelector.test.ts
      "Test Files: 1 passed (1), Tests: 61 passed (61), Duration: 1.19s"
      grammar.ts: CrossAxisPair + cross_axis_composition + getCompositionData + getChipState;
      TokenSelector.svelte: grammar/activeTokensByAxis props; resolveChipState/
        activeMetaComposition derived; chip--natural/chip--cautionary class bindings;
        Works well with + Caution meta sections; CSS rules;
      +page.svelte: grammar + activeTokensByAxis={selected} wired to both selectors;
      13 route test mocks: getCompositionData/getChipState added;
      Part C: AXIS_KEY_TO_GUIDANCE trimmed; make bar-grammar-update: 4 JSONs regenerated;
      Go tests: 3 tests migrated to CrossAxisCompositionFor checks | inline
  - removal | 2026-02-27T19:37:39Z | git stash (3 impl files) → 4 fail; stash pop → 61 pass |
      git stash -- src/lib/TokenSelector.svelte src/lib/grammar.ts src/routes/+page.svelte;
      npx vitest run → 57 pass 4 fail; git stash pop → 61 pass | inline
rollback_plan: >
  git restore --source=HEAD web/src/lib/grammar.ts web/src/lib/TokenSelector.svelte
  web/src/routes/+page.svelte lib/axisConfig.py;
  make bar-grammar-update;
  npx vitest run src/lib/TokenSelector.test.ts (should show 4 ADR-0148 failures)
delta_summary: >
  24 files changed, 421 insertions(+), 94 deletions(-).
  grammar.ts (+49): CrossAxisPair, cross_axis_composition, getCompositionData, getChipState.
  TokenSelector.svelte (+68): grammar/activeTokensByAxis props; resolveChipState/
    activeMetaComposition derived; chip--natural/chip--cautionary class bindings
    (grouped + flat blocks); Works well with + Caution meta sections; 3 CSS rules.
  TokenSelector.test.ts (+173): 8 ADR-0148 specifying tests (4 direction-A meta panel,
    4 chip traffic light); testGrammar fixture with CROSS_AXIS_COMPOSITION stub;
    upstream "filter closes panel" test merged after rebase.
  +page.svelte (+4): grammar + activeTokensByAxis={selected} on both TokenSelector instances.
  13 route test files (+4 each): getCompositionData + getChipState mocks added.
  axisConfig.py (+64/-11): 7 accessor functions restored after rebase conflict;
    Part C: 5 channel guidance entries removed, max/commit guidance trimmed.
  4 grammar JSONs (-13 each): cross-axis guidance prose removed; regenerated.
  2 Go test files (+26/-5, +27/-5): 3 tests migrated to CrossAxisCompositionFor assertions.
  Also resolved rebase conflicts: upstream bound token + CI + SPA filter fix merged cleanly.
loops_remaining_forecast: >
  0 loops remaining — all ADR-0148 phases complete (1a data, 1b TUI2 meta,
  1c TUI2 chip prefix, 2 SPA meta + chip + Part C prose cleanup).
  ADR-0148 ready for Accepted state.
residual_constraints: []
next_work:
  - Update ADR-0148 status from Proposed → Accepted (per loop helper contract).
  - Run bar build sanity check: `bar build shellscript make --subject "test"` to
      confirm cross-axis guidance renders correctly in help llm output.
```
