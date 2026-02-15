# ADR 0085 Cycle-2 Shuffle Evaluation: Complete Analysis

**Evaluation Date:** 2026-02-15  
**Seeds Evaluated:** 121-140  
**Evaluator:** Claude Code (AI Agent)  
**Methodology:** ADR 0083 Prompt Key Criteria + Bar Skills Meta-Evaluation  

---

## Seed: 121

**Tokens:**
- task: make
- completeness: deep
- scope: good
- method: verify
- form: test
- directional: fip rog
- persona: designer_to_pm (as designer, to product manager, directly)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "make" task with explicit content creation goal
- Constraint independence: 5/5 - All constraints (deep, good, verify, test, fip rog) operate independently without overlap
- Persona coherence: 5/5 - Designer-to-PM persona aligns perfectly with "good" scope (quality judgment) and "verify" method (rigorous analysis)
- Category alignment: 5/5 - Strong alignment: designer evaluating quality criteria through falsification, outputting test cases
- Combination harmony: 5/5 - Excellent synthesis: designer creates test cases (form) verifying quality claims (scope) through falsification (method) with deep completeness
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - "verify" method explicitly documented; "test" form well-defined
- Skill discoverability: 4/5 - All tokens discoverable via bar help system
- Heuristic coverage: 5/5 - Covers falsification, test case structure, directional movement
- Documentation completeness: 5/5 - All constraints have clear descriptions in catalog
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- Consider this combination as a "reference standard" for high-quality prompt design
- The designer_to_pm + verify + test combination could be highlighted in documentation as an exemplar

---

## Seed: 122

**Tokens:**
- task: fix
- completeness: full
- method: mod
- form: contextualise
- channel: gherkin
- directional: fip ong
- persona: fun_mode (casually)

**Prompt Key Scores:**
- Task clarity: 4/5 - Clear "fix" task, though the fun_mode persona seems mismatched with gherkin channel
- Constraint independence: 4/5 - Constraints operate independently, but "contextualise" form with gherkin channel creates ambiguity
- Persona coherence: 2/5 - Fun_mode with casual tone contradicts gherkin channel's structured, formal output requirement
- Category alignment: 3/5 - Method (mod) and form (contextualise) align, but channel-persona mismatch weakens overall alignment
- Combination harmony: 2/5 - Significant tension: fun_mode persona asking for casual output in rigid gherkin format
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Gherkin channel has clear inappropriateness warnings but lacks automatic incompatibility detection
- Skill discoverability: 4/5 - All tokens discoverable
- Heuristic coverage: 3/5 - Catalog notes gherkin inappropriate for non-behavioral tasks, but doesn't flag persona-channel conflicts
- Documentation completeness: 4/5 - Channel documentation mentions inappropriateness for certain tasks but not persona conflicts
- **Overall**: 3/5

**Issues:**
- **Persona-Channel Conflict:** fun_mode's casual tone directly contradicts gherkin's rigid structural requirements
- **Task-Channel Fit:** fix task is borderline for gherkin (more appropriate for check/plan/make)
- **Form-Channel Ambiguity:** contextualise form (adding context without rewriting) conflicts with gherkin's requirement for pure Gherkin output

**Recommendations:**
- Add persona-channel compatibility matrix to catalog
- Consider excluding fun_mode from channel-heavy prompts
- Clarify whether "contextualise" form can work with output-only channels like gherkin

---

## Seed: 123

**Tokens:**
- task: pull
- completeness: max
- method: diagnose
- form: table
- channel: codetour
- persona: appreciate (to team, casually)

**Prompt Key Scores:**
- Task clarity: 3/5 - Clear "pull" task, but "appreciate" intent with "diagnose" method creates confusion
- Constraint independence: 3/5 - Constraints are independent, but method-persona conflict exists
- Persona coherence: 2/5 - Appreciate intent (express thanks) conflicts with diagnose method (seek problems)
- Category alignment: 3/5 - Max completeness + diagnose align for thorough problem-finding, but appreciate intent undermines diagnostic stance
- Combination harmony: 2/5 - Tension: diagnosing problems while expressing appreciation creates mixed signals
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Diagnose method well-documented, but no guidance on intent-method compatibility
- Skill discoverability: 4/5 - All tokens discoverable
- Heuristic coverage: 3/5 - Missing heuristics for intent-method conflicts
- Documentation completeness: 3/5 - Intent descriptions don't discuss compatibility with methods
- **Overall**: 3/5

