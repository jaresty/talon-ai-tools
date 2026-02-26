# ADR 0148: Cross-Axis Composition Warnings in TUI2 and SPA

**Date:** 2026-02-26
**Status:** Proposed
**Authors:** jaresty

---

## Context

ADR-0147 introduced `CROSS_AXIS_COMPOSITION` — structured data capturing cautionary pairings for channel/form tokens (e.g., `shellscript+sim` tends to produce thin output; `code+to-ceo` is inaccessible). This data drives `bar help llm`'s "Choosing Channel" section, which provides pre-selection guidance to LLM users invoking bar via the skill.

ADR-0147 explicitly deferred:
> "Surfacing reframe descriptions in TUI2/SPA (would require new UI component)"

The gap is material: a user building prompts interactively in TUI2 or the SPA currently gets no warning when they select `shellscript` and then `sim`. The same user consulting `bar help llm` would see:
```
`shellscript`: ...
- Cautionary:
  - `sim` — tends to produce thin output — simulation is inherently narrative, not executable
```

This asymmetry leaves non-LLM users without the composition guidance that is central to ADR-0147's value.

### Existing UI state

**TUI2 selected-item detail panel** (`internal/bartui2/program.go` lines ~1854–1880):
- Renders for the currently focused token: Use When (cyan), Guidance (amber `→ `), description (wrapped)
- `TokenOption` fields: `Value`, `Slug`, `Label`, `Description`, `Guidance`, `UseWhen`, `Kanji`, `SemanticGroup`, `RoutingConcept`
- `CrossAxisCompositionFor()` not called anywhere in TUI2

**SPA meta panel** (`web/src/lib/TokenSelector.svelte` lines ~378–417):
- Renders on chip click: token header, description, "When to use" (use_when), "Notes" (guidance), Select button
- `TokenMeta` interface: `token`, `label`, `description`, `guidance`, `use_when`, `kanji`, `category`, `routing_concept`
- `Grammar` TypeScript interface lacks `cross_axis_composition`; no accessor for cautionary warnings

### Warning trigger: contextual vs. static

Cautionary warnings are most useful when they are **contextual** — shown only when the user has already selected a token that creates the problematic pairing. Always showing "shellscript has known cautionary pairings" on the shellscript chip would be noisy and uninformative; showing "⚠ sim — tends to produce thin output" only when `sim` is already selected is precisely targeted.

Both TUI2 and SPA have access to the current selection at render time, making contextual warnings achievable without changing token-building logic.

---

## Decision

### Warning model: contextual, render-time, selected-item only

Warnings appear in the selected-item detail panel (TUI2) or meta panel (SPA) when:

1. The token currently in focus (selected item / chip being inspected) appears in the `cautionary` dict of any channel or form token already active in the current selection, **or**
2. The token currently in focus is a channel or form token and any active token in a partner axis appears in its `cautionary` dict.

Direction (a): browsing task tokens while `shellscript` is active → `sim` shows a warning.
Direction (b): browsing `shellscript` channel token while `sim` is active → `shellscript` shows a warning.

Both directions are checked. Warning text comes directly from the `cautionary` dict entry.

Warnings are rendered only in the **selected-item / meta panel** context, not on token chips. This keeps the chip grid clean for scanning and reserves warnings for the moment the user is actively examining a token.

### Part A: TUI2

**Rendering location:** In `program.go`, inside the selected-item detail section of `renderTokensPane`. After the guidance line, if a contextual cautionary warning applies, render one line:

```
⚠ Caution: <warning text> (first sentence only if long)
```

Using `warningStyle` (amber, color 220) to match the existing guidance warning aesthetic.

**Data access:** `program.go` already has access to `m.grammar` (the Grammar object) and `m.tokens` (the current selection). Use `CrossAxisCompositionFor()` directly at render time — no changes to `TokenOption` struct or token-building functions required.

**Truncation:** Cautionary note truncated to first sentence (up to the first `. ` or 120 chars) to fit within the existing panel height budget. If a token has cautionary warnings from more than one active partner token, show the first one; the second is accessible by selecting the other token.

