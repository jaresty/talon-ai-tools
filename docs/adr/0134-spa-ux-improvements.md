# ADR-0134: SPA UX Improvements — Command Input, Metadata Panel, and Pattern Sync

## Status

Accepted

## Context

The bar SPA (browser-based prompt builder at `web/`) reads from `prompt-grammar.json`
for token data but has three independent UX gaps that reduce its utility:

### Gap 1 — No command input (UI is one-way)

The SPA generates `bar build` commands from UI selections but cannot parse them back.
A user who has a command in their clipboard — copied from a colleague, from the CLI
history, or from a patterns library — cannot load it into the SPA. The state serialization
uses Base64-encoded internal state, not the human-readable bar grammar syntax.

### Gap 2 — Token metadata hidden in tooltips

The `guidance` (notes, conflicts) and `use_when` (when-to-use heuristics) fields are
loaded from `prompt-grammar.json` and appended into a browser `title` attribute.
They are invisible unless the user hovers over a token chip and reads a plain-text tooltip.
A small dot indicator (`●`) is the only persistent visual cue that metadata exists.
This makes `use_when` — the primary mechanism for specialist form discoverability
established in ADR-0132 — largely invisible in the SPA.

### Gap 3 — Pattern lists diverge silently

`help_llm.go` has 32 hardcoded usage patterns in Go code. `PatternsLibrary.svelte`
has 8 separate patterns hardcoded in TypeScript. They address different tasks, use
different token combinations, and diverge silently as new patterns are added to either
side. There is no shared source of truth, no lint, and no mechanism to detect drift.

### Structural relationship

Gaps 1 and 2 are independent, SPA-only changes that can be shipped without touching
the grammar pipeline. Gap 3 requires a pipeline change (Python SSOT → generator →
grammar JSON → both consumers) and carries significant migration cost. Gaps 1 and 2
have high user value at low complexity; Gap 3 is the architecturally correct long-term
fix but is separable.

---

## Decision

### D1 — Add a command input box to the SPA (Gap 1)

Add a text input field to the SPA that accepts a `bar build` command string. On submit,
the parser:

1. Strips the `bar build` prefix and any `--subject` / `--addendum` flags (extracting
   their values into the subject/addendum fields if present)
2. Tokenizes the remaining string by whitespace
3. Resolves each token against `grammar.axes.definitions` and `grammar.tasks` to
   identify its axis and set the corresponding selector state
4. For persona tokens (`voice=`, `audience=`, `tone=`, `intent=`, `persona=`), parses
   the key=value form and sets persona state accordingly
5. Ignores unrecognized tokens with a visible warning listing them

This is a pure client-side change. The grammar already contains all information needed
to classify tokens by axis. The parser is stateless and requires no new data source.

**Placement:** A collapsible "Load command" input above or below the token selector grid.

**Falsifiable:** After entering `bar build show mean full plain` into the input, the
task selector shows `show`, completeness shows `full`, scope shows `mean`, and channel
shows `plain` — all other axes clear.

### D2 — Replace tooltip metadata with an expandable inline panel (Gap 2)

Replace the `title`-attribute tooltip with an expandable information panel. When a
token chip is selected or clicked, a panel below the chip row (or in a fixed sidebar)
expands to show:

- **Description**: the token's definition (currently in the tooltip)
- **When to use**: the `use_when` field, formatted as guidance text
- **Notes / Conflicts**: the `guidance` field, formatted with a distinct visual style

The small dot indicator (`●`) may remain as a discoverability cue but is no longer the
only way to know metadata exists.

**Approach:** Extend `TokenSelector.svelte` to track an `activeToken` state and render
an inline `<details>` or animated panel for the active token's metadata. The data is
already in the grammar object passed to the component.

**Falsifiable:** Clicking the `wardley` form chip shows "Strategic mapping: user wants
to position components on an evolution axis..." in a visible panel without requiring hover.

### D3 — Move patterns into `prompt-grammar.json` SSOT (Gap 3)

Add `USAGE_PATTERNS` as a list of `{title, command, example, desc, tokens}` dicts to
`lib/axisConfig.py`. Wire through the existing pipeline (`axisCatalog.py` →
`promptGrammar.py`) so `patterns` appears as a top-level key in `prompt-grammar.json`,
parallel to `axes`, `tasks`, and `hierarchy`.

