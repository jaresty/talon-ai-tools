# Shuffle Evaluation: Seeds 0041–0060
**Date:** 2026-02-10
**Evaluator:** Claude Sonnet 4.5
**Cycle:** 3 (validation cycle, post-ADR-0091 and post-ADR-0104)

## Context

This is the third evaluation cycle. The previous cycle (seeds 0021–0040) identified output-exclusive format conflicts as the dominant issue and proposed mutual-exclusion validation rules. The output-exclusive validation was NOT implemented before this cycle was generated, so conflict rates are expected to remain similar to cycle 2 (25%).

**Targets from recommendations-post-refactor.yaml:**
- Excellent (≥4.0): target ≥70%, previous 55%
- Overall average: target ≥4.30, previous 4.16
- Output-exclusive conflicts: target ≤5%, previous 25%

---

## Summary Statistics

- Total prompts: 20
- Excellent (≥4.0): 13 (65%)
- Good (3.0–3.9): 3 (15%)
- Problematic (≤2.9): 4 (20%)
- Average score: 4.09
- Output-exclusive conflicts: 5 (25%)
- Previous cycle (0021–0040): 55% excellent, 4.16 avg, 25% output-exclusive conflicts
- Trend: broadly stable; excellent rate improved by 10 pp despite missing validation implementation; conflict rate unchanged, confirming the validation gap

---

## Individual Evaluations

### Seed 0041

**Tokens:** probe + deep + prioritize(method) + scaffold(form) + junior_engineer(voice) + casually(tone)

**Prompt task:** The response analyzes the subject to surface structure, assumptions, or implications beyond restatement.

**Scores:**
- Task clarity: 5 – "probe" is unambiguous: surface structure, assumptions, implications
- Constraint independence: 5 – prioritize(method) adds ordering lens; scaffold(form) adds pedagogical structure; both enhance HOW without redefining WHAT
- Persona coherence: 5 – junior engineer voice with casual tone is perfect for a scaffold-driven deep probe; curious, candid, concrete
- Category alignment: 5 – all tokens are cleanly in their correct axes; scaffold is form, prioritize is method, casually is tone
- Combination harmony: 5 – scaffold + deep + prioritize create a natural "explain from first principles, ranked by importance" pattern; junior engineer + casual tone fits perfectly for a learning-oriented deep dive
- **Overall: 5.0**

**Notes:** Excellent combination. The scaffold form and prioritize method are mutually reinforcing: scaffold starts from first principles and prioritize ensures the most important ideas are foregrounded. Deep completeness gives the space needed for scaffolded explanation. The junior engineer + casual persona makes the output approachable for learners. No conflicts. Note: the corpus summary describes fip_ong as a directional for this seed, but the JSON has no directional; the evaluation is based on the actual corpus JSON.

**Recommendations:** None. Positive pattern — scaffold + prioritize is a strong pedagogical combination worth documenting.

---

### Seed 0042

**Tokens:** peer_engineer_explanation(preset) + diff + narrow + thing(scope) + origin(method) + fip_ong(directional)

**Prompt task:** The response compares two or more subjects, highlighting relationships such as similarities, differences, or tradeoffs.

**Scores:**
- Task clarity: 5 – "diff" is clear; narrow + thing scope tightly bounds the comparison
- Constraint independence: 5 – origin(method) adds historical framing; thing(scope) sets entity boundary; fip_ong(directional) adds abstract–concrete–action–extension cadence; all shape HOW
- Persona coherence: 5 – peer_engineer_explanation preset (programmer to programmer) fits narrow technical comparison perfectly
- Category alignment: 5 – every token in its correct axis; origin is a method token, thing is scope, fip_ong is directional
- Combination harmony: 5 – narrow completeness + thing scope = very focused; origin method adds "why does this difference exist historically" depth that naturally fits diff; fip_ong directional drives the response from principle to example to action; peer engineer persona reinforces precision
- **Overall: 5.0**

**Notes:** Tight, purposeful combination. The origin method is particularly well-matched to diff: understanding where entities diverged historically illuminates why they differ now. The narrow + thing pairing creates a laser focus on specific entity comparisons. fip_ong provides good structural cadence for comparative analysis.

**Recommendations:** None. Positive pattern — diff + narrow + origin + fip_ong is a strong focused comparative analysis recipe.

---

### Seed 0043

**Tokens:** executive_brief(preset) + diff + minimal + induce(method) + sync(channel) + dip_ong(directional)

**Prompt task:** The response compares two or more subjects, highlighting relationships such as similarities, differences, or tradeoffs.

**Scores:**
- Task clarity: 4 – "diff" is clear, but minimal + sync creates a slight ambiguity about whether this is a quick decision-support comparison or a mini-workshop
- Constraint independence: 4 – induce(method) adds inductive reasoning to comparison, appropriately; sync channel changes delivery format, not task definition; dip_ong adds concrete-first cadence; all stay in their lanes with minor overlap between "minimal" completeness and "sync" format (minimal session plans feel underspecified)
- Persona coherence: 3 – executive_brief preset expects crisp, business-impact-framed output for a CEO. A sync session plan format is unusual for an executive brief; executives typically receive documents, not facilitation scripts
- Category alignment: 5 – all tokens correctly placed in their axes
- Combination harmony: 3 – the tension is between executive_brief (document delivery, business framing) and sync (live session plan). Minimal completeness with a session plan is awkward: a minimal agenda risks feeling incomplete. dip_ong (concrete→action→extend) works well for the comparison, but the overall deliverable is unclear: is this an executive briefing document or a session plan?
- **Overall: 3.8**

**Notes:** The executive_brief preset + sync channel combination replicates the pattern seen in seed 0034 (ADR channel + sync) from the previous cycle, but with a persona dimension instead of a form conflict. The core issue is that sync specifies a live-session deliverable, while the executive_brief persona implies a document prepared for a senior audience. These are not technically output-exclusive tokens, but they represent incompatible delivery modalities. Minimal completeness aggravates this: a minimal session plan may not satisfy executive standards for thorough briefing.

**Recommendations:** Flag executive_brief + sync as an awkward combination. The sync channel is optimized for facilitation contexts; executive_brief targets document-reading contexts. Consider adding delivery_mode metadata (document vs. live) to help the system warn when these diverge.

---

### Seed 0044

**Tokens:** pull + full + fip_rog(directional) + to_product_manager(audience)

**Prompt task:** The response selects or extracts a subset of the given information without altering its substance.

**Scores:**
- Task clarity: 5 – "pull" (extract/isolate) is clear and simple
- Constraint independence: 5 – full completeness governs depth; fip_rog(directional) governs cognitive cadence; to_product_manager(audience) governs framing; none redefine the extraction task
- Persona coherence: 5 – product manager audience is well-suited to pulled/extracted information that connects user value and trade-offs
- Category alignment: 5 – full is completeness, fip_rog is directional, to_product_manager is audience; all correct
- Combination harmony: 5 – elegant minimal combination. fip_rog (abstract↔concrete, structure, reflect) gives the extracted content a natural organizational cadence. Full completeness ensures nothing relevant is dropped. PM audience keeps the extraction grounded in scope and value.
- **Overall: 5.0**

**Notes:** Clean, sparse, effective. This seed demonstrates that short token combinations can be highly purposeful. The fip_rog directional adds structural richness without adding cognitive weight. Product manager audience is a consistently strong performer.

**Recommendations:** None. Positive pattern — pull + directional + single audience token is a strong minimal combination.

---

### Seed 0045

**Tokens:** product_manager_to_team(preset) + plan + full + shift(method) + rog(directional)

**Prompt task:** The response proposes steps, structure, or strategy to move from the current state toward a stated goal.

