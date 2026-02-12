# Shuffle Evaluation: Seeds 0081–0100
**Date:** 2026-02-11
**Evaluator:** Claude Sonnet 4.5
**Cycle:** 5

## Context

This is the fifth evaluation cycle. The previous cycle (seeds 0061–0080) showed regression: 50% excellent, 3.4 avg, 20% form+channel conflicts. ADR-0105 (Incompatibilities section in `bar help llm`) was completed before cycle 4, but didn't prevent new undocumented conflict patterns. Cycle 4 produced R1–R7 covering: sim+code/markup task-affinity, prose-form + code-channel rule, compound directionals documentation, sort+order tautology, taxonomy+channel composability, fix task naming, and adr sim task-affinity note in `bar help llm`. R6 (fix task clarification) is confirmed implemented — seed 0099 shows the updated description.

**Targets from recommendations-seeds-0061-0080.yaml:**
- Excellent (≥4.0): target ≥70% (prev 50%)
- Overall average: target ≥3.90 (prev 3.4)
- Form+channel conflicts: target ≤10% (prev 20%)

---

## Summary Statistics

- Total prompts: 20
- Excellent (4–5): 13 (65%)
- Acceptable (3): 3 (15%)
- Problematic/Broken (1–2): 4 (20%)
- Average score: 3.65
- Form+channel conflicts: 3 (15%) — cocreate+svg (0082), quiz+presenterm (0085), bug+sync (0099)
- Additional broken combos: sort+adr task-affinity (0091)
- Previous cycle (0061–0080): 50% excellent, 3.4 avg, 20% form+channel conflicts
- Trend: improvement in excellent rate (65% vs 50%) and average (3.65 vs 3.4); form+channel conflict rate reduced (15% vs 20%); sim+facilitate tension confirmed as recurring pattern; new task-affinity failure (sort+adr); R6 fix description confirmed implemented.

---

## Individual Evaluations

### Seed 0081

**Tokens:** sim + full + time(scope) + operations(method) + wasinawa(form) + fly bog(directional) + persona: teach_junior_dev

**Prompt task:** The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.

**Scores:**
- Task clarity: 5 — sim is a clear scenario-playback task
- Constraint independence: 4 — time(scope) amplifies sim's temporal nature; operations(method) adds OR/management-science framing; wasinawa(form) structures the reflection as What/So What/Now What; fly bog(directional) adds abstract-pattern-to-action lens; all complement without redefining. Minor: wasinawa is retrospective in character while sim plays forward — a slight but workable temporal tension.
- Persona coherence: 5 — teach_junior_dev is a natural fit for sim; scenario playback is a classic teaching device
- Category alignment: 5
- Combination harmony: 4 — sim + time(scope) is tight; operations(method) analytical lens adds value; wasinawa(form) works as scenario post-mortem structure; fly bog(directional) is coherent. Rich but not overcrowded.
- **Overall: 4**

**Notes:** Very coherent combination. wasinawa (retrospective framing) vs. sim (forward playback) is a minor semantic tension worth noting: the combination works best when sim is interpreted as a completed or ongoing scenario being reflected upon.

**Recommendations:**
- [ ] Positive pattern: sim + time(scope) is a strong pairing to highlight in bar-autopilot

---

### Seed 0082

**Tokens:** pull + max + thing(scope) + cluster(method) + cocreate(form) + svg(channel) + fly ong(directional) + persona: facilitator voice

**Prompt task:** The response selects or extracts a subset of the given information without altering its substance.

**Scores:**
- Task clarity: 4 — pull is clear
- Constraint independence: 2 — cocreate(form) requires interactive, iterative dialogue (propose small moves → check alignment → iterate); svg(channel) requires SVG markup-only output. These are fundamentally incompatible: cocreate needs back-and-forth prose interaction; svg mandates a single static SVG file with no surrounding prose.
- Persona coherence: 3 — facilitator voice works for cocreate but is incongruous with svg-only output
- Category alignment: 5
- Combination harmony: 2 — cocreate + svg is an output-exclusive conflict: cocreate generates collaborative prose dialogue; svg mandates code-only output. Same class as case+code and formats+slack (cycle 4, seeds 0075/0076). cocreate was not covered in ADR-0105 R2. Also: pull(task) + cluster(method) has slight directional tension — extract a subset vs. group all items — but is not a conflict.
- **Overall: 2**

