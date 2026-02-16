# ADR 0085 Evaluation - Pilot Run

**Date**: 2026-02-15
**Evaluator**: Agent
**Purpose**: Validate ADR 0129 improvements

## Seeds 1-10 Quick Evaluation

### Seed 1: pull, cross, table, sync, fig
- **Task**: pull (extract subset)
- **Scope**: cross (cross-cutting concerns)
- **Form**: table
- **Channel**: sync
- **Directional**: fig

**Evaluation**:
- Task clarity: 4 (clear extraction task)
- Category alignment: 4 (cross is well-defined for cross-cutting, table is standard)
- Combination harmony: 4 (fig + sync + table work well together)

### Seed 2: shift, domains, taxonomy
- **Task**: shift (rotate perspectives)
- **Method**: domains (bounded contexts)
- **Form**: taxonomy

**Evaluation**:
- Task clarity: 4 
- Category alignment: 4 (domains + taxonomy align)
- Combination harmony: 5 (excellent - taxonomy organizes domains)

### Seed 3: plan, fail, product
- **Task**: plan
- **Scope**: fail (failure modes)
- **Method**: product (product lens)

**Evaluation**:
- Task clarity: 4
- Category alignment: 4 
- Combination harmony: 4 (product lens on failures works)

### Seed 4: probe, assume
- **Task**: probe (analyze)
- **Scope**: assume (premises)

**Evaluation**:
- Task clarity: 5 (clear)
- Category alignment: 5 (assume + probe = examining premises)
- Combination harmony: 5

### Seed 5: make, cross, melody
- **Task**: make (create)
- **Scope**: cross (cross-cutting)
- **Method**: melody (coordination)

**Evaluation**:
- Task clarity: 4
- Category alignment: 3 (melody is about coordination, unclear how it adds to cross)
- Combination harmony: 3 (cross + melody slightly redundant)

### Seed 6: sim, scaffold
- **Task**: sim (scenario)
- **Form**: scaffold

**Evaluation**:
- Task clarity: 5
- Category alignment: 5
- Combination harmony: 5

### Seed 7: sort, assume, meld, tight
- **Task**: sort
- **Scope**: assume (premises)
- **Method**: meld (balances)
- **Form**: tight

**Evaluation**:
- Task clarity: 4
- Category alignment: 4 (meld balances constraints)
- Combination harmony: 4 (tight + meld = concise balancing)

### Seed 8: shift, assume, experimental, contextualise
- **Task**: shift
- **Scope**: assume
- **Method**: experimental
- **Form**: contextualise

**Evaluation**:
- Task clarity: 4
- Category alignment: 4
- Combination harmony: 4

### Seed 9: sim, cross
- **Task**: sim
- **Scope**: cross

**Evaluation**:
- Task clarity: 5
- Category alignment: 5
- Combination harmony: 5

### Seed 10: sort, cross
- **Task**: sort
- **Scope**: cross

**Evaluation**:
- Task clarity: 4
- Category alignment: 4
- Combination harmony: 4

## Summary

| Metric | Average | Notes |
|--------|---------|-------|
| Task clarity | 4.3 | All prompts have clear tasks |
| Category alignment | 4.2 | Most tokens clearly fit their axes |
| Combination harmony | 4.3 | Most combinations work well |

**Observations**:
- Seeds with method axis (2, 5, 7, 8) had slightly lower scores - method selection is the trickiest
- Seed 5 (melody) was the weakest - the method axis is where differentiation matters most
- The differentiation guidance should help with method selection

**Next Steps**:
- The scores are reasonably high (4.2-4.3)
- Method differentiation guidance is now available in bar help llm
- No obvious candidates for retirement at this point
