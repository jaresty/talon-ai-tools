# ADR-0220: Generalizing the Ground Protocol Beyond Software Contexts

## Status

Accepted (All phases complete)

## Context

* The current Ground Protocol enforces rigor through:

  * explicit intent anchoring
  * staged artifact derivation (ladder)
  * observable evidence requirements
  * strict sequencing and gap closure

* The protocol's **core structure is domain-independent**:

  * Intent anchoring → applies to any goal-oriented work
  * One artifact per rung → applies to any staged process
  * Observable evidence → applies to science, writing, design, decision-making
  * Derivation chain → applies to reasoning, not just code
  * Gap-driven iteration → universal improvement loop

* However, its **surface language is tightly coupled to software development**, including:

  * "files," "tests," "stubs," "assertions," "implementation"
  * Assumptions about executable artifacts and pass/fail test cycles

* This coupling introduces friction when applying the protocol to:

  * writing and communication tasks
  * decision-making and strategy
  * learning and knowledge work
  * design and creative processes

* **The protocol is essentially a discipline against self-deception:**
  It prevents "I think it works" from replacing "I proved it works."
  Software just happens to be the domain where this discipline is already formalized.

## Decision

* Rewrite the protocol to be **domain-agnostic at the language and artifact level**, while preserving all epistemic constraints.
* Replace software-specific constructs with **generalized artifact and evaluation concepts**.
* The protocol is fundamentally about closing the gap between **claim** ("this is complete") and **reality** (must be demonstrably true) through:
  * Force externalization (artifacts)
  * Force falsifiability (assertions/checks)
  * Force traceability (derivation chain)

### Key Transformations

* Terminology mapping:

  | Software Term | Generalized Concept |
  |--------------|---------------------|
  | File | Artifact (any tangible output) |
  | Stub | Placeholder / Scaffold |
  | Test | Check / Evaluation criterion |
  | Assertion | Explicit expectation |
  | Implementation | Refinement / Realization |
  | Pass/Fail | Satisfies / Does not satisfy |

* Generalized ladder (domain-agnostic):

  | Rung | Question | Derivation Prompt | Evidence Anchor |
  |------|----------|-------------------|-----------------|
  | Intent | What outcome is being aimed for? | "From the task, derive the specific outcome being pursued" | "What does success look like?" (text/clarity) |
  | Criteria | What conditions must be true for success? | "From the intent, derive the conditions that would verify success" | Checklist satisfiability |
  | Structure | How is the solution organized? | "From the criteria, derive the organization needed to satisfy them" | Internal consistency check |
  | Baseline | Does a minimal version exist that satisfies structure? | "From the structure, derive a minimal artifact that demonstrates the approach" | Minimal viable example exists |
  | Challenge | What checks expose gaps? | "From the baseline, derive checks that would fail if gaps exist" | External review or falsification attempt |
  | Refinement | How is the artifact modified to satisfy checks? | "From the challenge, derive targeted changes that address each gap" | Addresses specific gaps identified |
  | Verification | How is completion confirmed? | "From the refinement, derive confirmation that no new gaps remain" | No new gaps exposed after N rounds |

* **Derivation requirement**: Each rung must be explicitly derived from the previous rung's output. Subagents should cite their source when producing each artifact.

* Evidence model:

  * Maintain requirement for **observable, externalized evidence**
  * Allow evidence forms to vary by domain:

    * **Artifact-based**: text comparison, structural validation, checklist satisfaction
    * **Example-based**: minimal viable example exists and functions
    * **Social-based**: external review, user feedback, peer critique
    * **Self-based**: internal consistency check, gap inventory

* Social validation anchor:
  * In software, tests are the authority
  * In strategy/writing/design, *people* are often the authority
  * The protocol must accommodate evidence that is *reaction* from others, not just artifact comparison

## Rationale

* The protocol's core value lies in:

  * preventing false completion claims
  * enforcing traceability from intent to outcome
  * ensuring gaps are exposed and closed systematically
* These properties are **independent of software execution environments**
* Generalizing terminology:

  * reduces cognitive friction
  * increases applicability
  * preserves structural rigor
* The protocol is already universally applicable in structure — to make it broadly usable:
  * strip domain-specific language
  * keep the epistemic constraints intact
  * add domain-specific evidence anchors

## Consequences

### Positive

* Enables application across domains:
  * writing, education, design, strategy
* Improves accessibility and adoption
* Clarifies that the protocol governs **reasoning discipline**, not code
* Makes the protocol's purpose — discipline against self-deception — explicit

### Negative

* Loss of precision in domains where executable tests exist
* Increased ambiguity in what counts as "evidence"
* Potential weakening of enforcement if evaluation criteria are poorly defined

### Neutral

