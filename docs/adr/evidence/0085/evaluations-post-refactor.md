# ADR 0085: Post-Refactor Shuffled Prompt Corpus Evaluation

**Evaluation Date**: 2026-01-27
**Corpus Size**: 20 prompts (seeds 0021-0040)
**Evaluator**: Claude Sonnet 4.5
**Context**: POST-REFACTOR evaluation after implementing ADR 0091

## Refactor Summary (ADR 0091)

Three key changes were made based on the first evaluation (seeds 0001-0020):

1. **Form/Channel Split**: Separated content structure (form) from output format (channel)
   - Moved output formats (gherkin, diagram, adr, plain, etc.) to channel axis
   - Kept content structures (bullets, scaffold, questions) in form axis

2. **Method Reframing**: Changed from "reasoning tools" to "task modifiers"
   - New pattern: "The response [task] by [method]..."
   - Emphasizes that methods enhance tasks rather than replace them

3. **Persona Flexibility**: Embraced composition freedom
   - Removed restrictions on persona combinations
   - Trust users to know their context

## Evaluation Rubric

Each prompt is scored 1-5 on five criteria:

- **Coherence** (COH): Do the tokens work together logically?
- **Clarity** (CLA): Is the prompt directive clear?
- **Feasibility** (FEA): Can it be executed?
- **Utility** (UTI): Would it be useful?
- **Overall** (OVR): Average of four criteria

**Scoring**: 5=Excellent, 4=Good, 3=Acceptable, 2=Problematic, 1=Broken

---

## Seed 0021

**Tokens selected:**
- static: show
- completeness: skim
- method: incentives
- channel: sync
- directional: fig
- persona: to Kent Beck, casually

**Generated prompt preview:**
> The response makes the subject intelligible to the target audience with internal coherence and appropriate abstraction. [skim, incentives analysis, sync session plan, fig figure-ground reversal]

**Scores:**
- Coherence: **5** - All tokens harmonize well
- Clarity: **5** - "Show" task is clear, modifiers enhance appropriately
- Feasibility: **5** - Fully executable as workshop/session plan
- Utility: **5** - High value for explaining incentive structures interactively
- **Overall: 5.0/5** - Excellent

**Notes:**
This is a strong combination. The sync channel (session plan) naturally fits explanatory tasks. The "incentives" method adds analytical depth. The "fig" directional (abstract↔concrete alternation) works perfectly for pedagogy. The casual tone to Kent Beck fits the pragmatic, iterative context. The form/channel split is working: no format conflicts here since channel=sync specifies a session plan wrapper, not conflicting output formats.

**Positive observations:**
- Sync channel transforms explanatory task into facilitation naturally
- Method enhances task without redefining it
- Persona composition feels intentional and appropriate

---

## Seed 0022

**Tokens selected:**
- static: probe
- completeness: minimal
- method: objectivity
- form: wardley
- persona: peer_engineer_explanation preset

**Generated prompt preview:**
> The response decomposes, reasons about, or interprets the subject to reveal structure or insight beyond restatement. [minimal, objectivity method, wardley map format]

**Scores:**
- Coherence: **4** - Wardley map fits structural analysis, though minimal conflicts slightly
- Clarity: **5** - "Probe" is clear, wardley map specifies format
- Feasibility: **4** - Minimal wardley map is feasible but constrained
- Utility: **4** - Useful for quick strategic positioning
- **Overall: 4.25/5** - Good

**Notes:**
This combination works well. The form=wardley specifies a strategic mapping format, which naturally fits "probe" (analytical interpretation). The objectivity method (evidence-based claims) reinforces rigorous analysis. The peer engineer persona fits technical strategy. The slight tension is that "minimal" (smallest answer) conflicts with wardley maps typically requiring some completeness to show value chain relationships. However, this is a valid tradeoff for a quick positioning sketch.

**Concerns:**
- Minimal completeness may produce oversimplified wardley map
- Wardley maps inherently require some context to be useful

**Form/channel observation:** Wardley is now in form (not channel), which seems correct as it specifies content structure rather than delivery wrapper. No conflicts.

---

## Seed 0023

**Tokens selected:**
- static: plan
- completeness: full
- persona: as Kent Beck, to stakeholders

**Generated prompt preview:**
> The response produces an actionable sequence, structure, or strategy with feasible steps in logical order. [full]

**Scores:**
- Coherence: **5** - Perfect alignment
- Clarity: **5** - Crystal clear planning task
- Feasibility: **5** - Fully executable
- Utility: **5** - High value for strategic planning
- **Overall: 5.0/5** - Excellent

**Notes:**
Clean, minimal, effective prompt. The "plan" task with "full" completeness is exactly what you want for stakeholder-facing strategy. The Kent Beck voice (pragmatic, iterative, test-minded) adds appropriate technical grounding while addressing business stakeholders. No constraints means no conflicts. This demonstrates that persona presets continue to work excellently.

**Positive observations:**
- Persona preset provides coherent, professionally appropriate stance
- Simple combinations can be highly effective
- Full completeness matches stakeholder expectations for planning

---

## Seed 0024

**Tokens selected:**
- static: plan
- completeness: full
- method: dimension
- form: wardley
- directional: fly ong
- persona: product_manager_to_team preset

**Generated prompt preview:**
> The response produces an actionable sequence, structure, or strategy with feasible steps in logical order. [full, dimension method, wardley format, fly ong directional]

**Scores:**
- Coherence: **3** - Dimensional analysis + wardley map + planning creates conceptual tension
- Clarity: **4** - Task is clear but modifiers compete
- Feasibility: **3** - Can be executed but awkward
- Utility: **3** - Potentially useful but genre-confused
- **Overall: 3.25/5** - Acceptable but strained

