# ADR-0113 Loop-11 Summary — Channel Post-Apply Validation + Completeness Axis

**Date:** 2026-02-18
**Status:** Complete
**Focus:** Part A — Post-apply validation of loop-10 channel fixes
           Part B — Completeness axis discoverability

---

## Part A — Post-Apply Validation: Loop-10 Channel Fixes

Re-evaluated 4 previously gapped tasks after loop-10 added use_when entries and
usage patterns for `plain`, `sync`, `sketch`, and `remote` channels.

**SSOT check:** `AXIS_KEY_TO_USE_WHEN` in `lib/axisConfig.py` is intact (all 4 channel
entries present). No regression this loop.

| Task | Channel | Pre-fix | Post-fix | Delta | Verdict |
|------|---------|---------|---------|-------|---------|
| T188 | sync | 3 | 4 | +1 | PASS |
| T189 | sketch | 3 | 4 | +1 | PASS |
| T190 | plain | 3 | 5 | +2 | PASS |
| T193 | remote | 3 | 4 | +1 | BORDERLINE PASS |

**Mean pre-fix:** 3.0 → **Mean post-fix:** 4.25 ✅ (target ≥4.0)

### Fix Analysis

**T188 — sync:** "session plan" trigger fires cleanly. Usage pattern + use_when both
present. `sync` is now the natural choice for "session plan" phrasings. PASS.

**T189 — sketch:** "D2 diagram" trigger fires cleanly. D2/Mermaid disambiguation now
explicit. Users who say "D2 diagram" route to sketch; users who say "diagram" route to
diagram (Mermaid). Correct behavior. PASS.

**T190 — plain:** Strongest fix. "No lists, no bullets, just flowing paragraphs" hits
three heuristic triggers simultaneously. usage pattern + use_when align. PASS (score 5).

**T193 — remote:** Borderline. "distributed session" fires for "distributed engineering
team"; "needs to work well in a remote setting" is recognized as delivery goal. The
use_when note ("team being remote ≠ remote channel") adds nuance but residual ambiguity
remains. A second usage pattern for remote (e.g., retrospective + remote) would
strengthen further. BORDERLINE PASS.

### Part A Conclusion

✅ All 4 loop-10 channel fixes confirmed to land
✅ Mean improved from 3.0 → 4.25 (above 4.0 target)
⚠️ T193 (remote) borderline — consider adding a usage pattern for remote+facilitate

---

## Part B — Completeness Axis Discoverability

### Summary

| Task | Expected Token | Autopilot Selection | Score | Gap? |
|------|----------------|---------------------|-------|------|
| T196 | gist | full (default) | 3 | Yes — G-L11-01 |
| T197 | max | max | 4 | No |
| T198 | minimal | minimal | 4 | No |
| T199 | deep | deep | 5 | No |
| T200 | gist/skim | full (default) | 2 | Yes — G-L11-01/02 |

**Mean score (Part B):** 3.6/5 — below 4.0 target

### Central Finding

**Completeness tokens split into two discoverability tiers:**

**Tier 1 — Self-describing (no use_when needed):**
- `deep`: "deep dive" → deep (idiomatic, near-self-naming)
- `minimal`: "smallest change" → minimal (semi-self-naming)
- `max`: "exhaustive" → max (word-for-word in description)
- `full`: default — autopilot picks this when uncertain (correct for most tasks)

**Tier 2 — Undiscoverable without routing heuristic:**
- `gist`: "quick/brief/overview" → no heuristic → autopilot defaults to `full`
- `skim`: "light pass/quick review" → no heuristic → autopilot defaults to `full`
- `narrow`: very small slice → no known task phrasing routes here

### Gaps Found

**G-L11-01 — gist: No use_when for "brief/quick/overview" requests**
- Severity: High — very common user phrasings; response is over-thorough without gist
- Fix: Add use_when — "quick", "brief", "overview", "tldr", "standup" → gist

**G-L11-02 — skim: No use_when for "light pass/spot check" requests**
- Severity: Medium — skim serves a distinct review use case that gist doesn't cover
- Fix: Add use_when — "light review", "spot check", "quick pass", "just obvious issues" → skim

**G-L11-03 — narrow: No routing path**
- Severity: Low — narrow is a niche token; no natural trigger phrase found
- Fix: Add use_when — "specifically", "only", "just this part" → narrow

### Recommendations

| Rec | Token | Action | Severity |
|-----|-------|--------|----------|
| R-L11-01 | gist | add use_when to AXIS_KEY_TO_USE_WHEN["completeness"] | High |
| R-L11-02 | skim | add use_when to AXIS_KEY_TO_USE_WHEN["completeness"] | Medium |
| R-L11-03 | narrow | add use_when to AXIS_KEY_TO_USE_WHEN["completeness"] | Low |

---

## Pattern: AXIS_KEY_TO_USE_WHEN Coverage Gaps

Loop-11 reveals a structural gap: `AXIS_KEY_TO_USE_WHEN` only covers `channel` and
`form` axes. The `completeness`, `scope`, and `method` axes have no use_when entries.

| Axis | use_when coverage | Discoverability |
|------|------------------|----|
| channel | 4 of ~15 tokens | Good (explicit naming helps for named outputs) |
| form | 9 of ~32 tokens | Good (explicit naming helps) |
| completeness | **0 of 7 tokens** | Poor for gist/skim/narrow |
| scope | **0 of 13 tokens** | Unknown — not tested this loop |
| method | **0 of 51 tokens** | Variable — tested in prior loops |

The `completeness` axis is the first tested where **the default token (`full`) is also
the safe fallback** — so gaps are less catastrophic than for specialist channels/forms,
but still produce sub-optimal responses for users who want brevity.

---

## Loop History (Updated)

| Loop | Focus | Mean Score |
|------|-------|------------|
| Loop-5 | Scope validation | 4.875 |
| Loop-6 | Token guidance (ADR-0128) | 4.5 |
| Loop-7 | Directionals + persona | 4.75 |
| Loop-8 | Specialist forms | 3.38 |
| Loop-9 | Post-apply validation (loop-8) | 5.0 |
| Loop-10 | Output channels | 4.15 |
| **Loop-11A** | **Post-apply validation (loop-10)** | **4.25** ✅ |
| **Loop-11B** | **Completeness axis** | **3.6** ⚠️ |

---

## SSOT Check

`AXIS_KEY_TO_USE_WHEN` in `lib/axisConfig.py` is intact (no regression this loop).
Regression has occurred after loops 9 and 10. Monitoring continues.

---

## Next Actions

1. Apply R-L11-01: Add `gist` use_when to AXIS_KEY_TO_USE_WHEN["completeness"] (High)
2. Apply R-L11-02: Add `skim` use_when to AXIS_KEY_TO_USE_WHEN["completeness"] (Medium)
3. Apply R-L11-03: Add `narrow` use_when to AXIS_KEY_TO_USE_WHEN["completeness"] (Low)
4. Regenerate grammar files (`make bar-grammar-update`) — **check git diff on axisConfig.py first**
5. Post-apply validation: re-test T196 and T200 after adding use_when entries
6. Optional: Add usage pattern for remote+facilitate (T193 borderline improvement)
7. Consider testing scope axis discoverability in loop-13 (0 use_when entries for 13 tokens)
