# 030 - Axis token storage and hydration boundary

## Status
Accepted

## Context
- Axis Talon lists store short keys mapped to long, instruction-style descriptions; `model_default_completeness` even defaults to the hydrated text from `completenessModifier.talon-list`.
- `modelPrompt()` writes the effective axis values straight into `GPTState.system_prompt` (lib/talonSettings.py:393-453), so completeness and any hydrated scope/method/style values live in state in their long form.
- To keep the recap and rerun grammar short, those hydrated strings are mapped back to tokens with `_axis_recipe_token()` (lib/talonSettings.py:242-288) before filling `last_recipe`/`last_*`.
- The response canvas recap reads only the tokenised `last_*` fields (lib/modelResponseCanvas.py:565-597), so the UI depends on the heuristic reverse mapping working.
- This coupling makes axis changes brittle: any edits to the long descriptions require regex/substring tolerance in `_axis_recipe_token`, and mismatches silently leak hydrated blobs into UI state.

## Decision
- Treat canonical axis state as the short token set (names) for completeness/scope/method/style; keep hydrated descriptions as a derived view used only when constructing the system prompt for the model.
- Normalise Talon settings and static prompt profiles to store tokens; hydrate to full text at the boundary where we build `GPTSystemPrompt.format_as_array()` or other model-facing strings.
- Replace reverse-mapping heuristics with a single, explicit token->description hydrator; UI recap and rerun logic consume the canonical token state directly.
- Introduce a small migration/normalisation path that maps any legacy hydrated settings back to tokens on load so existing users do not lose defaults.

## Rationale
- Storing canonical tokens avoids brittle string matching and keeps state stable when list descriptions evolve.
- A single hydration boundary reduces duplication and makes it obvious where model-facing instructions come from.
- UI and rerun paths become simpler and more predictable because they no longer depend on best-effort pattern matching.

## Implementation notes
- Add an axis hydration helper that takes a token or token set and returns the mapped description(s) from the Talon lists; use it when building the system prompt lines.
- Update `GPTSystemPrompt`/`modelPrompt` to persist token values in state and hydrate only when producing system messages; keep `_axis_recipe_token` only for legacy heuristics (for example, truncated `samples` variants, directional shorthands).
- Normalise persisted settings/static profiles at startup (e.g., map hydrated strings to tokens once) and store tokens going forward; log unmapped values for follow-up.
- Refresh tests around axis mapping, rerun, and recap to assert token preservation and boundary-only hydration.

## Consequences
- Axis list description edits will not risk breaking UI recap or rerun because state no longer stores hydrated strings.
- System prompt construction gains a clear, testable mapping layer but requires updates to any code that currently assumes hydrated values in `GPTState.system_prompt`.
- One-time normalisation reduces surprise for existing users but may surface legacy values that cannot be mapped, which will need migration guidance.
- UIs (constraints, suggestion picker, response recap) hydrate tokens at display time; verbose hydrated text lives behind meta/toggles to keep recaps concise.