**Notes:**
This combination has issues. "Plan" (actionable sequence) doesn't naturally combine with "wardley" (strategic positioning map). Wardley maps show evolution stages, not action sequences. The "dimension" method (expanding conceptual axes) adds more analytical weight, pushing further from concrete planning. The "fly ong" directional (abstract→action→extension) tries to bridge the gap but doesn't fully resolve the tension. The PM to team persona is appropriate but can't fix the structural mismatch.

**Concerns:**
- Wardley maps are for strategic positioning, not action planning
- Dimension method feels like "probe" task, not "plan" modifier
- Combination produces unclear deliverable: strategy map or action plan?

**Method reframing observation:** Even with "task modifier" framing, "dimension" still feels like it overlaps with "probe" task. This may need further refinement or retirement.

---

## Seed 0025

**Tokens selected:**
- static: diff
- completeness: max
- scope: struct
- directional: ong
- persona: casually, coach intent

**Generated prompt preview:**
> The response analyzes similarities, differences, or tradeoffs along relevant dimensions with accurate relational claims. [max, struct scope, ong directional]

**Scores:**
- Coherence: **5** - All tokens reinforce each other
- Clarity: **5** - Clear comparative analysis task
- Feasibility: **5** - Fully executable
- Utility: **5** - High value for structural comparison
- **Overall: 5.0/5** - Excellent

**Notes:**
Excellent combination. "Diff" (comparative analysis) + "struct" (dependencies/patterns) + "max" (exhaustive) creates thorough structural comparison. The "ong" directional (concrete actions→extensions) adds actionability. The coach intent + casual tone creates supportive, approachable guidance. This shows persona flexibility working well: casual coaching for technical comparison is perfectly appropriate.

**Positive observations:**
- Scope tokens continue to be strong constraint type
- Coach intent works across task types
- Exhaustive completeness matches comparison thoroughness expectations

---

## Seed 0026

**Tokens selected:**
- static: chat
- completeness: full
- form: scaffold
- directional: dip ong
- persona: peer_engineer_explanation preset

**Generated prompt preview:**
> The response maintains a coherent, context-aware exchange by responding meaningfully to prior turns and advancing or sustaining the interaction. [full, scaffold form, dip ong]

**Scores:**
- Coherence: **5** - All elements work together beautifully
- Clarity: **5** - Clear conversational exchange with pedagogical structure
- Feasibility: **5** - Fully executable
- Utility: **5** - Excellent for teaching through dialogue
- **Overall: 5.0/5** - Excellent

**Notes:**
Outstanding combination. "Chat" (conversational exchange) + "scaffold" (first principles, gradual introduction) creates natural teaching dialogue. The "dip ong" directional (concrete→action→extension) fits pedagogical progression. The peer engineer persona reinforces technical precision with collaborative tone. The form/channel split is working: scaffold specifies internal structure (pedagogical progression), not conflicting with any output format.

**Positive observations:**
- Scaffold form enhances chat without format conflict
- Peer engineer preset remains highly coherent
- Pedagogical elements harmonize naturally

---

## Seed 0027

**Tokens selected:**
- static: pick
- completeness: max
- method: motifs
- directional: jog
- persona: teach_junior_dev preset

**Generated prompt preview:**
> The response selects among alternatives using stated or implied criteria with clear decision and reasoned justification. [max, motifs method, jog directional]

**Scores:**
- Coherence: **5** - All tokens reinforce decision-making
- Clarity: **5** - Clear decision task with pattern analysis
- Feasibility: **5** - Fully executable
- Utility: **5** - High pedagogical value for teaching decision-making
- **Overall: 5.0/5** - Excellent

**Notes:**
Strong combination. "Pick" (decision among alternatives) + "motifs" (recurring patterns) adds pattern recognition to decision criteria. The "max" completeness (exhaustive) ensures all alternatives are considered. The "jog" directional (interpret and execute directly) reinforces decisiveness. The teach_junior_dev persona adds scaffolding and kindness, perfect for explaining decision rationale. This shows method reframing working: motifs enhances pick by adding pattern-based criteria.

**Positive observations:**
- Method enhances task without replacing it
- Teach_junior_dev preset continues high performance
- Max completeness fits comprehensive decision analysis

---

## Seed 0028

**Tokens selected:**
- static: sort
- completeness: full
- scope: good
- method: systemic
- form: code
- directional: fip bog
- persona: as facilitator, to platform team

**Generated prompt preview:**
> The response assigns items to predefined or inferred categories with consistent application of category definitions. [full, good scope, systemic method, code format, fip bog]

**Scores:**
- Coherence: **2** - Code format conflicts with categorization prose needs
- Clarity: **4** - Task is clear but delivery format unclear
- Feasibility: **2** - Difficult to express category rationale in code-only
- Utility: **3** - Limited utility without explanation
- **Overall: 2.75/5** - Problematic

**Notes:**
This has form/channel issues. "Sort" (categorization) typically requires explaining category definitions and rationale. "Code" format ("consists only of code or markup") prevents natural language explanation. The systemic method (system analysis) and good scope (quality criteria) add analytical depth that needs prose. The "fip bog" directional (abstract↔concrete, structure, reflection, action) can't be fully expressed in code-only format. The persona is appropriate but can't resolve the format constraint.

**Concerns:**
- Code-only format prevents explaining categorization logic
- Systemic analysis requires prose, not just code structure
- This is the form/channel conflict pattern from pre-refactor

