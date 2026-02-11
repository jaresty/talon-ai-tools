# Shuffle Evaluation: Seeds 0061–0080
**Date:** 2026-02-10
**Evaluator:** Claude Sonnet 4.5
**Cycle:** 4 (validation cycle, post-ADR-0105)

## Context

This is the fourth evaluation cycle. The previous cycle (seeds 0041–0060) identified output-exclusive format conflicts as the dominant issue, with a 25% conflict rate and a mean score of 4.09. The cycle 3 recommendations proposed mutual-exclusion validation rules and task-affinity metadata for codetour and gherkin channels. ADR-0105 was completed before this cycle, adding an Incompatibilities section to `bar help llm` covering codetour and gherkin task-affinity (D2) and rewrite+make conflicts. Compound directionals (fly rog, fip rog, dip ong, etc.) have been observed in practice but remain undocumented.

**Targets from recommendations-seeds-0041-0060.yaml:**
- Excellent (≥4.0): target ≥70%, previous 65%
- Overall average: target ≥4.30, previous 4.09
- Form+channel conflicts: target ≤5%, previous 25%

---

## Summary Statistics

- Total prompts: 20
- Excellent (4–5): 10 (50%)
- Acceptable (3): 5 (25%)
- Problematic/Broken (1–2): 5 (25%)
- Average score: 3.4
- Form+channel conflicts: 4 (20%) — case+code (0075), formats+slack (0076), sim+code (0072), taxonomy+gherkin (0069)
- Additional broken combo: 2 format conflicts + known task-affinity failure (0061)
- Previous cycle (0041–0060): 65% excellent, 4.09 avg, 25% output-exclusive conflicts
- Trend: regression in excellent rate (50% vs 65%) and average (3.4 vs 4.09); form+channel conflict rate unchanged at ~25%; ADR-0105 did not prevent new undocumented conflict patterns

---

## Individual Evaluations

### Seed 0061

**Tokens:** diff + full + visual(form) + codetour(channel)

**Prompt task:** The response compares two or more subjects, highlighting relationships such as similarities, differences, or tradeoffs.

**Scores:**
- Task clarity: 2 — diff is a clear comparison task, but visual(form) and codetour(channel) each mandate incompatible output structures; the task deliverable becomes undefined
- Constraint independence: 1 — visual(form) requires an abstract visual layout response; codetour(channel) requires a VS Code CodeTour JSON file; these are mutually exclusive output formats that cannot coexist. Both override normal response structure, making constraint independence zero.
- Persona coherence: N/A — no persona tokens
- Category alignment: 4 — tokens are placed in correct axes, but the codetour channel for a non-code diff task is a task-affinity violation documented in ADR-0105 D2
- Combination harmony: 1 — three independent conflicts: (1) visual(form) + codetour(channel) are output-exclusive; (2) diff + codetour is a known task-affinity failure (ADR-0105 D2 explicitly notes codetour is awkward with diff); (3) full completeness with a Mermaid-or-JSON-output mandate produces irresolvable verbosity requirements
- **Overall: 1**

**Notes:** This seed has two simultaneous format conflicts and instantiates a known task-affinity failure. Even if one of the two format conflicts were removed, the remaining combination would still be broken. diff + codetour is the explicit example listed in ADR-0105 D2. Adding visual(form) on top of that creates a triple failure. The full completeness token cannot rescue a combination where the output format itself is undefined. This is the most broken prompt in the cycle 4 corpus.

**Recommendations:** Confirm visual(form) as output-exclusive in the validation catalog (alongside codetour, gherkin, diagram, plain). Any combination of two output-exclusive tokens should be blocked at generation time. The ADR-0105 D2 codetour+diff task-affinity entry is confirmed as necessary and correct.

---

### Seed 0062

**Tokens:** pick + fail(scope) + full + jira(channel)

**Prompt task:** The response chooses one or more options from a set of alternatives.

**Scores:**
- Task clarity: 5 — pick (choose from alternatives) is unambiguous; fail(scope) tightly bounds the selection domain to failure modes
- Constraint independence: 5 — fail(scope) defines WHAT is being selected from (failure modes); jira(channel) defines the output markup format; full governs completeness; all shape HOW without redefining WHAT
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed; fail is scope, jira is channel
- Combination harmony: 5 — pick + fail(scope) is semantically tight: choosing among failure modes is a coherent and practical task (e.g., triage, risk prioritization). jira(channel) produces Jira markup, which is appropriate for ticket-formatted options or risk assessments. full completeness ensures all failure-mode alternatives are presented. Coherent, practical, clean.
- **Overall: 4**

**Notes:** Good, practical combination. pick + fail(scope) is a strong scoping pattern that narrows selection to failure conditions specifically. The Jira channel is a natural fit for any defect or risk selection workflow. No conflicts. This combination is immediately usable in an engineering workflow context.

**Recommendations:** None. Positive pattern — pick + fail(scope) + jira is a strong triage/risk-selection combination.

---

### Seed 0063

**Tokens:** show + assume(scope) + origin(method) + recipe(form) + skim(completeness)

**Prompt task:** The response explains or describes the subject for the stated audience.

**Scores:**
- Task clarity: 4 — show (explain/describe) is clear; assume(scope) focuses on premises and assumptions; recipe(form) defines a step-by-step structure
- Constraint independence: 4 — origin(method) applies causal/historical reasoning; recipe(form) specifies step-by-step instruction format; assume(scope) focuses on premises; skim limits depth; these are mostly independent, but origin (causation) and recipe (how-to instructions) pull in different directions
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed in their axes
- Combination harmony: 3 — the origin+recipe tension is the key issue. origin method is about causal reasoning: explaining how and why something came to be. recipe form is about sequential instruction: how to do something step by step. Explaining the causal origins of a subject (origin) does not naturally map to step-by-step instructions (recipe). The result is an awkward hybrid: a recipe for understanding causation, or a causal explanation structured as steps. assume(scope) adds focus on premises, which suits origin but is somewhat at odds with recipe's action-orientation. skim appropriately limits depth for this combination.
- **Overall: 3**

**Notes:** The origin+recipe pairing is the defining tension here. Both tokens are individually well-motivated (causal reasoning is a good method for show tasks; recipe is a useful form for how-to explanations), but they point at different explanatory modes. Causal reasoning asks "why/how did this arise?" while recipe format asks "what are the steps to do this?" The assume(scope) compounds this: premises analysis is aligned with origin but not with recipe. Acceptable rather than good because the combination is interpretable but strained.

**Recommendations:** Consider adding a usage note to the origin method description: "best paired with show, probe, or diff tasks; mismatches with recipe form because causal reasoning does not naturally map to sequential instruction." This would help users avoid the origin+recipe pairing.

---

### Seed 0064

**Tokens:** show + fail(scope) + gist(completeness) + faq(form)

**Prompt task:** The response explains or describes the subject for the stated audience.