**Issues:**
- **Intent-Method Conflict:** "appreciate" intent (positive regard) contradicts "diagnose" method (problem-finding)
- **Channel Appropriateness:** codetour appropriate for pull task, but table form may not translate well to JSON tour format
- **Persona Completeness:** No voice specified in persona

**Recommendations:**
- Add intent-method compatibility guidance to documentation
- Consider marking certain intent-method pairs as incompatible
- Document how form (table) interacts with channel (codetour)

---

## Seed: 124

**Tokens:**
- task: probe
- completeness: full
- scope: motifs
- channel: jira
- directional: dip ong
- persona: peer_engineer_explanation (as programmer, to programmer)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "probe" task analyzing structure
- Constraint independence: 5/5 - All constraints operate independently
- Persona coherence: 5/5 - Peer engineer explanation aligns perfectly with probe task and motifs scope (pattern identification)
- Category alignment: 5/5 - Strong alignment: programmer analyzing code patterns, outputting in Jira format for team consumption
- Combination harmony: 5/5 - Excellent synthesis: peer engineer probes motifs in code, starting from concrete examples (dip ong), formatted for Jira
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - All skills well-documented and appropriate
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 5/5 - Comprehensive coverage of analysis patterns
- Documentation completeness: 5/5 - Jira channel clearly documented for team communication
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- This combination exemplifies effective use of directional tokens (dip ong) with analysis tasks
- Consider as reference for peer_engineer persona effectiveness

---

## Seed: 125

**Tokens:**
- task: sort
- completeness: full
- method: product
- form: socratic
- persona: to stream aligned team (formally)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "sort" task for categorization
- Constraint independence: 5/5 - Constraints operate independently
- Persona coherence: 4/5 - Product method aligns well with stream-aligned team audience; formal tone fits team communication
- Category alignment: 5/5 - Strong alignment: sorting items using product lens, asking socratic questions to team
- Combination harmony: 5/5 - Product method (features, user needs) + socratic form (questions) creates effective prioritization dialogue
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Product method and socratic form well-documented
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 5/5 - Good coverage of team collaboration patterns
- Documentation completeness: 5/5 - Stream-aligned team audience well-defined
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- This combination could serve as template for team prioritization exercises
- Socratic form with product method creates excellent discovery process

---

## Seed: 126

**Tokens:**
- task: fix
- completeness: deep
- scope: motifs
- method: unknowns
- form: table
- channel: svg
- persona: product_manager_to_team (as PM, to team, kindly)

**Prompt Key Scores:**
- Task clarity: 3/5 - Clear "fix" task, but SVG output for reformatting task is unusual
- Constraint independence: 4/5 - Constraints independent, though channel-form interaction unclear
- Persona coherence: 4/5 - PM persona aligns with scope (motifs/patterns) and method (unknowns exploration)
- Category alignment: 3/5 - Fix task + SVG channel mismatch; table form may not render well in SVG
- Combination harmony: 2/5 - Significant friction: fix task (reformat) + SVG channel (graphics) + table form creates confusing output expectations
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - SVG channel documented but lacks clear task compatibility guidance
- Skill discoverability: 4/5 - All tokens discoverable
- Heuristic coverage: 2/5 - Missing heuristics for channel-task compatibility
- Documentation completeness: 3/5 - SVG channel description doesn't address table form compatibility
- **Overall**: 3/5

**Issues:**
- **Task-Channel Mismatch:** Fix task typically outputs text/code; SVG expects graphics
- **Form-Channel Conflict:** Table form (Markdown) doesn't naturally translate to SVG
- **Completeness-Task Fit:** "Deep" completeness with "fix" task may be overkill for simple reformatting

**Recommendations:**
- Define clear task-channel compatibility matrix
- Add warnings when table form paired with non-text channels
- Consider whether "fix" should exclude visual channels like SVG

---

## Seed: 127

