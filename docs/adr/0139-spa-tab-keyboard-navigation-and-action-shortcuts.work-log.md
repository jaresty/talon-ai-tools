# Work-log: ADR-0139 SPA Tab Keyboard Navigation and Action Shortcuts

Helper version: `helper:v20251223.1`

---

## Loop-1 — 2026-02-18 | T1: ARIA tablist on tab-bar nav

**helper_version:** `helper:v20251223.1`

**focus:** ADR-0139 §T1 — Add ARIA tablist semantics and arrow-key navigation to the tab-bar nav. Active constraint: tab buttons have no `role="tab"` or keyboard handler, so keyboard users cannot navigate between axes at all.

**active_constraint:** The tab `<nav>` has no `role="tablist"` and buttons have no `role="tab"` or `onkeydown` handler. `F1`/`F2`/`F3` tests do not yet exist and `npm test -- keyboard-navigation` exits non-zero because the test file is absent. Impact: High (keyboard users cannot navigate axes). Probability: High (deterministic). Time sensitivity: High (foundation for T2/T3). Expected value: High × High × High.

**validation_targets:** `npm test -- keyboard-navigation` targeting F1/F2/F3 in `web/src/routes/keyboard-navigation.test.ts`.

**evidence:**
- red | 2026-02-18T18:30:00Z | exit 1 | `cd web && npx vitest run src/routes/keyboard-navigation.test.ts`
  - helper:diff-snapshot=0 files changed
  - F1/F2/F3 tests absent; test file does not exist — vitest exits 1 with "No test files found" | inline
- green | 2026-02-18T18:45:00Z | exit 0 | `cd web && npx vitest run src/routes/keyboard-navigation.test.ts`
  - helper:diff-snapshot=3 files changed, 142 insertions(+), 4 deletions(-)
  - F1/F2/F3 pass: tablist role, tab roles, aria-selected, ArrowRight/Left advance activeTab | inline
- removal | 2026-02-18T18:46:00Z | exit 1 | `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/keyboard-navigation.test.ts && cd web && npx vitest run src/routes/keyboard-navigation.test.ts`
  - helper:diff-snapshot=0 files changed
  - F1/F2/F3 fail again after revert | inline

**rollback_plan:** `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/keyboard-navigation.test.ts` then replay red command.

**delta_summary:** Added `keyboard-navigation.test.ts` (F1/F2/F3 specifying tests). Added `role="tablist"` to `<nav>`, `role="tab"` + `aria-selected` + `aria-controls` + managed `tabindex` to each tab button, `role="tabpanel"` + `id` + `aria-labelledby` + `tabindex="0"` to each panel. Added `handleTabKey` function with ArrowLeft/Right/Home/End and focus management on keyboard tab switch. Commit: loop-1 green.

**loops_remaining_forecast:** 2 loops (T2 auto-advance, T3 action shortcuts). Confidence: High — scope is well-bounded.

**residual_constraints:**
- T2 auto-advance: Tab key still exits axis panel without advancing to next tab. Severity: High. Mitigation: next loop. Monitoring: F4/F5 tests. Reopen: if Tab-exhaustion intercept breaks mobile or non-chip panels.
- T3 action shortcuts: Cmd+Shift+C/P/U not yet wired. Severity: Medium. Mitigation: loop 3. Monitoring: F6/F7/F8 tests.

**next_work:**
- Behaviour T2: Auto-advance Tab-exhaustion. Validation: `npm test -- keyboard-navigation` F4/F5. Future-shaping: `onTabNext`/`onTabPrev` callbacks make the advance contract explicit and testable.

---

## Loop-2 — 2026-02-18 | T2: Auto-advance Tab-exhaustion

**helper_version:** `helper:v20251223.1`

**focus:** ADR-0139 §T2 — Tab from last chip in axis auto-advances to next tab; Shift+Tab from first chip retreats to previous. Active constraint: Tab from the last chip in a panel exits to Subject textarea, skipping all remaining axes.

**active_constraint:** `TokenSelector.svelte` has no `onTabNext`/`onTabPrev` props and `handleGridKey` does not intercept Tab. F4/F5 tests do not exist and will fail. Impact: High. Probability: High. Time sensitivity: High. Expected value: High.

**validation_targets:** `npm test -- keyboard-navigation` targeting F4/F5 in `keyboard-navigation.test.ts`.

**evidence:**
- red | 2026-02-18T19:00:00Z | exit 1 | `cd web && npx vitest run src/routes/keyboard-navigation.test.ts`
  - helper:diff-snapshot=0 files changed
  - F4/F5 tests absent; suite exits 1 | inline