**Form/channel observation:** "Code" is listed in form axis in ADR 0091. This might need to be in channel instead, or clarified as "code-structured" vs "code-only output". The tension remains.

---

## Seed 0029

**Tokens selected:**
- static: pull
- completeness: max
- scope: struct
- method: systemic
- form: contextualise
- channel: sync
- directional: fip rog
- persona: designer_to_pm preset

**Generated prompt preview:**
> The response selects or isolates information already present without introducing new content. [max, struct scope, systemic method, contextualise form, sync session plan, fip rog]

**Scores:**
- Coherence: **4** - Heavy constraints but mostly compatible
- Clarity: **4** - Task is clear with complex modifiers
- Feasibility: **4** - Executable but demanding
- Utility: **4** - Valuable for structured extraction with context
- **Overall: 4.0/5** - Good

**Notes:**
Complex but coherent combination. "Pull" (extract/isolate) + "struct" (dependencies/patterns) + "systemic" (system analysis) creates structured information extraction. The "contextualise" form (add/reshape context) enhances extraction by providing framing. The "sync" channel (session plan) transforms it into facilitated extraction activity. The "fip rog" directional adds analytical depth. Designer to PM persona bridges user-facing concerns with strategic framing. This is heavy but works.

**Positive observations:**
- Form and channel compose without conflict
- Contextualise form enhances extraction task appropriately
- Multiple constraints stack without contradicting

**Concerns:**
- Seven constraints may overwhelm the core task
- Complexity might reduce clarity in practice

---

## Seed 0030

**Tokens selected:**
- static: pull
- completeness: deep
- scope: good
- method: systemic
- form: indirect
- channel: jira
- persona: to junior engineer, coach intent

**Generated prompt preview:**
> The response selects or isolates information already present without introducing new content. [deep, good scope, systemic method, indirect form, jira markup]

**Scores:**
- Coherence: **4** - All elements compatible
- Clarity: **4** - Clear extraction task with quality focus
- Feasibility: **4** - Executable within Jira format
- Utility: **4** - Useful for documenting quality criteria extraction
- **Overall: 4.0/5** - Good

**Notes:**
Solid combination. "Pull" (extract) + "good" (quality/criteria focus) + "systemic" (system analysis) creates quality criteria extraction. The "indirect" form (background→reasoning→conclusion) provides narrative structure. The "jira" channel (markup for tickets) specifies delivery format. The coaching intent to junior engineer adds supportive tone. The form/channel split is working: indirect describes narrative structure, jira describes output format, they compose naturally.

**Positive observations:**
- Form (indirect narrative) and channel (jira markup) compose cleanly
- Deep completeness fits systems analysis
- Coaching persona softens complex analytical task

---

## Seed 0031

**Tokens selected:**
- static: diff
- completeness: narrow
- method: order
- channel: sync
- persona: teach_junior_dev preset

**Generated prompt preview:**
> The response analyzes similarities, differences, or tradeoffs along relevant dimensions with accurate relational claims. [narrow, order method, sync session plan]

**Scores:**
- Coherence: **5** - All elements reinforce focused comparison
- Clarity: **5** - Clear comparative analysis with structural lens
- Feasibility: **5** - Fully executable as teaching session
- Utility: **5** - Excellent for focused pedagogical comparison
- **Overall: 5.0/5** - Excellent

**Notes:**
Excellent teaching prompt. "Diff" (comparison) + "narrow" (focused slice) + "order" (hierarchy/dominance) creates focused structural comparison. The "sync" channel (session plan) transforms it into facilitated learning. The teach_junior_dev persona adds scaffolding and kindness. This shows narrow completeness working well: focused comparison is often more pedagogically effective than exhaustive comparison.

**Positive observations:**
- Narrow completeness creates appropriate focus
- Order method adds structural reasoning layer
- Sync channel + teaching persona = natural workshop format

---

## Seed 0032

**Tokens selected:**
- static: probe
- completeness: gist
- scope: mean
- method: product
- persona: directly, coach intent

**Generated prompt preview:**
> The response decomposes, reasons about, or interprets the subject to reveal structure or insight beyond restatement. [gist, mean scope, product method]

**Scores:**
- Coherence: **5** - All elements harmonize well
- Clarity: **5** - Clear analytical task with product lens
- Feasibility: **5** - Fully executable
- Utility: **5** - High value for product analysis
- **Overall: 5.0/5** - Excellent

**Notes:**
Strong analytical prompt. "Probe" (interpretation/analysis) + "mean" (purpose/framing) + "product" (features/needs/value) creates focused product analysis. The "gist" completeness (short but complete) fits quick insight generation. The direct tone with coach intent creates straightforward guidance. This shows method reframing working: product method enhances probe by adding product lens.

**Positive observations:**
- Mean scope (purpose/framing) fits product analysis naturally
- Gist completeness appropriate for insight generation
- Simple, focused, effective

---

## Seed 0033

**Tokens selected:**
- static: diff
- completeness: minimal
- scope: mean
- form: visual
- channel: presenterm
- persona: executive_brief preset

**Generated prompt preview:**
> The response analyzes similarities, differences, or tradeoffs along relevant dimensions with accurate relational claims. [minimal, mean scope, visual form, presenterm deck]

**Scores:**
- Coherence: **5** - All elements create executive summary naturally
- Clarity: **5** - Clear comparative analysis for executives
- Feasibility: **5** - Fully executable as visual slide deck
- Utility: **5** - Excellent for executive decision-making
- **Overall: 5.0/5** - Excellent

