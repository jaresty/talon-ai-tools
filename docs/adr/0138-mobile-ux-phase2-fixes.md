# ADR-0138: Mobile UX Phase 2 — Action Access, Prompt Visibility, Guidance Drawer

## Status

Accepted

## Context

ADR-0137 delivered the first phase of mobile UX improvements: tabbed axis navigation, preview toggle, expanded textareas, stacked persona selects, and a floating action button (FAB). Post-deployment review at https://jaresty.github.io/talon-ai-tools/ revealed a second tier of issues that survived phase 1 or were introduced by it.

### Remaining Problems

1. **FAB trapped in preview panel** — The FAB (`⋯`) is a child of `.preview-panel`. When the preview panel is hidden, the FAB disappears with it — all actions (Copy cmd, Copy prompt, Share, Clear) become inaccessible. On long token lists, the action-row also expands *inline* inside `.command-box`, which may be 1000 px+ below the viewport when the FAB is tapped, giving the user no visible feedback.

2. **Rendered prompt never shown** — The app shows only the bar command string (e.g. `bar build show mean full`), never the full rendered prompt text. The `renderPrompt()` function exists but its output is never displayed inline. The "Show Preview" / "Hide Preview" toggle label is confusing because "preview" has no clear referent — users don't know whether it previews the command, the prompt, or something else.

3. **`showPreview` default bug** — `showPreview` is initialised to `true` in Svelte state, so the `.visible` class is always present on page load, overriding the mobile `display: none` CSS rule. The preview panel is always visible on mobile regardless of the toggle, making the button inert on first load.

4. **Token guidance off-screen on mobile** — Tapping a token chip reveals the meta-panel (use_when, description, guidance) *inline*, below the token grid. On mobile the user must scroll down past the grid to see it, losing sight of the chip they tapped and the surrounding context.

5. **Touch targets below 44 px** — Tab buttons (~28 px), persona chips (~16 px), selected chips in preview (~16 px), and the Load Command toggle div (~28 px, also not a `<button>` element) all fall below the recommended 44 px minimum for touch interfaces.

6. **iOS auto-zoom on textarea focus** — `.input-area` and `.load-cmd-input` have `font-size` of ~13 px. iOS Safari auto-zooms the viewport when any input with font-size < 16 px receives focus, then fails to zoom back out, leaving the user in a misaligned zoomed state.

7. **PWA icon black box on iPhone** — The home-screen icon renders as a solid black square on iOS. iOS ignores the Web App Manifest for home-screen icons and uses `apple-touch-icon` link tags exclusively; no such tag exists in `app.html`. Additionally the icon PNG must have a non-transparent background (iOS renders transparency as black).

## Decision

We will implement the following fixes in 7 sequential loops:

### Loop 1 — Fix `showPreview` default bug

Change `let showPreview = $state(true)` → `$state(false)` in `+page.svelte`. Verify the preview panel is correctly hidden on mobile page load and correctly toggled by the button.

### Loop 2 — Relocate FAB and action overlay to layout root

Move `.fab-btn` and `.action-row` out of `.preview-panel` and make them direct children of `.layout`. The action-row becomes a `position: fixed` overlay anchored to the bottom of the viewport (above the FAB), always reachable regardless of preview panel state. Tapping outside the overlay or pressing ✕ closes it.

### Loop 3 — Show rendered prompt inline; rename panel to "Output"

Add a `<pre class="prompt-preview">` inside the output panel that displays `renderPrompt(grammar, selected, subject, addendum, persona)` reactively, labelled "Rendered Prompt". Rename the toggle button from "Show Preview" / "Hide Preview" to "Show Output" / "Hide Output". Rename the panel class from `preview-panel` to `output-panel` (or add a label change without class rename to minimise diff).

### Loop 4 — Token guidance bottom drawer on mobile

On mobile (`max-width: 767px`), when `activeToken` is set in TokenSelector, render the `.meta-panel` content in a `position: fixed; bottom: 0` drawer that slides up over the token grid rather than appearing inline below it. The chip and grid remain visible above the drawer. A close button or tap-outside dismisses the drawer. On desktop, behaviour is unchanged (inline meta-panel).

### Loop 5 — Touch targets

In `@media (max-width: 767px)`:
- Add `min-height: 44px` to `.tab` buttons
- Add `min-height: 44px; padding: 0.5rem 0.75rem` to `.persona-chip`
- Add `min-height: 44px; padding: 0.5rem 0.75rem` to `.selected-chip`
- Convert `.load-cmd-toggle` from `<div>` to `<button>` and add `min-height: 44px`

### Loop 6 — iOS auto-zoom fix

In `@media (max-width: 767px)`, set `font-size: 1rem` on `.input-area` and `.load-cmd-input` to prevent iOS Safari from auto-zooming on focus.

### Loop 7 — PWA icon fix

In `web/src/app.html`, add `<link rel="apple-touch-icon" href="/talon-ai-tools/apple-touch-icon.png">`. Ensure the referenced PNG (180×180 px) exists in `web/static/` with a solid non-transparent background. Update `manifest.json` if the icon entry is missing or points to a transparent image.

## Alternatives Considered

1. **Bottom sheet for actions** (ADR intent from 0137) — A full slide-up bottom sheet with animation would be higher fidelity but requires more state management and CSS transition work. The fixed-overlay approach in Loop 2 is simpler and solves the same task-blocking failure mode; the sheet can be upgraded later.

2. **Prompt display as primary mobile view** — Making the rendered prompt the default visible output (with command secondary) would reframe the UX more fundamentally. Deferred: Loop 3's additive approach (prompt shown below the command) is lower risk for a phase 2 fix.

3. **Separate mobile build** — Rejected: defeats the PWA/single-codebase goal.

## Consequences

### Positive

- FAB and actions are always reachable regardless of output panel state (eliminates task-blocking failure)
- Users can verify prompt content without leaving the app or running bar locally
- Token guidance visible without losing grid context
- iOS users get a stable, unzoomed viewport experience
- Home screen icon renders correctly on iPhone

### Negative

- Fixed overlay for actions adds z-index management; must not conflict with guidance drawer (both fixed)
- Prompt display increases page weight on mobile; should be collapsible or truncated if very long
- Converting `.load-cmd-toggle` div to a button may require minor style adjustments

### Technical Debt

- The `preview-panel` naming persists if only the label changes in Loop 3; a full rename is a larger refactor deferred to phase 3
- The guidance drawer in Loop 4 adds a new fixed-position layer; a shared bottom-drawer component would clean this up later

## Implementation Notes

- Use `@media (max-width: 767px)` for all mobile breakpoints
- Fixed overlays: use `z-index: 150` for action overlay, `z-index: 200` for guidance drawer (above action overlay)
- `renderPrompt` is already imported in `+page.svelte`; Loop 3 only adds a reactive display expression
- PWA icon: 180×180 px PNG with solid `#1a1a1a` background (matching `--color-bg`) and the existing bar icon centred

## Evidence Root

`docs/adr/evidence/0138/`

## VCS Revert

`git restore --source=HEAD`
