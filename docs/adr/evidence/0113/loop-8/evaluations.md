# ADR-0113 Loop-8 Evaluations — Specialist Form Token Coverage

**Date:** 2026-02-17
**Tasks evaluated:** T170–T182 (13 tasks)
**Focus:** Do specialist form tokens get surfaced by bar-autopilot, or is there a systematic discoverability gap?

---

## Evaluation Approach

Each task was:
1. Manually built with the optimal bar command (verifying token fitness)
2. Assessed for whether bar-autopilot would *independently* surface the specialist form token
3. Scored on the standard 5-dimension coverage rubric

The central question: **does the skill guidance lead autopilot to select specialist forms, or does it default to generic forms (checklist, walkthrough, bullets, variants, table)?**

---

## T170 — Competitive landscape Wardley map

**Task description:** "Map our product's e-commerce components on a Wardley evolution axis"
**Domain:** Design / strategy
**Target form:** wardley

**Command built:** `bar build make full struct wardley`
**Command output preview:** The response creates new content... Completeness (full)... Scope (struct)... Form (wardley): shows value chain evolution from genesis to commodity.

**Skill selection reasoning:**
- Task: `make` ✅ — producing a Wardley map is artifact creation
- Scope: `struct` — acceptable (component relationships/dependencies), though wardley maps show *evolution* which has no dedicated scope token
- Form: `wardley` ✅ — correct specialist form

**Autopilot discoverability assessment:** LOW
- No usage pattern for "competitive landscape" or "strategic mapping" in bar help llm
- Autopilot would likely default to `diagram` channel (produces a Mermaid diagram) or `table` form
- The `wardley` form description is clear but not linked to any strategic planning task type

**Coverage scores:**
- Token fitness: 4 (struct+wardley good; no scope token for evolution axis)
- Token completeness: 4 (wardley carries the key requirement)
- Skill correctness: 2 (no usage pattern; autopilot misses wardley)
- Prompt clarity: 5
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token

```yaml
gap_type: undiscoverable-token
task: T170 — Wardley competitive landscape
dimension: form
observation: >
  wardley form is well-described but has no usage pattern guiding selection for
  strategic landscape, value chain analysis, or evolutionary mapping tasks.
  Autopilot defaults to diagram channel or table form for "map X components".
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    ### Strategic Landscape / Wardley Mapping
    Use when mapping product or system components along an evolution axis.
    Pattern: bar build make full struct wardley --subject "..."
    Heuristic: "map components on evolution", "Wardley map", "genesis to commodity" → wardley form
evidence: [T170]
```

---

## T171 — Post-incident reflection

**Task description:** "We shipped a DB migration that dropped a FK constraint; 300% slowdown for 4 hours. Reflect on what happened."
**Domain:** Engineering / retrospective
**Target form:** wasinawa

**Command built:** `bar build show full wasinawa`
**Command output preview:** The response explains or describes... Form (wasinawa): What–So What–Now What reflection.

**Skill selection reasoning:**
- Task: `show` ✅ — describing/explaining what happened
- Completeness: `full` ✅
- Form: `wasinawa` ✅ — What happened, why it matters, what to do next

**Autopilot discoverability assessment:** LOW
- No usage pattern for post-incident reflection or retrospective in bar help llm
- Autopilot would likely default to `walkthrough` (step-by-step) or `checklist`
- `wasinawa` is distinctive but has no task-type anchor in the skill guidance

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 2 (no usage pattern for incident reflection)
- Prompt clarity: 5
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token

```yaml
gap_type: undiscoverable-token
task: T171 — Post-incident reflection
dimension: form
observation: >
  wasinawa is the ideal form for incident retrospectives (what happened, so what,
  now what) but has no usage pattern. Autopilot routes incident review to
  walkthrough or probe+fail, missing the structured reflection format.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    ### Post-Incident Reflection / Retrospective
    Use when reflecting on an incident, deployment failure, or past decision.
    Pattern: bar build show full wasinawa --subject "..."
    Heuristic: "what happened + why it matters + next steps" → wasinawa form
    Distinguish from pre-mortem (inversion method) which assumes future failure.
evidence: [T171]
```

---

## T172 — Technology investigation spike

**Task description:** "Should we adopt GraphQL for our API? Frame this as a research spike."
**Domain:** Engineering / planning
**Target form:** spike

**Command built:** `bar build plan full mean spike`

**Issues found:**
- `plan` task = "proposes steps, structure, or strategy" — partially correct
- But `spike` form description says "formats the backlog item as a research spike" — this is an *artifact* (a backlog item), not a plan. `make` is more precise: produce a spike artifact.
- `plan + spike` is semantically redundant: you're saying "propose a plan formatted as a backlog spike" when the spike IS the plan artifact.