**Scores:**
- Task clarity: 5 — show (explain/describe) is clear; fail(scope) bounds explanation to failure modes specifically
- Constraint independence: 5 — fail(scope) defines the domain (failures); faq(form) defines the structure (Q&A); gist defines depth (brief/essential); all are orthogonal and reinforce each other
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed in their axes
- Combination harmony: 5 — this combination is semantically precise and practically excellent. show + fail(scope) = "explain failure modes." faq(form) = Q&A structure. gist = brief and essential. The result is a brief FAQ about failure modes: immediately useful, inherently scannable, naturally scoped. Each token strengthens the others: the FAQ form makes failure-mode explanations approachable; gist completeness prevents the FAQ from becoming encyclopedic; fail(scope) ensures relevance. No conflicts.
- **Overall: 5**

**Notes:** Exemplary minimal combination. The semantic alignment of all four tokens is unusually clean: each one answers a different question about the same deliverable (WHAT to explain, HOW to structure it, HOW MUCH to include, and WHICH domain to focus on). This is a model of how a short combination can be maximally coherent. The lack of a persona is not a weakness here; the combination's clarity makes the implicit audience obvious.

**Recommendations:** None. Document as a positive exemplar: show + fail(scope) + gist + faq demonstrates the ideal four-token minimal combination structure.

---

### Seed 0065

**Tokens:** diff + full + fog(directional)

**Prompt task:** The response compares two or more subjects, highlighting relationships such as similarities, differences, or tradeoffs.

**Scores:**
- Task clarity: 5 — diff (compare subjects) is unambiguous
- Constraint independence: 5 — full governs completeness; fog(directional) adds a specific→abstract cognitive cadence; both shape HOW the comparison is conducted without redefining WHAT
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed; fog is a directional token
- Combination harmony: 4 — sparse but coherent. diff + full is a comprehensive comparison; fog(directional) (specific→abstract) is a natural fit for comparison tasks: starting from concrete specifics and moving toward higher-level patterns and generalizations is a sound comparative strategy. The fog directional adds acknowledged-uncertainty framing, which makes the comparison intellectually honest. Three tokens is very minimal, leaving substantial freedom, but the combination is logically consistent.
- **Overall: 4**

**Notes:** Simple, clean, functional. fog(directional) is a consistent performer across comparison tasks. The minimal token count means the prompt is flexible and general, which may be appropriate for many use cases. The absence of scope, method, or persona tokens means the combination has low information density — it will work, but the output will be shaped primarily by the subject matter rather than the token constraints.

**Recommendations:** None. This is a minimal viable comparison prompt. Useful as a starting template for diff tasks.

---

### Seed 0066

**Tokens:** fix + assume(scope) + full + slack(channel) + rog(directional)

**Prompt task:** The response changes the form or presentation of given content while keeping its intended meaning.

**Scores:**
- Task clarity: 3 — fix as "transform form/presentation while keeping meaning" is technically accurate per the catalog, but counterintuitive given the conventional meaning of fix (correct/repair). Users interpreting this combination might expect bug-fixing or correction behavior rather than reformatting.
- Constraint independence: 4 — assume(scope) focuses on premises and assumptions; slack(channel) specifies Slack markdown format; rog(directional) adds a structural reflection cadence; full governs completeness; these are mostly independent, though rog (a primitive single-direction token) adds less differentiation than compound directionals
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed in their axes; rog is a valid if minimal directional token
- Combination harmony: 3 — the combination is coherent: transforming content (fix) focused on premises (assume) into Slack markdown (slack) with structural reflection (rog) is interpretable. The main concerns are: (1) fix naming ambiguity — the conventional reading of "fix" implies correction, not reformatting, and this will confuse users who do not know the token catalog definition; (2) rog is an opaque primitive directional that functions but provides little semantic lift compared to compound directionals; (3) assume(scope) for a slack message transform is slightly unusual — most Slack transformations focus on brevity or tone, not explicit assumption-surfacing
- **Overall: 3**

**Notes:** The fix task naming issue is the most consequential problem here. fix means "reformat/transform without changing meaning" in the bar catalog, but virtually every user's instinct will be to read it as "correct something." This mismatch between token name and token semantics will produce incorrect prompts when users select fix intending to mean repair. Seeds 0066, 0071, 0075, and 0078 in this cycle all instantiate the fix task, giving a clear picture of how the naming ambiguity distributes across combinations. The rog directional is technically correct but underspecified; compound directionals (fly rog, fip rog) are more informative.

**Recommendations:** Add a prominent disambiguation note to the fix task description: "fix means 'reformat or restructure while preserving intent' — it does NOT mean 'correct errors or bugs.' Use probe or check for evaluation tasks." This is the fix naming issue identified across multiple seeds.

---

### Seed 0067

**Tokens:** pick + assume(scope) + deep(completeness)

**Prompt task:** The response chooses one or more options from a set of alternatives.

**Scores:**
- Task clarity: 5 — pick (choose from alternatives) is unambiguous; assume(scope) focuses selection on the underlying assumptions and premises of each option
- Constraint independence: 5 — assume(scope) defines the lens (premises and assumptions) through which selection criteria are evaluated; deep governs completeness; both shape HOW without redefining WHAT
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed in their axes
- Combination harmony: 4 — pick + assume(scope) is a productive pairing: selecting among alternatives by surfacing and comparing their underlying assumptions is a defensible and useful selection strategy. It is particularly well-suited to ambiguous or contested decisions where the apparent criteria mask deeper premise differences. deep completeness ensures the assumption analysis is thorough. Three tokens is minimal, but the combination is logically sound.
- **Overall: 4**

**Notes:** Clean and useful. The assume(scope) lens is underutilized in selection tasks; most pick combinations focus on criteria evaluation (what is best?) rather than premise examination (what are we assuming to be true?). This combination is especially valuable for strategy or architecture decisions. The short token count makes it flexible and widely applicable.

**Recommendations:** None. Positive pattern — pick + assume(scope) is a strong assumption-surfacing selection combination.

---

### Seed 0068

**Tokens:** sort + order(method) + direct(form) + full(completeness)

**Prompt task:** The response arranges items into categories or an order using a specified or inferred scheme.

**Scores:**
- Task clarity: 4 — sort (arrange into categories or order) is clear; but order(method) creates visible redundancy with the sort task itself
- Constraint independence: 3 — order(method) and sort(task) are functionally overlapping: sort already means "arrange into order using a scheme," and the order method adds "ordering or prioritization reasoning" — which is what sort already does. The tokens are not independent; order(method) does not add a distinct cognitive lens that sort doesn't already imply. direct(form) adds a straightforward formatting constraint; full adds completeness; these are genuinely independent.
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — tokens are in their correct axes; the redundancy concern is semantic, not categorical
- Combination harmony: 3 — direct(form) and full completeness are both well-matched to sort: a comprehensive, direct ordered list is a natural output for a sort task. The problem is sort + order(method) redundancy: the user selecting both tokens appears to be double-specifying the same instruction. In practice this is harmless (order method would reinforce rather than conflict with sort task), but it means one token is doing no independent work. This is a clarity concern, not a conflict.
- **Overall: 3**