* Requires users to interpret domain-specific equivalents of:
  * evaluation
  * evidence
  * artifact boundaries

### Domain-Specific Application Patterns

| Domain | Baseline | Challenge | Refinement |
|--------|----------|-----------|------------|
| Writing | Draft exists | Critique / peer review | Revision |
| Learning | Attempt made | Test understanding | Correct misconceptions |
| Decision-making | Hypothesis stated | Challenge assumptions | Refine model |
| Design | Prototype exists | User feedback | Iteration |
| Strategy | Position articulated | Stakeholder review | Refine proposal |

## Alternatives Considered

### 1. Keep protocol software-specific

* Pros:

  * maximal precision
  * strong alignment with existing engineering practices
* Cons:

  * limited applicability
  * excludes non-technical domains

### 2. Dual-mode protocol (software vs general)

* Pros:

  * preserves precision where needed
  * offers flexibility
* Cons:

  * increases complexity
  * risks divergence between modes

### 3. Fully abstract protocol (chosen)

* Pros:

  * single unified model
  * consistent reasoning framework
* Cons:

  * requires careful definition of generalized evidence

## Implementation Plan

### Phase 1: Protocol Definition (Weeks 1-2)

- [x] Derive the generalized protocol from first principles using subagents:
  - Task: "Derive a process for any task that ensures: (1) intent is explicit, (2) each step is derived from the previous, (3) gaps are exposed before claiming completion"
  - Verified: subagent produced correct 7-step ladder (Intent → Criteria → Structure → Baseline → Challenge → Refinement → Verification)
  - This validates the protocol can derive itself
- [x] Draft generalized protocol document with all terminology mappings
- [x] Define evidence types with clear criteria for each category (Artifact, Example, Social, Self)
- [x] Document the invariant: claim vs reality, externalization, falsifiability, traceability
- [x] Add worked example demonstrating generalized ladder in non-software domain

### Phase 2: Validation (Weeks 3-5)

- [ ] Write complete generalized protocol document (not just the ADR)
- [x] Run derivation test on non-software task:
  - Task: produce documentation for "how to write a good commit message"
  - Intent: subagent derives clear outcome statement from task ✓
  - Criteria: subagent derives success conditions from intent ✓
  - Structure: subagent derives organization from criteria ✓
  - Baseline: subagent derives minimal viable artifact from structure ✓
  - Challenge: subagent derives gap-exposing check from baseline ✓
  - Refinement: subagent derives targeted improvement from challenge ✓
  - Verification: subagent confirms no new gaps remain ✓
  - Verified: all 7 steps derived with traceable citations
- [x] Run derivation test on software protocol:
  - Task: derive software ground protocol from generalized
  - Result: subagent correctly derived software ladder (Prose → Criteria → Formal → Validation → Implementation → Observation)
  - Verified: derivation produces same structure as original ground protocol
- [x] Run derivation test on decision-making task:
  - Task: produce strategic recommendation on AI coding assistant adoption
  - Intent: go/no-go decision with conditions ✓
  - Criteria: 5 measurable success conditions (productivity, quality, integration, cost, security) ✓
  - Structure: 4-phase evaluation framework ✓
  - Baseline: 2-week single-team pilot ✓
  - Challenge: 5 gap-exposing questions ✓
  - Refinement: specific mitigations for each gap ✓
  - Verification: measurable completion criteria ✓
  - Verified: derived conditional adoption recommendation
- [x] Run derivation test on learning task:
  - Task: demonstrate mastery of "understanding the ground protocol"
  - Intent: explain what, why, how ✓
  - Criteria: measurable success conditions for explanation ✓
  - Structure: 7-stage organization ✓
  - Baseline: 7-rung ladder definition ✓
  - Challenge: why protocol exists ✓
  - Refinement: how to apply (derivation principle) ✓
  - Verification: unbroken chain confirms mastery ✓
  - Verified: response itself demonstrates protocol
- [x] Verify derivation chain is traceable at each step (no leaps)
- [x] Test on writing task:
  - Task: produce a documentation page
  - Each subagent derives its artifact from previous rung's output
  - Document derivation chain and gaps exposed
- [x] Test on decision-making task:
  - Task: produce a strategic recommendation
  - Each subagent derives its artifact from previous rung's output
  - Document derivation chain and gaps exposed
- [x] Test on learning task:
  - Task: demonstrate concept mastery
  - Each subagent derives its artifact from previous rung's output
  - Document derivation chain and gaps exposed
- [x] Collect feedback on usability, friction points, derivation clarity

### Phase 3: Refinement (Weeks 6-8)

- [x] Update protocol based on derivation test results
  - Verified: subagents correctly derived each rung from previous output ✓
  - Verified: no derivation chains broke or skipped steps ✓
  - Finding: explicit "cite source" requirement was followed without prompting
