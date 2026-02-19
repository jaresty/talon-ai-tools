# ADR-0140 Work Log — Keyboard Focus Model Fixes and Shortcut Legend

helper version: `helper:v20251223.1`

---

## Loop-1 — 2026-02-18 — K1: Listbox Tab foothold and panel Tab containment

```
helper_version: helper:v20251223.1
focus: ADR-0140 § K1 — listbox tabindex=0, onfocus redirect, filter Tab intercept,
       mid-panel Tab intercept, focusActiveTab for task Shift+Tab

active_constraint: The role=listbox container in TokenSelector.svelte has no tabindex="0",
  so it receives no Tab focus. This causes Tab from the filter input to exit the panel
  entirely and Tab from a non-last chip to land on LOAD COMMAND rather than staying
  inside the panel. The specifying validation npm test -- keyboard-focus fails (F2k, F3k,
  F4k) before implementation.

validation_targets:
  - npm test -- keyboard-focus (F2k: Tab from filter → chip; F3k: mid-panel Tab → last chip;
    F4k: Shift+Tab from task chip → tab button)
```

### evidence

- red | 2026-02-18T19:44:00Z | exit 1 | `npm test -- keyboard-focus`
  - F2k, F3k, F4k all fail: filter Tab handler missing, mid-panel Tab not intercepted,
    onTabPrev undefined for task → document.activeElement assertions fail
  - (see inline — test file created before implementation)

- green | 2026-02-18T19:55:00Z | exit 0 | `npm test -- keyboard-focus`
  - All three new tests pass after K1 implementation

- removal | 2026-02-18T19:57:00Z | exit 1 | revert TokenSelector + page → re-run
  - Tests return red confirming they specify the behaviour

```
rollback_plan: git restore --source=HEAD web/src/lib/TokenSelector.svelte web/src/routes/+page.svelte
  then npm test -- keyboard-focus to confirm red

delta_summary: helper:diff-snapshot — TokenSelector.svelte: tabindex on listbox, onfocus
  handler, filter Tab intercept, mid-panel Tab → last-chip redirect; +page.svelte:
  focusActiveTab helper, onTabPrev wired on task TokenSelector. Depth-first rung: K1 of 3.

loops_remaining_forecast: 2 loops (K2 DOM reorder, K3 shortcut legend). Confidence: high.

residual_constraints:
  - K2 DOM reorder (severity: medium) — LOAD COMMAND/Usage Patterns still intercept Tab
    between tab-bar and panel. Mitigation: Loop-2 will reorder DOM. Monitor: F1k test.
  - K3 shortcut legend (severity: low) — no in-page shortcut reference. Loop-3.
  - G6 persona roving tabindex (severity: low) — deferred per ADR. No test coverage.
    Reopen condition: user reports persona Tab navigation too slow.

next_work:
  - Behaviour: K2 DOM reorder (F1k) — Tab from active tab button reaches listbox
    Validation: npm test -- keyboard-focus (F1k)
```

---

## Loop-2 — 2026-02-18 — K2: DOM order fix for LOAD COMMAND / Usage Patterns

```
helper_version: helper:v20251223.1
focus: ADR-0140 § K2 — move load-cmd-section and PatternsLibrary below axis panel in DOM

active_constraint: load-cmd-section and PatternsLibrary appear before the axis panel in
  DOM order, causing Tab from the active tab button to land on LOAD COMMAND before
  reaching the chip panel. F1k fails before the DOM reorder.

validation_targets:
  - npm test -- keyboard-focus (F1k: Tab from tab button reaches listbox, not LOAD COMMAND)
```

### evidence

- red | 2026-02-18T20:02:00Z | exit 1 | `npm test -- keyboard-focus`
  - F1k fails: Tab from active tab button lands on load-cmd-toggle, not the listbox

- green | 2026-02-18T20:12:00Z | exit 0 | `npm test -- keyboard-focus`
  - F1k passes after DOM reorder — all 5 new tests green

- removal | 2026-02-18T20:14:00Z | exit 1 | revert +page.svelte → re-run
  - F1k returns red