**Better command:** `bar build make full mean spike`

**Autopilot discoverability assessment:** LOW
- No usage pattern for "research spike" or "technology adoption decision"
- Autopilot routes "should we adopt X?" to `diff` (comparison) or `probe` (analysis)
- Neither surfaces the `spike` form which packages the investigation as a backlog item

**Coverage scores:**
- Token fitness: 3 (`plan` is close but `make` is more precise for spike artifact production)
- Token completeness: 5 (spike carries the format need)
- Skill correctness: 2 (no usage pattern; autopilot misses spike form entirely)
- Prompt clarity: 4
- **Overall: 3**

**Gap diagnosis:** skill-guidance-wrong + undiscoverable-token

```yaml
gap_type: skill-guidance-wrong
task: T172 — Technology investigation spike
dimension: task token + form
observation: >
  Research spike tasks are routed to diff (comparison) or probe (analysis) by
  bar-autopilot. Neither surfaces the spike form. The correct pattern is
  make + spike: produce a backlog artifact formatted as a research spike.
  Additionally, the task token should be make, not plan, for spike artifacts.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    ### Research Spike (Technology Investigation)
    Use when framing a technology adoption decision as a backlog spike item.
    Pattern: bar build make full mean spike --subject "..."
    Heuristic: "should we adopt X?", "spike on Y", "investigation backlog item" → make + spike
    Note: use make (artifact production) not plan; the spike IS the artifact.
evidence: [T172]
```

---

## T173 — Iterative collaborative design

**Task description:** "Help me work through the API design incrementally with explicit decision points"
**Domain:** Engineering / design
**Target form:** cocreate

**Command built:** `bar build make full struct cocreate`
**Command output preview:** The response creates... Scope (struct)... Form (cocreate): collaborative process — small moves, explicit decision points, alignment checks.

**Skill selection reasoning:**
- Task: `make` ✅ — producing a design iteratively
- Scope: `struct` ✅ — structural API design
- Form: `cocreate` ✅ — explicit decision points, small moves

**Autopilot discoverability assessment:** LOW
- No usage pattern for "collaborative design with decision points" in bar help llm
- Autopilot routes API design to `make + struct + code` or `make + variants`
- `cocreate` is for when the *process* of creation matters, not just the artifact

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 2 (no usage pattern; cocreate not surfaced)
- Prompt clarity: 5
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token

```yaml
gap_type: undiscoverable-token
task: T173 — Iterative collaborative design
dimension: form
observation: >
  cocreate is ideal for iterative design tasks with explicit decision points but
  has no usage pattern. Autopilot routes design tasks to make+variants (options)
  or make+code (artifact), both of which produce one-shot responses.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    ### Collaborative / Iterative Design
    Use when the design process requires explicit checkpoints and user input.
    Pattern: bar build make full [scope] cocreate --subject "..."
    Heuristic: "work through incrementally", "decision points", "iterative design" → cocreate form
evidence: [T173]
```

---

## T174 — Abstraction-ladder diagnosis

**Task description:** "Help understand this latency issue by stepping up and down abstraction levels"
**Domain:** Engineering / diagnosis
**Target form:** ladder

**Command built:** `bar build probe full fail ladder`
**Command output preview:** The response analyzes... Scope (fail): breakdowns and failure modes... Form (ladder): abstraction laddering — stepping up to higher-level causes, down to consequences.

**Skill selection reasoning:**
- Task: `probe` ✅ — surfacing structure and implications
- Scope: `fail` ✅ — diagnosing what's failing
- Form: `ladder` ✅ — up/down abstraction levels

**Autopilot discoverability assessment:** MEDIUM
- No usage pattern, but ladder is somewhat discoverable: "step up and down levels" is a hint
- Autopilot might surface `ladder` if the user phrases the request explicitly
- Without that cue, autopilot defaults to `walkthrough` for structured diagnosis

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 3 (somewhat discoverable from explicit user phrasing)
- Prompt clarity: 5
- **Overall: 4**

**Gap diagnosis:** undiscoverable-token (minor)

```yaml
gap_type: undiscoverable-token
task: T174 — Abstraction ladder diagnosis
dimension: form (minor)
observation: >
  ladder form is discoverable from explicit user phrasing ("step up and down abstraction
  levels") but has no usage pattern for system diagnosis tasks. Without the explicit
  hint, autopilot defaults to walkthrough.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    ### Abstraction-Ladder Analysis
    Use when analyzing causes or effects that span multiple levels of abstraction.
    Pattern: bar build probe full [scope] ladder --subject "..."
    Heuristic: "why is this happening at a systems level?", "step up", "root cause hierarchy" → ladder
evidence: [T174]
```