- green | 2026-02-18T19:20:00Z | exit 0 | `cd web && npx vitest run src/routes/keyboard-navigation.test.ts`
  - helper:diff-snapshot=2 files changed, 48 insertions(+), 2 deletions(-)
  - F4/F5 pass: Tab on last chip fires onTabNext; Shift+Tab on first chip fires onTabPrev | inline
- removal | 2026-02-18T19:21:00Z | exit 1 | `git restore --source=HEAD web/src/lib/TokenSelector.svelte web/src/routes/+page.svelte web/src/routes/keyboard-navigation.test.ts && cd web && npx vitest run src/routes/keyboard-navigation.test.ts`
  - helper:diff-snapshot=0 files changed
  - F4/F5 fail again | inline

**rollback_plan:** `git restore --source=HEAD web/src/lib/TokenSelector.svelte web/src/routes/+page.svelte web/src/routes/keyboard-navigation.test.ts` then replay red.

**delta_summary:** Added `onTabNext?: () => void` and `onTabPrev?: () => void` optional props to `TokenSelector`. Extended `handleGridKey` to intercept Tab (last chip → call onTabNext) and Shift+Tab (first chip → call onTabPrev). In `+page.svelte`: wired `onTabNext`/`onTabPrev` to axis-advance functions that update `activeTab` and schedule `firstChip?.focus()` via `requestAnimationFrame`. Added F4/F5 test cases. Commit: loop-2 green.

**loops_remaining_forecast:** 1 loop (T3 action shortcuts). Confidence: High.

**residual_constraints:**
- Persona panel auto-advance: persona panel is not a TokenSelector; Tab from its last select will still exit to Subject textarea. Severity: Low (persona is rarely the last configured axis). Mitigation: deferred. Monitoring: manual test.
- T3 action shortcuts: Cmd+Shift+C/P/U not yet wired. Severity: Medium. Mitigation: next loop.

**next_work:**
- Behaviour T3: Action shortcuts. Validation: `npm test -- keyboard-navigation` F6/F7/F8. Future-shaping: shortcuts surfaced in button tooltips.

---

## Loop-3 — 2026-02-18 | T3: Action keyboard shortcuts

**helper_version:** `helper:v20251223.1`

**focus:** ADR-0139 §T3 — Add Cmd+Shift+C (copy cmd), Cmd+Shift+P (copy prompt), Cmd+Shift+U (share) to the global keydown handler. Active constraint: common actions require mouse; F6/F7/F8 tests do not exist.

**active_constraint:** `handleGlobalKey` in `onMount` handles only `Cmd+K`; no shortcut for copy or share. F6/F7/F8 tests do not exist. Impact: Medium. Probability: High. Time sensitivity: Medium. Expected value: Medium-High.

**validation_targets:** `npm test -- keyboard-navigation` targeting F6/F7/F8.

**evidence:**
- red | 2026-02-18T19:35:00Z | exit 1 | `cd web && npx vitest run src/routes/keyboard-navigation.test.ts`
  - helper:diff-snapshot=0 files changed
  - F6/F7/F8 tests absent; suite exits 1 | inline
- green | 2026-02-18T19:50:00Z | exit 0 | `cd web && npx vitest run src/routes/keyboard-navigation.test.ts`
  - helper:diff-snapshot=1 file changed, 36 insertions(+), 4 deletions(-)
  - F6/F7/F8 pass: Cmd+Shift+C/P/U fire correct handlers | inline
- removal | 2026-02-18T19:51:00Z | exit 1 | `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/keyboard-navigation.test.ts && cd web && npx vitest run src/routes/keyboard-navigation.test.ts`
  - helper:diff-snapshot=0 files changed
  - F6/F7/F8 fail again | inline

**rollback_plan:** `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/keyboard-navigation.test.ts` then replay red.

**delta_summary:** Extended `handleGlobalKey` with Cmd+Shift+C → `copyCommand()`, Cmd+Shift+P → `copyPrompt()`, Cmd+Shift+U → `sharePrompt()`. Updated Clear button `title` to include full shortcut reference. Added F6/F7/F8 test cases. Commit: loop-3 green.

**loops_remaining_forecast:** 0. All T1/T2/T3 behaviours landed green. ADR-0139 eligible for completion.

**residual_constraints:**
- Shortcut conflict risk (Cmd+Shift+C = Chrome devtools element picker): Low severity; users running the SPA in a browser with devtools open may see conflict. Mitigation: documented in ADR consequences; no code change needed. Monitoring: manual check on Chrome. Reopen condition: user reports shortcut swallowed.
- Persona panel Tab-exhaustion auto-advance: deferred (Low severity). Monitoring: manual test.

**next_work:**
- ADR-0139 complete. No open T-behaviours. Update ADR status to Accepted.
