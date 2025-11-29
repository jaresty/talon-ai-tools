# ADR Loop / Execute Helper Prompt

This helper describes a simple, repeatable loop for making progress on ADRs.
It is **not** an ADR itself and is intentionally ADR‑agnostic.

When asked to “run an ADR loop/execute iteration using this helper”, follow
the steps below to deliver one small, concrete slice of work that advances an
ADR’s own objectives in this repo.

The caller may either:
- Specify the target ADR explicitly (for example, by id), or
- Ask the assistant to choose an appropriate ADR autonomously.

When using this helper:
- Keep reasoning and status updates **concise and high‑signal**.
  - Summarise the plan, what you changed, and what remains.
  - Avoid narrating each inspection step (for example, which file you are
    about to open or which search you will run) unless it affects a
    decision.
- Focus on external artefacts (code, tests, docs, work‑logs, ADR metadata),
  not on describing your internal thought process in detail.
- Once you have chosen a slice for this loop, **commit to it** unless you
  hit a hard blocker. Do not keep shopping for alternative slices or
  repeatedly re‑stating high‑level options.

---

## 0. Clear relevant red checks

- If you already know about failing tests, lint errors, or type‑check
  failures that are relevant to the area you plan to touch, treat fixing or
  triaging those as the first task in this loop.
- Respect test intent: when behaviour is wrong, fix the implementation;
  when requirements have genuinely changed, update the tests and the
  relevant ADR/work‑log to match.
- Do not start new ADR work while knowingly leaving relevant red checks
  unaddressed, unless the failure is explicitly recorded and parked in an
  ADR work‑log as a short‑lived regression.

---

## 1. Choose an ADR and focus area

- If the caller has specified a target ADR, use that ADR.
- Otherwise, pick a single ADR that is clearly **incomplete** in this repo
  (for example, open tasks, non‑terminal status, or an active work‑log with
  remaining slices).
- When several ADRs are incomplete, prefer ones where:
  - A small slice will retire a meaningful objective, or
  - A slice will exercise a risky or central assumption (for example,
    entrypoints, critical workflows, or cross‑component contracts).
- Within that ADR, choose one **focus area** for this loop: a function,
  module, workflow, guardrail, or specific task already described in the ADR
  or its work‑log.

---

## 2. Plan one small slice

For the chosen ADR and focus area:

- Re‑read the ADR and its work‑log to understand:
  - The ADR’s stated objectives and remaining tasks in this repo.
  - Any existing decisions about scope, exclusions, or deferrals.
- Open or create the ADR’s work‑log file
  (for example, `0118-example-adr.work-log.md`) and add a dated heading for
  this loop.
- Decide on **one small, coherent slice** that moves the ADR forward. Common
  patterns (not exhaustive) include:
  - Implementing or extending a behaviour or workflow the ADR calls for.
  - Simplifying or refactoring code the ADR identifies as a hotspot.
  - Adding or tightening a guardrail the ADR requires.
  - Adding or improving tests or documentation when the ADR explicitly calls
    for them, or when they are clearly needed to make the planned change
    safe.
- Do **not** assume every slice must combine behaviour and tests. Choose
  the slice that best advances the ADR’s objectives; use tests and other
  checks as strategies to make those changes safe.
- Keep the slice small enough that you can, within this single loop:
  - Implement the change,
  - Run at least the most relevant checks/tests, and
  - Update the work‑log.

---

## 3. Execute, validate, and record

Execute the slice end‑to‑end:

- Make the necessary edits (code, tests, docs, or configuration) to satisfy
  the chosen objective.
- Run focused checks that exercise the affected area (for example, targeted
  tests or a representative CLI/API call) to confirm behaviour.
- If you discover that the ADR’s objectives are unclear, too broad, or
  partly out‑of‑date for this area, prefer to:
  - Clarify the intent in the ADR’s work‑log, and
  - Implement the smallest safe subset that you can state clearly,
  rather than silently redefining the ADR.
- Before claiming that an ADR objective in this focus area is complete or
  removed (that is, before you change `B_a` for this ADR), run the relevant
  checks that cover this change (targeted tests at minimum, and broader
  project checks when the change is wide‑ranging or high‑risk).
- Then update the ADR work‑log entry for this loop with:
  - The ADR id and focus area you chose.
  - A brief summary of the concrete changes you made.
  - Which ADR objectives or tasks you believe were retired or reduced.
  - Any follow‑up tasks you discovered and did **not** complete in this loop.

The loop is complete once you have landed a coherent slice that:

- Advances at least one ADR‑defined objective or task in this repo.
- Leaves tests and guardrails at least as strong as before (and stronger
  when that was part of the slice).
- Records what changed and what remains in the ADR’s work‑log so that the
  next loop can pick up from a clear state.

Periodically, when `B_a` for an ADR is nearly or fully exhausted in this
repo, reconcile the ADR’s own metadata (for example, `Status` and any
remaining task lists) with the work‑log. Before making a **major status
change** (for example, marking an ADR as effectively complete for this
repo), first run the project’s usual gating checks (tests, lint, type‑check)
that cover the affected areas so the status update accurately reflects a
green, stable state.

---

### Optional shorthand

You can think about each ADR `a` in terms of a simple state:

- `B_a`: remaining in‑scope objectives or tasks in this repo
  (behaviour, refactors, guardrails, tests, docs, or other concrete work the
  ADR calls for).
- `C_a`: how well the areas `a` touches are supported by evidence
  (for example, tests, checks, or other validation that make changes safer).

Each loop chooses one ADR and one slice, then:

- Reduces `B_a` by completing or shrinking at least one ADR‑defined task.
- Keeps or improves `C_a` enough that future changes in this area remain
  safe and easy to reason about.
