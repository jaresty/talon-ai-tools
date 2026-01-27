# ADR 0085: Shuffled Prompt Corpus Evaluation

**Evaluation Date**: 2026-01-26
**Corpus Size**: 20 prompts
**Evaluator**: Claude Sonnet 4.5

## Evaluation Rubric

Each prompt is scored 1-5 on five criteria:

- **Task clarity** (TC): Does the static prompt clearly define what success looks like?
- **Constraint independence** (CI): Do constraints shape HOW without redefining WHAT?
- **Persona coherence** (PC): Does the persona stance make sense for this task?
- **Category alignment** (CA): Is each token doing the job of its stated category?
- **Combination harmony** (CH): Do the selected tokens work together or fight?

**Scoring**: 5=Excellent, 4=Good, 3=Acceptable, 2=Problematic, 1=Broken

---

## Seed 0001

**Tokens selected:**
- static: probe
- completeness: minimal
- scope: struct
- form: gherkin
- channel: presenterm
- directional: fig
- persona: to Kent Beck

**Generated prompt preview:**
> The response decomposes, reasons about, or interprets the subject to reveal structure or insight beyond restatement. [minimal, struct, gherkin in presenterm, fig reversal]

**Scores:**
- Task clarity: **5** - "probe" clearly defines analytical task
- Constraint independence: **2** - gherkin (form) and presenterm (channel) conflict heavily
- Persona coherence: **4** - Kent Beck audience makes sense for structural analysis
- Category alignment: **3** - gherkin is a testing DSL, not suited for presenterm slides
- Combination harmony: **1** - gherkin + presenterm is contradictory (Gherkin-only vs slide deck)

**Overall**: **2/5** - Broken combination

**Notes:**
The fundamental conflict is form=gherkin ("outputs only Gherkin") vs channel=presenterm ("valid multi-slide deck"). These are mutually exclusive outputs. The "minimal" constraint fights the "full deck" expectation of presenterm. The "fig" directional (abstract/concrete alternation) might work with slides but not with pure Gherkin.

**Recommendations:**
- [ ] **Recategorize**: gherkin should not combine with presenterm/diagram/sync channels
- [ ] **Edit**: gherkin description should clarify incompatibility with structured channels

---

## Seed 0002

**Tokens selected:**
- static: diff
- completeness: skim
- scope: (none)
- method: inversion
- form: spike
- channel: (none)
- directional: (none)
- persona: fun_mode + casually

**Generated prompt preview:**
> The response analyzes similarities, differences, or tradeoffs along relevant dimensions with accurate relational claims. [skim, inversion, spike format]

**Scores:**
- Task clarity: **5** - "diff" is clear
- Constraint independence: **3** - inversion (method) is heavy for a light "skim"
- Persona coherence: **4** - fun_mode works for exploratory diff analysis
- Category alignment: **4** - spike (form) fits research framing
- Combination harmony: **3** - inversion + skim creates tension (deep thinking vs light pass)

**Overall**: **4/5** - Good with minor tension

**Notes:**
"Inversion" (thinking backward from catastrophic outcomes) feels unnecessarily heavy for a "skim" pass. The spike format (research questions) is appropriate for diff analysis. Fun mode adds lightness that helps balance the heavy method.

**Recommendations:**
- [ ] **Note**: skim + inversion combination may produce superficial catastrophic thinking

---

## Seed 0003

**Tokens selected:**
- static: pick
- completeness: gist
- scope: fail
- method: simulation
- channel: diagram
- directional: fly ong
- persona: (none)

**Generated prompt preview:**
> The response selects among alternatives using stated or implied criteria with clear decision and reasoned justification. [gist, fail scope, simulation, diagram only]

**Scores:**
- Task clarity: **5** - "pick" is crystal clear
- Constraint independence: **2** - diagram (channel) severely constrains a decision task
- Persona coherence: **N/A** - no persona
- Category alignment: **2** - diagram as channel limits decision articulation
- Combination harmony: **2** - simulation + diagram is awkward (narrative thought experiments in Mermaid?)

