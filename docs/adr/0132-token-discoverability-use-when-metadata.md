# ADR-0132: Token Discoverability Metadata (`use_when`)

**Status:** Accepted

---

## Context

ADR-0113 Loop-8 identified a systemic discoverability gap: 8 specialist form tokens
(`wardley`, `wasinawa`, `spike`, `cocreate`, `taxonomy`, `facilitate`, `recipe`, `visual`)
produce good prompts when manually selected but are invisible to bar-autopilot because no
usage patterns guide selection for the tasks they serve.

The naive fix would add static usage patterns directly to the bar-autopilot skill file.
But this creates a second source of truth that drifts from the grammar — whenever a token
is renamed, added, or its semantics shift, both the grammar config and the skill file must
be updated in lockstep, with no enforcement mechanism.

ADR-0110 established a `guidance` field per token for conflict/constraint notes ("avoid
with X", "conflicts with Y"). This ADR adds a parallel `use_when` field for positive
task-type heuristics: "select me when the user wants X".

**Problem statement:** A selecting agent (bar-autopilot or human) reading `bar help llm`
sees token descriptions that explain what the token does but not when to reach for it.
The `use_when` field closes this gap by expressing intent-to-token mapping directly on
the token.

---

## Decision

Add a `use_when` metadata field, parallel to `guidance` (ADR-0110), propagated through
the same Python → JSON → Go → render pipeline.

### Field semantics

| Field | Purpose | Phrasing pattern |
|-------|---------|-----------------|
| `guidance` (ADR-0110) | Constraints — what to avoid, conflicts, do-not-pair | "Avoid with...", "Conflicts with...", "Do not use when..." |
| `use_when` (ADR-0132) | Discoverability — when to reach for this token | "Select when user wants X. Heuristic: phrase Y → token." |

The distinction is critical: `guidance` is a constraint (negative signal); `use_when` is
a positive heuristic (selection trigger). Mixing them would make the notes harder to scan.

### Initial token set

Nine form tokens from ADR-0113 Loop-8 analysis:

| Token | Use when |
|-------|----------|
| `wardley` | Strategic mapping on evolution axis |
| `wasinawa` | Post-incident reflection on past events |
| `spike` | Technology investigation as a backlog spike artifact |
| `cocreate` | Iterative design with explicit decision points |
| `ladder` | Abstraction laddering up/down |
| `taxonomy` | Type hierarchy or category classification |
| `facilitate` | Workshop or retrospective planning |
| `recipe` | Structured process with recurring notation |
| `visual` | Abstract/metaphorical overview for non-technical audience |

---

## Pipeline

```
lib/axisConfig.py            AXIS_KEY_TO_USE_WHEN dict + axis_key_to_use_when_map()
        ↓
lib/axisCatalog.py           axis_catalog() returns "axis_use_when" key
        ↓
lib/promptGrammar.py         _build_axis_section() exports section["use_when"]
        ↓
internal/barcli/embed/       prompt-grammar.json axes.use_when populated
        ↓
internal/barcli/grammar.go   AxisSection.UseWhen field + AxisUseWhen() getter
        ↓
internal/barcli/help_llm.go  renderTokenCatalog() adds 5th column "When to use"
```

The embedded JSON is the single artefact that crosses the Python/Go boundary. No
skill-file hardcoding is needed.

---

## Files Changed

| File | Change |
|------|--------|
| `lib/axisConfig.py` | Added `AXIS_KEY_TO_USE_WHEN` dict and `axis_key_to_use_when_map()` helper |
| `lib/axisCatalog.py` | Added `"axis_use_when"` key to `axis_catalog()` return value |
| `lib/promptGrammar.py` | Added `use_when` export in `_build_axis_section()` |
| `internal/barcli/grammar.go` | Added `UseWhen` field to `AxisSection` and `rawAxisSection`; added `AxisUseWhen()` getter |
| `internal/barcli/help_llm.go` | Added "When to use" as 5th column in `renderTokenCatalog()` axis tables |
| `internal/barcli/embed/prompt-grammar.json` | Regenerated |
| `build/prompt-grammar.json` | Regenerated |

---

## Consequences

**Positive:**
- Single source of truth: discoverability hints live on the token, not in a separate
  skill file that can drift.
- Scalable: adding `use_when` to a new token requires one dict entry in `axisConfig.py`
  and a JSON regen — no Go changes.
- Visible at runtime: `bar help llm` exposes the hints in the "When to use" column,
  making them available to any agent that ingests the LLM help output.
- Consistent with ADR-0110 pattern: `use_when` follows the same propagation path as
  `guidance`, so the codebase already knows how to handle it.

**Neutral:**
- Axis tables now have 5 columns. Rows without `use_when` data show an empty 5th cell.
  This is consistent with the empty `Notes` column for tokens without guidance.

**Scope boundary:**
- In scope: `AxisSection` form tokens (initial set of 9 from Loop-8).
- Out of scope: `StaticSection` tasks (already well-described by their profiles);
  `PersonaSection` (self-describing by design).
- Future: extend to other axes if discoverability gaps emerge in later ADR-0113 loops.
