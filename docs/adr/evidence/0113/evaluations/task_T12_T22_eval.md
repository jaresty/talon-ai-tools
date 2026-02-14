# Tasks T12 + T22 — Undiscoverable tokens: inversion and actors

---

## Task T12 — Evaluate architecture against known failure patterns

**Task description:** "Evaluate this microservices design for split-brain, cascade failure, and thundering herd patterns"
**Probability weight:** 4%
**Domain:** analysis

### Skill selection log

Bar-autopilot consults usage patterns:

> **Risk Assessment**: `bar build probe fail full adversarial checklist`

- Task: `probe`
- Scope: `fail`
- Method: `adversarial` (from usage pattern; stress-test for weaknesses)
- Form: `checklist`

**Bar command (autopilot):** `bar build probe full fail adversarial checklist`

**Better command:** `bar build probe full fail inversion adversarial checklist`

### Why inversion is better here

The `inversion` method description: "The response enhances the task by beginning from
undesirable or catastrophic outcomes, asking what would produce or amplify them, then
working backward to avoid, mitigate, or design around those paths."

This is precisely the mental model for architecture evaluation against failure patterns:
start from the known failure (split-brain, cascade failure) and ask "what architectural
choices create or amplify this?" Then evaluate the proposed design against that.

`adversarial` is more general (stress-test for any weakness); `inversion` is specifically
the backward-from-catastrophe method that architecture review against failure patterns
demands.

The skill doesn't surface `inversion` for architecture evaluation because:
1. The heuristics list `inversion` under "Diagnostic Methods: Root cause analysis → diagnose, inversion, adversarial"
2. Architecture evaluation against known failure patterns is not listed as a use case for inversion
3. The skill routes to the generic "Risk Assessment" pattern using `adversarial`

### Coverage scores
- Token fitness: 4 (adversarial is useful but inversion is more specific)
- Token completeness: 4 (inversion is missing from the autopilot selection)
- Skill correctness: 3 (skill doesn't connect architecture evaluation to inversion method)
- Prompt clarity: 4 (adversarial still produces a useful risk-checking prompt)
- **Overall: 4** (still above threshold but with a specific method gap)

### Gap diagnosis

```yaml
gap_type: undiscoverable-token
task: T12 — Evaluate architecture against known failure patterns
dimension: method
observation: >
  The 'inversion' method ("beginning from undesirable or catastrophic outcomes,
  asking what would produce or amplify them, then working backward") is precisely
  the right analytical approach for evaluating architecture against known failure
  modes (split-brain, cascade failure, thundering herd, etc.).

  The user has named the failure modes. The architectural review question is:
  "which design choices in this proposal create or amplify each of these failure modes?"
  This is inversion: start from the catastrophic outcome, work backward.

  Bar-autopilot's heuristics list inversion under "Root cause analysis" diagnostics,
  but don't mention architecture evaluation. The skill routes this task to the generic
  risk assessment pattern (probe+fail+adversarial), which is good but misses the
  richer inversion-based backward reasoning.

recommendation:
  action: edit
  token: inversion
  axis: method
  proposed_addition: >
    Well-suited for architecture evaluation: starting from known failure modes
    (cascade failure, split-brain, thundering herd, data loss scenarios) and asking
    which design choices create or amplify them. Use when the failure patterns are
    named and the question is whether the architecture protects against them.

    Example: evaluating a microservices design against cascade failure by starting
    from the cascade outcome and working backward to identify which service boundaries,
    timeouts, or retry policies produce or prevent it.
evidence: [T12]
```

---

## Task T22 — Security threat modelling

**Task description:** "Perform threat modelling on the file upload service"
**Probability weight:** 2%
**Domain:** analysis

### Skill selection log

- Task: `probe`
- Scope: `fail` (security failures)
- Method: `adversarial` (stress-test for weaknesses)
- Form: `checklist`

**Bar command (autopilot):** `bar build probe full fail adversarial checklist`

**Better command:** `bar build probe full fail adversarial actors checklist`

### Why actors is relevant

The `actors` method description (from bar help llm Token Catalog):
"The response enhances the task by focusing on the entities involved in the subject—who they
are, what motivates them, and how their roles and goals interact."

Threat modelling is explicitly actor-centric: threat actors (attackers, insider threats,
external APIs, malicious users) are first-class citizens of the analysis. A threat model
that doesn't identify who the threat actors are and what they want is incomplete.

The `actors` method exists and would directly improve threat modelling prompts by directing
the LLM to enumerate and reason about threat actors. But bar-autopilot doesn't surface
`actors` for security tasks because:
1. The method description focuses on "entities, motivations, roles" without mentioning security/threats
2. No usage pattern connects threat modelling to the actors method
3. The skill routes security tasks to the generic adversarial pattern

### Coverage scores
- Token fitness: 3 (probe+fail+adversarial misses the actor dimension of threat modelling)
- Token completeness: 3 (actors method is absent from selection)
- Skill correctness: 3 (skill doesn't connect threat modelling to actors method)
- Prompt clarity: 4 (adversarial still produces a useful security prompt)
- **Overall: 3**

### Gap diagnosis

```yaml
gap_type: undiscoverable-token
task: T22 — Security threat modelling
dimension: method
observation: >
  The 'actors' method ("focusing on the entities involved — who they are, what
  motivates them, and how their roles and goals interact") directly maps to the
  threat actors concept in security threat modelling.

  A threat model is fundamentally actor-centric: who are the attackers, what do
  they want, what access do they have, what can they do? The actors method exists
  to surface exactly this kind of entity-and-motivation analysis, but its description
  doesn't mention security or threat actors as a use case.

  Bar-autopilot selects adversarial for security tasks (systematic stress-test for
  weaknesses) but omits actors. The result is a prompt that finds weaknesses
  without reasoning about who would exploit them or why — a structurally incomplete
  threat model.

recommendation:
  action: edit
  token: actors
  axis: method
  proposed_addition: >
    Well-suited for security threat modelling: identifying threat actors (external
    attackers, insiders, automated bots, compromised dependencies), their motivations
    (data theft, service disruption, privilege escalation), and how their capabilities
    interact with system attack surfaces. Use alongside 'adversarial' for a complete
    threat model that covers both what can be attacked and who would attack it.
evidence: [T22]
```
