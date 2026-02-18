# ADR-0113 Loop-15 Evaluations

**Date:** 2026-02-18
**Binary:** /tmp/bar-new (built from source)
**Focus:** Part A — Post-apply validation of loop-14 method fixes (T221, T222, T223)
           Part B — General health check: 10 diverse cross-axis tasks

---

# Part A — Post-Apply Validation: Loop-14 Method Fixes

Re-evaluating T221 (meld, score 2), T222 (mod, score 2), T223 (field, score 1).

---

## T221 — Consistency vs. availability balance (re-test)

**Loop-14 score:** 2 (meld missed — compare preempted it)

**Post-fix:** use_when "balance between", "navigate tensions between" → meld
- User: "trade-offs between consistency and availability... right balance"
- "balance between" fires ✅; "navigate tensions between" fires ✅

**Bar command (post-fix):** `bar build probe full meld`

**Scores:** fitness 5, completeness 4, correctness 4, clarity 4 → **Overall: 4** ✅

---

## T222 — Cyclic behaviors in retry logic (re-test)

**Loop-14 score:** 2 (mod missed — simulation used instead)

**Post-fix:** use_when "repeats across cycles", "cyclic behavior", "periodic pattern" → mod
- User: "patterns repeat across retry cycles — are there cyclic behaviors"
- "repeats across cycles" fires ✅; "cyclic behaviors" fires ✅ (exact match)

**Bar command (post-fix):** `bar build probe fail full mod`

**Scores:** fitness 5, completeness 4, correctness 5, clarity 4 → **Overall: 4** ✅

---

## T223 — Service mesh routing through shared infrastructure (re-test)

**Loop-14 score:** 1 (field missed — mapping/struct used instead)

**Post-fix:** use_when "shared infrastructure", "service mesh routing", "effects propagate" → field
- User: "shared mesh infrastructure... why does traffic route the way it does"
- "service mesh routing" fires ✅; "shared infrastructure" fires ✅

**Bar command (post-fix):** `bar build show full field`

**Scores:** fitness 4, completeness 4, correctness 4, clarity 4 → **Overall: 4** ✅

---

## Part A Summary

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| T221 | meld | 2 | 4 | +2 | PASS |
| T222 | mod | 2 | 4 | +2 | PASS |
| T223 | field | 1 | 4 | +3 | PASS |

**Mean pre-fix:** 1.67 → **Mean post-fix:** 4.0 ✅

---

# Part B — General Health Check

**Purpose:** Verify that cumulative loop-1–14 improvements hold together across the full
token catalog. 10 diverse tasks drawing from multiple axes simultaneously.

**Evaluation criteria:** Each task should score ≥4 on overall coverage rubric. Tasks that
score ≤3 indicate either a new gap or a cross-axis interaction issue.

---

## GH-T01 — Refactor authentication service incrementally

**Task:** "Refactor our authentication service to separate the session management from token validation. Start with the absolute minimum change, coordinate the rollout with the platform team, and avoid breaking existing integrations."

**Expected tokens:** make minimal grow (completeness+method) + melody (method) + stable (scope)

**Skill selection:**
- Task: make (creating the refactored output)
- Completeness: minimal ("absolute minimum change" → minimal use_when ✅)
- Scope: stable ("avoid breaking existing integrations" → stable use_when "won't change" ✅)
- Method: grow ("start minimal" → grow use_when "YAGNI/minimum viable" ✅)
         melody ("coordinate rollout with platform team" → melody use_when "coordinate across teams" ✅)
- Max 3 methods: grow + melody + (depends optional for dependency tracking)

**Bar command:** `bar build make minimal stable grow melody`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 4 → **Overall: 5** ✅

**Notes:** This task fires use_when triggers from loops 11 (minimal), 12 (stable), and 13
(grow, melody) simultaneously — the first true cross-loop compound verification.

---

## GH-T02 — Diagnose recurring authentication outages

**Task:** "We've had three authentication outages this month. Help me work backward from the worst possible failure to find what's keeping this problem alive."

**Expected tokens:** probe fail full inversion + systemic (method)

**Skill selection:**
- Task: probe
- Scope: fail ("outages", "worst possible failure")
- Method: inversion ("work backward from worst possible failure" → inversion notes ✅)
         systemic ("what's keeping this problem alive" → "feedback loops" in systemic ✅)

**Bar command:** `bar build probe fail full inversion systemic`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

---

## GH-T03 — Session plan for a distributed team retrospective

**Task:** "Create a session plan for a retrospective with our distributed team — 2 hours, needs to work well for remote participants across timezones."

**Expected tokens:** plan act full sync (channel) + remote (channel) — wait, only 1 channel allowed.
Resolves to: sync (session plan, higher specificity) + facilitate (form) + remote (channel — delivery optimization)

**Skill selection:**
- Task: plan
- Scope: act (action steps)
- Completeness: full
- Form: facilitate ("retrospective" → facilitate use_when ✅)
- Channel: sync ("session plan" → sync use_when ✅) — sync wins over remote here (sync = structure; remote = delivery optimization; can only pick one)

**Bar command:** `bar build plan act full facilitate sync`

**Scores:** fitness 4, completeness 4, correctness 4, clarity 4 → **Overall: 4** ✅

**Notes:** remote channel would add value but channel axis allows only 1. sync is the right
primary choice. This is an acceptable constraint within the grammar.