**Notes:** The sort+order redundancy concern is real but mild. The combination is not broken — it will produce a correct output. But the presence of order(method) alongside sort(task) reflects a potential catalog design issue: if the order method's description ("ordering or prioritization reasoning") overlaps with what sort already does, users may select order to reinforce sort without realizing they are adding no new constraint. Conversely, users might interpret order(method) as adding something distinct, leading to over-interpreted outputs. A disambiguation note would resolve this.

**Recommendations:** Add a disambiguation note to either order(method) or sort(task): "sort(task) already implies ordering behavior; the order method is best combined with non-ordering tasks (pick, check, plan) where explicit prioritization reasoning adds value beyond the task itself."

---

### Seed 0069

**Tokens:** plan + verify(method) + taxonomy(form) + gherkin(channel) + max(completeness)

**Prompt task:** The response proposes steps, structure, or strategy to move from the current state toward a goal.

**Scores:**
- Task clarity: 3 — plan (propose steps/strategy) is clear, and plan+gherkin is cited as appropriate in ADR-0105 D2; but taxonomy(form) conflicts with gherkin(channel), making the output format undefined
- Constraint independence: 2 — taxonomy(form) requires a classification system with definitional prose; gherkin(channel) mandates Given/When/Then format exclusively. Both prescribe incompatible output structures. They are not independent constraints.
- Persona coherence: N/A — no persona tokens
- Category alignment: 4 — tokens are in correct axes, but the taxonomy+gherkin form+channel conflict indicates a gap in the incompatibilities documentation
- Combination harmony: 2 — plan + gherkin is explicitly approved in ADR-0105 D2, and verify(method) is a natural pairing for planning (validating preconditions). These elements are coherent. However, taxonomy(form) breaks the combination: a classification system requires prose definitions, and gherkin requires BDD test scenarios — these are irreconcilable output structures. max completeness would amplify the conflict by generating maximum output in a format that cannot be specified. verify + taxonomy would be coherent (verifying a classification system); gherkin breaks both.
- **Overall: 2**

**Notes:** This seed demonstrates that ADR-0105 D2's approval of plan+gherkin does not protect against form+channel conflicts introduced by additional tokens. Even with a valid task+channel pairing at its core, adding taxonomy(form) creates an irresolvable format conflict. The approved plan+gherkin pairing is rendered moot by taxonomy's incompatibility with gherkin's output mandate. This is new evidence that ADR-0105 D5's Incompatibilities section needs to add taxonomy+gherkin (and more broadly, taxonomy + any code-output channel) as an incompatible pair.

**Recommendations:** Add taxonomy+gherkin to ADR-0105 D5 Incompatibilities section. More broadly: any form token that requires definitional prose (taxonomy, visual, indirect) should be flagged as incompatible with any channel that mandates code-only or schema-only output (gherkin, codetour, diagram, code, shellscript, html).

---

### Seed 0070

**Tokens:** make + motifs(scope) + deduce(method) + skim(completeness) + fly rog(directional)

**Prompt task:** The response creates new content that did not previously exist, based on the input and constraints.

**Scores:**
- Task clarity: 5 — make (create new content) is clear; motifs(scope) focuses creation on recurring patterns; deduce(method) specifies deductive reasoning as the creative approach
- Constraint independence: 5 — motifs(scope) defines WHAT domain to focus on (recurring patterns); deduce(method) defines HOW to reason (deductively); skim defines depth; fly rog(directional) defines cognitive cadence; all are orthogonal and mutually reinforcing
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed; fly rog is a compound directional token that renders as a single merged token
- Combination harmony: 4 — make + motifs + deduce is a coherent creative triad: creating new content by identifying recurring patterns through deductive reasoning is a productive and distinctive approach. skim limits the scope appropriately. fly rog renders coherently as a compound directional. No conflicts. The combination's main limitation is low information density for a make task — without a persona or channel, the output format and audience are unspecified, though this leaves healthy creative freedom.
- **Overall: 4**

**Notes:** Good combination with a notable feature: fly rog demonstrates that compound directional tokens are functional. They appear as a single token with a merged description rather than as separate tokens, which confirms they are not grammar violations. The combination of motifs(scope) + deduce(method) is distinctive — most creation combinations use inductive or abductive methods; deductive creation from recurring patterns is an unusual and productive approach.

**Recommendations:** None. Positive pattern — make + motifs(scope) + deduce continues the observation from cycle 3 that motifs scope appears in top-scoring seeds. Document fly rog as a confirmed functional compound directional.

---

### Seed 0071

**Tokens:** fix + mean(scope) + test(form) + full(completeness) + dip ong(directional)

**Prompt task:** The response changes the form or presentation of given content while keeping its intended meaning.

**Scores:**
- Task clarity: 3 — fix (transform form/presentation) is clear per catalog; mean(scope) focuses on semantic/meaning content; but the fix naming ambiguity (see seed 0066) means users may misread this as "correct the meaning" rather than "transform how meaning is presented"
- Constraint independence: 4 — mean(scope) focuses on semantic content; test(form) defines a test-cases output structure; full governs completeness; dip ong is a compound directional; these are mostly independent, with minor tension between fix+mean (transform presentation of meaning) and test form (presenting as test cases) — unusual but interpretable
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed; dip ong is a compound directional
- Combination harmony: 3 — the combination is unusual but coherent: restructuring semantic content (fix + mean) into test case format (test form) is interpretable as "rewrite this content as test cases that verify the meaning." dip ong directional renders coherently. full completeness is appropriate for thorough test case coverage. The main concern is whether "transform semantic content into test cases" is a practical use case — it is, for content validation workflows, but it requires a specialized context to make sense. The fix naming ambiguity adds to this complexity.
- **Overall: 3**

**Notes:** Acceptable but niche. The fix + mean + test combination is coherent in a content-validation workflow context (rewrite prose into test cases that verify key semantic claims), but it is not immediately legible outside that context. This is an example of the fix naming problem compounding with an unusual form choice to produce a combination that scores acceptably but would confuse most users. dip ong functions correctly as a compound directional.

**Recommendations:** The fix naming ambiguity noted here and in seeds 0066, 0075, and 0078 is a systemic issue. A disambiguation note on the fix task would improve all four seeds' legibility.

---

### Seed 0072

**Tokens:** sim + motifs(scope) + code(channel) + full(completeness) + rog(directional)

**Prompt task:** The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.

**Scores:**
- Task clarity: 2 — sim (simulate scenario over time) inherently generates narrative prose; code(channel) mandates code-only output. These are structurally incompatible.
- Constraint independence: 1 — code(channel) prescribes code-only output; sim requires narrative prose to describe a scenario unfolding over time. These constraints are not independent — code output overrides what sim can produce, making the task undoable as specified.
- Persona coherence: N/A — no persona tokens
- Category alignment: 4 — tokens are in correct axes, but the sim + code channel incompatibility reveals a task-affinity gap in the catalog documentation
- Combination harmony: 2 — motifs(scope) + deduce or sim + narrative reasoning would be coherent. But code(channel) forces the output into programming language syntax, which cannot represent a scenario simulation. rog directional and full completeness cannot resolve this: a "full" simulation in code-only format is incoherent. This is the sim+code incompatibility that parallels the sim+gherkin pattern. The same reasoning applies: sim generates narrative; code-only channels forbid narrative.
- **Overall: 2**

