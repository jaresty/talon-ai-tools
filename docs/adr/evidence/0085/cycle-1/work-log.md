# ADR-0085 Cycle-1 Work Log — Shuffle-Driven Catalog Refinement

**Date:** 2026-02-14  
**Status:** In Progress  
**Previous:** ADR-0113 Loop 4 (task-gap analysis complete, mean 4.87/5.0)

---

## Cycle 1 Objectives

1. **Test token coherence** — Do randomly selected tokens work together?
2. **Identify conflicts** — Find token combinations that fight or contradict
3. **Validate new tokens** — Test `cross` (R-01) and `compare` (R-L2-01) in combinations
4. **Check category alignment** — Are tokens in the right axes?

---

## Phase 1: Generation

**Command:**
```bash
for seed in $(seq 1 30); do
  bar shuffle --seed $seed --json > corpus/shuffle_$seed.json
done
```

**Output:** 30 shuffled prompts with reproducible seeds

**Sampling strategy:**
- Seeds 1-30: Broad sweep (random combinations)
- Future: Category deep-dives (method-focused, scope-focused)

**Status:** ✅ Complete

---

## Phase 2: Evaluation

### Evaluation Criteria (ADR-0085)

For each shuffled prompt, score 1-5 on:

1. **Task clarity** — Does task define success clearly?
2. **Constraint independence** — Do constraints shape HOW not WHAT?
3. **Persona coherence** — Does persona make sense for this task?
4. **Category alignment** — Is each token in right axis?
5. **Combination harmony** — Do tokens work together or fight?

**Overall score:** 1-5

---

## Progress Tracker

| Phase | Status | Notes |
|-------|--------|-------|
| 1. Generate | ✅ Complete | 30 shuffled prompts (seeds 1-30) |
| 2. Evaluate | ✅ Complete | All 30 seeds evaluated |
| 3. Meta-evaluate | ✅ Complete | Skill alignment checked |
| 4. Recommend | ✅ Complete | 3 recommendations (1 high priority) |

---

## Cycle 1 Final Results

### Overall Statistics

| Score | Count | Percentage |
|-------|-------|------------|
| 5 (Excellent) | 15 | 50% |
| 4 (Good) | 12 | 40% |
| 3 (Acceptable) | 2 | 7% |
| 2 (Problematic) | 1 | 3% |
| 1 (Broken) | 0 | 0% |

**Mean:** 4.37/5.0

### Key Findings

✅ **90% of combinations score ≥ 4** — Catalog internally consistent  
✅ **`cross` token validated** — Appears naturally in shuffles  
⚠️ **1 conflict found:** faq + shellscript (Seed 30)  
ℹ️ **2 minor issues:** log+diagram, quiz+presenterm

### Recommendations

| ID | Priority | Description |
|----|----------|-------------|
| R-0085-01 | **High** | Add faq ↔ shellscript/code/codetour incompatibility |
| R-0085-02 | Low | Document quiz+presenterm interaction |
| R-0085-03 | Low | Document log+diagram precedence |

---

## Artifacts

| File | Description |
|------|-------------|
| `corpus/shuffle_*.json` | 30 generated prompts |
| `evaluations/seeds_*_eval.md` | Batch evaluations |
| `evaluations/seed_01_eval.md` | Detailed single-seed example |
| `cycle-1-summary.md` | Complete analysis |
| `work-log.md` | This progress tracker |

---

## Next: Evaluate Seeds 1-10

Starting systematic evaluation of shuffled combinations.

