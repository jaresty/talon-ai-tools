# ADR 0085: Shuffle-Driven Catalog Refinement — Seeds 0101-0120

**Evaluation Date**: 2026-02-13
**Corpus Size**: 20 prompts (seeds 0101-0120)
**Evaluator**: Claude Sonnet 4.5
**Context**: Cycle 6 — post-ADR-0109/0110/0111 evaluation (token labels, guidance fields, persona labels)

## Context for This Cycle

Three ADRs were implemented since cycle 5:

- **ADR-0109**: Added `AXIS_KEY_TO_LABEL` — short 3-8 word labels for all axis tokens (CLI/TUI display)
- **ADR-0110**: Added `AXIS_KEY_TO_GUIDANCE` — selection guidance for ambiguous/trap tokens (TUI display, outside prompt body)
- **ADR-0111**: Added `PERSONA_KEY_TO_LABEL` — short labels for persona/voice/audience/tone tokens

The key structural change: guidance now lives in two separate places: the **REFERENCE KEY** section in the prompt (meta-instructions for how to interpret the structured prompt), and the **TUI guidance fields** (selection heuristics displayed before token selection, not injected into the prompt). This evaluation assesses whether these changes improve combination quality and whether new issues emerge.

## Evaluation Rubric

Each prompt is scored 1-5 on four criteria:

- **Coherence** (COH): Do the tokens work together logically?
- **Clarity** (CLA): Is the prompt directive clear?
- **Feasibility** (FEA): Can it be executed?
- **Utility** (UTI): Would it be useful?
- **Overall** (OVR): Mean of four criteria

**Scoring**: 5=Excellent, 4=Good, 3=Acceptable, 2=Problematic, 1=Broken

---

## Seed 0101

**Tokens selected:**
- task: show
- completeness: full
- method: melody
- channel: plain
- directional: fly ong
- persona: designer_to_pm (as designer → to product manager, directly)

**Generated prompt preview:**
> The response explains or describes the subject for the stated audience. [full, melody coordination analysis, plain prose, fly ong abstract→concrete→extend, designer→PM directly]

**Scores:**
- Coherence: **5** — show+melody+plain+fly ong all work together
- Clarity: **5** — clear explanation task with coordination analysis depth
- Feasibility: **5** — fully executable
- Utility: **4** — designer→PM coordination explanation is high value; "fly ong" adds pattern abstraction
- **Overall: 4.75 → 5**

**Notes:**
Strong combination. "show" (explain for audience) pairs naturally with "melody" (coordination analysis) — this is an explanation of how things coordinate. Plain prose is right for PM audience. "fly ong" (abstract→concrete→extend) adds analytical sweep that suits PM communication style. No conflicts.

---

## Seed 0102

**Tokens selected:**
- task: probe
- completeness: full
- scope: mean
- method: probability
- form: walkthrough
- persona: as Kent Beck

**Generated prompt preview:**
> The response analyzes the subject to surface structure, assumptions, or implications beyond restatement. [full, mean scope, probability method, walkthrough form, Kent Beck voice]

**Scores:**
- Coherence: **5** — probe+mean+probability+walkthrough all reinforce each other
- Clarity: **5** — analytical deep-dive with clear probabilistic framing
- Feasibility: **5** — fully executable
- Utility: **5** — Kent Beck style + probability + walkthrough is excellent for uncertainty analysis
- **Overall: 5**

**Notes:**
Canonical analytical combination. "probe" + "mean" (conceptual framing/purpose) + "probability" (characterize uncertainty) is a natural stack for surfacing hidden assumptions. "walkthrough" form guides the reader step-by-step through the probabilistic analysis. Kent Beck's pragmatic, iterative stance suits this framing perfectly.

---

## Seed 0103

**Tokens selected:**
- task: pull
- completeness: full
- scope: motifs
- form: merge
- directional: fly ong
- persona: executive_brief (as programmer → to CEO, directly)