**Overall**: **2/5** - Problematic

**Notes:**
The "diagram" channel ("Mermaid code only") contradicts the task of making a justified decision with "reasoned justification". Simulation method (scenario walkthroughs with feedback loops) is hard to express in pure Mermaid. "Fly ong" (abstract to concrete to related) doesn't map well to diagram-only output.

**Recommendations:**
- [ ] **Recategorize**: diagram channel should be incompatible with tasks requiring prose justification (pick, probe, plan)
- [ ] **Edit**: simulation method description should note limits for diagram-only output

---

## Seed 0004

**Tokens selected:**
- static: plan
- completeness: full
- scope: act
- method: (none)
- form: (none)
- channel: (none)
- directional: (none)
- persona: product_manager_to_team

**Generated prompt preview:**
> The response produces an actionable sequence, structure, or strategy with feasible steps in logical order. [full, act scope, as PM to team kindly]

**Scores:**
- Task clarity: **5** - "plan" is clear
- Constraint independence: **5** - act (scope) reinforces without redefining
- Persona coherence: **5** - PM to team is perfect for planning
- Category alignment: **5** - all tokens well-aligned
- Combination harmony: **5** - everything works together

**Overall**: **5/5** - Excellent

**Notes:**
This is a clean, coherent prompt. The scope (act) naturally fits planning. The persona preset adds appropriate framing. The completeness (full) matches the thoroughness expected of a plan. No conflicts.

**Recommendations:**
- None - exemplar combination

---

## Seed 0005

**Tokens selected:**
- static: fix
- completeness: full
- scope: fail
- method: grove
- channel: presenterm
- directional: fip rog
- persona: directly

**Generated prompt preview:**
> The response changes the representation or form while preserving underlying meaning and semantic equivalence. [full, fail scope, grove accumulation, presenterm deck, fip rog]

**Scores:**
- Task clarity: **4** - "fix" (transformation) is clear but abstract
- Constraint independence: **3** - fail (scope: breakdowns/risks) partially redefines fix's purpose
- Persona coherence: **4** - "directly" tone works
- Category alignment: **3** - grove (accumulation/decay) is odd for transformation task
- Combination harmony: **3** - fail + fix + grove is conceptually confused

**Overall**: **3/5** - Acceptable but strained

**Notes:**
"Fix" is about transformation/translation, but "fail" scope (risks, edge cases) pushes toward error analysis. "Grove" (accumulation effects over time) doesn't naturally fit semantic equivalence preservation. The presenterm channel adds structure but doesn't resolve the conceptual tension.

**Recommendations:**
- [ ] **Edit**: fix description should clarify relationship to error/failure scenarios
- [ ] **Note**: grove method may not fit transformation tasks

---

## Seed 0006

**Tokens selected:**
- static: show
- completeness: narrow
- scope: (none)
- method: (none)
- form: log
- channel: (none)
- directional: dip ong
- persona: peer_engineer_explanation

**Generated prompt preview:**
> The response makes the subject intelligible to the target audience with internal coherence and appropriate abstraction. [narrow, log format, dip ong]

**Scores:**
- Task clarity: **5** - "show" (explain) is clear
- Constraint independence: **5** - all constraints shape delivery appropriately
- Persona coherence: **5** - peer engineer fits explanatory task
- Category alignment: **5** - log (form) and narrow (completeness) work well
- Combination harmony: **5** - coherent combination

**Overall**: **5/5** - Excellent

**Notes:**
Clean, well-aligned prompt. The narrow completeness + log format creates focused documentation. The directional (concrete to action to extension) fits pedagogical explanation. Persona reinforces technical precision.

**Recommendations:**
- None - exemplar combination

---

## Seed 0007

