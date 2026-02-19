# ADR-0140: Keyboard Focus Model Fixes and Shortcut Legend

## Status

Accepted

## Context

ADR-0139 delivered ARIA tablist semantics (T1), Tab-exhaustion auto-advance (T2), and action
shortcuts Cmd+Shift+C/P/U (T3). Post-implementation browser testing exposed six structural gaps
in the Tab-order that make keyboard-only navigation impractical:

| Gap | Symptom |
|---|---|
| G1 | Tab from active tab button goes to LOAD COMMAND, skipping the chip panel |
| G2 | Tab from filter input exits the panel to LOAD COMMAND instead of staying inside |
| G3 | `role="listbox"` container has no `tabindex="0"` — no Tab foothold in panels with ≤8 tokens |
| G4 | Tab from a chip mid-panel jumps to LOAD COMMAND (only last-chip Tab-exhaustion works) |
| G5 | Shift+Tab from first chip of first axis (task) misses the tab-bar, hits filter or Usage Patterns |
| G6 | Persona panel uses natural Tab through N preset buttons + 3 selects — slow and inconsistent |

**Root cause:** G3 is the primary driver. Because the listbox container has no `tabindex="0"`, it is
not a Tab stop. LOAD COMMAND/Usage Patterns intercept Tab before the panel because the panel
offers no Tab foothold. G1, G2, G4, and G5 are all downstream symptoms of the missing container
tabindex combined with out-of-order DOM placement.

Additionally, the keyboard shortcut inventory (Cmd+K, Cmd+Shift+C/P/U) is not visible on the
page — it only appears as a tooltip on the Clear button, which is not discoverable.

---

## Decision

Implement fixes in three sequential tasks.

### K1 — Fix Listbox Tab Foothold and Panel Tab Containment

**`TokenSelector.svelte`:**

- Add `tabindex="0"` to the `role="listbox"` container div.
- Add an `onfocus` handler on the listbox: when the container itself receives focus (i.e., Tab
  landed on the container rather than a chip), move focus to the roving-tabindex chip:
  `focusChip(focusedIndex === -1 ? 0 : focusedIndex)`.
- In `handleGridKey`, intercept Tab when `focusedIndex` is **not** at the last chip:
  redirect focus back to the listbox container (i.e., call `gridRef?.focus()`) so Tab stays
  inside the panel. Only the last-chip Tab (already wired as `onTabNext`) exits forward.
- Intercept Shift+Tab on the listbox container (`onfocus` guard: fired from container focus
  directly) when at the first chip: call `onTabPrev()` to retreat. When at a non-first chip,
  redirect Shift+Tab back to the filter input (if present) or to the listbox container.

**`+page.svelte`:**

- Add a `focusActiveTab()` helper: `document.querySelector<HTMLElement>('[role="tab"][aria-selected="true"]')?.focus()`.
- Pass `onTabPrev={focusActiveTab}` to the task `TokenSelector` (was `undefined`). This makes
  Shift+Tab from the first chip of the first axis return to the tab-bar correctly.

This collapses each chip panel to **two Tab stops**: filter input (optional, on axes with >8
tokens) + listbox container. All chip navigation stays on Arrow keys.

### K2 — Fix DOM Order for LOAD COMMAND / Usage Patterns

Move the `load-cmd-section` and `PatternsLibrary` below the active axis panel in the DOM. This
ensures Tab from the tablist reaches the panel before utility controls, matching the visual
reading order (tab-bar → axis panel → utilities → preview). No CSS changes needed — the panel
already appears above load/patterns visually on desktop.

> **Note:** If reordering breaks the visual layout, suppress Tab on utility buttons while a chip
> panel is active using `tabindex={panelHasFocus ? -1 : 0}` instead.

### K3 — Keyboard Shortcut Legend

Add a `<details>` disclosure element (closed by default) below the tab-bar, above the axis
panel. Title: **"Keyboard shortcuts ▸"**. When opened, shows a compact two-column table:

