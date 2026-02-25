# ADR-0145: Desktop Horizontal Scroll Tab Navigation

## Status

Accepted

## Context

The Bar Prompt Builder SPA supports swipe-left/swipe-right gesture navigation between axis tabs
on mobile. On desktop, tabs are reachable only by clicking the tab strip or using
ArrowLeft/ArrowRight keyboard navigation (established by ADR-0141).

Trackpad users on desktop have a natural horizontal scroll gesture available (two-finger
horizontal swipe on macOS/Windows Precision Touchpad). Bringing the same "swipe to navigate
tabs" idiom to desktop would:

- reduce pointer travel to the tab bar for trackpad-primary users
- create gesture parity between mobile and desktop interaction models
- complement the keyboard shortcuts already documented in ADR-0140/0141

### Conflict surface

Desktop horizontal scroll introduces a gesture conflict that does not exist on mobile:
the SPA's tab content may itself contain horizontally scrollable elements (wide tables, code
blocks, token catalogs). A naive global handler would consume scroll events intended for
content, not navigation. The chosen variant must resolve this conflict cleanly.

### Input diversity

Desktop input devices are heterogeneous. Trackpad users (macOS, Precision Touchpad on
Windows/Linux) generate smooth `WheelEvent` streams with `deltaX`/`deltaY` populated.
Standard USB mice with no horizontal tilt wheel cannot produce horizontal scroll at all.
The feature must degrade gracefully for mouse-only users without surfacing confusion.

---

## Decision

### Chosen variant: threshold-gated dominant-axis detection (Variant B)

A `wheel` event listener on the SPA root container fires tab navigation only when all of
the following conditions are simultaneously true:

1. **Horizontal dominance** — `|deltaX| > |deltaY| * 1.5` (the gesture is more horizontal
   than vertical; diagonal scrolling is excluded)
2. **Minimum displacement** — `|deltaX| > 40px` (single-frame micro-movements do not trigger)
3. **Cooldown clear** — at least 400 ms has elapsed since the last tab change from this
   handler (momentum scrolling cannot skip multiple tabs per swipe)

When all three conditions pass, the handler calls the same `setActiveTab()` function used by
tab-bar click and keyboard navigation — no parallel code path.

### G1 — WheelEvent listener placement

- Attach the listener to the `.spa-root` container element (the outermost SPA wrapper),
  not to `window` or `document`.
- Use `{ passive: true }` to avoid blocking the browser's native scroll thread.
- Do **not** call `preventDefault()` — the gesture navigates but does not consume the scroll
  event, which allows browser-level back/forward swipe gestures at the viewport edge to
  continue to work.

### G2 — Content-area scroll boundary

Any tab panel that contains a horizontally scrollable element must wrap that element with a
container that attaches a `wheel` handler calling `event.stopPropagation()` when
`|deltaX| > |deltaY|`. This prevents horizontal scroll within content from propagating to
the root navigation listener.

Initial audit of tab panels: the token catalog table in the `method` axis panel is the
primary candidate. Subsequent panels must be audited before shipping.

### G3 — Post-navigation cooldown

After a tab change triggered by this handler, set a `lastScrollNav` timestamp. Ignore
further `wheel` events for 400 ms. This prevents trackpad momentum from advancing two or
more tabs on a single physical swipe.

### G4 — Animation consistency

- When `prefers-reduced-motion: no-preference`: apply the same slide-transition animation
  used for mobile swipe (direction determined by swipe direction: left swipe → advance tab,
  right swipe → previous tab).
- When `prefers-reduced-motion: reduce`: apply instant tab switch (no animation). Do not
  disable the gesture itself.

### G5 — Code path unification

Gesture-triggered navigation must go through `setActiveTab()` / the existing tab-change
event bus, identical to click and keyboard navigation. This ensures:

- Unsaved-state guards fire
- URL hash/query-param updates occur
- Analytics events are emitted
- Any future tab-change middleware applies automatically

### G6 — User opt-out

Add a `gestures.horizontalScrollNav` boolean key to the SPA's `localStorage` settings store,
defaulting to `true`. When `false`, the wheel listener is a no-op for navigation purposes.
Expose the toggle in the Settings panel (or equivalent preferences surface).

### G7 — Discoverability