**Tokens selected:**
- static: sort
- completeness: gist
- scope: act
- method: converge
- form: adr
- channel: (none)
- directional: (none)
- persona: formally + coach

**Generated prompt preview:**
> The response assigns items to predefined or inferred categories with consistent application of category definitions. [gist, act scope, converge, adr format]

**Scores:**
- Task clarity: **5** - "sort" is clear
- Constraint independence: **4** - converge (method) is almost a different task (decide)
- Persona coherence: **4** - coach intent + formal tone works for structured categorization
- Category alignment: **3** - adr (form) expects decision rationale, not categorization
- Combination harmony: **3** - sort + converge + adr creates genre confusion

**Overall**: **4/5** - Good but slightly misaligned

**Notes:**
"Sort" is about categorization, but "converge" (narrow to recommendations/decision) and "adr" (decision record) push toward decision-making. The form (ADR) expects context/decision/consequences, which doesn't naturally fit pure categorization. The coach intent helps but doesn't resolve the genre mismatch.

**Recommendations:**
- [ ] **Edit**: adr form should clarify fit for sort vs pick/plan tasks
- [ ] **Note**: converge method overlaps with pick task

---

## Seed 0008

**Tokens selected:**
- static: diff
- completeness: full
- scope: act
- method: roles
- form: scaffold
- channel: (none)
- directional: bog
- persona: product_manager_to_team

**Generated prompt preview:**
> The response analyzes similarities, differences, or tradeoffs along relevant dimensions with accurate relational claims. [full, act scope, roles, scaffolding, bog]

**Scores:**
- Task clarity: **5** - "diff" is clear
- Constraint independence: **5** - all constraints shape HOW appropriately
- Persona coherence: **5** - PM to team fits collaborative analysis
- Category alignment: **5** - roles method fits organizational diff analysis
- Combination harmony: **5** - all elements reinforce

**Overall**: **5/5** - Excellent

**Notes:**
Strong combination. The "roles" method (responsibilities/ownership) adds dimension to diff analysis. Scaffold form (gradual explanation from first principles) fits teaching tradeoffs. The "bog" directional (structure to reflection to action) creates a complete analytical arc. Act scope focuses on operational differences.

**Recommendations:**
- None - exemplar combination

---

## Seed 0009

**Tokens selected:**
- static: show
- completeness: full
- scope: fail
- method: (none)
- form: (none)
- channel: (none)
- directional: (none)
- persona: designer_to_pm

**Generated prompt preview:**
> The response makes the subject intelligible to the target audience with internal coherence and appropriate abstraction. [full, fail scope]

**Scores:**
- Task clarity: **5** - "show" is clear
- Constraint independence: **5** - fail (scope: risks/limits) shapes focus appropriately
- Persona coherence: **5** - designer to PM fits risk communication
- Category alignment: **5** - clean alignment
- Combination harmony: **5** - well-balanced

**Overall**: **5/5** - Excellent

**Notes:**
Simple but effective. The fail scope (breakdowns, edge cases) gives "show" a specific lens. Designer to PM persona naturally emphasizes usability risks and friction points. Direct tone keeps it actionable.

**Recommendations:**
- None - exemplar combination

---

## Seed 0010

**Tokens selected:**
- static: sort
- completeness: skim
- scope: thing
- method: (none)
- form: (none)
- channel: (none)
- directional: (none)
- persona: as designer + casually + entertain

**Generated prompt preview:**
> The response assigns items to predefined or inferred categories with consistent application of category definitions. [skim, thing scope]

**Scores:**
- Task clarity: **5** - "sort" is clear
- Constraint independence: **5** - thing (scope: objects/entities) fits categorization
- Persona coherence: **3** - "entertain" intent conflicts with categorization rigor
- Category alignment: **5** - clean token alignment
- Combination harmony: **3** - entertain + sort creates tonal confusion

**Overall**: **4/5** - Good with persona tension

