# ADR 0146: Help LLM SSOT Alignment — Move Token-Specific Guidance Out of help_llm.go

**Date:** 2026-02-25
**Status:** Proposed
**Authors:** jaresty

---

## Context

`bar help llm` serves as the primary reference document consumed by LLM agents using bar. It is rendered by `internal/barcli/help_llm.go`, which mixes two distinct sources:

1. **Metadata-driven content** — token descriptions, labels, use_when, guidance, kanji, and categories pulled from `lib/axisConfig.py` and `lib/personaConfig.py` at grammar-generation time.
2. **Hardcoded prose** — sections written directly as `fmt.Fprintf` calls in `help_llm.go`, independent of any metadata.

The second category creates a SSOT (single source of truth) violation: guidance that is logically owned by a specific token lives in Go source rather than in the Python metadata files where all other token properties live. This means:

- When a new token is added, its heuristic routing entry must be added manually to `help_llm.go` in addition to the metadata — the second location is easy to forget.
- When a token's meaning changes, the hardcoded prose may not be updated in sync.
- The hardcoded content is invisible to tools that read token metadata (the SPA, TUI2, and any future tooling).

An audit of `help_llm.go` against `axisConfig.py` and `personaConfig.py` (ADR-0085 Cycle 9 process, run 2026-02-25) identified three categories of hardcoded text that belong in token metadata:

### Finding 1 — `max` + `grow` cross-axis tension (no metadata backing at all)

The "Completeness × Method compatibility" note in `renderTokenSelectionHeuristics`:

> "`max` (尽 — exhaust all coverage) + `grow` (増 — expand only under demonstrated necessity) send contradictory signals. … Avoid combining them."

Neither `max` (completeness) nor `grow` (method) has any `guidance` entry in `axisConfig.py`. The rule lives only in hardcoded Go prose. If either token's description changes, the tension note will not update.

**Fix:** Add the tension note to `AXIS_KEY_TO_GUIDANCE["completeness"]["max"]` and `AXIS_KEY_TO_GUIDANCE["method"]["grow"]`. Remove the hardcoded block from `renderTokenSelectionHeuristics`.

### Finding 2 — Channel × audience incompatibility (no metadata backing at all)

The "Channel × audience compatibility" note in `renderTokenSelectionHeuristics > Choosing Persona`:

> "technical output channels (`code`, `shellscript`, `codetour`) are incompatible with non-technical audiences (to-CEO, to-managers, to-stakeholders, to-team)."

No channel token has this audience-incompatibility in its `guidance` entry. The rule lives only in hardcoded Go prose, and was added specifically to address a shuffle-cycle finding (ADR-0085 Cycle 9, R33) without being reflected in the SSOT.

**Fix:** Add the incompatibility note to `AXIS_KEY_TO_GUIDANCE["channel"]["code"]`, `["shellscript"]`, and `["codetour"]`. Remove the hardcoded block from `renderTokenSelectionHeuristics`.

### Finding 3 — "Choosing intent=" condensed line duplicates per-token use_when

The hardcoded line in `renderTokenSelectionHeuristics`:

> "use when the framing purpose matters — `intent=inform` (transfer knowledge/status), `intent=persuade` (influence belief or action), `intent=teach` (build deep understanding), `intent=announce` (share news or a change), `intent=coach` (develop the audience's capability), `intent=appreciate` (express thanks or recognition)."

`PERSONA_KEY_TO_USE_WHEN["intent"]` in `personaConfig.py` already has a full per-token entry for each of these six intent tokens with heuristic phrases and disambiguation. The Token Catalog table in `bar help llm` renders those entries. The hardcoded line is a stale abbreviation of that data. If a seventh intent token is added, the hardcoded line silently omits it.

**Fix:** Remove the hardcoded `Choosing intent=` line. The Token Catalog table already provides the complete per-token guidance.

---

### Finding 4 — Distilled routing guide has no metadata bucket (deferred)

The "Choosing Scope" and "Choosing Form" sections in `renderTokenSelectionHeuristics` contain compact concept-to-token routing bullets:

```
- Entities/boundaries → `thing`, `struct`
- Failure modes → `fail`
- Actionable next steps → `actions`, `checklist`
```