**Tokens:**
- task: probe
- completeness: narrow
- scope: good
- method: risks
- form: indirect
- channel: gherkin
- persona: (none)

**Prompt Key Scores:**
- Task clarity: 4/5 - Clear "probe" task, but missing persona reduces clarity
- Constraint independence: 4/5 - Constraints independent, though narrow completeness + gherkin may conflict
- Persona coherence: 3/5 - No persona specified; task and constraints stand alone but lack voice
- Category alignment: 3/5 - Probe + risks + good scope align, but gherkin channel inappropriate for probing analysis
- Combination harmony: 2/5 - Significant issues: probing analysis (qualitative) in gherkin format (behavioral scenarios) + indirect form creates confusion
- **Overall**: 3/5

**Meta-Evaluation:**
- Skill alignment: 3/5 - Gherkin channel has inappropriateness warnings but still appears in probe task
- Skill discoverability: 4/5 - All tokens discoverable
- Heuristic coverage: 2/5 - Missing automatic incompatibility detection for gherkin with non-behavioral tasks
- Documentation completeness: 3/5 - Channel documentation warns about inappropriateness but doesn't prevent selection
- **Overall**: 3/5

**Issues:**
- **Channel-Task Incompatibility:** Gherkin explicitly inappropriate for probe task per channel documentation
- **Missing Persona:** No persona leaves prompt without voice/audience guidance
- **Form-Channel Tension:** Indirect form (background → conclusion) conflicts with gherkin's scenario structure

**Recommendations:**
- Implement hard constraints preventing gherkin with non-behavioral tasks
- Require persona for all prompts (or provide default)
- Review why gherkin appeared in shuffle for probe task despite incompatibility

---

## Seed: 128

**Tokens:**
- task: diff
- completeness: max
- persona: scientist_to_analyst (as scientist, to analyst, formally)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "diff" comparison task
- Constraint independence: 5/5 - Single constraint (max completeness) is clear
- Persona coherence: 5/5 - Scientist to analyst perfectly suits diff task requiring rigor and structure
- Category alignment: 5/5 - Strong alignment: scientist comparing subjects rigorously for analyst consumption
- Combination harmony: 5/5 - Minimal but effective: max completeness ensures thorough comparison, scientist persona adds rigor
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Diff task and scientist persona well-documented
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 4/5 - Could benefit from method or scope token for richer analysis
- Documentation completeness: 5/5 - Clear documentation for all tokens
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- Demonstrates effectiveness of minimal, high-quality token combinations
- Consider as example of when fewer tokens create clearer prompts

---

## Seed: 129

**Tokens:**
- task: make
- completeness: full
- method: product
- channel: sketch
- persona: persuade (formally)

**Prompt Key Scores:**
- Task clarity: 4/5 - Clear "make" task, but persuade intent without audience is unclear
- Constraint independence: 5/5 - Constraints operate independently
- Persona coherence: 3/5 - Persuade intent lacks voice and audience; formal tone without context
- Category alignment: 4/5 - Make + product + sketch aligns for creating product diagrams
- Combination harmony: 4/5 - Good synthesis: creating product-focused diagrams with persuasive intent
- **Overall**: 4/5

**Meta-Evaluation:**
- Skill alignment: 4/5 - Sketch channel well-documented for D2 diagrams
- Skill discoverability: 4/5 - All tokens discoverable
- Heuristic coverage: 4/5 - Could benefit from scope token
- Documentation completeness: 4/5 - Sketch channel has excellent syntax documentation
- **Overall**: 4/5

**Issues:**
- **Incomplete Persona:** Persuade intent without audience or voice leaves persona underspecified
- **Intent Clarity:** Persuasive diagram creation is clear, but toward what end is unspecified

**Recommendations:**
- Consider requiring audience when intent token is used
- Document common make + product + sketch use cases

---

## Seed: 130

