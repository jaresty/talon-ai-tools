# ADR Loop / Execute Helper Prompt (Single-Agent Sequential Process)

This helper defines the loop for advancing any ADR. It protects safety and
observability while keeping a single agent efficient by bundling only when the
behaviour, documentation, and guardrails share the same objective.

**Treat every invocation as fresh.** Rebuild context from the ADR text, its
work-log, and current repo state; do not rely on conversational history.

---

## Core Principles

1. **Test before change.** Characterise or re-verify behaviour with automated
   checks *before* implementation edits land. Add or update tests first, or cite
   and re-run existing ones explicitly. When landing a behaviour change, ensure a
   targeted test is failing (new or existing) **before** modifying implementation
   code. If existing coverage currently passes, update the expectation to reflect
   the desired behaviour and re-run to capture the failure before touching
   implementation. For refactors, rely on characterization tests and temporarily
   break the implementation to prove the tests detect the regression before
   carrying the refactor through.
2. **One substantial slice per loop.** Work is sequential; finish the current
   slice (including validation and logging) before planning the next.
3. **Observable deltas only.** Each loop must change code, tests, docs, config,
   or ADR task/status in a way that would matter if reverted.
4. **Lean process, rich evidence.** Keep planning lightweight (scratch notes are
   fine) but record concrete evidence: commands run, output, files touched, and
   removal tests.
5. **Adversarial mindset.** Assume the ADR may still be incomplete; look for
   gaps each loop and especially before declaring completion.

---

## Loop Outline

### 0. Clear Relevant Red Checks

- If failures relate to the target ADR, fix or triage them first.
- When a failure cannot be resolved now, record the blocker (with evidence) in
  the ADR work-log before proceeding.

### 1. Rebuild Context & Choose the Focus Area

- Re-read the ADR body and work-log to refresh objectives, tasks, and recent
  slices. For large ADRs, re-scan only the sections relevant to today’s slice and
  note which sections you inspected.
- Confirm the ADR still has in-repo work. When unsure, perform an adversarial
  scan (see completion section) before editing.
- Select one focus area aligned with ADR goals (e.g., specific module, workflow,
  guardrail, or documented task). Prefer high-signal slices that reduce risk or
  retire tasks outright.

### 2. Plan a Substantial Slice (Bundling Checklist)

- Capture a quick pre-plan (scratch notes allowed) listing involved files,
  intended behaviour change, validation commands, and documentation updates. Note
  the exact command(s) you will run for red/green evidence so they can be cited
  later without guesswork.
- A slice qualifies when it:
  - Changes a single user-visible behaviour or guardrail end-to-end, **or**
  - Completes an ADR task/subtask, **or**
  - Tightens CI/telemetry coverage for an existing behaviour.
- **Bundling checklist (all must be true):**
  1. All edits address the same behaviour, feature flag, or guardrail decision.
  2. Exactly one acceptance/validation command (or command set) will prove the
     entire bundle.
  3. No more than one major component boundary is crossed (config + implementation
     + docs counts as one if governed by the same behaviour). If uncertain, split
     into separate loops or seek review before bundling.
  4. A clear rollback plan exists: reverting this slice must restore the previous
     behaviour cleanly.
- If any criterion fails, split the work into multiple loops.
- If no safe behaviour slice exists, record the blocker (with evidence) and the
  follow-up plan instead of forcing a no-op loop. Status-only loops still require
  an observable change (e.g., reclassifying a task with evidence) and must be
  separated by behaviour/guardrail loops.

### 3. Execute & Validate (Testing-First)

3a. **Draft or update targeted tests.**
    - Add/extend targeted tests, or re-run existing ones that cover the affected
      paths.
    - Survey existing suites and harnesses before adding new tests; extend the
      canonical seam when possible and document any divergence.
    - When relying on existing coverage, cite the exact test cases and explain
      why they cover the behaviour. For every code edit, name the specific
      test(s) that would fail if that change were reverted.

3b. **Capture the failing run (red-first proof).**
    - Before touching implementation, run the chosen validation command and
      capture the failing result (new test or updated expectation). If existing
      coverage currently passes, update the expectation to reflect the desired
      behaviour and re-run to capture the failure before touching
      implementation. For refactors, rely on characterization tests and
      temporarily break the implementation to prove the tests detect the
      regression before carrying the refactor through.
    - The failing state must originate from the guardrail test or expectation
      change itself—not ad-hoc instrumentation. Temporary code edits to induce
      red runs are disallowed **except** when backfilling missing coverage; in
      that case, revert the intentional regression immediately after proving the
      test detects it.
    - Record each command in a structured evidence block: command, timestamp,
      exit status, and a short excerpt or checksum proving the outcome.
    - When automation is impossible, log the blocker and the attempted command
      before continuing, including the command you attempted to run.

3c. **Implement the slice.**
    - Apply code/config/doc changes, staying within the chosen focus area.
    - Keep edits minimal yet complete for the intended behaviour.
    - Before rerunning validation, inspect the diff and remove any change not
      required to flip the failing test; treat unexpected edits as suspect until
      they are justified.

3d. **Re-run for green.**
    - Execute the same validation command(s) after implementation edits to
      confirm the behaviour passes.
    - Before accepting the final green run, temporarily roll back the behaviour
      change and re-run the validation; if it stays green, you either left
      incidental edits or loosened the guardrail—shrink or tighten until the red
      returns.
    - Avoid repo-wide runs unless cross-cutting changes demand them; justify when
      broader runs are necessary.
    - Capture relevant output in the evidence block (pass/fail summary, key log
      lines, or hashes).

**Red/green checklist (do not advance until all are satisfied):**
- 3b captured the failing command before implementation edits (red).
- 3c landed the implementation change for the focused slice.
- 3d re-ran the same command(s) and captured the passing result (green).