**Notes:** cocreate(form) + svg(channel) is a new instance of the prose-form + code-channel conflict. The R2 recommendation from cycle 4 proposed adding "prose-form conflicts" to `bar help llm`, but cocreate specifically was not listed. This seed extends that list.

**Recommendations:**
- [ ] Edit: add cocreate(form) to the prose-form conflicts list in bar help llm § Incompatibilities

---

### Seed 0083

**Tokens:** sort + full + good(scope) + persona: executive_brief (programmer voice → CEO)

**Prompt task:** The response arranges items into categories or an order using a specified or inferred scheme.

**Scores:**
- Task clarity: 5 — sort is unambiguous; good(scope) bounds it to quality criteria
- Constraint independence: 5 — good(scope) defines the sorting dimension; full governs completeness; both shape HOW
- Persona coherence: 4 — programmer-to-CEO for quality-criteria sorting is slightly unusual but valid for feature prioritization, technical risk ranking, etc.
- Category alignment: 5
- Combination harmony: 4 — sort + good(scope) is a strong pairing: arranging by quality/success criteria is a classic prioritization pattern. No conflicts.
- **Overall: 4**

**Notes:** Clean, practical combination. sort + good(scope) is a useful prioritization pattern.

---

### Seed 0084

**Tokens:** sim + full + facilitate(form) + dip rog(directional) + persona: teacher-to-stakeholders

**Prompt task:** The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.

**Scores:**
- Task clarity: 3 — sim assumes the LLM performs the simulation; facilitate(form) assumes the LLM structures others in performing work. These two roles conflict, creating ambiguity about what the response should actually do.
- Constraint independence: 3 — facilitate(form) partially redefines the execution model (who does the work), creating a role conflict with sim's direct-execution assumption
- Persona coherence: 4 — teacher-to-stakeholders is reasonable; dip rog (grounded → reflective) adds appropriate analytical depth
- Category alignment: 5
- Combination harmony: 3 — sim + facilitate creates recurring conceptual tension: simulate (LLM does the work) vs. facilitate (LLM structures others doing the work). The combination is workable as "design a facilitation structure for a simulation exercise," but the ambiguity about whose role is primary makes it a 3.
- **Overall: 3**

**Notes:** First instance of the sim + facilitate tension (also confirmed in seed 0093). The combination is usable but requires clear intent from the user.

**Recommendations:**
- [ ] Document: sim + facilitate(form) combination guidance — clarify this means "facilitate a simulation discussion" not "LLM performs simulation directly"

---

### Seed 0085

**Tokens:** plan + narrow + meld(method) + quiz(form) + presenterm(channel) + bog(directional) + persona: product_manager_to_team

**Prompt task:** The response proposes steps, structure, or strategy to move from the current state toward a stated goal.

**Scores:**
- Task clarity: 4 — plan is clear
- Constraint independence: 2 — quiz(form) requires interactive Q&A flow (pose questions → receive answers → clarify); presenterm(channel) requires a static multi-slide Markdown deck. These are fundamentally incompatible: quiz requires back-and-forth interaction; presenterm is a static output format.
- Persona coherence: 4 — PM-to-team for plan tasks is natural
- Category alignment: 5
- Combination harmony: 2 — quiz(form) + presenterm(channel) is the same prose-form + code-channel conflict class. quiz requires interaction; presenterm is static. Cannot simultaneously be interactive quiz AND static presentation deck.
- **Overall: 2**

**Notes:** quiz(form) + presenterm(channel) extends the prose-form + code-channel conflict class. Like cocreate (seed 0082), quiz is an interactive/dialogue form that conflicts with any output-exclusive static channel.