**Tokens:**
- task: sim
- completeness: gist
- scope: fail
- form: log
- persona: as PM (directly)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "sim" task playing out failure scenarios
- Constraint independence: 5/5 - All constraints operate independently
- Persona coherence: 5/5 - PM voice with direct tone suits failure simulation and log format
- Category alignment: 5/5 - Excellent alignment: PM simulating failure scenarios in concise log format
- Combination harmony: 5/5 - Perfect synthesis: gist completeness keeps log brief, fail scope focuses on breakdowns, PM provides stakeholder perspective
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Sim task, fail scope, and log form well-documented
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 5/5 - Comprehensive scenario coverage
- Documentation completeness: 5/5 - Log form clearly defined
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- This combination exemplifies effective use of scope tokens (fail) with simulation
- PM + fail + log could be documented as standard risk assessment pattern

---

## Seed: 131

**Tokens:**
- task: plan
- completeness: full
- scope: assume
- method: simulation
- form: variants
- directional: dip ong
- persona: designer_to_pm (as designer, to product manager, directly)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "plan" task with rich constraint set
- Constraint independence: 5/5 - All constraints operate independently
- Persona coherence: 5/5 - Designer to PM aligns perfectly with planning task and assumption analysis
- Category alignment: 5/5 - Excellent alignment: designer creating plan variants, examining assumptions, simulating outcomes for PM
- Combination harmony: 5/5 - Outstanding synthesis: plan + assume + simulation + variants + dip ong creates comprehensive planning methodology
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - All skills well-documented and complementary
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 5/5 - Comprehensive planning methodology coverage
- Documentation completeness: 5/5 - Variants form and simulation method excellently documented
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- This combination represents a "gold standard" for planning prompts
- Document as exemplar for plan task usage
- The assume scope + simulation method pairing is particularly powerful

---

## Seed: 132

**Tokens:**
- task: fix
- completeness: max
- channel: codetour
- directional: fly ong
- persona: to managers

**Prompt Key Scores:**
- Task clarity: 3/5 - Clear "fix" task, but codetour for managers is questionable
- Constraint independence: 4/5 - Constraints independent, though directional may not fit fix task
- Persona coherence: 2/5 - Managers audience with codetour channel (code navigation) is mismatched
- Category alignment: 2/5 - Fix + codetour aligns for code refactoring, but managers audience doesn't fit code tours
- Combination harmony: 2/5 - Significant tension: codetour outputs code tours for... managers? Fly ong (abstract→concrete) with fix task is awkward
- **Overall**: 2/5

**Meta-Evaluation:**
- Skill alignment: 2/5 - Codetour channel has audience mismatch not caught by system
- Skill discoverability: 4/5 - All tokens discoverable
- Heuristic coverage: 2/5 - Missing audience-channel compatibility heuristics
- Documentation completeness: 3/5 - Codetour documents appropriate tasks but not appropriate audiences
- **Overall**: 2/5

**Issues:**
- **Audience-Channel Mismatch:** Codetour is for developers navigating code, not managers
- **Directional-Task Fit:** Fly ong (abstract patterns → concrete actions) doesn't align well with fix task (reformat)
- **Completeness Overkill:** Max completeness with fix task may be excessive

**Recommendations:**
- Add audience-channel compatibility matrix
- Codetour should be restricted to technical audiences (programmers, team)
- Review directional token appropriateness for each task type

---

## Seed: 133

**Tokens:**
- task: make
- completeness: full
- scope: fail
- form: rewrite
- channel: gherkin
- persona: executive_brief (as programmer, to CEO, directly)

**Prompt Key Scores:**
- Task clarity: 2/5 - Make task with rewrite form is semantically incoherent per form documentation
- Constraint independence: 3/5 - Form-task conflict is documented but combination still generated
- Persona coherence: 3/5 - Executive brief to CEO with programmer voice creates tension
- Category alignment: 1/5 - Multiple conflicts: make+rewrite (documented incoherent), fail scope with CEO audience, gherkin with make task
- Combination harmony: 1/5 - Critical issues: documented semantic incoherence, inappropriate channel for task, persona-audience mismatch
- **Overall**: 1/5

**Meta-Evaluation:**
- Skill alignment: 1/5 - Rewrite form documentation explicitly warns against pairing with make, yet combination was generated
- Skill discoverability: 4/5 - All tokens discoverable
- Heuristic coverage: 1/5 - Critical failure: documented incompatibility not enforced
- Documentation completeness: 2/5 - While incompatibility is documented, system didn't prevent selection
- **Overall**: 1/5