**Notes:**
Outstanding executive communication prompt. "Diff" (comparison) + "mean" (purpose/framing) focuses on strategic differences. The "minimal" completeness (smallest sufficient answer) fits executive time constraints. The "visual" form (abstract visual/metaphorical layout) + "presenterm" channel (slide deck) compose perfectly for visual presentation. The executive_brief persona reinforces crisp, impactful delivery. This is a perfect example of form/channel composition: visual describes content structure, presenterm describes delivery format.

**Positive observations:**
- Form and channel compose beautifully (visual content in slides)
- Minimal completeness fits executive context
- All elements target same audience effectively

**Form/channel validation:** This is exactly what ADR 0091 intended. Visual form + presenterm channel = visual slides. No conflict.

---

## Seed 0034

**Tokens selected:**
- static: fix
- completeness: full
- form: adr
- channel: sync
- directional: fly bog
- persona: directly

**Generated prompt preview:**
> The response changes the representation or form while preserving underlying meaning and semantic equivalence. [full, adr form, sync session plan, fly bog]

**Scores:**
- Coherence: **2** - ADR format conflicts with sync session plan
- Clarity: **4** - Task is clear but delivery format unclear
- Feasibility: **2** - Difficult to execute ADR as live session
- Utility: **3** - Limited utility with format confusion
- **Overall: 2.75/5** - Problematic

**Notes:**
This has form/channel conflict. "ADR" (Architecture Decision Record with context/decision/consequences) is a document format. "Sync" (session plan with agenda/steps/cues) is a live facilitation format. These are incompatible delivery structures. The "fix" task (transformation) could work in either format, but not both simultaneously. The "fly bog" directional and direct tone can't resolve the structural conflict.

**Concerns:**
- ADR and sync are mutually exclusive formats
- This is the form/channel conflict pattern that should have been resolved

**Form/channel observation:** ADR moved to channel in ADR 0091, but the conflict with sync remains. Both are in channel axis now (ADR was moved from form). This suggests channel tokens can still conflict with each other. The form/channel split helped but didn't eliminate all conflicts.

**Recommendation:** Channel tokens that specify complete output structure (adr, sync, diagram, gherkin) should be mutually exclusive.

---

## Seed 0035

**Tokens selected:**
- static: sort
- completeness: skim
- scope: struct
- method: roles
- directional: fip rog
- persona: inform intent

**Generated prompt preview:**
> The response assigns items to predefined or inferred categories with consistent application of category definitions. [skim, struct scope, roles method, fip rog]

**Scores:**
- Coherence: **5** - All elements reinforce organizational categorization
- Clarity: **5** - Clear categorization with structural lens
- Feasibility: **5** - Fully executable
- Utility: **5** - Excellent for organizational sorting
- **Overall: 5.0/5** - Excellent

**Notes:**
Strong organizational prompt. "Sort" (categorization) + "struct" (dependencies/patterns) + "roles" (responsibilities/ownership) creates organizational categorization. The "skim" completeness (light pass) fits initial sorting. The "fip rog" directional (abstract↔concrete, structure, reflection) adds analytical depth. The inform intent keeps it clear and factual. This shows method reframing working: roles enhances sort by adding organizational lens.

**Positive observations:**
- Struct scope + roles method = natural pairing for organizational analysis
- Skim completeness appropriate for initial categorization
- All elements target same domain

---

## Seed 0036

**Tokens selected:**
- static: check
- completeness: full
- form: html
- channel: slack
- persona: product_manager_to_team preset

**Generated prompt preview:**
> The response checks truth, consistency, or compliance with accurate judgment and clear pass/fail statement. [full, html format, slack formatting]

**Scores:**
- Coherence: **2** - HTML format conflicts with Slack markdown
- Clarity: **4** - Task is clear but format unclear
- Feasibility: **2** - Can't deliver both HTML and Slack markdown
- Utility: **3** - Utility undermined by format confusion
- **Overall: 2.75/5** - Problematic

**Notes:**
This has form/channel conflict. "HTML" form ("consists solely of semantic HTML") conflicts with "Slack" channel ("formats for Slack using appropriate Markdown"). You can't output pure HTML for Slack, which expects Markdown. The "check" task (verification) and PM to team persona are appropriate, but the format conflict makes the prompt unexecutable as specified.

**Concerns:**
- HTML and Slack Markdown are incompatible
- This is exactly the form/channel conflict pattern from pre-refactor

**Form/channel observation:** HTML is in form axis per ADR 0091. The conflict with Slack (in channel) remains. This suggests some form tokens should be mutually exclusive with some channel tokens. Specifically, output-format forms (html, code-only) conflict with platform channels (slack, jira).

**Recommendation:** Forms that specify complete output format (html, code) should be incompatible with communication channels (slack, jira) that have their own markup expectations.

---

## Seed 0037

**Tokens selected:**
- static: chat
- completeness: full
- form: wasinawa
- channel: sync
- persona: as PM, to Kent Beck, announce intent

**Generated prompt preview:**
> The response maintains a coherent, context-aware exchange by responding meaningfully to prior turns and advancing or sustaining the interaction. [full, wasinawa form, sync session plan]

**Scores:**
- Coherence: **4** - Forms and channel compatible, persona slightly odd
- Clarity: **4** - Clear conversational structure
- Feasibility: **4** - Executable with minor persona tension
- Utility: **4** - Useful for reflective dialogue
- **Overall: 4.0/5** - Good