These are a third content type — distinct from `use_when` (verbose heuristic phrases) and `guidance` (disambiguation/warnings). They are *distilled routing labels*: the shortest phrase that maps a user's framing to one or two tokens.

Currently they are hardcoded in `help_llm.go`. There is no metadata bucket for them. Two structural patterns appear:

| Pattern | Example | Token count |
|---------|---------|------------|
| Single-token routing | "Failure modes → `fail`" | 1 |
| Multi-token routing | "Entities/boundaries → `thing`, `struct`" | 2+ |

**Option A — Use existing `AXIS_KEY_TO_LABEL`**
Labels are already 3–8 word CLI-facing descriptions. If labels were written as concept-first routing phrases ("Failure modes", "Entities/boundaries"), the Choosing Scope/Form sections could render dynamically from `AXIS_KEY_TO_LABEL`. Downside: labels are per-token; multi-token routing bullets can't be expressed this way.

**Option B — New `AXIS_KEY_TO_ROUTING_CONCEPT` bucket**
A new dict mapping each token to a short routing concept phrase ("Failure modes", "Entities and boundaries"). `help_llm.go` groups tokens that share a routing concept and renders them as a single bullet ("Entities/boundaries → `thing`, `struct`"). Enables the routing guide to be fully dynamic and usable by other surfaces (TUI2, SPA hover text).

**Option C — Keep hardcoded; add cross-reference pointer only**
Accept that routing bullets are editorial and maintain them as prose. Add a note in `help_llm.go` that the complete per-token guide is in the Token Catalog. Lower implementation cost; retains hardcoded staleness risk when tokens are added.

**Decision: Deferred.** The three immediate changes (Findings 1–3) remove genuine SSOT violations. Finding 4 is a quality-of-life improvement — the routing bullets are intentionally distilled and their hardcoded nature is less harmful because they rarely need to change. The `AXIS_KEY_TO_ROUTING_CONCEPT` design (Option B) is appealing for future SPA/TUI2 integration but requires a separate ADR once there is a concrete consumer need beyond `help_llm.go`.

---

### Out of scope (confirmed stays hardcoded)

The following hardcoded content was audited and classified as **Type A** (cross-token or cross-axis rules with no single metadata home):

| Content | Why it stays |
|---|---|
| "Known audience: prefer explicit `audience=` over presets" | Spans the entire presets × audience token space |
| "Presets are shortcuts — verify audience matches" | Cross-system meta-guidance |
| Compound directionals require `full`/`deep` completeness | Applies to the compound directional *type*, not any specific token |
| Choosing Method sub-group labels ("Narrowing to recommendation → converge, meld", etc.) | Editorial sub-groupings within `AXIS_KEY_TO_CATEGORY`; no token-level metadata field maps to these |
| Choosing Scope one-liners ("Entities/boundaries → thing, struct") | See Finding 4; deferred to future ADR |
| Choosing Form partial list | See Finding 4; deferred to future ADR |

---

## Decision

Apply three targeted changes to move hardcoded token-specific guidance into the SSOT:

### Change 1: `max` + `grow` guidance → `AXIS_KEY_TO_GUIDANCE`

Add to `lib/axisConfig.py`:

```python
AXIS_KEY_TO_GUIDANCE["completeness"]["max"] = (
    "Contradicts grow method: max = exhaust all coverage; grow = expand only under "
    "demonstrated necessity. Avoid pairing max + grow. Prefer max for exhaustive treatment; "
    "prefer grow for disciplined minimalism."
)

AXIS_KEY_TO_GUIDANCE["method"]["grow"] = (
    "Contradicts max completeness: grow = expand only when necessity is demonstrated; "
    "max = exhaust all coverage. Avoid pairing grow + max. Prefer grow for disciplined "
    "minimalism; prefer max for exhaustive treatment."
)
```

Remove from `renderTokenSelectionHeuristics` in `help_llm.go`:

```go
// REMOVE this block:
fmt.Fprintf(w, "**Completeness × Method compatibility:**\n")
fmt.Fprintf(w, "- `max` ... + `grow` ... send contradictory signals. ...\n\n")
```

