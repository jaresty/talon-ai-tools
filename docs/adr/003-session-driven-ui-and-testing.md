# ADR 003: Extend PromptSession to UI surfaces and integration tests

- Status: Proposed
- Date: 2025-02-14

## Context
PromptSession now orchestrates GPT requests across most high-traffic actions, and the test harness exercises the new flow. Remaining code paths—particularly confirmation GUI/destination handlers and multi-step conversations—still rely on ad-hoc state changes or lack regression coverage. Aligning these areas with the session pipeline will make behaviour consistent and easier to test.

## Decision
We plan to:
1. Route confirmation GUI and destination insertions through PromptSession-aware helpers so UI surfaces never mutate `GPTState` directly.
2. Introduce integration-style tests that simulate multi-step conversations, thread reuse, and tool-call recursion using the Talon stub harness.
3. Document the workflow in CONTRIBUTING to standardize how new commands and tests interact with PromptSession.

## Consequences
- UI code becomes thinner and easier to reason about, at the cost of refactoring destination insert logic.
- Deeper tests will slow the suite slightly but give confidence when changing orchestration logic.
- Contributors will have clearer guidance, reducing the chance of bypassing PromptSession accidentally.

## Next Steps
1. Refactor `lib/modelDestination.py` and `lib/modelConfirmationGUI.py` to consume a consolidated response object produced by PromptSession.
2. Add integration tests that cover threading, tool recursion, and destination rendering under `tests/`.
3. Update CONTRIBUTING with the PromptSession/testing guidelines already summarized in README.