**Recommendations:**
- [ ] Edit: add quiz(form) to the prose-form conflicts list in bar help llm § Incompatibilities

---

### Seed 0086

**Tokens:** diff + skim + experimental(method) + walkthrough(form) + ong(directional) + persona: product_manager_to_team

**Prompt task:** The response compares two or more subjects, highlighting relationships such as similarities, differences, or tradeoffs.

**Scores:**
- Task clarity: 5 — diff is unambiguous
- Constraint independence: 4 — walkthrough(form) provides step-by-step structure for comparison; experimental(method) proposes concrete tests; ong(directional) pushes toward action; all shape HOW
- Persona coherence: 4 — PM-to-team for compare + experiment is sensible (evaluate approaches, propose validation tests)
- Category alignment: 5
- Combination harmony: 4 — diff + walkthrough(form) is practical (walk through differences step by step); experimental(method) + ong(directional) both push toward actionable next steps. skim completeness appropriately limits depth. Coherent, action-oriented.
- **Overall: 4**

**Notes:** Good practical combination. diff + walkthrough + experimental + ong is a strong action-oriented comparison workflow.

---

### Seed 0087

**Tokens:** sort + full + remote(channel) + fly ong(directional) + persona: PM voice, gently tone

**Prompt task:** The response arranges items into categories or an order using a specified or inferred scheme.

**Scores:**
- Task clarity: 5 — sort is unambiguous
- Constraint independence: 5 — remote(channel) shapes delivery format (remote-optimized); fly ong(directional) modifies from abstract patterns → concrete actions; both shape HOW
- Persona coherence: 4 — PM voice with gentle tone for remote delivery is natural
- Category alignment: 5
- Combination harmony: 4 — sort + remote(channel) is coherent (organizing content for distributed delivery — workshop agenda, prioritized backlog for a distributed team). fly ong adds pattern-to-action flow. No conflicts.
- **Overall: 4**

**Notes:** remote(channel) appears rarely in evaluations; this seed shows it composing cleanly with sort.

---

### Seed 0088

**Tokens:** sim + minimal + stable(scope) + abduce(method) + indirect(form) + persona: product_manager_to_team

**Prompt task:** The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.

**Scores:**
- Task clarity: 4 — sim is clear; stable(scope) focuses the scenario on stability/persistence dynamics
- Constraint independence: 4 — stable(scope) defines what to examine (stability states); abduce(method) defines inference mode (abductive hypothesis generation); indirect(form) defines response structure (background → reasoning → bottom-line). All shape HOW.
- Persona coherence: 4 — PM-to-team for stability scenario analysis is reasonable
- Category alignment: 5
- Combination harmony: 4 — sim + stable(scope) is a tight pairing (stability dynamics scenarios); abduce(method) adds abductive reasoning; indirect(form) works for scenario briefings where reasoning leads to conclusion. The minimal completeness is a slight tension (sim benefits from more depth), but workable.
- **Overall: 4**

**Notes:** sim + stable(scope) is a strong new pairing — stability analysis scenarios (system design, market modeling, equilibrium analysis) are practical and well-served by this combination.

---

### Seed 0089

**Tokens:** show + full + persona: gently tone

**Prompt task:** The response explains or describes the subject for the stated audience.

**Scores:**
- Task clarity: 5
- Constraint independence: 5 — minimal tokens, no conflicts possible
- Persona coherence: 5
- Category alignment: N/A
- Combination harmony: 5 — baseline minimal case always scores 5
- **Overall: 5**

**Notes:** Confirms that the simplest combinations remain clean and function as the lower bound. No recommendations.

---

### Seed 0090

**Tokens:** make + skim + presenterm(channel) + bog(directional) + persona: designer_to_pm

**Prompt task:** The response creates new content that did not previously exist, based on the input and constraints.

