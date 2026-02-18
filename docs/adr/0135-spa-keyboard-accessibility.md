# ADR-0135: SPA Token Selector Keyboard Accessibility

## Status

Accepted

## Context

The bar SPA (`web/`) token chip selector is entirely mouse-dependent. Token chips are
rendered as `<div>` elements with `onclick` handlers, placing them outside the tab order
and making them unreachable to keyboard-only users, screen-reader users, and power users
who prefer not to lift from the keyboard after typing a filter query.

### Gaps identified (probe act dig analysis)

Seven keyboard interaction gaps exist across the SPA:

| Gap | Element | Root cause | Severity |
|---|---|---|---|
| No tab focus on chips | `.token-chip` div | Missing `tabindex` | Critical |
| No keyboard activation | `.token-chip` div | Missing `onkeydown` (Enter/Space) | Critical |
| Filter → chip focus trap | filter `<input>` | No ArrowDown handler | High |
| No arrow-key navigation within axis | chip grid | No roving tabindex | High |
| D2 metadata panel unreachable | `.meta-panel` | No keyboard trigger path | Medium |
| Selected badge chips non-interactive | `selected-chip` span | Missing `tabindex`/`onkeydown` | Medium |
| No visible focus indicator | `.token-chip` | Missing `:focus-visible` CSS | Medium |

The two critical gaps mean a keyboard-only user cannot interact with the token grid
at all. The high-severity filter gap means that even after typing a filter query,
the user must reach for the mouse to select from the narrowed results.

### Approach evaluated

Three patterns were considered (show act full compare):

**A — tabindex=0 per chip:** Add `tabindex="0"` and `onkeydown` to every chip div.
Simplest code, but creates one tab stop per visible chip — potentially hundreds across
7 axis panels. Disqualified by tab-stop explosion.

**B — Roving tabindex (ARIA listbox):** Each axis panel is a single tab stop
(`role="listbox"`). Arrow keys navigate chips within the panel; only the active chip
holds `tabindex="0"`, all others hold `tabindex="-1"`. Enter/Space activate. ArrowDown
from the filter input transfers focus to the first chip. This is the ARIA-specified
pattern for listbox widgets.

**C — Filter-as-combobox:** The filter input is the sole control; ArrowDown opens a
popup listbox. Fits search-then-select workflows well but is architecturally mismatched
here: most axis panels have no filter input (token count ≤ 8), so combobox semantics
would apply inconsistently across panels.

---

## Decision

Implement **approach B (roving tabindex / ARIA listbox)** in `TokenSelector.svelte`,
with supporting fixes in `+page.svelte`.

### Changes to `TokenSelector.svelte`

**State additions:**
- `focusedIndex = $state(-1)` — index of the chip holding `tabindex="0"` within
  the current `filtered` array. Reset to `-1` when `filtered` changes length.
- `chipRefs = $state<(HTMLDivElement | null)[]>([])` — parallel DOM ref array for
  programmatic focus. Reset alongside `focusedIndex`.
- `filterInputRef = $state<HTMLInputElement | null>(null)` — ref for Escape-to-filter.

**Chip grid container (`role="listbox"`):**
- Add `role="listbox"`, `aria-label="{axis} tokens"`,
  `aria-multiselectable={maxSelect > 1}` to the `.token-grid` div.
- Add `onkeydown={handleGridKey}` to the grid container.
- `handleGridKey` handles: ArrowRight/ArrowDown (next chip, wrapping), ArrowLeft/ArrowUp
  (previous chip, wrapping), Home (first chip), End (last chip), Escape (return focus to
  filter input or blur).

**Individual chips (`role="option"`):**
- Add `role="option"`, `aria-selected={isSelected}`.
- `tabindex={focusedIndex === i ? 0 : -1}` — roving tabindex.
- `bind:this={chipRefs[i]}` — DOM ref for programmatic `.focus()`.
- `onkeydown`: Enter and Space call `handleChipClick(meta, atCap)`.
- `onfocus`: set `focusedIndex = i` and `activeToken = meta.token` — D2 metadata panel
  opens for the keyboard-focused chip without a separate click.

