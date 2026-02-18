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

residual_constraints:
  - id: RC-0135-01
    constraint: >
      selected-chip badge spans in +page.svelte have no tabindex/onkeydown.
      F5 falsifiable unaddressed.
    severity: Medium
    mitigation: Loop-2.
    owning_adr: ADR-0135
```
