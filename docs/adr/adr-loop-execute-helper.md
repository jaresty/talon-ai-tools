# ADR Loop / Execute Helper Prompt

This file is a small, generic utility prompt for running **loop + execute** iterations over ADRs. It is **not** an ADR itself and is not tied to any specific ADR number.

When asked to “run an ADR loop/execute iteration using `docs/adr/adr-loop-execute-helper.md`”, the assistant should:

0. **Clear known red checks first (hard requirement)**
   - If there are any **known failing tests, lint errors, or type-check failures** in the current repository that the assistant is already aware of from this session (for example, a red `npm test`, `npm run lint`, or `npm run typecheck` that has not yet been addressed), the *first and only* task for this loop **until resolved** must be to fix or explicitly triage those failures.
   - Fixes **must respect test intent**:
     - If a test is failing because requirements have genuinely changed, it is acceptable to update or, in rare cases, remove the test — but only after making the new requirement explicit in the relevant ADR/work-log and ensuring the updated/removed test still reflects a clear, reviewed contract.
     - If the implementation is broken relative to the documented behaviour or test expectations, the implementation must be fixed; do **not** weaken or delete the test just to make the suite green.
   - We **never intentionally leave red tests** in this repository. Any failure encountered during a loop must be brought back to green (via correct implementation or contract update) before moving on.
   - Treat fixing these red checks as an ADR-aligned slice when they are clearly tied to an existing ADR (for example, test guardrails or invariants introduced by a lifecycle ADR like 0107 or a CLI hotspot ADR); otherwise, treat them as preconditions that must be cleared before selecting a new ADR task.
   - The assistant **must not** select a new ADR or start fresh ADR work in this loop while aware of unresolved red tests/lint/type checks. Only once the relevant checks are green again (or a failure is explicitly and temporarily acknowledged/parked in an ADR work-log with rationale as a short-lived regression to be fixed immediately in the next loop) may the assistant proceed to step 1 and pick up a new ADR task below.

1. **Select a target ADR**
   - Prefer an ADR that appears **incomplete** (for example, non-terminal or missing `Status`, an open tasks section, or an active work-log with unfinished material work).
   - If the user has provided a list or ordering of ADRs, respect that as a priority queue and choose the first that still appears incomplete.
   - If no ADR appears incomplete under these heuristics, report that no suitable ADR was found and perform no work.

2. **Run one loop / execute iteration for that ADR**
   - Re-read the ADR and any associated work-log to understand its scope, intent, and current state.
   - **Work-log location and convention:** for each ADR, prefer a dedicated work-log file named `docs/adr/<ADR-NUMBER>-<slug>.work-log.md` (for example, `docs/adr/0118-concordance-churn-complexity-hidden-domain-refresh.work-log.md`). If no such file exists yet for the chosen ADR, create one on first use and record slices there rather than appending large change histories directly to the primary ADR document.
   - Enumerate remaining work and break it down into **atomic, behavior-focused tasks** that you can realize via concrete edits (code, tests, or docs). A single task may involve multiple files or commands as long as it forms one coherent slice (for example, “regenerate fixture X and promote updated artifacts” or “refactor CLI Y behind an orchestrator plus add tests”).
   - Filter to tasks that are **material and behavior-affecting** or clearly improve maintainability/guardrails for the ADR.
   - Choose at least one feasible atomic task to advance, preferring the one that tests or exercises the **riskiest assumption** (the assumption whose failure would most undermine the ADR).
   - Implement the chosen task(s) concretely (edit code/docs/tests), then run minimal, fast checks and fix issues you encounter.
   - Update the ADR’s dedicated work-log and, if present, its “Salient Tasks” section to reflect what changed and what remains, keeping the primary ADR document focused on stable decisions rather than slice-by-slice execution history.
   - If and only if no qualifying tasks remain after a fresh pass and checks are green, you may mark the ADR complete or terminal according to the project’s lifecycle conventions.

Example invocation:

> Run one ADR loop/execute iteration using the helper in `docs/adr/adr-loop-execute-helper.md`, letting you pick any ADR that still looks incomplete, unless I’ve explicitly queued ADRs in this conversation.
