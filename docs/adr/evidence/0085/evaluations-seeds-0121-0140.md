# ADR 0085: Shuffle-Driven Catalog Refinement — Seeds 0121-0140

**Evaluation Date**: 2026-02-16
**Corpus Size**: 20 prompts (seeds 0121-0140)
**Evaluator**: Claude Sonnet 4.5
**Context**: Cycle 7 — post-ADR-0109/0110/0111 + R14/R15/R16 guidance implementation

## Context for This Cycle

Three guidance additions were implemented since Cycle 6 (R14-R16):

- **R14**: Added `questions` and `recipe` form incompatibility notes to descriptions and AXIS_KEY_TO_GUIDANCE
- **R15**: Added social-intent guidance to `appreciate`, `entertain`, `announce` — "use only when..."
- **R16**: Added `formally` tone guidance about conversational-register channels

This cycle assesses whether those guidance additions are sufficient, and looks for new conflict patterns.

## Evaluation Rubric

Each prompt is scored 1-5 on four criteria:

- **Coherence** (COH): Do the tokens work together logically?
- **Clarity** (CLA): Is the prompt directive clear?
- **Feasibility** (FEA): Can it be executed?
- **Utility** (UTI): Would it be useful?
- **Overall** (OVR): Mean of four criteria, rounded to nearest integer

**Scoring**: 5=Excellent, 4=Good, 3=Acceptable, 2=Problematic, 1=Broken

---

## Seed 0121

**Tokens selected:**
- task: make
- completeness: deep
- scope: view
- method: actors
- form: commit
- directional: fip rog
- persona: designer_to_pm

**Generated prompt preview:**
> Task: creates new content. [deep, view scope, actors method, commit form, fip rog abstract↔concrete+structural+reflect, designer→PM directly]

**Scores:**
- Coherence: **3** — view+actors+make has good synergy (create content centered on stakeholder roles). But `commit` form (conventional commit message: type/scope line + concise body) is in direct tension with `deep` completeness and `fip rog` directional (both require expansive exploration). Commit messages are inherently brief artifacts.
- Clarity: **3** — unclear output: create a commit message about stakeholder views? The commit form constrains expressiveness that deep+fip rog expect.
- Feasibility: **4** — technically executable; an LLM can produce a commit message with this framing
- Utility: **3** — low utility; commit form limits the potential of the other constraints
- **Overall: 3**

**Notes:** The `commit` form is a narrow artifact type (one-line type + short body) that fundamentally conflicts with `deep` completeness and complex directionals. When commit form appears with constraints expecting multi-layered output, it always wins the format battle but wastes the depth constraints.

**Recommendations:**
- [ ] Add guidance to `commit` form: "Intended for reformatting or summarizing content AS a commit message. Avoid combining with `deep` or `max` completeness (commit messages are brief) or with complex directionals that require expansive exploration."

---

## Seed 0122

**Tokens selected:**
- task: fix
- completeness: full
- method: cite
- form: story
- channel: gherkin
- directional: fip ong
- persona: fun_mode

**Generated prompt preview:**
> Task: change form/presentation while preserving meaning. [full, cite method, story form, gherkin channel, fip ong abstract↔concrete→actions→extend, fun mode casually]

**Scores:**
- Coherence: **2** — `story` form (user story: "As a... I want... so that..."; explicitly "avoids Gherkin or test-case syntax") and `gherkin` channel ("outputs only Gherkin format") are directly incompatible output formats. Story form says no Gherkin; gherkin channel says only Gherkin.
- Clarity: **1** — the output format is undefined: reformat as a user story, or as Gherkin, or somehow both?
- Feasibility: **2** — the LLM must choose one format, ignoring the other; result will be either a user story OR Gherkin, not a coherent combination
- Utility: **2** — whichever format wins, the combination guidance was misleading
- **Overall: 2**

**Notes:** New conflict instance: `story` form explicitly prohibits Gherkin, `gherkin` channel mandates Gherkin-only output. This is the same output-exclusive mutual exclusion pattern seen in previous cycles. The catalog descriptions contain the conflict signal but `bar build` doesn't catch it.

