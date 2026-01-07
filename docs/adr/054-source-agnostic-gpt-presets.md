# 054 – Source-agnostic GPT presets

## Status
Proposed

## Context
- `model preset save <name>` captures the last recipe’s stance (persona/intent) and contract axes, then the new `model run [source] [destination] preset <name>` command seeds `GPTState` and replays the recipe through `gpt_rerun_last_recipe`.
- During replay, `gpt_rerun_last_recipe` first checks `GPTState.last_source_messages`; if present it reuses the cached transcript, otherwise it falls back to `user.model_default_source`.
- Users expecting presets to behave like any other `model run …` call often hit two failure modes:
  - The original cached messages run again instead of the freshly selected text.
  - When no cached messages remain and nothing is selected the rerun executes with an empty subject, causing the response to feel context-free.
- Destination handling is similarly opaque: presets silently reuse the last implicit destination unless the user resorts to a follow-up `model run <source> again` command.

## Decision
- Treat presets as stance + contract bundles only; do **not** reuse cached source messages when executing a preset.
- Introduce a new voice grammar entry: `model run [<user.modelSimpleSource>] [<user.modelDestination>] preset <user.text>`.
  - When a source token is spoken, resolve it via `create_model_source`; otherwise fall back to `user.model_default_source`.
  - When a destination token is spoken, resolve it via `create_model_destination`; otherwise fall back to `user.model_default_destination` while still seeding the preset’s saved destination kind if present.
- Retire the legacy `model preset run <name>` command so presets are only executed through the explicit `model run … preset …` path, avoiding confusion between behaviours.
- Update confirmation/recap surfaces so that running a preset explicitly reports the chosen source and destination alongside the stance summary.

## Rationale
- Aligns preset ergonomics with the core `model run …` grammar by keeping source selection an explicit, per-invocation concern.
- Removes confusing magic where presets “remember” old context, making them reliable shortcuts instead of behaving like history replays.
- Encourages users to combine presets with the existing source/destination vocabulary, improving clarity for voice-only workflows.

## Implementation Plan
1. Refactor `gpt_preset_run` to clear or bypass `GPTState.last_source_messages` before delegating, ensuring every execution resolves a fresh source.
2. Add a `user.gpt_run_preset_with_source(destination, preset_name)` action that:
   - Hydrates stance/contract state from the preset.
   - Resolves optional spoken source/destination tokens.
   - Calls the existing `gpt_rerun_last_recipe_with_source` helper.
3. Extend `GPT/gpt.talon` with the `model run [source] [destination] preset <name>` rule and remove the older `model preset run <name>` capture so there is a single command path.
4. Update quick-help text and any confirmation UI strings to mention the new command form and explicit source/destination behaviour.
5. Add regression tests in `_tests/test_gpt_actions.py` (and related suggestion history tests) covering:
   - Running a preset with and without explicit source tokens.
   - Verifying cached source messages are ignored after the refactor.
   - Confirming destination overrides take effect.

## Consequences
- Users gain predictable, source-specific presets without memorising follow-up commands.
- Removing the legacy alias avoids mixing behaviours; recordings that relied on it must migrate to the explicit `model run … preset …` command.
- Slight initial migration cost: documentation and guardrail fixtures must be refreshed to include the new grammar line and recap strings.
- Removes one avenue for accidental data leakage where old clipboard/selection content might otherwise rerun unexpectedly.

## Alternatives Considered
- Adding a separate `model preset run fresh <name>` command while keeping current behaviour as default — rejected to avoid two competing semantics.
- Forcing presets to prompt for a source interactively — rejected to keep voice-first flows quick and non-modal.
