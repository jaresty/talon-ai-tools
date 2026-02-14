# Task T30 — Multi-turn collaborative brainstorming

**Task description:** "Let's iteratively brainstorm the API design together"
**Probability weight:** 0.5%
**Domain:** design

## Skill selection log

- Task: `make` (creating something)
- Form: `cocreate` (the closest match: "collaborative process — small moves, explicit
  decision points, and alignment checks")
- No scope or method selected (brainstorming is exploratory)

**Bar command (autopilot):** `bar build make full cocreate`

**Bar output (cocreate):** "The response structures itself as a collaborative process —
small moves, explicit decision points, and alignment checks rather than a one-shot answer.
Without an output-exclusive channel, conducts this interactively: proposes, pauses for
feedback, and iterates. With an output-exclusive channel, formats the artifact to expose
decision points, show alternative moves, and make the response-inviting structure visible
within the output."

## Coverage scores

- Token fitness: 2 (cocreate gets conceptually close but bar produces a single-turn prompt)
- Token completeness: 1 (the task fundamentally requires stateful multi-turn capability)
- Skill correctness: N/A (bar cannot represent multi-turn; this is correct behaviour)
- Prompt clarity: 2 (the cocreate form makes the output appear collaborative but isn't truly interactive)
- **Overall: 2**

## Gap diagnosis

```yaml
gap_type: out-of-scope
task: T30 — Real-time collaborative brainstorming
observation: >
  Bar constructs single-turn structured prompts. Multi-turn collaborative brainstorming
  requires stateful interaction across turns: the user responds, the AI builds on that
  response, they iterate toward a shared artifact.

  The 'cocreate' form is the closest representation bar has, and it does something useful:
  it instructs the LLM to structure its response with explicit decision points and
  "response-inviting structure". But this is a communication style, not stateful collaboration.
  A single cocreate-prompted response cannot substitute for an actual iterative conversation.

  This is a known boundary of bar's single-prompt grammar model.
recommendation:
  action: document
  note: >
    Add to bar help llm in a "Scope note" or "Boundary conditions" section:
    "Bar constructs single-turn structured prompts. It does not model multi-turn
    interactive sessions or stateful collaboration loops. For iterative work,
    use 'cocreate' form to produce a response structured for iteration, then
    continue the conversation manually rather than expecting bar to manage the
    state across turns."
evidence: [T30]
```