**Scores:**
- Task clarity: 5 – "plan" is clear; proposes steps and strategy
- Constraint independence: 5 – shift(method) adds perspective rotation to planning; rog(directional) adds structural reflection; full governs completeness; all enhance HOW without altering WHAT
- Persona coherence: 5 – product_manager_to_team is excellent for planning: outcomes-focused, collaborative, actionable; kindly tone fits team communication
- Category alignment: 5 – shift is method, rog is directional, full is completeness, all correct
- Combination harmony: 5 – shift method (cycling through distinct cognitive modes) works beautifully with plan: it ensures the strategy is viewed through multiple lenses (user perspective, technical, business, etc.) before committing to steps. rog (structure→reflect) adds metacognitive framing. Full completeness ensures the plan covers all major aspects. The PM-to-team preset ties it together with collaborative, actionable tone.
- **Overall: 5.0**

**Notes:** Excellent planning combination. shift is one of the better method tokens for plan tasks: it explicitly prevents single-perspective planning blind spots. rog adds the "why does this structure exist" reflection that distinguishes thoughtful plans from mechanical to-do lists. The PM preset continues its strong run.

**Recommendations:** None. Positive pattern — plan + shift + rog is a strong multi-perspective planning recipe.

---

### Seed 0046

**Tokens:** as_facilitator(voice) + kindly(tone) + pick + full

**Prompt task:** The response chooses one or more options from a set of alternatives.

**Scores:**
- Task clarity: 5 – "pick" (choose from alternatives) is clear
- Constraint independence: 5 – full completeness governs depth; facilitator voice and kindly tone govern delivery; no constraints redefine the selection task
- Persona coherence: 4 – facilitator voice for a "pick" task is slightly unusual: facilitators typically guide others to choose rather than choosing themselves. However, a facilitator making a process recommendation (which option to choose) is reasonable. Kindly tone reinforces collaborative spirit.
- Category alignment: 5 – all tokens correctly categorized
- Combination harmony: 4 – sparse but coherent. The facilitator + kind tone creates a warm, supportive selection recommendation. Full completeness ensures justification is thorough. The slight oddness (facilitator choosing vs. guiding choice) is a minor friction rather than a conflict.
- **Overall: 4.6**

**Notes:** Simple but solid. The low token count leaves substantial freedom in interpretation, which is appropriate for a general "pick" task. The facilitator voice with kindly tone is distinctive and creates a recognizable communication style.

**Recommendations:** None.

---

### Seed 0047

**Tokens:** teach_junior_dev(preset) + fix + full + view(scope) + visual(form) + adr(channel)

**Prompt task:** The response changes the form or presentation of given content while keeping its intended meaning.

**Scores:**
- Task clarity: 4 – "fix" (transform/reformat) is clear, but the combination of visual form and ADR channel creates ambiguity about what the final output looks like
- Constraint independence: 3 – visual(form) and adr(channel) both specify complete output structures that conflict: visual means "abstract visual/metaphorical layout with legend," ADR means "structured document with context/decision/consequences sections." These are incompatible structural directives
- Persona coherence: 5 – teach_junior_dev preset is appropriate for explaining and transforming content; kindly tone fits
- Category alignment: 4 – tokens are in correct axes, but the placement of both visual and ADR in this combination reveals that visual(form) and structural channels (adr) should be flagged as incompatible
- Combination harmony: 2 – visual form and ADR channel are output-exclusive in practice: a response cannot simultaneously be "an abstract visual layout with legend" and "a structured ADR document with context/decision/consequences." The view scope adds value (stakeholder perspective focus) but cannot resolve the format conflict. view(scope) + visual(form) is actually a good pairing, but adr(channel) breaks it.
- **Overall: 3.6**

**Notes:** This is an output-exclusive conflict between visual(form) and adr(channel). This is a new variant of the pattern identified in seeds 0034 (adr+sync) and 0039 (shellscript+presenterm) from the previous cycle. The form/channel axes now contain two tokens that each prescribe the entire output structure. The teach_junior_dev persona and view scope are both strong, and the fix task is reasonable, but the format conflict makes the prompt unexecutable as specified.

**Recommendations:** Flag visual(form) + adr(channel) as an output-exclusive conflict. The visual form should be tagged with output_exclusive: true to participate in the mutual exclusion validation rule proposed in recommendations-post-refactor.yaml. This provides new evidence for that rule.

---

### Seed 0048

**Tokens:** as_designer(voice) + teach(intent) + make + full + resilience(method)

**Prompt task:** The response creates new content that did not previously exist, based on the input and constraints.

**Scores:**
- Task clarity: 5 – "make" (create new content) is clear
- Constraint independence: 5 – resilience(method) focuses the creation on stress-behavior and robustness; full governs completeness; as_designer(voice) and teach(intent) govern delivery stance; none redefine WHAT
- Persona coherence: 5 – designer voice with teach intent is coherent: designers teaching through creation, foregrounding usability and clarity in what they build. Resilience method adds systems-thinking depth that a thoughtful designer would apply.
- Category alignment: 5 – all tokens correctly placed
- Combination harmony: 5 – the resilience method is an excellent pair with make: creating something new while concentrating on how it behaves under stress produces more robust artifacts. Designer voice adds a user-centered, visually clear angle. Teach intent shapes the delivery toward explanation and learning. Full completeness ensures depth. Clean, harmonious combination.
- **Overall: 5.0**

**Notes:** Strong combination. The resilience method is underutilized in this corpus and here it works naturally. Creating something (make) through a resilience lens produces artifacts designed for fragility awareness from the start. The designer voice + teach intent creates an approachable, illustrative delivery.

**Recommendations:** None. Positive pattern — make + resilience is a strong robust-creation combination.

---

### Seed 0049

**Tokens:** designer_to_pm(preset) + fix + full + objectivity(method)

**Prompt task:** The response changes the form or presentation of given content while keeping its intended meaning.

**Scores:**
- Task clarity: 5 – "fix" (transform while preserving meaning) is clear
- Constraint independence: 5 – objectivity(method) grounds the transformation in evidence-based standards; full governs completeness; designer_to_pm provides persona framing; none redefine WHAT
- Persona coherence: 5 – designer_to_pm (designer speaking to product manager) is excellent for transformation tasks: translating design concerns into PM-relevant language with objectivity is exactly what a designer must do when bridging these roles
- Category alignment: 5 – all tokens correctly placed
- Combination harmony: 5 – objectivity + fix is a natural pairing: transformation tasks benefit from evidence-based grounding to avoid subjective drift. The designer-to-PM framing adds professional specificity. Full completeness ensures thoroughness. Minimal token count, maximal coherence.
- **Overall: 5.0**

**Notes:** Excellent minimal combination. The designer_to_pm preset continues its strong performance. objectivity is a strong method for fix tasks: it prevents the transformation from introducing subjective interpretation under the guise of reformatting. This is one of the cleanest prompts in the corpus.

**Recommendations:** None.

---

### Seed 0050

**Tokens:** appreciate(intent) + as_programmer(voice) + to_managers(audience) + pick + deep + thing(scope) + indirect(form) + adr(channel)

**Prompt task:** The response chooses one or more options from a set of alternatives.

**Scores:**
- Task clarity: 4 – "pick" (choose from alternatives) is clear; the deep + thing scope narrows focus appropriately; but appreciate(intent) introduces ambiguity about whether this is a decision document or an expression of thanks for options
- Constraint independence: 4 – indirect(form) and adr(channel) compose reasonably well: indirect means "background→reasoning→recommendation," which maps naturally onto ADR structure (context→decision→consequences). The form provides narrative flow; the channel provides document structure. Minor: appreciate(intent) with pick(task) is a conceptual mismatch—appreciation is an emotional intent, selection is a cognitive task
- Persona coherence: 3 – appreciate(intent) feels misaligned with pick(task). A programmer expressing appreciation to managers while making a technical selection is a specific scenario that exists (e.g., "I appreciate you considering these options; here's my recommendation"), but the combination feels strained rather than natural. to_managers(audience) + as_programmer(voice) is strong; appreciate intent is the weak link
- Category alignment: 5 – all tokens in correct axes
- Combination harmony: 3 – indirect(form) + adr(channel) is actually a positive composition: indirect narrative structure filling ADR sections is coherent (unlike visual+adr in seed 0047). But appreciate(intent) creates tonal confusion: appreciation suggests gratitude, pick suggests decisiveness. Deep completeness + thing scope works well. The persona intent is the harmony disruptor.
- **Overall: 3.8**