**Scores:**
- Task clarity: 4 — make is clear; skim + presenterm is a slight tension (skim may produce a sketch rather than a full deck)
- Constraint independence: 4 — presenterm(channel) defines output format; bog(directional) modifies execution direction; both shape HOW
- Persona coherence: 4 — designer-to-PM for make + presenterm is natural (creating a deck to communicate design decisions)
- Category alignment: 5
- Combination harmony: 4 — make + presenterm is a natural pairing. skim + presenterm tension: skim suggests a light pass, which for a presenterm deck might produce an outline rather than a full slide deck. This is a minor tension rather than a conflict. No incompatibility.
- **Overall: 4**

**Notes:** make + presenterm is a canonical presentation creation pattern. skim + presenterm minor tension worth documenting.

---

### Seed 0091

**Tokens:** sort + full + time(scope) + adr(channel) + persona: inform intent

**Prompt task:** The response arranges items into categories or an order using a specified or inferred scheme.

**Scores:**
- Task clarity: 2 — sort (arrange into categories/order) combined with adr(channel) (Architecture Decision Record format) creates significant semantic tension. An ADR has a fixed structure (Context, Decision, Consequences) that is fundamentally a decision artifact, not a sorting/ordering artifact.
- Constraint independence: 2 — adr(channel) defines a complete decision-record output structure that doesn't accommodate a sorted list as the primary deliverable.
- Persona coherence: 4 — inform intent is appropriate
- Category alignment: 5 — tokens correctly placed but combination creates task-affinity failure
- Combination harmony: 2 — sort + adr(channel) is a task-affinity violation. sort produces a ranked/categorized list; adr produces a structured decision record. These are incompatible output types. time(scope) adding temporal dimension doesn't help — a timeline sort in ADR format is forced.
- **Overall: 2**

**Notes:** New task-affinity failure: sort + adr. The adr channel is appropriate for decision-making tasks (plan, probe, make) but conflicts with tasks that produce non-decision outputs (sort, pull, diff). This extends the task-affinity pattern documented for codetour and gherkin in ADR-0105 D2.

**Recommendations:**
- [ ] Edit: add adr(channel) to task-affinity restrictions in bar help llm § Incompatibilities. Document: adr is appropriate for plan/probe/make (decision-making tasks); conflicts with sort/pull/diff which produce non-decision outputs.

---

### Seed 0092

**Tokens:** probe + skim + fail(scope) + mod(method) + scaffold(form) + bog(directional) + persona: executive_brief (programmer → CEO)

**Prompt task:** The response analyzes the subject to surface structure, assumptions, or implications beyond restatement.

**Scores:**
- Task clarity: 4 — probe + fail(scope) is a tight pairing for failure mode analysis
- Constraint independence: 3 — scaffold(form) requires gradual "first principles" introduction for beginners; this conflicts with the executive_brief persona (CEO audience), who is not a beginner. Form and persona pull in opposite directions.
- Persona coherence: 3 — executive_brief (programmer→CEO) + scaffold(form) (beginner-level explanation) is a persona-form mismatch. Scaffolding from first principles doesn't fit CEO communication.
- Category alignment: 5
- Combination harmony: 3 — probe + fail(scope) is strong; mod(method) is unusual for failure analysis but not incoherent (cyclic failure patterns); scaffold(form) is the friction point (beginner framing for executive audience). bog(directional) is reasonable. Overall workable but with a clear form-persona mismatch.
- **Overall: 3**

**Notes:** New observation: scaffold(form) is an educational/teaching form token. When paired with senior executive personas (CEO, executive_brief), there's an audience mismatch. This is different from output-exclusive conflicts — it's a persona-form semantic incompatibility. bar help llm should document scaffold as most appropriate for learning/teaching contexts and flag friction with executive-level personas.

**Recommendations:**
- [ ] Edit: scaffold(form) description should note "most appropriate for educational/learning audiences (junior engineer, student); may feel mismatched with executive or expert audiences."

---

### Seed 0093

**Tokens:** sim + full + stable(scope) + facilitate(form) + fip rog(directional) + persona: PM audience, kindly, coach intent

**Prompt task:** The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.