**Generated prompt preview:**
> The response selects or extracts a subset of the given information without altering its substance. [full, motifs scope, merge form, fly ong directional, programmer→CEO directly]

**Scores:**
- Coherence: **3** — pull+merge semantic tension
- Clarity: **3** — which operation dominates: extraction or combination?
- Feasibility: **4** — executable but with ambiguity
- Utility: **3** — pull+merge is unusual for CEO briefs; fly ong adds value but can't resolve core tension
- **Overall: 3**

**Notes:**
"pull" (extract a subset) and "merge" (combine multiple sources into one) create directional tension. "pull" implies narrowing/selecting from a single source; "merge" implies combining across multiple sources. The combination is usable only when the implicit reading is "extract motifs from multiple sources and merge them into one coherent pattern list," but that reading requires work. "full" completeness with "pull" is also mildly awkward — if you're extracting a subset, what does "full" coverage of that subset mean? "fly ong" adds abstracting-to-principles value for CEO, but the pull/merge tension weakens the combination.

---

## Seed 0104

**Tokens selected:**
- task: sim
- completeness: full
- method: rigor
- form: wasinawa
- directional: fip ong
- persona: fun_mode (casually)

**Generated prompt preview:**
> The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions. [full, rigor method, wasinawa form, fip ong, casual/fun]

**Scores:**
- Coherence: **4** — sim+rigor+wasinawa work; fip ong is compatible; casual+rigor contrast is intentional
- Clarity: **5** — the structural flow is clear (sim → wasinawa reflection frame → abstract/concrete cycling)
- Feasibility: **5** — fully executable
- Utility: **4** — rigor+casual is a rare but valuable combination for accessible scenario analysis
- **Overall: 4.5 → 4**

**Notes:**
Good combination. "wasinawa" (What/So What/Now What) structures the simulation output cleanly. "rigor" ensures the scenario reasoning is disciplined. "fip ong" (fig+ong: concrete↔abstract alternation → actions → extend) synergizes with wasinawa's progression. Casual tone from fun_mode is an interesting contrast with "rigor" — this works as an accessible, engaging presentation of rigorous analysis.

---

## Seed 0105

**Tokens selected:**
- task: make
- completeness: full
- scope: motifs
- form: wardley
- directional: fly bog
- persona: as designer, kindly

**Generated prompt preview:**
> The response creates new content that did not previously exist. [full, motifs scope, wardley map form, fly bog directional, designer+kindly]

**Scores:**
- Coherence: **4** — make+wardley is natural; motifs+wardley unusual but interesting
- Clarity: **4** — wardley map format is clear; "fly bog" organizational philosophy readable
- Feasibility: **4** — executable; directional may shape the Wardley Map structure
- Utility: **4** — Wardley Map of recurring motifs/patterns is high value; designer persona fits
- **Overall: 4**

**Notes:**
"make + wardley" is a natural pairing (create a Wardley Map). "motifs" scope adds an interesting constraint: the Wardley Map should emphasize recurring patterns/themes rather than just mapping all components. "fly bog" (abstract→concrete→reflect→extend) is slightly unusual when the output format is a Wardley Map, but it can be understood as the organizing philosophy for what to include. Designer+kindly is fine for Wardley Maps in product/design contexts.

---

## Seed 0106

**Tokens selected:**
- task: pick
- completeness: gist
- method: bias
- channel: plain
- persona: product_manager_to_team (as PM → to team, kindly)

**Generated prompt preview:**
> The response chooses one or more options from a set of alternatives. [gist, bias method, plain channel, PM→team kindly]

**Scores:**
- Coherence: **5** — pick+bias+gist+plain all reinforce
- Clarity: **5** — choose an option, surfacing cognitive biases that might distort judgment
- Feasibility: **5** — fully executable
- Utility: **5** — PM context: bias-aware decision-making for team is high-value daily use case
- **Overall: 5**