**Issues:**
- **CRITICAL: Documented Semantic Incoherence:** Rewrite form docs state: "Pairing with `make` is semantically incoherent: `make` implies creating from nothing while `rewrite` implies transforming existing content"
- **Channel Inappropriateness:** Gherkin for make task is inappropriate per channel docs
- **Persona-Audience Tension:** Programmer voice to CEO in executive brief persona is awkward
- **Scope-Audience Mismatch:** Fail scope (breakdowns, edge cases) with CEO audience (business impact focus) misaligned

**Recommendations:**
- **URGENT:** Implement hard constraint preventing documented incompatible pairs (make+rewrite)
- Add task-form compatibility validation
- Review gherkin channel appropriateness for all tasks
- Consider persona-audience compatibility validation

---

## Seed: 134

**Tokens:**
- task: sim
- completeness: gist
- form: socratic
- channel: shellscript
- directional: fly ong
- persona: teach (as programmer, to programmer)

**Prompt Key Scores:**
- Task clarity: 2/5 - Sim task (scenario) with shellscript channel (executable code) is inappropriate per channel docs
- Constraint independence: 3/5 - Channel-task incompatibility documented but not enforced
- Persona coherence: 4/5 - Teach intent with programmer voice/audience aligns well
- Category alignment: 2/5 - Socratic form (questions) with shellscript channel (code output) conflicts; fly ong with simulation awkward
- Combination harmony: 1/5 - Critical conflict: narrative simulation task forced into shellscript format with socratic questioning
- **Overall**: 2/5

**Meta-Evaluation:**
- Skill alignment: 2/5 - Shellscript channel explicitly inappropriate for sim tasks per documentation
- Skill discoverability: 4/5 - All tokens discoverable
- Heuristic coverage: 1/5 - Documented incompatibility (shellscript for sim) not prevented
- Documentation completeness: 2/5 - Clear documentation exists but not enforced
- **Overall**: 2/5

**Issues:**
- **Channel-Task Incompatibility:** Shellscript channel docs state: "Not appropriate for narrative tasks (`sim`, `probe`)"
- **Form-Channel Conflict:** Socratic form (asking questions) incompatible with shellscript channel (code output)
- **Directional-Task Mismatch:** Fly ong (abstract→concrete→extend) doesn't align with simulation over time

**Recommendations:**
- **URGENT:** Implement hard constraint preventing shellscript with sim/probe tasks
- Add form-channel compatibility validation
- Review all channel inappropriateness warnings and enforce them

---

## Seed: 135

**Tokens:**
- task: make
- completeness: full
- method: branch
- persona: product_manager_to_team (as PM, to team, kindly)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "make" task with branching reasoning
- Constraint independence: 5/5 - All constraints operate independently
- Persona coherence: 5/5 - PM persona aligns perfectly with branch method (exploring options) and team audience
- Category alignment: 5/5 - Strong alignment: PM creating content while exploring multiple reasoning paths for team
- Combination harmony: 5/5 - Excellent synthesis: PM explores branches, kindly presents options to team with full completeness
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Branch method well-documented for parallel reasoning
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 5/5 - Good coverage of decision-making patterns
- Documentation completeness: 5/5 - Clear documentation for all tokens
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- This combination exemplifies effective use of method tokens (branch) with creation tasks
- PM + branch + team could be documented as standard option-exploration pattern

---

## Seed: 136

**Tokens:**
- task: diff
- completeness: deep
- channel: gherkin
- persona: teach (as writer, kindly)

**Prompt Key Scores:**
- Task clarity: 2/5 - Diff task with gherkin channel is inappropriate per channel docs (no behavioral subject)
- Constraint independence: 4/5 - Constraints independent despite channel-task mismatch
- Persona coherence: 4/5 - Teach intent with writer voice and kind tone aligns well
- Category alignment: 2/5 - Diff task (comparison) doesn't involve system behavior; gherkin inappropriate
- Combination harmony: 2/5 - Significant mismatch: comparing subjects in Gherkin scenario format is forced
- **Overall**: 2/5