**Notes:**
The task and constraints are clean. However, "entertain" (intent: engage or amuse) sits awkwardly with the precision required for consistent categorization. The casual tone helps lighten it, but the fundamental intent mismatch remains.

**Recommendations:**
- [ ] **Note**: entertain intent may undermine tasks requiring precision (sort, check, pull)

---

## Seed 0011

**Tokens selected:**
- static: show
- completeness: full
- scope: (none)
- method: dynamics
- form: (none)
- channel: diagram
- directional: dig
- persona: teach_junior_dev

**Generated prompt preview:**
> The response makes the subject intelligible to the target audience with internal coherence and appropriate abstraction. [full, dynamics, diagram only, dig]

**Scores:**
- Task clarity: **5** - "show" is clear
- Constraint independence: **4** - diagram limits explanation flexibility
- Persona coherence: **5** - teaching junior dev fits well
- Category alignment: **4** - dynamics + diagram works but is limiting
- Combination harmony: **4** - mostly coherent, channel constrains

**Overall**: **4/5** - Good

**Notes:**
The combination mostly works. "Dynamics" (system evolution/feedback) maps well to state diagrams or sequence diagrams. The "dig" directional (focus on concrete details) fits diagram concreteness. However, teaching complex dynamics purely through diagrams (no prose explanation) is challenging.

**Recommendations:**
- [ ] **Note**: diagram channel limits pedagogical explanations

---

## Seed 0012

**Tokens selected:**
- static: show
- completeness: full
- scope: struct
- method: (none)
- form: (none)
- channel: (none)
- directional: dip rog
- persona: as principal engineer + to XP enthusiast + announce

**Generated prompt preview:**
> The response makes the subject intelligible to the target audience with internal coherence and appropriate abstraction. [full, struct scope, dip rog]

**Scores:**
- Task clarity: **5** - "show" is clear
- Constraint independence: **5** - struct (scope: patterns/dependencies) shapes focus well
- Persona coherence: **3** - "announce" intent conflicts with "show" (explain)
- Category alignment: **5** - clean alignment
- Combination harmony: **3** - announce + show creates purpose confusion

**Overall**: **4/5** - Good with persona tension

**Notes:**
Strong task and constraints. The struct scope + dip rog directional creates good structural explanation. However, "announce" intent (share news/updates) conflicts with "show" (make intelligible). Is this an explanation or an announcement? The principal engineer voice helps but doesn't resolve the intent mismatch.

**Recommendations:**
- [ ] **Edit**: announce intent description should clarify fit with different static prompts
- [ ] **Note**: announce may conflict with analytical tasks (show, probe, diff)

---

## Seed 0013

**Tokens selected:**
- static: sort
- completeness: full
- scope: (none)
- method: (none)
- form: plain
- channel: diagram
- directional: (none)
- persona: executive_brief

**Generated prompt preview:**
> The response assigns items to predefined or inferred categories with consistent application of category definitions. [full, plain prose, diagram only]

**Scores:**
- Task clarity: **5** - "sort" is clear
- Constraint independence: **1** - plain (form) and diagram (channel) are contradictory
- Persona coherence: **4** - executive brief could work for categorization
- Category alignment: **2** - form and channel conflict
- Combination harmony: **1** - plain prose vs diagram-only is broken

**Overall**: **2/5** - Broken combination

**Notes:**
Fundamental conflict: form=plain ("plain prose with natural paragraphs") vs channel=diagram ("Mermaid diagram code only"). These are mutually exclusive. The executive brief persona can't resolve this structural impossibility.

**Recommendations:**
- [ ] **Retire or recategorize**: plain form should be incompatible with diagram/presenterm/gherkin channels

---

## Seed 0014

**Tokens selected:**
- static: pull
- completeness: full
- scope: struct
- method: objectivity
- form: cocreate
- channel: (none)
- directional: fip rog
- persona: as scientist + to junior engineer + formally

