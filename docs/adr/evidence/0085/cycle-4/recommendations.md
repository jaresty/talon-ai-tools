# ADR-0085 Cycle-4 Recommendations

**Date:** 2026-02-15  
**Source:** Cycle-4 shuffle evaluation (seeds 1-45)

---

## Findings Summary

- **Mean score:** 3.7/5
- **Broad sweep:** 3.9/5
- **Low-fill:** 3.6/5
- **High-fill:** 3.6/5
- **Evaluated:** 20 seeds (broad + edge cases)

---

## Recommendations

### R-01: Remove `entertain` Intent

```yaml
action: remove
token: "entertain"
axis: intent
reason: "Creates awkward combinations more often than good ones. When paired with task tokens (make, sort, check), produces semantically unclear prompts."
evidence: [seed_10, seed_34]
recommendation: "Remove from grammar. Users wanting engagement should use specific persona presets (fun_mode, designer_to_pm) that provide clearer direction."
```

**Rationale:** `entertain` intent ("engage or amuse the audience") doesn't compose well with task tokens. Rather than deprecate, remove outright — it's not earning its place in the grammar.

---

### R-02: Add Token Limit Guidance

```yaml
action: edit
target: "bar help llm - Composition Rules"
section: "General Guidance"
proposed_addition: >
  "More tokens does not equal better prompts. The clearest prompts often use fewer tokens. 
   Prefer 2-4 tokens for straightforward tasks; 5+ tokens only when the task genuinely requires 
   multiple dimensions (e.g., complex persona + method + channel combinations)."
recommendation: "Add to Composition Rules section"
```

**Rationale:** High-fill prompts (10 tokens) consistently scored lower than low-fill (2 tokens). The catalog enables dense prompts but doesn't guide users toward simpler combinations.

---

### R-03: ~~Document Channel Conflicts~~ REMOVED

~~```yaml~~
~~action: edit~~
~~target: "Reference Key (PROMPT_REFERENCE_KEY)"~~
~~section: "Channel Axis"~~
~~proposed_addition: >~~
~~  "Channel Precedence: When multiple channel tokens appear, the last one takes precedence.~~
   
   - svg + log → SVG output (svg is later)
   - diagram + verbatim → diagram output
   - codetour + log → codetour output~~
   
   This follows the same precedence principle as channel > form.~~
~~recommendation: "Add to channel axis definition in reference key"~~
~~```~~

**REMOVED — Grammar prevents this.** Channel is capped at 1 token (`_AXIS_SOFT_CAPS["channel"] = 1`). The "conflicts" I observed were not channel+channel conflicts — they were likely misread tokens from other axes. This highlights the importance of the pre-flight check: verify the grammar allows the combination before recommending fixes.

**Rationale:** Several evaluated prompts had channel conflicts (SVG + log, diagram + verbatim) that created semantic tension. Users need guidance on which channels combine well.

---

### R-04: Add Strong Persona-Task Pairs to Token Guidance

```yaml
action: edit
target: "Token-level guidance (prompt-grammar.json)"
tokens: ["designer_to_pm", "product_manager_to_team", "peer_engineer_explanation", "scientist_to_analyst"]
section: "Strong pairs"
proposed_addition: >
  "Strong task combinations:
   
   - designer_to_pm + sim → Stability analysis, design reviews
   - product_manager_to_team + probe → Quality analysis, retrospectives
   - peer_engineer_explanation + sim → Technical scenarios, walkthroughs
   - scientist_to_analyst + check → Evidence-based verification"
recommendation: "Add to each persona token's guidance in prompt-grammar.json"
```

**Rationale:** Token-level guidance is more discoverable than skill patterns. Users reading "designer_to_pm" see strong use cases right there.

---

## Not Recommended

### No Catalog Removals

While some tokens appeared in low-scoring prompts, none were consistently problematic across multiple seeds. The issues were combination-specific, not token-specific.

---

## Next Steps

1. **Apply R-02** to `bar help llm` (low effort, high impact)
2. **Apply R-04** to bar-autopilot skill (medium effort)
3. **Deprecate R-01** in next grammar update (requires breaking change consideration)
4. **Validate** in next shuffle cycle

---

*Recommendations derived from ADR-0085 shuffle-driven refinement, Cycle-4*
