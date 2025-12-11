# 0039 Save Model Exchanges via File Destination – Work Log

## 2025-12-10 (loop 1)
- Slice: introduce a `file` model destination and wire `modelDestination` list mapping.
- Changes:
  - Added a `File` destination to `lib/modelDestination.py` that writes a human-oriented markdown file containing:
    - A header (`saved_at`, `kind=response`, model, recipe/axes, directional).
    - Optional `# Prompt / Context` (from `GPTState.last_prompt_text`).
    - A `# Response` section with the full response body.
  - Resolved the base directory from `user.model_source_save_directory` (expanding `~`), falling back to `~/talon-ai-model-sources`.
  - Extended `GPT/lists/modelDestination.talon-list` with a `to file: file` entry so `file` is a first-class destination token.
  - Added `test_file_destination_writes_markdown_with_response` in `_tests/test_model_destination.py` to exercise the new destination against a temporary directory.
- Validation: `python3 -m pytest _tests/test_model_destination.py`.

## 2025-12-10 (loop 2)
- Slice: migrate bespoke "save source" surfaces to the unified `file` destination.
- Changes:
  - Removed the `model source save file` grammar from `GPT/gpt.talon` and stopped exposing `gpt_save_source_to_file` as a primary surface.
  - Added `confirmation_gui_save_to_file` in `lib/modelConfirmationGUI.py`, which takes the current confirmation text, wraps it in a `PromptResult`, and routes it through the `File` destination.
  - Updated the confirmation GUI advanced actions to expose a "Save to file" button wired to `confirmation_gui_save_to_file` instead of the old source helper.
  - Retargeted model pattern and prompt-pattern GUI save actions (`model_pattern_save_source_to_file`, `prompt_pattern_save_source_to_file`) to delegate to `confirmation_gui_save_to_file`, so all save flows share the same destination semantics.
  - Updated `_tests/test_model_confirmation_gui.py` and `_tests/test_model_pattern_gui.py` to assert that the new save-to-file actions are invoked.
  - Left `gpt_save_source_to_file` as an internal helper only (no grammar or GUI surfaces rely on it), allowing future clean-up if desired.
- Validation: `python3 -m pytest _tests/test_gpt_actions.py _tests/test_model_confirmation_gui.py _tests/test_model_pattern_gui.py`.
