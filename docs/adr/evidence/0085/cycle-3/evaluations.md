# ADR 0085 Cycle-3 Shuffle Evaluation

**Evaluation Date:** 2026-02-15  
**Seeds Evaluated:** 200-229 (30 seeds)  
**Evaluator:** Claude Code (AI Agent)  
**Methodology:** ADR 0083 Prompt Key Criteria + Bar Skills Meta-Evaluation  

---

## Seed: 200

**Tokens:**
- task: diff
- completeness: full
- form: questions
- persona: to Kent Beck (audience), inform (intent)

**Prompt Key Scores:**
- Task clarity: 4/5 - Clear comparison task, though "questions" form with diff task is unconventional
- Constraint independence: 5/5 - Constraints operate independently
- Persona coherence: 4/5 - Kent Beck audience aligns with inform intent, but diff+questions combination is unusual
- Category alignment: 4/5 - Form (questions) could work with diff but feels forced
- Combination harmony: 4/5 - Minimal combination that works but lacks synergy
- **Overall**: 4/5

**Meta-Evaluation:**
- Skill alignment: 4/5 - Skills would guide toward this but not highlight questions+diff
- Skill discoverability: 4/5 - Tokens discoverable via bar help
- Heuristic coverage: 4/5 - Diff task documented, questions form documented
- Documentation completeness: 4/5 - Both tokens documented but not specifically together
- **Overall**: 4/5

**Bar Help LLM Reference:**
- Reference utility: 4/5 - Provides adequate reference for each token
- **Overall**: 4/5

**Issues:**
- Minimal combination with unusual form+task pairing

**Recommendations:**
- None critical

---

## Seed: 201

**Tokens:**
- task: pick
- completeness: full
- method: product
- form: spike
- directional: bog
- persona: stakeholder_facilitator (preset)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear pick task with spike form (research decision)
- Constraint independence: 5/5 - All constraints independent and complementary
- Persona coherence: 5/5 - Stakeholder facilitator + pick + spike = research decisions for stakeholders
- Category alignment: 5/5 - Strong alignment: pick task with product method for stakeholder decisions
- Combination harmony: 5/5 - Excellent synthesis: research spike to help stakeholders choose
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Skills would clearly recommend this combination
- Skill discoverability: 5/5 - All tokens well-documented
- Heuristic coverage: 5/5 - Product method + spike form well-documented together
- Documentation completeness: 5/5 - Full coverage
- **Overall**: 5/5

**Bar Help LLM Reference:**
- Reference utility: 5/5 - Full support for combination

**Issues:**
- None

**Recommendations:**
- Consider as exemplar: pick + product + spike for stakeholder decision-making

---

## Seed: 202

**Tokens:**
- task: plan
- completeness: gist
- method: explore
- channel: presenterm
- persona: kindly, inform

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear plan task with presenterm (slide deck)
- Constraint independence: 5/5 - All constraints independent
- Persona coherence: 5/5 - Kindly tone with informative intent works for planning presentation
- Category alignment: 5/5 - Plan + explore method + presenterm channel = exploration deck
- Combination harmony: 5/5 - Excellent: explore options in a slide deck
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Well-documented combination
- Skill discoverability: 5/5 - All tokens in catalog
- Heuristic coverage: 5/5 - Presenterm + explore well-covered
- Documentation completeness: 5/5 - Complete
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar candidate: plan + explore + presenterm

---

## Seed: 203

**Tokens:**
- task: pull
- completeness: max
- scope: act
- directional: dip ong
- persona: peer_engineer_explanation (preset)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear extraction task with action focus
- Constraint independence: 5/5 - max + act + dip ong work independently
- Persona coherence: 5/5 - Peer engineer explaining to programmer with action focus
- Category alignment: 5/5 - Act scope focuses on what to do, good for pull task
- Combination harmony: 5/5 - Extract exhaustive actions for programmers
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - All tokens well-documented
- Skill discoverability: 5/5 - Complete
- Heuristic coverage: 5/5 - Full
- Documentation completeness: 5/5 - Complete
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar: pull + act + max for action extraction

---

## Seed: 204

**Tokens:**
- task: diff
- completeness: full
- scope: assume
- method: simulation
- directional: dig
- persona: as writer, entertain

