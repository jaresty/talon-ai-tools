# ADR-0234: bar lookup --subject / --addendum Contextual Reranking

**Status**: Proposed
**Date**: 2026-04-24

---

## Context

`bar lookup <query>` currently runs two passes:

1. **Tier pass** — AND-matches query words against token name, heuristics, distinctions,
   definition. Tier 3 = exact name/heuristic match; 2 = substring; 1 = distinction; 0 =
   definition. Results sorted tier desc then axis:token asc.
2. **BM25 backfill** — scores all tokens against the same query; tokens not already in tier
   results fill remaining slots up to cap of 10.

The query is a specificity lens: "I think I want `show` — find me `show`-like tokens." But
there is no way to express contextual intent — what the user is actually trying to do — to
influence ranking. A user explaining authentication code to a manager has no way to signal
that context to `bar lookup`.

ADR-0233 added BM25-driven chip dimming to the SPA using subject+addendum as the query signal.
This ADR extends the same idea to the CLI.

---

## Problem Statement

Two workflows that the current lookup cannot address well:

1. **Confirmation** — "I think I want `show` — does it fit my task of explaining auth code to
   my manager?" The query finds `show` but gives no confidence signal relative to the context.

2. **Discovery** — "I have a subject and addendum but don't know which tokens to pick."
   Currently requires guessing query words. `bar lookup --subject "..." --addendum "..."` with
   no positional query would return BM25-ranked tokens across all axes using the full context
   as the search signal.

---

## Decision

Add `--subject` and `--addendum` flags to `bar lookup`. They interact with the positional
query as follows:

### Mode A: Confirmation (positional query present)

The positional query still drives tier matching and the BM25 backfill exactly as today.
`--subject`/`--addendum` contribute a **secondary BM25 score** computed against the full
`subject + " " + addendum` string. This score reranks results *within* each tier group —
tokens that match both the query and the context float above tokens that match the query alone.

Tier ordering is preserved (tier 3 always beats tier 2, etc.), but within a tier the secondary
BM25 score is the tiebreaker instead of the current alphabetical axis:token sort.

This answers "does this token fit my context?" without changing which tokens are candidates.

### Mode B: Discovery (no positional query)

When `--subject` or `--addendum` is provided but no positional query is given, the tier pass
is skipped entirely. The combined `subject + " " + addendum` string is used as the BM25 query
across all tokens (respecting `--axis` filter if present). Results are ranked by BM25 score
desc, capped at 10.

This is the CLI analog of ADR-0233's chip dimming: same BM25 engine, same signal source,
returned as a ranked list rather than visual opacity.

### Flag semantics

```
bar lookup [<query>] [--axis AXIS] [--subject TEXT] [--addendum TEXT] [--json]
```

- `--subject` and `--addendum` are both optional and independent; either or both may be given
- When combined with a positional query → Mode A (rerank within tiers)
- When no positional query → Mode B (BM25 discovery)
- `--axis` continues to filter results in both modes
- `--json` output gains a `context_score` field (float64) on each result when
  `--subject`/`--addendum` are present; 0 if the token had no contextual score

---

## Implementation Plan

**`internal/barcli/lookup.go`**

- Add `LookupOptions` struct (or extend `LookupTokens` signature) with `Subject`, `Addendum`
  string fields
- Mode A: after tier + BM25 backfill, if subject/addendum non-empty, compute secondary BM25
  scores and use them as tiebreaker within each tier group
- Mode B: if no positional query and subject/addendum non-empty, skip tier pass; run BM25
  directly on `subject + " " + addendum`; return top 10 by score
- `LookupResult` gains `ContextScore float64` field

**`internal/barcli/lookup_cmd.go`** (or wherever the CLI surface lives)

- Add `--subject` and `--addendum` flag parsing
- Wire into `LookupTokens` call

**`internal/barcli/lookup_test.go`**
- Mode A: results with matching context float above results without, within same tier
- Mode B: no query + subject → BM25 discovery results; no query + no subject → existing
  error behavior unchanged
- `--axis` filter applies in both modes

---

## Consequences

**Positive**:
- Lookup becomes useful for discovery, not just name-lookup
- Context signal reuses the BM25 engine already in place — no new infrastructure
- `--subject`/`--addendum` flags mirror `bar build`'s flags — consistent CLI surface
- Backwards-compatible: omitting the new flags preserves existing behavior exactly

**Neutral**:
- Mode B with no axis filter can return noisy results for short/generic subjects; users can
  scope with `--axis`

**Negative / risks**:
- Mode A reranking within tiers may surprise users who expect alphabetical ordering; mitigated
  by `context_score` in JSON output making the reranking transparent

---

## Scope

- `bar lookup` CLI command only
- BM25 contextual reranking within tier groups (Mode A)
- BM25 discovery mode when no positional query (Mode B)

Out of scope:
- SPA changes (ADR-0233 already covers the SPA)
- Suppression/filtering of zero-context-score results (may be a future `--filter` flag)
- `bar help` or `bar suggest` changes

---

## Related

- ADR-0233: SPA BM25 Token Suggestion via Subject/Addendum
- ADR-0163: bar lookup command (original)
- ADR-0232: BM25 ranking for token filter (BM25 engine)
- `internal/barcli/lookup.go` — existing implementation
- `internal/barcli/bm25.go` — existing BM25 engine