**Scores:**
- Task clarity: 3 — same sim + facilitate tension as seed 0084
- Constraint independence: 3 — facilitate(form) partially redefines who does the work
- Persona coherence: 5 — coach intent + kindly + PM audience is coherent for facilitation
- Category alignment: 5
- Combination harmony: 3 — sim + facilitate recurring tension. fip rog (abstract ↔ concrete, examine patterns) + facilitate(form) creates an interesting facilitated simulation that alternates between principles and examples — not broken, but the primary tension remains.
- **Overall: 3**

**Notes:** Confirms the sim + facilitate pattern (both seeds 0084 and 0093). Two occurrences in 20 seeds (10% of corpus) suggests this is a non-trivial pattern that warrants documentation.

---

### Seed 0094

**Tokens:** make + max + grow(method) + dip bog(directional) + persona: peer_engineer_explanation

**Prompt task:** The response creates new content that did not previously exist, based on the input and constraints.

**Scores:**
- Task clarity: 5 — make is clear; max means exhaustive creation
- Constraint independence: 5 — grow(method) defines build strategy (simplest first, progressively generalize); dip bog(directional) (concrete → structure → act → extend) complements grow perfectly; both shape HOW
- Persona coherence: 5 — peer engineer to programmer is ideal for make+grow (technical progressive construction)
- Category alignment: 5
- Combination harmony: 5 — make + grow + dip bog is exceptionally coherent: create content starting from simplest valid behavior, ground in concrete examples, examine structure, extend. This is a canonical TDD-style construction approach. max completeness is consistent with grow's "defer complexity until forced" philosophy.
- **Overall: 5**

**Notes:** Excellent combination. make + grow + dip bog is a canonical pattern for incremental construction. Should be highlighted as a positive exemplar in bar-autopilot guidance.

---

### Seed 0095

**Tokens:** plan + full + plain(channel) + persona: Kent Beck audience, entertain intent

**Prompt task:** The response proposes steps, structure, or strategy to move from the current state toward a stated goal.

**Scores:**
- Task clarity: 5 — plan is unambiguous
- Constraint independence: 5 — plain(channel) shapes format; Kent Beck + entertain shapes voice; all independent
- Persona coherence: 4 — "entertain" intent is unusual for a plan task but creates a distinctive playful planning voice. Addressing Kent Beck (TDD inventor) specifically is creative and functional.
- Category alignment: 5
- Combination harmony: 4 — plan + plain(channel) is clean; entertain intent with Kent Beck audience creates a distinctive thought-experiment style. Not a conflict, just an unusual persona composition that works.
- **Overall: 4**

**Notes:** Notable for the "entertain" intent token paired with plan — an unusual but valid combination that creates a distinctive playful/exploratory planning voice.

---

### Seed 0096

**Tokens:** sort + deep + time(scope) + faq(form) + fip rog(directional) + persona: product_manager_to_team

**Prompt task:** The response arranges items into categories or an order using a specified or inferred scheme.

**Scores:**
- Task clarity: 4 — sort is clear; time(scope) focuses on temporal ordering
- Constraint independence: 5 — faq(form) structures output as Q&A; fip rog alternates abstract/concrete; deep completeness; all shape HOW
- Persona coherence: 5 — PM-to-team for temporal ordering tasks is natural
- Category alignment: 5
- Combination harmony: 4 — sort + time(scope) is tight (temporal ordering); faq(form) applied to sort is creative: "Q: What happens first? A: ... Q: What happens next? A: ..." produces a timeline in FAQ format, which could be useful for sequencing rationale. Not a conflict, just an unusual but workable form.
- **Overall: 4**

**Notes:** sort + faq(form) is a creative but valid combination — FAQ-formatted sort results are useful for timeline explanations or sequencing rationale where "why this order?" is as important as the order itself.

---

### Seed 0097

**Tokens:** pull + full + domains(method) + tight(form) + persona: scientist_to_analyst

**Prompt task:** The response selects or extracts a subset of the given information without altering its substance.