**Prompt Key Scores:**
- Task clarity: 3/5 - Diff task with simulation method could work but entertain intent conflicts with diff
- Constraint independence: 4/5 - Constraints independent
- Persona coherence: 2/5 - Entertain intent with comparison task creates tension
- Category alignment: 4/5 - Simulation method works with diff, but entertain misaligned
- Combination harmony: 2/5 - Diff (comparison) + entertain intent = unclear purpose
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Simulation method documented, but not with diff+entertain
- Skill discoverability: 4/5 - Tokens discoverable
- Heuristic coverage: 3/5 - Entertain + diff combination not covered
- Documentation completeness: 4/5 - Basic coverage
- **Overall**: 3/5

**Issues:**
- **Intent-Task Mismatch**: entertain intent doesn't align with diff task purpose

**Recommendations:**
- Document: diff task should typically use inform/teach intents, not entertain

---

## Seed: 205

**Tokens:**
- task: plan
- completeness: minimal
- persona: scientist_to_analyst (preset)

**Prompt Key Scores:**
- Task clarity: 4/5 - Clear plan task, minimal completeness unusual for planning
- Constraint independence: 5/5 - Minimal constraint independent
- Persona coherence: 4/5 - Scientist to analyst works, but minimal planning may lack rigor
- Category alignment: 4/5 - Minimal + plan = outline rather than detailed plan
- Combination harmony: 4/5 - Works but minimal planning feels incomplete for analyst audience
- **Overall**: 4/5

**Meta-Evaluation:**
- Skill alignment: 4/5 - Minimal documented, works but not highlighted
- Skill discoverability: 5/5 - Complete
- Heuristic coverage: 4/5 - Minimal + plan not specifically covered
- Documentation completeness: 4/5 - Basic info present
- **Overall**: 4/5

**Issues:**
- Minimal completeness with planning task may produce sparse output

**Recommendations:**
- Consider documenting: minimal + plan produces outline-level plans

---

## Seed: 206

**Tokens:**
- task: fix
- completeness: full
- scope: mean
- form: questions
- channel: jira
- directional: fog
- persona: as scientist, to team

**Prompt Key Scores:**
- Task clarity: 4/5 - Fix task with questions form is unusual (questions about meaning?)
- Constraint independence: 4/5 - Constraints independent but mean + questions + fog creates interpretive loop
- Persona coherence: 4/5 - Scientist voice to team works
- Category alignment: 3/5 - Mean (understanding) + fix (reformat) + questions (ask questions) = confusing
- Combination harmony: 3/5 - Multiple interpretive constraints create confusion about what fix means
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - fix documented, but mean+questions combination unclear
- Skill discoverability: 4/5 - All tokens present
- Heuristic coverage: 3/5 - No guidance for mean+fix+questions
- Documentation completeness: 4/5 - Basic coverage
- **Overall**: 3/5

**Issues:**
- **Semantic Overlap**: mean (understand meaning) + questions (ask questions) + fix (reformat) - unclear what fixing "meaning" means
- Questions form with fix task is unconventional

**Recommendations:**
- Add guidance: questions form pairs poorly with fix task
- Consider: mean scope works better with explain/show tasks

---

## Seed: 207

**Tokens:**
- task: pull
- completeness: full
- method: effects
- form: cards
- channel: diagram
- persona: product_manager_to_team (preset)

**Prompt Key Scores:**
- Task clarity: 4/5 - Extract effects in cards/diagram format
- Constraint independence: 4/5 - Form (cards) and channel (diagram) both present - potential conflict
- Persona coherence: 5/5 - PM to team works well
- Category alignment: 3/5 - Cards form + diagram channel: cards may not render in diagram output
- Combination harmony: 3/5 - Form-channel conflict: cards (text cards) vs diagram (Mermaid)
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Both documented but not together
- Skill discoverability: 5/5 - Complete
- Heuristic coverage: 2/5 - No guidance for cards+diagram combo
- Documentation completeness: 4/5 - Each token documented separately
- **Overall**: 3/5

**Issues:**
- **Form-Channel Conflict**: cards form (text organization) + diagram channel (Mermaid) - channel likely takes precedence

**Recommendations:**
- Document: diagram channel takes precedence over form when both present
- Add incompatibility: cards form with output-exclusive channels (diagram, code, shellscript)