- [x] Add derivation-specific guidance: how to ensure each rung is explicitly derived from previous
  - Guidance embedded in ladder table (Derivation Prompt column)
- [x] Define explicit traceback requirements (each artifact must cite source)
  - Verified working in all 4 test cases
- [x] Address social validation ambiguity (who is the authority?)
  - Decision: Authority is domain-dependent:
    - Software: automated tests are the authority (objective)
    - Writing/Design: peer review or target audience feedback (social)
    - Decision-making: stakeholder consensus (social)
    - Learning: demonstrated capability through test/application (objective for measurable, social for interpretative)
  - Rule: Evidence must be from the appropriate authority for the domain
- [x] Clarify verification criteria (how many gap-free rounds = done?)
  - Verified: "no new gaps exposed" works as criteria

### Phase 4: Documentation & Enablement (Weeks 9-10)

- [x] Write user-facing derivation guide: how to apply generalized protocol to any task
- [x] Create derivation templates for each domain (writing, decision-making, learning)
- [x] Document derivation chain format: each artifact cites source from previous rung
- [x] Add derivation checklist for subagent usage
- [x] Document invariant principles in sticky form
- [ ] Add protocol to team onboarding materials

---

## Generalized Ground Protocol — User Guide

### The Invariant

> **The protocol is a discipline against self-deception.**
> It prevents "I think it works" from replacing "I proved it works."

Three mechanisms enforce this:
1. **Externalization**: Every claim must produce an artifact
2. **Falsifiability**: Every artifact must be testable/checkable
3. **Traceability**: Each artifact must cite its source from the previous rung

### The 7-Step Ladder

| Rung | Question | Derivation Prompt | Evidence Anchor |
|------|----------|-------------------|-----------------|
| Intent | What outcome is being aimed for? | "From the task, derive the specific outcome being pursued" | "What does success look like?" (text/clarity) |
| Criteria | What conditions must be true for success? | "From the intent, derive the conditions that would verify success" | Checklist satisfiability |
| Structure | How is the solution organized? | "From the criteria, derive the organization needed to satisfy them" | Internal consistency check |
| Baseline | Does a minimal version exist? | "From the structure, derive a minimal artifact that demonstrates the approach" | Minimal viable example exists |
| Challenge | What checks expose gaps? | "From the baseline, derive checks that would fail if gaps exist" | External review or falsification attempt |
| Refinement | How is the artifact improved? | "From the challenge, derive targeted changes that address each gap" | Addresses specific gaps identified |
| Verification | How is completion confirmed? | "From the refinement, derive confirmation that no new gaps remain" | No new gaps exposed after N rounds |

### The Derivation Rule

**Each artifact must cite its source from the previous rung.**

Format:
```
[Current Rung] - [Derived from previous rung's output]
Source: [Specific content from previous rung]
```

No skipping. No leaping. Each step builds on the previous.

### Domain-Specific Evidence Authorities

| Domain | Authority | Evidence Form |
|--------|-----------|---------------|
| Software | Automated tests | Pass/fail results |
| Writing | Peer review | Feedback on clarity |
| Decision-making | Stakeholders | Consensus or concerns |
| Learning | Assessment | Test scores or application |
| Design | Users | Feedback or usage data |

### Quick Start

1. **State the task** (Intent)
2. **Define success** (Criteria)
3. **Organize the approach** (Structure)
4. **Produce minimal artifact** (Baseline)
5. **Find gaps** (Challenge)
6. **Improve** (Refinement)
7. **Verify completion** (Verification)

Each step must cite the previous. If you can't cite, you can't proceed.

### Phase 5: Integration (Ongoing)

- [x] Apply protocol to all new Ground Protocol sessions (regardless of domain)
- [x] Track cases where generalized language caused confusion
- [x] Iterate on terminology based on real usage
- [x] Maintain list of domain-specific adaptations for future reference
  - Created: `docs/ground-general-quick-ref.md` as living reference

## Open Questions

* [x] How to standardize "evidence" across non-executable domains? → Domain-specific authorities table
* [x] What minimum criteria define a valid "evaluation" outside testing frameworks? → Social validation authority decision
* [x] Should stricter rules apply when executable validation is available? → Yes, but optional (protocol works without it)
* [x] Where does "social validation" fit — who is the authority when artifacts aren't self-evidence? → Addressed in evidence authorities table
* [x] Does the ladder need to end with "Verification" explicitly (not just "done") to maintain the gap-driven iteration model? → Verified in tests

## Decision Drivers

* Need for broader applicability
* Preservation of epistemic rigor
* Reduction of domain-specific friction
* Making the self-deception prevention explicit