---

## T175 — Error type classification

**Task description:** "Classify all the types of errors in our payment service"
**Domain:** Engineering / analysis
**Target form:** taxonomy

**Command built:** `bar build show full struct taxonomy`

**Issues found:**
- Scope: `struct` covers "how parts are arranged" — structural arrangement
- But error classification is more about "what kinds of things exist" — this maps better to `thing` scope ("physical elements, concrete entities, measurable quantities")
- `show full thing taxonomy` would be more precise than `show full struct taxonomy`

**Autopilot discoverability assessment:** LOW
- No usage pattern for "classification tasks" or "type hierarchy creation"
- Autopilot might default to `table` form (a table of error types) or `checklist`
- `taxonomy` form is specific: "classification system, type hierarchy, category taxonomy"

**Coverage scores:**
- Token fitness: 3 (`struct` scope is imprecise for classification; `thing` fits better)
- Token completeness: 4 (taxonomy carries the key need)
- Skill correctness: 2 (no usage pattern; autopilot defaults to table/checklist)
- Prompt clarity: 5
- **Overall: 3**

**Gap diagnosis:** skill-guidance-wrong + scope selection issue

```yaml
gap_type: skill-guidance-wrong
task: T175 — Error type classification
dimension: form + scope
observation: >
  Classification tasks ("classify all types of X") have no usage pattern.
  Autopilot defaults to table or checklist. taxonomy form is more precise for
  hierarchical type systems. Additionally, struct scope is imprecise for
  classification; thing scope better captures "what kinds of entities exist".
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    ### Classification / Type Taxonomy
    Use when producing a type hierarchy or category classification.
    Pattern: bar build show full thing taxonomy --subject "..."
    Heuristic: "classify all types of X", "what kinds of Y exist", "type hierarchy" → taxonomy form + thing scope
evidence: [T175]
```

---

## T176 — Technical retrospective facilitation

**Task description:** "Plan and facilitate a retrospective on our Q4 deployment failures"
**Domain:** Team process / facilitation
**Target form:** facilitate

**Command built:** `bar build plan full act facilitate`
**Command output preview:** The response proposes steps... Scope (act): tasks and activities... Form (facilitate): facilitation plan — session structure, participation management.

**Skill selection reasoning:**
- Task: `plan` ✅ — planning the facilitation
- Scope: `act` ✅ — activities to be done
- Form: `facilitate` ✅ — facilitation plan with session structure

**Autopilot discoverability assessment:** LOW
- No usage pattern for facilitation tasks
- Autopilot routes "plan a retrospective" to `plan + walkthrough` (agenda) or `plan + checklist`
- Neither produces a proper facilitation guide with participation cues and session structure

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 2 (no usage pattern; autopilot misses facilitate)
- Prompt clarity: 5
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token

```yaml
gap_type: undiscoverable-token
task: T176 — Retrospective facilitation
dimension: form
observation: >
  facilitate form produces facilitation plans (agenda, goals, participation cues,
  session structure) but has no usage pattern. Autopilot routes facilitation
  planning to plan+walkthrough which produces an agenda without facilitation structure.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    ### Facilitation Planning
    Use when planning a workshop, retrospective, or collaborative session.
    Pattern: bar build plan full act facilitate --subject "..."
    Heuristic: "facilitate a X", "run a retrospective", "workshop planning" → facilitate form
    Use plan+facilitate for static deliverable; facilitate alone in TUI for live facilitation.
evidence: [T176]
```

---

## T177 — Process documented as recipe

**Task description:** "Document how to set up our dev environment: Docker, pnpm, postgres, env vars, local SSL"
**Domain:** Engineering / documentation
**Target form:** recipe

**Command built:** `bar build show full flow recipe`

**Notes:**
- Task: `show` ✅ — describing/explaining the setup
- Method: `flow` ✅ — sequential steps
- Form: `recipe` ✅ — recipe with custom mini-language and key
- Alternative: `make full flow recipe` would work too (making a documentation artifact)

**Autopilot discoverability assessment:** VERY LOW
- No usage pattern for "process as recipe" in bar help llm
- Recipe form is the most unusual specialist form: produces a "custom mini-language and short key"
- Autopilot would default to `show + walkthrough` (step-by-step) for setup documentation
- The recipe form's distinctive feature (custom mini-language) is not obvious from the name alone