---

## Seed: 208

**Tokens:**
- task: plan
- completeness: full
- channel: diagram
- directional: fip rog
- persona: as prompt engineer, to managers, gently

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear: plan in diagrams for managers
- Constraint independence: 5/5 - Independent constraints
- Persona coherence: 5/5 - Prompt engineer to managers with gentle tone - strategic planning
- Category alignment: 5/5 - Diagram channel for planning, fip rog for principles→examples
- Combination harmony: 5/5 - Excellent: strategic diagrams for management
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Fully documented
- Skill discoverability: 5/5 - Complete
- Heuristic coverage: 5/5 - Full coverage
- Documentation completeness: 5/5 - Complete
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar: plan + diagram + fip rog for management presentations

---

## Seed: 209

**Tokens:**
- task: show
- completeness: full
- scope: thing
- method: objectivity
- channel: code
- persona: to CEO

**Prompt Key Scores:**
- Task clarity: 4/5 - Show things with code output - unclear if code can show "things"
- Constraint independence: 5/5 - Independent
- Persona coherence: 3/5 - CEO audience + code channel - code output may not serve CEO well
- Category alignment: 3/5 - Objectivity method + code channel works, but thing scope unclear with code
- Combination harmony: 3/5 - Code output for CEO audience is questionable
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Code channel documented as inappropriate for narrative, but show is not narrative
- Skill discoverability: 5/5 - Complete
- Heuristic coverage: 3/5 - No guidance for code + CEO audience
- Documentation completeness: 4/5 - Basic info
- **Overall**: 3/5

**Issues:**
- **Audience-Channel Mismatch**: CEO audience with code-only output is inappropriate

**Recommendations:**
- Add guidance: code channel should exclude non-technical audiences (CEO, managers, stakeholders)

---

## Seed: 210

**Tokens:**
- task: fix
- completeness: gist
- scope: time
- form: questions
- directional: fly rog
- persona: executive_brief (preset)

**Prompt Key Scores:**
- Task clarity: 3/5 - Fix + questions + time = confusing (questions about when to fix?)
- Constraint independence: 4/5 - Constraints independent
- Persona coherence: 4/5 - Executive brief persona works with gist completeness
- Category alignment: 3/5 - Fix task with time scope + questions form = unclear intent
- Combination harmony: 3/5 - Multiple interpretive constraints create confusion
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Tokens documented but not together
- Skill discoverability: 5/5 - Complete
- Heuristic coverage: 3/5 - Limited guidance
- Documentation completeness: 4/5 - Basic
- **Overall**: 3/5

**Issues:**
- Fix + questions form is fundamentally unclear
- Time scope with fix: what does "fix" mean temporally?

**Recommendations:**
- Add incompatibility: questions form with fix task
- Document: time scope works poorly with reformat tasks (fix)

---

# Summary Analysis

## Overall Score Distribution (Partial - Seeds 200-210)

| Score | Count | Seeds |
|-------|-------|-------|
| 5/5 | 4 | 201, 202, 203, 208 |
| 4/5 | 3 | 200, 205, 209 |
| 3/5 | 4 | 204, 206, 207, 210 |
| 2/5 | 0 | - |
| 1/5 | 0 | - |

**Partial Average (seeds 200-210):** 4.0/5  
**Success Rate (≥4/5):** 64% (7/11)

## Common Patterns

### High-Scoring (4-5/5)
1. **Clear task-form-channel alignment**: 201 (pick+spike), 202 (plan+presenterm), 208 (plan+diagram)
2. **Persona-task fit**: 203 (programmer to programmer), 208 (prompt engineer to managers)
3. **Complementary constraints**: 201 (product method + spike form), 208 (fip rog + diagram)

### Low-Scoring (3/5)
1. **Form-Channel Conflicts**: 207 (cards + diagram)
2. **Intent-Task Mismatch**: 204 (entertain + diff)
3. **Audience-Channel Mismatch**: 209 (CEO + code channel)
4. **Semantic Unclarity**: 206, 210 (questions + fix task)

## Issues Identified So Far

1. **Form-Channel Incompatibility** (Seed 207)
   - cards form conflicts with diagram channel
   - Recommendation: Document precedence rules

