# ADR-0233: SPA BM25 Token Suggestion via Subject/Addendum

**Status**: Proposed
**Date**: 2026-04-24

---

## Context

The SPA token selector requires users to know which tokens exist and manually browse axes to find
relevant ones. The BM25 ranking engine already exists in `web/src/lib/bm25.ts` (ported from the
CLI) and indexes token descriptions, definitions, heuristics, and distinctions.

The subject and addendum fields capture the user's intent in natural language before they pick
any tokens. This text is the ideal query source for surfacing relevant tokens.

---

## Problem Statement

Users starting from a blank state must browse all axes to find tokens that fit their task.
There is no affordance that says "given what you've typed, these tokens are likely relevant."
The BM25 engine exists but is only used for the filter input in `TokenSelector`.

---

## Decision

Use the subject and addendum fields as a live BM25 query. When non-empty, tokens that score
below a relevance threshold are dimmed (reduced opacity) across all axis chip grids. Tokens
that score above threshold remain at full opacity.

### Behavior

- BM25 scores are computed reactively from `subject + ' ' + addendum`
- Scores are computed across all tokens from all axes simultaneously
- Tokens with a score above a threshold render at full opacity
- Tokens with zero score (no match) render at reduced opacity (e.g. 35%)
- When subject and addendum are both empty, no dimming is applied — all tokens at full opacity
- Already-selected tokens are never dimmed regardless of score
- The effect is purely visual — no tokens are hidden or removed

### Why dim rather than highlight

Dimming unmatched tokens directs the eye to relevant tokens without adding decoration to chips.
It degrades gracefully: empty subject = no effect. It also avoids the visual ambiguity of
"highlighted = selected" that a positive highlight treatment would create.

---

## Implementation Plan

**`web/src/routes/+page.svelte`**
- Derive `bm25Scores: Map<string, number>` reactively from subject + addendum using
  `bm25Score(allTokens, query)` — recompute when either field changes
- Pass scores down to `TokenSelector` as a new optional prop `suggestionScores`

**`web/src/lib/TokenSelector.svelte`**
- Accept `suggestionScores?: Map<string, number>` prop
- When prop is present and non-empty, apply `opacity: 0.35` to chip wrappers whose token
  name has a zero score; leave all others at full opacity
- Selected chips are exempt from dimming

**`web/src/lib/bm25.ts`**
- No changes required — `bm25Score(tokens, query)` already accepts a flat token list and
  returns a Map

---

## Consequences

**Positive**:
- Zero friction — suggestion activates as a side effect of normal use
- No new UI surface, no modal, no button
- Works offline, no API calls
- BM25 engine is already battle-tested (ported from CLI, has tests)

**Neutral**:
- BM25 keyword matching will miss semantic relationships (e.g. "manager" won't match
  `audience=to-manager` unless heuristics include that word)
- Threshold tuning may be needed; start with any non-zero score as "relevant"

**Negative / risks**:
- Dimming many tokens at once may feel noisy for short/generic subject text
- Mitigation: only activate when subject length exceeds a minimum (e.g. 10 chars)

---

## Scope

- SPA chip grids only (desktop and mobile)
- Subject + addendum as query source only (not the task/persona selectors)
- Visual dimming only — no reordering, no hiding

Out of scope:
- Paste-back LLM suggestion flow (separate ADR if pursued)
- CLI or TUI changes

---

## Related

- `web/src/lib/bm25.ts` — existing BM25 engine
- `web/src/lib/TokenSelector.svelte` — chip grid component
- ADR-0232: SPA Collection Sharing
