# ADR-0170: SPA Persona Section Layout — Preset-First Visual Hierarchy

**Status**: Proposed
**Date**: 2026-03-16

---

## Context

The SPA persona tab has two layers of persona control:

1. **Preset selector** — 8 chips (Designer to PM, Executive brief, etc.), each encoding a voice + audience + tone bundle.
2. **Per-axis selectors** — four `<select>` dropdowns (Voice, Audience, Tone, Intent).

The underlying model is:

- `preset` and `{voice, audience, tone}` are **mutually exclusive**: selecting any axis dropdown clears `persona.preset`; selecting a preset clears voice/audience/tone.
- `intent` is **additive**: it never clears `preset`. It can accompany either a preset or per-axis selections.

### Observed problems (screenshot: 2026-03-16)

The current flat layout treats preset chips and axis dropdowns as visual peers. A user encounters:

```
PRESET
  [Designer to PM]  [Executive brief]  ...
  ← preset detail card (when selected) →

Voice      ——
Audience   ——
Tone       ——
Intent     ——
```

**Gap 1 — No affordance for the override model.** There is no visual indication that the axis dropdowns "override" or replace the preset. A user who picks a preset and then changes Voice receives no feedback that they are leaving preset mode; the preset chip appears deselected with no explanation.

**Gap 2 — Intent looks like voice/audience/tone.** All four selects have the same visual weight, but Intent has different semantics (additive, not exclusive). A user can reasonably infer they must pick only one path when the correct answer is "pick a preset or axis selects for voice/audience/tone, and optionally add intent either way."

**Gap 3 — Preset value is invisible at override decision time.** When a preset is selected, its axis values appear in the detail card. But when the user scrolls to the axis dropdowns, the preset's values are no longer visible — they cannot see what they would be overriding.

**Gap 4 — No token metadata browsing for voice/audience/tone/intent.** The `<select>` elements only show token names. Users cannot browse definitions, heuristics, or distinctions before selecting — unlike every other axis in the SPA, which uses `TokenSelector` chip grids with hover/click detail panels.

---

## Decision

Restructure the persona section into three visually distinct zones, replacing `<select>` dropdowns with `TokenSelector` chip grids for all four persona axes.

### Zone 1 — Preset (primary)

Unchanged: chip grid with 8 presets at full visual weight.

When a preset is active, replace the current prose detail card with a compact **axis summary strip** immediately below the chips — a single line of `voice=X audience=Y tone=Z` codes using `<code>` chips. This keeps the preset's constituent values visible as the user considers whether to override.

### Zone 2 — Voice / Audience / Tone (subordinate chip grids)

Replace the three `<select>` elements with `TokenSelector` chip grids, indented behind a dim "or customize" divider. Each grid includes:
- A filter input (same as all other axes)
- Token chips showing name + routing concept
- Click-to-select detail panel with definition, heuristics, and distinctions

Token counts: voice (12), audience (15), tone (5) — all fit naturally as chip grids with filter.

```
──────── or customize ────────

  VOICE  0–1
  filter…
  [as designer] [as programmer] [as future historian] …

  AUDIENCE  0–1
  filter…
  [to product manager] [to programmer] …

  TONE  0–1
  [casually] [directly] [formally] [gently] [kindly]
```

Selecting any chip clears `persona.preset` (existing behavior, unchanged).

### Zone 3 — Intent (peer, always-accessible chip grid)

Intent sits outside and below the "or customize" container with the same chip grid treatment. Its structural separation from Zone 2 communicates that it is additive (never clears preset).

Token count: intent (6) — very compact, no filter needed.

```
INTENT  0–1
[announce] [appreciate] [coach] [inform] [persuade] [teach]
```

### Resulting layout

```
PERSONA
Communication style — who speaks, for whom, and in what tone.

PRESET
[Designer to PM ✓]  [Executive brief]  [Fun mode]  ...
  voice=as designer  audience=to product manager  tone=directly

──────── or customize ────────

  VOICE  0–1
  filter…
  [as designer ✓]  [as programmer]  [as future historian]  ...

  AUDIENCE  0–1
  filter…
  [to product manager ✓]  [to programmer]  ...

  TONE  0–1
  [casually]  [directly ✓]  [formally]  [gently]  [kindly]

INTENT  0–1
[announce]  [appreciate]  [coach]  [inform]  [persuade]  [teach]
```

When no preset is active, the axis summary strip is hidden and all four chip grids are shown at full weight.

---

## Consequences

### Positive

- The preset-first model is now self-evident from visual structure alone.
- Voice/audience/tone/intent gain full token metadata browsing (definitions, heuristics, distinctions) — consistent with every other axis in the SPA.
- Intent's additive role is communicated structurally.
- No behavioral change — token generation, serialization, and existing test coverage are unaffected.

### Negative / constraints