**Scores:**
- Task clarity: 5 — pull is unambiguous; domains(method) focuses extraction on domain boundaries
- Constraint independence: 5 — domains(method) identifies bounded contexts as the extraction criterion; tight(form) mandates concise prose; all shape HOW
- Persona coherence: 5 — scientist-to-analyst is ideal for pull+domains (extracting domain boundaries with scientific rigor for analytical presentation)
- Category alignment: 5
- Combination harmony: 5 — pull + domains(method) is a strong pairing (extract domain boundaries, bounded contexts, capabilities); tight(form) perfectly complements (concise prose is ideal for domain model summaries); scientist-to-analyst is a natural fit. Canonical domain analysis pattern.
- **Overall: 5**

**Notes:** Excellent combination. pull + domains + tight + scientist-to-analyst is a canonical domain model extraction pattern. Highlight as positive exemplar.

---

### Seed 0098

**Tokens:** show + full + act(scope) + mod(method) + persona: prompt engineer voice, persuade intent

**Prompt task:** The response explains or describes the subject for the stated audience.

**Scores:**
- Task clarity: 4 — show is clear; act(scope) focuses on operational dimension
- Constraint independence: 4 — act(scope) scopes explanation to actions/tasks; mod(method) applies cyclic/modular reasoning; persuade intent shapes communication goal; all independent
- Persona coherence: 3 — prompt engineer voice + persuade intent for explaining actions through modulo-style reasoning is very specific and slightly contrived. Not incoherent but the specificity creates an unusual persona.
- Category alignment: 5
- Combination harmony: 4 — show + act(scope) + mod(method) is coherent: explain actions through cyclic/modular patterns. persuade intent is the odd element — persuasion via modulo reasoning is unusual but not broken.
- **Overall: 4**

**Notes:** mod(method) appears in both seeds 0092 and 0098 — it's a mathematically unusual method that creates niche but functional combinations. It's working correctly in its axis.

---

### Seed 0099

**Tokens:** fix + full + time(scope) + simulation(method) + bug(form) + sync(channel) + persona: teach_junior_dev

**Prompt task:** The response changes the form or presentation of given content while keeping its intended meaning. Note: in bar's grammar, `fix` is a reformat task...

**Scores:**
- Task clarity: 5 — The task description now includes the R6 clarification note from cycle 4. R6 is confirmed implemented.
- Constraint independence: 3 — bug(form) structures as a bug report (Steps to Reproduce, Expected Behavior, Actual Behavior) — designed for debugging. When paired with fix(task) as reformat, the form's debugging framing conflicts with the task's reformatting nature. Additionally, bug(form) + sync(channel): bug report (static document) vs. session plan (live agenda) are incompatible output structures.
- Persona coherence: 4 — teach_junior_dev works
- Category alignment: 5
- Combination harmony: 2 — Two tensions: (1) bug(form) has strong debugging semantic context; pairing with fix-as-reformat creates confusion despite R6 clarification in the task description. (2) bug(form) + sync(channel): both define complete output structures that are incompatible (bug report vs. session plan).
- **Overall: 2**

**Notes:** Two findings: (1) R6 fix task clarification is confirmed implemented — the task description now reads as a reformat task. (2) New pattern: bug(form) is context-affine — it has strong semantic associations with debugging that create friction even when paired with reformatting tasks. (3) bug(form) + sync(channel) is a new form+channel conflict.

**Recommendations:**
- [ ] R6 confirmed: fix task description updated — close the recommendation.
- [ ] Edit: bug(form) description should note "strongest with diagnostic/debugging tasks (probe, make with diagnostic methods); may create semantic confusion with non-debugging tasks like fix (which is a reformat task)."
- [ ] Edit: add bug(form) to the prose-form conflicts list in bar help llm § Incompatibilities when paired with output-exclusive channels (sync, presenterm, etc.)

---

### Seed 0100

**Tokens:** probe + full + grove(method) + fog(directional) + persona: PM voice, kindly

**Prompt task:** The response analyzes the subject to surface structure, assumptions, or implications beyond restatement.

