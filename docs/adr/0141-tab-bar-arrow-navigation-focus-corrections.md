# ADR-0141: Tab-Bar Arrow Navigation and Focus Model Corrections

## Status

Accepted

## Context

A Chrome DevTools MCP audit of keyboard navigation in the Bar Prompt Builder SPA
(conducted 2026-02-19) identified three bugs introduced by ADR-0140 and ADR-0139:

| Bug | Symptom | Root cause |
|---|---|---|
| B1 | ArrowRight/ArrowLeft on the tab-bar moves focus to the first chip, not the next tab button | `handleTabBarKey` calls `setTimeout(focusFirstChip)` — encoded by F1b/F2b tests that specified wrong behavior |
| B2 | Persona panel focus is lost to `<body>` when Tab-exhaustion wraps from directional → persona | `goToNextTab` calls `setTimeout(focusFirstChip)`; persona has no `[role="option"]` elements, so `focusFirstChip` silently does nothing |
| B3 | Shortcut legend `<summary>` adds an unexpected Tab stop between the active tab button and the filter/first chip | `<details class="shortcut-legend">` is positioned in DOM between the tab-bar and the axis panels |

**B1 is the user-reported issue.** After pressing ArrowRight to advance the tab, focus escapes to the chip grid. The next ArrowRight navigates chips instead of tabs, making tab-bar keyboard navigation unusable.

**ARIA tabs pattern (WAI-ARIA APG):** ArrowLeft/Right navigate between tab buttons; focus stays on the tab strip. Tab from the active tab button enters the tabpanel. The F1b/F2b tests in `keyboard-navigation.test.ts` encoded the wrong behavior (chip focus on ArrowKey) and must be corrected.

---

## Decision

### K1 — Correct ArrowKey focus: stay on tab strip

**`+page.svelte` `handleTabBarKey`:**
- Replace `setTimeout(focusFirstChip, 0)` with `setTimeout(focusActiveTab, 0)` in all ArrowKey branches.
  Focus stays on the tab strip after switching axes.

**`keyboard-navigation.test.ts`:**
- Remove (delete) F1b and F2b — they specify the wrong behavior.
- Add F1c and F2c: ArrowRight/ArrowLeft must leave `document.activeElement` on the active tab button
  (not on a chip).

### K2 — Fix persona panel focus loss on Tab-exhaustion wrap

**`+page.svelte` `focusFirstChip`:**
- After `document.querySelector('[role="option"]')` returns null, fall back to
  `document.querySelector<HTMLElement>('.selector-panel button, .selector-panel select, .selector-panel input')`.
- This ensures Tab-exhaustion from directional → persona focuses the first persona-chip button
  rather than losing focus to `<body>`.

**`keyboard-navigation.test.ts`:**
- Add F3c: Tab from last directional chip must not leave `document.activeElement` on `<body>`.
  It must focus the first interactive element in the newly-active persona panel.

### K3 — Move shortcut legend out of primary Tab flow

**`+page.svelte`:**
- Move `<details class="shortcut-legend">` from its current position (between tab-bar and axis panels)
  to after the `<PatternsLibrary>` component at the bottom of `.selector-panel`.
- This removes the unexpected Tab stop from the path: tab button → filter → chips.
  The legend remains keyboard-reachable via Tab after the axis/load/patterns controls.

**`keyboard-focus.test.ts` F5k:**
- The test only checks `.shortcut-legend` exists with 10+ rows — position is irrelevant.
  No test change required for K3.

---

## Salient Task IDs

- **K1** — Correct ArrowKey focus behavior (tab strip stays focused)
- **K2** — Fix persona panel focus loss
- **K3** — Move shortcut legend below axis panel

---

## Alternatives Considered

**Alt A — Remove `focusFirstChip` calls entirely from ArrowKey:**
Only change `activeTab`; let users Tab into the panel manually. Simpler, but loses the
ability to Tab-exhaust into a panel from outside. Rejected — Tab-exhaustion (from last chip)
into the next axis is good behavior and should be retained. The issue is only ArrowKey.

**Alt B — `tabindex="-1"` on the shortcut legend summary:**
Makes the legend keyboard-inaccessible. Rejected — users who navigate to the legend by Tab
need to be able to open it.

**Alt C — Move shortcut legend to the right/preview panel:**
The right panel is conditionally hidden on mobile. Rejected — the legend is hidden on touch
already; keeping it in the selector panel keeps it visible on desktop without coupling to
preview visibility.

---

## Consequences

### Positive
- ArrowRight/Left on the tab-bar keeps focus on the tab strip — standard ARIA tabs behavior.
- Persona panel is reachable via Tab-exhaustion without focus loss.
- Tab from active tab button lands on filter or first chip without an extra shortcut-legend stop.

### Negative / Risks
- F1b/F2b deletion removes coverage for the (wrong) chip-focus behavior. F1c/F2c replace it.
- Moving the shortcut legend to the bottom changes its visual position on desktop; acceptable
  since it is collapsed by default and is a secondary disclosure element.

### Neutral
- Mid-panel Tab redirecting to last chip (K1 F3k) is retained as-is; the audit confirmed
  it works correctly and the behavior is intentional per ADR-0140.
- All ADR-0139/0140 F-tests remain green except F1b/F2b (deleted and replaced).

---

## Validation Contract

| ID | Falsifiable | Validation command |
|---|---|---|
| F1c | ArrowRight on tab-bar leaves focus on the newly-active tab button (not a chip) | `npm test -- keyboard-navigation` |
| F2c | ArrowLeft on tab-bar leaves focus on the newly-active tab button (not a chip) | `npm test -- keyboard-navigation` |
| F3c | Tab-exhaustion from directional panel does not leave focus on `<body>` | `npm test -- keyboard-navigation` |
| F5k | `.shortcut-legend` details element present with 10+ rows (position irrelevant) | `npm test -- keyboard-focus` |

---

## Evidence Root

`docs/adr/evidence/0141/`

## VCS Revert

`git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/keyboard-navigation.test.ts`