The guidance will now render via the existing "Guidance for specific tokens (from axis configuration)" block in `renderCompositionRules`, which already iterates `AXIS_KEY_TO_GUIDANCE` for all axes.

### Change 2: Channel × audience incompatibility → `AXIS_KEY_TO_GUIDANCE`

Add to `lib/axisConfig.py` `AXIS_KEY_TO_GUIDANCE["channel"]`:

```python
"code": (
    "... (existing text) ... "
    "Audience incompatibility: avoid with non-technical audiences "
    "(to-CEO, to-managers, to-stakeholders, to-team). Prefer diagram, presenterm, "
    "sketch, or plain for non-technical audiences."
),
"shellscript": (
    "... (existing text) ... "
    "Audience incompatibility: avoid with non-technical audiences "
    "(to-CEO, to-managers, to-stakeholders, to-team)."
),
"codetour": (
    "... (existing text — already documents developer audience requirement) ..."
    # Note: codetour guidance already says "Avoid with manager, PM, executive, CEO,
    # stakeholder, analyst, or designer audiences." — confirm this covers the rule.
),
```

Remove the "Channel × audience compatibility" bullet from `renderTokenSelectionHeuristics`. The guidance will render via "Guidance for specific tokens."

Note: `codetour` already has audience guidance in its `AXIS_KEY_TO_GUIDANCE` entry — verify it covers non-technical audiences before adding a redundant note.

### Change 3: Remove hardcoded "Choosing intent=" line

Remove from `renderTokenSelectionHeuristics` in `help_llm.go`:

```go
// REMOVE this line:
fmt.Fprintf(w, "- **Choosing intent=**: use when the framing purpose matters — ...")
```

The complete per-token use_when entries in `PERSONA_KEY_TO_USE_WHEN["intent"]` already render in the Token Catalog Persona table. No replacement needed.

---

## Implementation Order

### Phase 1 — SSOT violations (this ADR)

1. **Change 3** (remove "Choosing intent=" line) — zero-risk deletion; Token Catalog already covers it
2. **Change 1** (`max`/`grow` guidance) — add to SSOT, remove hardcoded block, regenerate grammar
3. **Change 2** (channel × audience) — audit existing `codetour` guidance, add to `code`/`shellscript`, remove hardcoded block, regenerate grammar

After all three changes: run `make bar-grammar-update` and `go test ./...`.

### Phase 2 — Routing concept metadata (future ADR)

Design and implement `AXIS_KEY_TO_ROUTING_CONCEPT` (Finding 4, Option B) when a concrete consumer beyond `help_llm.go` emerges (e.g., TUI2 hover, SPA chip tooltip). Prerequisite: at least one non-help-llm surface that would render routing concept data.

---

## Consequences

### Positive

- Single source of truth: token guidance lives entirely in `axisConfig.py`/`personaConfig.py`
- New tokens automatically appear in the right `help llm` sections without requiring `help_llm.go` edits
- Guidance is available to all metadata consumers (SPA, TUI2, future tooling), not just `bar help llm`
- Eliminates staleness risk for the "Choosing intent=" line as intent tokens evolve

### Negative / Tradeoffs

- The "Guidance for specific tokens" section in `renderCompositionRules` renders all guidance alphabetically per axis — the `max`/`grow` tension note will no longer appear in the Choosing Method section where a user actively selects tokens. It will appear under Composition Rules > Token Guidance > Completeness and Method. This is less discoverable at selection time.
- **Mitigation:** Add a cross-reference pointer in Choosing Method: "See Completeness × Method compatibility in Token Guidance below."

### Risks

- If `AXIS_KEY_TO_GUIDANCE` rendering order changes, the placement of the moved guidance could shift.
- The `codetour` guidance already partially covers audience incompatibility — adding a redundant note risks inconsistency. Must audit the existing text before adding.

---

## Validation

```bash
# After applying changes:
make bar-grammar-update
go test ./...

# Verify guidance appears in correct section
bar help llm | grep -A 3 "max\|grow\|code.*audience\|codetour.*audience"

# Verify "Choosing intent=" line is gone from heuristics
bar help llm | grep "Choosing intent"  # should return nothing

# Verify Token Catalog still shows intent use_when
bar help llm | grep -A 2 "intent=inform"  # should still appear in Token Catalog
```
