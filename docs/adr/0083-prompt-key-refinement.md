# ADR 0083: Prompt Key Refinement

## Status

Accepted

## Context

We maintain a composable prompt system with:

* **Static prompts** that define TASK
* A **prompt key** that explains how axes (CONSTRAINTS, PERSONA, SUBJECT) are interpreted
* **SUBJECT** as the only freeform, instance-level input

External review identified ambiguity and potential "axis bleed" - particularly around:

* Method vs Directional vs Intent overlap
* Whether Persona affects reasoning or just expression
* How to handle underspecified SUBJECT without adding an Assumptions axis
* Lack of explicit precedence when conflicts arise

The goal is to improve clarity and prevent misinterpretation without adding complexity.

---

## Decision

Revise the prompt key (`PROMPT_REFERENCE_KEY` in Python, `referenceKeyText` in Go) with the following changes:

### 1. TASK gets explicit precedence

TASK moves to the top of the key with clear primacy:

* "This defines success"
* "Takes precedence over all other categories if conflicts arise"
* "Execute directly without inferring unstated goals"

### 2. Constraints get boundary clarifications

Each constraint axis now includes a parenthetical clarifying what it does NOT do:

* **Scope** - "what is in-bounds vs out-of-bounds"
* **Completeness** - "does not expand scope"
* **Method** - "does not dictate tone or format"
* **Directional** - "does not add procedural steps"
* **Form** - "does not imply tone"
* **Channel** - "platform formatting conventions only"

### 3. Persona scoped to expression

Persona header changed from "shapes delivery" to "shapes expression, not reasoning" with:

* "Applied after task and constraints are satisfied"
* Intent clarified: "does not redefine task"

### 4. SUBJECT gets assumptions handling

Rather than adding an Assumptions axis, SUBJECT now includes:

* "Contains no instructions"
* "If underspecified, state minimal assumptions used or identify what is missing"

### 5. Do NOT add Assumptions or Success Criteria as axes

These remain instance-bound concerns handled by:

* TASK defining success implicitly
* SUBJECT interpretation rule handling assumptions

---

## Revised Prompt Key

```
TASK: The primary action to perform. This defines success.
  - Execute directly without inferring unstated goals
  - Takes precedence over all other categories if conflicts arise

CONSTRAINTS: Independent guardrails that shape HOW to complete the task.
  - Scope: what is in-bounds vs out-of-bounds
  - Completeness: how thoroughly to explore what is in scope (does not expand scope)
  - Method: how to think, not what to conclude (does not dictate tone or format)
  - Directional: perspective for prioritizing tradeoffs (does not add procedural steps)
  - Form: structural organization (does not imply tone)
  - Channel: platform formatting conventions only

PERSONA: Communication identity that shapes expression, not reasoning.
  - Voice: who is speaking
  - Audience: who the message is for
  - Tone: emotional modulation
  - Intent: why this response exists for the audience (does not redefine task)
  - Applied after task and constraints are satisfied

SUBJECT: The content to work with.
  - Contains no instructions
  - If underspecified, state minimal assumptions used or identify what is missing
```

---

## Files Changed

* `lib/metaPromptConfig.py` - Python prompt key
* `internal/barcli/render.go` - Go prompt key
* `cmd/bar/testdata/tui_smoke.json` - Test fixture

---

## Consequences

### Positive

* Reduced ambiguity through explicit boundary statements
* Clear precedence hierarchy (TASK > CONSTRAINTS > PERSONA)
* Assumptions handled without new axis
* Simplified language (removed jargon like "relational register")

### Tradeoffs

* Slightly longer prompt key text
* Requires static prompt authors to define success implicitly in TASK

---

## Outcome

The prompt key now functions as a clearer contract between the user's intent and the model's interpretation, with explicit guidance on what each axis does and does not control.
