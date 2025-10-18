# ADR 004: Dynamic Self-Recursive ChatGPT Architecture

- Status: Proposed
- Date: 2025-02-14

## Context
Talon-AI-Tools currently orchestrates GPT calls through a single PromptSession pipeline. We want to explore more advanced behaviours where ChatGPT can recursively call itself—spawning delegate prompts, reflecting on intermediate results, and deciding when to stop—without hard-coded control flow. This meta-prompting approach should support decomposition, iteration, and multi-perspective synthesis while preserving guardrails.

## Decision
Introduce a layered orchestration model:
1. **Controller Session**: A top-level PromptSession that holds global context and has explicit permission (via system instructions) to emit structured recursion requests (e.g., `{"action": "call_self", ...}`).
2. **Delegate Sessions**: Dynamically instantiated PromptSessions created when the controller requests sub-tasks; each receives tailored prompts/roles.
3. **Synthesizer Phase**: The controller merges delegate outputs, reflects on confidence, and may spawn additional delegates or return the final answer.

The orchestrator will: interpret structured recursion directives, spawn delegate sessions, enforce depth/limit constraints, and feed results back to the controller. Delegates can be assigned roles (summarizer, critic, transformer) depending on the controller’s request.

## Consequences
- Enables adaptive recursion: ChatGPT decides when and how to branch or iterate, leading to richer reasoning without hand-coded flows.
- Requires guardrails: recursion depth limits, structured response validation, and context compression to avoid runaway loops and token exhaustion.
- Prompts must be carefully crafted so the controller understands how to request sub-calls and when to stop.

## Implementation Sketch
1. **Structured Response Schema**: Define JSON-like blocks (`call_self`, `reflection`, `next_action`) that the controller may emit.
2. **Session Graph**: Maintain a graph of PromptSessions with parent-child relationships, merging delegate outputs back into the controller state.
3. **Guardrails**: Enforce max depth (e.g., 3), cap delegate count, and require confidence thresholds before continuing recursion.
4. **Prompt Engineering**: Update controller system prompts to explain available recursion modes (decomposition, iteration, perspective splitting, transformation) and instruct on when to use them.
5. **Testing**: Add integration tests that simulate multi-step flows—controller delegates to critic & synthesizer, etc.—and verify halting conditions.

## Next Steps
1. Extend PromptSession to recognize controller/ delegate roles and structured recursion directives.
2. Implement orchestrator logic that spawns delegate sessions when instructed, respecting guardrails.
3. Craft controller/delegate prompts describing available recursion modes and reflection protocol.
4. Add integration tests covering decomposition, iteration, and perspective splitting, ensuring sessions merge results correctly.
5. Document the recursive calling interface for contributors.
