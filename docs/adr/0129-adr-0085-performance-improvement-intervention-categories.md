# ADR 0129: ADR 0085 Performance Improvement — Intervention Categories

## Status

Proposed

## Context

ADR 0085 (Shuffle-Driven Catalog Refinement) has been run multiple times, but ratings remain persistently low across evaluation dimensions:

- Task clarity
- Constraint independence
- Persona coherence
- Category alignment
- Combination harmony
- Skill alignment
- Skill discoverability
- Heuristic coverage
- Documentation completeness
- Reference utility (bar help llm)

Low scores indicate systemic issues in the prompt catalog, skill guidance, or reference documentation—not just individual token problems. We need to identify intervention categories that can improve performance without using logic to prevent token combinations.

**Key constraint**: All prompt adjustments belong in **tokens themselves**, not in help documentation or skills. `bar help llm` and skills focus on **token selection** guidance—what to choose and why—not on prompting instructions.

## Decision

Pursue a phased intervention strategy across four categories, ordered by effort-to-impact ratio:

### Phase 1: Token Selection Guidance (Highest Priority)

**Constraint**: Differentiation guidance belongs in `AXIS_KEY_TO_GUIDANCE` (selection help), NOT in `AXIS_KEY_TO_VALUE` (prompt content injected into LLM). VALUE descriptions should remain clean prompt instructions.

**Problem**: Tokens with overlapping semantic territory have descriptions that fail to communicate distinct purpose. Evaluators cannot distinguish them, leading to low "category alignment" and "documentation completeness" scores.

**Targets** (method axis, highest overlap - add to GUIDANCE):

| Token Pair | Issue | Differentiation Guidance |
|------------|-------|--------------------------|
| `systemic` + `analysis` | Both describe "understanding whole" | `systemic` = feedback loops/interactions; `analysis` = decomposition/structure |
| `explore` + `branch` | Both survey options | `explore` = generate options; `branch` = parallel reasoning with evaluation |
| `abduce` + `induce` + `deduce` | All reasoning methods, hard to distinguish | Abduce = evidence→hypothesis; Deduce = premises→conclusion; Induce = examples→pattern |
| `robust` + `resilience` | Both about handling adversity | `robust` = options across futures; `resilience` = behavior under stress |
| `meld` + `cluster` | Both combining/organizing | `meld` = balance constraints; `cluster` = group by characteristics |

**Files to modify**:
- `lib/axisConfig.py` — Add differentiation to `AXIS_KEY_TO_GUIDANCE["method"]` section
- Regenerate `prompt_grammar.json` after changes

### Phase 2: Skill Heuristic Updates

**Problem**: Low "skill alignment" scores indicate bar skills don't guide users toward valid combinations. Skills need to explain *why* certain combinations work.

**Targets**:

1. **bar-autopilot** § "Choosing Method" — Add method selection heuristics:
   - When to use reasoning methods (`abduce`, `induce`, `deduce`) vs exploratory methods (`explore`, `branch`)
   - How method combos create distinct reasoning profiles

2. **bar-suggest** § "Usage Patterns" — Add pattern:
   - "Evaluation with falsification" = `check` + `verify` + `risks`

3. **bar-workflow** — Clarify that method progressions (e.g., `explore` → `branch` → `converge`) are valid patterns

**Files to modify**:
- `internal/barcli/skills/bar-autopilot/skill.md`
- `internal/barcli/skills/bar-suggest/skill.md`
- `internal/barcli/skills/bar-workflow/skill.md`
- Sync to `.claude/skills/*/skill.md`

### Phase 3: bar help llm — Token Selection Focus

**Constraint**: `bar help llm` must focus on **token selection** guidance—what tokens to choose and why—not on prompting instructions. Prompt adjustments belong in the tokens themselves, not in the help reference.

**Problem**: Low "cheat sheet utility" and "selection guidance" scores indicate tokens are hard to find or understand in context.

**Targets** (token selection focus):

- Improve "Choosing Method" section with clearer **selection criteria** (what to consider when picking method tokens)
- Add cross-references between related tokens to aid **discovery**
- Expand "Usage Patterns by Task Type" showing **valid token combinations**
- Clarify "Composition Rules" for method combinations—what **works together**, not how to prompt
- Ensure token descriptions describe **what the token does** (constraint on the LLM's output), not prompting strategies

**What NOT to add**:
- How to construct prompts
- Prompt templates or examples that go beyond demonstrating token selection
- Prompting techniques or strategies

**Files to modify**:
- `internal/barcli/help_llm.go` — Token Catalog section and organizational sections

### Phase 4: Token Addition/Retirement (If Earlier Phases Insufficient)

**Problem**: Persistent "combination harmony" failures indicate missing tokens—valid combinations that lack a token to enable them—or redundant tokens that cannot be distinguished.

**Token Addition triggers**:
- 3+ evaluations noting "no token for X" where a reasonable token concept exists

**Token Retirement triggers**:
- 3+ evaluations showing token produces identical output to another
- Token scores ≤2 across all evaluation dimensions

---

## Pilot Iteration Structure

Before committing to broad changes, validate with a targeted pilot:

1. **Select 5 low-scoring evaluations** from prior ADR 0085 runs as test cases
2. **Apply Phase 1 description edits** to 10-15 high-overlap method tokens
3. **Re-run shuffle** with same seeds (reproducibility via `--seed`)
4. **Re-evaluate same prompts** with updated descriptions
5. **Compare scores**: If average improves by ≥0.5 on "description clarity" and "documentation completeness", proceed to Phase 2

**Success metrics**:
- "Description clarity" scores increase
- "Skill discoverability" scores increase (if skills updated)
- "Combination harmony" improves marginally

---

## Consequences

### Positive

- Low-effort, high-visibility fixes first
- Phased approach reduces risk of overcorrection
- Pilot validation prevents broad changes that don't improve scores
- Addresses root cause (unclear descriptions) rather than symptoms

### Tradeoffs

- Description edits alone may not solve all low-score patterns
- Token addition/retirement remains high-effort and disruptive
- Skill updates require coordination across multiple files

### Risks

- Over-editing descriptions could introduce new confusion
- Phase 1 improvements may plateau below acceptable scores
- Pilot selection bias (specific seeds may not represent broader patterns)

**Mitigations**:
- Require consensus on description edits (2+ reviewers)
- Track score improvements per evaluation dimension
- If Phase 1 plateaus, advance to Phase 2 even if not at target

---

## Validation

```bash
# Re-run pilot evaluations with updated descriptions
bar shuffle --seed {original-seed} --json

# Compare dimension scores before/after
# Target: +0.5 average on affected dimensions
```

---

## Future Extensions

- Automated overlap detection: Script that flags tokens with similar description embeddings
- Score trend tracking: Dashboard showing ADR 0085 scores over time
- Cross-validation with ADR 0113: Correlate shuffle scores with task-driven gap analysis