**Filter input:**
- Add `bind:this={filterInputRef}`.
- Add `onkeydown`: ArrowDown (with `preventDefault`) moves focus to `chipRefs[0]` and
  sets `focusedIndex = 0`. Tab is left unchanged (exits panel naturally).

**D2 metadata panel close button:**
- Change `<span class="meta-close">` to `<button class="meta-close">` — natively
  focusable; no extra `tabindex` needed.

**CSS:**
```css
.token-chip:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

/* Separate focus ring from active-meta outline to avoid visual doubling */
.token-chip.active-meta:not(:focus-visible) {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
}
```

### Changes to `+page.svelte`

**Selected-chip badges** (the `×` removal chips in the preview panel):
- Add `role="button"`, `tabindex="0"`, and `onkeydown` (Enter/Space → `toggle(axis, token)`)
  to each `selected-chip` span. These are few in number so individual tab stops are
  appropriate.

### Keyboard interaction contract (post-implementation)

| Gesture | Location | Result |
|---|---|---|
| Tab | Anywhere | Moves to next axis panel (one tab stop per panel) |
| ArrowRight / ArrowDown | Chip grid | Next chip (wraps) |
| ArrowLeft / ArrowUp | Chip grid | Previous chip (wraps) |
| Home | Chip grid | First chip |
| End | Chip grid | Last chip |
| Enter / Space | Focused chip | Toggle selection |
| ArrowDown | Filter input | Move focus to first chip |
| Escape | Chip grid | Return focus to filter input (or blur) |
| Tab / Shift+Tab | Anywhere | Natural document flow |

**D2 integration:** Focusing a chip via keyboard opens its metadata panel (same as
clicking). Escape from the grid closes the panel and returns focus to the filter input.

---

## Consequences

### Positive

- Keyboard-only users can navigate and select all tokens without a mouse
- Screen readers get correct `listbox`/`option` semantics and `aria-selected` state
- Tab stop count remains constant regardless of token count (one per axis panel)
- ArrowDown from filter → chip is a natural, learnable gesture that pairs with the
  existing filter-to-narrow workflow
- D2 metadata panel now surfaces automatically on keyboard focus — improves
  discoverability for keyboard users

### Tradeoffs

- `chipRefs` array requires `bind:this` on each chip in the `{#each}` loop —
  idiomatic Svelte but adds one binding per rendered chip
- `focusedIndex` must reset when `filtered` changes (filter input clears selection) —
  one `$effect` handles this

### Risks

- Low — changes are confined to `TokenSelector.svelte` and the `selected-chip` markup
  in `+page.svelte`. No grammar pipeline, no Python, no Go changes.
- The `bind:this` array pattern in Svelte 5 requires care when chips are added/removed
  by filtering; the `$effect` reset mitigates stale refs.

---

## Falsifiables

**F1 (critical gap closure):** After Tab-focusing into a form axis panel, pressing
ArrowRight moves focus through chips and Enter toggles selection — verified by vitest
`fireEvent.keyDown` in `TokenSelector.test.ts`.

**F2 (filter handoff):** Typing in a filter input then pressing ArrowDown moves DOM
focus to the first visible chip — verified by component test.

**F3 (screen-reader semantics):** The `.token-grid` has `role="listbox"` and each chip
has `role="option"` with correct `aria-selected` — verified by DOM attribute assertions
in tests.

**F4 (D2 integration):** ArrowRight to navigate to `wardley` chip shows the metadata
panel without a mouse click — verified by component test.

**F5 (selected badges):** Tab focuses a selected-chip badge and Enter deselects it —
verified by component test or manual check.

---

## Implementation Order

1. State additions and `$effect` reset (no visible change)
2. Grid `role="listbox"` + `handleGridKey`
3. Chip `role="option"` + roving `tabindex` + `onfocus` + `onkeydown`
4. Filter `onkeydown` ArrowDown handoff
5. D2 close button `<span>` → `<button>`
6. CSS `:focus-visible`
7. Page selected-chip badges
8. Tests: extend `TokenSelector.test.ts` with F1–F4 cases