**Scores:**
- Task clarity: 5 — probe is clear
- Constraint independence: 5 — grove(method) examines accumulation/decay/compounding; fog(directional) abstracts from specifics to general principles; both shape HOW
- Persona coherence: 4 — PM voice for compounding-effects analysis is natural for product/growth use cases
- Category alignment: 5
- Combination harmony: 5 — probe + grove(method) + fog(directional) is exceptional: analyze accumulation and compounding effects, then abstract to general principles. This is the kind of analysis useful for technical debt, user growth, system complexity, or organizational dynamics. No conflicts.
- **Overall: 5**

**Notes:** Excellent combination. probe + grove + fog is a canonical compounding-effects analysis pattern. Highlight as positive exemplar.

---

## Score Summary

| Seed | Tokens (abbreviated) | Score |
|------|----------------------|-------|
| 0081 | sim+time+operations+wasinawa+fly bog | 4 |
| 0082 | pull+cocreate+svg | **2** — cocreate+svg conflict |
| 0083 | sort+good | 4 |
| 0084 | sim+facilitate+dip rog | 3 — sim+facilitate tension |
| 0085 | plan+quiz+presenterm | **2** — quiz+presenterm conflict |
| 0086 | diff+experimental+walkthrough+ong | 4 |
| 0087 | sort+remote+fly ong | 4 |
| 0088 | sim+stable+abduce+indirect | 4 |
| 0089 | show+full | 5 |
| 0090 | make+skim+presenterm+bog | 4 |
| 0091 | sort+adr | **2** — sort+adr task-affinity |
| 0092 | probe+fail+mod+scaffold+executive | 3 — scaffold+CEO mismatch |
| 0093 | sim+stable+facilitate+fip rog | 3 — sim+facilitate tension |
| 0094 | make+max+grow+dip bog | **5** |
| 0095 | plan+plain+Kent Beck+entertain | 4 |
| 0096 | sort+time+faq+fip rog | 4 |
| 0097 | pull+domains+tight+scientist | **5** |
| 0098 | show+act+mod | 4 |
| 0099 | fix+bug+sync | **2** — bug+sync conflict + R6 confirmed |
| 0100 | probe+grove+fog | **5** |

---

## Key Findings for Cycle 5

### Issue 1: Interactive form tokens conflict with static output channels
**Seeds:** 0082 (cocreate+svg), 0085 (quiz+presenterm), 0099 (bug+sync)
The prose-form + code-channel conflict class (documented in ADR-0105) is broader than currently documented. Three new form tokens conflict with static/code channels:
- cocreate(form) requires interactive dialogue → conflicts with svg, code, html, shellscript
- quiz(form) requires back-and-forth Q&A → conflicts with presenterm, code, svg
- bug(form) structures as a static document → conflicts with sync(channel)

### Issue 2: sim + facilitate tension (recurring)
**Seeds:** 0084, 0093 (10% of corpus)
When sim and facilitate(form) are combined, ambiguity arises about whether the LLM should perform the simulation directly or structure a facilitated simulation session. This is a genuine conceptual tension that warrants guidance.

### Issue 3: sort + adr task-affinity failure
**Seed:** 0091
sort (produces ordered/categorized list) conflicts with adr(channel) (requires decision record structure). This extends the task-affinity failure class beyond codetour and gherkin.

### Issue 4: scaffold(form) audience mismatch with executive personas
**Seed:** 0092
scaffold(form) is an educational form token; paired with CEO/executive personas it creates a form-persona semantic mismatch.

### Issue 5: bug(form) context-affinity
**Seed:** 0099
bug(form) has strong debugging semantic associations. When paired with non-debugging tasks (fix-as-reformat), it creates friction even when the task description is clear about its meaning.

### Confirmed positive patterns
- make + grow + dip bog (seed 0094): canonical incremental construction
- pull + domains + tight (seed 0097): canonical domain analysis
- probe + grove + fog (seed 0100): canonical compounding-effects analysis
- sim + stable(scope) (seeds 0088, 0093): useful stability scenario pattern