- The persona section becomes taller. Voice (12 tokens) and Audience (15 tokens) each occupy more vertical space than a single `<select>` line. Mitigated by the filter inputs, which collapse the visible set quickly.
- `TokenSelector` is currently wired for constraint axes. It will need to accept persona token metadata (`PersonaTokenMetadata` from the grammar's `persona.metadata` section) rather than axis token metadata. The component interface may need a small generalisation or a thin wrapper.
- The existing `persona-select` and `persona-select-label` CSS can be removed; `.override-group` and `.intent-group` CSS is added.

### Non-changes

- Token generation logic (`tokens` derived store) is unchanged.
- `intent` behavioral semantics (does not clear preset) are unchanged.
- The preset detail card's Heuristics/Distinctions panels are removed — replaced by the per-token detail panels in the chip grids, which are more granular and available pre-selection.

---

## Implementation shape

Primary changes are in `web/src/routes/+page.svelte`. `TokenSelector.svelte` may need a small interface extension.

**Step 1 — Expose persona token metadata to TokenSelector**

`TokenSelector` currently receives tokens as `{ token, label, description, routing_concept, metadata }[]`. The grammar already exposes persona token metadata via `grammar.persona.metadata['voice'][token]` etc. Add a helper `getPersonaAxisTokensMeta(grammar, axis)` (parallel to the existing `getPersonaAxisTokens`) that returns the full token objects with metadata populated. Wire this into the three chip grid call sites.

**Step 2 — Add axis summary strip**

```svelte
{#if persona.preset}
  {@const presetMeta = getPersonaPresets(grammar).find(p => p.key === persona.preset)}
  <div class="preset-axis-summary">
    {#if presetMeta?.voice}<code class="preset-axis-tag">voice={presetMeta.voice}</code>{/if}
    {#if presetMeta?.audience}<code class="preset-axis-tag">audience={presetMeta.audience}</code>{/if}
    {#if presetMeta?.tone}<code class="preset-axis-tag">tone={presetMeta.tone}</code>{/if}
  </div>
{/if}
```

**Step 3 — Replace Zone 2 selects with chip grids**

Remove the three `<label class="persona-select-label">` blocks for voice, audience, tone. In their place, inside an `override-group` container with the "or customize" dim divider, render three `<TokenSelector>` instances:

```svelte
<div class="override-group">
  <div class="override-group-label">or customize</div>
  <TokenSelector
    axis="voice"
    tokens={getPersonaAxisTokensMeta(grammar, 'voice')}
    selected={persona.voice ? [persona.voice] : []}
    capacity={1}
    onselect={(tok) => { persona = { preset: '', voice: tok, audience: persona.audience, tone: persona.tone, intent: persona.intent }; }}
    ondeselect={() => { persona = { ...persona, voice: '' }; }}
  />
  <!-- audience, tone similarly -->
</div>
```

**Step 4 — Replace Zone 3 intent select with chip grid**

Remove the `<label class="persona-select-label">` block for intent. Replace with a `<TokenSelector>` outside the `override-group`, with `capacity={1}` and an `onselect` that preserves `persona.preset`.

**Step 5 — CSS cleanup**

- Remove: `.persona-select`, `.persona-select-label`, `.persona-hint`, `.persona-hint-note`
- Add: `.override-group` (left-border indent), `.override-group-label` (dim separator text), `.intent-group` (top margin separation)

**Acceptance criteria:**

1. Preset chips and axis summary strip are visible together; no scroll needed to see what a preset sets.
2. Voice, Audience, and Tone appear as chip grids below a dim "or customize" divider.
3. Intent appears as a chip grid outside and below the customize group.
4. Each chip grid shows a detail panel (definition, heuristics, distinctions) on token focus/click — same as task, scope, method, etc.
5. Selecting a voice/audience/tone chip clears `persona.preset` (no behavioral regression).
6. Selecting an intent chip does NOT clear `persona.preset` (no behavioral regression).
7. All existing SPA tests pass.
8. The page renders correctly at 390px mobile viewport — chip grids wrap and filter inputs are usable.

---

## Alternatives considered

**Option A — Keep `<select>` dropdowns, add post-selection disclosure**
Voice/audience/tone/intent remain as `<select>` elements; add a collapsible detail panel for the selected value. Addresses Gap 1–3 but not Gap 4 (no pre-selection browsing). Rejected — metadata browsing is the primary value of the chip grid pattern and consistency with other axes matters.

**Option B — Two-path explicit fork ("PRESET or CUSTOM")**
A hard OR separator with two titled sections. Cleaner conceptually, but breaks the existing mental model for users who use presets + intent together. Requires more template restructuring. Deferred.

**Option C — Status quo**
Accepted cost: documented UX gap (Tier 2 backlog). Rejected because the preset-axis relationship is a teaching surface that directly affects first-use success, and the absence of metadata browsing is inconsistent with all other axes.