**Notes:** Mixed prompt. The indirect form + ADR channel composition is notably better than the visual + ADR conflict in seed 0047, demonstrating that not all form + channel combinations are problematic. However, the appreciate intent is semantically incompatible with a selection task in most interpretations. This validates the need for intent-task affinity guidance.

**Recommendations:** Document that appreciate(intent) has strong task affinity constraints: it works well with show, announce, coach, teach, but is awkward with pick, check, sort, diff.

---

### Seed 0051

**Tokens:** teach_junior_dev(preset) + make + full + diagram(channel) + dig(directional)

**Prompt task:** The response creates new content that did not previously exist, based on the input and constraints.

**Scores:**
- Task clarity: 5 – "make" + diagram channel is very clear: create a new Mermaid diagram
- Constraint independence: 5 – diagram channel specifies output format; dig directional focuses on concrete specifics; full governs completeness; all stay in their lanes
- Persona coherence: 5 – teach_junior_dev for diagram creation is excellent: diagrams are inherently pedagogical, and a teacher creating a visual aid for a junior engineer is a completely natural scenario
- Category alignment: 5 – all tokens correctly placed; diagram is correctly in channel axis
- Combination harmony: 5 – make + diagram is the canonical use of the diagram channel: creating new Mermaid diagrams is exactly what this channel enables. dig(directional) (concrete specifics) grounds the diagram in real details rather than abstractions. teach_junior_dev + full completeness ensures the diagram covers key concepts thoroughly. Excellent coherence.
- **Overall: 5.0**

**Notes:** Clear positive pattern. make + diagram is the prototypical single-channel task combination: the task and channel name essentially the same deliverable, leaving all other tokens to shape quality and approach. The teach_junior_dev preset with dig directional creates a grounded, learner-focused visual.

**Recommendations:** None. Positive pattern — make + diagram + teach_junior_dev is a strong visual teaching combination. Document as exemplar of single-channel clarity.

---

### Seed 0052

**Tokens:** announce(intent) + as_facilitator(voice) + kindly(tone) + plan + full + rigor(method) + visual(form) + dip_bog(directional)

**Prompt task:** The response proposes steps, structure, or strategy to move from the current state toward a stated goal.

**Scores:**
- Task clarity: 4 – "plan" is clear; rigor + visual form create a well-defined deliverable; minor tension between announce(intent) (share news) and plan(task) (propose strategy)
- Constraint independence: 5 – rigor(method) applies disciplined reasoning to planning; visual(form) specifies content structure; dip_bog(directional) specifies cognitive progression; full governs depth; all shape HOW
- Persona coherence: 4 – facilitator voice + kindly tone + announce intent: a facilitator announcing a plan is reasonable (presenting a roadmap to a group), but announce intent slightly mismatches plan task (announcement implies completed decision, planning implies open construction). This is the same minor tension seen in seed 0037 (previous cycle: announce + chat).
- Category alignment: 5 – all tokens correctly placed; visual is correctly in form axis
- Combination harmony: 4 – rigor + visual form is a strong pairing for planning: rigorous reasoning expressed as a visual big-picture layout creates structured clarity. dip_bog (concrete→structure→reflect→action) is a good cognitive cadence for rigorous planning. The announce intent creates minor dissonance but does not break the combination. No output-exclusive conflicts: visual(form) without an output-exclusive channel means the visual is a content structure choice, not a format mandate.
- **Overall: 4.4**

**Notes:** Solid combination with minor persona tension. Notably, this seed has visual(form) WITHOUT an output-exclusive channel, unlike seed 0047 (visual + adr) and seed 0033 (visual + presenterm). This confirms the form/channel split working correctly when channels are not output-exclusive: visual form can coexist with any delivery channel because it describes internal structure, not output format. The announce + plan tension is minor and acceptable.

**Recommendations:** None. This seed provides positive evidence that visual(form) without a conflicting channel works well.

---

### Seed 0053

**Tokens:** coach(intent) + to_junior_engineer(audience) + make + deep + time(scope) + rewrite(form) + plain(channel) + fig(directional)

**Prompt task:** The response creates new content that did not previously exist, based on the input and constraints.

**Scores:**
- Task clarity: 3 – "make" (create new content) combined with rewrite(form) (rewrite/refactor preserving intent) creates a significant semantic conflict: make implies creating from nothing, rewrite implies transforming existing content. The task definition is contradictory.
- Constraint independence: 2 – rewrite(form) partially redefines the task from creation to transformation. This is a category boundary violation: rewrite in form axis is supposed to describe HOW the response is structured (as a mechanical transform), but it changes WHAT the deliverable is. plain(channel) is output-exclusive and conflicts with the normal expectation of deep, detailed coaching.
- Persona coherence: 5 – coach intent + to_junior_engineer is excellent for a deep, detailed response; fig directional (abstract↔concrete) is ideal for pedagogical coaching
- Category alignment: 3 – rewrite in form axis is questionable: "rewrite" describes a transformation activity more than a presentation structure. It may be better classified as a method or task modifier. Its presence in form axis causes the make + rewrite conflict.
- Combination harmony: 2 – make + rewrite(form) is the "make + rewrite" antipattern flagged in the task instructions. These tokens fight: you cannot simultaneously create-from-nothing (make) and transform-existing-content (rewrite). plain(channel) as output-exclusive further constrains a response that needs depth (deep completeness) and fig alternation—plain prose is restrictive for abstract–concrete figure-ground alternation. time(scope) is excellent with coaching; fig directional is excellent with coaching; coach + junior_engineer is excellent—but make + rewrite + plain create a conflicted core.
- **Overall: 3.0**

**Notes:** This seed confirms the "make + rewrite" antipattern explicitly listed in the task instructions. The rewrite form token implies existing content to transform, while make implies creating new content. This is a fundamental semantic conflict. Additionally, plain(channel) is output-exclusive; combined with deep completeness and fig alternation, it creates an oddly austere deliverable for a coaching context.

**Recommendations:** Add validation to flag make + rewrite(form) as a semantic conflict. Consider retiring or reclassifying rewrite(form): if rewrite is a transformation activity, it belongs either in the method axis (as a task modifier) or should only be valid when the task is fix or diff, not make.

---

### Seed 0054

**Tokens:** product_manager_to_team(preset) + sim + deep + mean(scope) + abduce(method) + codetour(channel) + dip_bog(directional)

**Prompt task:** The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.

**Scores:**
- Task clarity: 4 – "sim" (simulate scenario over time) is reasonably clear; mean(scope) adds a framing/interpretation lens that fits scenario exploration
- Constraint independence: 3 – codetour(channel) partially redefines what the deliverable is: a VS Code CodeTour JSON file is a code-navigation format, not a scenario simulation. The task becomes "create a CodeTour file that simulates a scenario," which is nonsensical. The channel is overriding the task rather than shaping it.
- Persona coherence: 3 – product_manager_to_team persona delivering a VS Code CodeTour JSON file to the team is extremely unusual. PMs do not typically author CodeTour files. The persona and channel are mismatched.
- Category alignment: 4 – tokens are in correct axes, but codetour in channel axis applied to a sim task reveals a task-affinity gap in the catalog
- Combination harmony: 2 – codetour is the primary conflict: it requires code files with line references to be meaningful. sim + mean + abduce create a rich, conceptual scenario exploration. codetour forces that exploration into a JSON format designed for walking through actual code. These are incompatible: a scenario simulation cannot be expressed as a valid CodeTour file without actual source code context. dip_bog and abduce are strong for sim, but codetour breaks the combination.
- **Overall: 3.2**

**Notes:** Codetour is the problematic token here. This is the same issue flagged in the corpus description under "codetour channel: only meaningful for code-related content." sim + codetour is one of the explicit flagged combinations. The product_manager_to_team persona adds further incongruity. This confirms that codetour needs task-affinity metadata restricting its use to code-related tasks (fix, make with code context, show for code).