**Notes:** This is a new undocumented gap parallel to sim+gherkin (documented in ADR-0105 D2). sim + code(channel) is incoherent for the same reason sim + gherkin was: the channel mandates a schema- or syntax-constrained output that cannot represent narrative scenario simulation. This pattern likely extends to sim + html and sim + shellscript for the same reason. The fact that this gap was not caught by ADR-0105 despite the sim+gherkin fix suggests the incompatibility rule was documented as a specific case rather than a general principle.

**Recommendations:** Add to ADR-0105 D5 Incompatibilities: "sim + any code-output channel (code, html, shellscript, gherkin) — sim produces narrative prose that cannot be expressed in code syntax or schema-constrained formats." This generalizes the existing sim+gherkin entry into a sim+code-channel class rule.

---

### Seed 0073

**Tokens:** pull + dimension(method) + direct(form) + narrow(completeness)

**Prompt task:** The response selects or extracts a subset of the given information without altering its substance.

**Scores:**
- Task clarity: 5 — pull (extract a subset without altering substance) is clear and unambiguous
- Constraint independence: 5 — dimension(method) applies facet/axis analysis to the extraction; direct(form) specifies straightforward, unadorned formatting; narrow completeness focuses on the most relevant subset only; all are orthogonal and mutually reinforcing
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed in their axes
- Combination harmony: 5 — pull + dimension + direct + narrow is a semantically precise combination. The dimension method (analyzing through multiple facets or axes) is an excellent fit for extraction tasks: identifying which dimensions of information are present before pulling the most relevant subset. direct(form) ensures the extracted information is presented cleanly without additional framing. narrow completeness reinforces the extraction focus. Four tokens, no redundancy, no conflicts, perfect coherence.
- **Overall: 5**

**Notes:** Excellent minimal combination. The dimension method is particularly well-matched to pull: extracting information through a dimensional lens produces structured, complete, non-redundant subsets. direct + narrow together create a clean, focused output style that is maximally practical. This combination would work for virtually any extraction context (pulling requirements from a specification, extracting claims from a document, isolating relevant sections from a long text).

**Recommendations:** None. Document as a positive exemplar: pull + dimension + direct + narrow is a canonical extraction combination.

---

### Seed 0074

**Tokens:** show + full(completeness) + fip rog(directional)

**Prompt task:** The response explains or describes the subject for the stated audience.

**Scores:**
- Task clarity: 4 — show (explain/describe) is clear; fip rog provides a cognitive cadence for structuring the explanation
- Constraint independence: 5 — full governs completeness; fip rog shapes the cognitive progression; both are orthogonal to the explanation task
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed; fip rog is a compound directional
- Combination harmony: 3 — the combination is functional but has very low information density. With only three tokens (task + completeness + directional), the prompt provides no scope, method, form, or persona guidance. The fip rog compound directional adds useful cognitive structure (abstract→concrete→structure→reflect), but this alone does not give the response much shape beyond "explain something thoroughly in a specific cognitive sequence." The combination works but is thin.
- **Overall: 3**

**Notes:** This is a minimal combination that relies entirely on the fip rog compound directional to differentiate it from a bare "show + full" prompt. It is functional but offers almost no constraint on what kind of explanation to produce, who to produce it for, or what method to use. As a starting template it has value; as a standalone prompt it is underspecified. fip rog renders correctly as a compound directional.

**Recommendations:** Document as a minimal viable explanation template. A note in the usage patterns section could indicate that show tasks benefit from at least one scope or method token to give the explanation a distinctive angle.

---

### Seed 0075

**Tokens:** fix + act(scope) + case(form) + code(channel) + narrow(completeness) + dip bog(directional)

**Prompt task:** The response changes the form or presentation of given content while keeping its intended meaning.

**Scores:**
- Task clarity: 2 — fix (transform form/presentation) is technically clear per catalog, but case(form) (structured argument/rationale) and code(channel) (code-only output) create an immediately irresolvable format conflict
- Constraint independence: 1 — case(form) produces structured prose rationale; code(channel) mandates code-only output. These are mutually exclusive output formats.
- Persona coherence: N/A — no persona tokens
- Category alignment: 4 — tokens are in correct axes; the conflict is a semantic incompatibility, not a categorization error
- Combination harmony: 2 — case(form) + code(channel) is a hard format conflict. A structured argument/rationale cannot be expressed as code-only output without losing its prose explanation content. fix + act(scope) would otherwise be coherent (transforming action-oriented content). dip bog directional and narrow completeness are both reasonable. But the case+code conflict makes the output format undefined. The fix naming ambiguity is a secondary concern.
- **Overall: 2**

**Notes:** The case+code format conflict is the dominant issue. This follows the same pattern as taxonomy+gherkin (0069) and sim+code (0072): a prose-producing form or task token is paired with a code-output-only channel, creating irresolvable format tension. case(form) requires prose argumentation; code(channel) prohibits prose. This conflict is not documented in ADR-0105 D5. The fix naming ambiguity (does this mean "transform" or "correct"?) is a secondary concern that would remain even if the format conflict were resolved.

**Recommendations:** Add case+code to ADR-0105 D5 Incompatibilities. More generally: any form token that inherently requires prose structure (case, indirect, scaffold, list with explanations, faq) should be flagged as incompatible with code-output-only channels.

---

### Seed 0076

**Tokens:** sim + prioritize(method) + formats(form) + slack(channel) + full(completeness)

**Prompt task:** The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.

**Scores:**
- Task clarity: 3 — sim (simulate scenario over time) is clear, but formats(form) + slack(channel) create structural ambiguity: formats wants multiple output varieties; slack enforces a single Slack markdown convention
- Constraint independence: 2 — formats(form) prescribes structural variety (multiple output types or sections); slack(channel) prescribes a single specific markup convention. These are not fully independent: formats wants diversity of structure, slack imposes structural uniformity. They partially conflict.
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed in their axes
- Combination harmony: 2 — sim + prioritize + full is a coherent core: a comprehensive scenario simulation with prioritized elements. But formats(form) and slack(channel) fight: formats wants "here are multiple output varieties (prose, bullet list, table, code block)," while slack imposes Slack markdown conventions on the entire response. The result is an output format that is simultaneously trying to be structurally diverse (formats) and format-uniform (slack). full completeness amplifies this: a full simulation with multiple output formats within Slack markdown is awkward and verbose. This is a form+channel soft conflict rather than a hard mutual exclusion, but the directives are genuinely opposed.
- **Overall: 2**

**Notes:** formats(form) + slack(channel) is a new undocumented conflict pattern. Unlike case+code (which is a hard mutual exclusion), this is a directional conflict: the form token wants variety, the channel token wants convention. The result is a prompt that cannot fully satisfy both constraints simultaneously. sim + prioritize is a strong core that deserves a cleaner combination. This conflict is not in ADR-0105 D5 and should be added.