**Notes:**
Canonical pick-under-cognitive-bias combination. "pick" (choose from alternatives) + "bias" (identify cognitive biases/systematic errors) is an excellent pairing — it produces a decision that's aware of its own heuristic distortions. "gist" completeness keeps it brief, appropriate for PM→team communication. "plain" channel is right for this stakeholder context. Strong combination.

---

## Seed 0107

**Tokens selected:**
- task: diff
- completeness: full
- channel: diagram
- directional: dip ong
- persona: to LLM

**Generated prompt preview:**
> The response compares two or more subjects, highlighting relationships, similarities, differences, or tradeoffs. [full, diagram channel (Mermaid), dip ong, to LLM]

**Scores:**
- Coherence: **4** — diff+diagram natural; dip ong awkward with diagram format
- Clarity: **4** — comparison-as-diagram is clear; directional application in diagram is unclear
- Feasibility: **4** — executable; LLM should be able to apply dip ong loosely to diagram structure
- Utility: **4** — "to LLM" audience + diagram is useful for structured prompting
- **Overall: 4**

**Notes:**
"diff + diagram" is a natural pairing (comparison as visual diagram). "dip ong" (concrete→actions→extend) is somewhat hard to apply when the output format is Mermaid code — the directional shapes how content is organized, but a diagram's structure is spatial rather than sequential. The LLM will likely interpret "dip ong" as sequencing the diagram to start with concrete comparisons, which is reasonable. Minor tension rather than conflict.

---

## Seed 0108

**Tokens selected:**
- task: check
- completeness: full
- scope: struct
- channel: plain
- persona: scientist_to_analyst (as scientist → to analyst, formally)

**Generated prompt preview:**
> The response evaluates the subject against a condition and reports whether it passes or fails. [full, struct scope, plain channel, scientist→analyst formally]

**Scores:**
- Coherence: **5** — check+struct+plain+scientist_to_analyst all reinforce
- Clarity: **5** — structural evaluation in scientific style
- Feasibility: **5** — fully executable
- Utility: **5** — scientific structural evaluation for an analyst audience is a canonical use case
- **Overall: 5**

**Notes:**
Excellent clean combination. "check" (evaluate pass/fail) + "struct" scope (focus on arrangements, dependencies, constraints) naturally produces a structural audit. "plain" prose fits analytical reading. "scientist_to_analyst" is perfectly calibrated — scientific rigor, hypothesis-driven framing, evidence focus. No conflicts.

---

## Seed 0109

**Tokens selected:**
- task: probe
- completeness: full
- scope: act
- method: inversion
- form: recipe
- channel: codetour
- directional: dip rog
- persona: to team, formally

**Generated prompt preview:**
> The response analyzes the subject to surface structure, assumptions, or implications beyond restatement. [full, act scope, inversion method, recipe form, codetour channel, dip rog, team formally]

**Scores:**
- Coherence: **1** — recipe+codetour form/channel conflict
- Clarity: **2** — token set is overloaded; format conflict undermines clarity
- Feasibility: **2** — LLM must choose between recipe (custom mini-language) and codetour (JSON schema)
- Utility: **3** — probe+inversion+act would be strong if output were not broken by format conflict
- **Overall: 2**

**Notes:**
Critical form/channel conflict. "recipe" form requires a custom mini-language with a documented key. "codetour" channel requires a valid VS Code CodeTour JSON file. These formats are mutually exclusive — the LLM must produce either a recipe OR a CodeTour JSON, not both. Even accepting the REFERENCE KEY guidance that "channel defines output format," a recipe is not a valid CodeTour JSON. This extends the form/channel conflict pattern beyond the previously documented interactive forms (R8) to include structured-format forms.

The probe+act+inversion content logic is strong (analyze intended operations, work backward from catastrophic failures). The directional dip rog is compatible. But the form/channel conflict makes this combination unusable as-is.

