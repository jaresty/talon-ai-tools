# 032 – Constraint Hierarchy Meta-Spec for Completeness/Method/Scope/Style

- Status: Accepted  
- Date: 2025-12-09  
- Context: Prompt constraint interpretation for completeness, method, scope, and style adjectives  
- Related ADRs:  
  - 012 – Style and Method Prompt Refactor  
  - 018 – Axis Modifier Decomposition into Pure Elements  
  - 020 – Richer Meta Interpretation Structure  
  - 026 – Axis Multiplicity for Scope/Method/Style  

---

## Context

We use adjectives to steer prompts, but their meanings are overloaded and the model's default tendencies introduce ambiguity. We need a deterministic interpretation layer baked into our axis interpreter—not just a copy-paste preamble—so that:
- Adjectives are classified into four constraint types (completeness, method, scope, style).
- The axis interpreter enforces priority ordering for conflict resolution.
- Multi-meaning adjectives resolve deterministically.
- Explicit category overrides and tradeoff rules are first-class in the system, not free text.

## Decision

Embed the following canonical hierarchy into the prompt axis interpreter and related scaffolding:

**Constraint Interpretation Rules**
1) **Constraint types**: Adjectives map to one of four categories: completeness (content required), method (reasoning process), scope (topical bounds), style (presentation).  
2) **Dominance order**: Completeness > Method > Scope > Style. Higher-priority constraints always win conflicts; lower ones are satisfied only when they do not violate higher ones.  
3) **Ambiguity rule**: If an adjective fits multiple categories, interpret it according to the highest-priority category consistent with the rest of the instruction.  
4) **Tradeoff rule**: Attempt to satisfy all constraints; when impossible, compromise minimally in priority order above and make compromises explicit.  
5) **Explicit overrides**: If an adjective is prefixed with `Completeness:`, `Method:`, `Scope:`, or `Style:`, treat it exactly as that category, regardless of other meanings.  
6) **Clarification preference**: If instructions remain ambiguous and cannot be safely resolved, ask for clarification before proceeding.

Implementation scope:
- Update the axis interpreter to apply the dominance order and ambiguity rule before composing prompts.
- Extend adjective-to-category lookup to support explicit prefixes and per-axis defaults.
- Provide both compact and verbose renderings for UI/help surfaces, sourced from this ADR, but keep the primary enforcement inside code.

## Consequences

Positive:
- Deterministic conflict resolution with explicit priority, reducing silent constraint drift.
- Lower ambiguity for multi-meaning adjectives and a clear override syntax for authors.
- System-level enforcement keeps axis interpretation consistent; help surfaces can still surface compact/verbose guidance.

Negative / mitigations:
- Slight implementation complexity to thread priority handling through axis composition; mitigated by keeping the rules small and centralized.
- Authors must map their adjectives into the four categories; mitigated by lookup tables, overrides, and optional verbose guidance in UI/help.
