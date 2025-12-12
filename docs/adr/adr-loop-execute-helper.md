# ADR Loop / Execute Helper Prompt

This helper describes a simple, repeatable loop for making progress on ADRs.
It is **not** an ADR itself and is intentionally ADR‑agnostic.

When asked to “run an ADR loop/execute iteration using this helper”, follow
the steps below to deliver one **substantial, concrete slice** of work that
advances an ADR’s own objectives in this repo. It is also valid to discover
that there is no substantial work left for a given ADR and report that fact.

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
- By default, prefer **behaviour‑changing slices** that touch multiple parts
  of the system; use narrow or status‑only loops only when a broader slice
  is clearly unsafe or blocked.
- Once you have chosen a slice for this loop, **commit to it**, but be
  willing to abandon it and pick a clearer, more meaningful slice if you
  discover the original is too small or not worth doing.
- Aim for slices that:
  - Touch at least two of: code, tests, docs, configuration, or UX surfaces, **or**
  - Retire or introduce at least one non‑trivial behaviour end‑to‑end (not just a single wording tweak).

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
- Once you have a focus area, **do not ask the caller to choose between candidate slices inside that ADR by default**. Instead, pick the slice that:
  - Exercises the highest‑coordination or highest‑risk area the ADR identifies as important or risky (and that already has sufficient test coverage), or
  - Retires a clearly‑defined ADR task end‑to‑end with minimal ambiguity.
  Ask the caller to prioritise only when there is an explicit external constraint (for example, "do not touch streaming this week") or when there is a genuine cross‑ADR product/business priority call you cannot infer from code, tests, and ADR text alone—not merely because multiple subtasks exist.
- If, after scanning a specified ADR and its work‑log, you believe there is no
  substantial, in‑repo work remaining for this ADR in this repo (for example,
  status is Accepted and there are no clearly remaining in‑repo tasks or
  subtasks you can name), you MUST first:
  - Run the adversarial check described below in this helper and record it in
    the ADR’s work‑log (listing at least one plausible area or task and why it
    is out‑of‑scope for this repo, requires a separate ADR, or is genuinely no
    longer required), and
  - Reconcile the ADR’s own task lists and subprojects with that conclusion
    (for example, marking in‑repo items as complete or explicitly out‑of‑repo
    with a short reason, tied to existing tests/code/docs).
  - Confirm there are no remaining unchecked in‑repo tasks or subtasks in that ADR; if there are, either complete at least one of them in this loop or explicitly mark them out‑of‑repo/no‑longer‑required with a short justification that:
    - Names the task or subtask being reclassified.
    - Points at concrete evidence (for example, tests/code/docs or an external decision) showing why it is out‑of‑repo or no longer required for this ADR.
    - Does not merely restate that the work is "too big" or "risky" without such evidence.
  Only after that reconciliation is it acceptable to:
  - Run a short status‑only confirmation slice for that ADR (updating the
    work‑log), **or**
  - Tell the caller there is no further substantial work for that ADR and
    suggest moving on to another ADR.

---

## 2. Plan one bounded, substantial slice

For the chosen ADR and focus area:

- Re‑read the ADR and its work‑log to understand:
  - The ADR’s stated objectives and remaining tasks in this repo.
  - Any existing decisions about scope, exclusions, or deferrals.
- Open or create the ADR’s work‑log file
  (for example, `0118-example-adr.work-log.md`) and add a dated heading for
  this loop.
- Decide on **one coherent slice** that moves the ADR forward.
  - You can describe the slice clearly.
  - You can land it end-to-end (code/tests/docs as needed) in a single loop.
  - You are not leaving behaviour half-migrated with no clear follow-up.
  - "Bounded" means *finishable in this loop*, not "small"—multi-module or multi-surface slices are encouraged when you can still implement and validate them safely end-to-end.

Common patterns (not exhaustive) include:

  - Implementing or extending a behaviour or workflow the ADR calls for.
  - Simplifying or refactoring code the ADR identifies as a high-impact area.
  - Adding or tightening a guardrail the ADR requires.
  - Adding or improving tests or documentation when the ADR explicitly calls
    for them, or when they are clearly needed to make the planned change
    safe.
  - Reconciling the ADR's stated tasks and scope
    with its current work-log and repo state
    (for example, marking tasks as out-of-scope
    for this repo, splitting overly broad tasks,
    or adding a concise "Current status" summary).
- As a rule of thumb, prefer slices that:
  - Change behaviour or configuration and exercise it with tests or representative runs, and/or
  - Update multiple ADR touchpoints together (for example, config + tests + docs), whether the slice is narrow or broad in scope, rather than microscopic, single-line edits.
- Do **not** assume every slice must combine behaviour and tests. Choose
  the slice that best advances the ADR's objectives; use tests and other
  checks as strategies to make those changes safe.
