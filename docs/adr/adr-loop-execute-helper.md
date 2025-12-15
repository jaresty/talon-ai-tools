# ADR Loop / Execute Helper Prompt

This helper describes a simple, repeatable loop for making progress on ADRs.
It is **not** an ADR itself and is intentionally ADR‑agnostic.

When asked to “run an ADR loop/execute iteration using this helper”, deliver
one **substantial, concrete slice** that changes an observable artefact
(code/tests/docs/config) or ADR task/status. Keep ADR bodies stable: record
loop entries in the ADR’s companion work‑log file (for example,
`ADR-ID-work-log.md`), not in the ADR proper. If you find no safe slice,
record the blocker instead of writing a no-delta loop.
- Treat every invocation of this helper as a **fresh** request, even within
  the same conversation. Re-read this helper and the target ADR/work-log,
  and avoid assuming persistent state beyond artefacts recorded in the repo;
  stale carry-over context is non-compliant.
- If you suspect conversational drift, **palate cleanse**: restate the ADR id,
  focus area, and current loop goal explicitly, disregard prior turn-by-turn
  assumptions, and rebuild context only from the ADR/work-log and repo files.
- If an ADR still has a work-log embedded in the ADR body, migrate it to the
  separate `ADR-ID-work-log.md` file before adding new entries; do not keep
  parallel logs in both places.
-
- Aim for minimal, high-signal slices that change observable artefacts; prefer
  deletion/simplification when it achieves the goal, but do not contort scope
  just to delete code.
- When renaming or re-homing concepts, prefer codemod-style mechanical updates
  (small, consistent passes) over bespoke one-offs to cut risk early.
- Assume no backward-compatibility shims are needed unless an ADR explicitly
  requires them; cut over cleanly by default.

The caller may either:
- Specify the target ADR explicitly (for example, by id), or
- Ask the assistant to choose an appropriate ADR autonomously.

When using this helper:
- Keep outputs concise and high‑signal: what slice, what changed, what
  remains. Focus on artefacts, not narration.
- Every loop entry must cite at least one touched or inspected artefact path
  (code/tests/docs/config) and, for status/task changes, the specific
  task/status field changed; absence of such pointers is non‑compliant.
- General principle: progress is measured by reality changing outside this helper. Bias toward behaviour or guardrail slices, and only introduce new tasks or status notes when paired with an artefact delta (code/tests/config/docs beyond the ADR itself) that would alter behaviour, tests, or task/status if reverted.
- When citing artefacts or checks, include how they were gathered in this loop:
  test command and exit result (if any), or file/section re-read. Self‑report
  without these details is non‑compliant.
  - Include a short snippet (or checksum) from command output or the changed
    section for each cited check where feasible; if omitted, state why and
    treat the loop as non-compliant if the omission blocks confidence.
    Absence of any artefact for cited checks must be called out explicitly.
- Choose the smallest slice that moves ADR objectives and yields an
  observable change. If reverting it wouldn’t change behaviour, tests,
  docs contract, or task/status (e.g., a test outcome, user-facing contract,
  or ADR task/status entry), pick a different slice.
- Status-only is valid only when a behaviour slice is unsafe this loop and
  you record the blocker; otherwise land a behavioural/guardrail/doc slice.
- Each loop must produce a concrete delta: modify code/tests/docs/config
  **or** change task/status state in the ADR/work‑log (complete/out‑of‑repo
  with evidence). Zero‑delta loops are non‑compliant.
- If you cannot identify a compliant delta for a loop, do not write a status
  entry; instead, add a short blocker note to the ADR/work‑log explaining why
  a new task or clarity is needed before proceeding, and log the observable
  trigger (failing test id/output, bug/ticket, external request) if one
  exists.
  - Do not repeat “parked”/blocker entries: once parked, your only options are
    to (a) record a new task/regression with its trigger and run a behaviour
    slice, or (b) run a fresh adversarial completion check to mark status.
- Once you have chosen a slice for this loop, **commit to it**, but be
  willing to abandon it and pick a clearer, more meaningful slice if you
  discover the original is too small or not worth doing.