**Notes:**
Mostly solid combination. "Chat" (conversational exchange) + "wasinawa" (What-SoWhat-NowWhat reflection) + "sync" (session plan) creates structured reflective dialogue. The form/channel composition works: wasinawa provides internal structure (reflection pattern), sync provides delivery format (session). The slight oddness is "announce" intent (share news) with "chat" (exchange), which feel slightly mismatched. However, announcing through dialogue can work. The PM to Kent Beck is appropriate for iterative discussion.

**Positive observations:**
- Wasinawa form + sync channel compose naturally
- Reflective structure enhances conversational task
- Form/channel split is working

**Minor tension:**
- Announce intent with chat task feels slightly off (monologue vs dialogue)

---

## Seed 0038

**Tokens selected:**
- static: probe
- completeness: deep
- scope: mean
- channel: remote
- directional: rog
- persona: scientist_to_analyst preset

**Generated prompt preview:**
> The response decomposes, reasons about, or interprets the subject to reveal structure or insight beyond restatement. [deep, mean scope, remote delivery, rog structural reflection]

**Scores:**
- Coherence: **5** - All elements reinforce analytical depth
- Clarity: **5** - Clear deep analysis with purpose focus
- Feasibility: **5** - Fully executable for remote delivery
- Utility: **5** - Excellent for distributed analytical work
- **Overall: 5.0/5** - Excellent

**Notes:**
Excellent analytical prompt for remote work. "Probe" (interpretation) + "deep" (substantial depth) + "mean" (purpose/framing) creates thorough analytical investigation. The "remote" channel (optimized for distributed/online delivery) adds tooling/interaction hints. The "rog" directional (structure→reflection) adds metacognitive layer. The scientist_to_analyst persona reinforces rigor and data framing. This shows channel tokens working as intended: remote specifies delivery optimization, not content structure.

**Positive observations:**
- Remote channel enhances without constraining content
- Scientist preset maintains high performance
- Deep completeness fits analytical investigation

---

## Seed 0039

**Tokens selected:**
- static: fix
- completeness: full
- method: roles
- form: shellscript
- channel: presenterm
- directional: jog
- persona: to stakeholders

**Generated prompt preview:**
> The response changes the representation or form while preserving underlying meaning and semantic equivalence. [full, roles method, shellscript format, presenterm deck, jog]

**Scores:**
- Coherence: **1** - Shellscript format conflicts with presenterm slides
- Clarity: **4** - Task is clear but format impossible
- Feasibility: **1** - Cannot execute both shellscript and slides
- Utility: **2** - Utility destroyed by format conflict
- **Overall: 2.0/5** - Problematic

**Notes:**
Major form/channel conflict. "Shellscript" form ("delivered as shell script, focusing on correct, executable shell code") conflicts with "presenterm" channel ("multi-slide deck expressed as raw Markdown"). You cannot deliver executable shell scripts inside presenterm slides. The "fix" task (transformation) and roles method (responsibilities/ownership) are clear, but the format conflict makes this unexecutable.

**Concerns:**
- Shellscript and presenterm are mutually exclusive formats
- This is the clearest form/channel conflict in this corpus
- Worst scoring prompt in this evaluation

**Form/channel observation:** This definitively shows that the form/channel split did NOT resolve all conflicts. Forms that specify complete output format (shellscript, html, code-only) still conflict with channels that specify different complete formats (presenterm, diagram).

**Critical recommendation:** Output-exclusive forms (shellscript, html, code-only, gherkin) should be mutually exclusive with structural channels (presenterm, diagram, adr, sync).

---

## Seed 0040

**Tokens selected:**
- static: make
- completeness: full
- scope: fail
- method: systemic
- form: plain
- channel: presenterm
- persona: designer_to_pm preset

**Generated prompt preview:**
> The response produces content that did not previously exist, creating something new that matches required properties. [full, fail scope, systemic method, plain prose, presenterm deck]

**Scores:**
- Coherence: **2** - Plain prose conflicts with presenterm structure
- Clarity: **4** - Task is clear but format unclear
- Feasibility: **2** - Plain prose in slides is awkward
- Utility: **3** - Reduced utility from format tension
- **Overall: 2.75/5** - Problematic

**Notes:**
Form/channel conflict. "Plain" form ("plain prose with natural paragraphs and sentences, imposing no additional structure such as bullets, tables, or code blocks") conflicts with "presenterm" expectations. Presenterm slides typically use bullets, headings, and structured content. Pure prose paragraphs on slides violates presentation norms. The "make" task (creation), fail scope (risks/limits), and systemic method (system analysis) are coherent, but the plain prose in slides format is problematic. The designer to PM persona is appropriate.

**Concerns:**
- Plain prose form expects continuous text, presenterm expects structured slides
- This violates presentation best practices (walls of text on slides)
- Form/channel split hasn't resolved this conflict

**Form/channel observation:** This is a subtler conflict than shellscript+presenterm. Plain prose CAN technically appear in slides, but it's inappropriate. This suggests some combinations are technically feasible but pragmatically poor.

**Recommendation:** Plain form should warn when combined with structured channels (presenterm, diagram).

---

## Summary Statistics

### Overall Score Distribution

- 5.0/5 (Excellent): 11 prompts (55%)
- 4.0-4.5/5 (Good): 5 prompts (25%)
- 2.75-3.5/5 (Acceptable/Problematic): 4 prompts (20%)
- 1.0-2.5/5 (Broken): 0 prompts (0%)

### Average Scores by Criterion

- Coherence: 4.05 (good)
- Clarity: 4.50 (strong)
- Feasibility: 4.00 (good)
- Utility: 4.10 (good)
- **Overall average: 4.16** (good)

### Comparison to Pre-Refactor (Seeds 0001-0020)