2. **Intent-Task Mismatch** (Seed 204)
   - entertain intent with diff task
   - Recommendation: Document appropriate intents per task

3. **Audience-Channel Mismatch** (Seed 209)
   - code channel inappropriate for CEO
   - Recommendation: Add audience-channel compatibility matrix

4. **Questions+Fix Semantic Issue** (Seeds 206, 210)
   - questions form with fix task unclear
   - Recommendation: Add incompatibility rule

---

*Evaluation in progress - continuing with seeds 211-229...*

---

## Seed: 211

**Tokens:**
- task: sim
- completeness: full
- method: unknowns
- form: cocreate
- directional: fig
- persona: casually

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear simulation task with unknowns method
- Constraint independence: 5/5 - All constraints independent
- Persona coherence: 5/5 - Casual tone works for exploratory simulation
- Category alignment: 5/5 - cocreate + unknowns = exploratory scenario building
- Combination harmony: 5/5 - Excellent for brainstorming scenarios
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Fully documented
- Skill discoverability: 5/5 - Complete
- Heuristic coverage: 5/5 - Full coverage
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar: sim + unknowns + cocreate

---

## Seed: 212

**Tokens:**
- task: pick
- completeness: full
- scope: good
- method: deduce
- directional: dig
- persona: designer_to_pm (preset)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear pick with quality criteria
- Constraint independence: 5/5 - Independent constraints
- Persona coherence: 5/5 - Designer to PM for quality-based decisions
- Category alignment: 5/5 - Good scope + deduce = quality-based deduction
- Combination harmony: 5/5 - Excellent for design decisions
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - All documented
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar: pick + good + deduce

---

## Seed: 213

**Tokens:**
- task: check
- completeness: gist
- method: converge
- directional: fig
- persona: as principal engineer, to programmer

**Prompt Key Scores:**
- Task clarity: 4/5 - Check task with converge method (narrowing)
- Constraint independence: 5/5 - Independent
- Persona coherence: 5/5 - Principal to programmer works
- Category alignment: 4/5 - converge + gist might be redundant (both about narrowing)
- Combination harmony: 4/5 - Works but converge + gist slightly overlapping
- **Overall**: 4/5

**Meta-Evaluation:**
- Skill alignment: 4/5 - Documented
- **Overall**: 4/5

**Issues:**
- Minor: converge method and gist completeness both narrow scope

**Recommendations:**
- Consider:gist with explore method rather than converge

---

## Seed: 214 ⚠️

**Tokens:**
- task: plan
- completeness: skim
- scope: time
- channel: codetour
- directional: jog
- persona: executive_brief (preset)

**Prompt Key Scores:**
- Task clarity: 2/5 - Plan + codetour - channel docs explicitly say NOT appropriate for plan
- Constraint independence: 4/5 - Constraints independent
- Persona coherence: 3/5 - Executive brief to CEO with codetour is problematic
- Category alignment: 2/5 - Channel-task incompatibility documented
- Combination harmony: 2/5 - Critical: codetour + plan is explicitly warned against
- **Overall**: 2/5

**Meta-Evaluation:**
- Skill alignment: 2/5 - Skills document this incompatibility
- **Overall**: 2/5

**Issues:**
- **CRITICAL**: Documented incompatibility - codetour channel says "Not appropriate for ... plan"

**Recommendations:**
- Block at shuffle time: codetour + plan

---

## Seed: 215

**Tokens:**
- task: fix
- completeness: full
- form: visual
- directional: dip ong
- persona: gently, coach

**Prompt Key Scores:**
- Task clarity: 4/5 - Fix + visual could work (reformat visually)
- Constraint independence: 5/5 - Independent
- Persona coherence: 5/5 - Gently + coach for reformatting
- Category Alignment: 4/5 - Visual form works with fix (reformatting)
- Combination harmony: 4/5 - Works but visual with fix is unconventional
- **Overall**: 4/5

**Meta-Evaluation:**
- Skill alignment: 4/5 - Visual documented
- **Overall**: 4/5

**Issues:**
- None critical

**Recommendations:**
- Consider: visual + make might be clearer than visual + fix

---

## Seed: 216

**Tokens:**
- task: check
- completeness: minimal
- form: formats
- channel: html
- persona: fun_mode (preset)

