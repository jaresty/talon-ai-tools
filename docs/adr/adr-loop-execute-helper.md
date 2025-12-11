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
- Once you have chosen a slice for this loop, **commit to it** unless you
  hit a hard blocker. Do not keep shopping for alternative slices or
  repeatedly re‑stating high‑level options.
- By default, aim for slices that:
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
- If, after scanning a specified ADR and its work‑log, you cannot identify any
  substantial, in‑repo work remaining (for example, status is Accepted and
  B_a is effectively 0), it is acceptable to:
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
- Decide on **one bounded, coherent slice** that moves the ADR forward.
  - “Bounded” here does **not** mean “small”. It means:
    - You can describe the slice clearly,
    - You can land it end-to-end (code/tests/docs as needed) in a single loop, and
    - You are not leaving behaviour half-migrated with no clear follow-up.
  Large, high-impact slices are fine when they meet these criteria.

Common patterns (not exhaustive) include:

  - Implementing or extending a behaviour or workflow the ADR calls for.
  - Simplifying or refactoring code the ADR identifies as a hotspot.
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
- After you have identified a couple of plausible slices, **choose one**
  and commit to it for this loop. Avoid repeatedly revisiting slice
  options unless you hit a hard blocker (for example, missing context or
  failing checks you cannot safely address here).
- Documentation-only slices should either:
  - Resolve a specific, observed confusion in current behaviour, tests, or
    workflows, **or**
  - Reconcile ADR tasks/status with actual repo state (for example,
    marking tasks complete/deferred and adding a short "Current status"
    snapshot), **or**
  - Take a broad, cross-cutting ADR task (for example, a single
    "remove duplicated lifecycle/history logic" bullet) and decompose it
    into a small set of named, bounded subtasks with:
      - Clear focus areas (functions/modules/workflows),
      - Expected artefacts (code/tests/docs), and
      - Primary tests/checks for each subtask,
    updating the ADR's Salient Tasks and work-log accordingly.
  Treat **pure wording-only tweaks** (that do not change behaviour, evidence,
  or status) as anti-patterns for ADR loops; batch those outside of this
  helper when possible.
  Status- or documentation-only slices should be the **exception**, not the
  default: for a given ADR, ensure that the clear majority of loops retire or
  introduce real behaviour/config/test changes rather than repeatedly
  re-describing scope or status. When you do mark tasks as out-of-scope in this
  repo, include a short justification of why they cannot or will not be
  implemented here (rather than simply being difficult or inconvenient).
  In the ADR's work-log entry for each loop, explicitly tag the slice as
  `kind: behaviour`, `kind: guardrail/tests`, or `kind: status` so that the
  balance of slice types is visible over time.
- Keep the slice **bounded and completable** enough that you can, within
this single loop:
  - Implement the change end-to-end,
  - Run at least the most relevant checks/tests, and
  - Update the work-log.
  This applies equally to small and large slices: big refactors are
  acceptable when you can still land them coherently within one loop.

  If, after scanning the ADR and work‑log, you genuinely cannot find any
  substantial slice that meets these criteria, first consider a
  **decomposition loop** for any broad or cross-cutting tasks (as described
  above). Only when remaining work is either clearly out-of-repo or already
  decomposed and exhausted should you treat this as a status confirmation
  loop: record in the work-log that there is no remaining in-repo work for
  this ADR (B_a ≈ 0) and report that outcome to the caller.

- Periodically (for example, every few loops for
  the same ADR), choose a slice that is primarily
  a **status snapshot**:
  - Scan the ADR's own task lists (for example,
    "Salient Tasks") and its work-log entries.
  - For this repo, mark which tasks are:
    - Completed or clearly characterised.
    - Still in-repo and incomplete.
    - Explicitly out-of-repo or deferred.
  - Add a short "Current status" or "Refactor plan
    and current status" subsection to the ADR or
    work-log so a future loop can see progress at
    a glance.
  - Do not run more than one status-snapshot loop
    in a row for the same ADR unless the previous
    loop has already established that `B_a ≈ 0`
    (no remaining in-repo work) and you are only
    confirming that state.

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

- Lands at least one concrete change in this repo (code, tests, or docs
  that change how Concordance is enforced or how ADR scope/status is
  applied).
- Advances at least one ADR-defined objective or task in this repo.
- Leaves tests and guardrails at least as strong as before (and stronger
  when that was part of the slice).
- Records what changed and what remains in the ADR's work-log so that the
  next loop can pick up from a clear state.

Periodically, when `B_a` for an ADR is nearly or fully exhausted in this
repo, or when several loops have landed for the
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

