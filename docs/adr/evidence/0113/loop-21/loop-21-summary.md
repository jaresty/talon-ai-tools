# ADR-0113 Loop-21 Summary — Directional Token Discoverability

**Date:** 2026-02-18
**Status:** Complete
**Focus:** All 16 directional tokens — none had use_when coverage. Tested primitives
           (jog, dig, fog, rog, ong, bog, fig) + compound tokens (fly-rog, fly-ong, dip-rog).

---

## Results

| Task | Key token | Score | Gap? |
|------|----------|-------|------|
| L21-T01 | jog | 3 | Yes |
| L21-T02 | dig | 3 | Yes |
| L21-T03 | fog | 3 | Yes |
| L21-T04 | rog | 4 | Yes (axis-level) |
| L21-T05 | ong | 4 | Yes (axis-level) |
| L21-T06 | bog | 2 | Yes |
| L21-T07 | fly-rog | 3 | Yes (compound) |
| L21-T08 | fly-ong | 3 | Yes (compound) |
| L21-T09 | fig | 4 | Partial |
| L21-T10 | dip-rog | 3 | Yes (compound) |

**Mean: 3.2/5** — lowest since loops 12–14.

---

## Root Cause: Entire Directional Axis Uncovered

The directional axis had **zero** use_when coverage. `AXIS_KEY_TO_USE_WHEN` had no
`"directional"` key at all. Autopilot never consulted the directional axis because there
was no signal to trigger it.

This is different from previous loops where individual tokens had gaps — here the entire
axis was invisible to the skill.

---

## Fix Applied

Added `"directional"` key to `AXIS_KEY_TO_USE_WHEN` in `lib/axisConfig.py` with use_when
for all 7 primitive/core tokens:

| Token | Heuristic phrases added |
|-------|------------------------|
| jog | 'just answer', 'don't ask me questions', 'make a call', 'don't hedge', 'just tell me' |
| dig | 'be concrete', 'give me specific examples', 'not abstract — real examples', 'make it tangible' |
| fog | 'step back and tell me the general principle', 'abstract away', 'what's the big picture', 'zoom out' |
| rog | 'describe the structure then tell me what it means', 'how is it organized and what does that reveal' |
| ong | 'what actions should I take and what comes next after each', 'give me the actions with follow-on steps' |
| bog | 'look at the structure, reflect on what it means, then tell me what to do', 'structure → meaning → action' |
| fig | 'alternate between the theory and examples', 'interleave concept and example' |

**Compound tokens** (fly-rog, fly-ong, fip-rog, fip-ong, dip-rog, dip-bog, dip-ong, fly-bog,
fip-bog): not given individual use_when — compounds are built from primitives and discovered
via `bar shuffle`. Now that primitives have use_when, compounds become reachable via composition.
The catalog note directs users to `bar shuffle --json` for compound discovery.

---

## Post-Apply Validation

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| L21-T01 | jog | 3 | 4 | +1 | PASS — 'just answer / make a call' now anchored |
| L21-T02 | dig | 3 | 4 | +1 | PASS — 'be concrete / specific examples' now anchored |
| L21-T03 | fog | 3 | 4 | +1 | PASS — 'step back / general principle / big picture' now anchored |
| L21-T06 | bog | 2 | 3 | +1 | PASS — 'structure → meaning → action' now anchored (complex 3-phase still needs discovery) |

Grammar regenerated. All tests pass. SSOT intact.

---

## Key Insight: Axis-Level vs Token-Level Gaps

Previous loops fixed individual token gaps (a token exists but its use_when is missing).
Loop-21 reveals a different failure mode: **an entire axis with no use_when coverage**.
Without any entry in `AXIS_KEY_TO_USE_WHEN["directional"]`, autopilot would never look at
directional tokens — even for tasks where directionals add real value.

**Implication:** After fixing individual token gaps, it's worth doing periodic axis-level
checks to ensure no entire axis has been missed. The directional axis went undetected for
21 loops.

---

## Program-Level Status (Post Loop-21)

| Axis | use_when coverage |
|------|-----------------|
| task (static) | sim + notes for fix/probe/pull/show |
| completeness | gist, skim, narrow |
| scope | agent, assume, cross, good, motifs, stable, time |
| method | abduce, boom, field, grove, grow, induce, jobs, meld, melody, mod, simulation, trans |
| form | activities, cocreate, contextualise, facilitate, indirect, ladder, questions, recipe, socratic, spike, taxonomy, visual, walkthrough, wardley, wasinawa |
| channel | plain + others from loop-10 |
| directional | **NEW (loop-21)**: bog, dig, fig, fog, jog, ong, rog |

All axes now have at least partial use_when coverage. **Re-trigger on new tokens or failure
reports.**
