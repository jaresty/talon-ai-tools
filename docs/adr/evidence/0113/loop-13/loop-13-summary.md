# ADR-0113 Loop-13 Summary — Scope Post-Apply + Method Axis (Metaphorical Tokens)

**Date:** 2026-02-18
**Status:** Complete
**Focus:** Part A — Post-apply validation of loop-12 scope fixes (T204, T205, T207, T210)
           Part B — Method axis discoverability (10 tasks, metaphorical token focus)

---

## Part A — Post-Apply Validation: Loop-12 Scope Fixes

| Task | Scope | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| T204 | time | 3 | 4 | +1 | PASS |
| T205 | agent | 2 | 5 | +3 | PASS |
| T207 | motifs | 2 | 5 | +3 | PASS |
| T210 | stable | 2 | 5 | +3 | PASS |

**Mean pre-fix:** 2.25 → **Mean post-fix:** 4.75 ✅

Three tasks scored 5 — the strongest validation result of any loop to date.
Exact phrase matches in use_when ("recurring patterns", "unlikely to change",
"who can approve") produce near-certain routing vs. the synonym-matching
that previously failed.

---

## Part B — Method Axis: Metaphorical Token Discoverability

### Task Scores

| Task | Target Method | Score | Gap? |
|------|--------------|-------|------|
| T211 | boom | 2 | Yes — G-L13-01 |
| T212 | grove | 1 | Yes — G-L13-02 |
| T213 | melody | 2 | Yes — G-L13-03 |
| T214 | bias | 4 | No |
| T215 | origin | 4 | No |
| T216 | simulation | 4 | No |
| T217 | jobs | 4 | No |
| T218 | grow | 2 | Yes — G-L13-04 |
| T219 | inversion | 5 | No |
| T220 | systemic | 5 | No |

**Mean score (Part B):** 3.3/5 — below 4.0 target

### Central Finding

**Metaphorical method names are the method axis's equivalent of undiscoverable channels.**
Tokens with evocative but non-literal names (`boom`, `grove`, `melody`, `grow`) have zero
routing path regardless of how well the description matches the user's intent. The pattern
mirrors the channel axis (loop-10: `sync`, `sketch`, `remote`, `plain`) and form axis
(loop-8: specialist forms like `wardley`, `wasinawa`, `spike`).

Description-anchored tokens (`bias`, `origin`, `simulation`, `inversion`, `systemic`, `jobs`)
are well-discoverable — the description provides enough synonym density to route correctly.

### Fixes Applied

| Rec | Token | When to use |
|-----|-------|-------------|
| R-L13-01 | boom | "at 10x", "extreme load", "what breaks at scale", "pushed to the limit" |
| R-L13-02 | grove | "compound", "accumulates over time", "feedback loop", "snowball", "network effect" |
| R-L13-03 | melody | "coordinate across teams", "synchronize changes", "coupling between components" |
| R-L13-04 | grow | "YAGNI", "start simple and expand", "minimum viable", "don't over-engineer" |

Grammar regenerated. All tests pass (ok 1.638s). SSOT intact.

---

## Loop History (Updated)

| Loop | Focus | Mean Score |
|------|-------|------------|
| Loop-10 | Output channels | 4.15 |
| Loop-11A | Post-apply (loop-10 channels) | 4.25 |
| Loop-11B | Completeness axis | 3.6 |
| Loop-12A | Post-apply (loop-11 completeness) | 4.0 |
| Loop-12B | Scope axis | 3.2 |
| **Loop-13A** | **Post-apply (loop-12 scope)** | **4.75** ✅ |
| **Loop-13B** | **Method axis (metaphorical tokens)** | **3.3** ⚠️ |

---

## SSOT Status (Current)

| Axis | Tokens with use_when | Total |
|------|---------------------|-------|
| completeness | 3 (gist, skim, narrow) | 7 |
| scope | 6 (agent, assume, good, motifs, stable, time) | 13 |
| method | 4 (boom, grove, grow, melody) | 51 |
| channel | 4 (plain, sync, sketch, remote) | 15 |
| form | 9 | ~32 |

Method axis: 4 of 51 covered (47 remaining). Most of the 47 are likely
description-discoverable. Next pass should verify the remaining metaphorical tokens:
`meld`, `mod`, `field`, and `shift`.

---

## Next Actions

- Post-apply validate loop-13 method fixes (re-test T211, T212, T213, T218)
- Continue method axis sampling: `meld`, `mod`, `field`, `shift` (remaining metaphorical tokens)
- Or pivot to task axis (11 tokens, 0 use_when) for completeness