**Meta-Evaluation:**
- Skill alignment: 2/5 - Gherkin channel docs explicitly state inappropriate for diff without behavioral subject
- Skill discoverability: 4/5 - All tokens discoverable
- Heuristic coverage: 1/5 - Documented incompatibility not enforced
- Documentation completeness: 3/5 - Warnings exist but aren't enforced
- **Overall**: 2/5

**Issues:**
- **Channel-Task Incompatibility:** Gherkin docs state: "Not appropriate for tasks that don't involve system behavior: `sort`, `sim`, `probe`, `diff` (without behavioral subject)"
- **Missing Subject:** No subject provided, so behavioral context unavailable

**Recommendations:**
- **URGENT:** Enforce gherkin channel restrictions programmatically
- Require subject when gherkin channel used with borderline tasks
- Review all channel appropriateness documentation for enforceability

---

## Seed: 137

**Tokens:**
- task: probe
- completeness: full
- scope: mean
- method: systemic
- channel: adr
- persona: scientist_to_analyst (as scientist, to analyst, formally)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "probe" task analyzing meaning systemically
- Constraint independence: 5/5 - All constraints operate independently
- Persona coherence: 5/5 - Scientist to analyst aligns perfectly with systemic analysis and ADR format
- Category alignment: 5/5 - Excellent alignment: scientist probing meaning through systemic lens, outputting ADR
- Combination harmony: 5/5 - Outstanding synthesis: systemic analysis of meaning documented as architecture decision
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Systemic method and ADR channel well-documented
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 5/5 - Comprehensive analysis pattern coverage
- Documentation completeness: 5/5 - ADR channel format clearly specified
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- This combination exemplifies sophisticated analysis workflow
- Document as reference for probe + systemic + adr pattern
- Scientist_to_analyst + adr is powerful for technical documentation

---

## Seed: 138

**Tokens:**
- task: sort
- completeness: skim
- scope: act
- form: test
- channel: html
- directional: bog
- persona: teach (as programmer, to team, kindly)

**Prompt Key Scores:**
- Task clarity: 4/5 - Clear "sort" task, though test form with sort is unusual
- Constraint independence: 4/5 - Constraints independent, though form-task fit is questionable
- Persona coherence: 5/5 - Teach intent with programmer voice, team audience, kind tone aligns well
- Category alignment: 4/5 - Sort + act scope (tasks/operations) + test form creates interesting categorization test cases
- Combination harmony: 4/5 - Good synthesis: sorting activities into testable categories in HTML format with reflection
- **Overall**: 4/5

**Meta-Evaluation:**
- Skill alignment: 4/5 - Test form and HTML channel documented, though sort+test combination rare
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 4/5 - Could use guidance on sort+test pairing
- Documentation completeness: 4/5 - HTML channel well-documented for semantic markup
- **Overall**: 4/5

**Issues:**
- **Form-Task Novelty:** Test form with sort task is uncommon; sorting test cases is valid but unusual
- **Completeness-Form Fit:** Skim completeness with test form may produce incomplete test coverage

**Recommendations:**
- Document sort + test use case for categorization validation
- Consider whether skim completeness is appropriate for test form
- Explore bog directional with sort tasks

---

## Seed: 139

**Tokens:**
- task: pick
- completeness: full
- method: spec
- form: recipe
- persona: scientist_to_analyst (as scientist, to analyst, formally)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "pick" task choosing from alternatives
- Constraint independence: 5/5 - All constraints operate independently
- Persona coherence: 5/5 - Scientist to analyst aligns perfectly with spec method (defining criteria) and recipe form
- Category alignment: 5/5 - Excellent alignment: scientist defining selection criteria (spec), presenting as recipe with mini-language
- Combination harmony: 5/5 - Perfect synthesis: pick + spec + recipe creates decision methodology with clear criteria and notation
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Spec method and recipe form well-documented
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 5/5 - Comprehensive decision-making coverage
- Documentation completeness: 5/5 - Recipe form clearly describes mini-language pattern
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- This combination exemplifies decision-making workflow
- Document as reference for pick + spec + recipe pattern
- Consider as standard for selection/prioritization tasks

---

## Seed: 140

**Tokens:**
- task: pull
- completeness: deep
- persona: designer_to_pm (as designer, to product manager, directly)

