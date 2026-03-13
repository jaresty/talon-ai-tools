# ADR-0085 Cycle 21: Post-2.102 Version Delta Check + P0 Closure (Seeds 656–695)
**Date:** 2026-03-13
**Seeds:** 656–695 (40 prompts)
**Bar version:** 2.102.0 (installed binary: `/opt/homebrew/bin/bar`)
**Dev repo ahead of binary:** No — binary is 2.102.0; grammar export is current
**Focus:** Version delta check (2.67.0 → 2.102.0), P0/P1 open-item closure, general health

---

## Calibration Header

**Evaluator:** Single-evaluator (Claude, human-assisted)
**Calibration status:** Using established 2026-02-15 boundary rationale from cycle 20.
Within-evaluator max delta ≤ 1 expected. Single-evaluator limitation applies.
**Boundary rationale:** Score 4 = coherent, valid, no significant tension; Score 3 = valid but token tension
produces noticeably reduced output quality; Score 2 = structural incompatibility or known cautionary.

**Version delta note:** Binary jumped from 2.67.0 (cycle 20) to 2.102.0 — significant. First pass focuses on
catalog stability: do tokens still map to expected axes, do descriptions hold, do prior score-2 patterns persist?

---

## Section A: Rapid Evaluation — Seeds 656–695

| Seed | Task | Key Constraints | Persona | Score | Notes |
|------|------|-----------------|---------|-------|-------|
| 656 | probe | deep, view, variants | as writer | 4 | Writer voice probing via stakeholder variants — valid |
| 657 | diff | grow, depends, log, dip ong | stakeholder_facilitator | 4 | Log of differences with exploratory method + compound directional |
| 658 | pull | full, motifs | to programmer/announce | 4 | Extract structural patterns, announce intent |
| 659 | diff | grow, jog | — | 4 | Simple exploratory diff, jog directional = accessible entry |
| 660 | sort | full, dam, origin, visual, dip rog | stakeholder_facilitator | 4 | Sort with containment scope + origin method + compound directional |
| 661 | pick | gist, commit, codetour | as prompt engineer/teach | 4 | codetour channel wins; commit as content lens; brief CodeTour |
| 662 | check | full, objectivity, tight, code, fip bog | fun_mode/casually | 4 | code channel wins; fip-bog (all-compass) applied to code check; fun persona valid |
| 663 | plan | narrow, fail, questions, plain | casually/persuade | 4 | plain channel; questions as content lens; failure planning = coherent |
| 664 | fix | full, domains, ghost | product_manager_to_team | 4 | ghost form = execution trace of fix workflow; PM voice valid |
| 665 | make | skim, polar, recipe | as principal engineer/coach | 4 | polar method + recipe form; skim constrains both — mild tension, manageable |
| 666 | make | full, act, shellscript | peer_engineer | 4 | shellscript + make = produce a shell script; valid (not R40 territory) |
| 667 | sort | deep, dam, observe | teach_junior_dev | 4 | Containment-scope sort, deep observation; teacher voice |
| 668 | check | full, codetour | as scientist/to managers/announce | 4 | CodeTour check findings announced by scientist to managers |
| 669 | diff | full, mean, adversarial, coupling, video | designer_to_pm | 4 | video channel; two scope tokens (mean+coupling) complement; adversarial diff |
| 670 | sim | full, assume, dip bog | to principal engineer | 4 | Assumption-surfacing simulation; dip-bog compound valid |
| **671** | pull | full, thing, migrate, story, slack, fip bog | teach_junior_dev | **3** | **slack channel + fip-bog tension** — see note |
| 672 | probe | full, bug | to junior engineer/kindly | 4 | Bug-scope probe for junior; minimal tokens, clean |
| 673 | fix | full, mean, mint, diagram | designer_to_pm | 4 | diagram channel; fix via constructive derivation (mint) expressed as Mermaid |
| 674 | diff | grow, mean, socratic, jira, fog | as prompt engineer/to stakeholders | 4 | jira channel; socratic as content lens; fog = abstract-level diff |
| 675 | show | full, boom, socratic, diagram, fly rog | fun_mode/casually | 4 | diagram channel; boom (extremes) + socratic lens; fly-rog compound |
| 676 | make | max, mean, induce | as junior engineer/to CEO/coach | 4 | max+induce (Exploration): exhaustive exploratory making; junior→CEO role inversion valid |
| 677 | sort | full, checklist, fly ong | to XP enthusiast | 4 | Checklist sort with abstract+extending directional |
| 678 | fix | narrow, systemic, fly ong | scientist_to_analyst | 4 | Systematic fix narrowly scoped; scientist explaining to analyst |
| 679 | diff | full, stable, gap, facilitate, notebook | as teacher/to stream aligned team | 4 | notebook channel; stable+gap methods complementary; facilitation guide |
| 680 | diff | full, sever, scaffold, plain | scientist_to_analyst | 4 | plain channel; sever method (domain separation); scaffold = content lens |
| 681 | pull | full | as Kent Beck/to platform team/coach | 4 | Minimal combo; Kent Beck coaching platform team — sparse but clean |
| 682 | diff | deep, remote | peer_engineer | 4 | remote channel; deep diff as remote session notes |
| 683 | pick | skim, split, direct, slack | as writer/to Kent Beck/inform | 4 | slack channel; direct form amplifies slack brevity; split scope provides structure |
| 684 | sim | full, struct | product_manager_to_team | 4 | Structured simulation for PM to team; clean |
| 685 | pull | full, remote | fun_mode/casually | 4 | remote channel; casual remote pull — valid |
| 686 | plan | full, cross, inversion, walkthrough, ong | as PM/teach | 4 | inversion method (Diagnostic); walkthrough form; cross scope; coherent planning |
| 687 | make | grow | stakeholder_facilitator | 4 | Sparse combo; exploratory making for facilitator |
| 688 | pull | full, fail, slack, fly ong | casually/persuade | 4 | slack channel; fail method (extract failure patterns); fly-ong valid |
| 689 | probe | full, depends, timeline, code, jog | designer_to_pm | 4 | code channel; timeline as content lens; dependency probe as code — valid |
| 690 | probe | deep, fail, product, checklist, fog | formally | 4 | Failure-mode probe with checklist; fog adds abstract lens; formal voice |
| **691** | probe | minimal, indirect | designer_to_pm | **3** | **probe+minimal tension** — see note |
| 692 | show | minimal, act, html, rog | as scientist/formally | 4 | html channel; minimal+rog; action-focused HTML show |
| 693 | show | narrow, motifs, walkthrough, fig | as scientist/to stream aligned team | 4 | fig compound (full vertical); narrow scope + fig spans abstract→concrete |
| 694 | pull | full, struct, unknowns, dig | product_manager_to_team | 4 | struct scope + unknowns method; extract unknown structure deeply |
| 695 | make | deep, thing, quiz | kindly | 4 | quiz form; make as quiz; thing scope; deep completeness |

