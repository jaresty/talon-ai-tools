# 076 – Axis Token Rebucket for Method/Form/Channel Purity

- Status: Proposed  
- Date: 2026-01-11  
- Context: Axis catalog tokens for `method`, `form`, and `channel` currently intermix output-shape semantics, reasoning workflows, and delivery media, creating conflicts with ADR 005/012 definitions and the dominance ladder (Completeness > Method > Scope > Style/Form > Channel).

---

## Summary (for users)

- Method tokens will strictly describe *how* the model reasons; visual-layout instructions move out.  
- Form tokens will own output containers such as diagrams, HTML/SVG markup, CodeTour JSON, and multi-variant option sets.  
- Channel tokens will focus on destination/medium biases (Slack, Jira, Presenterm, Remote, Sync) without dictating payload structure.  
- Guardrails and docs will update together so spoken modifiers map to the clarified buckets.

---

## Decision

1. **Re-home format-constrained channel tokens into the Form axis (required)**  
   - Move `diagram`, `html`, `svg`, and `codetour` from `channel` to `form`; their current descriptions already demand specific syntactic containers and safety rules, which belong to output shape.  
   - Add concise long-form descriptions in `form` mirroring existing guarantees (Mermaid/Presenterm safety, semantic HTML, SVG purity, CodeTour schema compliance).  
   - Keep channel focused on surface bias tokens: `slack`, `jira`, `presenterm`, `remote`, `sync`, plus any future “where it goes” hints.

2. **Retire the `visual` method token in favour of form-based instructions (required)**  
   - Remove `visual` from the method list; the behaviour collides with the `form.visual` token and causes conflicting instructions when both axes are set.  
   - Update affected patterns/help examples to swap `method=visual` with `form=visual` (or `method=mapping` where reasoning scaffolding is intended).  
   - Add a migration guardrail so spoken `method visual` produces a user-facing hint pointing to the new form token.

3. **Split sampling behaviour into reasoning and presentation facets (required)**  
   - Replace the current `method=samples` entry with `method=explore` (name TBD) that emphasises generating and comparing candidate options before committing, without promising multi-output formatting.  
   - Introduce a new `form=variants` token that carries the “deliver several self-contained options with optional probabilities” instruction.  
   - Update axis hydration, pattern recipes, and help copy so workflows call the reasoning token when they need divergent exploration and add `form=variants` only when the output must include multiple alternatives.

4. **Refresh guardrails, docs, and generators (required)**  
   - Regenerate `axisConfig.py`, Talon lists, and README/cheatsheet sections to reflect the new bucket assignments.  
   - Extend `_tests/test_axis_registry_drift.py`, axis catalog validators, and `modelPrompt` guardrails to fail fast if removed tokens resurface or if format-heavy tokens return to `channel`/`method`.  
   - Update affected GUIs (help hub, quick help, prompt patterns) so they show the rebucketed tokens in the correct sections and guide users away from legacy utterances.

5. **Migration and backward compatibility (recommended)**  
   - Provide release notes/help hub callouts summarising token moves and offering quick replacement commands (for example, “Say `form diagram` instead of `channel diagram`; say `form variants` + `method explore` for multi-option outputs”).  
   - Add transitional notifications in Talon grammar so legacy captures (e.g., `channel diagram`, `method visual`, `method samples`) produce actionable prompts instead of silent failure.  
   - Review static prompt profiles to ensure defaults remain coherent; update any that referenced the moved tokens.

---

## Consequences

### Benefits

- Restores axis orthogonality so each modifier affects only one dimension of the contract, reducing ambiguity and conflict resolution overhead.  
- Simplifies dominance reasoning: completeness vs. method vs. form/channel clashes no longer carry duplicate instructions.  
- Improves discoverability—users see format-centric tokens under Form and destination biases under Channel, aligning with ADR 005 mental models.  
- Creates a dedicated container (`form=variants`) for multi-option outputs, making “generate alternatives” recipes easier to teach and test.

### Risks and Mitigations

- **Risk:** Users with muscle memory for `channel diagram` / `method visual` experience capture failures.  
  **Mitigation:** Add explicit migration messaging in grammar guardrails, help hub, and release notes; provide alias period via hints (not silent aliases) so users adopt the new axis quickly.

- **Risk:** Rebucket requires coordinated updates across axis catalogs, GUIs, and docs; partial landing could desynchronise tests.  
  **Mitigation:** Treat the migration as a single workstream with combined PR/test plan; extend registry drift tests to enforce the new bucket assignments.

- **Risk:** Introducing `form=variants` may encourage overuse where a simple list suffices.  
  **Mitigation:** Document the intended use (“when stakeholders need separate, decision-ready options”) and keep examples scoped to high-value recipes.

- **Risk:** Renaming `method=samples` to `method=explore` could break pattern references.  
  **Mitigation:** Update pattern catalog entries in the same change set; add a temporary warning when legacy configs reference the old key.

- **Risk:** Token descriptions may drift toward imperative phrasing that over-constrains outputs.  
  **Mitigation:** Enforce a guardrail that all axis prompts and descriptions use declarative language ("The response ...") rather than imperative commands, leaving room for the LLM to choose the optimal realisation while still meeting axis constraints.  
  Add validator coverage so future edits fail CI if imperative lead-ins ("Do", "Generate", "Return", etc.) sneak back in.

### Follow-ups

1. Implement rebucket changes in axis lists, catalog generation, and guardrails.  
2. Update pattern/help surfaces and release documentation.  
3. Monitor usage telemetry post-migration to confirm reduced cross-axis conflicts and adjust token descriptions if confusion persists.
