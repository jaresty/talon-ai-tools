# ADR-0139: SPA Tab Keyboard Navigation and Action Shortcuts

## Status

Proposed

## Context

ADR-0137 introduced a tab-based layout to the Bar Prompt Builder SPA so that one axis
panel is visible at a time, making the interface usable on narrow mobile viewports.
ADR-0135 addressed in-panel chip navigation (ARIA listbox, roving tabindex, ArrowKey
navigation within an axis panel, filter→chip ArrowDown handoff).

What remains unaddressed is the **inter-axis keyboard model** — the mechanism for
moving between axis tabs — and the **action shortcut layer** for common output operations.

### Gaps after ADR-0137 / ADR-0135

| Gap | Root cause | Severity |
|---|---|---|
| Tab key cannot traverse across axes | Only one panel rendered; Tab exits to Subject textarea | High |
| Tab buttons are click-only | No `onkeydown`, no arrow-key model on the nav | High |
| No ARIA tablist semantics | `<nav>` holds plain buttons; no `role="tablist/tab"`, no `aria-selected` | High |
| No focus management on tab switch | After mouse-click tab switch, focus is not moved into the new panel | Medium |
| Common actions have no shortcuts | Copy cmd, Copy prompt, Share each require mouse; only Clear has `Cmd+K` | Medium |

The two high-severity gaps mean a desktop keyboard-only user cannot configure tokens
across more than one axis without reaching for the mouse.

### Relationship to existing ADRs

- **ADR-0135** delivered `role="listbox"` + roving tabindex inside each axis panel.
  That work is the foundation; this ADR adds the inter-panel layer above it.
- **ADR-0137 / ADR-0138** established the tab-based layout and mobile UX fixes.
  This ADR must not regress those behaviours.

---

## Decision

Implement three behaviour groups in three sequential loops.

### T1 — ARIA Tablist on the Tab-Bar Nav

Upgrade `<nav class="tab-bar">` to a compliant ARIA tab interface:

- `role="tablist"` on the `<nav>` element.
- Each tab `<button>` receives `role="tab"`, `aria-selected={activeTab === tab}`,
  `aria-controls="panel-{tab}"`, and managed `tabindex` (active tab = 0, others = -1).
- Each axis panel container (`{#if activeTab === axis}` or persona section) receives
  `role="tabpanel"`, `id="panel-{tab}"`, `aria-labelledby="tab-{tab}"`, and
  `tabindex="0"` (so the panel itself is reachable when no chip is focused).
- Add `onkeydown` to the tablist: ArrowRight/ArrowDown → next tab (cycle);
  ArrowLeft/ArrowUp → previous tab (cycle); Home → first tab; End → last tab.
- On keyboard-driven tab activation: `requestAnimationFrame(() => firstFocusable?.focus())`
  where `firstFocusable` is the first `[role="option"]` chip in the new panel, or the
  panel element itself if no chips exist.

### T2 — Auto-Advance on Tab-Exhaustion

Extend `TokenSelector.svelte`'s `handleGridKey` to intercept the Tab key:

- When Tab is pressed while focus is on the **last** `[role="option"]` chip
  (`focusedIndex === filtered.length - 1`), emit an `onTabNext` callback to the parent
  (`+page.svelte`) which advances `activeTab` to the next axis and moves focus to the
  first chip of the new panel.
- When Shift+Tab is pressed while focus is on the **first** chip (`focusedIndex === 0`),
  emit an `onTabPrev` callback which retreats `activeTab` to the previous axis and moves
  focus to the last chip of the previous panel.
- On the last axis: Tab falls through to Subject textarea normally.
- On the first axis: Shift+Tab falls through to the tab-bar naturally.

`TokenSelector` gains two optional props: `onTabNext?: () => void` and
`onTabPrev?: () => void`. The page wires them to axis-advance logic.

### T3 — Keyboard Shortcuts for Common Actions