On first load (or when the user has not yet triggered scroll navigation), display a one-time
tooltip or subtle hint near the tab bar: "Swipe horizontally to switch axes". Dismiss on
first gesture trigger or after 5 seconds. Do not show on devices that cannot produce
horizontal scroll events (detect via pointer media query: `pointer: fine` without
`hover: none`).

---

## Salient Task IDs

- **G1** — WheelEvent listener on `.spa-root`, passive, no preventDefault
- **G2** — stopPropagation boundary on horizontally scrollable content containers
- **G3** — 400 ms post-navigation cooldown
- **G4** — Animation: slide normally, instant under prefers-reduced-motion
- **G5** — Route through `setActiveTab()` — no parallel path
- **G6** — localStorage opt-out toggle
- **G7** — One-time discoverability hint

---

## Alternatives Considered

**Variant A — Pure horizontal scroll hijack**
Consume all horizontal scroll globally; no content area can scroll horizontally.
Rejected — the token catalog and any future wide-table content would become unreachable
via trackpad, requiring a horizontal scrollbar fallback that degrades the layout.

**Variant C — Modifier-gated navigation (Shift+scroll or Alt+scroll)**
Horizontal scroll only navigates when a modifier key is held.
Rejected — requires users to learn and remember the modifier; the gesture is no longer
natural or discoverable. Adds keyboard-gesture coupling that conflicts with system-level
Shift+scroll behaviors on some platforms.

**Variant D — Tab bar scroll region only**
Only horizontal scroll events originating from the tab bar strip trigger navigation.
Rejected — the tab bar is narrow (typically 40–48 px tall); the target area is too small
for reliable triggering, and users would need to aim at the tab bar rather than swipe freely.

**Variant E — Visual drag scrubber on tab bar**
Click-and-drag on the tab bar scrubs between tabs.
Rejected — drag conflicts with existing click-to-select behavior on individual tab buttons
and is not analogous to the mobile swipe idiom.

---

## Consequences

### Positive

- Trackpad users gain muscle-memory parity with mobile: the same physical gesture works on
  both surfaces.
- No new keyboard shortcut to memorize — the gesture is additive alongside existing ArrowKey
  navigation.
- Routing through `setActiveTab()` ensures all tab-change side effects (guards, URL, analytics)
  fire without duplication.

### Negative / Risks

- Content panels with horizontal scroll require an explicit `stopPropagation` boundary.
  Missing a panel creates a silent regression where scroll inside content accidentally
  navigates tabs.
- `{ passive: true }` means the handler cannot call `preventDefault()`. If a future
  requirement needs to suppress the scroll-position change on navigation, the listener
  must be re-registered as active (with the associated jank risk).
- Mouse-only users receive no benefit and no feedback; G7's hint must be gated on input
  device detection to avoid showing irrelevant UI.

### Neutral

- The 400 ms cooldown is a tunable constant. Optimal value may vary by platform; expose it
  as an internal config constant (not a user-facing setting) for easy adjustment.
- Keyboard navigation (ADR-0141 ArrowKey behavior) is entirely unaffected.

---

## Validation Contract

| ID | Falsifiable | Validation command |
|---|---|---|
| F1g | A dominant horizontal WheelEvent (deltaX=50, deltaY=10) on `.spa-root` advances the active tab | `npm test -- scroll-navigation` |
| F2g | A diagonal WheelEvent (deltaX=30, deltaY=30) does not change the active tab | `npm test -- scroll-navigation` |
| F3g | A second WheelEvent within 400 ms of a tab change does not advance a second tab | `npm test -- scroll-navigation` |
| F4g | A horizontal WheelEvent whose target is inside a `.h-scroll-boundary` element does not change the active tab | `npm test -- scroll-navigation` |
| F5g | With `prefers-reduced-motion: reduce`, a qualifying WheelEvent switches tabs without triggering a CSS transition | `npm test -- scroll-navigation` |
| F6g | With `gestures.horizontalScrollNav = false` in localStorage, a qualifying WheelEvent does not change the active tab | `npm test -- scroll-navigation` |
| F7g | A qualifying WheelEvent calls `setActiveTab()` exactly once (same path as click/keyboard) | `npm test -- scroll-navigation` |

---

## Evidence Root

`docs/adr/evidence/0145/`

## VCS Revert

`git restore --source=HEAD web/src/routes/+page.svelte web/src/lib/settings.ts web/src/lib/scrollNav.ts`