- Aim for slices that:
  - Touch at least two of: code, tests, docs, configuration, or UX surfaces, **or**
  - Retire or introduce at least one non-trivial behaviour end-to-end (not just a single wording tweak).
- Guiding principle: every loop must change reality outside this helper text or the ADR you’re working on. Planning/status is only compliant when paired with an observable delta (code/tests/config/docs beyond the ADR itself) or a blocker tied to evidence; otherwise, do not run the loop. After any status/planning note, the next loop MUST deliver a real change before another status/planning entry.

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
  - Do not delay riskier, central slices solely to do “safe” work first; tackle them when they are the most meaningful remaining slice and testable.
  Ask the caller to prioritise only when there is an explicit external constraint (for example, "do not touch streaming this week") or when there is a genuine cross‑ADR product/business priority call you cannot infer from code, tests, and ADR text alone—not merely because multiple subtasks exist.
- If the ADR is parked (all tasks complete) and no new task/regression has been
  recorded in the ADR/work-log before this loop, do not run or log a loop.
  Zero‑delta “status confirmations” are non‑compliant.
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

- Re‑read the ADR and work‑log for objectives, tasks, scope/deferrals.
- Add a dated heading to the ADR work‑log for this loop.
- Pick one coherent, finishable slice that yields an observable change. If you
  cannot, log a blocker instead of forcing a loop.
- Use the removal test: if reverting your slice wouldn’t change behaviour,
  tests, docs contract, or task/status, choose a different slice.
- Status/documentation-only is acceptable only when a behaviour slice is
  unsafe now and you record the blocker plus at least one concrete candidate
  behaviour slice for later.
  - Do not run status-only loops back-to-back; only run one after at least one
  behaviour/guardrail/tests loop since the last status-only, unless a newly
  recorded task/regression (added to the ADR/work-log before the loop)
  justifies it.
  - The intervening behaviour/guardrail/tests loop must itself satisfy the
  removal test (its reversion would change behaviour/tests/docs/task/status),
  not just a trivial edit.
- If no safe behaviour slice, decompose broad tasks into explicit, testable
  subtasks and record them in the ADR before considering status-only.
- Before claiming “no substantial in-repo work remains,” run an adversarial
  check in the work‑log: name plausible tasks you could touch, why they’re
  unsafe/too large now, and either split into subtasks or mark out-of-repo
  with evidence. Keep subprojects/subtasks in the ADR so future loops can
  retire them.
  - Do not reuse the same evidence verbatim across loops; confirm fresh
  inspection or test runs, and cite what was newly reviewed this loop. If
  repeating a check, note what changed since the prior run or why repetition
    was necessary, and point to an observable (failing test, log, contract)
    that motivated the repeat when available. Prefer noting whether the
    observed outcome changed versus the prior run (for example, pass→fail,
    fail→pass, doc/task/state updated).
- Tag the loop in the work‑log as `kind: behaviour`, `kind: guardrail/tests`,
  or `kind: status`.


---

## 3. Execute, validate, and record

Execute the slice end‑to‑end:

- Make the edits (code, tests, docs, config) to satisfy the objective. If the
  behaviour slice is unsafe, log the blocker and the candidate slice instead
  of forcing a status loop.
- Run focused checks (targeted tests or representative runs) for the affected
  area; cite what you ran or inspected and whether it was run/read in this
  loop.
- If objectives are unclear, clarify in the work‑log and land the smallest
  safe subset you can state clearly.
- Before marking an objective complete/removed, run the relevant checks.
- When marking work out‑of‑repo/no‑longer‑required, state the task, cite a
  boundary/constraint, point at current tests/docs/code, and, if possible,
  note the expected owner/system; if no owner is identified, record that
  explicitly. Avoid vague “future work” language.
- Update the ADR work‑log entry with the ADR id/focus area, concrete changes,
  objectives/tasks retired, follow-ups, and the artefact paths touched or
  inspected. Include a brief removal test statement (what would change if
  this loop were reverted) and the test command/exit or files/sections
  reviewed this loop.