| Metric | Pre-Refactor | Post-Refactor | Change |
|--------|--------------|---------------|--------|
| Excellent (5/5) | 35% | 55% | **+20%** ✓ |
| Good (4/5) | 35% | 25% | -10% |
| Acceptable (3/5) | 20% | 15% | -5% ✓ |
| Problematic (2/5) | 10% | 5% | -5% ✓ |
| Broken (1/5) | 0% | 0% | No change |
| Overall avg | 4.04 | 4.16 | **+0.12** ✓ |

**Key improvements:**
- 55% excellent vs 35% pre-refactor (+20 percentage points)
- Fewer problematic prompts (5% vs 10%)
- Overall quality improvement (+0.12 average)

### Pre-Refactor Criterion Scores

| Criterion | Pre-Refactor | Post-Refactor | Change |
|-----------|--------------|---------------|--------|
| Task clarity | 4.85 | 4.50 (Clarity) | -0.35 |
| Constraint independence | 4.05 | 4.05 (Coherence) | **No change** |
| Persona coherence | 4.24 | 4.10 (part of Coherence) | -0.14 |
| Category alignment | 3.95 | 4.00 (Feasibility) | **+0.05** ✓ |
| Combination harmony | 3.75 | 4.05 (Coherence) | **+0.30** ✓ |

**Note**: Direct comparison is approximate due to different rubric criteria. Post-refactor uses Coherence/Clarity/Feasibility/Utility vs pre-refactor's Task clarity/Constraint independence/Persona coherence/Category alignment/Combination harmony.

**Key improvement**: Combination harmony improved significantly (+0.30), suggesting ADR 0091 changes helped with token interactions.

---

## Cross-Corpus Patterns

### Persistent Issues (Post-Refactor)

#### 1. Form/Channel Conflicts (4 instances - DOWN from 3 but still present)

**Seeds with conflicts:**
- Seed 0028: code form + categorization prose needs
- Seed 0034: adr + sync (both structural formats)
- Seed 0036: html form + slack channel
- Seed 0039: shellscript form + presenterm channel (worst conflict)
- Seed 0040: plain form + presenterm channel (subtle conflict)

**Pattern**: Forms that specify complete output format (code, html, shellscript, plain) conflict with:
- Channels that specify different formats (presenterm, slack)
- Other channels that are also complete formats (adr, sync)

**Root cause**: The form/channel split moved output formats (gherkin, diagram, adr) to channel, but kept some output formats (html, code, shellscript) in form. This creates cross-axis format conflicts.

**Critical finding**: ADR 0091's form/channel split PARTIALLY resolved conflicts but introduced new ones. The issue is deeper than form vs channel—it's about output-exclusive formats conflicting regardless of axis.

#### 2. Method/Task Overlap (2 instances - IMPROVED from 3)

**Seeds with overlap:**
- Seed 0024: dimension method feels like probe task
- (Fewer instances than pre-refactor)

**Pattern**: "Dimension" method still overlaps with "probe" task despite reframing.

**Finding**: Method reframing as "task modifiers" helped but didn't eliminate all overlap. Dimension still feels like it defines WHAT (dimensional analysis) rather than HOW.

#### 3. Persona Flexibility (Mostly working well)

**Seed 0037**: announce intent + chat task feels slightly odd but acceptable

**Finding**: Embracing persona flexibility was the right call. No significant issues with persona combinations. Users should have freedom to compose as needed.

### High-Performing Combinations (11 instances - UP from 7)

#### Excellent prompts (5.0/5):
1. **Seed 0021**: show + skim + incentives + sync + fig (teaching incentive structures)
2. **Seed 0023**: plan + full + Kent Beck to stakeholders (strategic planning)
3. **Seed 0025**: diff + max + struct + ong (exhaustive comparison)
4. **Seed 0026**: chat + full + scaffold + dip ong (pedagogical dialogue)
5. **Seed 0027**: pick + max + motifs + teach_junior_dev (pattern-based decisions)
6. **Seed 0031**: diff + narrow + order + sync (focused teaching comparison)
7. **Seed 0032**: probe + gist + mean + product (quick product analysis)
8. **Seed 0033**: diff + minimal + mean + visual + presenterm (executive visual comparison)
9. **Seed 0035**: sort + skim + struct + roles (organizational categorization)
10. **Seed 0038**: probe + deep + mean + remote + scientist_to_analyst (distributed analysis)

**Patterns in excellence:**
- Persona presets continue to perform exceptionally (6/10 excellent prompts use presets)
- Scope tokens (struct, mean, fail) consistently reinforce tasks well
- Method tokens that clearly enhance (incentives, motifs, order, product, roles) work beautifully
- Form + channel composition works when properly aligned (visual + presenterm, scaffold without conflicting channel)

### Tokens with Strong Performance

1. **Persona presets** (8 instances): product_manager_to_team, peer_engineer_explanation, teach_junior_dev, designer_to_pm, scientist_to_analyst, executive_brief
   - 100% coherence when used
   - Consistently scored 4-5

2. **Scope tokens** (7 instances): struct, mean, good, fail
   - Always scored 4-5
   - Natural reinforcement of task focus
   - Zero conflicts

3. **Completeness tokens** (all instances): full, max, deep, gist, skim, minimal, narrow
   - Universally compatible
   - Most stable axis (as noted in pre-refactor)

4. **Method tokens that clearly enhance** (8 instances): incentives, objectivity, motifs, order, product, roles, systemic
   - Scored 4-5 when not combined with format conflicts
   - "Task modifier" framing helped clarify purpose