Add shortcuts to the existing `handleGlobalKey` listener in `onMount`:

| Shortcut | Action | Notes |
|---|---|---|
| `Cmd+Shift+C` / `Ctrl+Shift+C` | Copy command string | `copyCommand()` |
| `Cmd+Shift+P` / `Ctrl+Shift+P` | Copy rendered prompt | `copyPrompt()` |
| `Cmd+Shift+U` / `Ctrl+Shift+U` | Share URL (copy link) | `sharePrompt()` |
| `Cmd+K` / `Ctrl+K` | Clear all (existing) | unchanged |

All shortcuts call `e.preventDefault()`. The `title` attribute on the Clear button is
updated to reflect the full shortcut inventory.

---

## Salient Task IDs

- **T1** — ARIA tablist on tab-bar nav
- **T2** — Auto-advance Tab-exhaustion across axis panels
- **T3** — Action keyboard shortcuts

---

## Alternatives Considered

**Variant C — Keyboard Shortcut Layer Only (Alt+1–8):**
Adds `Alt+N` shortcuts to jump directly to each axis tab. Low complexity but shortcuts
are undiscoverable, conflict-prone with OS/browser bindings, and do not restore linear
Tab traversal. Retained as a supplemental affordance if T1+T2 prove insufficient.

**Variant D — Responsive Desktop Expansion:**
On wide viewports, remove tab gating and render all panels simultaneously (reverting
pre-mobile layout). Fully restores original desktop UX. Deferred: requires multi-column
layout design and dual-layout maintenance. Remains viable if T1+T2 prove insufficient.

---

## Consequences

### Positive

- Desktop keyboard-only users can build a full bar command across all 8 axes without a mouse.
- ARIA tablist semantics make the tab interface navigable by screen readers.
- Mobile layout and touch interactions are unaffected.
- Action shortcuts (Cmd+Shift+C/P/U) remove three required mouse interactions for power
  users who work keyboard-first.

### Negative / Risks

- Tab-exhaustion intercept fights the browser's natural focus model. Incorrect scoping of
  the focusable-element query could swallow Tab events unexpectedly.
- `onTabNext` / `onTabPrev` callbacks introduce API surface on `TokenSelector`; must be
  optional to avoid breaking the persona panel (which is not a TokenSelector).
- Action shortcuts must not conflict with browser defaults: Cmd+Shift+C (Chrome devtools
  element picker), Cmd+Shift+P (Chrome command palette). Risk is low for power users who
  understand the app context; note in implementation.

### Neutral

- `Cmd+K` clear shortcut is unchanged.
- No changes to grammar, rendering, or CLI pipeline.

---

## Validation Contract

| ID | Falsifiable | Validation command |
|---|---|---|
| F1 | ArrowRight on tablist moves `activeTab` to next axis | `npm test -- keyboard-navigation` |
| F2 | ArrowLeft on tablist moves `activeTab` to previous axis (cycling) | `npm test -- keyboard-navigation` |
| F3 | Tab-bar buttons have `role="tab"`, `aria-selected`, `aria-controls` | `npm test -- keyboard-navigation` |
| F4 | Tab from last chip in an axis auto-advances to next axis | `npm test -- keyboard-navigation` |
| F5 | Shift+Tab from first chip retreats to previous axis last chip | `npm test -- keyboard-navigation` |
| F6 | `Cmd+Shift+C` fires `copyCommand()` | `npm test -- keyboard-navigation` |
| F7 | `Cmd+Shift+P` fires `copyPrompt()` | `npm test -- keyboard-navigation` |
| F8 | `Cmd+Shift+U` fires `sharePrompt()` | `npm test -- keyboard-navigation` |

---

## Evidence Root

`docs/adr/evidence/0139/`

## VCS Revert

`git restore --source=HEAD web/src/routes/+page.svelte web/src/lib/TokenSelector.svelte web/src/routes/keyboard-navigation.test.ts`
