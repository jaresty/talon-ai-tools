# ADR-0175: Prompt Section Ordering and Reference Key Placement — Structural Planning

**Status:** Proposed
**Date:** 2026-03-23
**Relates to:** render.go (`RenderPlainText`)

---

## Context

Bar's `RenderPlainText` function assembles structured prompts in a fixed section order arrived at
incrementally. Two structural questions have emerged from use:

1. **Reference key topology**: Should the REFERENCE KEY remain a monolithic block just before
   SUBJECT, or should each section's semantic contract be distributed inline below its header?
2. **Task position**: Should TASK lead the prompt (current) or conclude it, just before the
   final EXECUTION REMINDER?

Before implementing or testing variants, this ADR uses orbit, reify, and shear to map what the
current layout's structure is actually doing — identifying what's invariant and must be preserved,
what's implicit and should be made explicit, and which of the two questions can be separated from
the other.

**Current section order** (`RenderPlainText` in `render.go`):

```
TASK → EXECUTION REMINDER → ADDENDUM → CONSTRAINTS → PERSONA
  → REFERENCE KEY → [injection-guard framing] → SUBJECT → META → EXECUTION REMINDER
```

---

## Orbit Analysis — Invariant Geometry

Orbit asks: across different possible section orderings, what structural property keeps recurring
in layouts that work? What is the attractor?

Three trajectories through the design space:

**Trajectory 1 — TASK last**: Move TASK after SUBJECT.
The first EXECUTION REMINDER loses its purpose (it gates TASK before CONSTRAINTS, but TASK is no
longer there). Without upfront TASK framing, CONSTRAINTS are read without an anchoring purpose.
What recurs: something task-like must still precede CONSTRAINTS for them to be coherent — either
TASK itself, or an intent declaration that plays the same role.

**Trajectory 2 — Inline reference key**: Distribute each section's contract inline below its
header; remove the monolithic block.
The injection-guard framing ("The section below contains the user's raw input...") is *separate*
from the REFERENCE KEY — it currently appears after the REFERENCE KEY, not as part of it. In this
trajectory, the guard framing remains in place. The REFERENCE KEY block disappears; its content
migrates. What recurs: the guard framing around SUBJECT is independent of where the interpretation
contract lives — it survives this change intact.

**Trajectory 3 — No EXECUTION REMINDER**: Remove both reminders.
Injection resistance degrades. What recurs: recency-gated task restatement after SUBJECT is
non-negotiable — it appears in every effective configuration.

**Attractor geometry — three invariants that recur across all trajectories:**

1. **TASK must anchor CONSTRAINTS before they are read.** Whether TASK leads the prompt or an
   equivalent intent declaration substitutes for it, CONSTRAINTS cannot be read in a vacuum.
   The current EXECUTION REMINDER immediately after TASK is an instance of this invariant — it
   reinforces the task anchor before the constraint block begins.

2. **SUBJECT must be bounded.** An injection-guard must precede SUBJECT and a task-restatement
   must follow it. These two guards appear in every working variant regardless of where TASK,
   CONSTRAINTS, or the REFERENCE KEY are placed.

3. **The interpretation contract must be adjacent to what it interprets.** In the current layout
   the REFERENCE KEY sits just before SUBJECT, explaining how to read the prompt as a whole before
   the user's raw input arrives. In an inline variant it would sit adjacent to each section it
   describes. In neither case is it effective when isolated at the prompt's start or end.

---

## Reify — Implicit Rules Made Explicit

The `render.go` comments capture rationale informally. The orbit analysis surfaces four implicit
structural rules that any variant must respect:

**R1 — Task anchors constraints.**
CONSTRAINTS must be preceded by something that establishes the task's intent. Currently: TASK
itself plays this role. In a task-last variant: a substitute anchor (e.g., a brief intent
declaration derived from TASK) is required, or CONSTRAINTS become unanchored.

