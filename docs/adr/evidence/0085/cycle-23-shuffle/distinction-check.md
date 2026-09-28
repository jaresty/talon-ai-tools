# Cycle 23 — Phase 2e Distinction Check

## Candidate 1: pull × deep (completeness vs task operation tension)

Not a same-axis redundancy pair — this is a task×completeness *operational* tension
(pull compresses; deep unpacks), not two interchangeable tokens. Phase 2e compare mode tests
redundancy between *same-role* tokens. This tension is better recorded as a cross-axis
observation than as a retire candidate. **No retire recommendation drafted.** Recorded as a
cautionary/help-llm candidate instead.

## Candidate 2: paradox × fix (method category vs transformation task)

**Compare-mode command:**
`bar build probe method=paradox,converge --subject "reformat this onboarding doc into a checklist"`

(Note: probe substitutes the task in compare mode; the real seed used `fix`. The comparison
still isolates the method-token distinction, which is the variable under test.)

**Distinction judgment (LLM-evaluated, single-evaluator):**

- `paradox` on a reformat/transformation subject: paradox's Description forbids synthesis,
  resolution, and explanation as closing moves. A reformat task's entire purpose is a
  resolved, meaning-preserving transformation. paradox applied here can only produce a
  meta-commentary ("this doc's structure resists being made into a linear checklist because
  onboarding is non-linear") rather than the requested checklist. The output is
  **distinguishable** from `converge` (which would just produce the checklist) — but it is
  distinguishable by *refusing the task*, not by doing it differently.

- **Result: `distinguishable` — but asymmetric in usefulness for transformation tasks.**
  paradox is not redundant with any other method (it has a unique, well-defined stance); it is
  simply *mismatched* to convergent production tasks (fix/make). This is a **category-fit**
  issue, not a redundancy/retire issue.

**Conclusion:** No retire recommendation. paradox is a valid, distinguishable, non-redundant
method token. The cycle-23 finding is that paradox (and Exploration/Diagnostic-tension methods
generally) should not be routed to transformation tasks (fix/make/prune) — a **skill-guidance
/ help-llm** matter, not a catalog defect. Recorded as skill-update candidate in
recommendations.yaml.

**Limitation:** single subject, single evaluator, compare prompt not actually executed by a
fresh model. Per Phase 2e, ≥3 subjects are needed before concluding indistinguishability —
but since the conclusion here is *distinguishable* (not a retire), the bar is met: one clear
distinguishing case suffices to retain both tokens.
