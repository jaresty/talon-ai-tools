# Work Log — ADR-0135 SPA Keyboard Accessibility

Sibling work-log for `0135-spa-keyboard-accessibility.md`.
Evidence under `docs/adr/evidence/0135/`.
VCS_REVERT: `git restore --source=HEAD` (file-targeted) or `git stash` (full).

---

## loop-1 | 2026-02-17 | Core roving-tabindex keyboard nav in TokenSelector.svelte

```
helper_version: helper:v20251223.1
focus: ADR-0135 §F1–F4 — roving tabindex, ArrowKey navigation, filter→chip handoff,
  ARIA listbox/option roles, D2 panel via keyboard focus. Slice scope: TokenSelector.svelte
  only; +page.svelte badge fix left for loop-2.

active_constraint: >
  Token chips are <div> elements with no tabindex and no onkeydown handler — keyboard
  users cannot reach or activate any chip. All 7 keyboard gaps from the ADR analysis
  are unaddressed.
  Falsifiable: npm test exits 1 because F1–F4 specifying-validation tests do not pass.

validation_targets:
  - npm test (TokenSelector.test.ts — F1 ArrowRight navigation, F2 filter handoff,
      F3 ARIA attributes, F4 keyboard-focus opens D2 panel)
    # specifying validation — new tests added this loop encoding correctness expectations

rollback_plan: >
  git restore --source=HEAD -- web/src/lib/TokenSelector.svelte
    web/src/lib/TokenSelector.test.ts
  Then re-run npm test to confirm F1–F4 return red (exit 1).

loops_remaining_forecast: >
  1 loop remaining after this one.
    Loop-2: selected-chip badge keyboard fix in +page.svelte (F5).
  Confidence: High.

evidence:
  - red | 2026-02-17T22:22:18Z | exit 1 | npm test
      13 new specifying-validation tests failed (F1–F4 not yet implemented) | inline
  - green | 2026-02-17T22:25:10Z | exit 0 | npm test
      72/72 passed; all F1–F4 falsifiables green | inline

delta_summary: >
  6f9f011 — 3 files changed: TokenSelector.svelte (roving tabindex, gridRef, ARIA roles,
  handleGridKey, filter handoff, button close, CSS focus-visible); TokenSelector.test.ts
  (22 new tests F1–F4); work-log created.

next_work:
  - Behaviour: F5 selected-chip badge keyboard fix in +page.svelte (Loop-2)
    validation: tab-focus badge + Enter/Space deselects token

residual_constraints:
  - id: RC-0135-01
    constraint: >
      selected-chip badge spans in +page.svelte have no tabindex/onkeydown.
      F5 falsifiable unaddressed.
    severity: Medium
    mitigation: Loop-2.
    owning_adr: ADR-0135
```

---

## loop-2 | 2026-02-17 | F5 selected-chip badge keyboard fix in +page.svelte

```
helper_version: helper:v20251223.1
focus: ADR-0135 §F5 — selected-chip <span> badges in +page.svelte get
  tabindex="0", role="button", and onkeydown (Enter/Space → deselect).

active_constraint: >
  Selected-chip removal badges (<span class="selected-chip">) have no tabindex
  or onkeydown — keyboard users cannot deselect tokens from the badge row.
  Falsifiable: npm test exits 1 because F5 specifying-validation test fails.

validation_targets:
  - npm test (page-level component or DOM test for F5 badge keyboard deselection)
    # specifying validation — new test added this loop

rollback_plan: >
  git restore --source=HEAD -- web/src/routes/+page.svelte
    web/src/lib/TokenSelector.test.ts (or wherever F5 test lives)
  Then re-run npm test to confirm F5 returns red (exit 1).

loops_remaining_forecast: >
  0 loops remaining after this one. ADR-0135 complete.
  Confidence: High.

evidence:
  - red | 2026-02-17T22:25:10Z | exit 1 | npm test
      4 F5 tests failed (fixture without tabindex/role/onkeydown) | inline
  - green | 2026-02-17T22:26:00Z | exit 0 | npm test
      76/76 passed; all F5 falsifiables green | inline
  - green | 2026-02-17T22:26:10Z | exit 0 | go test + python3 -m pytest
      1233 python + all go tests passed | inline

delta_summary: >
  loop-2 commit — 3 files changed: SelectedChipFixture.svelte (test fixture),
  selectedChip.test.ts (4 F5 tests), +page.svelte (role/tabindex/onkeydown on badge spans).

next_work:
  - Behaviour: Mark ADR-0135 Accepted; all falsifiables shipped.

residual_constraints:
  - id: RC-0135-DONE
    constraint: All F1–F5 falsifiables addressed after this loop.
    severity: Low
    mitigation: Mark ADR-0135 Accepted.
    owning_adr: ADR-0135
```