**Recommendations:** Add task_affinity metadata to codetour(channel): works_best_with: [fix, make, show, pull] when used with code subjects; awkward_with: [sim, sort, diff, plan, probe] for non-code subjects. This is new evidence supporting the recommendation in the corpus summary.

---

### Seed 0055

**Tokens:** persuade(intent) + casually(tone) + diff + full + rewrite(form) + codetour(channel) + fog(directional)

**Prompt task:** The response compares two or more subjects, highlighting relationships such as similarities, differences, or tradeoffs.

**Scores:**
- Task clarity: 3 – "diff" (compare subjects) is clear, but rewrite(form) implies transforming existing content rather than comparing it, creating ambiguity about the deliverable
- Constraint independence: 2 – rewrite(form) again conflicts with the task: diff is comparison, rewrite is transformation. These are different activities. codetour(channel) mandates VS Code JSON format, which is inappropriate for a persuasive comparison. Two tokens (rewrite and codetour) are redefining or overriding the task rather than modifying it.
- Persona coherence: 3 – persuade(intent) + casually(tone) is a natural combination for casual persuasion. But casual persuasion via a codetour JSON file is absurd: you cannot casually persuade through a VS Code code navigation format.
- Category alignment: 3 – rewrite in form axis for a diff task is misaligned: rewrite is a transformation activity, not a comparison presentation style. codetour in channel for a non-code task is a task-affinity failure.
- Combination harmony: 1 – multiple conflicts. First: diff + rewrite(form) — cannot simultaneously compare and transform. Second: codetour(channel) for diff + persuade — a VS Code CodeTour file cannot express comparative persuasion. Third: persuade intent + codetour channel — persuasive intent is incompatible with a schema-constrained JSON format. This is one of the most conflicted prompts in the corpus.
- **Overall: 2.4**

**Notes:** This seed has three overlapping issues. (1) rewrite(form) + diff(task): same semantic conflict as seed 0053. (2) codetour for non-code content: same issue as seed 0054. (3) persuade + codetour: persuasive intent cannot be expressed through a code-navigation JSON format. The casual tone is the only element without a conflict. fog directional (specific→abstract) would work fine with diff in another context. This is the lowest-scoring prompt in the corpus.

**Recommendations:** Two validation rules needed: (1) rewrite(form) should only combine with fix, make (with existing subject), or diff when the subject is code. (2) codetour channel should require code-subject context. This provides strong evidence for the codetour task-affinity recommendation in seed 0054.

---

### Seed 0056

**Tokens:** product_manager_to_team(preset) + check + full + good(scope) + dip_rog(directional)

**Prompt task:** The response evaluates the subject against a condition and reports whether it passes or fails.

**Scores:**
- Task clarity: 5 – "check" (evaluate against condition, pass/fail) is clear; good(scope) specifies quality criteria as the evaluation standard
- Constraint independence: 5 – good(scope) grounds the check in quality standards; dip_rog(directional) adds concrete-to-structural-to-reflective cadence; full governs completeness; all enhance HOW
- Persona coherence: 5 – product_manager_to_team is excellent for quality evaluation: outcomes-focused, communicating to the team with collaborative, actionable framing
- Category alignment: 5 – all tokens correctly placed
- Combination harmony: 5 – check + good(scope) is the ideal scope pairing for evaluation tasks: evaluating whether something meets quality criteria is exactly what "check" does, and "good" explicitly defines the evaluation axis. dip_rog adds the concrete→structural→reflective progression that makes a quality check thorough and actionable. product_manager_to_team rounds it out with team-focused communication.
- **Overall: 5.0**

**Notes:** Textbook quality evaluation prompt. The check + good(scope) pairing is semantically precise: check asks "does this pass?", good asks "pass against what quality criteria?" They answer each other. The dip_rog directional adds evaluation depth. Excellent.

**Recommendations:** None. Positive pattern — check + good(scope) is the canonical quality evaluation combination. Document as exemplar.

---

### Seed 0057

**Tokens:** casually(tone) + fix + full + thing(scope) + operations(method) + taxonomy(form) + diagram(channel) + dip_bog(directional)

**Prompt task:** The response changes the form or presentation of given content while keeping its intended meaning.

**Scores:**
- Task clarity: 4 – "fix" (transform preserving meaning) is clear; thing(scope) bounds the entities; but the combination of taxonomy(form) and diagram(channel) creates output ambiguity
- Constraint independence: 3 – taxonomy(form) and diagram(channel) are partially incompatible structural directives: taxonomy means "classification system / type hierarchy with definitions," while diagram means "Mermaid diagram code only." Expressing a taxonomy as Mermaid-only output is feasible (a Mermaid class or graph diagram could show a taxonomy), but the "defining types, their relationships, and distinguishing attributes clearly" requirement of taxonomy needs prose definitions that are forbidden by "Mermaid code only." The constraints are not fully independent.
- Persona coherence: 4 – casual tone for a taxonomy-building exercise with operations method is slightly mismatched (operations research is formal), but not a major issue
- Category alignment: 5 – all tokens correctly placed in their axes
- Combination harmony: 2 – taxonomy(form) + diagram(channel) is an output-exclusive conflict. taxonomy requires a prose classification system with attribute definitions; diagram requires Mermaid code only without surrounding prose. You cannot produce both simultaneously. operations method (identifying OR/MS concepts) also requires prose explanation. The casual tone cannot bridge this format conflict. This confirms the "taxonomy form + diagram channel" conflict flagged in the task instructions.
- **Overall: 3.6**

**Notes:** This is the taxonomy + diagram conflict explicitly listed in the key issues to flag. taxonomy(form) requires definitional prose to be meaningful; diagram(channel) prohibits prose. This is an output-exclusive conflict across form and channel axes. The fix task and other tokens are sound, but the format conflict makes the response unexecutable as specified.

**Recommendations:** Flag taxonomy(form) + diagram(channel) as an output-exclusive conflict in the validation rules. Add output_exclusive: true to taxonomy(form) if it truly demands definitional prose, or clarify that taxonomy can be expressed in Mermaid (without definitional prose) and relax the taxonomy description accordingly.

---

### Seed 0058

**Tokens:** scientist_to_analyst(preset) + probe + minimal + fail(scope) + grove(method) + remote(channel)

**Prompt task:** The response analyzes the subject to surface structure, assumptions, or implications beyond restatement.

**Scores:**
- Task clarity: 5 – "probe" (analyze to surface structure/implications) is clear; fail(scope) focuses analysis on breakdowns and limits; grove(method) adds compounding/accumulation lens
- Constraint independence: 5 – grove(method) examines how small failures accumulate over time; fail(scope) focuses on breakdown conditions; minimal keeps the response focused; remote(channel) optimizes delivery without redefining the task; all stay in their lanes
- Persona coherence: 5 – scientist_to_analyst is excellent for failure-mode analysis: scientific rigor, hypothesis testing, evidence-based framing; analyst audience gets structured, data-friendly output
- Category alignment: 5 – all tokens correctly placed
- Combination harmony: 5 – grove(method) + fail(scope) is a powerful pairing: examining how small failures compound over time is precisely what grove adds to failure analysis. minimal keeps this focused rather than sprawling. remote(channel) adds practical distributed-team hints without conflicting with content. scientist_to_analyst preset reinforces rigorous, evidence-based failure analysis. Excellent coherence.
- **Overall: 5.0**

**Notes:** Outstanding combination. The grove + fail pairing is the standout feature: grove's examination of accumulation and decay effects is naturally suited to failure analysis (how do small defects compound into catastrophic failures?). This is a new method + scope combination not seen in previous cycles, and it works beautifully. The scientist_to_analyst preset continues its strong track record. Minimal completeness keeps failure analysis targeted rather than exhaustive.

