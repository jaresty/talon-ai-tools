# 0038 Save Model Source to File Destination – Work Log

## 2025-12-10 (loop 4)
- Slice: ADR-0038 status reconciliation for this repo.
- Summary: The save-source-to-file behaviour is now implemented and tested across core helper, voice command, confirmation GUI, pattern/prompt GUIs, and request history surfaces; remaining follow-ups (like optional per-entry drawer affordances or "open last saved source") are explicitly recorded as future work rather than blockers.


## 2025-12-10 (loop 1)
- Slice: introduce a core helper and voice command to save the last model source to a markdown file (ADR-0038 – initial implementation).

## 2025-12-10 (loop 2)
- Slice: surface a "Save source to file" control in the confirmation GUI (ADR-0038 – confirmation surface wiring).

## 2025-12-10 (loop 3)
- Slice: add a history-surface helper and voice command to save the latest request's source prompt to a markdown file (ADR-0038 – request history surface wiring).
- Changes:
  - Introduced `_slugify_label`, `_model_source_save_dir`, and `_save_history_prompt_to_file` helpers in `lib/requestHistoryActions.py` to resolve the base directory from `user.model_source_save_directory`, build a timestamped/slugged filename, and write a markdown file containing the history entry's prompt under a shared `talon-ai-model-sources` directory.
  - Added a new `gpt_request_history_save_latest_source` action in `requestHistoryActions` and wired it to `GPT/request-history.talon` as `"model history save source"`.
  - Extended `_tests/test_request_history_actions.py` with `test_history_save_latest_source_writes_markdown_with_prompt`, which points the save directory at a temporary folder, appends a dummy history entry, invokes the new action, and asserts that a markdown file is created containing the prompt text and that at least one notification is emitted.
- Validation: `python3 -m pytest _tests/test_request_history_actions.py`.
- Follow-ups: future ADR-0038 slices can add per-entry save affordances in the history drawer (for arbitrary older entries) and consider a complementary helper to reopen the most recent saved source from history.
- Changes:
  - Added a "Save source to file" button to the advanced actions section of `lib/modelConfirmationGUI.py` that calls `actions.user.gpt_save_source_to_file()`, reusing the helper and action introduced in loop 1.
  - Extended `_tests/test_model_confirmation_gui.py` with `test_save_source_button_triggers_action`, which simulates toggling advanced actions and clicking the new button, then asserts that `gpt_save_source_to_file` is invoked via the Talon `actions.user` stub.
- Validation: `python3 -m pytest _tests/test_model_confirmation_gui.py _tests/test_gpt_actions.py`.
- Follow-ups: consider parallel save-source affordances in the response canvas and request history drawers so GUI and history views remain aligned with ADR-0038.
- Changes:
  - Added `_slugify`, `_model_source_save_dir`, and `_save_source_snapshot_to_file` helpers in `GPT/gpt.py` to resolve the effective model source (preferring `GPTState.last_source_messages` and falling back to the current default source), build a timestamped/slugged filename, and write a header + `# Source` body to a markdown file under a configurable base directory.
  - Taught `gpt_apply_prompt` to capture `GPTState.last_source_key` alongside `last_source_messages` so saved files can include a meaningful `source_type` header.
  - Exposed a new `UserActions.gpt_save_source_to_file` action and wired it to the Talon grammar as `"model source save file"` in `GPT/gpt.talon`.
  - Documented the optional `user.model_source_save_directory` setting in `talon-ai-settings.talon.example`, defaulting to a `talon-ai-model-sources` folder under the Talon user directory when unset.
  - Seeded a focused unit test in `_tests/test_gpt_actions.py` to exercise `gpt_save_source_to_file` against a temporary directory, asserting that a markdown file is created and contains both the source text and a header block.
- Validation: `python3 -m pytest _tests/test_gpt_actions.py`.
- Follow-ups: surface the save-source action in additional UI surfaces (confirmation GUI, pattern/prompt GUIs, and request history drawers) and consider a complementary "open last saved source" helper once users have exercised the basic persistence path.

## 2025-12-10 (loop 5)
- Slice: mark ADR-0038's bespoke save-source helper as superseded by ADR-0039's file destination.
- Summary: While the underlying source-only helpers remain available for advanced/debug cases, the primary user-facing "save" surfaces (confirmation GUI, pattern/prompt GUIs, and history commands) have now been migrated to the `file` destination path introduced in ADR-0039 (`model pass … to file`). New work should rely on the destination-based flow rather than extending `gpt_save_source_to_file`.
