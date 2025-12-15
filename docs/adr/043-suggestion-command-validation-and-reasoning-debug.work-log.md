# 043 – Suggestion command validation and reasoning – Work log

## 2025-12-11 – JSON/legacy validation and debug reasoning slice

- Implemented shared stance validator wiring and GUI layout improvements in earlier loops.
- Added structured validation for JSON `model suggest` responses in `GPT/gpt.py::gpt_suggest_prompt_recipes_with_source`:
  - Collects a `debug_failures` list with per-suggestion `name`, `raw` fields (recipe, axes, stance_command, reasoning), and failure codes.
  - Records failures for missing name/recipe, invalid recipes, and invalid stance commands.
  - When `GPTState.debug_enabled` is true, emits a single consolidated `print` log summarising up to 5 failed suggestions, including truncated reasoning.
- Tightened legacy (pipe-separated) suggestion parsing:
  - Applies `valid_stance_command` to legacy `Stance:` lines before surfacing them as `stance_command`.
  - In debug mode, logs invalid legacy stance commands instead of surfacing them.
- Added `_tests/test_gpt_suggest_validation.py`:
  - Feeds a JSON payload with one valid and one invalid stance plus reasoning through `gpt_suggest_prompt_recipes`.
  - Asserts that both suggestions are recorded, but only the valid one keeps `stance_command`.
- Ran focused tests:
  - `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py _tests/test_suggestion_stance_validation.py`
  - All passing.

Follow-ups for ADR 043:
- Consider tightening `valid_stance_command` so `model write` tails are restricted more strictly to the union of axis tokens, not just presence of a intent token.
- Add optional hooks to surface `debug_failures` through a more structured debug logging facility if/when one is introduced for GPT flows.