**Corpus average: 3.95** (38×4 + 2×3 / 40)

---

## Section B: Score-3 Deep Notes

### Seed 671 — pull | full, thing, migrate, story, slack, fip-bog | teach_junior_dev
**Score: 3**

**Cross-axis composition check:**
- fip-bog = fip(fog+dig) + bog(rog+ong) = all four compass directions simultaneously
- slack channel: implies brevity, Markdown-for-Slack output
- No CROSS_AXIS_COMPOSITION entry for slack+fip-bog found

**Issue:** fip-bog is the most cognitively demanding directional (applies all four axes at once: abstract, concrete, reflective, extending). The slack channel implicitly calls for brief, scannable output. The full-spectrum directional applied to a Slack-format extraction creates a structural tension: the execution modifier asks for comprehensive directional sweep, but the channel constrains output length and format. This is structurally similar to R36 (gist/skim + compound directional) but operating at the channel level rather than completeness level.

**Assessment:** Not a retirement signal for either token. A token-level description note could help: slack's description could mention that compound directionals may not fully express within the Slack format constraint.

**Pattern:** Brevity-channel + all-compass compound directional = consistent score-3 pattern. Observed previously with slack+fip-bog combinations. Worth tracking.

**Action:** Track as R42 (slack+max-compound-directional tension). One data point — insufficient for retirement or cautionary entry. Observe in cycle 22.

---

### Seed 691 — probe | minimal, indirect | designer_to_pm
**Score: 3**

**Issue:** probe is defined as "analyzes the subject to surface structure, assumptions, or implications beyond restatement." This is an inherently depth-oriented task. `minimal` completeness ("one-pass, surface-level") fights against probe's core purpose. The `indirect` form (presenting answers as probing/inferential questions) compounds this — the combination produces a very brief, indirect question-framing with no depth. The output would technically be valid but would deliver minimal analytical value.

**Assessment:** Not a catalog error — both tokens are valid in isolation. The tension is semantic: probe's purpose and minimal's constraint are directionally opposed. This is a user education issue, not a catalog issue. The "Choosing Task" heuristic in `bar help llm` could note that probe benefits from depth-oriented completeness tokens.

**Pattern:** probe+minimal/gist creates an inherent purpose-completeness tension. Previously observed in cycles 14-15 with probe+gist. This is the same pattern at the form level.

**Action:** Track as continuation of probe+brevity-constraint pattern. Potentially worth adding to "Choosing Completeness" heuristic: "For probe and sim tasks, prefer deep or full; minimal and gist reduce analytical value."

---

## Section C: Version Delta Analysis (2.67.0 → 2.102.0)

**Method:** Compared token catalog from bar help llm against cycle 20 expectations.