**Consumer changes:**
- `help_llm.go`: `renderUsagePatterns` reads `grammar.Patterns` instead of a hardcoded
  Go slice. The `Grammar` struct gains a `Patterns []GrammarPattern` field.
- `PatternsLibrary.svelte`: Remove the hardcoded TypeScript patterns array. Accept
  `patterns: GrammarPattern[]` as a prop populated from `getUsagePatterns(grammar)`.

**Schema:** Each pattern carries `tokens: Record<string, string[]>` mapping axis names
to token lists (serving the SPA selector state) in addition to the CLI-oriented
`command`/`example`/`desc` fields (serving `bar help llm` rendering).

**Rationale for not deferring:** The pipeline pattern is well-understood after loop-10
(`axis_use_when` followed the same path). The "patterns are in flux" argument cuts the
other way — more flux means more divergence. Fixing now stops compounding debt.

**Falsifiable:** After implementation, `go test ./internal/barcli/ -run TestGrammarPatternsLoaded`
passes, confirming `grammar.Patterns` is non-empty and `len >= 32`. The SPA
`PatternsLibrary` renders patterns loaded from the grammar without a local fallback.

---

## Consequences

### D1 — Command input

**Positive:**
- Unlocks the clipboard workflow: commands copied from docs, colleagues, or CLI history
  can be loaded into the SPA without re-selecting tokens manually
- Makes the SPA bidirectionally usable as a bar command explorer
- Pairs with D2: loading a command immediately shows the metadata for each loaded token

**Tradeoffs:**
- Parser must handle edge cases: directional compound tokens (`fly-rog`), persona
  key=value syntax, unknown tokens, flags with quoted values
- `--subject` and `--addendum` flag parsing is fragile if values contain quotes

**Risks:**
- Parser drift if bar grammar changes (new token forms, new axes). Mitigation: parser
  uses grammar.json as source of truth for token→axis mapping; only flag parsing is hardcoded.

### D2 — Metadata panel

**Positive:**
- Makes `use_when` discoverable without hover — directly addresses the ADR-0132 mechanism
  being invisible in the SPA
- Reduces friction for users learning the catalog; inline guidance reduces need to
  consult `bar help llm`

**Tradeoffs:**
- Requires UI real estate for the expanded panel; may need a collapsible design to avoid
  crowding the token grid

**Risks:**
- Low — data is already present; this is presentation-only. No new data dependencies.

### D3 — Patterns in grammar JSON SSOT

**Positive:**
- Single source of truth: adding a pattern to `USAGE_PATTERNS` in `axisConfig.py`
  automatically propagates to both `bar help llm` and the SPA after grammar regeneration
- Eliminates the two-list divergence problem permanently
- The `tokens` field enables the SPA to load any pattern into the token selectors,
  linking the patterns library to D1 (command input) and D2 (metadata panel)

**Tradeoffs:**
- Future pattern additions require regenerating grammar files; can no longer hot-edit
  `help_llm.go` alone
- Pattern token maps must be kept in sync with token names in the grammar

**Risks:**
- Low — pipeline is well-understood after loop-10; same path as `axis_use_when`

**Future extension:** ADR-0135 (proposed) — patterns in grammar JSON SSOT, with dynamic
rendering in both CLI help and SPA. Should be initiated when the pattern set is stable
and the generator pipeline is well-understood.

---

## Implementation Order

1. **D3 first** (patterns SSOT pipeline) — establishes the data foundation; D1 and D2
   benefit from `tokens` maps being available in the grammar
2. **D2 second** (metadata panel) — pure SPA, no data changes, unblocks ADR-0132 value
3. **D1 third** (command input) — pure SPA, pairs with D2 for immediate metadata display

---

## Alternatives Considered

### Command input via URL query params

Encoding bar commands in URL query params (e.g., `?cmd=show+mean+full+plain`) rather
than a text input box. Rejected: couples URL format to bar grammar, making URL-encoded
state fragile across grammar changes. The text input is user-initiated and ephemeral;
URL encoding is persistent and would require backward compatibility.

### Sidebar panel instead of inline panel for metadata

A fixed sidebar that updates as tokens are selected. Rejected at this stage: requires
more layout restructuring. The inline panel is progressive enhancement — it can be
shipped without redesigning the page layout.

### Tooltip enhancement (richer tooltip)

Improving the existing browser tooltip with formatted HTML. Rejected: `title` attributes
are plain text only; rich tooltips require a custom popup, which is effectively the same
implementation cost as the inline panel but with worse accessibility.