**New issue identified**: `recipe` form conflicts with any code-format channel (codetour, code, shellscript, svg, diagram, html) because recipe requires prose + custom language. This extends R8 beyond interactive forms.

---

## Seed 0110

**Tokens selected:**
- task: check
- completeness: minimal
- scope: fail
- method: grow
- directional: fly bog
- persona: designer_to_pm (as designer → to product manager, directly)

**Generated prompt preview:**
> The response evaluates the subject against a condition and reports whether it passes or fails. [minimal, fail scope, grow method, fly bog, designer→PM directly]

**Scores:**
- Coherence: **5** — check+fail+minimal+grow all reinforce
- Clarity: **5** — evaluate failure modes minimally, growing only what needs examining
- Feasibility: **5** — fully executable
- Utility: **5** — designer→PM failure mode evaluation is a canonical design review use case
- **Overall: 5**

**Notes:**
Excellent combination. "check + fail scope" naturally directs attention to failure modes and edge cases. "minimal" completeness + "grow" method creates a focused evaluation that expands only where evidence demands — this is ideal for design review (don't over-analyze what works; dig into what might break). "fly bog" adds the abstract-to-reflect pattern, turning raw failure identification into principled insight. Designer→PM framing is natural for surfacing design risk. Canonical design review pattern.

---

## Seed 0111

**Tokens selected:**
- task: plan
- completeness: deep
- scope: struct
- directional: dip rog
- persona: as teacher, casually, intent: appreciate

**Generated prompt preview:**
> The response proposes steps, structure, or strategy to move from the current state toward a stated goal. [deep, struct scope, dip rog, teacher casual, appreciate]

**Scores:**
- Coherence: **3** — plan+struct+deep+dip rog are coherent; appreciate intent breaks alignment
- Clarity: **3** — what does "appreciating" mean in the context of a structural plan?
- Feasibility: **4** — executable but the appreciate intent will likely be ignored or misapplied
- Utility: **3** — the underlying plan+struct+teacher combo is useful; appreciate intent adds noise
- **Overall: 3**

**Notes:**
Intent mismatch. "appreciate" intent means "express thanks, recognition, or positive regard." This makes no sense paired with a planning task unless the user explicitly wants a plan expressed as a gratitude/appreciation — an extremely narrow edge case. In practice, an LLM receiving this combination will likely ignore "appreciate" or awkwardly inject thanks into a planning response.

**New issue identified**: The "appreciate" intent token (and possibly "entertain", "announce") is being randomly selected alongside analytical/structural tasks where it creates semantic noise. These intents are meaningful only when the response's *purpose* is genuinely to express that intent toward the audience. They should not be treated as style modifiers for task-driven prompts. Guidance or selection restrictions are needed.

---

## Seed 0112

**Tokens selected:**
- task: pull
- completeness: full
- scope: fail
- persona: fun_mode (casually)

**Generated prompt preview:**
> The response selects or extracts a subset of the given information without altering its substance. [full, fail scope, casual/fun]

**Scores:**
- Coherence: **4** — pull+fail natural; full+pull minor tension
- Clarity: **4** — extract failure information with a light touch
- Feasibility: **5** — fully executable
- Utility: **4** — fun_mode for failure analysis is an underrated combination (makes risk analysis engaging)
- **Overall: 4**

**Notes:**
Clean, simple combination. "pull + fail" is natural (extract the failure mode information from the subject). "Full" completeness with "pull" creates mild tension (pulling a subset but covering all of it thoroughly) — but this is readable as "extract all failure information, fully." Fun_mode casual tone for failure analysis is useful: makes risk discussions less alarming and more approachable.

---

## Seed 0113

**Tokens selected:**
- task: plan
- completeness: full
- method: order
- channel: adr
- directional: dip rog
- persona: to principal engineer, formally, intent: appreciate

**Generated prompt preview:**
> The response proposes steps, structure, or strategy to move from the current state toward a stated goal. [full, order method, adr channel, dip rog, principal engineer formally, appreciate intent]

**Scores:**
- Coherence: **2** — appreciate intent mismatch + plan/adr channel tension
- Clarity: **3** — plan→adr is unusual but readable; appreciate breaks intent
- Feasibility: **3** — executable with workarounds; appreciate intent will likely be ignored
- Utility: **3** — underlying plan+order+adr+dip rog is interesting; two problems degrade it
- **Overall: 2.75 → 3**

**Notes:**
Two issues compound here:

1. **Appreciate intent mismatch** (same as seed 0111): "appreciate" has no natural role in a planning response to a principal engineer. The intent signal is noise.

2. **plan + adr channel task-affinity concern**: R9 flagged `adr` as having task-affinity for `plan/probe/make`. This combination (plan + adr) is actually in the *allowed* set, so this is not a conflict. But the specific reading is unusual: an ADR is typically a record of a decision already made, while "plan" produces steps toward a future goal. A "planning ADR" exists (documenting the decision to follow a particular plan), so this is workable but semantically niche.

The appreciate intent is the primary issue here.

---

## Seed 0114

**Tokens selected:**
- task: make
- completeness: full
- channel: shellscript
- directional: fly ong
- persona: (none)

**Generated prompt preview:**
> The response creates new content that did not previously exist. [full, shellscript channel, fly ong directional]

**Scores:**
- Coherence: **4** — make+shellscript natural; fly ong application in shellscript is awkward
- Clarity: **4** — create a shell script is clear; fly ong in code context is soft
- Feasibility: **4** — executable; LLM can apply fly ong loosely as script organization
- Utility: **4** — make+shellscript is a core use case; fly ong adds mild structural philosophy
- **Overall: 4**

**Notes:**
"make + shellscript" is a canonical combination (create shell scripts). "fly ong" (abstract→concrete→extend) is an unusual directional for code output — the script is a code artifact, not a discursive text. The directional may influence how the script is structured (e.g., start with abstract helper functions, then concrete invocations, then extended usage examples in comments). This is workable but the directional application is soft. No persona is fine for code generation tasks.

---

## Seed 0115

**Tokens selected:**
- task: show
- completeness: minimal
- form: questions
- channel: gherkin
- directional: bog
- persona: product_manager_to_team (as PM → to team, kindly)

**Generated prompt preview:**
> The response explains or describes the subject for the stated audience. [minimal, questions form, gherkin channel, bog directional, PM→team kindly]

**Scores:**
- Coherence: **2** — questions+gherkin form/channel conflict
- Clarity: **2** — Gherkin requires Given/When/Then; questions form requires question sentences
- Feasibility: **2** — LLM must choose one format; result will be confused
- Utility: **2** — underlying show+minimal+PM→team is useful; form/channel breaks it
- **Overall: 2**

**Notes:**
Clear form/channel conflict. "questions" form produces probing/clarifying questions. "gherkin" channel produces Given/When/Then feature scenarios. These are mutually exclusive output formats. An LLM receiving this combination will likely try to write Gherkin scenarios framed as questions ("Given?", "When?", "Then?"), which is not valid Gherkin and not useful probing questions.

Additionally, "show" (explain/describe) + "questions" form has inherent tension: "show" asks for explanation by statements, "questions" form asks for explanation via questioning. This is a valid tension — Socratic teaching via questions is a real pattern — but combined with the gherkin conflict it becomes unusable.

**Extends form/channel conflict pattern**: questions form conflicts with any format-specific output channel (gherkin, codetour, diagram, adr, presenterm). questions form needs a prose-compatible channel (plain, slack, jira, remote, sync, or no channel).

---

## Seed 0116

**Tokens selected:**
- task: fix
- completeness: max
- scope: act
- directional: dip bog
- persona: intent: entertain

**Generated prompt preview:**
> The response changes the form or presentation of given content while keeping its intended meaning. [max, act scope, dip bog, entertain intent]

**Scores:**
- Coherence: **4** — fix+max+act+dip bog work together; entertain intent is style modifier
- Clarity: **4** — reformat content with exhaustive task-focused coverage
- Feasibility: **4** — executable; "entertain" intent shapes tone
- Utility: **3** — max completeness with a reformat task is verbose; entertain intent is rare but valid
- **Overall: 3.75 → 4**

**Notes:**
Workable combination. "fix" (reformat/transform) + "max" is verbose but valid — exhaustively reformat all aspects of the content. "act" scope (tasks/activities) focuses the reformat on what's being done/intended. "dip bog" (concrete→reflect→actions→extend) adds depth to the analysis. "entertain" intent as a standalone intent (no voice/audience specified) means the LLM shapes tone for an engaging presentation — this is a valid but narrow use case for "fix." No severe conflicts, but max+fix+no-channel may produce an unusually lengthy output.

---

## Seed 0117

**Tokens selected:**
- task: pull
- completeness: deep
- scope: fail
- directional: fly rog
- persona: stakeholder_facilitator (as facilitator → to stakeholders, directly)

**Generated prompt preview:**
> The response selects or extracts a subset of the given information without altering its substance. [deep, fail scope, fly rog, facilitator→stakeholders directly]

**Scores:**
- Coherence: **5** — pull+fail+deep+fly rog all reinforce
- Clarity: **5** — extract failure information with depth and abstract synthesis
- Feasibility: **5** — fully executable
- Utility: **5** — facilitator→stakeholders + failure synthesis is a canonical risk communication pattern
- **Overall: 5**

**Notes:**
Excellent combination. "pull + fail" extracts failure information. "deep" completeness drives thorough coverage of failure modes, edge cases, and stress conditions. "fly rog" (abstract→reflect on structural implications) adds the critical synthesizing step — not just listing failures but identifying abstract patterns and what they reveal structurally. "stakeholder_facilitator" persona is ideal for this: a facilitator presenting risk findings to stakeholders, speaking directly. Canonical risk communication pattern.

---

## Seed 0118

**Tokens selected:**
- task: fix
- completeness: full
- channel: slack
- directional: dip bog
- persona: to CEO, formally, intent: teach

**Generated prompt preview:**
> The response changes the form or presentation of given content while keeping its intended meaning. [full, slack channel, dip bog, CEO formally, teach intent]

**Scores:**
- Coherence: **3** — formally+slack channel tension
- Clarity: **4** — reformat for Slack is clear; teach+CEO is unusual
- Feasibility: **4** — executable; "formally" and "slack" create a style conflict
- Utility: **3** — fix+slack is useful; formal tone contradicts Slack's informal register; teach→CEO is narrow
- **Overall: 3**

**Notes:**
Two issues:

1. **formally + slack channel tension**: Slack is an informal, conversational platform. "Formally" tone (professional, structured, uses elevated language) creates a semantic mismatch with Slack's expected register. The output will feel stilted or overly bureaucratic for Slack. A Slack message to a CEO that reads as a formal memo loses the purpose of Slack formatting.

2. **teach intent + CEO audience**: "teach" means "help the audience understand and learn material." Instructing or teaching a CEO is a narrow, unusual scenario (most CEO communication is briefing, not instructing). This is not a conflict per se, but the combination is semantically niche and may produce patronizing results.

**New issue identified**: Slack channel (and similarly: remote, sync, jira) have implicit register assumptions that conflict with "formally" tone. Guidance needed.

---

## Seed 0119

**Tokens selected:**
- task: make
- completeness: full
- channel: diagram
- directional: fog
- persona: teach_junior_dev (as teacher → to junior engineer, kindly)

**Generated prompt preview:**
> The response creates new content that did not previously exist. [full, diagram (Mermaid), fog directional, teacher→junior kindly]

**Scores:**
- Coherence: **5** — make+diagram+fog+teach_junior_dev all reinforce
- Clarity: **5** — create a diagram that generalizes from specifics, teaching a junior engineer
- Feasibility: **5** — fully executable
- Utility: **5** — pedagogical diagram with abstraction → generalizations is excellent for junior dev mentoring
- **Overall: 5**

**Notes:**
Excellent canonical combination. "make + diagram" creates a visual artifact. "fog" directional (generalize from specifics to broader insights) gives the Mermaid diagram a clear organizational principle: start from concrete components and reveal the abstract pattern. "teach_junior_dev" is perfectly calibrated — building a diagram that helps a junior engineer understand an abstract concept from concrete examples. Canonical pedagogical diagram pattern. New exemplar.

---

## Seed 0120

**Tokens selected:**
- task: sim
- completeness: full
- method: jobs
- form: questions
- channel: diagram
- directional: dip ong
- persona: as principal engineer → to analyst

**Generated prompt preview:**
> The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions. [full, jobs method, questions form, diagram channel, dip ong, PE→analyst]

**Scores:**
- Coherence: **2** — questions+diagram form/channel conflict
- Clarity: **2** — LLM must choose: probing questions or Mermaid code?
- Feasibility: **1** — cannot produce both formats simultaneously
- Utility: **3** — sim+jobs+PE→analyst is strong; form/channel conflict breaks execution
- **Overall: 2**

**Notes:**
Form/channel conflict. "questions" form produces probing/clarifying questions; "diagram" channel produces Mermaid code. These are mutually exclusive. An LLM receiving this combination will either ignore one token or produce something that satisfies neither.

"sim + jobs" (simulate a JTBD scenario) is an excellent combination (seed 0120 would score 5 without the conflict). "dip ong" + "PE→analyst" adds analytical depth. The form/channel conflict is the sole problem.

**Third instance of questions+format-channel conflict** (seeds 0109, 0115, 0120). This confirms "questions" form is particularly prone to channel conflicts because it requires prose sentence output, which is incompatible with any structured-format channel (diagram, gherkin, codetour, adr, code, shellscript, svg, html, presenterm).

---

## Score Summary

| Seed | Tokens | OVR |
|------|--------|-----|
| 0101 | show+full+melody+plain+fly ong+designer_to_pm | **5** |
| 0102 | probe+full+mean+probability+walkthrough+Kent Beck | **5** |
| 0103 | pull+full+motifs+merge+fly ong+executive_brief | 3 |
| 0104 | sim+full+rigor+wasinawa+fip ong+fun_mode | 4 |
| 0105 | make+full+motifs+wardley+fly bog+designer+kindly | 4 |
| 0106 | pick+gist+bias+plain+PM_to_team | **5** |
| 0107 | diff+full+diagram+dip ong+to LLM | 4 |
| 0108 | check+full+struct+plain+scientist_to_analyst | **5** |
| 0109 | probe+full+act+inversion+recipe+codetour+dip rog+to team | **2** — recipe+codetour conflict |
| 0110 | check+minimal+fail+grow+fly bog+designer_to_pm | **5** |
| 0111 | plan+deep+struct+dip rog+teacher+casual+appreciate | 3 — appreciate mismatch |
| 0112 | pull+full+fail+fun_mode | 4 |
| 0113 | plan+full+order+adr+dip rog+PE+formally+appreciate | 3 — appreciate mismatch |
| 0114 | make+full+shellscript+fly ong | 4 |
| 0115 | show+minimal+questions+gherkin+bog+PM_to_team | **2** — questions+gherkin conflict |
| 0116 | fix+max+act+dip bog+entertain | 4 |
| 0117 | pull+deep+fail+fly rog+stakeholder_facilitator | **5** |
| 0118 | fix+full+slack+dip bog+CEO+formally+teach | 3 — formally+slack tension |
| 0119 | make+full+diagram+fog+teach_junior_dev | **5** |
| 0120 | sim+full+jobs+questions+diagram+dip ong+PE→analyst | **2** — questions+diagram conflict |

**Score distribution:**
- 5 (Excellent): 7/20 = 35%
- 4 (Good): 6/20 = 30%
- 3 (Acceptable): 4/20 = 20%
- 2 (Problematic): 3/20 = 15%
- 1 (Broken): 0/20 = 0%

**Cycle mean: 3.85/5** (up from 3.65 in cycle 5)

---

## Key Findings for Cycle 6

### Issue 1: `questions` form conflicts with all structured-format channels (high priority)
**Seeds:** 0109 (recipe+codetour), 0115 (questions+gherkin), 0120 (questions+diagram)

"questions" form produces prose questions — it is categorically incompatible with any channel that forces a non-prose format (diagram, gherkin, codetour, adr, code, shellscript, svg, html, presenterm). This extends the form/channel conflict class documented in R8/R9 to explicitly cover the "questions" form token.

The REFERENCE KEY guidance ("when form and channel both present, channel defines output format") does not resolve this because the questions form requires sentence-level prose, which cannot be represented in Mermaid, Gherkin, or JSON formats.

More broadly, `recipe` form (requires custom prose mini-language) is also incompatible with code-format channels — confirmed in seed 0109.

### Issue 2: `appreciate`/social intent tokens mismatch with analytical/structural tasks (medium priority)
**Seeds:** 0111 (plan+appreciate), 0113 (plan+appreciate)

"appreciate," "entertain," and "announce" are *social intent* tokens that define the response's communicative purpose (gratitude, engagement, news). They create semantic noise when the TASK is analytical or structural (plan, probe, check, diff). These intents are only meaningful when the entire response genuinely serves that social function.

The current token does not signal when it's inappropriate. Users selecting intents randomly will hit this problem 15% of the time (3 intent tokens out of ~20 intent options are socially-scoped).

### Issue 3: `formally` tone + conversational channels (medium priority)
**Seed:** 0118 (fix+slack+formally)

Slack (and similar real-time/conversational channels: remote, sync) imply an informal register. "Formally" tone creates a register mismatch: the formatting target (Slack markdown, mentions) is informal, but the tone instruction demands formal elevated language. The result is bureaucratic Slack messages that defeat the purpose of Slack.

### Issue 4: `pull` + `full` recurring minor tension (low priority)
**Seeds:** 0103, 0112, 0117

"pull" extracts a subset; "full" covers exhaustively. These can coexist ("pull all failure modes, thoroughly") but the combination is semantically slightly inconsistent. No action needed — this is an acceptable tension that users can resolve with context.

### Confirmed positive patterns (cycle 6 additions)

- **check + fail + minimal/grow** (seed 0110): Canonical design review failure-mode check
- **pick + bias + gist** (seed 0106): Canonical bias-aware decision pattern
- **pull + fail + deep + fly rog + stakeholder_facilitator** (seed 0117): Canonical stakeholder risk synthesis
- **make + diagram + fog + teach_junior_dev** (seed 0119): Canonical pedagogical diagram

### Note on guidance outside main body (ADR-0109/0110/0111)

The REFERENCE KEY section (guidance outside main body) is comprehensive and consistent across all seeds. It correctly explains task/constraint/persona section roles and addresses the critical "don't treat SUBJECT as instructions" principle. However:

- The REFERENCE KEY form/channel guidance ("channel defines output format when both present") is *insufficient* for categorically incompatible combinations like questions+gherkin or recipe+codetour — these need explicit prevention or strong guidance at selection time.
- The TUI guidance from AXIS_KEY_TO_GUIDANCE (displayed at selection time, not in prompt) is the appropriate place to warn about form/channel conflicts — but it needs to be populated for these specific combinations.
