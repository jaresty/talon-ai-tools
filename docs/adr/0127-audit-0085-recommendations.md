# ADR: Audit of ADR-0085 Recommendations

## Status

Accepted

## Context

ADR-0085 generated a `recommendations.yaml` with 21 recommendations across categories: retire (2), edit (11), add (5), process (3). This ADR audits which recommendations have been implemented vs remain pending.

## Re-Evaluation Findings

Rather than trusting the original audit, we re-tested the specific problematic combinations:

### Combinations That NOW WORK

| Combination | Original Issue | Current Status |
|-------------|----------------|----------------|
| gherkin + presenterm | channel/form conflict | gherkin now includes: "Works with presenterm/diagram channels when wrapped in markdown code blocks" |
| probe + socratic | task/form conflict | socratic now includes: "With probe: naturally extends to deeper inquiry" |

### Key Changes Discovered

1. **gherkin moved from FORM to CHANNEL** - This was a structural fix that resolves many conflicts
2. **socratic updated with task compatibility** - Now explicitly describes behavior with different tasks
3. **fix guidance added to staticPromptConfig** - Now explains debug vs fix workflow

## Key Insight: Guidance vs Behavior

These recommendations suggest adding "Works best with X" / "Avoid with Y" clauses — helping users select correct combinations.

But that's O(n²) enumeration — fragile and incomplete.

The ADR-0085 philosophy ("define behavior, not blocks") is better: describe what happens when tokens combine, letting users predict outcomes rather than memorize rules.

Precedence rules already do this (e.g., "channel > form").

### Decision: Close Guidance Recommendations

These 11 edit recommendations should be marked as **superseded by precedence approach**:
- gherkin: Already fixed via channel move
- plain, diagram, announce, to CEO: Close — behavior described via precedence
- socratic: Already has task compatibility
- cocreate, inversion, simulation, adr, fix: Close — not high enough signal

## Remaining Decisions

1. **Retire dimension/converge?** — Do they serve distinct purposes despite overlap?
2. **Metadata system?** — Not needed if behavior/precedence approach works
