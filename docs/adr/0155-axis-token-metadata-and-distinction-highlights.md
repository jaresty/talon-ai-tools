# ADR-0155: Axis Token Structured Metadata + SPA Distinction Highlights

## Status

Draft

## Context

ADR-0154 introduced the `definition / heuristics / distinctions` schema for task tokens (11 tokens), replacing free-form `guidance` and `use_when` strings. That ADR explicitly deferred axis tokens.

Axis tokens (6 axes, ~158 tokens) carry two free-form text fields in `lib/axisConfig.py`:

| Field | Dict | Coverage | Current content mix |
|-------|------|----------|---------------------|
| `guidance` | `AXIS_KEY_TO_GUIDANCE` | 46/158 (29%) | Definition refinement + "Distinct from X" clauses |
| `use_when` | `AXIS_KEY_TO_USE_WHEN` | 153/158 (97%) | "Heuristic: 'X', 'Y'" + "Distinct from X" + cross-axis context |

Both fields mix semantic domains within the same string, for the same reasons as the task token fields in ADR-0154. The `use_when` strings in particular always follow a recognizable pattern: an intent description, a `Heuristic:` phrase with trigger words, and one or more "Distinct from X" comparisons.

Additionally, the SPA `TokenSelector.svelte` renders distinction entries as static text (`make — fix = reformat; make = create new`). A natural next step is to make those entries interactive: hovering a distinction's token name highlights the corresponding chip in the grid, giving the user a direct visual cross-reference without navigating away.

### Content mapping to ADR-0154 schema

| Current source | Content pattern | Target field |
|----------------|----------------|--------------|
| `use_when` first sentence / intent phrase | "user wants X", "focuses on Y" | `definition` (replaces or supplements grammar description) |
| `use_when` `Heuristic:` clause | `'analyze', 'debug', 'troubleshoot'` | `heuristics[]` |
| `use_when` + `guidance` "Distinct from X" | `X = note; this = note` | `distinctions[]` |

The split is systematic enough that axis-by-axis loops can use a consistent parse → curate → validate cycle.

### Distinction highlight behavior

When a user hovers a distinction entry's token `<code>` element in the meta panel:

- **Same-axis token**: the corresponding chip pulses/highlights in the current grid
- **Cross-axis token**: a small `→ axis` indicator appears on the distinction entry; clicking navigates to that axis and scrolls the chip into view

For the initial implementation (T-1), only same-axis highlighting is required; cross-axis navigation is a residual.

## Decision

Apply the ADR-0154 `definition / heuristics / distinctions` schema to all 6 axis token types, migrating axis-by-axis. Add SPA distinction chip highlighting as a consumer feature enabled by structured data.

### Schema extension

The `axes` section of `prompt-grammar.json` gains a parallel `metadata` key:

```json
{
  "axes": {
    "definitions": { "completeness": { "gist": "..." } },
    "metadata": {
      "completeness": {
        "gist": {
          "definition": "Brief but complete answer touching main points without deep exploration.",
          "heuristics": ["quick summary", "tldr", "overview", "just the gist"],
          "distinctions": [
            { "token": "skim", "note": "gist = brief but complete; skim = light pass, may miss non-obvious" }
          ]
        }
      }
    }
  }
}
```

### Python SSOT

`lib/axisConfig.py` gains `AXIS_TOKEN_METADATA: dict[str, dict[str, AxisTokenMetadata]]` — a nested dict keyed by axis then token, using the same `TypedDict` shape as `_TASK_METADATA`. Migration is axis-by-axis, co-existing with the old `AXIS_KEY_TO_GUIDANCE` / `AXIS_KEY_TO_USE_WHEN` dicts until an axis is fully migrated, then those dicts drop the migrated entries.

```python
class AxisTokenMetadata(TypedDict):
    definition: str
    heuristics: list[str]
    distinctions: list[AxisTokenDistinction]

class AxisTokenDistinction(TypedDict):
    token: str
    note: str

AXIS_TOKEN_METADATA: dict[str, dict[str, AxisTokenMetadata]] = {
    "completeness": {
        "gist": {
            "definition": "Brief but complete answer...",
            "heuristics": ["quick summary", "tldr", "overview"],
            "distinctions": [{"token": "skim", "note": "gist = brief but complete; skim = light pass"}]
        },
        ...
    },
    ...
}
```

### Pipeline

```
lib/axisConfig.py   AXIS_TOKEN_METADATA dict
      ↓
lib/axisCatalog.py  axis_catalog() adds "axis_token_metadata" key
      ↓
lib/promptGrammar.py  _build_axis_section() writes axes.metadata
      ↓
prompt-grammar.json   axes.metadata[axis][token] = {definition, heuristics, distinctions}
      ↓
grammar.go            AxisSection.Metadata + AxisMetadataFor() accessor
      ↓
grammar.ts            AxisSection.metadata + getAxisTokens() reads metadata
      ↓
TokenSelector.svelte  axis tokens use same structured panel rendering as task tokens
      ↓
help_llm.go           axis tables gain Definition / Heuristics / Distinctions columns
```