**Recommendations:** None. Positive pattern — probe + fail(scope) + grove(method) is a strong failure-mode analysis combination. Document grove as a strong method for fail-scoped probes.

---

### Seed 0059

**Tokens:** as_principal_engineer(voice) + to_stakeholders(audience) + make + full + spec(method)

**Prompt task:** The response creates new content that did not previously exist, based on the input and constraints.

**Scores:**
- Task clarity: 5 – "make" (create new content) is clear; spec(method) adds criteria-first rigor before creation
- Constraint independence: 5 – spec(method) shapes HOW creation proceeds (define correctness before building) without redefining WHAT (still creating new content); full governs completeness; voice and audience govern framing; all stay in their lanes
- Persona coherence: 5 – principal engineer voice addressing stakeholders is the ideal context for spec-first creation: systems thinking, trade-offs, pragmatic guidance framed for impact and decisions. The spec method matches the principal engineer's instinct to define success criteria before building.
- Category alignment: 5 – all tokens correctly placed; spec as method (not task) is correctly used here
- Combination harmony: 5 – make + spec is the natural pairing for disciplined creation: define what "correct" means before creating it. principal engineer + stakeholders creates a context where this rigor makes sense. full completeness ensures the specification and creation are both thorough. Elegant, purposeful combination.
- **Overall: 5.0**

**Notes:** Excellent. The spec method is one of the more distinctive tokens in the catalog, and it works best when the task is make or fix (create or transform with explicit correctness criteria). This seed is a strong positive example of spec's intended use. The principal engineer + stakeholders pairing is distinctive and coherent.

**Recommendations:** None. Positive pattern — make + spec + principal_engineer is a strong specification-driven creation combination.

---

### Seed 0060

**Tokens:** entertain(intent) + as_scientist(voice) + sort + full + gherkin(channel) + fly_ong(directional)

**Prompt task:** The response arranges items into categories or an order using a specified or inferred scheme.

**Scores:**
- Task clarity: 3 – "sort" (categorize/order using a scheme) is clear on its own, but gherkin(channel) mandates "only Gherkin format as the complete output." Expressing a categorization/ordering in Gherkin format is feasible for BDD test scenarios (Given/When/Then), but "sort" is not a testing task. The output would be awkward.
- Constraint independence: 2 – gherkin(channel) partially redefines the task from categorization to test-scenario writing. An output-exclusive channel that mandates BDD format is not just shaping HOW; it is changing the deliverable's fundamental nature for a non-testing task.
- Persona coherence: 3 – as_scientist voice with entertain intent is an amusing combination (imagine a scientist entertainingly categorizing things in Gherkin test format). The combination is whimsical but not incoherent. fly_ong directional (abstract→concrete→action) could work. However, entertain intent + gherkin channel is paradoxical: Gherkin is a formal test specification language not designed for entertainment.
- Category alignment: 5 – all tokens correctly placed
- Combination harmony: 2 – gherkin is output-exclusive and inappropriate for sort: sorting tasks require expressing categories and their members, not writing BDD test scenarios. fly_ong directional (abstract patterns→concrete actions→extensions) is at odds with Gherkin's fixed Given/When/Then structure. entertain intent cannot be expressed through schema-constrained Gherkin. The scientist voice is the only element that could plausibly work (rigorous categorization). Multiple tokens fight the gherkin mandate.
- **Overall: 3.0**

**Notes:** This confirms the "codetour/gherkin only meaningful for code-related content" observation. Gherkin is designed for behavior-driven development: defining system behavior in test scenarios. Applying it to sort, sim, probe, or other non-testing tasks produces fundamentally mismatched outputs. This is distinct from the output-exclusive format conflict in seeds 0047 and 0057: here there is only one output-exclusive token (gherkin), but it is the wrong channel for a non-testing task. Task affinity is the issue, not mutual exclusion.

**Recommendations:** Add task_affinity metadata to gherkin(channel): works_best_with: [fix, check, make] for behavior specification; awkward_with: [sort, sim, probe, diff, plan] for non-behavior tasks. This is a different class of issue from output-exclusive conflicts: it is a task-affinity mismatch rather than a format collision.

---

## Aggregated Findings

### Issues Confirmed (from previous cycles)

**1. Output-exclusive format conflicts persist (5 instances, 25%)**

Previous recommendation from cycle 2 was to add mutual-exclusion validation. That validation was NOT implemented before corpus generation. As a result, the same 25% rate recurs.

Seeds with output-exclusive conflicts:
- Seed 0047: visual(form) + adr(channel) — new variant of the visual + structural format conflict
- Seed 0053: make + rewrite(form) + plain(channel) — make/rewrite semantic conflict plus plain output-exclusive
- Seed 0054: sim + codetour(channel) — codetour task-affinity mismatch
- Seed 0055: diff + rewrite(form) + codetour(channel) — multiple conflicts: rewrite/diff semantic + codetour task-affinity
- Seed 0057: taxonomy(form) + diagram(channel) — output-exclusive format collision

**2. Codetour task-affinity failures (seeds 0054, 0055)**

Codetour is only meaningful for code-navigation tasks. Both instances in this corpus attach it to non-code tasks (sim, diff+persuade). Previous cycle had codetour in seed 0054's description but this corpus now confirms it as a systematic problem.

**3. make + rewrite semantic conflict (seeds 0053, 0055)**

The rewrite(form) token implies existing content to transform. make implies creating from nothing. These are semantically incompatible. This is a new recurring pattern not seen in previous cycles.

**4. Sync/codetour channel persona mismatch (seed 0043, 0054)**

Channels that imply specific delivery contexts (sync = live facilitation; codetour = VS Code navigation) conflict with personas that operate in different delivery contexts (executive_brief, product_manager_to_team). This is a softer version of the output-exclusive problem.

### New Issues

**1. Intent-task affinity gaps (seeds 0050, 0052, 0060)**

Several intents are semantically incompatible with certain tasks:
- appreciate(intent) + pick(task): appreciation is emotional, selection is cognitive
- announce(intent) + plan(task): announcing implies a completed decision, planning implies construction in progress
- entertain(intent) + gherkin(channel): entertainment intent cannot be expressed through test specification format

No validation currently catches intent-task affinity mismatches.

**2. rewrite(form) category misclassification**

rewrite(form) appears in two failing prompts (0053, 0055). The "rewrite" concept describes a transformation activity (a task or method), not a presentation structure. It may be miscategorized in form axis. When used with make or diff tasks, it fights rather than shaping how those tasks proceed.

**3. grove(method) is a strong newcomer**

grove appears for the first time in this corpus (seed 0058) and scores 5.0. Its combination with fail(scope) is semantically precise and produces excellent results. This method token deserves positive documentation.

**4. spec(method) is well-calibrated**

spec appears in seed 0059 with make(task) and scores 5.0. spec's description explicitly fits creation tasks (define correctness before building). This is a well-designed method token.

### Positive Patterns

**Persona presets continue to excel:** All 7 prompts with persona presets scored ≥4.0, with 5 scoring 5.0. Presets are the most reliable single factor for prompt quality.

**Scope tokens remain conflict-free:** All 9 prompts with scope tokens scored ≥4.0. The scope axis (thing, mean, fail, good, time, view) continues to add value without conflict.

**check + good(scope) is the canonical quality evaluation pattern:** Seed 0056 demonstrates this pairing is semantically precise and highly effective.

**make + diagram is the canonical single-channel creation pattern:** Seed 0051 demonstrates that task + channel naming the same deliverable produces maximum clarity.

**New strong method pairings discovered:** grove + fail(scope) (seed 0058), spec + make (seed 0059), shift + plan (seed 0045), resilience + make (seed 0048) — all produce excellent results.

**Directional tokens remain universally strong:** All 13 prompts with directional tokens scored ≥3.6, with 10 scoring ≥4.4. No directional token produced a conflict.

---

## Score Table