If the green rerun still fails, resolve it within the loop or record a blocker
entry (including the failing evidence) before proceeding to Step 4.

### 4. Record the Loop & Queue Next Work

Add a work-log entry containing:


- **Heading:** Date + `kind: behaviour`, `kind: guardrail/tests`, or
  `kind: status` (status entries still require an artefact change grounded in
  evidence).
- **Context:** Focus area and objective.
- **Deliverables:** Updated artefacts (files, scripts, docs). Keep bullet points
  short and factual. For each code edit, include a `Guardrail` bullet naming the
  failing/passing test or command (e.g., `tests/path/to_case::suite::check`).
- **Plan vs. outcome:** If the landed work diverged from the initial plan,
  briefly note what changed and why (e.g., “Deferred doc update pending new
  schema”).
- **Status-only loop guard:** If this entry only captures status or documentation
  deltas, queue the next behaviour/guardrail slice before closing the loop so the
  workflow keeps moving.
- **Evidence block:** For each validation command, provide two separate entries:
  one for the failing (red) run captured before implementation and one for the
  passing (green) rerun after edits. Do not merge red/green output into a single
  execution log.
  - Command executed (label each entry red or green).
  - Timestamp (UTC preferred).
  - Exit status or summary line (non-zero for the red run, zero for green).
  - Optional checksum or key output snippet.
  - Example evidence block:
    ```
    - red | 2025-12-19T17:42Z | exit 1 | scripts/__tests__/property/bootstrap-coordinator.test.ts
        expected helpers: apollo.userDetectedAnalyticsV2
    - green | 2025-12-19T17:55Z | exit 0 | scripts/__tests__/property/bootstrap-coordinator.test.ts
        helpers include apollo.userDetectedAnalyticsV2
    ```
- **Removal test:** What breaks or regresses if this slice is reverted? Explicitly
  confirm the targeted guardrail fails when the behaviour change is rolled back
  (e.g., `git checkout -- path/to/file`) and tighten the test if it remains green.
- **Adversarial “what remains” check:** Re-scan the ADR objectives, tasks, and
  recent loops for unresolved gaps—not just the current slice. Treat this like a
  mini completion pass: for each gap you uncover, either schedule the next loop
  (component + goal) or mark it out-of-repo/no-longer-required with supporting
  evidence.

### 5. Completion & Parking

When you suspect the ADR is satisfied:

1. Re-read all ADR/work-log sections covering its objectives.
2. Run an adversarial completion check and log it as a final entry:
   - Restate the ADR motivation and outcomes in your own words.
   - Hunt for realistic gaps (missing guardrails, untested surfaces, stale tasks).
     For each gap:
     - Land a slice now, **or** note a follow-up task with trigger/evidence,
     - Or mark it out-of-repo/no-longer-required with explicit justification.
    - Provide fresh evidence from this loop (tests rerun today, files re-read,
      dependency diffs) and tie it back to the red/green commands captured in Step
      3/4. If referencing prior evidence, explain why it remains valid and note
      any unchanged sections explicitly.

3. Confirm all ADR tasks/subtasks are closed or formally reclassified.
4. Update ADR status metadata if appropriate and mark the ADR “Accepted” in the
   work-log. No further loops should run unless a new task/regression (with
   trigger) is recorded.

---

## Additional Guidance

- **Scratch planning:** Maintain a private list of upcoming slices, validation
  commands, and file pointers to accelerate future loops. Refresh it whenever the
  plan changes.
- **Task shedding:** To drop a low-value task, use a loop to capture new evidence
  (test output, code review, external decision) showing the task is unnecessary,
  update the ADR task list, and ensure a behaviour/guardrail loop occurs before
  any status-only entry.
- **Targeted tooling:** Prefer focused commands; document rationale and evidence
  when running broad suites or formatters. Include tool versions if relevant.
- **Test placement:** Before writing new tests, confirm the canonical suite or
  harness for the behaviour and note the rationale if creating a new seam.
- **Test value:** Treat automated tests as behavioural guardrails that keep
  refactors safe. Default to high coverage with fast, independent tests. Surface a
  failing test before implementation changes; fall back to manual observation only
  when an automated check cannot expose the issue. Avoid duplicating low-value
  tests by restructuring suites so existing coverage carries the behaviour when it
  already guards the slice.
- **Manual observation evidence:** Behaviour changes may not land without a
  failing automated check. When automation is currently impossible, document the
  attempted commands, why they failed to expose the behaviour, and attach concrete
  artefacts (logs, timestamps, interpretations) before recording the blocker in the
  work-log.
- **Documentation-only slices:** Only acceptable when they encode a concrete
  contract/task decision or retire work with evidence. Each doc-only slice must
  cite the governing ADR clause or requirement and include a removal test
  demonstrating why the doc change matters. If the documentation updates testing
  guidance or guardrail expectations, rerun (or cite fresh evidence from) the
  referenced guardrail. The failing automated test rule applies to behaviour
  changes; doc-only loops satisfy evidence through their cited removal test.
- **Hand-off template:** When another contributor must take over, append a
  hand-off note to the work-log with the following fields:
  - Current focus area and objective.
  - Pending tests or validations.
  - Known risks/open questions.
  - Next candidate slice (component + goal).
- **Project adaptation:** Replace example commands with your repository’s test or
  build tooling. If repo-specific policies exist (e.g., formatting, linting,
  release checklists), follow them alongside this helper. Consider adding a short
  appendix mapping the structured evidence block to local tooling conventions.

By following this helper, each loop lands a well-tested, observable slice; the
work-log remains the single source of truth; and completion checks are decisive
without overfitting to a specific codebase.