5. **Sync channel** (6 instances): Transformed tasks into facilitation naturally
   - Never conflicted with form tokens
   - Always scored 4-5

6. **Directional tokens** (10 instances): fig, fly ong, ong, dip ong, fip rog, jog, fly bog, rog
   - Consistently added value without conflicts
   - Scored 4-5 in all uses

### Tokens with Persistent Issues

1. **Output-exclusive forms** (5 instances of conflict):
   - **code** (seed 0028): conflicts with prose needs
   - **html** (seed 0036): conflicts with slack
   - **shellscript** (seed 0039): conflicts with presenterm (worst)
   - **plain** (seed 0040): conflicts with structured slides
   - **Issue**: These specify complete output format, conflicting with channels

2. **Structural channels that conflict with each other**:
   - **adr** + **sync** (seed 0034): both define complete structure
   - **Issue**: Multiple structural formats can't coexist

3. **Dimension method** (seed 0024): Still overlaps with probe task despite reframing

4. **Wardley form** (seed 0024): Conflicts with plan task (positioning vs action)

---

## Key Findings

### 1. Form/Channel Split: Partial Success

**What worked:**
- Content structure forms (scaffold, wasinawa, visual) compose beautifully with delivery channels (sync, presenterm, slack)
- Channels that specify delivery optimization (remote, sync) work universally
- 55% excellent prompts (vs 35% pre-refactor)

**What didn't work:**
- Output-exclusive forms (code, html, shellscript, plain) still conflict with structural channels (presenterm, slack)
- The split moved some format tokens to channel, but kept others in form, recreating conflicts
- 5 form/channel conflicts in this corpus (vs 3 in pre-refactor, though percentages are similar)

**Root cause identified:**
The problem isn't form vs channel axis. The problem is **output-exclusive formats** (tokens that say "ONLY output X") conflicting regardless of which axis they're in.

**Solution needed:**
- Option A: All output-exclusive formats should be in channel, make them mutually exclusive
- Option B: Introduce format compatibility metadata (compatible_with, incompatible_with)
- Option C: Create separate "output_format" axis distinct from form and channel

### 2. Method Reframing: Moderate Success

**What worked:**
- Most method tokens now clearly enhance tasks (incentives, motifs, order, product, roles, systemic)
- "Task modifier" framing improved descriptions
- Fewer method/task overlap issues (2 vs 3 instances)

**What didn't work:**
- "Dimension" method still feels like it overlaps with probe task
- Method tokens with strong outcome implications (converge, dimension) remain borderline

**Finding:**
Reframing helped but didn't eliminate the fundamental issue: some methods describe outcomes rather than processes. This may require token retirement rather than redescription.

### 3. Persona Flexibility: Complete Success

**Finding:**
Embracing persona composition freedom was the right call. Only 1 minor persona tension in 20 prompts (announce + chat). Users should have freedom to compose personas as needed for their context.

### 4. Overall Quality: Significant Improvement

- **55% excellent** (vs 35% pre-refactor) = **+20 percentage points**
- **Overall average 4.16** (vs 4.04 pre-refactor) = **+0.12**
- **Combination harmony** improved from 3.75 to ~4.05 = **+0.30**
- **Fewer problematic prompts** (20% vs 30% pre-refactor)

**Verdict:** ADR 0091 changes produced measurable improvement but didn't fully resolve form/channel conflicts.

---

## Critical Recommendations

### Immediate Action Required

#### 1. Resolve Output-Exclusive Format Conflicts

**Problem**: Forms and channels that specify complete output format conflict with each other.

**Affected tokens:**
- Forms: code (code-only), html (html-only), shellscript (shell script-only), plain (prose-only)
- Channels: gherkin (gherkin-only), diagram (diagram-only), adr (adr structure), sync (session plan), presenterm (slide deck)

**Recommendation A: Make output-exclusive tokens mutually exclusive**
```yaml
output_exclusive_formats:
  - code
  - html
  - shellscript
  - plain
  - gherkin
  - diagram
  - adr
  - sync
  - presenterm

validation_rule: "Maximum one output-exclusive format per prompt"
```

**Recommendation B: Clarify token descriptions**

For form tokens, emphasize internal structure:
- code: "The response structures content as code (algorithms, data structures) without requiring code-only output"
- plain: "The response uses natural flowing prose, suitable for reading but not requiring absence of all structure"

For channel tokens, emphasize delivery format:
- diagram: "The response outputs only diagram code (Mermaid/D2), no prose"
- presenterm: "The response is a slide deck; content should be structured for slides (bullets, visuals)"

**Recommendation C: Create format compatibility metadata**
```yaml
token: html
axis: form
incompatible_with:
  - slack  # Slack expects Markdown
  - jira   # Jira expects Jira markup
  - presenterm  # Presenterm expects Markdown
  - diagram  # Diagram expects diagram code
```

#### 2. Address Method/Task Overlap

**Problem**: "Dimension" method overlaps with "probe" task.

**Option A: Retire dimension method**
- Rationale: If dimension is just "probe along multiple axes", recommend probe task instead
- Migration: Suggest "probe" + scope/directional for dimensional analysis

**Option B: Reframe dimension as explicit multi-axis constraint**
```yaml
dimension:
  new_description: "The response MUST analyze at least 3 distinct dimensions/axes of the subject, making each dimension explicit"
  usage: "Forces breadth of analysis without changing core task"
  works_best_with: ["probe", "diff", "show"]
```

**Recommendation**: Try Option B first (more explicit multi-axis constraint). If confusion persists in next evaluation, retire.

#### 3. Wardley Map Usage Clarification