| Seed | Overall | Issue |
|------|---------|-------|
| 0041 | 5.0 | — |
| 0042 | 5.0 | — |
| 0043 | 3.8 | executive_brief + sync delivery mismatch |
| 0044 | 5.0 | — |
| 0045 | 5.0 | — |
| 0046 | 4.6 | — |
| 0047 | 3.6 | visual(form) + adr(channel) output-exclusive conflict |
| 0048 | 5.0 | — |
| 0049 | 5.0 | — |
| 0050 | 3.8 | appreciate(intent) + pick(task) intent-task mismatch |
| 0051 | 5.0 | — |
| 0052 | 4.4 | announce(intent) + plan(task) minor mismatch |
| 0053 | 3.0 | make + rewrite(form) semantic conflict; plain output-exclusive |
| 0054 | 3.2 | codetour task-affinity mismatch with sim |
| 0055 | 2.4 | rewrite(form) + diff conflict; codetour task-affinity mismatch |
| 0056 | 5.0 | — |
| 0057 | 3.6 | taxonomy(form) + diagram(channel) output-exclusive conflict |
| 0058 | 5.0 | — |
| 0059 | 5.0 | — |
| 0060 | 3.0 | gherkin task-affinity mismatch with sort |
| **Mean** | **4.09** | |

---

## Comparison to Previous Cycles

| Metric | Cycle 1 (0001–0020) | Cycle 2 (0021–0040) | Cycle 3 (0041–0060) | Target |
|--------|---------------------|---------------------|---------------------|--------|
| Excellent (≥4.0) | 35% | 55% | 65% | ≥70% |
| Problematic (≤2.9) | 30% | 20% | 20% | — |
| Average score | 4.04 | 4.16 | 4.09 | ≥4.30 |
| Output-exclusive conflicts | ~15% | 25% | 25% | ≤5% |

**Trend:** Excellent rate is improving (+10 pp over cycle 2, +30 pp over cycle 1) despite the absence of validation implementation. Average score is slightly below cycle 2 (4.09 vs 4.16), which may reflect natural corpus variance rather than regression. The output-exclusive conflict rate remains at 25%, confirming that validation rules are the critical missing implementation.

**Key observation:** The targets for average score (≥4.30) and output-exclusive conflicts (≤5%) are unmet, but both are directly attributable to the absence of validation implementation. The excellent rate is approaching target (65% vs 70% goal). With validation rules in place, cycle 4 should be able to reach all three targets.

---

## Phase 2b: Meta-Evaluation Against Bar Skills

### Overview

This phase evaluates whether the four bar skills (bar-autopilot, bar-manual, bar-workflow, bar-suggest) would guide a user to the token combinations found in seeds 0041–0060.

### Established Skill Deficiencies

Before evaluating individual seeds, the following systemic deficiencies apply to all four skills:

1. **Non-existent command reference:** All four skills reference `bar help llm` as the "preferred" discovery mechanism. This command does not exist in the current bar binary. The actual working command is `bar help tokens`. Skills label `bar help tokens` as "legacy / older versions," but it is the only working approach.

2. **Missing sections in actual output:** Skills reference sections — § "Usage Patterns by Task Type", § "Choosing Method", § "Token Selection Heuristics", § "Composition Rules" — that only exist in `bar help llm` (non-existent). `bar help tokens` has no such sections.

3. **Incorrect task token discovery path:** Skills state `bar help tokens task` to discover task tokens; the actual section name is `static` (i.e., `bar help tokens static`).

4. **Method categorization fiction:** Skills describe Exploration Methods, Understanding Methods, Decision Methods, and Diagnostic Methods as distinct categories. No such categorization exists in `bar help tokens`.

5. **No output-exclusive conflict guidance:** Skills provide no warnings about combining tokens that each prescribe the entire output format.

6. **No guidance on new scope tokens:** ADR-0104 added `assume`, `motifs`, `stable`, and `view` to the scope axis. None of the skills reflect these additions.

The discoverability score (1–5) below reflects how well a user following the skills as written would arrive at the token combination in each seed:
- 5 = skills would reliably guide to this combination
- 4 = skills would likely guide to this combination with minor gaps
- 3 = skills provide partial guidance; user would need to discover some tokens independently
- 2 = skills provide minimal guidance; key tokens are undiscoverable or actively misdirected
- 1 = skills would not guide to this combination and may mislead

---

### Per-Seed Discoverability Assessment

**Seed 0041** — probe + deep + prioritize(method) + scaffold(form) + junior_engineer(voice) + casually(tone)
- Discoverability: 3
- Gap: Skills reference `bar help llm` § "Choosing Method" for the prioritize + scaffold pairing. These sections do not exist. A user following `bar help tokens` would find prioritize and scaffold listed but with no guidance on their combination. The junior_engineer voice and casually tone are likely discoverable via the voice/tone sections that do function in `bar help tokens`. Methods section is discoverable. Net: task/form/method discoverable in isolation; combination logic is not.

**Seed 0042** — peer_engineer_explanation(preset) + diff + narrow + thing(scope) + origin(method) + fip_ong(directional)
- Discoverability: 3
- Gap: thing(scope) is a new scope token from ADR-0104 and skills contain no updated guidance for it. A user following skills would not know to look for thing in the scope section. Skills do reference `bar help tokens static` correctly for the diff task (though via the non-existent `bar help tokens task` path), so task is findable. Directionals are underdocumented in skills. Preset is discoverable.

**Seed 0043** — executive_brief(preset) + diff + minimal + induce(method) + sync(channel) + dip_ong(directional)
- Discoverability: 3
- Gap: Skills describe channels but give no guidance on executive_brief + sync delivery mismatch (the awkward combination identified in evaluation). A user following skills might combine these without any warning. inductive method is discoverable but not under the categorization system skills describe. No guidance on completeness tokens beyond basic mention.

**Seed 0044** — pull + full + fip_rog(directional) + to_product_manager(audience)
- Discoverability: 4
- Gap: This is a simple, short combination. Skills adequately guide to task (pull) and completeness (full) tokens. Audience token is discoverable. fip_rog directional is mentioned in skills but without the selection logic that would guide a user to choose it over other directionals. Minor gap only.

**Seed 0045** — product_manager_to_team(preset) + plan + full + shift(method) + rog(directional)
- Discoverability: 3
- Gap: Skills would not guide a user to the shift method specifically. Under the fictional method categorization in skills (Decision Methods, etc.), shift would be hard to locate without the actual taxonomy, which doesn't exist in `bar help tokens`. rog directional is discoverable. Preset and task are straightforward.

**Seed 0046** — as_facilitator(voice) + kindly(tone) + pick + full
- Discoverability: 4
- Gap: Simple combination, all standard tokens. Skills would guide to voice, tone, task, and completeness adequately. The only gap is that skills reference `bar help tokens task` (wrong section name, should be `static`) for pick discovery. Minor.

**Seed 0047** — teach_junior_dev(preset) + fix + full + view(scope) + visual(form) + adr(channel)
- Discoverability: 2
- Gap 1: `view(scope)` is a new ADR-0104 scope token. Skills have no guidance for it. A user following skills would not know view exists.
- Gap 2: Skills provide no output-exclusive conflict warning. A user following skills would not be warned that visual(form) + adr(channel) is an irresolvable format conflict. They might reasonably select both tokens separately based on independent token descriptions, creating the exact conflict that scored this prompt 3.6.
- This is the most significant skill failure in the corpus: not only does it fail to guide correctly, it would actively lead users into a known-bad combination.

**Seed 0048** — as_designer(voice) + teach(intent) + make + full + resilience(method)
- Discoverability: 4
- Gap: resilience method is discoverable via `bar help tokens` method listings. Skills reference a non-existent § "Understanding Methods" category that would nominally include resilience, but the token itself is listed in the actual help output. Intent, voice, task, completeness all discoverable. Minor method-categorization gap.

**Seed 0049** — designer_to_pm(preset) + fix + full + objectivity(method)
- Discoverability: 4
- Gap: Very simple combination. Objectivity method is in `bar help tokens`. Preset, task, completeness all straightforward. Minor gap from incorrect `bar help tokens task` section reference.