- Documentation- or status-only slices should be **rare**. Use them only when:
  - You cannot safely land a behaviour slice in this loop *after* attempting to decompose it, **and** you:
    - Propose at least one concrete candidate behaviour slice for this ADR in the work-log (naming the module/function or workflow you would change). This candidate must be a minimal, single-loop behaviour slice for the focus area, not an obviously oversized "rewrite everything" task when smaller subtasks already exist, and
    - Record one or more concrete blocking conditions for that slice (for example, missing fixtures, failing tests that must be fixed first, an explicit external constraint, or unclear cross-ADR scope). When using "unclear scope" as a blocker, also add a follow-up task to clarify or split that scope (for example, via a new ADR or decomposition slice), **or**
  - You are reconciling ADR tasks/status with already-landed work and can point to concrete evidence (tests, code, docs) that all in-repo objectives are effectively complete.
  In all other cases, prefer behaviour/refactor/guardrail slices.
- If you cannot find a safe behaviour slice, first try a small **decomposition** slice (splitting a broad ADR task into concrete, testable subtasks) before falling back to a pure status loop, and record those subtasks explicitly in the work-log.
- Before claiming there is "no substantial in-repo work remaining" for an ADR, run an adversarial check in the work-log entry:
  - List at least one area or task the ADR names that you *could* plausibly touch.
  - Explain why each is unsafe or too large for this loop (for example, requires a multi-ADR design change, or would leave behaviour half-migrated).
  - For tasks that are genuinely multi-loop or multi-surface design/refactor work, make that scope explicit *inside this ADR* by:
    - Introducing a short **subproject** or subsection that names the larger goal and breaks it into smaller, concrete, testable subtasks.
    - Ensuring at least one of those subtasks is small enough to complete safely in a single loop (behaviour or guardrail/tests), leaving the rest as clearly-labelled follow-up subtasks under the same ADR.
  - Keep those subproject subtasks in the ADR's own task/status sections so repeated loops can retire them one by one without pretending the overarching goal fits into a single loop.
  - When such a subproject already lists concrete subtasks and there is no explicit external constraint, treat those subtasks as the default pool for the next loop and pick one yourself as the focus slice, rather than asking the caller which to choose.
  - Skipping all such subtasks in a loop is only acceptable when you also record in that loop’s work-log entry why each remaining subtask is temporarily blocked or no longer a safe single-loop slice.
- Always tag each loop in the ADR work-log as `kind: behaviour`, `kind: guardrail/tests`, or `kind: status` so the balance of slice types stays visible over time.


---

## 3. Execute, validate, and record

Execute the slice end‑to‑end:

- Make the necessary edits (code, tests, docs, or configuration) to satisfy
  the chosen objective. By default, a loop should land at least one concrete
  change in this repo; pure status loops are the exception, not the norm.
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
- Each loop MUST do at least one of:
  - Land a behaviour, refactor, guardrail, test, docs, or configuration change in this repo for the chosen ADR focus area that is non-trivial with respect to the ADR’s objectives (for example, not just formatting-only or rename-only changes unrelated to the behaviour being exercised), or
  - Mark at least one ADR task or subtask as completed or explicitly out-of-repo with a short justification recorded in the ADR and/or its work-log, in line with the adversarial checks above.

The loop is complete once you have landed a coherent slice that:

- Lands at least one concrete change in this repo (code, tests, or docs
  that change behaviour in the ADR’s target area or how ADR scope/status is
  applied).
- Advances at least one ADR-defined objective or task in this repo.
- Leaves tests and guardrails at least as strong as before (and stronger
  when that was part of the slice).
- Records what changed and what remains in the ADR's work-log so that the
  next loop can pick up from a clear state.

Periodically, when the remaining in-scope work for an ADR is nearly or fully
exhausted in this repo, or when several loops have landed for the
same ADR, run a dedicated **status reconciliation**
loop:

- Use the ADR's own task lists and work-log to
  summarise what is:
  - Completed in this repo.
  - Still in-repo and planned.
  - Out-of-repo or intentionally deferred.
- Update the ADR's metadata (for example,
  `Status` and any remaining task lists) and/or
  work-log with a short "Current status" summary.
- Before making a major status change (for
  example, marking an ADR as effectively complete
  for this repo), run the project's usual gating
  checks (tests, lint, type-check) that cover the
  affected areas so the updated status reflects a
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
 
 - Reduces `B_a` by completing or shrinking at least one ADR‑defined task **in this
   repo**; pure status-only loops should only reduce `B_a` when they mark work as
   complete or explicitly out-of-repo with a brief, concrete justification rooted
   in prior behavioural evidence, and when that decision is recorded in the
   work-log for later review—not as a way to avoid implementing planned changes.
 - Keeps or improves `C_a` enough that future changes in this area remain
   safe and easy to reason about.
 
 ---
 
 ### Definitions (for this helper)
 
 - **In-repo objective / task**: Any behaviour, refactor, guardrail, test, docs, or configuration change that the ADR text or its work-log names as work for this repo, including explicit subtasks under subprojects.
 - **Substantial slice**: A slice whose removal would change at least one test outcome, runtime behaviour, or ADR task/status that is observable from outside this helper.
 - **Non-trivial change**: A change whose removal would alter behaviour under test, a guardrail, or the ADR’s effective task list/status. Pure formatting/renames that do not affect tests, behaviour, or tasks are trivial.
 - **Candidate behaviour slice**: A small, named change scoped to a single focus area (function, module, workflow, or guardrail) that could be landed and tested in one loop without leaving that area half-migrated.