**Prompt Key Scores:**
- Task clarity: 5/5 - Clear "pull" extraction task
- Constraint independence: 5/5 - Single constraint (deep completeness) is clear
- Persona coherence: 5/5 - Designer to PM aligns well with pull task (extracting design insights)
- Category alignment: 5/5 - Strong alignment: designer deeply extracting information for PM consideration
- Combination harmony: 5/5 - Minimal but effective: deep completeness ensures thorough extraction, designer perspective adds UX focus
- **Overall**: 5/5

**Meta-Evaluation:**
- Skill alignment: 5/5 - Pull task and designer persona well-documented
- Skill discoverability: 5/5 - All tokens discoverable
- Heuristic coverage: 4/5 - Could benefit from scope or method token for richer extraction
- Documentation completeness: 5/5 - Clear documentation for all tokens
- **Overall**: 5/5

**Issues:**
- None identified

**Recommendations:**
- Demonstrates effectiveness of focused, minimal token combinations
- Designer_to_pm + pull could be documented for design-to-handoff workflows

---

# Summary Analysis

## Overall Score Distribution

| Score | Count | Seeds |
|-------|-------|-------|
| 5/5 | 10 | 121, 124, 125, 128, 130, 131, 135, 137, 139, 140 |
| 4/5 | 2 | 122, 129, 138 |
| 3/5 | 4 | 122, 123, 126, 127 |
| 2/5 | 3 | 132, 134, 136 |
| 1/5 | 1 | 133 |

**Average Score:** 3.7/5  
**Success Rate (≥4/5):** 60% (12/20)

## Common Patterns in High-Scoring Prompts (4-5/5)

### 1. **Aligned Persona-Task Relationships**
High-scoring prompts consistently show persona-task alignment:
- Designer personas with make/probe tasks (121, 124, 131)
- PM personas with planning/simulation tasks (130, 131, 135)
- Scientist personas with analysis tasks (124, 128, 137, 139)
- Minimal but focused combinations (128, 140)

### 2. **Complementary Constraint Sets**
Effective prompts feature constraints that enhance each other:
- `assume` scope + `simulation` method + `variants` form (131)
- `fail` scope + `sim` task + `log` form (130)
- `spec` method + `recipe` form + `pick` task (139)
- `systemic` method + `adr` channel + `probe` task (137)

### 3. **Appropriate Channel Selection**
High scores correlate with proper channel-task fit:
- Jira for team communication (124)
- ADR for architectural decisions (137)
- Log form for scenarios (130)
- Table form for extraction (123, 126)

### 4. **Clear Directional Movement**
Directional tokens add value when aligned:
- `dip ong` (concrete→actions→extend) with analysis/planning (124, 131)
- `bog` (structure→reflection→actions) with sorting (138)

## Common Issues in Low-Scoring Prompts (1-3/5)

### 1. **Documented Incompatibilities Not Enforced** ⚠️ CRITICAL
The most severe issues involve combinations that documentation explicitly warns against:

- **Seed 133:** `make` + `rewrite` - Form docs: "Pairing with `make` is semantically incoherent"
- **Seed 134:** `sim` + `shellscript` - Channel docs: "Not appropriate for narrative tasks (`sim`, `probe`)"
- **Seed 127, 136:** `probe/diff` + `gherkin` - Channel docs: "Not appropriate for tasks that don't involve system behavior"

### 2. **Persona-Channel Conflicts**
Multiple prompts show persona tone conflicting with channel requirements:
- **Seed 122:** `fun_mode` (casual) + `gherkin` (rigid structure)
- **Seed 132:** `to managers` + `codetour` (developer tool)

### 3. **Intent-Method Tensions**
Conflicting intents and methods create confusion:
- **Seed 123:** `appreciate` intent + `diagnose` method (positive vs. problem-focused)

### 4. **Audience Mismatches**
Audience-token misalignment appears in:
- **Seed 132:** Managers audience with codetour channel
- **Seed 133:** CEO audience with programmer voice

### 5. **Form-Channel Incompatibility**
Form and channel requirements conflict:
- **Seed 122:** `contextualise` form (add context without rewriting) + `gherkin` channel (pure output)
- **Seed 126:** `table` form + `svg` channel
- **Seed 134:** `socratic` form (questions) + `shellscript` channel (code)

