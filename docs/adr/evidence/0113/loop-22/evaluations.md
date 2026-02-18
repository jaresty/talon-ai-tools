# ADR-0113 Loop-22 Evaluations — Cross-Axis Health Check

**Date:** 2026-02-18
**Dev binary:** bar version dev
**Focus:** Fresh cross-axis health check across 8 diverse task types

---

## Task: L22-T01 — Security audit

**Task description:** "Audit a codebase for security vulnerabilities: identify common attack
surfaces, misconfigurations, and risky patterns"

**Skill selection log:**
- Task: probe (surface assumptions/implications — appropriate for surfacing vulnerabilities)
- Completeness: full
- Scope: struct (arrangement/dependencies), fail (failure modes/limits)
- Method: adversarial (systematic stress-test for weaknesses)
- Form: checklist (actionable imperative items)

**Bar command:** `bar build probe full struct fail adversarial checklist`

**Coverage scores:**
- Token fitness: 4 — probe+adversarial+fail is a strong security audit combination
- Token completeness: 4 — `cross` scope would capture cross-cutting concerns (auth, logging,
  input validation) across modules, but struct+fail covers the core sufficiently
- Skill correctness: 5 — correct task and method for a security audit
- Prompt clarity: 4 — checklist+adversarial gives actionable, stress-tested output
- **Overall: 4**

**Gap diagnosis:** none (minor: `cross` scope could strengthen cross-cutting coverage)

---

## Task: L22-T02 — Explain technical debt to engineering manager

**Task description:** "Explain technical debt to an engineering manager: what it is, how it
accumulates, and why paying it down matters"

**Skill selection log:**
- Task: show (explain for audience — correct)
- Completeness: full
- Scope: mean (conceptual framing — correct)
- Form: (none)
- Channel: plain (prose — correct)
- Persona: peer_engineer_explanation → **WRONG** (as-programmer to-programmer; target is manager)

**Bar command used:** `bar build show mean persona=peer_engineer_explanation plain`

**Correct command:** `bar build show full mean voice=as-programmer audience=to-managers plain`

**Coverage scores:**
- Token fitness: 4 — show+mean+plain is right for conceptual explanation in prose
- Token completeness: 4 — all key dimensions covered
- Skill correctness: 2 — persona selected wrong audience; `peer_engineer_explanation` targets
  programmer audience, not manager. `audience=to-managers` was available and would produce
  "highlighting outcomes, risk, and staffing" — exactly what a manager needs.
- Prompt clarity: 3 — the persona mismatch means the LLM targets wrong audience calibration
- **Overall: 3**

**Gap diagnosis:**
```yaml
gap_type: skill-guidance-wrong
task: L22-T02 — Explain technical debt to engineering manager
dimension: persona
observation: >
  Skill defaulted to `peer_engineer_explanation` preset (as-programmer to-programmer)
  for an "explain X to [manager]" task. The target audience is a manager, not a programmer.
  `audience=to-managers` exists and correctly describes "highlighting outcomes, risk, and
  staffing" — what a manager needs. No heuristic guides the autopilot on when to use
  explicit audience tokens vs presets, or how to match the task's stated audience to the
  right persona combination.
recommendation:
  action: skill-update
  target: help_llm.go renderHeuristics()
  section: "Token Selection Heuristics"
  proposed_addition: >
    Add "### Choosing Persona" section:
    - When audience is specified in the task description, prefer explicit `audience=` tokens
      over presets. Presets are shortcuts for common pairings, verify the audience matches.
    - Engineer explaining to manager → voice=as-programmer audience=to-managers
    - Engineer explaining to junior → persona=teach_junior_dev
    - Engineer explaining to PM → persona=designer_to_pm or voice=as-programmer audience=to-product-manager
    - Engineer explaining to exec/CEO → persona=executive_brief
    - Non-technical audience (manager, PM, CEO, stakeholder) → check to-managers, to-product-manager,
      to-ceo, to-stakeholders audience tokens
evidence: [L22-T02]
```

---

## Task: L22-T03 — Developer onboarding flow

**Task description:** "Design an onboarding flow for a new developer joining the team: what
should they do, in what order, across their first 30 days"