**Generated prompt preview:**
> The response selects or isolates information already present without introducing new content. [full, struct scope, objectivity, cocreate, fip rog]

**Scores:**
- Task clarity: **4** - "pull" (extract) is clear but passive
- Constraint independence: **5** - constraints shape delivery well
- Persona coherence: **3** - cocreate conflicts with formal scientist persona
- Category alignment: **4** - good alignment except persona/form tension
- Combination harmony: **3** - formal scientist vs collaborative iteration creates friction

**Overall**: **4/5** - Good with persona/form tension

**Notes:**
The task and constraints work well. Objectivity (evidence-based) fits extraction. However, "cocreate" (iterative collaboration) conflicts with "formally" (professional tone) and "as scientist" (rigorous authority). Scientists typically deliver findings, not co-create through iteration.

**Recommendations:**
- [ ] **Edit**: cocreate description should clarify persona compatibility
- [ ] **Note**: formal tone may conflict with collaborative forms (cocreate, socratic)

---

## Seed 0015

**Tokens selected:**
- static: probe
- completeness: full
- scope: struct
- method: effects
- channel: (none)
- directional: (none)
- persona: product_manager_to_team

**Generated prompt preview:**
> The response decomposes, reasons about, or interprets the subject to reveal structure or insight beyond restatement. [full, struct scope, effects method]

**Scores:**
- Task clarity: **5** - "probe" is clear
- Constraint independence: **5** - all constraints shape HOW appropriately
- Persona coherence: **5** - PM to team fits systems analysis
- Category alignment: **5** - effects (downstream consequences) fits structural analysis
- Combination harmony: **5** - everything reinforces

**Overall**: **5/5** - Excellent

**Notes:**
Exemplary combination. "Probe" (analytical interpretation) + struct (dependencies/patterns) + effects (downstream consequences) creates coherent systems thinking. PM persona fits the strategic implications focus.

**Recommendations:**
- None - exemplar combination

---

## Seed 0016

**Tokens selected:**
- static: chat
- completeness: minimal
- scope: (none)
- method: (none)
- form: (none)
- channel: jira
- directional: dip ong
- persona: to CEO + casually

**Generated prompt preview:**
> The response maintains a coherent, context-aware exchange by responding meaningfully to prior turns and advancing or sustaining the interaction. [minimal, jira markup, dip ong]

**Scores:**
- Task clarity: **4** - "chat" (conversational exchange) is clear
- Constraint independence: **4** - constraints mostly work
- Persona coherence: **2** - casually to CEO is problematic
- Category alignment: **4** - jira channel is odd but not broken
- Combination harmony: **3** - casual tone to CEO creates inappropriate register

**Overall**: **3/5** - Acceptable with persona issue

**Notes:**
The task and constraints are workable. However, "casually" (casual tone) + "to CEO" (business impact/risk focus) creates inappropriate communication register. CEOs typically expect crisp, professional updates, not casual chat. The jira channel (markup for tickets) is odd for chat but not impossible.

**Recommendations:**
- [ ] **Edit**: to CEO audience should suggest formal/direct tone, not casual
- [ ] **Note**: chat task with channel constraints (jira/slack) may feel forced

---

## Seed 0017

**Tokens selected:**
- static: probe
- completeness: full
- scope: (none)
- method: (none)
- form: (none)
- channel: sync
- directional: (none)
- persona: as teacher + casually + inform

**Generated prompt preview:**
> The response decomposes, reasons about, or interprets the subject to reveal structure or insight beyond restatement. [full, sync session plan]

**Scores:**
- Task clarity: **5** - "probe" is clear
- Constraint independence: **4** - sync (channel: live session plan) partially reframes task
- Persona coherence: **5** - teacher + inform fits well
- Category alignment: **4** - sync is more structural than pure channel
- Combination harmony: **4** - mostly coherent

**Overall**: **4/5** - Good