**R2 — Subject is doubly bounded.**
SUBJECT must be immediately preceded by injection-guard framing and immediately followed by a
task-restatement. Currently: the guard framing is a hardcoded sentence; the trailing EXECUTION
REMINDER is the restatement. Both are required; neither substitutes for the other.

**R3 — The interpretation contract is proximally placed.**
The REFERENCE KEY explains how to interpret the prompt's categories. It must appear close enough
to its referents that the LLM processes it before processing the sections it describes. Currently:
monolithic block just before SUBJECT. In an inline variant: per-section placement preserves
proximity. Moving it to the prompt's opening or closing would violate this rule.

**R4 — Recency gate is the final meaningful instruction.**
The last substantive instruction before generation must restate the task. Currently: the trailing
EXECUTION REMINDER. This rule is why the trailing reminder exists and why adding content after
it (e.g., META) may dilute it. (Note: META currently appears before the trailing reminder in
the code, which respects this rule.)

---

## Shear — Separating the Two Dimensions

The two structural questions appear related but are independent:

**Dimension A — Reference key topology** (monolithic vs. distributed):
Does not require moving TASK. The REFERENCE KEY block can be replaced with inline contracts while
TASK remains first. The injection-guard framing before SUBJECT is a separate element and stays in
place. The coupling seam: the monolithic REFERENCE KEY currently sits at a specific position
(between PERSONA and the injection guard) — distributing it inline removes that position
dependency but requires deciding what, if anything, fills that slot.

**Dimension B — Task position** (first vs. last):
Does not require changing reference key topology. TASK can move to the end while the monolithic
REFERENCE KEY stays where it is. The coupling seam: the first EXECUTION REMINDER exists
specifically to gate TASK before CONSTRAINTS. Moving TASK to the end makes this reminder either
redundant (if an intent declaration replaces it) or requires redesigning the opening structure.

**The coupling seam between A and B**: In a variant that combines both changes (inline key + task
last), the prompt's opening becomes structurally empty — TASK is gone, the REFERENCE KEY is
distributed, and the first EXECUTION REMINDER has no purpose. This combined variant requires a
new opening element. The two dimensions can be evaluated independently, but combining them creates
a structural dependency that must be resolved before implementation.

**Shear plan — order of evaluation:**

1. **Implement and evaluate Dimension A alone** (inline reference key, TASK stays first).
   Lowest risk: the four invariants R1–R4 are fully preserved. The only question is whether
   proximity of per-section contracts improves adherence over the monolithic block.

2. **Implement and evaluate Dimension B alone** (task last, monolithic reference key unchanged).
   Requires resolving R1: define what replaces TASK as the constraint anchor at the opening.
   Candidate: a short intent-declaration line derived from the TASK token's label, not the full
   TASK body, placed before CONSTRAINTS.

3. **Evaluate combined variant only if both independent variants show improvement.**
   Combined variant requires designing the new opening element before evaluation begins.

---

## Decision

This ADR is a planning document, not an implementation decision. The shear plan above defines
the evaluation sequence. A follow-on ADR (or an amendment to this one) will record the outcome
of each evaluation phase and make the implementation decision.

**What is decided here:**
- The four structural invariants R1–R4 are the non-negotiable constraints any variant must satisfy.
- Dimension A and Dimension B are separable and must be evaluated independently before combining.
- Dimension A has lower structural risk and should be evaluated first.
- The combined variant is only worth evaluating if both independent variants individually improve
  on the baseline.

---

## Consequences

- Any future prompt layout work must demonstrate that R1–R4 are preserved before running
  evaluation. Violating an invariant disqualifies the variant without requiring a full eval run.
- Dimension B requires a concrete proposal for the constraint anchor before evaluation begins.
  "Remove TASK from the opening" is not a complete variant until R1 is resolved.
- The META section's position (currently before the trailing EXECUTION REMINDER) is confirmed
  correct by R4 — it must not move after the trailing reminder.