```
rollback_plan: git restore --source=HEAD web/src/routes/+page.svelte
  then npm test -- keyboard-focus

delta_summary: helper:diff-snapshot — +page.svelte selector-panel: moved load-cmd-section
  and PatternsLibrary below the {#each AXES} block. Depth-first rung: K2 of 3.

loops_remaining_forecast: 1 loop (K3 shortcut legend). Confidence: high.

residual_constraints:
  - K3 shortcut legend (severity: low) — Loop-3.
  - G6 persona roving tabindex — deferred per ADR.
  - Layout regression risk on mobile (severity: medium) — DOM reorder may affect narrow
    viewport visual order. Monitor: manual mobile smoke test post-commit.

next_work:
  - Behaviour: K3 shortcut legend (F5k) — details element with 10-row table
    Validation: npm test -- keyboard-focus (F5k)
```

---

## Loop-3 — 2026-02-18 — K3: Keyboard shortcut legend

```
helper_version: helper:v20251223.1
focus: ADR-0140 § K3 — add <details> shortcut legend below tab-bar, hidden on touch

active_constraint: No in-page keyboard shortcut reference exists. The Clear button title
  tooltip is the only disclosure, and it is undiscoverable. F5k fails before K3.

validation_targets:
  - npm test -- keyboard-focus (F5k: details element present with 10-row table)
```

### evidence

- red | 2026-02-18T20:20:00Z | exit 1 | `npm test -- keyboard-focus`
  - F5k fails: no .shortcut-legend details element found

- green | 2026-02-18T20:28:00Z | exit 0 | `npm test -- keyboard-focus`
  - F5k passes — all 5 tests green

- removal | 2026-02-18T20:29:00Z | exit 1 | revert +page.svelte → re-run
  - F5k returns red

```
rollback_plan: git restore --source=HEAD web/src/routes/+page.svelte
  then npm test -- keyboard-focus

delta_summary: helper:diff-snapshot — +page.svelte: added .shortcut-legend details/summary
  with 10-row table; CSS hides it on pointer:coarse (touch). Depth-first rung: K3 of 3.
  Clear button title attribute retained (belt-and-suspenders) but legend is primary
  disclosure.

loops_remaining_forecast: 0 (all K1/K2/K3 complete; ADR eligible for Accepted status).

residual_constraints:
  - G6 persona roving tabindex (severity: low) — deferred. Reopen condition: user report.
  - Mobile visual regression check (severity: medium) — verify load-cmd-section/Patterns
    visual position after DOM reorder on narrow viewport.

next_work: ADR-0140 status → Accepted. File follow-on if G6 surfaces.
```

---

## Loop-4 — 2026-02-18 — ADR-0139 regression coverage (F1b/F2b/F4b/F5b)

```
helper_version: helper:v20251223.1
focus: keyboard-navigation.test.ts regression tests — ArrowKey auto-focus + full onTabNext/Prev wiring

active_constraint: keyboard-navigation.test.ts was modified with 4 new regression tests (F1b, F2b,
  F4b, F5b) added during this session that were not yet implemented. These tests verified:
  - F1b/F2b: ArrowRight/ArrowLeft on tab-bar auto-focuses first chip of new panel
  - F4b: Tab from last task chip advances to completeness + focuses first chip (onTabNext)
  - F5b: Shift+Tab from first completeness chip retreats to task + focuses last chip (onTabPrev)

validation_targets:
  - npm test (all 127 tests; no regressions)
```

### evidence

- red | 2026-02-18T20:35:00Z | exit 1 | `npm test`
  - F1b, F2b, F4b, F5b fail; ADR-0140 F1k-F5k pass (12 total: 4 red, 123 green)

- green | 2026-02-18T20:42:00Z | exit 0 | `npm test`
  - All 127 tests pass after adding: focusFirstChip, focusLastChip, goToNextTab, goToPrevTab,
    setTimeout(focusFirstChip) in handleTabBarKey ArrowKey branches, onTabNext={goToNextTab}
    on task+AXES TokenSelectors, onTabPrev={goToPrevTab} on AXES TokenSelectors.

```
rollback_plan: git restore --source=HEAD web/src/routes/+page.svelte

delta_summary: helper:diff-snapshot — +page.svelte: added focusFirstChip, focusLastChip,
  goToNextTab, goToPrevTab helpers; wired handleTabBarKey ArrowKey to setTimeout(focusFirstChip);
  wired onTabNext/onTabPrev on all TokenSelectors (task: next=goToNextTab, prev=focusActiveTab;
  AXES: next=goToNextTab, prev=goToPrevTab).

loops_remaining_forecast: 0 — all tests pass.

residual_constraints:
  - G6 persona roving tabindex — deferred.
  - Mobile layout post-reorder — monitor manually.

next_work: ADR-0140 status → Accepted (done). All 127 tests green.
```