| Keys | Action |
|---|---|
| `←` `→` on tab-bar | Switch axis |
| `↑` `↓` `Home` `End` on tab-bar | Switch axis |
| Arrow keys in panel | Navigate chips |
| `Enter` / `Space` | Select focused chip |
| `Tab` from last chip | Advance to next axis |
| `Shift+Tab` from first chip | Retreat to previous axis |
| `⌘K` / `Ctrl+K` | Clear all |
| `⌘⇧C` / `Ctrl+Shift+C` | Copy command |
| `⌘⇧P` / `Ctrl+Shift+P` | Copy rendered prompt |
| `⌘⇧U` / `Ctrl+Shift+U` | Share URL |

The `<details>` element is keyboard-accessible by default. No JavaScript required. On mobile the
section is hidden (CSS `@media (pointer: coarse)`).

Remove the `title` attribute shortcut inventory from the Clear button once the legend exists —
the tooltip is no longer the only disclosure.

---

## Salient Task IDs

- **K1** — Listbox Tab foothold and panel Tab containment
- **K2** — DOM order fix for LOAD COMMAND / Usage Patterns
- **K3** — Keyboard shortcut legend

---

## Alternatives Considered

**Alt A — `tabindex="-1"` on utility buttons dynamically:**
Conditionally suppress LOAD COMMAND/Usage Patterns from Tab order when a panel is focused.
Rejected as primary fix — fragile focus-tracking state; DOM reorder (K2) is simpler and more
robust. Retained as fallback if K2 breaks layout.

**Alt B — Skip-link "Jump to tokens":**
A visually hidden skip link above the tab-bar that focuses the chip panel. Avoids DOM reorder.
Deferred — skip links require knowing which panel is active, and this is equivalent complexity
to K2. Can be added as an accessibility enhancement layer after K1+K2.

**Alt C — Persona roving tabindex (G6):**
Extract persona chips into a `role="listbox"` component with Arrow-key navigation, matching
TokenSelector. Deferred out of this ADR — G6 is a consistency gap but not a blocking usability
issue; persona has few presets and they are all visible without scrolling. File as follow-on.

---

## Consequences

### Positive

- Tab from the tab-bar now reaches the chip panel directly (no interception by utility controls).
- Each axis panel is a clean two-Tab-stop region: filter (if present) + listbox.
- Shift+Tab from the first axis returns to the tab-bar reliably.
- The shortcut legend makes the full keyboard inventory discoverable without a tooltip.
- Mobile is unaffected (legend hidden on touch devices; Tab order irrelevant for touch).

### Negative / Risks

- Moving `load-cmd-section` and `PatternsLibrary` in the DOM may affect visual order on narrow
  viewports — test on mobile after K2.
- Adding `tabindex="0"` to the listbox container means it gains a visible focus ring; ensure
  the existing `.token-chip:focus-visible` ring is not confused with the container ring.
- `onfocus` on the listbox container fires on every focus event including chip-to-chip Arrow
  navigation; the redirect must guard against re-entry (check `event.target === gridRef`).

### Neutral

- Action shortcuts (Cmd+Shift+C/P/U) and Cmd+K unchanged.
- ARIA tablist semantics from ADR-0139 unchanged.
- Mobile layout and touch interactions unchanged.

---

## Validation Contract

| ID | Falsifiable | Validation command |
|---|---|---|
| F1k | Tab from active tab button reaches the listbox (not LOAD COMMAND) | `npm test -- keyboard-focus` |
| F2k | Tab from filter input stays in panel (focuses listbox), does not exit to LOAD COMMAND | `npm test -- keyboard-focus` |
| F3k | Tab mid-panel (non-last chip) wraps to listbox container, not LOAD COMMAND | `npm test -- keyboard-focus` |
| F4k | Shift+Tab from first chip of task panel focuses the active tab button | `npm test -- keyboard-focus` |
| F5k | Shortcut legend `<details>` is present and contains the 10-row table | `npm test -- keyboard-focus` |

---

## Evidence Root

`docs/adr/evidence/0140/`

## VCS Revert

`git restore --source=HEAD web/src/lib/TokenSelector.svelte web/src/routes/+page.svelte`
