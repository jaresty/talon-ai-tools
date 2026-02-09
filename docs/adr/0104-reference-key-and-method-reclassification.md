# ADR-0104: Reference Key Clarification and Method Reclassification

## Status
Accepted

## Context

The prompt framework distinguishes between:
- **Tasks** (what kind of response is required),
- **Scopes** (what epistemic dimension the response should privilege),
- **Forms** (how the response is rendered),
- **Methods** (how the agent approaches or structures its reasoning).

Over time, the method token set accumulated items that functioned less like reasoning approaches and more like:
- analytical targets (e.g. incentives, constraints),
- representational formats (e.g. table),
- or scope-like stances (e.g. dynamics).

This caused ambiguity in:
- token intent,
- enforcement expectations,
- and the boundary between prompt-time interpretation and system-time classification rules.

In parallel, the **reference key**—an in-prompt artifact meant to guide the LLM’s interpretation of a *single prompt*—began to risk absorbing taxonomy governance logic that should instead live outside the prompt.

This ADR resolves both issues by:
1. Clarifying what belongs in the reference key versus ADRs.
2. Reclassifying or deprecating method tokens that no longer meet the definition of “method.”

---

## Decision 1: Reference Key Scope and Edits

### Decision

The reference key is defined as an **interpretive aid for an individual prompt**, not a taxonomy enforcement mechanism.

It:
- explains how to understand fields *as used in this prompt*,
- defines local meanings and priorities,
- does **not** encode system-wide classification rules.

### Implications for the Reference Key

The reference key:
- MAY describe what a scope, task, form, or method *means in use*.
- MAY clarify precedence or interaction between fields.
- MUST NOT include rules such as:
  - how tokens are classified system-wide,
  - negative tests for scopes vs methods,
  - deprecation rationale.

All such rules live in ADRs and design documentation.

### Edit Summary

- Reference key language was tightened to:
  - remove taxonomy justification,
  - remove cross-axis adjudication logic,
  - focus purely on interpretive guidance for the active prompt.

### Updated reference key
Reference Key

This key explains how to interpret the fields used in this prompt.

Task
The task specifies what kind of response is required (e.g., explanation, transformation, evaluation). It defines the primary action the response should perform.

Scope
The scope indicates which dimension of understanding to privilege when responding. It frames *what kind of understanding matters most* for this prompt.

Method
The method describes the reasoning approach or analytical procedure the response should follow. It affects *how* the analysis is carried out, not what topic is discussed or how the output is formatted.

Form
The form specifies the desired structure or presentation of the output (e.g., list, table, scaffold). It does not change the underlying reasoning, only how results are rendered.

Subject
The subject provides the content or material the task operates on. It may be supplied inline or via stdin.

Notes
If multiple fields are present, interpret them as complementary signals. Where ambiguity exists, prioritize the task and scope to determine the response’s intent.


---

## Decision 2: Method Reclassification and Deprecation

### Method Definition (Reaffirmed)

A **method** is a reasoning approach or procedural stance that:
- changes *how* the agent thinks or organizes analysis,
- is orthogonal to subject matter,
- can be applied across many domains without redefining the task or scope.

Tokens that primarily name *what to look at* rather than *how to think* do not qualify.

---

## Itemized Method Review and Recommendations

### 1. incentives
**Recommendation:** Remove from methods  
**Rationale:**  
Incentives identify a *subject of analysis*, not a reasoning approach. They naturally appear within scopes like `mean`, `fail`, or `act`. Treating them as methods encourages shallow enumeration rather than disciplined analysis.

---

### 2. dynamics
**Recommendation:** Reclassify as scope (if retained)  
**Rationale:**  
Dynamics represent a distinct epistemic commitment: explaining behavior via interaction and change over time. This is not a procedural method but a stance about what kind of explanation matters.

---

### 3. interfaces
**Recommendation:** Remove from methods  
**Rationale:**  
Interfaces are structural artifacts (boundaries, seams, interaction surfaces). Analysis of interfaces belongs under `struct`, `fail`, or `thing`. As a method, it collapses into content enumeration.

---

### 4. constraints
**Recommendation:** Remove from methods  
**Rationale:**  
Constraints are descriptive properties that appear across many scopes. There is no independent “constraint-thinking” method; the analytical work is always structural, temporal, or failure-oriented.


---

### 6. roles
**Recommendation:** Remove from methods  
**Rationale:**  
Roles are entities or perspectives, not reasoning approaches. They are handled by `thing` (ontology) and `view` (perspective). As a method, roles incentivize shallow listings.


---

### 9. assumptions
**Recommendation:** New scope  
**Rationale:**  
Assumptions target preconditions of reasoning itself. This suspends action, evaluation, and structure, making it a strong and distinct scope rather than a method.

---

## Consequences

### Positive
- Sharper method semantics.
- Reduced taxonomy drift.
- Clear separation between:
  - prompt interpretation (reference key),
  - system governance (ADRs).

### Negative / Tradeoffs
- Some analytical concepts lose first-class token status.
- Users must rely on scopes and tasks to surface these concepts implicitly.

This is an intentional tradeoff to preserve conceptual integrity.

---

## Design Principle (Codified)

> **Scopes represent dominant epistemic commitments.  
> Methods represent reasoning procedures.  
> Forms represent output shape.  
> Analytical nouns alone do not justify new axes.**

---

## Follow-up Work

- Update documentation to reflect revised method and scope sets.
- Audit existing prompts for deprecated method tokens.
- Consider optional internal checklists for concepts like incentives or constraints without promoting them to first-class tokens.

