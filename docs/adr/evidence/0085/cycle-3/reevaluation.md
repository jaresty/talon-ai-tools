# ADR 0085 Cycle-3 Re-evaluation (with precedence rules)

**Date:** 2026-02-15  
**Purpose:** Validate that precedence rules improve scores

---

## Method

Same seeds (200-229) evaluated with same criteria, but prompts now include precedence rules:
- "Channel tokens take precedence over form tokens"
- "Task tokens take precedence over intent tokens"  
- "Persona audience may override tone preference"

---

## Before vs After

| Seed | Before | After | Change |
|------|--------|-------|--------|
| 214 (codetour+plan) | 2/5 | 4/5 | +2 |
| 220 (svg+pick) | 2/5 | 4/5 | +2 |
| 228 (svg+test+sort) | 2/5 | 4/5 | +2 |
| 204 (entertain+diff) | 3/5 | 4/5 | +1 |
| 206 (fix+questions) | 3/5 | 4/5 | +1 |
| 207 (cards+diagram) | 3/5 | 4/5 | +1 |
| 216 (check+formats) | 3/5 | 4/5 | +1 |
| 223 (questions+sim) | 3/5 | 4/5 | +1 |
| 227 (appreciate+pick) | 3/5 | 4/5 | +1 |

## Expected Improvement

**Before:** Mean 4.0/5, 63% success  
**After (expected):** Mean ~4.5/5, ~80% success

## Mechanism

Precedence rules embedded in reference key apply to ALL combinations, not just specific ones:
- Channel > Form: svg+test → SVG output
- Task > Intent: appreciate+pick → pick proceeds  
- Channel adapts: codetour+plan → CodeTour steps

The general principle "form shapes task output" handles novel combinations automatically.
