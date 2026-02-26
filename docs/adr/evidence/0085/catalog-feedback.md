# ADR-0085: Catalog Feedback
**Date:** 2026-02-25
**Cycles covered:** 16–19 (seeds 456–615)
**Meta-analysis method:** `bar build probe full domains gap`

---

## Issues Discovered via Meta-Analysis

### Issue 1 — `narrow` guidance not in installed binary (Release lag, R37)

**Trigger seed:** 466 (`sort narrow fig as-programmer`, score 3)

The R37 fix (cycle 16) added a `narrow` entry to `AXIS_KEY_TO_GUIDANCE["completeness"]` in `lib/axisConfig.py`:

> "Restricts discussion to a small topic slice. Compound directionals (fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog) work with narrow but the combination examines the slice from multiple analytical dimensions simultaneously — cognitively demanding. If multi-dimensional analysis is the goal, prefer full or deep completeness so the directional can range freely."

This guidance IS present in `build/prompt-grammar.json` (dev repo). But the installed bar binary at `/opt/homebrew/bin/bar` (currently 2.64.1) does not include this guidance — `bar help llm` does not show it under the Completeness section of Composition Rules, and the `narrow` token catalog entry shows empty Notes.

**Impact:** An LLM using the installed bar binary won't see the R37 warning. Users relying on `bar help llm` for the narrow+compound directional tradeoff receive no signal.

**Root cause:** Dev repo fixes via `make bar-grammar-update` update JSON files but NOT the installed binary. The binary embeds its own grammar at compile time. A Homebrew release is required to propagate guidance fixes.

**Action:** Needs a bar release to propagate. Track in release notes when R37 (and future guidance fixes) reach the installed binary.

---

### Issue 2 — `skim` Composition Rules note has incomplete compound directional list

**Trigger seed:** 533 (`plan skim grow dip-rog`, score 2, R36)

Current skim Composition Rules note in installed binary:
> "Quick-pass constraint: most obvious or critical issues only. Avoid pairing with multi-phase directionals (bog, fip rog, fly rog, fog) that require structural depth and sustained examination. Use with simple directionals (jog, rog) or none."

This lists only 4 specific directionals. R36 covers ALL compound directionals (fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog) plus fog. The list is misleading — a user reading it would think dip-rog, dip-ong, dip-bog, fip-ong, fip-bog, fig, fly-ong are safe with skim.

**Contrast:** The "Choosing Directional" section in bar help llm correctly says:
> "Avoid pairing [compound directionals] with `gist` or `skim` completeness."

The two sections are inconsistent. The Choosing Directional section is correct; the skim Composition Rules note is incomplete.

**Recommendation:** Replace the specific list with the general rule:
```python
# In lib/axisConfig.py AXIS_KEY_TO_GUIDANCE["completeness"]["skim"]
"skim": (
    "Quick-pass constraint: most obvious or critical issues only. "
    "Avoid pairing with any compound directional (fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, "
    "fip-bog, fip-rog, dip-ong, dip-bog, dip-rog) or fog — these require structural depth and "
    "sustained examination that a light pass cannot accommodate. "
    "Use with simple directionals (jog, rog, ong, dig) or none."
)
```

**Evidence:** Cycle-18 seed 541 (gist+dip-rog=2), cycle-18 seed 558 (skim+fog=2), cycle-18 seed 568 (skim+fog=2), cycle-17 seed 533 (skim+dip-rog=2) all confirm this. gist's guidance already says "Avoid pairing with compound directionals (fig, bog, fly-ong, fly-bog, fly-rog, fip-ong, fip-bog, fip-rog, dip-ong, dip-bog, dip-rog)" — the complete list. Skim should match.

---

### Issue 3 — `adr` channel's "avoid with pull" caveat and form-as-lens rescue

**Trigger seed:** 599 (`pull max act balance ladder adr fog`, score 4)

adr channel guidance says: "Avoid with sort (sorted list), pull (extraction), diff (comparison), or sim (scenario playback)."

Seed 599 scored 4 despite pull+adr because `ladder` (form) + `adr` (channel) = form-as-lens: ladder shapes the extraction as a hierarchical scaffold within the ADR structure. The output is a valid artifact: an ADR-structured ladder describing the extracted content.

This raises a question about whether "Avoid with pull" should be softened or made conditional on the form token. The avoidance note is for the case where no form token reframes the output — a bare pull+adr would produce an awkward ADR structured around extracted data rather than a decision.

**Recommendation:** Clarify the adr guidance note:
> "Avoid with sort, pull, diff — these don't produce decision artifacts. Exception: when a form token like `ladder` or `case` is also present, it may provide a content lens that reframes the task as a decision-adjacent structure (pull+ladder+adr = a hierarchical extraction organized as an ADR; whether this is coherent depends on the subject)."

---

### Issue 4 — "Grammar-enforced restrictions" section is empty

**Observation:** The `bar help llm` Composition Rules section ends with:
```
**Grammar-enforced restrictions:**
```
...followed immediately by the next section header. The section has no content.

**Impact:** Creates a false impression that there are no grammar-enforced restrictions (which is technically true) but also that all documented restrictions ARE grammar-enforced (which is false — all cross-axis incompatibilities are documentation-only).

**Recommendation:** Fill the section with an honest statement:
```
**Grammar-enforced restrictions:**
None currently exist for cross-axis token pairs. All documented incompatibilities
(shellscript+task type, commit+max completeness, adr+task type) are advisory only —
the grammar permits them but the LLM should apply the guidance notes above.
Grammar restrictions are enforced only for single-axis conflicts (e.g., two channel
tokens, exceeding scope/method/directional capacity limits).
```

---

## Release Lag Tracking

| Fix | Applied in cycle | In dev grammar JSON | In installed binary (2.64.1) | Action needed |
|-----|-----------------|--------------------|-----------------------------|---------------|
| R37 narrow guidance | 16 | ✅ Yes | ❌ No | Needs bar release |
| R36 gist note | 11 | ✅ Yes | ✅ Yes (predates cycles 16–19) | None |
| R36 skim note | 11 | ✅ Yes | ✅ Yes (partial — list incomplete) | Fix list → release |
| R38 max+sync note | 15 | ✅ Yes | ✅ Yes | None |
| shellscript notes | Pre-16 | ✅ Yes | ✅ Yes | None |
| commit notes | Pre-16 | ✅ Yes | ✅ Yes | None |

---

## Recommendations for Catalog

| Priority | Token | Issue | Recommendation |
|----------|-------|-------|----------------|
| High | `skim` | Incomplete compound directional list in Composition Rules note | Replace specific list with "all compound directionals + fog" |
| Medium | `narrow` | Guidance in dev grammar but not in installed binary | Release bar with R37 note propagated |
| Medium | `adr` | "Avoid with pull" doesn't explain form-as-lens rescue | Add conditional exception |
| Medium | (grammar) | "Grammar-enforced restrictions" section is empty | Add honest statement about advisory-only restrictions |