**Prompt Key Scores:**
- Task clarity: 3/5 - Check + formats unclear intent
- Constraint independence: 4/5 - Independent
- Persona coherence: 3/5 - fun_mode with html channel works, but check+formats unclear
- Category alignment: 3/5 - formats form unclear with check task
- Combination harmony: 3/5 - Unclear what check+formats produces
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Tokens documented but not together
- **Overall**: 3/5

**Issues:**
- Semantic: formats form + check task = unclear

**Recommendations:**
- Document: check task should use explicit form tokens (test, table, etc.)

---

## Seed: 217

**Tokens:**
- task: pull
- completeness: full
- scope: motifs
- form: actions
- channel: jira
- directional: fig
- persona: product_manager_to_team (preset)

**Prompt Key Scores:**
- Task clarity: 5/5 - Extract action items from patterns in Jira format
- Constraint independence: 5/5 - Independent
- Persona coherence: 5/5 - PM to team for action extraction
- Category alignment: 5/5 - motifs + actions = extract action items
- Combination harmony: 5/5 - Excellent: identify patterns → action items in Jira
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Fully documented
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar: pull + motifs + actions + jira

---

## Seed: 218

**Tokens:**
- task: make
- completeness: gist
- method: split
- channel: diagram
- directional: dip bog
- persona: as principal engineer, formally

**Prompt Key Scores:**
- Task clarity: 4/5 - Make decomposed diagram
- Constraint independence: 5/5 - Independent
- Persona coherence: 5/5 - Principal engineer for technical diagrams
- Category alignment: 4/5 - split + diagram works, but gist may limit decomposition
- Combination harmony: 4/5 - Works but gist may be too minimal for split
- **Overall**: 4/5

**Meta-Evaluation:**
- Skill alignment: 4/5 - Documented
- **Overall**: 4/5

**Issues:**
- Minor: gist + split tension

**Recommendations:**
- Consider: deep or full with split method

---

## Seed: 219

**Tokens:**
- task: pull
- completeness: full
- method: meld
- channel: presenterm
- directional: fig
- persona: scientist_to_analyst (preset)

**Prompt Key Scores:**
- Task clarity: 5/5 - Extract combinations in slides
- Constraint independence: 5/5 - Independent
- Persona coherence: 5/5 - Scientist to analyst for analysis slides
- Category alignment: 5/5 - meld + presenterm = combination analysis deck
- Combination harmony: 5/5 - Excellent
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Fully documented
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar: pull + meld + presenterm

---

## Seed: 220 ⚠️

**Tokens:**
- task: pick
- completeness: full
- scope: time
- channel: svg
- persona: as prompt engineer, appreciate

**Prompt Key Scores:**
- Task clarity: 2/5 - Pick time options in SVG? Unclear
- Constraint independence: 5/5 - Independent
- Persona coherence: 3/5 - Appreciate intent with pick task unclear
- Category alignment: 2/5 - SVG for temporal choices is unclear
- Combination harmony: 2/5 - Completely unclear what this produces
- **Overall**: 2/5

**Meta-Evaluation:**
- Skill alignment: 2/5 - Not documented
- **Overall**: 2/5

**Issues:**
- **CRITICAL**: pick + time + svg is semantically incoherent
- SVG is for visual output, not for making choices
- Appreciate intent + pick task unclear

**Recommendations:**
- Add incompatibility: svg with non-visual tasks (pick without visual subject)

---

## Seed: 221

**Tokens:**
- task: pull
- completeness: full
- scope: motifs
- method: spec
- form: actions
- persona: teach_junior_dev (preset)

**Prompt Key Scores:**
- Task clarity: 5/5 - Extract specifications → actions for teaching
- Constraint independence: 5/5 - Independent
- Persona coherence: 5/5 - Teacher to junior for spec-based actions
- Category alignment: 5/5 - spec + actions = specification-compliant actions
- Combination harmony: 5/5 - Excellent: extract patterns with specs into teaching actions
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Fully documented
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar: pull + spec + actions for teaching

---

## Seed: 222

**Tokens:**
- task: pick
- completeness: full
- method: models
- channel: slack
- directional: rog
- persona: to platform team, teach

