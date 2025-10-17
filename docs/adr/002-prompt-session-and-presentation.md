# ADR 002: Formalize Prompt Session and Presentation Domains

- Status: Proposed
- Date: 2025-02-14

## Context
Churn and branching concentrate in the GPT orchestration layer (`lib/modelHelpers.py`, `GPT/gpt.py`, `lib/modelConfirmationGUI.py`). These files coordinate Talon actions, prompt sources and destinations, HTTP calls, and presentation. Coordination is mostly implicit via `GPTState` and `actions.user` side effects, so changing one concern regularly forces edits in the others.

## Decision
1. Introduce a `PromptSession` domain:
   - Wrap `GPTState` in a class that exposes lifecycle methods (`prepare_request`, `execute`, `append_thread`).
   - Split request assembly, tool execution, and HTTP transport into focused collaborators (for example, `RequestBuilder`, `ToolRunner`, `Transport`).
   - Provide a Talon adapter layer so voice actions call explicit methods instead of touching globals.

2. Create a `PromptPipeline` facade for voice commands:
   - Encapsulate source gathering, prompt configuration, and destination selection behind a single service that returns structured responses.
   - Move capture return types (`ApplyPromptConfiguration`, `PassConfiguration`) into this module so grammar changes don’t leak across files.

3. Define a `ResponsePresentation` contract:
   - Standardize how responses are rendered (text, snippet, thread diff, rich HTML) before destinations consume them.
   - Update confirmation GUI, clipboard, browser, and TTS handlers to rely on this contract, eliminating duplicated string assembly.

## Consequences
- Higher initial refactor cost and temporary duplication while migrating to the new interfaces.
- Enables isolated testing of prompt sessions and presentations without the Talon runtime.
- Reduces coordination cost when adding new sources, destinations, or UI surfaces because each domain has clearer boundaries.

## Next Steps
1. Spike the `PromptSession` prototype and map existing `GPTState` usage to method calls.
2. Migrate a high-traffic command (`gpt_run_prompt`) to the new pipeline to validate ergonomics.
3. Roll the presentation contract into GUI and browser destinations, then retire legacy helpers.
