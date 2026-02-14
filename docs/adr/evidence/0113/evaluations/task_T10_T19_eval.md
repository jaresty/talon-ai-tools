# Tasks T10 + T19 — Design tasks with scaffold form misrouting

Evaluated together because they share the same gap type.

---

## Task T10 — Design a new API, schema, or data model

**Task description:** "Design a REST API for the notification service"
**Domain:** design

### Skill selection log

- Task: `make` (creating an artifact)
- Scope: `struct` (structural design = arrangements, relationships, schema)
- Method: none selected
- Form: `scaffold` (selected because Token Selection Heuristics: "Building understanding → scaffold")
  The skill interprets "design" as needing a learning-oriented structure.
- Channel: `code` (output as code/markup)

**Bar command (autopilot):** `bar build make full struct scaffold code`

**Better command:** `bar build make full struct code`

### Coverage scores
- Token fitness: 3 (scaffold is wrong form for design output)
- Token completeness: 4 (make+struct+code is good without scaffold)
- Skill correctness: 3 (scaffold misapplied from "building understanding" heuristic)
- Prompt clarity: 3 (scaffold description conflicts with design intent)
- **Overall: 3**

---

## Task T19 — Design system architecture from requirements

**Task description:** "Design the high-level architecture for a real-time event pipeline"
**Domain:** design

### Skill selection log

- Task: `make` (creating an architecture)
- Scope: `struct` (architectural structure)
- Form: `scaffold` (same misrouting as T10)
- Channel: `diagram` (output as Mermaid diagram)

**Bar command (autopilot):** `bar build make full struct scaffold diagram`

**Better command:** `bar build make full struct diagram`

### Coverage scores
- Token fitness: 3
- Token completeness: 4
- Skill correctness: 3
- Prompt clarity: 3
- **Overall: 3**

---

## Shared Gap Diagnosis

```yaml
gap_type: skill-guidance-wrong
tasks: [T10, T19]
dimension: form selection
observation: >
  The Token Selection Heuristics entry "Building understanding → scaffold" is being
  applied to design tasks where the output is a design artifact (API spec, architecture
  diagram), not an explanation for a learner.

  The scaffold form description says: "it starts from first principles, introduces ideas
  gradually, uses concrete examples and analogies, and revisits key points so a learner
  can follow and retain the concepts. Most effective with learning-oriented audiences
  (student, entry-level engineer). May conflict with expert-level or brevity-first personas
  where first-principles exposition contradicts assumed expertise."

  This form is clearly wrong for design tasks: the user wants a design artifact, not a
  first-principles tutorial on how to design one. Yet "design" and "understand the structure"
  both activate the heuristic "building understanding → scaffold", which incorrectly fires
  for artifact-producing tasks.

  The correct guidance is:
  - scaffold = for EXPLAINING a concept to a learner (show task, education context)
  - No special form needed for PRODUCING a design artifact (make task + code/diagram channel)

  When task = 'make', the output is an artifact; form tokens that describe presentation
  style (scaffold, walkthrough) should generally be avoided or only used if the user
  explicitly wants an explained design.

recommendation:
  action: skill-update
  skill: bar-autopilot
  section: "Token Selection Heuristics — Choosing Form"
  proposed_addition: >
    Do not apply form tokens when 'make' task is producing a design artifact:
    - 'scaffold' is for EXPLANATION tasks (show, probe), not artifact production (make)
    - When task='make' with code/diagram/adr channel: omit form tokens; the channel
      already specifies the output structure
    - Use scaffold only when the user explicitly wants a step-by-step explanation,
      not when they want a design artifact produced

    Scaffold is for the reader learning; make+code is for producing something they can use.
evidence: [T10, T19]
```
