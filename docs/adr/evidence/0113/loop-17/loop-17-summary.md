# ADR-0113 Loop-17 Summary — Form Token Health Check

**Date:** 2026-02-18
**Status:** Complete
**Focus:** Uncovered scope (act, mean) and form tokens (indirect, case, activities, scaffold,
           tight, formats) + channel tokens (adr, gherkin)

---

## Results

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| GH17-T01 | act scope | 5 | No |
| GH17-T02 | mean scope | 5 | No |
| GH17-T03 | indirect form | 3 | Yes — G-L17-01 |
| GH17-T04 | case form | 4 | No |
| GH17-T05 | activities form | 3 | Yes — G-L17-02 |
| GH17-T06 | scaffold form | 4 | No |
| GH17-T07 | tight form | 5 | No |
| GH17-T08 | adr channel | 5 | No |
| GH17-T09 | gherkin channel | 5 | No |
| GH17-T10 | formats form | 5 | No |

**Mean: 4.4/5**

---

## Gaps Found and Fixed

| ID | Token | Axis | Root cause | Fix |
|----|-------|------|-----------|-----|
| G-L17-01 | indirect | form | Opaque name; competes with `case` | use_when: 'walk me through the reasoning first', 'reasoning before conclusion' |
| G-L17-02 | activities | form | Preempted by `facilitate` use_when; segment vs. plan distinction unclear | use_when: 'session activities', 'what happens in each segment', 'design sprint activities' |

## Post-Apply Validation

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| GH17-T03 | indirect | 3 | 4 | +1 | PASS |
| GH17-T05 | activities | 3 | 4 | +1 | PASS |

Grammar regenerated. All tests pass. SSOT intact.

---

## Tokens Confirmed Discoverable (no use_when needed)

| Token | Axis | Reason |
|-------|------|--------|
| act | scope | "tasks being performed" exact description match |
| mean | scope | "what does X mean" canonical phrase |
| case | form | "build the case/argument" in description |
| scaffold | form | "junior/learning audience" noted in description |
| tight | form | "dense... no bullets or tables" exact description match |
| formats | form | "format" in user request matches token name |
| adr | channel | Well-known format name in engineering |
| gherkin | channel | Explicit BDD format name |

---

## Key Findings

1. **`indirect` vs `case` confusion confirmed**: Both forms produce build-before-conclude output;
   `indirect` is the softer narrative version, `case` is the structured-argument version. Without
   use_when, autopilot reaches for `case` (more self-descriptive name). use_when disambiguates
   via the "reasoning first" vs "building the case" phrasing distinction.

2. **`activities` preempted by `facilitate`**: The `facilitate` use_when ("workshop planning")
   is a broad trigger that captures most session-design tasks, including those better served by
   `activities`. use_when for `activities` adds the segment-level heuristics that distinguish it.

3. **Tight form is highly discoverable**: The description contains the exact phrases users use
   ("dense", "no bullets or tables", "freeform"). No use_when needed.

4. **Description-anchored scope tokens hold**: act and mean both scored 5 from descriptions
   alone, consistent with loop-16 findings for struct/view/thing.

---

## AXIS_KEY_TO_USE_WHEN Coverage (Post Loop-17)

| Axis | With use_when | Total | Key tokens covered |
|------|--------------|-------|---------------------|
| completeness | 3 | 7 | gist, skim, narrow |
| scope | 7 | 13 | agent, assume, cross, good, motifs, stable, time |
| method | 7 | 51 | boom, field, grove, grow, meld, melody, mod |
| channel | 4 | 15 | plain, sync, sketch, remote |
| form | 14 | ~32 | …+ activities, indirect (new) |