- Avoid hollow artefact citations: note a substantive change or observation
  (not whitespace/format-only) so reversion would alter behaviour/tests or
  task/status. If the change is small, call out the specific observable it
  affects (test expectation, contract wording, task/status) and tie it to a
  test or explicit acceptance/contract reference when possible. Prefer
  citing the specific test/contract id or assertion that would change if
  reverted.
- Each loop MUST do at least one of:
  - Land a behaviour, refactor, guardrail, test, docs, or configuration change
    in this repo for the chosen ADR focus area that is non-trivial with
    respect to the ADR’s objectives, or
  - Mark at least one ADR task/subtask as completed or explicitly out-of-repo
    with a short justification recorded in the ADR and/or its work-log, in
    line with the adversarial checks above.
  - Status-only loops are allowed only when they update tasks/status with
    evidence, are not back-to-back, and are limited to one after at least one
    behaviour/guardrail/tests loop unless driven by a newly recorded
    task/regression (added to the ADR/work-log before the loop). If no
    artefact delta is available, skip the loop. After parking an ADR, any new
    loop must start by recording a new task/regression in the ADR/work‑log.

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
- Before making any major status change (for example, marking an ADR as
  effectively complete for this repo), you MUST first run and record an
  adversarial completion check for that ADR in its work-log that:
  - Restates the ADR’s original motivation and key objectives in this repo
    in your own words.
  - Lists at least one plausible way the ADR could still be incomplete or
    mis-scoped (for example, an area the ADR text mentions that has no
    corresponding code, tests, or docs evidence).
  - For each plausible gap, either:
    - Add a concrete follow-up task or subtask in the ADR or work-log,
      naming the module, workflow, or guardrail to change, **and** include a
      trigger (failing test id/output, bug/ticket, external request), **or**
    - Explain briefly, with pointers to evidence, why it is genuinely
      out-of-scope or no longer required for this repo; claiming “new feature”
      is only acceptable when paired with a concrete trigger or external scope
      decision. Unsupported “new feature” labels are non-compliant.
  - Confirms which remaining in-scope items (if any) are still required
    for this repo and records them as explicit follow-up tasks.
  - Use fresh evidence for this completion check: rerun targeted tests in
    this loop or re-read relevant modules today, citing what was run or
    inspected and whether it was done in this loop. If no tests are rerun,
    cite the specific files/sections reviewed. Reusing only prior checks is
    non-compliant; record the actual commands/outputs or file sections
    inspected. The adversarial check itself must be rigorous (plausible gaps,
    evidence, and dispositions recorded, not cursory). A completion check is
    valid only if it produces an artefact delta (for example, updated
    tasks/status) and the ADR is not parked without a new recorded
    task/regression; otherwise skip and do not log a completion entry. Do not
    change status without a recorded adversarial completion check that meets
    these criteria.
- You MUST NOT mark the ADR as effectively complete for this repo while any
  of those required in-scope follow-up tasks remain open; they represent
  remaining `B_a` and must be completed or explicitly reclassified as
  out-of-repo/no-longer-required in a later loop.
- Once that adversarial completion check is recorded and any required
  follow-up tasks for this focus area are either completed in this loop or
  explicitly left for future loops, run the project's usual gating checks
  (tests, lint, type-check) that cover the affected areas so the updated
  status reflects a green, stable state.
- After a completion check declares all tasks done, park the ADR: do not run
  additional loops unless a new requirement/regression is logged as a new
  task or subtask. Record that new task in the ADR/work-log before starting
  another loop, with a pointer to its trigger (failing test id/output,
  bug/ticket, external request, or explicit contract/test that would change).
  “Parked” has this specific meaning; do not rebrand it (“paused”, “done for
  now”, etc.) to bypass the rule—no loops without a newly recorded task/
  regression and trigger.


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
 - **Parked**: If you cannot name a compliant in-repo slice, the ADR is parked: do not run or log a loop until you first record a new task/regression in the ADR/work-log (with a pointer to its trigger: failing test id/output, bug/ticket, external request). Different wording (“paused”, “done for now”, etc.) still counts as parked. You cannot keep reporting “parked”; the next action must be a new task-driven slice or a completion check to update status.
