# ADR Loop / Execute Helper Prompt

This file is a small, generic utility prompt for running **loop + execute** iterations over ADRs. It is **not** an ADR itself and is not tied to any specific ADR number.

When asked to “run an ADR loop/execute iteration using this helper”, the assistant should **decide autonomously** which ADR and slice to target, without asking the user to choose, and should bias toward slices that exercise the riskiest assumptions early — including end‑to‑end flows that validate real CLI behaviour, not just local refactors.

0. **Clear known red checks first (hard requirement)**
   - If there are any **known failing tests, lint errors, or type-check failures** in the current codebase that the assistant is already aware of from this session (for example, a red `npm test`, `npm run lint`, or `npm run typecheck` that has not yet been addressed), the *first and only* task for this loop **until resolved** must be to fix or explicitly triage those failures.
   - Fixes **must respect test intent**:
     - If a test is failing because requirements have genuinely changed, it is acceptable to update or, in rare cases, remove the test — but only after making the new requirement explicit in the relevant ADR/work-log and ensuring the updated/removed test still reflects a clear, reviewed contract.
     - If the implementation is broken relative to the documented behaviour or test expectations, the implementation must be fixed; do **not** weaken or delete the test just to make the suite green.
   - We **never intentionally leave red tests** in this codebase. Any failure encountered during a loop must be brought back to green (via correct implementation or contract update) before moving on.
   - Treat fixing these red checks as an ADR-aligned slice when they are clearly tied to an existing ADR (for example, test guardrails or invariants introduced by a lifecycle ADR or a CLI hotspot ADR); otherwise, treat them as preconditions that must be cleared before selecting a new ADR task.
   - The assistant **must not** select a new ADR or start fresh ADR work in this loop while aware of unresolved red tests/lint/type checks. Only once the relevant checks are green again (or a failure is explicitly and temporarily acknowledged/parked in an ADR work-log with rationale as a short-lived regression to be fixed immediately in the next loop) may the assistant proceed to step 1 and pick up a new ADR task below.

1. **Select a target ADR**
   - Prefer an ADR that appears **incomplete** (for example, non-terminal or missing `Status`, an open tasks section, or an active work-log with unfinished material work).
   - When several ADRs are incomplete, **prioritise those that are closest to completion** (for example, ones where most Salient Tasks are marked done and remaining work is narrow and well-understood) so that loops tend to drive ADRs to terminal states and limit concurrent work-in-progress across many ADRs. This prioritisation is about **which ADR** to work on; slice size for that ADR (small vs larger, end-to-end slices) is chosen independently in step 2 based on risk and feasibility, not to favour smallness for its own sake.
   - If the user has provided a list or ordering of ADRs, treat that as a priority queue and choose the first that still appears incomplete, but **do not** stop to ask the user which ADR to pick; the assistant is expected to make this choice.
   - If no ADR appears incomplete under these heuristics, report that no suitable ADR was found and perform no work.

2. **Run one loop / execute iteration for that ADR**
   - Re-read the ADR and any associated work-log to understand its scope, intent, and current state.
   - **Work-log location and convention:** for each ADR, prefer a dedicated work-log file alongside the primary ADR document, following a convention such as `<ADR-NUMBER>-<slug>.work-log.md` (for example, `0118-example-adr.work-log.md`). If no such file exists yet for the chosen ADR, create one on first use and record slices there rather than appending large change histories directly to the primary ADR document.
   - Enumerate remaining work and break it down into **behavior-focused tasks** that you can realize via concrete edits (code, tests, or docs), and the **validation flows** that demonstrate those behaviours end‑to‑end.
     - Prioritise tasks that **clarify or test the riskiest assumptions first** (for example, assumptions about end‑to‑end workflows, critical invariants, or cross‑component contracts such as API interactions or persistence semantics). Size is secondary to risk: choose slices that give the most information about whether the ADR’s core bets actually hold.
     - **Larger, well-scoped slices (including refactors or end-to-end workflows) are explicitly allowed and often preferred early** when they best exercise a high-risk or poorly understood assumption, as long as they can reasonably be completed within a single loop. When taking a larger slice:
       - Outline a short, concrete plan before editing code.
       - Keep the work bounded to a coherent theme (for example, a specific hotspot, workflow, or end‑to‑end run) that can reasonably be completed within this loop.
       - Plan **end-to-end validation** up front: when applicable, run the real commands or workflows the ADR cares about for at least one realistic target, not just unit tests.
     - Use **small, atomic slices** when a meaningful micro-task exists that clearly de-risks a larger change (for example, adding a missing characterisation test, extracting a helper that multiple callers will use, or landing a trivial-but-risky bugfix). A single slice may still involve multiple files or commands as long as it forms one coherent unit (for example, "regenerate fixture X and promote updated artifacts" or "refactor CLI Y behind an orchestrator plus add tests").
   - Avoid **deferral-only** slices:
     - Do not treat “write more ADRs” or “move work into a future ADR” as a valid outcome on its own; when you touch an ADR via this helper, land at least one concrete improvement (code, tests, or a clearly behavior-describing doc change) in this repo.
     - Successor ADRs and “future round” notes are fine, but only **alongside** behavior-level work; they should describe or coordinate work you are actually doing, not replace it.
     - Pure documentation slices (ADR text/work-log only) are acceptable occasionally when they clarify already-implemented behaviour or reconcile ADRs with the current code/tests, but must not be used to avoid obvious, in-scope behavior changes the ADR already calls for.
   - Filter to tasks that are **material and behavior-affecting** or clearly improve maintainability/guardrails for the ADR.
   - Choose at least one feasible task to advance, **without asking the user to choose among options**, and prefer the one that tests or exercises the **riskiest assumption** (the assumption whose failure would most undermine the ADR), even if that implies a larger, end‑to‑end slice.
   - For larger slices, outline a short, concrete plan in your response (a few ordered steps) before you start editing code, then implement that plan within this loop.
   - Implement the chosen task(s) concretely (edit code/docs/tests), then run **both focused tests and the relevant end‑to‑end commands** to validate behaviour:
     - For pure library/refactor work, this may be unit + integration tests.
     - For CLI/generator/verification work, this should include running the entrypoints or workflows the ADR talks about for at least one realistic target.
     - Respect existing project constraints around environments, fixtures, and test data, and record important validation commands and outcomes in the ADR work-log.
   - Update the ADR’s dedicated work-log and, if present, its “Salient Tasks” section to reflect what changed and what remains, keeping the primary ADR document focused on stable decisions rather than slice-by-slice execution history.
   - When you conclude that the remaining meaningful work for an ADR should be **deferred to future ADRs** (for example, because it represents a larger, multi-step lifecycle project), you must:
     - Write or extend the appropriate successor ADR(s) to own that work explicitly, and
     - Update the current ADR and/or its work-log to point to those successor ADRs, rather than leaving vague references to "future ADRs" without concrete ids.
   - If and only if no qualifying tasks remain after a fresh pass and checks are green, you may mark the ADR complete or terminal according to the project’s lifecycle conventions.

Example invocation:

> Run one ADR loop/execute iteration using this ADR loop helper prompt, letting you pick any ADR that still looks incomplete. You should autonomously select the ADR and slice, and you may choose either a small, focused slice or, when it adds more value (especially to drive out risky assumptions early), a larger but well-scoped refactor or workflow for that ADR, as long as you plan it and validate behaviour within this loop.
