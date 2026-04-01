# Generalized Ground Protocol — Quick Reference

> **The Protocol is a discipline against self-deception.**
> It prevents "I think it works" from replacing "I proved it works."

## The 7-Step Ladder

| # | Rung | Question | Derivation Prompt |
|---|------|----------|-------------------|
| 1 | Intent | What outcome is being aimed for? | "From the task, derive the specific outcome being pursued" |
| 2 | Criteria | What conditions must be true for success? | "From the intent, derive the conditions that would verify success" |
| 3 | Structure | How is the solution organized? | "From the criteria, derive the organization needed to satisfy them" |
| 4 | Baseline | Does a minimal version exist? | "From the structure, derive a minimal artifact that demonstrates the approach" |
| 5 | Challenge | What checks expose gaps? | "From the baseline, derive checks that would fail if gaps exist" |
| 6 | Refinement | How is the artifact improved? | "From the challenge, derive targeted changes that address each gap" |
| 7 | Verification | How is completion confirmed? | "From the refinement, derive confirmation that no new gaps remain" |

## The Derivation Rule

**Each artifact must cite its source from the previous rung.**

```
Step N: [Artifact]
Source: [Specific content from Step N-1]
```

## Domain-Specific Evidence Authorities

| Domain | Authority | Evidence Form |
|--------|-----------|---------------|
| Software | Automated tests | Pass/fail results |
| Writing | Peer review | Feedback on clarity |
| Decision-making | Stakeholders | Consensus or concerns |
| Learning | Assessment | Test scores or application |
| Design | Users | Feedback or usage data |

## Terminology Mapping

| Software Term | Generalized Concept |
|--------------|---------------------|
| File | Artifact (any tangible output) |
| Stub | Placeholder / Scaffold |
| Test | Check / Evaluation criterion |
| Assertion | Explicit expectation |
| Implementation | Refinement / Realization |
| Pass/Fail | Satisfies / Does not satisfy |

## Quick Start

1. **State the task** → Intent
2. **Define success** → Criteria
3. **Organize the approach** → Structure
4. **Produce minimal artifact** → Baseline
5. **Find gaps** → Challenge
6. **Improve** → Refinement
7. **Verify completion** → Verification

---

*Derived from ADR-0220: Generalizing the Ground Protocol Beyond Software Contexts*
