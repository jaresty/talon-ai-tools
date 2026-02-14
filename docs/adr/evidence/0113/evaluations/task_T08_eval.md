# Task T08 — Risk summary for a release or architectural decision

**Task description:** "What are the risks of deploying this service on Friday?"
**Probability weight:** 5%
**Domain:** analysis

## Skill selection log

Bar-autopilot consulting `bar help llm` Usage Patterns section sees:

> **Risk Assessment**: Use for identifying and evaluating potential risks
> Pattern: `bar build probe fail full adversarial checklist`

- Task: `probe` — selected from usage pattern (risk assessment)
- Completeness: `full`
- Scope: `fail` — selected from usage pattern
- Method: `adversarial` — selected from usage pattern
- Form: `checklist` — selected from usage pattern

**Bar command constructed (by bar-autopilot):** `bar build probe full fail adversarial checklist`

**Better command (manual analysis):** `bar build pull full fail risks checklist`

**Difference:**
- `probe` = "analyzes the subject to surface structure, assumptions, implications beyond restatement"
- `pull` = "extracts a targeted subset of the input for inspection, filtering, or reuse"
- `adversarial` = "stress-tests, searching for weaknesses, edge cases, counterexamples"
- `risks` = "focuses on potential problems, failure modes, or negative outcomes and likelihood"

For "what are the risks of X?", the user wants an **extraction** task (extract the risk
subset from the overall picture), not an open-ended analysis of the subject. `pull+fail+risks`
more precisely instructs the LLM: "extract [pull] the failure-related [fail] risks [risks method]."

`probe+fail+adversarial` is a valid risk analysis pattern but it's broader — it's an analysis
that incidentally surfaces risks rather than directly extracting them.

## Coverage scores

- Token fitness: 3 (probe is functional but imprecise; pull+risks is sharper)
- Token completeness: 4 (fail scope is correct)
- Skill correctness: 3 (usage pattern actively misroutes to probe)
- Prompt clarity: 4 (probe+adversarial still produces a useful risk prompt)
- **Overall: 3**

## Gap diagnosis

```yaml
gap_type: skill-guidance-wrong
task: T08 — Risk summary for a release/decision
dimension: task selection
observation: >
  The "Risk Assessment" usage pattern in bar help llm defaults to 'probe' for any
  risk-related task. However, "produce a risk summary" is an extraction task — the
  user wants to pull out a specific subset (risks) from a subject, not analyze the
  subject broadly.

  'pull' task ("extracts a targeted subset for inspection, filtering, or reuse") is
  more semantically precise for "what are the risks?" questions. 'risks' method
  ("focuses on potential problems, failure modes, negative outcomes and their
  likelihood or severity") reinforces this: combined as pull+fail+risks, the prompt
  says "extract the risk subset, focused on failure dimension, enumerating risks."

  The usage pattern's choice of 'probe' as the universal risk task causes
  bar-autopilot to select a broader analysis pattern when an extraction pattern is
  more appropriate.

  Both patterns produce useful outputs, but the distinction matters when the user
  wants a focused risk register, not a broad analysis-with-risk-observations.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  target: "Risk Assessment pattern"
  proposed_addition: >
    Distinguish two risk task subtypes:
    - Risk extraction ("what are the risks?", "list risks", "risk summary"):
      prefer 'pull + fail + risks checklist'. The user wants the risk subset extracted.
    - Risk analysis ("how risky is this?", "assess risk posture", "analyse failure modes"):
      prefer 'probe + fail + adversarial'. The user wants open-ended analysis.
    Reserve 'probe' for the analytical form; use 'pull' when a bounded risk list
    or summary is the deliverable.
evidence: [T08]
```

## Notes

This gap was anticipated in the ADR template as a concrete example (gap type 3, T19 in the
template). The actual finding confirms the prediction: the risk assessment usage pattern
routes everything to `probe`, but extraction tasks should use `pull`.

The `risks` method token exists and is well-described ("focuses on potential problems,
failure modes, or negative outcomes and their likelihood or severity") but is not shown in
the usage patterns section for risk assessment. It should be prominently featured there.
