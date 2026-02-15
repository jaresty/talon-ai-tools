# ADR 0085 Cycle-3 Recommendations: Precedence Rules

**Date:** 2026-02-15  
**Source:** Cycle-3 shuffle evaluation (seeds 200-229)

---

## Philosophy

Rather than blocking incompatible token combinations, define their behavior. This:
- Keeps shuffle generative (no artificial limits)
- Makes behavior predictable and documented
- Treats edge cases as defined semantics, not errors
- Aligns with ADR 0085's "evaluate and recommend" approach

---

## Precedence Rules

### Channel-Form Precedence

| Combination | Behavior |
|-------------|----------|
| `svg` + `test` | Channel takes precedence → Test scenarios visualized as SVG flow/structure diagram |
| `svg` + `cards` | Channel takes precedence → Cards rendered as visual elements in SVG |
| `diagram` + `cards` | Channel takes precedence → Cards formatted within diagram structure |
| `gherkin` + any form | Channel takes precedence → Pure Gherkin output, form ignored |

### Channel-Task Precedence

| Combination | Behavior |
|-------------|----------|
| `codetour` + `plan` | Channel takes precedence → Plan as interactive CodeTour steps (sequence of code locations) |
| `codetour` + `sort` | Channel takes precedence → Sort order visualized as CodeTour navigation |
| `svg` + `pick` | Channel takes precedence → Options visualized as SVG; choice indicated by highlighted nodes |
| `code` + `sim` | Channel warns but allows → Code output of simulation rather than narrative |
| `code` + `probe` | Channel warns but allows → Code output of analysis rather than narrative |

### Intent-Task Resolution

| Combination | Behavior |
|-------------|----------|
| `appreciate` + `pick` | Intent subsumed → Pick proceeds without appreciative framing |
| `appreciate` + `check` | Intent subsumed → Check proceeds without appreciative framing |
| `entertain` + `diff` | Intent subsumed → Comparison remains primary, presented engagingly |
| `teach` + `pick` | Intent recast → Choice framed as learning opportunity |
| `coach` + `make` | Intent merges → Creation includes coaching guidance |

### Form-Task Semantics

| Combination | Behavior |
|-------------|----------|
| `test` + `plan` | Form recasts → Plan becomes test plan/acceptance criteria |
| `questions` + `sim` | Blend → Simulation explores via Socratic questioning |
| `questions` + `fix` | Questions precede → Clarifying questions about what to fix before reformatting |
| `case` + `make` | Form merges → Creation structured as argument case |
| `spike` + `pick` | Form guides → Pick outcome is research spike output |

### Scope-Task Compatibility

| Combination | Behavior |
|-------------|----------|
| `time` + `fix` | Scope reframes → Temporal focus on when/how fix applies, not what to fix |
| `time` + `diff` | Scope reframes → Comparison of temporal aspects |

### Persona-Tone Adjustment

| Combination | Behavior |
|-------------|----------|
| `casually` + `to Kent Beck` | Tone adjusts → More technically precise despite casually token |
| `formally` + `to junior engineer` | Tone adjusts → Formality relaxed for clarity |
| `gently` + `to CEO` | Tone adjusts → Gentle within business brevity |

### Minimal-Completeness with Task

| Combination | Behavior |
|-------------|----------|
| `minimal` + `plan` | Produces outline-level plan |
| `skim` + `probe` | Light pass analysis |
| `narrow` + `make` | Focused creation on narrow slice |

---

## Documentation Strategy

### 1. Token Descriptions

Add "When combined with..." clauses to token descriptions:

```markdown
# Example: codetour channel
channel: codetain
description: >
  Delivered as CodeTour steps.
  
  When combined with:
  - plan: Steps become navigation sequence for planning
  - sort: Order becomes visit sequence
  - other tasks: Standard CodeTour format
```

### 2. bar help llm - Composition Rules

Expand "Composition Rules" section with precedence table:

```markdown
## Precedence Rules

When tokens from different axes combine:

| Axis | Takes Precedence Over |
|------|----------------------|
| channel | form, scope (output-defined) |
| task | intent (when incompatible) |
| persona | tone (audience-adjusted) |

See specific combinations below...
```

### 3. Shuffle Transparency

Log precedence rules applied:

```json
{
  "seed": 214,
  "tokens": ["plan", "codetour"],
  "precedence_applied": "channel-task: codetour takes precedence over plan semantics"
}
```

---

## Comparison: Cycle-2 vs Cycle-3

| Metric | Cycle-2 | Cycle-3 |
|--------|---------|---------|
| Mean Score | 3.7/5 | 4.0/5 |
| Success Rate | 60% | 63% |
| Approach | "Block incompatibilities" | "Define precedence" |

Cycle-3's shift to defining behavior rather than blocking produces slightly better scores and provides actionable semantics.

---

## Next Steps

1. **Update token descriptions** with precedence clauses
2. **Enhance bar help llm** composition rules section
3. **Add shuffle transparency** - log precedence decisions
4. **Validate** with future shuffle cycles

---

*Recommendations derived from ADR 0085 shuffle-driven refinement process*