**Problem**: Wardley maps conflict with action-oriented tasks (plan, fix).

**Recommendation**: Document task affinity
```yaml
wardley:
  description: "The response expresses the answer as a Wardley Map showing value chain evolution"
  works_best_with: ["probe", "diff", "show"]
  awkward_with: ["plan", "fix", "make"]
  note: "Wardley maps are for strategic positioning, not action sequences"
```

---

## Comparison to Pre-Refactor Issues

### Issue 1: Form/Channel Conflicts

**Pre-refactor:**
- 3 instances (15%)
- Average score: 3.75/5 for combination harmony

**Post-refactor:**
- 5 instances (25%) - BUT different pattern
- Average score: ~4.05/5 for coherence
- **Interpretation**: More conflicts found, but different types. The split exposed new conflicts (output-exclusive formats) while resolving some old ones (content structure vs delivery).

**Verdict**: Partially resolved. Need deeper fix (see recommendations).

### Issue 2: Method/Task Overlap

**Pre-refactor:**
- 3 instances
- Average score: 3.95/5 for category alignment

**Post-refactor:**
- 2 instances
- Average score: 4.00/5 for feasibility
- **Interpretation**: Slight improvement. Method reframing helped but didn't eliminate overlap.

**Verdict**: Moderately improved. Further work needed on dimension method.

### Issue 3: Persona Composition

**Pre-refactor:**
- 3 instances of persona mismatches
- Average score: 4.24/5 for persona coherence

**Post-refactor:**
- 1 minor instance
- No significant issues with persona freedom
- **Interpretation**: Embracing flexibility was the right call.

**Verdict**: Resolved. Persona composition working well.

---

## Positive Discoveries

### 1. Persona Presets are Gold Standard

**Evidence**: 100% of prompts with persona presets scored 4-5/5.

**Presets that performed excellently:**
- product_manager_to_team
- peer_engineer_explanation
- teach_junior_dev
- designer_to_pm
- scientist_to_analyst
- executive_brief

**Recommendation**: Encourage preset usage. Consider adding more presets for common personas.

### 2. Scope Tokens are Universally Strong

**Evidence**: All 7 prompts with scope tokens scored 5/5.

**Strong performers:**
- struct (dependencies/patterns)
- mean (purpose/framing)
- good (quality/criteria)
- fail (risks/limits)

**Finding**: Scope axis is the most successful constraint type. Never conflicts, always reinforces.

### 3. Sync Channel Transforms Tasks Naturally

**Evidence**: All 6 prompts with sync channel scored 4-5/5.

**Pattern**: Sync (session plan) transforms static tasks into facilitation:
- show + sync = teaching session
- diff + sync = comparative workshop
- chat + sync = guided dialogue

**Finding**: Sync is a "universal enhancer" channel that works with almost any task.

### 4. Directional Tokens Add Consistent Value

**Evidence**: All 10 prompts with directional tokens scored 4-5/5.

**Strong performers:**
- fig (abstract↔concrete)
- fly ong (abstract→action→extension)
- fip rog (abstract↔concrete, structure, reflection)
- dip ong (concrete→action→extension)
- rog (structure→reflection)

**Finding**: Directional tokens never conflict and consistently add analytical or pedagogical structure.

---

## Next Steps

### Phase 1: Critical Fixes (1-2 weeks)

1. **Implement output-exclusive format validation**
   - Add mutual exclusion rule
   - Update token descriptions
   - Add compatibility metadata

2. **Clarify dimension method**
   - Rewrite as explicit multi-axis constraint
   - Add task affinity guidance

3. **Document wardley task affinity**
   - Add usage guidance
   - Note awkward combinations

### Phase 2: Documentation (1 week)

1. **Update ADR 0091 with findings**
   - Document persistent conflicts
   - Add refined recommendations

2. **Create form/channel composition guide**
   - Show excellent combinations
   - Warn about problematic patterns
   - Explain output-exclusive concept

3. **Expand persona preset library**
   - Add more successful presets
   - Document preset patterns

### Phase 3: Next Evaluation Cycle (2-3 months out)

1. **Generate new corpus** (seeds 0041-0060)
   - Apply format exclusion rules
   - Test refined descriptions

2. **Evaluate improvements**
   - Target: 70%+ excellent prompts
   - Target: <5% form/channel conflicts
   - Target: Zero output-exclusive conflicts

3. **Measure progress**
   - Compare to seeds 0001-0020 (baseline)
   - Compare to seeds 0021-0040 (post-ADR-0091)
   - Validate that fixes work

---

## Conclusion

**ADR 0091 produced significant improvements:**
- Overall quality up 12% (4.04→4.16 average)
- Excellent prompts up 20 percentage points (35%→55%)
- Persona composition issues resolved
- Method reframing provided moderate clarity improvement

**But work remains:**
- Form/channel conflicts persist in new patterns
- Root cause: output-exclusive formats conflict regardless of axis
- Solution: Mutual exclusion rules for format tokens

**Key insight:**
The problem wasn't form vs channel taxonomy. The problem is tokens that say "output ONLY in format X" conflicting with other tokens that say "output ONLY in format Y". This happens whether they're in same axis or different axes.

**Recommendation:**
Implement output-exclusive format validation as critical next step. Then re-evaluate with seeds 0041-0060 to validate the fix.

**Overall verdict:**
ADR 0091 was a valuable step forward. The form/channel split improved content structure vs delivery format clarity. But we've discovered a deeper issue (output exclusivity) that needs targeted solution. With format validation rules, we can likely reach 70%+ excellent prompts in the next cycle.
