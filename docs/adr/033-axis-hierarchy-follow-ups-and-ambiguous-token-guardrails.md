# 033 – Axis Hierarchy Follow-Ups and Ambiguous Token Guardrails

- Status: Accepted  
- Date: 2025-12-09  
- Context: Consolidating remaining work for ADR 032 (constraint hierarchy) across vocab, UI surfaces, and regressions  
- Related ADRs:  
  - 005 – Orthogonal Prompt Modifiers and Defaults  
  - 012 – Style and Method Prompt Refactor  
  - 018 – Axis Modifier Decomposition into Pure Elements  
  - 020 – Richer Meta Interpretation Structure  
  - 026 – Axis Multiplicity for Scope/Method/Style  
  - 032 – Constraint Hierarchy Meta-Spec for Completeness/Method/Scope/Style  

---

## Context

ADR 032 embedded the completeness>method>scope>style hierarchy and prefix handling into the axis interpreter. Follow-up work remains to:
- Audit vocabulary overlaps across axes and add guardrails/tests for ambiguous tokens.
- Surface the hierarchy and prefix syntax in help/GUI surfaces so users understand how conflicts resolve.
- Ensure downstream consumers (recipes, history, suggestion GUI) rely on the resolved axes, not raw tokens, and expose reassignments when useful.

### Overlap definition and detection

An overlap means an adjective plausibly fits multiple constraint layers (completeness, method, scope, style). Detect overlaps using the following methods:
- **Adversarial substitution**: Drop the adjective into per-axis templates. If it sounds natural in more than one (for example, completeness, method, scope, style), it overlaps.
- **Conflict-stress**: Pair the adjective with conflicting instructions and see which axis it pulls (for example, “detailed but short” vs. “detailed but only drivetrain” vs. “detailed with simple method”).
- **Meaning decomposition**: Ask if it governs content amount (completeness), reasoning process (method), topical bounds (scope), or presentation (style). Multiple “yes” answers mean overlap.
- **Corpus scan**: Ask the model for usage examples and map them to axes; multiple axes in examples imply overlap.

Remediation options once overlap is confirmed:
- Require disambiguation phrases (for example, “deep (conceptual)” vs. “deep (comprehensive)”).
- Assign a fixed category in the meta-spec (“focused” always equals scope).
- Replace with more atomic adjectives (“compact” → “short” for style or “dense” for completeness).

## Decision

Track and complete the remaining work as part of this ADR:

1) **Vocabulary overlap audit and guardrails**  
   - Inventory current axis token/value overlaps across completeness/method/scope/style.  
   - Decide per-token whether overlap is intentional; if not, adjust lists or add explicit prefixes in profiles/mappings.  
   - Add regression tests that feed ambiguous tokens through `modelPrompt` to assert ADR 032 priority (Completeness > Method > Scope > Style) and prefix overrides.

2) **UI/help surfacing**  
   - Surface a compact hierarchy summary and prefix syntax in quick help/axis docs/GUI surfaces (reuse ADR 032 text).  
   - Consider a lightweight notification or tooltip when tokens are reassigned across axes (optional UX guardrail).

3) **Downstream consumer alignment**  
   - Ensure last_recipe, suggestion GUI, and history/log entries serialize the resolved axes; avoid showing raw misfiled tokens.  
   - Add coverage for axis reassignment visibility (e.g., confirmation/recipe recap shows the resolved axis values).
   - Apply ADR 032 guardrails (dominance order and prefix overrides) when mapping profile/help vocab to the fixed-axis decisions from the overlap analysis before treating this ADR as complete.

## Consequences

Positive:
- Reduces silent drift from ambiguous adjectives; makes overlaps explicit and tested.
- Users see the hierarchy/prefix rules in UI/help, decreasing confusion.
- Recipes/history reflect actual enforced axes, improving replay fidelity.

Negative / mitigations:
- Slightly more verbosity in help surfaces; mitigate with a compact summary and optional verbose view.
- Extra tests and list adjustments may require occasional vocabulary tweaks; mitigate with clear per-token decisions and prefixes when needed.