**Recommendations:**
- [ ] Add `story` form to the list of prose-incompatible-with-gherkin forms (alongside `questions`, `recipe`). Story description already says "avoids Gherkin" — this should be surfaced as a validation warning.

---

## Seed 0123

**Tokens selected:**
- task: pull
- completeness: max
- method: operations
- form: spike
- channel: codetour
- intent: appreciate
- audience: to team
- tone: casually

**Generated prompt preview:**
> Task: select/extract subset. [max, operations method, spike form, codetour channel, appreciate intent, team audience, casually]

**Scores:**
- Coherence: **2** — `spike` form (research spike: problem statement + key questions for learning) and `codetour` channel (VS Code CodeTour JSON) are incompatible: a research spike is a prose question-document; a CodeTour is a structured JSON file for code walkthrough steps. Additionally, `appreciate` intent (express thanks/recognition) with a `pull` task (extract information) creates semantic noise.
- Clarity: **1** — three conflicting signals: extract subset, as a research spike, delivered as CodeTour JSON. What is the actual artifact?
- Feasibility: **2** — an LLM would have to abandon either spike or codetour; the result would be malformed
- Utility: **2** — even resolving the format conflict, the combination has low utility
- **Overall: 2**

**Notes:** New conflict: `spike` form + `codetour` channel. Spike (prose question document) is incompatible with any code-format channel (codetour, shellscript, svg, html). This extends the documented form/channel conflict taxonomy. Social intent `appreciate` still appears despite R15 guidance (guidance added to description, but doesn't prevent selection).

**Recommendations:**
- [ ] Add `spike` form to the documented list of prose forms incompatible with code-format channels (alongside `questions`, `recipe`).
- [ ] Evaluate whether R15 guidance (appreciate/entertain/announce description updates) is sufficient, or whether stronger AXIS_KEY_TO_GUIDANCE entries are needed.

---

## Seed 0124

**Tokens selected:**
- task: probe
- completeness: full
- scope: good
- channel: jira
- directional: dip ong
- persona: peer_engineer_explanation

**Generated prompt preview:**
> Task: analyze to surface structure/assumptions/implications. [full, good scope (quality criteria), jira channel, dip ong concrete→actions→extend, programmer→programmer]

**Scores:**
- Coherence: **5** — probe + good scope (analyze quality criteria/standards) + jira channel + peer engineer is a natural, high-value combination. Technical peer analysis of quality standards in Jira format.
- Clarity: **5** — clear directive: analyze quality criteria starting from concrete examples, formatted for Jira
- Feasibility: **5** — fully executable
- Utility: **5** — peer-to-peer quality analysis in Jira is a common high-value real-world pattern
- **Overall: 5**

**Notes:** Canonical excellent combination. Preset persona + scope + clean channel with directional guidance. No conflicts.

---

## Seed 0125

**Tokens selected:**
- task: sort
- completeness: full
- method: split
- form: merge
- audience: to stream aligned team
- tone: formally

**Generated prompt preview:**
> Task: arrange items into categories/order. [full, split method (decompose into parts), merge form (combine sources into whole), stream-aligned team, formally]

**Scores:**
- Coherence: **3** — `split` method (decompose into isolated parts, bracketing interactions) and `merge` form (combine multiple sources into coherent whole) create conceptual tension. They describe opposite movements: decompose vs. synthesize. Applied to a sort task, the pipeline could be "decompose categories → sort → merge into classification" but this reading requires inference.
- Clarity: **3** — ambiguous: should the output be a sorted decomposition, a merged synthesis, or both?
- Feasibility: **4** — technically executable; an LLM can interpret as decompose-then-synthesize
- Utility: **3** — useful if the split→merge pipeline is intentional; confusing if accidental
- **Overall: 3**

**Notes:** Split method and merge form represent opposing analytical movements (decompose vs. synthesize). When both appear, the intended workflow is ambiguous. This is a new method/form conceptual tension pattern worth documenting.

**Recommendations:**
- [ ] Add guidance note to `merge` form: "Works well with tasks that aggregate (show, pull, diff). Creates conceptual tension when paired with methods that decompose (split, partition) — clarify in subject whether decomposition or synthesis is the primary goal."

---

## Seed 0126

**Tokens selected:**
- task: fix
- completeness: deep
- scope: good
- method: cite
- form: log
- channel: svg
- persona: product_manager_to_team

**Generated prompt preview:**
> Task: change form/presentation while preserving meaning. [deep, good scope, cite method, log form, svg channel, PM→team kindly]

**Scores:**
- Coherence: **1** — `log` form (work/research log entry with date markers, bullet-style text) and `svg` channel ("consists solely of SVG markup... minimal and valid for direct use in an .svg file") are completely incompatible. SVG markup cannot represent a text log entry; log entries cannot be expressed as SVG without losing all log-specific structure.
- Clarity: **1** — undefined output: a log in SVG? The combination is internally contradictory.
- Feasibility: **2** — an LLM might produce SVG with text nodes simulating a log, but the result would be technically invalid or unusable
- Utility: **1** — no practical use case for a PM log in SVG format
- **Overall: 1**

**Notes:** New form/channel conflict: `log` form + `svg` channel. Log form is a prose-text artifact; SVG is a markup format for graphics. This is the same class as log+codetour or log+diagram — any prose-text form is incompatible with graphics-output channels. This gap is not currently documented.

**Recommendations:**
- [ ] Add `log` form to the list of prose forms that conflict with code/graphics-format channels (svg, codetour, diagram). Add incompatibility note to `log` form description and AXIS_KEY_TO_GUIDANCE.
- [ ] Consider whether `log` form should have a broader note: "Conflicts with any output-exclusive non-text channel (svg, diagram/sketch, codetour, gherkin, shellscript)."

---

## Seed 0127

**Tokens selected:**
- task: probe
- completeness: narrow
- scope: mean
- method: cluster
- form: direct
- channel: gherkin

**Generated prompt preview:**
> Task: analyze to surface structure/assumptions. [narrow, mean scope (conceptual framing), cluster method (group by shared characteristics), direct form (lead with main point), gherkin channel]

**Scores:**
- Coherence: **2** — two issues: (1) `probe` + `gherkin` is a confirmed task-affinity problem (gherkin specifies behavior scenarios; probe analyzes conceptual framing — incompatible analytical modes); (2) `direct` form (lead with main point → supporting context) describes prose structure that is incompatible with Gherkin's Given/When/Then format (channel dominates per reference key, making `direct` meaningless).
- Clarity: **2** — what is a "clustered analysis of conceptual framing in Gherkin"? Gherkin scenarios can't capture conceptual clustering.
- Feasibility: **3** — an LLM could produce Gherkin scenarios with mean-scope framing, but quality would be poor
- Utility: **2** — low; Gherkin for conceptual analysis is not a useful pattern
- **Overall: 2**

**Notes:** Fourth Gherkin failure this cycle (out of 4 appearances). Gherkin consistently scores ≤2 when paired with non-specification tasks. The gherkin channel appears to have a very narrow task-affinity: it works primarily with `make` tasks creating feature specifications. Any other task type produces poor results.

**Recommendations:**
- [ ] Strengthen gherkin task-affinity guidance beyond what's already documented. Consider adding AXIS_KEY_TO_GUIDANCE that warns: "Gherkin is designed for behavior specification. Best with `make` tasks creating acceptance tests or feature specs. Avoid with analytical tasks (probe, diff, sort, pull, check)."

---

## Seed 0128

**Tokens selected:**
- task: diff
- completeness: max
- persona: scientist_to_analyst

**Generated prompt preview:**
> Task: compare subjects highlighting similarities/differences/tradeoffs. [max exhaustive, scientist→analyst formally]

**Scores:**
- Coherence: **5** — minimal, focused. Exhaustive comparison from scientist to analyst is exactly right.
- Clarity: **5** — clear: compare comprehensively with scientific rigor for analyst consumption
- Feasibility: **5** — fully executable
- Utility: **5** — high-value, frequently useful pattern
- **Overall: 5**

**Notes:** Another confirmation that minimal combinations (3 tokens) reliably score 5. Clean persona preset + appropriate completeness + task is a solid formula.

---

## Seed 0129

**Tokens selected:**
- task: make
- completeness: full
- method: mod
- channel: sketch
- intent: announce
- tone: formally

**Generated prompt preview:**
> Task: create new content. [full, mod method (modular/cyclic patterns), sketch channel (D2 diagram only), announce intent, formally tone]

**Scores:**
- Coherence: **3** — `make + mod + sketch` has genuine synergy (create a D2 diagram of cyclic/modular patterns). But `announce` intent (share news/updates) with a diagram-creation task creates semantic noise: are we announcing the diagram, or does the diagram announce something? `formally` tone for a D2 SVG/diagram output is also slightly awkward (tone affects prose; diagram output has no prose).
- Clarity: **3** — the diagram task is clear; announce intent muddies it without adding value
- Feasibility: **4** — sketch channel (D2) is executable; mod method guides the diagram content; announce might be effectively ignored
- Utility: **3** — moderate; make+mod+sketch alone would be a clean 5. The persona tokens add noise without value.
- **Overall: 3**

**Notes:** Confirms R15 pattern: social intent tokens (`announce`, `appreciate`) continue to appear in technical task combinations and degrade clarity. The description guidance ("use only when delivering news...") doesn't prevent selection. The announce intent is being ignored by the effective channel constraint, wasting the token.

---

## Seed 0130

**Tokens selected:**
- task: sim
- completeness: gist
- scope: thing
- form: cocreate
- voice: as PM
- tone: directly

**Generated prompt preview:**
> Task: play out scenario over time. [gist, thing scope (entities in view), cocreate form (collaborative with decision points), PM voice, directly]

**Scores:**
- Coherence: **5** — sim + gist + thing scope (what entities are involved) + cocreate (collaborative scenario) + PM voice all reinforce each other. A brief, entity-focused collaborative simulation from a PM perspective is coherent and natural.
- Clarity: **5** — clear: simulate a scenario focusing on entities involved, interactively, from PM perspective
- Feasibility: **5** — fully executable; cocreate without output-exclusive channel runs interactively
- Utility: **5** — PM-led collaborative scenario simulation is high-value; `gist` keeps it focused
- **Overall: 5**

**Notes:** Excellent combination. sim+cocreate continues to be a strong pairing. Minimal persona (voice+tone only, no preset) works well here.

---

## Seed 0131

**Tokens selected:**
- task: plan
- completeness: full
- scope: time
- method: deduce
- form: socratic
- directional: dip ong
- persona: designer_to_pm

**Generated prompt preview:**
> Task: propose steps/strategy from current state toward goal. [full, time scope (phases/temporal dynamics), deduce method (logical entailment), socratic form (question-led), dip ong concrete→actions→extend, designer→PM directly]

**Scores:**
- Coherence: **5** — plan + time scope (phased timeline strategy) + deduce method (logically derived steps) + socratic form (discover through questions) + dip ong (concrete → actions → extension). All five constraints complement each other: a Socratic, deductively-structured temporal planning session.
- Clarity: **4** — complex but not ambiguous; each constraint adds a specific dimension
- Feasibility: **5** — fully executable; socratic form guides the interaction style
- Utility: **5** — collaborative Socratic planning on temporal strategy from a designer's perspective is a sophisticated, high-value use case
- **Overall: 5**

**Notes:** Complex multi-constraint combination that scores 5 because all constraints pull in compatible directions. This validates that high token count doesn't hurt quality when tokens are complementary.

---

## Seed 0132

**Tokens selected:**
- task: fix
- completeness: max
- channel: codetour
- directional: fly ong
- audience: to managers

**Generated prompt preview:**
> Task: change form/presentation while preserving meaning. [max exhaustive, codetour channel (VS Code JSON), fly ong abstract patterns→actions→extend, to managers audience]

**Scores:**
- Coherence: **2** — `codetour` channel (VS Code CodeTour JSON for code walkthroughs) + `to managers` audience is a fundamental mismatch. CodeTour files are developer-facing VS Code artifacts; managers don't use VS Code CodeTour. `fly ong` directional adds analytical depth that cannot be expressed in CodeTour JSON structure.
- Clarity: **2** — who is the target? A manager doesn't consume a VS Code CodeTour file.
- Feasibility: **3** — technically can produce a CodeTour JSON, but the output is useless for the stated audience
- Utility: **2** — low; managers + CodeTour is a category error
- **Overall: 2**

**Notes:** Confirms the codetour audience-mismatch pattern. CodeTour has a narrow appropriate audience (developers using VS Code) and consistently scores poorly when paired with non-developer audiences or non-code tasks. The existing ADR-0105 D2 documents task-affinity but doesn't address audience-affinity for codetour.

**Recommendations:**
- [ ] Add audience-affinity guidance to `codetour` channel: "Intended for developer audiences using VS Code. Avoid with manager, PM, executive, or business stakeholder audiences — the output artifact is a VS Code JSON file that non-developers cannot use."

---

## Seed 0133

**Tokens selected:**
- task: make
- completeness: full
- scope: thing
- form: case
- channel: gherkin
- persona: executive_brief

**Generated prompt preview:**
> Task: create new content. [full, thing scope (entities in view), case form (background→evidence→alternatives→recommendation), gherkin channel (only Gherkin), programmer→CEO directly]

**Scores:**
- Coherence: **1** — triple conflict: (1) `case` form (layered argument-building with evidence, trade-offs, alternatives, recommendation) requires prose output; `gherkin` channel ("outputs only Gherkin format") requires Gherkin syntax — incompatible output formats; (2) `gherkin` channel + `executive_brief` persona (programmer → CEO) — CEOs do not read Given/When/Then Gherkin scenarios; (3) `case` form content (trade-offs, recommendations, objections) cannot be expressed in Gherkin
- Clarity: **1** — completely undefined output
- Feasibility: **2** — an LLM would produce either case structure OR Gherkin, not both; neither would satisfy the executive_brief persona
- Utility: **1** — no practical use
- **Overall: 1**

**Notes:** Worst combination this cycle. Three simultaneous conflicts. Also confirms that `case` form is prose-based and should be added to the list of forms incompatible with code-format channels.

**Recommendations:**
- [ ] Add `case` form to the list of prose forms incompatible with code-format channels (gherkin, svg, codetour, shellscript, diagram/sketch).

---

## Seed 0134

**Tokens selected:**
- task: sim
- completeness: gist
- form: cocreate
- channel: shellscript
- directional: fly ong
- voice: as programmer
- audience: to programmer
- intent: inform

**Generated prompt preview:**
> Task: play out scenario over time. [gist, cocreate form (collaborative with decision points), shellscript channel, fly ong abstract→actions→extend, programmer→programmer, inform]

**Scores:**
- Coherence: **3** — `cocreate` form explicitly handles output-exclusive channels: "formats the artifact to expose decision points, show alternative moves, make response-inviting structure visible within the output." So cocreate+shellscript = a shell script that exposes decision branches. `sim` + `shellscript` = simulate a scenario as a shell script; plausible for technical simulations. `fly ong` adds analytical sweep that could be expressed in code comments/structure.
- Clarity: **3** — technically interpretable but unusual: a simulation script with decision points from a programmer perspective
- Feasibility: **4** — executable; cocreate adaptation logic handles the exclusive channel
- Utility: **3** — moderate utility; the combination is legitimate but niche (scripted simulation for programmers)
- **Overall: 3**

**Notes:** Interesting case where the `cocreate` form's built-in adaptation logic handles the exclusive-channel challenge. This partially redeems the combination. But `sim` + `shellscript` remains an unusual pairing that limits clarity.

---

## Seed 0135

**Tokens selected:**
- task: make
- completeness: full
- method: deduce
- persona: product_manager_to_team

**Generated prompt preview:**
> Task: create new content. [full, deduce method (deductive reasoning from premises), PM→team kindly]

**Scores:**
- Coherence: **5** — minimal, focused. Create content using deductive reasoning as a PM communicating to the team.
- Clarity: **5** — clear directive
- Feasibility: **5** — fully executable
- Utility: **5** — PM + deduction + team communication is a high-value combination for logical product decisions
- **Overall: 5**

**Notes:** Another minimal combination (4 tokens) scoring 5. Confirms the "fewer tokens = clearer prompts" finding from Cycle 4. make + deduce + PM-to-team is clean and effective.

---

## Seed 0136

**Tokens selected:**
- task: diff
- completeness: deep
- channel: gherkin
- voice: as writer
- tone: kindly
- intent: teach

**Generated prompt preview:**
> Task: compare subjects highlighting similarities/differences/tradeoffs. [deep, gherkin channel (only Gherkin), writer voice, kindly, teach intent]

**Scores:**
- Coherence: **2** — `diff` + `gherkin` is a confirmed task-affinity problem (comparative analysis in Gherkin syntax is awkward; Gherkin specifies behavior, not comparisons). Additionally: `writer` voice + `gherkin` + `kindly` + `teach` intent all pull toward prose communication; gherkin channel mandates non-prose output. The persona is entirely incompatible with the output channel.
- Clarity: **2** — who is writing this, and in what format? A writer teaching kindly in Given/When/Then syntax?
- Feasibility: **3** — an LLM could produce Gherkin "comparison" scenarios, but quality would be low
- Utility: **2** — low; teaching comparisons in Gherkin is not a useful pattern
- **Overall: 2**

**Notes:** Fourth gherkin failure this cycle. All four gherkin appearances score 2 or below. The pattern is now extremely consistent across 7 evaluation cycles: gherkin+non-specification-task = poor quality.

---

## Seed 0137

**Tokens selected:**
- task: probe
- completeness: full
- scope: motifs
- method: boom
- channel: adr
- persona: scientist_to_analyst

**Generated prompt preview:**
> Task: analyze to surface structure/assumptions/implications. [full, motifs scope (recurring structural patterns), boom method (behavior at extremes), adr channel (Architecture Decision Record), scientist→analyst formally]

**Scores:**
- Coherence: **5** — probe + motifs scope (find recurring patterns) + boom method (examine behavior at extremes) + adr channel (document as ADR) + scientist-to-analyst is sophisticated and coherent. Scientifically analyzing structural patterns that emerge at scale, documented as an architectural decision record.
- Clarity: **4** — complex but clear; each constraint adds a specific analytical dimension
- Feasibility: **5** — fully executable
- Utility: **5** — highly valuable: scale-behavior pattern analysis documented as architecture decisions for analyst review
- **Overall: 5**

**Notes:** Excellent combination. probe + analysis method + adr channel is consistently excellent (confirms Cycle 6 findings). motifs + boom is a novel and powerful combination: finding patterns that dominate at extremes.

---

## Seed 0138

**Tokens selected:**
- task: sort
- completeness: skim
- scope: view
- form: bug
- channel: html
- directional: bog
- voice: as programmer
- audience: to team
- tone: kindly
- intent: persuade

**Generated prompt preview:**
> Task: arrange items into categories/order. [skim, view scope (stakeholder perspective), bug form (Steps/Expected/Actual/Environment), html channel (only HTML), bog structure→reflect→actions→extend, programmer→team kindly persuade]

**Scores:**
- Coherence: **2** — multiple issues: (1) `bug` form description explicitly states "Creates semantic friction with non-debugging tasks" — `sort` is not a debugging task; (2) `html` channel for a bug report artifact is awkward (bug reports are typically plain text/markdown); (3) `skim` completeness (quick pass) vs. `bog` directional (structural examination + reflection) creates depth tension; (4) 10 tokens is a high count — more tokens = more potential for conflicts.
- Clarity: **2** — what is the output? A quick bug report of sorted stakeholder items in HTML?
- Feasibility: **3** — technically executable but the conflicting signals produce unclear output
- Utility: **2** — low; sorting items as HTML bug reports is not a useful real-world pattern
- **Overall: 2**

**Notes:** Confirms that `bug` form creates semantic friction with non-diagnostic tasks (sort, fix, plan). Also confirms that high token count (10 tokens) increases conflict probability. skim+bog (shallow vs. structural-reflective) is a new depth-tension pattern.

**Recommendations:**
- [ ] Add `skim` completeness guidance: "Avoid pairing with complex directionals (bog, fip rog, fly rog) that require structural depth. Skim implies a quick pass; complex directionals require sustained examination."

---

## Seed 0139

**Tokens selected:**
- task: pick
- completeness: full
- method: operations
- form: taxonomy
- persona: scientist_to_analyst

**Generated prompt preview:**
> Task: choose one or more options from alternatives. [full, operations method (OR/management science concepts), taxonomy form (classification hierarchy), scientist→analyst formally]

**Scores:**
- Coherence: **5** — pick + operations (OR/decision theory concepts) + taxonomy (classify alternatives into a hierarchy) + scientist-to-analyst is an excellent, coherent combination. Choosing from alternatives using operations research, organized as a classification structure, with scientific rigor for analyst consumption.
- Clarity: **4** — clear direction: select options using OR concepts, organized as a taxonomy for analyst review
- Feasibility: **5** — fully executable
- Utility: **5** — scientific rigor + option selection + taxonomy organization is a high-value decision-analysis pattern
- **Overall: 5**

**Notes:** pick + operations + taxonomy is a powerful decision-analysis combination. Confirms that analytical methods (operations, deduce, cluster) pair well with pick/probe/diff tasks.

---

## Seed 0140

**Tokens selected:**
- task: pull
- completeness: deep
- persona: designer_to_pm

**Generated prompt preview:**
> Task: select/extract subset of information. [deep, designer→PM directly]

**Scores:**
- Coherence: **5** — minimal, clean combination. Deep extraction from a designer's perspective for PM.
- Clarity: **5** — clear
- Feasibility: **5** — fully executable
- Utility: **5** — focused, high-value extraction pattern
- **Overall: 5**

**Notes:** Another minimal combination (3 tokens) scoring 5. The pattern is consistent: minimal preset + task + completeness reliably produces excellent prompts.

---

## Summary Statistics

- **Total prompts:** 20
- **Excellent (5):** 8 (40%) — seeds 0124, 0128, 0130, 0131, 0135, 0137, 0139, 0140
- **Acceptable (3):** 4 (20%) — seeds 0121, 0125, 0129, 0134
- **Problematic (2):** 6 (30%) — seeds 0122, 0123, 0127, 0132, 0136, 0138
- **Broken (1):** 2 (10%) — seeds 0126, 0133
- **Average score: 3.30**

**Comparison to Cycle 6:**
| Metric | Cycle 6 (0101-0120) | Cycle 7 (0121-0140) | Delta |
|--------|---------------------|---------------------|-------|
| Excellent (≥4) | 35% | 40% | +5pp |
| Problematic (≤2) | 15% | 40% | +25pp |
| Average | 3.85 | 3.30 | -0.55 |

**Regression note:** Cycle 7 shows a significant increase in problematic prompts (15% → 40%) driven by:
1. **Gherkin over-selection** (4/20 = 20% of seeds; all 4 scored ≤2)
2. **New form/channel conflict pairs** (log+svg, spike+codetour, case+gherkin, story+gherkin)

---

## Pattern Analysis

### Dominant Issue: Gherkin Over-Selection

`gherkin` appeared in 4/20 seeds (20%) and scored ≤2 in all 4 instances. Across all 7 cycles, `gherkin` + non-specification-task is now a consistent failure pattern. The current guidance (D2 in ADR-0105) documents specific task-affinity failures but hasn't reduced the selection frequency.

| Seed | Gherkin Pairing | Score |
|------|-----------------|-------|
| 0122 | story form + gherkin | 2 |
| 0127 | probe + direct form + gherkin | 2 |
| 0133 | case form + gherkin + executive_brief | 1 |
| 0136 | diff + writer persona + gherkin | 2 |

### New Form/Channel Conflicts Identified

| Conflict | Seeds | Score |
|----------|-------|-------|
| story form + gherkin channel | 0122 | 2 |
| spike form + codetour channel | 0123 | 2 |
| log form + svg channel | 0126 | 1 |
| case form + gherkin channel | 0133 | 1 |

All four are instances of prose-structure forms paired with code/graphics-exclusive channels.

### Positive Patterns Confirmed

1. **Minimal combinations score reliably** (0128, 0135, 0140 — all 3 tokens, all scored 5)
2. **Preset personas anchor quality** (6/8 excellent seeds used preset personas)
3. **probe + analysis method + adr channel** = excellent (0137)
4. **pick + analytical method + taxonomy** = excellent (0139)
5. **sim + cocreate** = consistently excellent when channel-compatible (0130)
6. **Complex complementary constraints score well** (0131: 6 tokens, all compatible, scores 5)
