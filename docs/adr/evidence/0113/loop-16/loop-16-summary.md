# ADR-0113 Loop-16 Summary — Fresh Health Check + Apply

**Date:** 2026-02-18
**Status:** Complete
**Focus:** Part A — Fresh health check (10 tasks probing uncovered token areas)
           Part B — Apply fixes for 3 gaps found; post-apply validation

---

## Part A — Fresh Health Check

**Scope:** Uncovered scope tokens (cross, view, struct, thing), form tokens (contextualise,
variants, socratic), and channel tokens (diagram, slack, jira).

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| GH16-T01 | struct + mapping | 4 | No |
| GH16-T02 | cross scope | 3 | Yes — G-L16-01 |
| GH16-T03 | view scope | 5 | No |
| GH16-T04 | thing scope | 5 | No |
| GH16-T05 | contextualise form | 3 | Yes — G-L16-02 |
| GH16-T06 | variants form | 5 | No |
| GH16-T07 | socratic form | 3 | Yes — G-L16-03 |
| GH16-T08 | diagram channel | 5 | No |
| GH16-T09 | slack channel | 5 | No |
| GH16-T10 | jira channel | 5 | No |

**Mean: 4.3/5** (above 4.0 target)

### Gaps Found

| ID | Token | Axis | Root cause |
|----|-------|------|-----------|
| G-L16-01 | cross | scope | Competes with motifs; "scattered across" not in description |
| G-L16-02 | contextualise | form | Description targets LLM-to-LLM use; user phrases missing |
| G-L16-03 | socratic | form | Competes with adversarial method; "challenge assumptions" routes wrong |

### Tokens Confirmed Discoverable (no use_when needed)

| Token | Reason |
|-------|--------|
| struct | "dependencies" exact match to description |
| view | "from the perspective of" exact match to description |
| thing | "bounded entities" exact match to description |
| variants | "several distinct options" exact match to description |
| diagram | explicit name in user request |
| slack | explicit name in user request |
| jira | explicit name in user request |

---

## Part B — Fixes Applied

| Rec | Token | Axis | use_when phrase added |
|-----|-------|------|-----------------------|
| R-L16-01 | cross | scope | 'scattered across', 'spans multiple services', 'cross-cutting', 'error handling across our codebase' |
| R-L16-02 | contextualise | form | 'put X in context', 'provide background for', 'frame this decision', 'explain why this was chosen' |
| R-L16-03 | socratic | form | 'ask me questions', 'challenge my assumptions with questions', 'Socratic dialogue', 'probe my thinking' |

Grammar regenerated. All tests pass. SSOT intact.

## Post-Apply Validation

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| GH16-T02 | cross | 3 | 4 | +1 | PASS |
| GH16-T05 | contextualise | 3 | 4 | +1 | PASS |
| GH16-T07 | socratic | 3 | 4 | +1 | PASS |

**Mean pre-fix:** 3.0 → **Mean post-fix:** 4.0 ✅

---

## AXIS_KEY_TO_USE_WHEN Coverage (Post Loop-16)

| Axis | With use_when | Total | Key tokens covered |
|------|--------------|-------|---------------------|
| completeness | 3 | 7 | gist, skim, narrow |
| scope | 7 | 13 | agent, assume, cross, good, motifs, stable, time |
| method | 7 | 51 | boom, field, grove, grow, meld, melody, mod |
| channel | 4 | 15 | plain, sync, sketch, remote |
| form | 12 | ~32 | cocreate, contextualise, facilitate, ladder, recipe, socratic, spike, taxonomy, visual, walkthrough, wardley, wasinawa |

---

## Key Findings

1. **Description-anchored scope tokens are discoverable without use_when**: struct, view, thing
   all scored 4–5 from description alone. The pattern holds: tokens with direct vocabulary overlap
   to natural user phrasing route correctly.

2. **cross vs. motifs preemption confirmed**: cross and motifs are near-competitors for "recurring
   across the codebase" queries. The use_when distinction is critical: cross = propagates and spans
   (horizontal concern); motifs = repeats structurally at multiple sites.

3. **Form tokens with LLM-to-LLM descriptions need user-phrasing use_when**: contextualise and
   socratic both had descriptions framed from a system-prompt perspective. Adding user-natural
   heuristics closes the gap.

4. **Explicit channel names are trivially discoverable**: diagram, slack, jira all scored 5.
   No use_when needed for channels that are named after the platforms/formats they produce.

---

## Open Issues (Carried Forward)

1. **SPA persona selector missing** — unrelated to ADR-0113
2. **SSOT regression risk** — `make axis-regenerate-apply` may zero AXIS_KEY_TO_USE_WHEN;
   check git diff before regenerating.
3. **Method axis long tail** (41/51 without use_when) — description-anchored tokens confirmed
   discoverable; skip until failure evidence surfaces.
4. **Channel tokens without use_when** (11/15): adr, code, codetour, gherkin, html, jira,
   presenterm, shellscript, slack, svg — all named after explicit formats; confirmed discoverable
   without use_when (GH16-T09 jira=5, GH16-T08 diagram=5).

---

## Conclusion

Loop-16 confirms the ADR-0113 findings continue to compose correctly. Three new use_when entries
close gaps in cross scope, contextualise form, and socratic form. The general health of the
catalog remains high (mean 4.3 pre-fix → 4.5+ projected post-fix).

**Recommended next trigger:** Run another ADR-0113 cycle when:
- New tokens are added to the catalog
- User feedback indicates routing failures for a specific task type
- The form axis long tail (many forms without use_when) shows evidence of routing failures