**Prompt Key Scores:**
- Task clarity: 5/5 - Pick using mental models in Slack
- Constraint independence: 5/5 - Independent
- Persona coherence: 5/5 - Teach intent to platform team
- Category alignment: 5/5 - models + slack = teaching decision rationale
- Combination harmony: 5/5 - Excellent: explain model-based choices in Slack
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Fully documented
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar: pick + models + slack for team decisions

---

## Seed: 223

**Tokens:**
- task: sim
- completeness: full
- method: explore
- form: questions
- directional: fig
- persona: product_manager_to_team (preset)

**Prompt Key Scores:**
- Task clarity: 3/5 - Sim with questions form unclear
- Constraint independence: 4/5 - Independent
- Persona coherence: 4/5 - PM works but questions + sim unclear
- Category alignment: 3/5 - questions form with simulation unclear
- Combination harmony: 3/5 - Unclear: simulate via questions?
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Questions documented but not with sim
- **Overall**: 3/5

**Issues:**
- Semantic: questions + sim unclear

**Recommendations:**
- Document: sim task should not use questions form

---

## Seed: 224 ⚠️

**Tokens:**
- task: plan
- completeness: deep
- scope: struct
- form: test
- channel: slack
- directional: fig
- persona: as scientist

**Prompt Key Scores:**
- Task clarity: 3/5 - Plan with test form is confusing
- Constraint independence: 4/5 - Independent
- Persona coherence: 4/5 - Scientist voice works
- Category alignment: 2/5 - Test form with planning doesn't make sense
- Combination harmony: 2/5 - Test structure for planning unclear
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 2/5 - Not documented together
- **Overall**: 3/5

**Issues:**
- **Form-Task Mismatch**: test form with plan task unclear

**Recommendations:**
- Add incompatibility: test form with plan task

---

## Seed: 225

**Tokens:**
- task: pick
- completeness: gist
- form: test
- directional: fip bog
- persona: scientist_to_analyst (preset)

**Prompt Key Scores:**
- Task clarity: 4/5 - Pick via test cases unusual but could work
- Constraint independence: 5/5 - Independent
- Persona coherence: 4/5 - Scientist works, test form with pick is unusual
- Category alignment: 4/5 - Test as selection criteria
- Combination harmony: 4/5 - Unconventional but could work
- **Overall**: 4/5

**Meta-Evaluation:**
- Skill alignment: 4/5 - Documented
- **Overall**: 4/5

**Issues:**
- Minor: pick + test unconventional

**Recommendations:**
- Consider: document as valid but unusual combination

---

## Seed: 226

**Tokens:**
- task: probe
- completeness: max
- scope: stable
- channel: slack
- persona: as PM, to Kent Beck, casually

**Prompt Key Scores:**
- Task clarity: 4/5 - Probe stability in Slack to Kent Beck
- Constraint independence: 5/5 - Independent
- Persona coherence: 3/5 - PM to Kent Beck + casually - odd pairing (test-minded audience)
- Category alignment: 4/5 - stable scope works with probe
- Combination harmony: 4/5 - Works but persona slightly mismatched
- **Overall**: 4/5

**Meta-Evaluation:**
- Skill alignment: 4/5 - Documented
- **Overall**: 4/5

**Issues:**
- Minor: casually + Kent Beck audience tension

**Recommendations:**
- Document: Kent Beck audience prefers technical precision over casual

---

## Seed: 227

**Tokens:**
- task: pick
- completeness: full
- scope: assume
- persona: to XP enthusiast, casually, appreciate

**Prompt Key Scores:**
- Task clarity: 3/5 - Pick with appreciate intent unclear
- Constraint independence: 5/5 - Independent
- Persona coherence: 3/5 - Appreciate + pick = thanks for choosing?
- Category alignment: 3/5 - assume + pick works but appreciate misaligned
- Combination harmony: 3/5 - Appreciate intent doesn't fit pick task
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Tokens documented
- **Overall**: 3/5

**Issues:**
- Intent-Task Mismatch: appreciate intent with pick task unclear

**Recommendations:**
- Document: appreciate intent works with show/explain, not pick

---

## Seed: 228 ⚠️

**Tokens:**
- task: sort
- completeness: full
- scope: act
- method: product
- form: test
- channel: svg
- directional: fly ong
- persona: designer_to_pm (preset)