### Part B: SPA

**Rendering location:** In `TokenSelector.svelte`, inside the meta panel, after the "Notes" (guidance) section. A new "Caution" section, styled with a distinct warning background, renders contextual warnings.

**Data pipeline:**
1. Add `CrossAxisComposition` to the `Grammar` TypeScript interface in `grammar.ts`
2. Add `getCompositionWarning(grammar, axis, token, activeTokensByAxis) → string | null` accessor — looks up cautionary entry given active channel/form tokens
3. In `TokenSelector.svelte`, compute `compositionWarning` from `getCompositionWarning()` using the current `selectedTokens` prop; render if non-null

**Chip indicator (optional, Phase 2):** Evaluate whether a small `⚠` badge on task/audience chips adds value when a cautionary channel is selected. Only implement if signal-to-noise ratio is favorable (task axis cautionary only; defer audience cautionary chips to a later cycle).

---

## Consequences

### Positive

- Non-LLM users (TUI2, SPA) receive the same cautionary guidance as LLM users (`bar help llm`)
- Single SSOT: `CROSS_AXIS_COMPOSITION` in `lib/axisConfig.py` drives all three surfaces
- No new grammar data required — existing `cautionary` dict is used directly
- Contextual display keeps the token grid clean; warnings appear only when relevant
- No changes to `TokenOption`, `buildAxisOptions`, or the Python grammar pipeline

### Risks

**R1 — TUI2 panel height.** Adding a cautionary line to the selected-item area may reduce visible lines for description on terminals with limited height. Mitigation: truncate to first sentence; skip caution line entirely if `paneHeight < 12` (same threshold used for routing concept subtitle).

**R2 — SPA chip badge noise.** Non-technical audience tokens (to-ceo, to-managers, to-stakeholders, to-team) all trigger cautionary warnings when `shellscript` or `code` is selected. Showing badges on all four chips simultaneously would dominate the audience section visually. Mitigation: meta panel only in Phase 1; chip badge decision deferred to Phase 2 after observing usage.

**R3 — Type-safety in SPA.** Adding `CrossAxisComposition` to the TypeScript `Grammar` interface requires mapping the nested Python dict structure. The shape is `Record<string, Record<string, Record<string, { natural: string[], cautionary: Record<string, string> }>>>`. Mitigation: use a named TypeScript type `CrossAxisPair` mirroring the Go struct.

---

## Implementation Plan

### Phase 1: TUI2 contextual warning (program.go only)

1. In `program.go` selected-item render: lookup `m.grammar.CrossAxisCompositionFor(axis, token)` for each channel/form token in `m.tokens`; if current token appears in any `cautionary` map, render one warning line using `warningStyle`
2. Also check reverse: if current token is a channel/form token, check if any active token in partner axis is in its `cautionary` map
3. Test: extend TUI2 smoke fixture or unit test to cover cautionary note render path

### Phase 2: SPA meta panel warning

1. `grammar.ts`: Add `CrossAxisComposition` interface type; add `getCompositionWarning()` accessor
2. `TokenSelector.svelte`: Add "Caution" section in meta panel; render when `compositionWarning` is non-null; style with warning background (distinct from `.meta-note`)
3. Test: extend SPA tests to cover the new section; all 110+ existing SPA tests must continue to pass

### Phase 3: SPA chip badge (deferred, evaluate post-Phase 2)

1. Evaluate signal-to-noise: count average number of chips that would show ⚠ in typical selection state
2. If acceptable, add small ⚠ indicator to chip when compositionWarning applies
3. Limit to task axis cautionary warnings in initial implementation

---

## Deferred

- Chip-level badges (Phase 3, signal-to-noise evaluation required)
- Surfacing `natural` combinations as positive confirmations in the UI (e.g., "✓ Natural pairing" for `shellscript+make`) — low priority; positive cases are already derivable from the Reference Key universal rule
- Extending warnings to completeness×method tensions (`skim+rigor`) if/when those are added to `CROSS_AXIS_COMPOSITION`
