# ADR-0152 – Token Description Spill Reduction

Status: Draft
Date: 2026-03-03
Owners: Architecture Review

## Context

Token descriptions in `lib/axisConfig.py` (`AXIS_KEY_TO_VALUE`) are the
primary behavioral instruction surface passed to the model. A spill analysis
identified that a subset of descriptions have accumulated content that extends
beyond their definitional scope into:

- Policy and ethical framing (verify)
- Methodological prescription exceeding the token's definition (balance)
- A "may not be attributed to X without Y" clause cluster used by formal-discipline
  tokens (afford, polar, trans, canon)
- Cross-axis conditional coupling embedded in prose ("With pull: ...", "With
  make/fix: ...", "Adapts to the channel: ...") across form tokens (contextualise,
  socratic, taxonomy, quiz, facilitate, cocreate)
- Technical safety specification that exceeds description scope but has no
  alternative container (presenterm)

The compound directional tokens (bog, fig, fly bog, etc.) were separately
reviewed and are not spill — their references to component tokens (rog, ong,
fog, dig) are the definition, not imports.

## Problem

Descriptions doing multiple jobs produce two failure modes:

1. **Ambiguity of scope** — a reader cannot tell which part of a description is
   definitional (what the token *is*) versus operational (constraints on how to
   apply it) versus cross-axis guidance (how it interacts with other tokens).

2. **Coupling fragility** — embedding cross-axis interaction in descriptions
   means a change to one token's semantics may silently make another token's
   description stale or wrong.

Five entities are in scope for this ADR, ordered by confidence in the fix:

| Entity | Spill type | Fix confidence |
|--------|------------|---------------|
| `verify` | Policy/ethics language beyond falsification definition | High — non-load-bearing |
| `balance` | Sentences 2–3 are methodology prescription; sentence 1 is definition | High — non-load-bearing |
| `afford`, `polar`, `trans`, `canon` | "May not be attributed to X without Y" cluster; possibly load-bearing for formal-discipline tokens | Medium — requires testing |
| `contextualise`, `socratic`, `taxonomy`, `quiz`, `facilitate`, `cocreate` | Cross-axis conditional coupling ("With X: ...", "Adapts to channel: ...") | Medium — correct home is `CROSS_AXIS_COMPOSITION`; requires migration |
| `presenterm` | 18-line technical specification; content necessary but field inappropriate | Low — blocked on infrastructure (no `notes`/`constraints` field exists) |

## Decision

Three phases, executed as ADR loops:

**Phase 1 — Immediate trims (T-1, T-2)**

Edit `verify` and `balance` in `AXIS_KEY_TO_VALUE`. For `verify`: retain the
falsification definition; remove the authority-transfer and human-oversight
policy language. For `balance`: retain sentence 1 (the definition); remove
sentences 2–3 (operational prescription).

Validation: grammar export passes; a before/after behavioral check confirms the
trimmed descriptions preserve the intended token behavior.

**Phase 2 — Load-bearing test of the "may not" cluster (T-3)**

Before trimming `afford`, `polar`, `trans`, or `canon`, run each against 2–3
representative prompts using both the current and a trimmed description. If
model output quality degrades measurably when the negative constraint is absent,
the clause is load-bearing and should be retained or moved to `use_when`. If
output is equivalent, trim.

Validation: written comparison of before/after outputs for each token; decision
recorded per token.

**Phase 3 — Cross-axis coupling migration (T-4, T-5)**

Evaluate whether `CROSS_AXIS_COMPOSITION` is the right destination for the
cross-axis conditional guidance currently in `contextualise`, `socratic`,
`taxonomy`, `quiz`, `facilitate`, `cocreate`, or whether a dedicated `notes`
field should be added to the token metadata structure.

If `CROSS_AXIS_COMPOSITION` is the destination: populate it for these tokens
and remove the prose from their descriptions. If a `notes` field is added:
define it in `axisConfig.py`, move the overflow content, update the grammar
export pipeline to include it, and trim descriptions. `presenterm` is unblocked
once this infrastructure decision lands.

Validation: descriptions trimmed; guidance present and accessible from its new
location; `bar help llm` output still surfaces the cross-axis guidance.

## Salient Tasks

- **T-1** — Trim `verify`: remove policy/ethics language, retain falsification core
- **T-2** — Trim `balance`: remove sentences 2–3 (prescription), retain sentence 1 (definition)
- **T-3** — Test "may not" cluster: afford, polar, trans, canon before/after comparison; decide per token
- **T-4** — Infrastructure decision: CROSS_AXIS_COMPOSITION migration vs. notes field
- **T-5** — Cross-axis coupling migration for contextualise, socratic, taxonomy, quiz, facilitate, cocreate (and unblock presenterm)

## Risks

| Risk | Mitigation |
|------|------------|
| Trimming load-bearing language degrades model output quality | Phase 2 testing gates the decision for the "may not" cluster |
| Cross-axis guidance lost when removed from descriptions | Phase 3 requires guidance to be accessible from its new location before descriptions are trimmed; validated via `bar help llm` |
| `notes` field added but not surfaced in UI/help | Grammar export pipeline and `bar help llm` updated as part of T-5 |
| Presenterm technical constraints cause output errors after trim | Presenterm trim is blocked until T-4 lands an infrastructure solution |

## Metadata

Analyzed: 2026-03-03
Method: Spill analysis via bar prompt (scope:thing, method:robust+spill)
Scope: lib/axisConfig.py AXIS_KEY_TO_VALUE descriptions