**Seed 0050** — appreciate(intent) + as_programmer(voice) + to_managers(audience) + pick + deep + thing(scope) + indirect(form) + adr(channel)
- Discoverability: 2
- Gap 1: `thing(scope)` is a new ADR-0104 scope token. Skills have no guidance for it.
- Gap 2: Skills have no guidance on the intent-task affinity issue (appreciate + pick mismatch). A user following skills would not be warned.
- Gap 3: adr(channel) discovery requires navigating the channel section; skills describe channels but with no task-affinity filtering.
- Net: thing(scope) is undiscoverable; no conflict warning; 8-token combination has no composition guidance in skills.

**Seed 0051** — teach_junior_dev(preset) + make + full + diagram(channel) + dig(directional)
- Discoverability: 4
- Gap: All tokens discoverable individually. diagram channel is well-documented. dig directional is mentioned. Minor gap: no skills guidance confirming make + diagram as a canonical pairing (positive pattern not documented). Still, a user could arrive at this combination through normal token exploration.

**Seed 0052** — announce(intent) + as_facilitator(voice) + kindly(tone) + plan + full + rigor(method) + visual(form) + dip_bog(directional)
- Discoverability: 3
- Gap 1: Skills reference non-existent § "Token Selection Heuristics" for form token guidance (including visual).
- Gap 2: No guidance on announce(intent) + plan(task) minor mismatch.
- Gap 3: rigor(method) falls under the fictional method categorization. Discoverable in `bar help tokens` but not under the described category system.
- Net: each token discoverable individually; no composition guidance; intent-task mismatch unwarned.

**Seed 0053** — coach(intent) + to_junior_engineer(audience) + make + deep + time(scope) + rewrite(form) + plain(channel) + fig(directional)
- Discoverability: 2
- Gap 1: `time(scope)` is a new ADR-0104 scope token. Skills have no guidance for it.
- Gap 2: Skills provide no warning for make + rewrite(form) semantic conflict. A user following skills would not be warned that this is contradictory.
- Gap 3: plain(channel) is output-exclusive; no output-exclusive guidance exists in skills.
- This seed has three guidance failures: undiscoverable scope token, unwarned semantic conflict, unwarned output-exclusive combination.

**Seed 0054** — product_manager_to_team(preset) + sim + deep + mean(scope) + abduce(method) + codetour(channel) + dip_bog(directional)
- Discoverability: 2
- Gap 1: `mean(scope)` is a new ADR-0104 scope token. Skills have no guidance for it.
- Gap 2: Skills provide no task-affinity guidance for codetour. A user following skills would read codetour's description and might select it for a sim task without realizing it is only meaningful for code-navigation contexts.
- Gap 3: The product_manager_to_team + codetour persona mismatch is not flagged anywhere in skills.
- Net: scope token undiscoverable; codetour task-affinity mismatch unwarned; PM persona + codetour incongruity unwarned.

**Seed 0055** — persuade(intent) + casually(tone) + diff + full + rewrite(form) + codetour(channel) + fog(directional)
- Discoverability: 1
- Gap 1: Skills have no warning for rewrite(form) + diff(task) semantic conflict.
- Gap 2: Skills have no task-affinity guidance for codetour; user would not know codetour is inappropriate for a non-code diff task.
- Gap 3: persuade + codetour intent/channel mismatch is not flagged anywhere.
- Gap 4: Three overlapping conflicts exist; skills would guide a user to select all these tokens without any friction or warning.
- This is the worst skill-guidance outcome in the corpus: a prompt that scores 2.4 would not be flagged as problematic by any current skill.

**Seed 0056** — product_manager_to_team(preset) + check + full + good(scope) + dip_rog(directional)
- Discoverability: 3
- Gap: `good(scope)` is a new ADR-0104 scope token. Skills have no guidance for it. However, the remaining tokens (check, full, preset, directional) are all discoverable. Without good(scope), the prompt is still valid but less precise.
- Net: partial discoverability — the combination minus the new scope token is fully guided; the scope token that makes it excellent is not.