---

## GH-T04 — Quick overview of CQRS for a standup

**Task:** "Give me a brief overview of CQRS — I need to explain it at the standup, keep it very brief."

**Expected tokens:** show mean gist (completeness)

**Skill selection:**
- Task: show
- Scope: mean ("what CQRS means" → mean ✅)
- Completeness: gist ("brief overview", "standup", "very brief" → gist use_when ✅)

**Bar command:** `bar build show mean gist`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

---

## GH-T05 — API quality criteria from ops perspective

**Task:** "What makes our REST API well-designed from the operations team's perspective — what quality criteria matter most to them?"

**Expected tokens:** check good view (scope x2)

**Skill selection:**
- Task: check (evaluating against criteria)
- Scope: good ("quality criteria", "well-designed" → good use_when ✅)
         view ("from the operations team's perspective" → view use_when ✅)
- Two scope tokens used (max 2 allowed): good + view

**Bar command:** `bar build check good view full`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

**Notes:** First test of good + view scope combination — both use_when entries fire
independently and compose cleanly.

---

## GH-T06 — What assumptions underlie our microservices boundaries

**Task:** "What assumptions are we making about service ownership and data boundaries that might not hold as our team grows?"

**Expected tokens:** probe assume full + unknowns (method)

**Skill selection:**
- Task: probe
- Scope: assume ("what assumptions are we making" → assume use_when ✅)
- Method: unknowns ("might not hold" → unknowns: "surface critical unknown unknowns")
- Completeness: full

**Bar command:** `bar build probe assume full unknowns`

**Scores:** fitness 5, completeness 4, correctness 4, clarity 4 → **Overall: 4** ✅

---

## GH-T07 — Recurring patterns in how teams handle technical debt

**Task:** "What recurring patterns appear in how different teams handle technical debt across our engineering org?"

**Expected tokens:** probe motifs full

**Skill selection:**
- Task: probe
- Scope: motifs ("recurring patterns" → motifs use_when ✅, exact match)
- Completeness: full

**Bar command:** `bar build probe motifs full`

**Scores:** fitness 5, completeness 4, correctness 5, clarity 4 → **Overall: 4** ✅

---

## GH-T08 — Balance service autonomy vs. shared libraries constraint

**Task:** "We need to decide how much to share code in common libraries vs. let each service own its own implementation. Find the right balance between autonomy and standardization."

**Expected tokens:** pick full meld (method)

**Skill selection:**
- Task: pick (selecting from alternatives)
- Method: meld ("balance between autonomy and standardization" → meld use_when "balance between" ✅)
         compare ("decide how much to share vs. own" → compare)
- Completeness: full

**Bar command:** `bar build pick full meld compare`

**Scores:** fitness 4, completeness 4, correctness 4, clarity 4 → **Overall: 4** ✅

---

## GH-T09 — Spot check the deployment pipeline for obvious issues

**Task:** "Do a quick spot check of our deployment pipeline — just flag any obvious problems, don't go deep."

**Expected tokens:** check skim (completeness) fail

**Skill selection:**
- Task: check (evaluating)
- Completeness: skim ("spot check", "just flag obvious problems", "don't go deep" → skim use_when ✅)
- Scope: fail (looking for problems)

**Bar command:** `bar build check fail skim`

**Scores:** fitness 5, completeness 5, correctness 5, clarity 5 → **Overall: 5** ✅

---

## GH-T10 — What breaks at extreme message queue load

**Task:** "Our message queue handles 50k msg/s normally. What happens to our downstream processors at 10x that load — what breaks first and what dominates?"

**Expected tokens:** probe fail full boom

**Skill selection:**
- Task: probe
- Scope: fail (breakdowns)
- Method: boom ("at 10x that load", "what breaks first", "what dominates" → boom use_when ✅)
- Completeness: full

**Bar command:** `bar build probe fail full boom`

**Scores:** fitness 5, completeness 4, correctness 5, clarity 4 → **Overall: 4** ✅

---

## Part B Summary — General Health Check

| Task | Key tokens | Score |
|------|-----------|-------|
| GH-T01 | minimal + stable + grow + melody | 5 |
| GH-T02 | fail + inversion + systemic | 5 |
| GH-T03 | act + facilitate + sync | 4 |
| GH-T04 | mean + gist | 5 |
| GH-T05 | good + view | 5 |
| GH-T06 | assume + unknowns | 4 |
| GH-T07 | motifs | 4 |
| GH-T08 | meld + compare | 4 |
| GH-T09 | fail + skim | 5 |
| GH-T10 | fail + boom | 4 |

**Mean: 4.5/5** ✅ (well above 4.0 target)

**No new gaps found.** All 10 tasks scored ≥4. No cross-axis interaction failures.

### Loop-1–14 Fix Verification

Tasks GH-T01–GH-T10 collectively verified fixes from:
- Loop-10 (channel: sync) ✅ GH-T03
- Loop-11 (completeness: gist, skim) ✅ GH-T04, GH-T09
- Loop-12 (scope: assume, good, motifs, stable) ✅ GH-T01, GH-T05, GH-T06, GH-T07
- Loop-13 (method: boom, grow, melody) ✅ GH-T01, GH-T10
- Loop-14 (method: meld) ✅ GH-T08

All fixes hold. No regressions detected.