**Skill selection log:**
- Task: plan (proposes steps/strategy — correct)
- Completeness: full
- Scope: act (tasks/activities), time (sequences/phases)
- Form: walkthrough (step-by-step guide)

**Bar command:** `bar build plan full act time walkthrough`

**Coverage scores:**
- Token fitness: 5 — plan+time+walkthrough is excellent for a phased onboarding plan
- Token completeness: 5 — act captures "what to do", time captures "30-day progression"
- Skill correctness: 5 — clean, well-reasoned selection
- Prompt clarity: 5 — walkthrough guides step-by-step with temporal phases
- **Overall: 5**

**Gap diagnosis:** none

---

## Task: L22-T04 — REST vs GraphQL API comparison

**Task description:** "Compare REST vs GraphQL API design: trade-offs, when to choose each,
and decision factors"

**Skill selection log:**
- Task: diff (compare — correct)
- Completeness: full
- Scope: thing (entities being compared), mean (conceptual framing of each)
- Method: branch (parallel reasoning paths for when to choose each)
- Form: table (structured comparison)

**Bar command:** `bar build diff full thing mean branch table`

**Coverage scores:**
- Token fitness: 5 — diff+branch+table is a strong comparison setup
- Token completeness: 5 — thing+mean define what and how; branch covers decision factors
- Skill correctness: 5 — appropriate token selection throughout
- Prompt clarity: 5 — table output with branch reasoning serves the comparison well
- **Overall: 5**

**Gap diagnosis:** none

---

## Task: L22-T05 — Payment module test case generation

**Task description:** "Generate test cases for a payment processing module: happy path,
edge cases, and failure scenarios"

**Skill selection log:**
- Task: make (create new content — correct for generating test cases)
- Completeness: full
- Scope: fail (failure modes/edge cases), good (quality criteria/happy path)
- Channel: gherkin (structured test format)

**Bar command:** `bar build make full fail good gherkin`

**Coverage scores:**
- Token fitness: 5 — make+gherkin is right for creating Gherkin test artifacts
- Token completeness: 5 — fail+good captures "failure scenarios + happy path" precisely
- Skill correctness: 5 — strong selection; `check` vs `make` distinction correctly applied
- Prompt clarity: 5 — gherkin channel enforces test-case structure
- **Overall: 5**

**Gap diagnosis:** none

---

## Task: L22-T06 — Monolith-to-microservices migration roadmap

**Task description:** "Create a roadmap for migrating from a monolith to microservices:
phases, dependencies, risks, and decision points"

**Skill selection log:**
- Task: plan (proposes strategy — correct)
- Completeness: full
- Scope: struct (dependencies/arrangement), time (phases/temporal)
- Form: variants (multiple phasing options / decision points)

**Bar command:** `bar build plan full struct time variants`

**Coverage scores:**
- Token fitness: 4 — plan+struct+time is excellent for migration planning
- Token completeness: 4 — variants handles decision points; addendum mentions "risks" but no
  explicit risk scope/method selected. `fail` scope or `risks` method would strengthen this.
- Skill correctness: 4 — good selection; risk dimension slightly underweighted
- Prompt clarity: 4 — variants+struct+time produces phased options with dependencies
- **Overall: 4**

**Gap diagnosis:** none (minor: `risks` method or `fail` scope would fully capture the
risk dimension when the task explicitly mentions risks)

---

## Task: L22-T07 — Race condition debugging

**Task description:** "Debug a race condition in a concurrent system: identify the root
cause, explain why it occurs, and propose fixes"