**Notes:**
The combination works. "Sync" (agenda/session plan format) transforms analytical probe into facilitation structure. The teacher persona + inform intent aligns with guided exploration. The casual tone makes it approachable.

**Recommendations:**
- [ ] **Note**: sync channel transforms tasks into facilitation format

---

## Seed 0018

**Tokens selected:**
- static: check
- completeness: skim
- scope: (none)
- method: (none)
- form: gherkin
- channel: slack
- directional: (none)
- persona: product_manager_to_team

**Generated prompt preview:**
> The response checks truth, consistency, or compliance with accurate judgment and clear pass/fail statement. [skim, gherkin only, slack formatting]

**Scores:**
- Task clarity: **5** - "check" is clear
- Constraint independence: **2** - gherkin (form) and slack (channel) create friction
- Persona coherence: **5** - PM to team fits quality checks
- Category alignment: **2** - gherkin ("outputs only Gherkin") conflicts with "Slack formatting"
- Combination harmony: **2** - gherkin-only vs Slack markdown is contradictory

**Overall**: **3/5** - Acceptable but strained

**Notes:**
"Check" task is clear. However, gherkin ("outputs only Gherkin, omitting surrounding explanation") conflicts with slack ("formats for Slack using appropriate Markdown, mentions, code blocks"). Gherkin is typically in code blocks, so maybe this means Gherkin in Slack-formatted code blocks? The ambiguity is problematic.

**Recommendations:**
- [ ] **Recategorize**: gherkin should clarify compatibility with communication channels (slack/jira)

---

## Seed 0019

**Tokens selected:**
- static: fix
- completeness: deep
- scope: (none)
- method: dimension
- form: socratic
- channel: (none)
- directional: (none)
- persona: casually

**Generated prompt preview:**
> The response changes the representation or form while preserving underlying meaning and semantic equivalence. [deep, dimension expansion, socratic questions]

**Scores:**
- Task clarity: **4** - "fix" (transformation) is clear
- Constraint independence: **3** - dimension (method) and socratic (form) partially redefine task
- Persona coherence: **4** - casual works for socratic dialogue
- Category alignment: **3** - dimension + socratic push toward exploration, not transformation
- Combination harmony: **3** - fix + socratic creates task confusion

**Overall**: **3/5** - Acceptable but conceptually strained

**Notes:**
"Fix" is about transformation/translation, but "socratic" (question-led, withholding conclusions) conflicts with delivering a transformed output. "Dimension" (expanding conceptual axes) also pushes toward exploration rather than equivalence-preserving transformation. The deep completeness adds thoroughness but doesn't resolve the conceptual tension.

**Recommendations:**
- [ ] **Edit**: socratic form should clarify incompatibility with delivery-focused tasks (fix, plan)
- [ ] **Note**: dimension method overlaps with probe task

---

## Seed 0020

**Tokens selected:**
- static: chat
- completeness: full
- scope: (none)
- method: order
- form: bullets
- channel: (none)
- directional: (none)
- persona: designer_to_pm

**Generated prompt preview:**
> The response maintains a coherent, context-aware exchange by responding meaningfully to prior turns and advancing or sustaining the interaction. [full, order reasoning, bullets only]

**Scores:**
- Task clarity: **5** - "chat" is clear
- Constraint independence: **5** - constraints shape delivery well
- Persona coherence: **5** - designer to PM fits conversational exchange
- Category alignment: **5** - order (structural reasoning) + bullets works
- Combination harmony: **5** - coherent

**Overall**: **5/5** - Excellent

**Notes:**
Clean, effective combination. The "order" method (hierarchy, dominance) adds analytical depth to chat. Bullets format keeps responses crisp. Designer to PM persona creates appropriate professional register. Direct tone maintains clarity.

**Recommendations:**
- None - exemplar combination

---

## Summary Statistics

**Overall Score Distribution:**
- 5/5 (Excellent): 7 prompts (35%)
- 4/5 (Good): 7 prompts (35%)
- 3/5 (Acceptable): 4 prompts (20%)
- 2/5 (Problematic): 2 prompts (10%)
- 1/5 (Broken): 0 prompts (0%)

