# Task T07 — Identify cross-cutting concerns in a codebase

**Task description:** "Where are observability concerns handled inconsistently across our services?"
**Probability weight:** 5%
**Domain:** code

## Skill selection log

- Task: `probe` (surface structure and patterns)
- Completeness: `full`
- Scope considered: `struct` (arrangements/dependencies), `motifs` (recurring patterns)
  → chose: `struct motifs` (two scopes: structural organization + recurring patterns)
- Method: `systemic` (reason about the whole, components, flows, feedback loops)
  → also considered `mapping` (spatial map of relationships)
- Form: none selected (mapping is a method here, not a form)
- Channel: none

**Bar command constructed:** `bar build probe full struct motifs systemic`

**Bar output:**
- Scope ("struct"): focuses on arrangements, dependencies, organizing patterns
- Scope ("motifs"): identifies recurring patterns, themes, clusters
- Method ("systemic"): reasons about the subject as an interacting whole

## Coverage scores

- Token fitness: 3
- Token completeness: 3
- Skill correctness: 3
- Prompt clarity: 3
- **Overall: 3**

## Gap diagnosis

```yaml
gap_type: missing-token
task: T07 — Identify cross-cutting concerns in a codebase
dimension: scope
observation: >
  No scope token specifically foregrounds cross-cutting concerns as a distinct
  structural lens. Cross-cutting concerns (logging, authentication, error handling,
  observability, caching) are characterized by spanning multiple modules — they exist
  as a repeated concern that cuts horizontally across vertical module boundaries.

  'struct' focuses on "arrangements or related dependencies, coordination, constraints"
  — this is about the structure within a module or between modules, not about concerns
  that are applied repeatedly everywhere.

  'motifs' focuses on "recurring patterns, themes, or clusters" — this is closer but
  "motifs" implies optional/stylistic patterns, not mandatory cross-cutting concerns.
  Cross-cutting concerns are not just patterns; they're structural obligations.

  The combination struct+motifs+systemic gets close: it asks for a systemic analysis
  of structural patterns. But the prompt does not direct the LLM toward the specific
  question: "which concerns are handled inconsistently or in multiple places, and
  what are the module-boundary implications?"

  The user wants an answer to: "Where is X concern handled? How consistently? What
  modules own it?" No single token or combination precisely expresses this lens.
recommendation:
  action: add
  axis: scope
  proposed_token: "cross"
  proposed_description: >
    The response focuses on concerns that span multiple modules or components —
    patterns applied repeatedly across the codebase (logging, error handling,
    authentication, observability, caching) — examining their consistency,
    distribution, and coupling characteristics. Use when the question is about
    where a concern lives across the system, not just within one place.
evidence: [T07]
```

## Notes

The combination `probe full struct motifs systemic` produces a reasonable prompt but is
semantically imprecise. An LLM using this bar output would analyze structural patterns and
systemic interactions, but not necessarily focus on the horizontal cross-cutting nature of
the concerns. A dedicated `cross` scope token would precisely target this analysis mode.

The absence of this token means users must either use the imprecise struct+motifs combination
or add ADDENDUM text to refine the scope — which defeats the purpose of having a scope axis.
