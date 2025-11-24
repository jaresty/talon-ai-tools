# ADR Loop / Execute Helper Prompt

This file is a small, generic utility prompt for running **loop + execute** iterations over ADRs. It is **not** an ADR itself and is not tied to any specific ADR number.

When asked to “run an ADR loop/execute iteration using `docs/adr/adr-loop-execute-helper.md`”, the assistant should:

0. **Clear known red checks first**
   - If there are any **known failing tests, lint errors, or type-check failures** in the current repository that the assistant is already aware of from this session (for example, a red `npm test`, `npm run lint`, or `npm run typecheck` that has not yet been addressed), the *first* task for this loop must be to fix or explicitly triage those failures.
   - Treat fixing these red checks as an ADR-aligned slice when they are clearly tied to an existing ADR (for example, test guardrails or invariants introduced by a lifecycle ADR like 0107 or a CLI hotspot ADR); otherwise, treat them as preconditions that must be cleared before selecting a new ADR task.
   - Only once the relevant checks are green again (or a failure is explicitly and temporarily acknowledged/parked in an ADR work-log with rationale) may the assistant pick up a new ADR task below.

1. **Select a target ADR**
   - Prefer an ADR that appears **incomplete** (for example, non-terminal or missing `Status`, an open tasks section, or an active work-log with unfinished material work).
   - If the user has provided a list or ordering of ADRs, respect that as a priority queue and choose the first that still appears incomplete.
   - If no ADR appears incomplete under these heuristics, report that no suitable ADR was found and perform no work.

2. **Run one loop / execute iteration for that ADR**
   - Re-read the ADR and any associated work-log to understand its scope, intent, and current state.
   - Enumerate remaining work and break it down into **atomic, text-edit-level tasks** (code, tests, or docs).
   - Filter to tasks that are **material and behavior-affecting** or clearly improve maintainability/guardrails for the ADR.
   - Choose at least one feasible atomic task to advance, preferring the one that tests or exercises the **riskiest assumption** (the assumption whose failure would most undermine the ADR).
   - Implement the chosen task(s) concretely (edit code/docs/tests), then run minimal, fast checks and fix issues you encounter.
   - Update any relevant work-log or “Salient Tasks” section to reflect what changed and what remains.
   - If and only if no qualifying tasks remain after a fresh pass and checks are green, you may mark the ADR complete or terminal according to the project’s lifecycle conventions.

Example invocation:

> Run one ADR loop/execute iteration using the helper in `docs/adr/adr-loop-execute-helper.md`, letting you pick any ADR that still looks incomplete, unless I’ve explicitly queued ADRs in this conversation.