**Skill selection log (incorrect):**
- Task: fix → **WRONG** (bar's fix = "reformat content", not "debug/fix a bug")
- Completeness: full
- Scope: struct, time
- Method: diagnose (correct method, wrong task)

**Bar command used (incorrect):** `bar build fix full struct time diagnose`

**Correct command:** `bar build probe full struct time diagnose bug`

**Coverage scores (for incorrect selection):**
- Token fitness: 1 — `fix` task produces "changes form or presentation of content" — completely
  wrong for debugging. The TASK section says "changes the form or presentation" which does not
  serve the debugging objective at all.
- Token completeness: 3 — diagnose method and struct+time scopes are correct
- Skill correctness: 1 — fundamental task token misrouting. "debug a race condition" maps
  naturally to "fix a bug" in everyday language, but bar's `fix` is a reformatting task.
- Prompt clarity: 1 — LLM would attempt to reformat content rather than debug
- **Overall: 2**

**Note:** The dev bar's `fix` use_when already states: "In bar's grammar, fix means reformat —
not debug. To analyze/debug: use probe with diagnose, inversion, or adversarial." This warning
exists but is in the token description table, not in the Token Selection Heuristics section.
The heuristics lack a "Choosing Task" sub-section that would provide *positive routing*
(debugging → probe + diagnose) rather than just *negative warning* (don't use fix).

**Gap diagnosis:**
```yaml
gap_type: skill-guidance-wrong
task: L22-T07 — Race condition debugging
dimension: task (static token)
observation: >
  The skill selected `fix` for "debug a race condition" because "debug/fix a bug" in natural
  language maps to the `fix` token by name. Bar's `fix` is a content-reformatting task, not
  a debugging task. The `fix` use_when already warns against this use, but the warning is in
  the token description table. The Token Selection Heuristics section has no "Choosing Task"
  sub-section, so there is no *positive heuristic* routing debugging tasks to `probe + diagnose`.
  The catalog is correctly documented; the heuristics are the gap.
recommendation:
  action: skill-update
  target: help_llm.go renderHeuristics()
  section: "Token Selection Heuristics"
  proposed_addition: >
    Add "### Choosing Task" section before Choosing Scope:
    - Explain / describe → show
    - Analyze, surface structure or assumptions → probe
    - Debug, troubleshoot, diagnose a problem → probe + diagnose method (NOT fix)
    - Create new content or artifacts → make
    - Plan steps or strategy → plan
    - Compare or contrast subjects → diff
    - Reformat or restructure existing content → fix (content transformation only, not bug-fixing)
    - Verify or audit against criteria → check
    - Extract a subset of information → pull
    - Simulate a scenario over time → sim
    - Select from alternatives → pick
    - Organize into categories or order → sort
evidence: [L22-T07]
```

---

## Task: L22-T08 — Legacy system architecture documentation

**Task description:** "Document the architecture of a legacy system for future
maintainability: capture key decisions, constraints, and design rationale"

**Skill selection log:**
- Task: make (create documentation — correct)
- Completeness: full
- Scope: struct (arrangement/dependencies), mean (rationale/conceptual framing)
- Channel: adr (ADR format — captures decisions + context + consequences)

**Bar command:** `bar build make full struct mean adr`

**Coverage scores:**
- Token fitness: 5 — make+adr is right for creating architecture documentation
- Token completeness: 5 — struct+mean captures "decisions + design rationale"
- Skill correctness: 5 — ADR channel naturally structures decisions with context/consequences
- Prompt clarity: 5 — clean, well-aligned selection
- **Overall: 5**

**Gap diagnosis:** none

---

## Summary

| Task | Tokens used | Score | Gap? |
|------|------------|-------|------|
| L22-T01 | probe full struct fail adversarial checklist | 4 | Minor |
| L22-T02 | show mean peer_engineer_explanation plain | 3 | **Yes — wrong persona** |
| L22-T03 | plan full act time walkthrough | 5 | None |
| L22-T04 | diff full thing mean branch table | 5 | None |
| L22-T05 | make full fail good gherkin | 5 | None |
| L22-T06 | plan full struct time variants | 4 | Minor |
| L22-T07 | fix full struct time diagnose | **2** | **Yes — wrong task** |
| L22-T08 | make full struct mean adr | 5 | None |

**Mean: 4.125/5**

**Gaps requiring action:** 2
- G-L22-01: Missing "Choosing Task" heuristic → T07 misrouting (score 2)
- G-L22-02: Missing "Choosing Persona" heuristic → T02 audience mismatch (score 3)

Both are **skill-guidance-wrong** gaps in the Token Selection Heuristics section of
`help_llm.go`. The catalog tokens and their use_when are correctly specified. The gap
is that the heuristics section has no positive routing for task token selection or
persona selection — autopilot must infer these from name-matching alone.