### Migration order

Axes ordered by token count and guidance coverage to minimize scope per loop:

| Order | Axis | Tokens | Guidance entries | UseWhen entries |
|-------|------|--------|-----------------|-----------------|
| T-3 | completeness | 7 | 3 | 7 |
| T-4 | channel | 15 | 1 | 15 |
| T-5 | directional | 16 | 0 | 7 |
| T-6 | scope | 13 | 1 | 13 |
| T-7 | form | 34 | 10 | 34 |
| T-8 | method | 73 | 31 | 73 |

Each migration loop: populate `AXIS_TOKEN_METADATA[axis]` from existing strings → validate with token coverage test → remove migrated entries from the old dicts.

### SPA distinction highlight

`TokenSelector.svelte` gains a `hoveredDistinctionToken: string | null` reactive variable. Hovering a `.meta-distinction-entry` sets it; mouseleave clears it. Chips with `data-token={hoveredDistinctionToken}` receive a `chip--distinction-ref` CSS class (subtle ring/pulse, does not conflict with selected/disabled/cautionary states).

### Consumer requirements

| Consumer | Change |
|----------|--------|
| `TokenSelector.svelte` | Axis tokens: same `{#if activeMeta.metadata}` branch used for task tokens — structured panel renders automatically |
| `help_llm.go` | Axis token tables: swap `Guidance \| When to use` columns for `Definition \| Heuristics \| Distinctions` |
| `tui_tokens.go` | Derive `Guidance`/`UseWhen` strings from `AxisMetadataFor()` (same adapter pattern as task tokens) |
| `AXIS_KEY_TO_GUIDANCE` | Remove entries as each axis is migrated |
| `AXIS_KEY_TO_USE_WHEN` | Remove entries as each axis is migrated |

## Salient Task List

- **T-1** SPA distinction chip highlight: `hoveredDistinctionToken` state + `chip--distinction-ref` CSS — works immediately for task tokens
- **T-2** Python/Go/TS pipeline: `AXIS_TOKEN_METADATA` dict + `axis_token_metadata` catalog key + grammar export + `AxisSection.Metadata` + `AxisMetadataFor()` + `grammar.ts` type update — no content yet, schema wiring only
- **T-3** completeness axis migration (7 tokens)
- **T-4** channel axis migration (15 tokens)
- **T-5** directional axis migration (16 tokens)
- **T-6** scope axis migration (13 tokens)
- **T-7** form axis migration (34 tokens)
- **T-8** method axis migration (73 tokens)
- **T-9** Wire SPA `TokenSelector.svelte` axis token panel to use `activeMeta.metadata` structured rendering (drop legacy `guidance`/`use_when` fallback for axis tokens once all axes migrated)
- **T-10** Wire `help_llm.go` axis tables to use structured metadata; remove `AxisGuidance()`/`AxisUseWhen()` accessors
- **T-11** Wire `tui_tokens.go` axis tokens to use `AxisMetadataFor()`; remove old accessor calls
- **T-12** Remove `AXIS_KEY_TO_GUIDANCE` and `AXIS_KEY_TO_USE_WHEN` from `axisConfig.py` (after T-3–T-8 complete)

## Alternatives Considered

### Keep free-form strings, structured display only
Parse heuristics/distinctions at render time in the SPA/CLI using regex. Rejected: fragile, breaks when strings don't match pattern, and doesn't clean up the SSOT.

### Extend ADR-0154 instead of new ADR
ADR-0154 is Accepted with a clean implementation record. The axis migration is a larger and distinct effort (100+ tokens vs 11). New ADR preserves traceability.

### Automated extraction only (no curation)
Write a parser that extracts heuristics and distinctions from existing strings without manual review. Rejected: strings vary enough in structure that extraction errors would compound across 158 tokens. Human review per axis is required.

## Consequences

### Positive
- Axis tokens gain the same structured discoverability surface as task tokens
- SPA panel renders consistently for all tokens
- Distinction highlighting improves cross-reference navigation
- `AXIS_KEY_TO_GUIDANCE`/`USE_WHEN` eventually removed — single structured SSOT

### Negative
- Migration effort: ~158 tokens × manual curation ≈ significant content work
- T-3–T-8 must complete before T-9/T-10/T-12 can land

### Residual
- Cross-axis distinction navigation (→ axis indicator, auto-scroll) deferred from T-1

---

*Work-log: `0155-axis-token-metadata-and-distinction-highlights.work-log.md`*
