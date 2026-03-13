# ADR-0113 Loop-26: ADR-0160 New Token Discoverability
**Date:** 2026-03-13
**Bar version:** 2.102.0 (dev build /tmp/bar-new; installed 2.102.0)
**Trigger:** ADR-0160 added 11 new tokens since loop-25 (2026-03-08):
  - Method: enforce, observe, ritual, yield, mark, ground (reworked)
  - Form: timeline, coupling, twin, prep, vet, ghost
  - Scope: dam (tested in ADR-0085 cycle-21 — adequate)
**Pre-eval finding:** timeline/coupling/twin/prep/vet have zero AXIS_TOKEN_METADATA["form"] entries — Gap Type 1 confirmed before first task.

---

## Calibration

Single-evaluator. Using established boundary rationale from loop-25. Within-evaluator max delta ≤ 1.

---

## Task Evaluation

| Task | Autopilot Selection | Correct Selection | Gap | Score | Notes |
|------|---------------------|-------------------|-----|-------|-------|
| T01: "show the deployment history as a timeline" | `show time trace walkthrough` | `show time trace timeline` | Type 1 | 3 | `timeline` absent from AXIS_TOKEN_METADATA["form"] and routing concept map — completely invisible |
| T02: "map out the coupling between these services" | `probe struct mapping snag` | `probe struct mapping snag coupling` | Type 2 | 3 | `coupling` visible in "Choosing Form" but no heuristics; method tokens capture signal, form missed |
| T03: "compare option A and option B side by side" | `diff compare table` | `diff compare twin` | Type 2 | 3 | `twin` visible in "Choosing Form" but no heuristics; `table` ("tabular comparison") selected instead |
| T04: "design an experiment to test whether our caching strategy is working" | `make experimental` | `make experimental prep` | Type 2 | 3 | `prep` visible in "Choosing Form" but no heuristics; `experimental` method captures signal; form missed |
| T05: "review the results of our load test against what we predicted" | `check compare` | `check compare vet` | Type 1 | 2 | `vet` is the primary value of the selection; no heuristics; completely missed |
| T06: "write the tests first before you implement the feature" | `make ground` | `make ground` | Type 4 | 4 | `ground` discoverable via token catalog heuristics; not listed in "Choosing Method" bullets; `enforce` as complement missed |
| T07: "run the existing tests and tell me what you observe" | `check observe` | `check observe` | None | 5 | `observe` heuristics precisely match; clean routing |
| T08: "structure this process according to established team roles and procedures" | `fix actors` | `fix ritual` | Type 1 | 2 | `ritual` absent from AXIS_KEY_TO_ROUTING_CONCEPT["method"] and "Choosing Method" bullets |
| T09: "let the design emerge — minimal intervention, just guide it gently" | `probe` (no method) | `probe yield` | Type 1 | 2 | `yield` absent from AXIS_KEY_TO_ROUTING_CONCEPT["method"] and "Choosing Method" bullets |
| T10: "quickly probe what assumptions we're making about our API users" | `probe assume gap` (omitting skim) | `probe skim assume gap` | Type 3 | 4 | Choosing Completeness guidance discourages `skim` for `probe`; conflicts with user's explicit "quickly" |
| T11: "give me a brief simulation of what happens if we migrate to Kubernetes" | `sim migrate` (without gist) | `sim gist migrate` | Type 3 | 3 | Choosing Completeness guidance actively conflicts with user's explicit "brief" signal |
| T12: "extract the risk items from this architecture review document" | `pull fail risks` | `pull fail risks` | None | 5 | All tokens precise heuristic matches; clean routing |

**Mean: 3.25/5** (lowest since loop-16; 3 score-2 gaps, 5 score-3 gaps, 2 score-5 controls)

---

## Gap Summary

| ID | Token | Axis | Gap Type | Score | Root Cause |
|----|-------|------|----------|-------|------------|
| G-L26-01 | `vet` | form | Type 1 | 2 | No AXIS_TOKEN_METADATA["form"] entry; no heuristics |
| G-L26-02 | `ritual` | method | Type 1 | 2 | Has heuristics but absent from AXIS_KEY_TO_ROUTING_CONCEPT["method"] and "Choosing Method" bullets |
| G-L26-03 | `yield` | method | Type 1 | 2 | Has heuristics but absent from AXIS_KEY_TO_ROUTING_CONCEPT["method"] and "Choosing Method" bullets |
| G-L26-04 | `timeline` | form | Type 1 | 3 | Completely absent from AXIS_TOKEN_METADATA["form"] AND routing concept map |
| G-L26-05 | `twin` | form | Type 2 | 3 | Routing concept visible; no heuristics; `table` selected instead |
| G-L26-06 | `prep` | form | Type 2 | 3 | Routing concept visible; no heuristics; `experimental` method captures signal; form missed |
| G-L26-07 | `coupling` | form | Type 2 | 3 | Routing concept visible; no heuristics; method tokens capture signal; form missed |
| G-L26-08 | Choosing Completeness | help_llm | Type 3 | 3 | Guidance discourages gist/skim for probe/sim but overrides explicit user brevity signals ("quickly", "brief") |

**Not a gap (confirmed healthy):** observe (T07, 5), pull+fail routing (T12, 5), ground via token catalog heuristics (T06, 4)