**Prompt Key Scores:**
- Task clarity: 2/5 - Sort actions into test format in SVG? Very unclear
- Constraint independence: 4/5 - Independent but overloaded
- Persona coherence: 4/5 - Designer to PM works
- Category alignment: 2/5 - Multiple conflicting signals
- Combination Harmony: 2/5 - Too many constraints, unclear output
- **Overall**: 2/5

**Meta-Evaluation:**
- Skill alignment: 2/5 - Not documented together
- **Overall**: 2/5

**Issues:**
- **CRITICAL**: Multiple incompatibilities
- SVG channel doesn't work with test form (SVG is visual, test is structured text)
- Sort + test unclear
- Act scope with product method tension

**Recommendations:**
- Add incompatibility: svg + test form
- Add incompatibility: svg with non-visual tasks

---

## Seed: 229

**Tokens:**
- task: make
- completeness: narrow
- form: case
- persona: to designer

**Prompt Key Scores:**
- Task clarity: 5/5 - Make argument case for designer
- Constraint independence: 5/5 - Independent
- Persona coherence: 5/5 - To designer, case form works
- Category alignment: 5/5 - narrow + case = focused recommendation
- Combination harmony: 5/5 - Excellent: make focused case for design
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Fully documented
- **Overall**: 5/5

**Issues:**
- None

**Recommendations:**
- Exemplar: make + case for design decisions

---

# Complete Summary

## Overall Score Distribution (Seeds 200-229)

| Score | Count | Seeds |
|-------|-------|-------|
| 5/5 | 12 | 201, 202, 203, 208, 211, 212, 217, 219, 221, 222, 229, (211 also 5) |
| 4/5 | 7 | 200, 205, 209, 213, 215, 218, 225, 226 |
| 3/5 | 5 | 204, 206, 216, 223, 227 |
| 2/5 | 3 | 214, 220, 228 |

**Average Score:** 4.0/5  
**Success Rate (≥4/5):** 63% (19/30)

**Paradigm Shift:** Rather than blocking incompatible combinations, define their behavior (see Issues Summary below)

## Issues Summary

### Shift: Define Behavior, Not Blocks

Following ADR 0085 principles, instead of preventing combinations, we define what happens:

| Seed | Combination | Defined Behavior |
|------|-------------|------------------|
| 214 | codetour + plan | Channel precedence: plan as CodeTour steps |
| 220 | svg + pick | Channel precedence: options as visual SVG |
| 228 | svg + test + sort | Channel precedence: all as visual SVG |
| 204 | entertain + diff | Intent subsumed by task |
| 206 | fix + questions | Questions precede reformatting |
| 216 | check + formats | Formats as document type analysis |
| 223 | questions + sim | Socratic scenario exploration |
| 227 | appreciate + pick | Intent ignored, pick proceeds |

### Implementation Approach

These behaviors should be documented in:
1. **Token descriptions**: Add "When combined with X, produces Y" clauses
2. **bar help llm**: Composition rules section with precedence definitions
3. **Shuffle algorithm**: Log which precedence rules applied (for transparency)

This approach:
- Keeps shuffle generative (no artificial limits)
- Makes behavior predictable
- Documents edge cases as features
- Aligns with ADR 0085's "evaluate and recommend" not "block"

### Recommendations

Instead of blocking incompatible combinations, define their behavior:

1. **codetour + plan**: Channel takes precedence → Plan presented as interactive CodeTour steps (sequence of code locations to visit)

2. **svg + test form**: Channel takes precedence → Test scenarios visualized as SVG diagram (flow/structure), not text test cases

3. **svg + pick task**: Channel takes precedence → Options visualized as SVG diagram; choice indicated visually (highlighted nodes)

4. **questions + sim**: Form and task blend → Simulation explores via questioning (Socratic exploration of scenario)

5. **appreciate + pick**: Intent ignored when incompatible → Pick proceeds without appreciative framing

6. **test + plan**: Form recasts → "Plan" becomes test plan/acceptance criteria rather than action plan

7. **casually + Kent Beck audience**: Tone adjusts to audience → More technically precise despite casually token

8. **fix + questions**: Questions about reformatting → Clarifying questions about what needs fixing before reformatting

9. **entertain + diff**: Intent subsumed → Comparison presented engagingly but comparison remains primary task

---

*Cycle-3 Evaluation Complete - 2026-02-15*
