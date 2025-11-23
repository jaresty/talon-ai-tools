# ADR Loop / Execute Helper Prompt

This file is a small, generic utility prompt for running **loop + execute** iterations over ADRs. It is **not** an ADR itself and is not tied to any specific ADR number.

When asked to “run an ADR loop/execute iteration using `docs/adr/adr-loop-execute-helper.md`”, the assistant should:

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