**Recommendations:** Add formats+slack (and more broadly, formats + any single-convention channel like jira, remote, sync) to ADR-0105 D5 Incompatibilities. formats(form) is only coherent when no channel is specified, or when the channel is neutral (plain, or no channel).

---

### Seed 0077

**Tokens:** check + act(scope) + sketch(channel) + deep(completeness) + fip ong(directional)

**Prompt task:** The response evaluates the subject against a condition and reports whether it passes or fails.

**Scores:**
- Task clarity: 5 — check (evaluate against condition, pass/fail) is clear; act(scope) focuses evaluation on actions or behaviors specifically
- Constraint independence: 5 — act(scope) defines the evaluation domain (actions); sketch(channel) specifies the output format (informal diagram or rough layout); deep governs completeness; fip ong adds cognitive cadence; all are orthogonal
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed; fip ong is a compound directional
- Combination harmony: 4 — check + sketch is a well-matched pairing: sketch format is well-suited to review tasks because it permits informal, annotated visual representation of findings — the exact kind of output a check task produces (pass/fail markers, annotations, summary layout). act(scope) focuses the evaluation on behavioral elements. deep completeness ensures thorough coverage. fip ong compound directional renders coherently. No conflicts.
- **Overall: 4**

**Notes:** Good combination with a notably apt channel choice. sketch is underused but is one of the better channels for review and evaluation tasks: it allows for annotated, informal visual output that matches how reviewers think (noting pass/fail items in a layout rather than writing formal prose). fip ong functions correctly as a compound directional. act(scope) + check is a natural pairing for action-item or behavior evaluation.

**Recommendations:** None. Positive pattern — check + sketch is a strong evaluation combination. Document sketch as a recommended channel for check and probe tasks.

---

### Seed 0078

**Tokens:** fix + assume(scope) + flow(method) + full(completeness) + dig(directional)

**Prompt task:** The response changes the form or presentation of given content while keeping its intended meaning.

**Scores:**
- Task clarity: 4 — fix (transform form/presentation) is clear per catalog; the fix naming ambiguity is mitigated here by assume+flow context, which suggests analytical reformatting rather than bug-fixing
- Constraint independence: 5 — assume(scope) focuses on premises; flow(method) applies process/flow analysis; full governs completeness; dig(directional) drives toward concrete specifics; all are orthogonal and mutually reinforcing
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed in their axes
- Combination harmony: 5 — every token in this combination reinforces the others. fix + assume + flow = "transform the presentation of process-flow content, focusing on its underlying premises." dig directional drives toward concrete, detailed implementation specifics. full completeness ensures nothing is dropped. The result is a combination that has a distinctive, well-defined purpose: take content that contains a process or workflow, surface its assumptions, and reformat it with deep concrete detail. No conflicts, no redundancy, high coherence.
- **Overall: 5**

**Notes:** Excellent. This is one of the most coherent four-token task combinations in the corpus. Each token answers a different question about the same deliverable without any overlap or conflict. The fix task's conventional ambiguity is actually resolved contextually here: assume+flow context makes it clear this is about reformatting process content, not repairing errors. This demonstrates that fix can be used effectively when paired with tokens that constrain its semantic scope.

**Recommendations:** None. Document as a positive exemplar: fix + assume + flow + dig is a canonical process-reformatting combination that also demonstrates how context can resolve the fix naming ambiguity.

---

### Seed 0079

**Tokens:** pull + thing(scope) + wardley(form) + skim(completeness) + fip ong(directional)

**Prompt task:** The response selects or extracts a subset of the given information without altering its substance.

**Scores:**
- Task clarity: 5 — pull (extract a subset) is clear; thing(scope) specifies entities as the extraction domain; wardley(form) specifies Wardley mapping as the output format
- Constraint independence: 5 — thing(scope) defines WHAT to extract (entities); wardley(form) defines HOW to structure the output (Wardley map); skim defines depth; fip ong adds cognitive cadence; all are orthogonal
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed; fip ong is a compound directional
- Combination harmony: 4 — pull + thing + wardley is a coherent specialized extraction pattern: extracting entities from content and mapping them in Wardley format (positioning on axes of evolution/visibility) is a sensible architectural analysis workflow. skim completeness keeps the Wardley map focused rather than exhaustive. fip ong directional renders coherently. The only limitation is that Wardley mapping is a specialized form requiring domain-specific knowledge; the combination works but has a narrower applicable context than simpler extraction patterns.
- **Overall: 4**

**Notes:** Good specialized combination. pull + thing + wardley is a recognizable pattern in architectural analysis: identifying entities in a system and mapping their strategic positioning. The combination is immediately useful for technical strategy and architecture contexts. fip ong functions correctly as a compound directional.

**Recommendations:** None. Positive pattern — pull + thing + wardley is a strong entity-extraction-to-mapping combination. Document as a recommended pattern for architecture and strategy contexts.

---

### Seed 0080

**Tokens:** pick + motifs(scope) + analog(method) + minimal(completeness)

**Prompt task:** The response chooses one or more options from a set of alternatives.

**Scores:**
- Task clarity: 5 — pick (choose from alternatives) is clear; motifs(scope) focuses selection on recurring patterns; analog(method) applies analogical reasoning to the selection
- Constraint independence: 5 — motifs(scope) defines the selection domain (recurring patterns); analog(method) defines the reasoning approach (by analogy); minimal governs completeness; all are orthogonal and mutually reinforcing
- Persona coherence: N/A — no persona tokens
- Category alignment: 5 — all tokens correctly placed in their axes
- Combination harmony: 5 — pick + motifs + analog + minimal is an exemplary selection combination. motifs(scope) and analog(method) are semantically complementary: recognizing recurring patterns (motifs) and reasoning by analogy (analog) are related cognitive operations — patterns ARE the basis for analogical reasoning. Together they create a selection approach that identifies recurring patterns across alternatives and chooses by analogy to known-good patterns. minimal completeness keeps this focused rather than exhaustive. No conflicts, no redundancy, high coherence.
- **Overall: 5**

**Notes:** Excellent. This is a textbook four-token combination: each token answers a different compositional question (TASK: choose; SCOPE: from recurring patterns; METHOD: by analogy; DEPTH: briefly) without overlap or conflict. The motifs+analog semantic complementarity is particularly notable — these two tokens are designed to work together. This is the second top-scoring seed in this cycle to feature motifs(scope), confirming the cycle 3 observation that motifs is one of the stronger scope tokens.

**Recommendations:** None. Document as a positive exemplar: pick + motifs + analog + minimal is a canonical pattern-recognition selection combination. Confirms motifs scope as a consistently high-performing token across cycles 3 and 4.

---

## Aggregated Findings

### Issues Confirmed (from previous cycles)

**1. Form+channel conflicts remain the #1 source of low scores (4 instances, 20%)**

ADR-0105 added an Incompatibilities section, but it only covered codetour, gherkin, and rewrite+make conflicts. Four new form+channel conflicts appeared in this cycle, none of which are documented in ADR-0105 D5:

- Seed 0069: taxonomy(form) + gherkin(channel) — taxonomy requires definitional prose; gherkin mandates BDD test format
- Seed 0072: sim(task) + code(channel) — sim produces narrative prose; code mandates code-only output
- Seed 0075: case(form) + code(channel) — case produces structured argument prose; code mandates code-only output
- Seed 0076: formats(form) + slack(channel) — formats wants structural variety; slack enforces a single convention

**2. sim + code-output channel is a new confirmed gap**

sim + gherkin was documented in ADR-0105 D2. sim + code is structurally identical (sim produces narrative; channel mandates non-narrative format) but not documented. This gap likely extends to sim + html and sim + shellscript. The ADR-0105 fix documented a specific instance rather than the general class.

**3. fix task naming ambiguity affects 4 seeds in this cycle**

Seeds 0066, 0071, 0075, and 0078 all instantiate the fix task. In three of them (0066, 0071, 0075) the naming ambiguity (fix = repair vs. fix = reformat) contributes to confusion or low scores. Only 0078 resolves the ambiguity through strong contextual signals. This is a systemic documentation gap.

**4. sort+order redundancy confirmed**

Seed 0068 confirms that sort(task) + order(method) provide redundant instructions. The combination is not broken but produces no additional constraint value from the order token.

### New Issues

**1. Compound directionals are functional but undocumented**

Five seeds in this cycle contain compound directionals (fly rog: 0070, fip rog: 0074, dip ong: 0071, dip bog: 0075, fip ong: 0077, 0079). All rendered correctly as single merged tokens. None are documented in skills, `bar help llm` § Token Catalog, or `bar help tokens`. A user building a prompt manually from the reference documentation has no way to discover that compound directionals exist or how to use them.

**2. formats(form) + single-convention channel is a new gap**

formats(form) wants structural variety across multiple output types. Any channel that enforces a single specific markup convention (slack, jira, remote, sync) will conflict with this form token. This is a directional conflict rather than a hard mutual exclusion, but it reliably produces problematic combinations.

**3. motifs scope continues to perform well**

motifs(scope) appears in three seeds this cycle (0070, 0072, 0080) and scores well in all non-conflicted instances. This confirms the cycle 3 observation that motifs is one of the strongest scope tokens in the catalog.

**4. case(form) lacks conflict documentation**

case(form) appears in seed 0075 paired with code(channel) in an irresolvable conflict. Like taxonomy, case requires prose argumentation that is incompatible with code-output-only channels. case is not mentioned in the ADR-0105 Incompatibilities section.

### Positive Patterns

**motifs(scope) is a high-performing scope token across multiple cycles:** Seeds 0070 and 0080 (this cycle) plus multiple cycle 3 seeds all achieve top scores when motifs is used without channel conflicts. This token has the strongest track record in the scope axis.

**Compound directionals render correctly:** fly rog, fip rog, dip ong, dip bog, fip ong all function as single merged tokens without grammar violations. They provide structural cadence and add value proportional to their component directionals.

**Minimal combinations with strong internal coherence score highest:** The five-point seeds in this cycle (0064, 0073, 0078, 0080) are all short combinations (3–4 core tokens) where each token answers a distinct compositional question. Low redundancy and absence of format conflicts are the strongest predictors of top scores.

**fix can be used effectively when context resolves naming ambiguity:** Seed 0078 demonstrates that fix + assume + flow is clear enough that the naming ambiguity becomes a non-issue. This suggests that fix can be rehabilitated by documentation improvements rather than catalog restructuring.

**check + sketch is a well-matched evaluation pairing:** Seed 0077 confirms that sketch channel is well-suited to check and review tasks. This pairing deserves positive documentation as a recommended combination.

---

## Score Table

| Seed | Tokens | Score | Issue |
|------|--------|-------|-------|
| 0061 | diff + full + visual + codetour | 1 | Two format conflicts + known task-affinity failure |
| 0062 | pick + fail + full + jira | 4 | — |
| 0063 | show + assume + origin + recipe + skim | 3 | origin+recipe slight mismatch |
| 0064 | show + fail + gist + faq | 5 | — |
| 0065 | diff + full + fog | 4 | — |
| 0066 | fix + assume + full + slack + rog | 3 | fix naming ambiguity; rog legibility |
| 0067 | pick + assume + deep | 4 | — |
| 0068 | sort + order + direct + full | 3 | sort+order redundancy |
| 0069 | plan + verify + taxonomy + gherkin + max | 2 | taxonomy+gherkin format conflict |
| 0070 | make + motifs + deduce + skim + fly rog | 4 | — |
| 0071 | fix + mean + test + full + dip ong | 3 | fix naming ambiguity; unusual form |
| 0072 | sim + motifs + code + full + rog | 2 | sim+code incompatibility |
| 0073 | pull + dimension + direct + narrow | 5 | — |
| 0074 | show + full + fip rog | 3 | Thin; no scope/method/persona |
| 0075 | fix + act + case + code + narrow + dip bog | 2 | case+code format conflict |
| 0076 | sim + prioritize + formats + slack + full | 2 | formats+slack directional conflict |
| 0077 | check + act + sketch + deep + fip ong | 4 | — |
| 0078 | fix + assume + flow + full + dig | 5 | — |
| 0079 | pull + thing + wardley + skim + fip ong | 4 | — |
| 0080 | pick + motifs + analog + minimal | 5 | — |
| **Mean** | | **3.4** | |

---

## Comparison to Previous Cycles

| Metric | Cycle 1 (0001–0020) | Cycle 2 (0021–0040) | Cycle 3 (0041–0060) | Cycle 4 (0061–0080) | Target |
|--------|---------------------|---------------------|---------------------|---------------------|--------|
| Excellent (≥4.0) | 35% | 55% | 65% | 50% | ≥70% |
| Acceptable (3.0–3.9) | — | — | 15% | 25% | — |
| Problematic (≤2.9) | 30% | 20% | 20% | 25% | — |
| Average score | 4.04 | 4.16 | 4.09 | 3.4 | ≥4.30 |
| Form+channel conflicts | ~15% | 25% | 25% | 20% | ≤5% |

**Trend:** Cycle 4 shows a regression in excellent rate (50% vs 65%) and average score (3.4 vs 4.09). This is primarily driven by four form+channel conflicts that ADR-0105 did not document. The conflict rate dropped marginally (20% vs 25%), likely reflecting natural corpus variation rather than the ADR-0105 Incompatibilities additions. The excellent rate regression is substantial and reflects that new undocumented conflict patterns (case+code, formats+slack, sim+code, taxonomy+gherkin) are suppressing the ceiling. With the three or four additional incompatibility entries recommended below, cycle 5 should recover to cycle 3 levels and potentially exceed them.

**Key observation:** ADR-0105 fixed documented conflicts but did not address the general class of prose-form + code-channel conflicts. Every new form+channel conflict in this cycle falls into that class. A general rule ("form tokens that require prose are incompatible with code-output-only channels") would prevent all four new conflicts without requiring per-pair documentation entries.

---