**Coverage scores:**
- Token fitness: 4 (show+flow+recipe is good; make also valid)
- Token completeness: 4
- Skill correctness: 2 (no usage pattern; most unusual form in catalog)
- Prompt clarity: 5
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token

```yaml
gap_type: undiscoverable-token
task: T177 — Recipe documentation
dimension: form
observation: >
  recipe form produces documentation with a custom mini-language and key — a
  distinctive format for process documentation. No usage pattern exists.
  Autopilot routes all "how to do X" documentation to walkthrough (step-by-step).
  recipe is the appropriate form when the process has a recurring structure that
  benefits from a custom notation.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Usage Patterns by Task Type"
  proposed_addition: >
    ### Process-as-Recipe Documentation
    Use when documenting a process that has a recurring structure or a custom notation.
    Pattern: bar build show full flow recipe --subject "..."
    Heuristic: "document as recipe", "process with custom notation", "setup guide" with structured steps → recipe form
    Distinguish from walkthrough: walkthrough = linear narrated steps; recipe = structured with custom mini-language.
evidence: [T177]
```

---

## T178 — Learn via Socratic questioning

**Task description:** "Help me understand event sourcing through questions, not explanation"
**Domain:** Learning / education
**Target form:** socratic

**Command built:** `bar build show full mean socratic`
**Command output preview:** The response explains... Scope (mean): conceptual framing... Form (socratic): question-led method, withholds conclusions.

**Skill selection reasoning:**
- Task: `show` ✅ — explanation/teaching context
- Scope: `mean` ✅ — conceptual understanding
- Form: `socratic` ✅ — question-led, Socratic method

**Autopilot discoverability assessment:** MEDIUM-HIGH
- The user's explicit phrasing "through questions, not explanation" is a strong signal
- `socratic` form description directly mentions this use case
- Autopilot should surface it when user explicitly asks for question-led learning
- Without the explicit cue, autopilot might default to `scaffold` (first-principles explanation)

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 3 (discoverable with explicit cues; no usage pattern)
- Prompt clarity: 5
- **Overall: 4**

**Gap diagnosis:** undiscoverable-token (minor — only affects implicit cases)

---

## T179 — Merge multiple documents

**Task description:** "Combine three architecture docs into a single coherent specification"
**Domain:** Documentation / synthesis
**Target form:** merge

**Command built:** `bar build pull full struct merge`
**Command output preview:** The response selects or extracts a subset... Scope (struct)... Form (merge): combines multiple sources into a single coherent whole.

**Skill selection reasoning:**
- Task: `pull` ✅ — extracting/combining (pull = extract subset from source material)
- Scope: `struct` ✅ — structural architecture content
- Form: `merge` ✅ — combining multiple sources

**Autopilot discoverability assessment:** MEDIUM
- `merge` description says "combine multiple sources" which matches the task description
- Autopilot with three input docs should surface merge
- But without explicit multi-document framing, might default to `pull + gist`

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 3 (somewhat discoverable; no usage pattern)
- Prompt clarity: 5
- **Overall: 4**

**Gap diagnosis:** undiscoverable-token (minor)

---

## T180 — VS Code CodeTour creation

**Task description:** "Create a CodeTour for our authentication flow"
**Domain:** Engineering / documentation
**Target:** codetour (channel)

**Command built:** `bar build show full flow codetour`
**Command output preview:** The response explains... Method (flow): step-by-step progression... Channel (codetour): VS Code CodeTour .tour JSON file.

**Notes:**
- User explicitly named CodeTour — high discoverability by design
- `show + flow + codetour` is clean: explain the flow, output as CodeTour JSON
- The channel description is self-describing for users who know what CodeTour is

**Autopilot discoverability assessment:** HIGH (user-directed)
- User names CodeTour explicitly; autopilot should map this to `codetour` channel
- No usage pattern needed given explicit naming

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 4 (user-directed; channel name is self-describing)
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

---

## T181 — Quiz-based knowledge check

**Task description:** "Test my understanding of CQRS through a quiz"
**Domain:** Learning / education
**Target form:** quiz

**Command built:** `bar build probe full mean quiz`

**Notes:**
- Task: `probe` — surfacing structure and implications (for CQRS concepts)
- But `probe` is about analysis, not interactive teaching. For quiz, `show` might be cleaner: "explain CQRS through a quiz structure"
- `probe + quiz` = analyze CQRS concepts formatted as a quiz. Workable.
- Without a channel (output-exclusive), quiz conducts interactively — the LLM poses questions and waits. This is correct for "test my understanding."