## Aggregated Recommendations

### Critical Priority

1. **Implement Hard Constraints for Documented Incompatibilities**
   - Block `make` + `rewrite` (form documentation explicitly warns)
   - Block `shellscript` channel with `sim`/`probe` tasks
   - Block `gherkin` channel with non-behavioral tasks (`sort`, `sim`, `probe`, `diff` without behavioral subject)
   - Block `codetour` with non-code tasks (`sim`, `sort`, `probe`, `diff` without code, `plan`)

2. **Add Persona-Channel Compatibility Matrix**
   - Fun_mode should exclude channel-heavy outputs (gherkin, shellscript, codetour)
   - Audience-channel fit: codetour→developers, gherkin→BDD stakeholders, adr→architects

3. **Enforce Intent-Method Compatibility**
   - Appreciate/teach intents should exclude diagnostic methods (diagnose, risks, verify)
   - Persuade intent requires explicit audience

### High Priority

4. **Form-Channel Compatibility Validation**
   - Table form should warn with non-text channels (svg, html with limitations)
   - Socratic form should exclude code-only channels (shellscript, svg)
   - Contextualise form should exclude output-only channels

5. **Add Completeness-Task Guidance**
   - `max` completeness with simple tasks (fix, pull) may be overkill
   - `skim` completeness with test form may produce incomplete coverage

6. **Directional Token Appropriateness Review**
   - Review directional tokens for task fit
   - `fly ong` (abstract→concrete) may not suit reformattings (fix)
   - Document which directional tokens work best with which task types

### Medium Priority

7. **Require Persona Completeness**
   - Consider requiring at least voice + audience for all prompts
   - Or provide sensible defaults when persona is sparse

8. **Subject-Channel Validation**
   - Some channels require subjects (gherkin for behavior, codetour for code)
   - Validate subject presence when channel requires it

9. **Catalog Documentation Enhancements**
   - Add "Common Compatible Tokens" section to each token doc
   - Document exemplar combinations (like 121, 131, 139)
   - Add "Anti-patterns" section with problematic combinations

### Observations

10. **High-Quality Exemplars Identified**
    - **Seed 121:** Designer + make + verify + test + fip rog (reference for rigorous creation)
    - **Seed 131:** Designer + plan + assume + simulation + variants + dip ong (reference for planning)
    - **Seed 139:** Scientist + pick + spec + recipe (reference for decision-making)
    - **Seed 140:** Designer + pull + deep (reference for minimal effective prompts)

11. **Token Distribution Observations**
    - Gherkin channel appeared 4 times (122, 127, 133, 136) with 3 inappropriate pairings
    - Shellscript appeared once (134) with inappropriate sim task
    - Fun_mode appeared once (122) with inappropriate gherkin channel
    - Scientist_to_analyst persona appeared 4 times (128, 137, 139, 132*) with high success

12. **Shuffle Algorithm Observations**
    - Documented incompatibilities are appearing in shuffles, suggesting constraints not enforced
    - Channel appropriateness warnings exist but aren't preventing selection
    - Consider implementing compatibility scoring in shuffle algorithm

---

## Conclusion

This evaluation of 20 shuffled prompts reveals a **60% success rate** for high-quality (4-5/5) combinations, with **critical issues** around documented incompatibilities not being enforced by the system.

**Key Findings:**
1. When tokens align, they create powerful, clear prompts (exemplars: 121, 131, 137, 139)
2. Documented incompatibilities MUST be enforced programmatically
3. Persona-channel and intent-method conflicts need validation
4. The catalog has good documentation, but it needs to be enforced

**Immediate Action Required:**
- Implement hard constraints for make+rewrite, shellscript+sim/probe, gherkin+non-behavioral
- Add persona-channel and intent-method compatibility checks
- Review and potentially remove problematic combinations from shuffle algorithm

**Long-term Recommendations:**
- Develop compatibility scoring for shuffle algorithm
- Create exemplar documentation from high-scoring seeds
- Add anti-pattern documentation from low-scoring seeds

---

*Evaluation completed using ADR 0083 Prompt Key Criteria and Bar Skills Meta-Evaluation methodology.*