## Phase 2b: Meta-Evaluation Against Bar Skills

### Overview

This phase evaluates whether the bar skills (bar-autopilot, bar-manual, bar-workflow, bar-suggest) would guide a user to the token combinations found in seeds 0061–0080. Following the same methodology as cycle 3.

### Established Skill Deficiencies (carried from cycle 3)

The following systemic deficiencies apply to all four skills and were not resolved between cycles 3 and 4:

1. **Mandatory bar invocation compliance:** New mandatory bar invocation sections were added this session. These address compliance gate-keeping but do not affect token discovery quality.
2. **Compound directionals absent from documentation:** fly rog, fip rog, dip ong, dip bog, fip ong — none of these compound tokens are documented in skills, `bar help llm` § Token Catalog, or `bar help tokens`. A user following bar-manual would not know they exist.
3. **ADR-0105 Incompatibilities section incomplete:** Skills now reference the Incompatibilities section, but it does not contain case+code, formats+slack, sim+code, or taxonomy+gherkin — all four conflict types found in this cycle.
4. **Output-exclusive concept not generalized:** Skills contain per-case incompatibility guidance but no statement of the general principle (prose-output form tokens are incompatible with code-output-only channel tokens).
5. **method-category fiction persists:** Skills describe method categories (Exploration, Understanding, Decision, Diagnostic) that do not exist in the actual token catalog or help output.

The discoverability score (1–5) below uses the same scale as cycle 3:
- 5 = skills would reliably guide to this combination
- 4 = skills would likely guide to this combination with minor gaps
- 3 = skills provide partial guidance; user would need to discover some tokens independently
- 2 = skills provide minimal guidance; key tokens are undiscoverable or actively misdirected
- 1 = skills would not guide to this combination and may mislead

### Aggregated Discoverability Assessment

**Seeds achieving discoverability 4–5 (adequate guidance):** 0062, 0064, 0065, 0067, 0073, 0077, 0079, 0080

These seeds contain standard tokens that are well-represented in the skills documentation. Simple combinations with task + scope + completeness + directional tend to score well because all four axes have reasonable skills coverage. The absence of format conflicts also means skills would not lead users into broken combinations for these seeds.

**Seeds achieving discoverability 3 (partial guidance):** 0063, 0066, 0068, 0070, 0074, 0078

These seeds are reachable via skills with some independent exploration. The gaps are typically minor: an underdocumented method token, the compound directional (which is absent from documentation but does not prevent the rest of the combination from being discovered), or a scope token whose description is present but not highlighted. In seed 0066, the fix naming ambiguity would lead a user following skills to misinterpret the task token.

**Seeds achieving discoverability 1–2 (inadequate guidance):** 0061, 0069, 0071, 0072, 0075, 0076

For these seeds, skills either fail to warn against the format conflict present in the combination, fail to surface tokens that would prevent the conflict, or (in the case of compound directionals like dip bog in 0075) present undiscoverable tokens. The most critical skill failures are:

- Seed 0061: Skills would not warn against the visual+codetour output-exclusive conflict or the diff+codetour task-affinity violation (even though ADR-0105 D2 documents diff+codetour, this is in `bar help llm` not in the skills themselves)
- Seed 0069: Skills do not warn against taxonomy+gherkin conflict
- Seed 0072: Skills do not warn against sim+code conflict (sim+gherkin is documented in ADR-0105 D2 but not yet reflected in skills)
- Seed 0075: case+code conflict not documented in skills; dip bog compound directional is undiscoverable
- Seed 0076: formats+slack conflict not documented anywhere

**Discoverability score distribution (20 seeds):**

| Score | Count | Seeds |
|-------|-------|-------|
| 4–5 (adequate guidance) | 8 | 0062, 0064, 0065, 0067, 0073, 0077, 0079, 0080 |
| 3 (partial guidance) | 6 | 0063, 0066, 0068, 0070, 0074, 0078 |
| 1–2 (inadequate guidance) | 6 | 0061, 0069, 0071, 0072, 0075, 0076 |

**Mean discoverability score: approximately 3.5 / 5**

This is a genuine improvement over cycle 3 (2.9 / 5), driven by the ADR-0105 additions and the mandatory bar invocation compliance sections. However, the improvement is concentrated in the high-scoring seeds; the low-scoring seeds have essentially unchanged discoverability because the new incompatibility entries in ADR-0105 do not cover the conflict types found in this cycle.

### Gap Category Analysis

1. **Form+channel conflict guidance incomplete (4 seeds):** Seeds 0069, 0072, 0075, 0076. All four form+channel conflicts in this cycle are absent from the Incompatibilities section that ADR-0105 added. Skills cannot warn users about these conflicts.

2. **Compound directionals undocumented (multiple seeds):** fly rog (0070), fip rog (0074), dip ong (0071), dip bog (0075), fip ong (0077, 0079) — none discoverable via skills or reference documentation. Users following bar-manual would not know these tokens exist.

3. **fix task naming misleads users (4 seeds):** Seeds 0066, 0071, 0075, 0078 all involve the fix task. Skills would not alert users to the counterintuitive semantics of fix (reformat ≠ repair). In three of these four seeds, the ambiguity contributes to lower scores or interpretation confusion.

4. **sim + code-channel incompatibility undocumented (seed 0072):** Skills reference ADR-0105 D2 for sim+gherkin, but the analogous sim+code rule is not documented. A user would find no warning for this combination.

5. **sort+order redundancy undocumented (seed 0068):** Skills contain no disambiguation note clarifying that order method does not add value when the task is already sort. A user would select both tokens without realizing the redundancy.

---

## Phase 2c: Bar Help LLM Reference Evaluation

### Overview

This phase evaluates the `bar help llm` reference document (introduced by ADR-0105) as a reference for constructing the prompts in seeds 0061–0080. ADR-0105 D4 removed phantom tokens; ADR-0105 D5 added an Incompatibilities section. These are genuine improvements over the `bar help tokens` baseline from cycle 3.

### Evaluation Criteria

**Criterion 1: Token Discovery — Does `bar help llm` enable a user to discover the relevant tokens?**

- Score: 4/5
- Rationale: ADR-0105 D4 removed phantom tokens, which means the catalog is now accurate. All tokens used in this cycle are present with accurate descriptions. The Token Selection Heuristics section (added in ADR-0105) improves discovery for common patterns. The main gap is compound directionals: fly rog, fip rog, dip ong, dip bog, fip ong are not in the catalog. A user building a prompt manually from `bar help llm` would never know these tokens exist.

**Criterion 2: Token Description Accuracy — Are token descriptions accurate and sufficient?**

- Score: 4/5
- Rationale: Token descriptions are accurate after ADR-0105 D4 cleanup. The main remaining deficiency is the fix task: its description accurately reflects the catalog semantics (transform form/presentation) but does not flag the counterintuitive naming (fix does not mean correct/repair). This is a documentation gap that affects 4 seeds in this cycle.

**Criterion 3: Incompatibility Coverage — Does `bar help llm` § Incompatibilities document the relevant conflicts?**