**Autopilot discoverability assessment:** MEDIUM-HIGH
- User explicitly says "through a quiz" — strong signal
- But quiz form description says interactive without channel; autopilot might not realize this and add a static channel

**Coverage scores:**
- Token fitness: 4 (probe works; show might be slightly more natural)
- Token completeness: 4
- Skill correctness: 3 (discoverable from explicit "quiz" request)
- Prompt clarity: 4 (quiz interactivity may not be obvious to user)
- **Overall: 4**

**Gap diagnosis:** undiscoverable-token (minor — quiz is self-describing but channel guidance helpful)

---

## T182 — Abstract visual microservices layout

**Task description:** "Show the relationship between microservices as an abstract visual layout (not a Mermaid diagram)"
**Domain:** Engineering / communication
**Target form:** visual

**Command built:** `bar build show full struct visual`
**Command output preview:** The response explains... Scope (struct)... Form (visual): abstract visual or metaphorical layout with short legend.

**Skill selection reasoning:**
- Task: `show` ✅
- Scope: `struct` ✅ — microservices structural relationships
- Form: `visual` ✅ — abstract visual layout vs precise Mermaid

**Critical distinction:** `visual` form (abstract, metaphorical) vs `diagram` channel (precise Mermaid)
- Without "not a Mermaid diagram" in the task, autopilot would select `diagram` channel
- The `visual` form's distinctive value — abstract/metaphorical representation — is lost

**Autopilot discoverability assessment:** LOW
- "Show microservices relationships" → autopilot defaults to `diagram` channel
- `visual` form requires the user to explicitly want non-diagrammatic visual layout
- The distinction between visual (form) and diagram (channel) is not in any usage pattern

**Coverage scores:**
- Token fitness: 4 (correct given "abstract visual" requirement)
- Token completeness: 4
- Skill correctness: 2 (autopilot defaults to diagram channel; visual form undiscoverable)
- Prompt clarity: 4 (distinction not well-signaled in prompt)
- **Overall: 3**

**Gap diagnosis:** undiscoverable-token

```yaml
gap_type: undiscoverable-token
task: T182 — Abstract visual layout
dimension: form vs channel distinction
observation: >
  visual form (abstract/metaphorical layout) and diagram channel (precise Mermaid) serve
  different needs but autopilot always selects diagram channel for "show relationships".
  The visual form's use case (when you want prose + metaphor, not structured diagram) has
  no usage pattern and is never surfaced by autopilot.
recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Token Selection Heuristics — Choosing Form"
  proposed_addition: >
    **visual vs diagram:**
    - diagram channel: precise structural diagram (Mermaid) with nodes and edges
    - visual form: abstract/metaphorical prose layout with legend
    Use visual form when: (a) Mermaid would be too detailed, (b) user wants conceptual
    overview rather than implementation-accurate diagram, (c) audience is non-technical.
    Use diagram channel when: precise relationships, exact topology, or diagrammatic fidelity matters.
evidence: [T182]
```

---

## Summary Table

| Task | Form | Command | Fit | Complete | Skill | Clarity | Overall |
|------|------|---------|-----|----------|-------|---------|---------|
| T170 | wardley | make full struct wardley | 4 | 4 | 2 | 5 | **3** |
| T171 | wasinawa | show full wasinawa | 5 | 5 | 2 | 5 | **3** |
| T172 | spike | plan full mean spike | 3 | 5 | 2 | 4 | **3** |
| T173 | cocreate | make full struct cocreate | 5 | 5 | 2 | 5 | **3** |
| T174 | ladder | probe full fail ladder | 5 | 5 | 3 | 5 | **4** |
| T175 | taxonomy | show full struct taxonomy | 3 | 4 | 2 | 5 | **3** |
| T176 | facilitate | plan full act facilitate | 5 | 5 | 2 | 5 | **3** |
| T177 | recipe | show full flow recipe | 4 | 4 | 2 | 5 | **3** |
| T178 | socratic | show full mean socratic | 5 | 5 | 3 | 5 | **4** |
| T179 | merge | pull full struct merge | 5 | 5 | 3 | 5 | **4** |
| T180 | codetour | show full flow codetour | 5 | 5 | 4 | 5 | **5** |
| T181 | quiz | probe full mean quiz | 4 | 4 | 3 | 4 | **4** |
| T182 | visual | show full struct visual | 4 | 4 | 2 | 4 | **3** |

**Mean score: 3.38/5**
**Tasks scoring ≤3: 8 (T170, T171, T172, T173, T175, T176, T177, T182)**
**Tasks scoring 4: 4 (T174, T178, T179, T181)**
**Tasks scoring 5: 1 (T180)**