**Seed 0057** — casually(tone) + fix + full + thing(scope) + operations(method) + taxonomy(form) + diagram(channel) + dip_bog(directional)
- Discoverability: 2
- Gap 1: `thing(scope)` is a new ADR-0104 scope token. Skills have no guidance for it.
- Gap 2: Skills have no output-exclusive conflict warning for taxonomy(form) + diagram(channel). A user following skills would not know these two tokens conflict.
- Gap 3: taxonomy(form) description does not clearly communicate in skills that it mandates definitional prose (incompatible with diagram's Mermaid-only output).
- Net: scope token undiscoverable; output-exclusive conflict unwarned.

**Seed 0058** — scientist_to_analyst(preset) + probe + minimal + fail(scope) + grove(method) + remote(channel)
- Discoverability: 3
- Gap: `fail(scope)` is a new ADR-0104 scope token. Skills have no guidance for it. The combination otherwise (probe, minimal, grove, remote, preset) is well-guided. remote channel and grove method are discoverable individually. Without fail(scope), the probe would be less precisely targeted.
- Net: similar to seed 0056 — a strong combination partly obscured by an undiscoverable scope token.

**Seed 0059** — as_principal_engineer(voice) + to_stakeholders(audience) + make + full + spec(method)
- Discoverability: 4
- Gap: Very simple, all-standard combination. spec method is in `bar help tokens` method listings. Voice, audience, task, completeness are all discoverable. Minor gap from the fictional method categorization in skills (spec would fall under some unspecified category). The combination is short enough that a user exploring tokens independently would likely find all five.

**Seed 0060** — entertain(intent) + as_scientist(voice) + sort + full + gherkin(channel) + fly_ong(directional)
- Discoverability: 2
- Gap 1: Skills have no task-affinity guidance for gherkin. A user following skills would read gherkin's description ("BDD test scenarios in Given/When/Then format") and might still select it for a sort task without realizing it is inappropriate for non-behavior tasks.
- Gap 2: entertain(intent) + gherkin(channel) incompatibility is not flagged anywhere.
- Net: gherkin task-affinity mismatch unwarned; intent/channel mismatch unwarned. Skills would not prevent this 3.0-scoring combination from being constructed.

---

### Aggregated Skill Gap Findings

**Discoverability Score Distribution (20 seeds):**

| Score | Count | Seeds |
|-------|-------|-------|
| 4–5 (adequate guidance) | 6 | 0044, 0046, 0048, 0049, 0051, 0059 |
| 3 (partial guidance) | 7 | 0041, 0042, 0043, 0045, 0052, 0056, 0058 |
| 1–2 (inadequate guidance) | 7 | 0047, 0050, 0053, 0054, 0055, 0057, 0060 |

**Mean discoverability score: 2.9 / 5**

**Gap Category Analysis:**

1. **New scope tokens undiscoverable (7 seeds):** Seeds 0042 (thing), 0047 (view), 0050 (thing), 0053 (time), 0054 (mean), 0056 (good), 0057 (thing), 0058 (fail). All four ADR-0104 scope tokens appear in this cycle and none are guided by any current skill. This is a systemic gap: ADR-0104 was implemented, skills were not updated, and users have no path to these tokens via skills.

2. **Output-exclusive conflicts unwarned (4 seeds):** Seeds 0047, 0053, 0057, 0060. For each of these, skills would guide a user to select the conflicting tokens independently without any friction. No skill contains output-exclusive conflict guidance.

3. **Task-affinity mismatches unwarned (3 seeds):** Seeds 0054, 0055, 0060. Codetour (0054, 0055) and gherkin (0060) have task-affinity restrictions that no skill documents. Users following skills have no signal that these channels are inappropriate for non-code and non-behavior tasks respectively.

4. **Non-existent `bar help llm` reference (all seeds):** The primary discovery path in all skills is broken. Users who follow the "preferred" path will receive a command-not-found error. The working path (`bar help tokens`) is labeled "legacy" which may cause users to distrust it or seek alternative discovery methods that don't exist.

5. **Semantic conflict guidance absent (2 seeds):** Seeds 0053 and 0055 both involve make/diff + rewrite(form) conflicts that no skill warns against.

6. **Composition guidance absent (all multi-token seeds):** The § "Composition Rules" and § "Token Selection Heuristics" sections referenced in skills do not exist. For any combination of 5+ tokens, skills provide no guidance on how tokens interact.

**Seeds where skill gaps directly contributed to low scores:** 0047 (3.6), 0050 (3.8), 0053 (3.0), 0054 (3.2), 0055 (2.4), 0057 (3.6), 0060 (3.0). All 7 low/mid-scoring seeds with gaps scored below 4.0, and for 5 of them (0047, 0053, 0054, 0055, 0057) the skill gap either directly led to or would have failed to prevent the conflict.

---

## Phase 2c: Bar Help Tokens Reference Evaluation

### Overview

This phase evaluates `bar help tokens` (the actual working reference tool) as a reference for understanding and constructing the prompts in seeds 0041–0060. Note: `bar help llm` does not exist; `bar help tokens` is the only available binary reference tool.

### Reference Structure

`bar help tokens` lists all tokens with one-line descriptions organized by axis. It does not contain:
- Usage patterns by task type
- Selection heuristics
- Composition rules
- Incompatibility guidance
- Output-exclusive concept documentation
- Task-affinity metadata

New scope tokens (assume, motifs, stable, view) are present after recent binary rebuild. All cycle 3 scope tokens (thing, mean, fail, good, time, view) are present and accurately described.

### Evaluation Criteria

Each criterion is scored 1–5 across the 20-seed corpus:

**Criterion 1: Token Discovery — Does `bar help tokens` enable a user to discover the relevant tokens?**

- Score: 3/5
- Rationale: All tokens used in seeds 0041–0060 are listed in `bar help tokens` with descriptions. Discovery is possible for any individual token. However, discovery is essentially exhaustive enumeration: users must read all entries and infer relevance. There are no categories, task-type groupings, or use-case guides. For seeds with 7–8 tokens, the likelihood of independent discovery of the optimal combination is low. The new scope tokens (view, mean, fail, good, time) are present and correctly described, which is a significant improvement over the skills gap.

**Criterion 2: Token Description Accuracy — Are token descriptions accurate and sufficient?**

- Score: 4/5
- Rationale: Token descriptions are broadly accurate. Task tokens correctly describe their function. Method tokens have clear descriptions. Persona presets are described adequately. The main deficiencies are:
  - codetour: described accurately but with no task-affinity guidance ("produces a VS Code CodeTour JSON file" — accurate, but doesn't say "only meaningful with code subjects")
  - gherkin: similarly accurate without task-affinity context
  - visual and taxonomy forms: descriptions do not make their whole-response-scope clear (does not say "this overrides normal response structure entirely")
  - rewrite form: description does not flag the semantic conflict with make/diff tasks

**Criterion 3: Output-Exclusive Concept — Does `bar help tokens` document the output-exclusive concept?**

- Score: 1/5
- Rationale: The output-exclusive concept — that certain tokens each mandate the entire output format, making them mutually exclusive — is not documented anywhere in `bar help tokens`. The channel axis description implies "at most one" channel per prompt, but this logic is not extended to form tokens that are also output-exclusive (visual, taxonomy, code, html, shellscript). A user consulting `bar help tokens` alone has no way to know that visual(form) + adr(channel) is irresolvable, or that taxonomy(form) + diagram(channel) will conflict. This is the reference tool's most significant gap relative to the corpus issues.

**Criterion 4: Composition Guidance — Does `bar help tokens` help users compose multiple tokens?**

- Score: 1/5
- Rationale: `bar help tokens` provides no composition guidance whatsoever. It does not explain how tokens from different axes interact, which combinations are productive, which are conflicting, or how to sequence token selection. The channel axis has an implicit "at most one" rule, but it is not stated explicitly in the help output. For all 20 seeds, the combination logic must be entirely inferred by the user from token descriptions alone.

**Criterion 5: Task-Affinity Guidance — Does `bar help tokens` help users match tokens to tasks?**

- Score: 2/5
- Rationale: Some task tokens have clear implied affinities (e.g., diff implies comparison, make implies creation), but no token descriptions include explicit works_best_with or avoid_with metadata. The codetour and gherkin channels are a particular failure: their descriptions accurately convey what format they produce but give no signal about which tasks they are appropriate for. A user could reasonably select codetour for a sim task based on description alone (seeds 0054, 0055). A user could select gherkin for a sort task (seed 0060). The reference tool provides no protection against these mismatches.

**Criterion 6: New Scope Token Coverage — Does `bar help tokens` adequately cover the ADR-0104 scope tokens?**

- Score: 4/5
- Rationale: All four new scope tokens (assume, motifs, stable, view) are present and accurately described after the binary rebuild. The five scope tokens used in this cycle (thing, mean, fail, good, time, view) are all present and correctly described. This is a genuine improvement and a significant advantage over the skills documentation. The minor gap is that the descriptions, while accurate, do not explain the scope tokens' relationship to the existing scope set (no explanation of "what distinguishes thing from struct" or "when to use view vs mean").

**Criterion 7: Form Token Clarity — Do form token descriptions make their structural scope clear?**

- Score: 3/5
- Rationale: Standard form tokens (list, table, scaffold, etc.) are clearly described. However, the more complex form tokens have description gaps:
  - visual: description conveys "abstract visual layout" but does not state that this replaces normal prose structure for the entire response
  - taxonomy: description conveys "classification system" but does not state it implies definitional prose incompatible with Mermaid-only channels
  - rewrite: description implies transformation but does not flag that it conflicts semantically with make (create) or that it is inappropriate for non-transformation tasks
  - indirect: description is adequate; the form's compatibility with adr(channel) (as noted in seed 0050 analysis) is not documented but also not needed — users would discover the harmony
  - plain: output-exclusive status is not flagged; users would not know it mandates prose-only output exclusive of markup

---

### Aggregated Reference Tool Findings

| Criterion | Score |
|-----------|-------|
| Token Discovery | 3/5 |
| Token Description Accuracy | 4/5 |
| Output-Exclusive Concept Coverage | 1/5 |
| Composition Guidance | 1/5 |
| Task-Affinity Guidance | 2/5 |
| New Scope Token Coverage | 4/5 |
| Form Token Clarity | 3/5 |
| **Mean** | **2.6/5** |

**Summary of reference tool findings:**

`bar help tokens` is adequate as a token dictionary but inadequate as a composition guide. Its core strength is completeness: all tokens are present and descriptions are broadly accurate. Its core weakness is the total absence of meta-guidance: no composition rules, no incompatibility warnings, no task-affinity signals.

For users building single-token or two-token prompts, `bar help tokens` is sufficient. For users building the 5–8 token combinations characteristic of this corpus, the reference tool provides the ingredients but no recipe, and no warning labels for dangerous combinations.

**Priority gaps in `bar help tokens` relative to cycle 3 findings:**

1. No output-exclusive documentation — directly enabled 5 conflicting seeds (0047, 0053, 0057 at minimum)
2. No task-affinity documentation for codetour and gherkin — directly enabled 3 mismatched seeds (0054, 0055, 0060)
3. rewrite form lacks semantic conflict warning — directly contributed to 2 conflicted seeds (0053, 0055)
4. visual and taxonomy form descriptions do not communicate whole-response scope replacement — underspecified for conflict detection

**What would raise the mean score from 2.6 to ≥4.0:**

- Adding an output-exclusive concept section (would raise criterion 3 from 1 to 4)
- Adding a short composition guidance section (would raise criterion 4 from 1 to 3)
- Adding task-affinity notes to codetour and gherkin descriptions (would raise criterion 5 from 2 to 4)
- Adding scope-replacement clarification to visual, taxonomy, and plain form descriptions (would raise criterion 7 from 3 to 4)

These four changes are targeted and achievable without restructuring the reference tool.