**Average Scores by Criterion:**
- Task clarity: 4.85 (strong)
- Constraint independence: 4.05 (good)
- Persona coherence: 4.24 (good)
- Category alignment: 3.95 (acceptable)
- Combination harmony: 3.75 (acceptable)

---

## Cross-Corpus Patterns

### Problematic Token Combinations

1. **Form/Channel conflicts** (3 instances):
   - gherkin + presenterm (seed 0001)
   - plain + diagram (seed 0013)
   - gherkin + slack (seed 0018)
   - **Pattern**: Form tokens expecting prose conflict with channel tokens expecting structured output

2. **Task/Method misalignment** (3 instances):
   - fix + dimension + socratic (seed 0019)
   - sort + converge (seed 0007)
   - diff + diagram (seed 0003)
   - **Pattern**: Analytical methods (dimension, simulation) conflict with delivery tasks (fix, pick)

3. **Persona/Intent mismatch** (3 instances):
   - sort + entertain (seed 0010)
   - show + announce (seed 0012)
   - chat to CEO casually (seed 0016)
   - **Pattern**: Intent tokens conflict with task rigor or audience expectations

### High-Performing Combinations

1. **Scope + matching static** (4 instances):
   - plan + act (seed 0004)
   - show + fail (seed 0009)
   - probe + struct (seed 0015)
   - diff + act (seed 0008)
   - **Pattern**: Scope tokens naturally reinforce task focus

2. **Persona presets** (6 instances):
   - product_manager_to_team (seeds 0004, 0008, 0015, 0018)
   - designer_to_pm (seeds 0009, 0020)
   - teach_junior_dev (seed 0011)
   - **Pattern**: Preset personas are internally coherent and broadly compatible

### Tokens with Consistent Issues

1. **gherkin** (form): Conflicts with presenterm, slack, diagram channels
2. **diagram** (channel): Limits tasks requiring prose justification (pick, sort with plain)
3. **entertain** (intent): Undermines precision tasks (sort, check)
4. **announce** (intent): Conflicts with analytical tasks (show, probe)
5. **socratic** (form): Conflicts with delivery tasks (fix, plan)
6. **dimension** (method): Overlaps with probe task
7. **converge** (method): Overlaps with pick task

### Tokens with Strong Performance

1. **struct** (scope): Always scored 4-5, reinforces analytical tasks
2. **full** (completeness): Widely compatible, appeared in 11/20 prompts
3. **act** (scope): Natural fit for planning/action tasks
4. **product_manager_to_team** (persona preset): Consistently coherent
5. **scaffold** (form): Adds pedagogical structure without conflicts

---

## Key Findings

1. **Channel/form boundary violation is the #1 issue**: Pure-output channels (diagram, gherkin) conflict with prose forms (plain, scaffold) and other channels (presenterm, slack). Need better mutual exclusion rules.

2. **Method tokens blur into task territory**: dimension, converge, and simulation partially redefine WHAT rather than HOW, violating the constraint boundary.

3. **Intent tokens need task compatibility guidance**: entertain and announce create mismatches with specific static prompts.

4. **Persona presets outperform composed personas**: Presets (product_manager_to_team, designer_to_pm) showed 100% coherence vs 75% for composed personas.

5. **Scope tokens are the strongest constraint type**: struct, act, and fail consistently reinforced tasks without conflicts.

6. **Completeness is the most stable axis**: full, gist, and minimal worked across almost all combinations.

---

## Next Steps

1. Review recommendations in recommendations.yaml
2. Prioritize form/channel mutual exclusion rules
3. Consider retiring or recategorizing method tokens that overlap with tasks
4. Add compatibility metadata to tokens (compatible_with, incompatible_with)
5. Re-run evaluation after catalog edits to measure improvement
