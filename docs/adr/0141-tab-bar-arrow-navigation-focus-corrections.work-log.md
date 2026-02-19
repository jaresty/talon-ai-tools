# ADR-0141 Work Log — Tab-Bar Arrow Navigation and Focus Model Corrections

helper version: `helper:v20251223.1`

---

## Loop-1 — 2026-02-19 — K1: Correct ArrowKey focus + K3: Move shortcut legend

```
helper_version: helper:v20251223.1
focus: ADR-0141 § K1 — replace setTimeout(focusFirstChip) with setTimeout(focusActiveTab)
       in handleTabBarKey; delete F1b/F2b; add F1c/F2c.
       ADR-0141 § K3 — move shortcut-legend details below PatternsLibrary.

active_constraint: handleTabBarKey calls setTimeout(focusFirstChip) after ArrowKey, causing
  focus to escape the tab strip to the first chip of the new panel. F1b/F2b specify this
  wrong behavior. The correct ARIA tabs pattern keeps focus on the tab button after ArrowKey.
  Validation: npm test -- keyboard-navigation (F1c, F2c must go red before fix, green after).

validation_targets:
  - npm test -- keyboard-navigation (F1c, F2c, F3c)
  - npm test -- keyboard-focus (F5k)
```

### evidence

- red | 2026-02-19T01:20:00Z | exit 1 | `npm test -- keyboard-navigation`
  - F1c, F2c fail: ArrowKey calls setTimeout(focusFirstChip) → focus on chip not tab button
  - F3c fails: directional → persona wrap; focusFirstChip finds no [role="option"], focus lost to body

- green | 2026-02-19T01:22:31Z | exit 0 | `npm test` (128 tests)
  - All 128 pass after K1 (focusActiveTab in handleTabBarKey), K2 (persona fallback in
    focusFirstChip), K3 (shortcut legend moved below PatternsLibrary)

- removal | 2026-02-19T01:21:00Z | exit 1 | `git restore --source=HEAD web/src/routes/+page.svelte && npm test -- keyboard-navigation`
  - F1c, F2c, F3c return red with original implementation

```
rollback_plan: git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/keyboard-navigation.test.ts

delta_summary: helper:diff-snapshot — 4 files changed, 253 insertions(+), 39 deletions(-).
  +page.svelte: handleTabBarKey ArrowKey branches → focusActiveTab; focusFirstChip persona
  fallback; shortcut-legend moved after PatternsLibrary.
  keyboard-navigation.test.ts: F1b/F2b deleted; F1c/F2c/F3c added.
  ADR-0141 and work-log created. Depth-first: all three rungs (K1/K2/K3) in one loop.

loops_remaining_forecast: 0 — all K1/K2/K3 complete. ADR eligible for Accepted.

residual_constraints:
  - Mid-panel Tab → last chip redirect (K1 F3k) retained; no test failures observed.
    Reopen condition: user reports linear-Tab expectation broken. Severity: low.
  - Persona panel Tab-exhaustion now focuses first persona-chip button — verify visually
    that focus lands on a useful element. Severity: low.

next_work: ADR-0141 → Accepted. No further loops required.
```