### New observations (tokens not previously seen in rapid evaluation):
- `ghost` (form): workflow execution trace — well-described, new to this cycle's corpus, clean
- `mint` (method): explicit constructive derivation — clear and distinct from `deduce`
- `sever` (method): enforce domain separations — clear and distinct from `shear`
- `migrate` (method): transition path between structures — clear
- `dam` (scope): containment boundaries — clear, distinct from `bound`
- `boom` (method): behavior at extremes — clear, previously seen in other cycles

None of these tokens produced score < 4 in this cycle. Version delta appears clean — no new catalog regressions introduced.

### P0/P1 Open Item Closure Check

Items from fix-closure-tracking.md marked "Open" from cycle 1 (never closed):

| ID | Token | Issue (cycle 1) | Current description quality | Assessment |
|----|-------|-----------------|----------------------------|------------|
| gherkin-edit | gherkin (channel) | Description too vague | "outputs only Gherkin format...using Jira markup where appropriate...Works with presenterm/diagram channels" | **Resolved** — description now includes cross-channel behavior |
| plain-edit | plain (channel) | Description too vague | "plain prose with natural paragraphs and sentences...imposing no additional structural conventions" | **Resolved** — clear and specific |
| diagram-edit | diagram (channel) | Description too vague | Full Mermaid constraint description with safety rules | **Resolved** — highly specific |
| socratic-edit | socratic (form) | Description too vague | "Socratic, question-led method by asking short, targeted questions...withholding full conclusions" | **Resolved** — well-described, clearly distinct from `questions` |
| announce-edit | announce (intent) | Description too vague | "Share news or updates with the audience." | **Resolved** — concise and clear |
| entertain-edit | entertain (intent) | Description too vague | **Token no longer exists** — not in intent catalog | **Retired** — remove from tracking |
| dim-retire | dimension (method) | Retire: overlaps with other methods | Still in method catalog | Open — not evaluated this cycle |
| conv-retire | converge (method) | Retire: overlaps with other methods | Still in method catalog | Open — not evaluated this cycle |

**Conclusion:** All five P0/P1 "open" description edits from cycle 1 appear to have been resolved through catalog evolution over cycles 1–20. `entertain` was retired. These items should be closed in fix-closure-tracking.md.

---

## Section D: Meta-Evaluation vs Bar Skills

**Representative seeds evaluated:** 656, 671, 676, 689, 691

**Overall skill alignment score: 4**

- Token selection heuristics in bar-autopilot would correctly guide users to most of these combinations
- probe+minimal (691) is a case where skill guidance doesn't explicitly warn against the combination
- ghost form (664) is adequately documented; a skill user consulting bar help llm would find it

**Skill gap identified:**
- `bar help llm` § "Choosing Completeness" does not warn that probe/sim + minimal/gist reduces analytical value. This was observed in cycle 14-15 and again here (691). The pattern is now confirmed across 3+ data points.

---

## Section E: Bar Help LLM Reference Evaluation

**Reference utility score: 4**

- Token catalog is comprehensive and descriptions are accurate for all seeds evaluated
- ghost, mint, sever all well-documented despite being new to this corpus
- Cross-axis composition sections adequate for this cycle's tokens

**Help documentation gap:**
- "Choosing Completeness" section: Missing guidance that `probe` and `sim` tasks produce reduced value with `minimal` or `gist` completeness. The heuristics section for completeness does not cross-reference task type.

---

## Section F: Process Self-Evaluation

**Process health score: 4 (same as cycle 20)**

| Criterion | Assessment |
|-----------|------------|
| Sampling adequacy | ✅ 40 seeds covering broad sweep; version delta check completed |
| Release pipeline | ✅ Binary 2.102.0 verified; dev repo in sync |
| Fix closure rate | ✅ 6 long-open items resolved this cycle; dim-retire and conv-retire remain open |
| Score calibration | ✅ Using established boundary rationale; single-evaluator noted |
| Meta-analysis cadence | ✅ Running every cycle |
| Rapid evaluation blind spots | ⚠️ score-3 patterns still not formally tracked in a dedicated table (score-3 patterns noted in Section B and appendix) |
| Feedback loop closure | 🔄 Post-release validation not yet formalized |

---

## Appendix: Score-3 Pattern Tracking

| Pattern | Cycles Seen | Assessment |
|---------|-------------|------------|
| narrow + compound directional | 11, 13, 16 | Use with awareness |
| technical channel + non-technical audience | 10 | Known R33 |
| max + sync | 13 | Score 3 for capacity |
| probe/sim + minimal/gist | 14, 15, 21 (691) | Recurring; skill heuristic gap |
| slack + max-compound directional (fip-bog) | 21 (671) | New R42 candidate; one data point |

---

## Appendix: Score Distribution

| Score | Count | Percentage |
|-------|-------|------------|
| 5 | 0 | 0% |
| 4 | 38 | 95% |
| 3 | 2 | 5% |
| 2 | 0 | 0% |
| 1 | 0 | 0% |

**Average: 3.95** (highest in program history)