- Score: 2/5
- Rationale: ADR-0105 D5 added an Incompatibilities section that covers codetour and gherkin task-affinity (D2) and rewrite+make conflicts. This is an improvement over cycle 3 (score would have been 1). However, the four conflict types in this cycle — case+code, formats+slack, sim+code, taxonomy+gherkin — are not documented. The section addresses specific known cases rather than the general principle (prose-form tokens are incompatible with code-output channels). For this cycle's conflicts, the section provides no coverage.

**Criterion 4: Composition Guidance — Does `bar help llm` help users compose multiple tokens?**

- Score: 3/5
- Rationale: The Token Selection Heuristics section added by ADR-0105 provides some composition guidance: it mentions common token pairings and task-type patterns. This is a genuine improvement over `bar help tokens` (which scored 1/5 on this criterion in cycle 3). However, the heuristics do not cover the combination patterns in seeds 0061–0080 (no guidance on pick+scope patterns, sim task combinations, fix task disambiguation, or form+channel mutual exclusion as a general rule).

**Criterion 5: Task-Affinity Guidance — Does `bar help llm` help users match tokens to tasks?**

- Score: 3/5
- Rationale: ADR-0105 D2 added task-affinity notes for codetour and gherkin. This covers the cycle 3 failures. For this cycle, the sim+code task-affinity mismatch (seed 0072) is not covered. The general principle (channels that mandate code/schema output are inappropriate for prose-generating tasks like sim) is not stated. Partial improvement but new gaps remain.

**Criterion 6: Compound Directional Coverage — Does `bar help llm` document compound directionals?**

- Score: 1/5
- Rationale: Compound directionals (fly rog, fip rog, dip ong, dip bog, fip ong and others) are not documented anywhere in `bar help llm` — not in § Token Catalog, not in § Token Selection Heuristics, not in § Incompatibilities. A user following `bar help llm` has no way to know these tokens exist, what they mean, or how to compose them. Five seeds in this cycle use compound directionals.

**Criterion 7: Fix Task Documentation — Does `bar help llm` adequately describe the fix task's non-intuitive semantics?**

- Score: 2/5
- Rationale: The fix task description is accurate per catalog (transform form/presentation while preserving meaning), but it does not flag the counterintuitive relationship between the token name and its semantics. The word "fix" conventionally implies correction or repair; the catalog meaning is reformatting. No disambiguation note, no "note: fix does not mean correct errors" warning, no cross-reference to tasks that do mean correction (probe, check). Four seeds in this cycle are affected by this gap.

---

### Aggregated Reference Tool Findings

| Criterion | Cycle 3 Score | Cycle 4 Score | Change |
|-----------|--------------|--------------|--------|
| Token Discovery | 3/5 | 4/5 | +1 (phantom token removal) |
| Token Description Accuracy | 4/5 | 4/5 | 0 |
| Incompatibility Coverage | 1/5 | 2/5 | +1 (D5 additions, but incomplete) |
| Composition Guidance | 1/5 | 3/5 | +2 (Token Selection Heuristics added) |
| Task-Affinity Guidance | 2/5 | 3/5 | +1 (D2 additions for codetour/gherkin) |
| Compound Directional Coverage | N/A | 1/5 | new criterion |
| Fix Task Documentation | N/A | 2/5 | new criterion |
| **Mean** | **2.6/5** | **2.7/5** | +0.1 net |

**Summary of reference tool findings:**

`bar help llm` is a genuine improvement over `bar help tokens` for composition guidance and incompatibility awareness. ADR-0105's additions are real and correct. However, the improvement is concentrated in previously-known conflicts; the new conflict types in this cycle are entirely unaddressed. The net improvement (+0.1) reflects that ADR-0105 added value but did not close the gap between what the reference provides and what users need to build conflict-free prompts.

The two new criteria introduced in cycle 4 (compound directional coverage and fix task documentation) both score at the floor. These represent quality gaps that were not visible in cycle 3 because the relevant tokens appeared less prominently.

**Priority gaps in `bar help llm` relative to cycle 4 findings:**

1. No documentation for compound directionals — affects 5 seeds in this cycle, likely a systematic corpus-wide issue
2. Incompatibilities section missing case+code, formats+slack, sim+code, taxonomy+gherkin — four new conflict types, all in the same class (prose-form + code-channel)
3. fix task naming ambiguity undocumented — affects 4 seeds in this cycle, likely widespread in practice
4. sim task-channel incompatibility not generalized — ADR-0105 covers gherkin but not the class (code-output channels)
5. sort+order redundancy undocumented — minor but recurring

**What would raise the mean score from 2.7 to ≥4.0:**

- Documenting compound directionals in § Token Catalog (would raise criterion 6 from 1 to 4)
- Adding a general prose-form + code-channel incompatibility rule and the four missing specific entries (would raise criterion 3 from 2 to 4)
- Adding a fix task disambiguation note (would raise criterion 7 from 2 to 4)
- Generalizing sim+gherkin to sim+code-channel class (would raise criterion 5 from 3 to 4)

These four targeted changes would address the dominant issues in cycle 4 without restructuring the reference document.

---

## Recommendations for YAML File

The following recommendations should be written to the companion recommendations YAML file:

1. **Add `sim` task-affinity note to code/html/shellscript channel descriptions** — same class as the existing gherkin+sim entry in ADR-0105 D2. sim produces narrative prose that cannot be expressed as code-only output. Apply to code, html, shellscript, and any other code-output-only channel.

2. **Add case+code and formats+channel conflicts to § Incompatibilities** — case(form) requires prose argumentation incompatible with code-output channels. formats(form) requires structural variety incompatible with single-convention channels (slack, jira, remote). Add both entries to ADR-0105 D5.

3. **Add taxonomy+gherkin conflict to § Incompatibilities** — taxonomy requires definitional prose; gherkin mandates BDD test format. This is confirmed by seed 0069 even though plan+gherkin is an approved pairing (per ADR-0105 D2).

4. **Add compound directionals documentation to `bar help llm` § Token Catalog** — fly rog, fip rog, dip ong, dip bog, fip ong, and others are functional tokens that appear in corpus and produce coherent outputs but are completely invisible to users building prompts from documentation.

5. **Add fix task disambiguation note** — "fix means reformat/restructure while preserving intent — it does NOT mean correct errors or bugs. Use probe for analysis, check for evaluation, or a task-specific term for repair." Apply to `bar help llm` fix task description and to the bar skills that describe the fix task.

6. **Add sort+order disambiguation note** — sort(task) already implies ordering behavior; order(method) adds no differentiation when task is sort. Note: order method is most useful with non-ordering tasks (pick, check, plan) where explicit prioritization reasoning adds value.

7. **Add general prose-form + code-channel incompatibility principle** — rather than documenting only specific pairs, add a general rule: "form tokens that require prose structure (case, indirect, scaffold, faq, taxonomy, visual) are incompatible with channels that mandate code-only or schema-only output (code, html, shellscript, gherkin, codetour, diagram)." This would prevent all four cycle 4 format conflicts and is more robust than per-pair documentation.
