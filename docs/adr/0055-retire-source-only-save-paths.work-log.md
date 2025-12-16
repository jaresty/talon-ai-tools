# ADR-0055 Work Log

## 2025-12-15 – Loop 1 (kind: behaviour)
- Focus: retire the exposed source-only save action and its guardrails; align settings/help copy with the unified `file` destination.
- Change: removed the public `UserActions.gpt_save_source_to_file` entrypoint and pruned its source-only guardrails/tests, including `_tests/test_gpt_source_snapshot.py`; refreshed `lib/talonSettings.py` and `talon-ai-settings.talon.example` copy to point to the `file` destination; updated `GPT/gpt.py` commentary to frame source snapshots as a debug-only affordance.
- Artefact deltas: `GPT/gpt.py`, `_tests/test_gpt_actions.py`, `_tests/test_gpt_source_snapshot.py` (deleted), `lib/talonSettings.py`, `talon-ai-settings.talon.example`.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass, 101 tests).
- Removal test: reverting would reintroduce a user-facing source-only save action/tests and reinsert settings/help text for the deprecated pathway, undermining ADR-0055’s push toward the `file` destination as the single save surface.

## 2025-12-15 – Loop 2 (kind: behaviour)
- Focus: repoint history saves to the unified `file` destination shape (prompt + response + meta) instead of prompt-only snapshots.
- Change: updated `lib/requestHistoryActions.py::_save_history_prompt_to_file` to write prompt/response/meta sections and notify with “Saved history to …”; adjusted history save guardrails to reflect the new content shape and updated expectations in `_tests/test_request_history_actions.py`.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass, 92 tests).
- Removal test: reverting would restore prompt-only history saves and their guardrails, reintroducing the source-only artefact ADR-0055 aims to retire and breaking the unified `file` destination contract for history saves.

## 2025-12-15 – Loop 3 (kind: behaviour)
- Focus: retire the “history save source” surface in favour of an exchange-oriented command aligned with the unified `file` destination.
- Change: renamed the Talon grammar to `model history save exchange`, refreshed notifications and README/help strings to point at the new command and exchange payload, and updated guardrails for Talon grammar and README coverage.
- Artefact deltas: `GPT/request-history.talon`, `readme.md`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_talon_commands.py`, `_tests/test_readme_history_commands.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_show_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py` (pass, 94 tests).
- Removal test: reverting would reintroduce the “save source” command/copy and break guardrails that now expect the exchange-focused save surface, moving the ADR back toward the deprecated prompt-only flow.

## 2025-12-15 – Loop 4 (kind: behaviour)
- Focus: remove the unused source-only save helper to retire residual source-only code paths.
- Change: deleted `_save_source_snapshot_to_file` and its slug/dir helpers from `GPT/gpt.py`, fully eliminating the source-only snapshot code path now that no grammar or tests depend on it.
- Artefact deltas: `GPT/gpt.py`.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py _tests/test_request_history_actions.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py` (pass, 195 tests).
- Removal test: reverting would reintroduce the source-only snapshot helper, expanding the surface for deprecated save behaviour and increasing drift risk against ADR-0055’s single `file` destination model.

## 2025-12-15 – Loop 5 (kind: status, adversarial completion check)
- Focus: confirm ADR-0055 is complete for this repo and align status.
- Adversarial check: scanned `readme.md` (history section), `GPT/request-history.talon`, `lib/requestHistoryActions.py`, and the ADR text to look for remaining source-only surfaces or help/grammar drift. No remaining callable/action-tested source-only helpers or commands exist; history saves and copy/open/show flows point to the exchange command and file destination. Potential gap considered: older work-logs still mention "save source" phrasing, but no runtime surfaces or guardrails depend on it; leaving historical notes intact is acceptable.
- Change: marked ADR status Accepted to reflect completion in this repo.
- Artefact delta: `docs/adr/0055-retire-source-only-save-paths.md`.
- Checks: no new tests run (doc/status-only change); evidence gathered via re-reading the files listed above this loop.
- Removal test: reverting the status change would re-open ADR-0055 despite no remaining in-repo work, creating churn and ambiguity for future loops.

## 2025-12-15 – Loop 6 (kind: docs/guardrail)
- Focus: clean up lingering "history save source" wording in historical ADR-0054 work-log to reflect the renamed exchange command.
- Change: updated `docs/adr/0054-concordance-axis-canvas-request-code-quality.work-log.md` to reference `model history save exchange` (formerly `save source`) so downstream readers and tests don’t point at the retired command.
- Artefact deltas: `docs/adr/0054-concordance-axis-canvas-request-code-quality.work-log.md`.
- Checks: `python3 -m pytest _tests/test_readme_history_commands.py` (pass).
- Removal test: reverting would reintroduce doc/copy drift that directs readers to the deprecated "save source" command, weakening ADR-0055’s single-surface intent and breaking the updated guardrail wording.

## 2025-12-15 – Loop 7 (kind: status, adversarial completion check)
- Focus: confirm no remaining in-repo work for ADR-0055 after renames/cleanup.
- Adversarial check: reran `rg "save source" --glob '!docs/adr/*'` and `rg "history save source"` to look for residual source-only surfaces; none found outside ADR history. Re-reviewed `GPT/request-history.talon` and `readme.md` to ensure the exchange command is the only live surface.
- Change: recorded completion confirmation; ADR remains Accepted with no in-repo follow-ups.
- Artefact delta: this work-log entry.
- Checks: no new tests (status-only); evidence via the ripgrep commands and file re-reads above.
- Removal test: dropping this entry would hide the completion check, reducing traceability on why ADR-0055 is considered fully implemented in this repo.

## 2025-12-15 – Loop 8 (kind: guardrail/tests)
- Focus: add a guardrail to prevent reintroducing the deprecated `history save source` command outside ADR history.
- Change: added `_tests/test_no_source_only_saves.py` to scan the repo (excluding ADRs and cache/tmp artefacts) and fail if the old command string resurfaces.
- Artefact delta: `_tests/test_no_source_only_saves.py`.
- Checks: `python3 -m pytest _tests/test_no_source_only_saves.py` (pass).
- Removal test: reverting would drop the guardrail, making it easier to accidentally reintroduce the deprecated command in docs or Talon grammar, weakening ADR-0055 enforcement.

## 2025-12-15 – Loop 9 (kind: guardrail/tests)
- Focus: broaden the guardrail to catch other source-only save strings (e.g., `model source save`, `save source to file`) outside ADR history.
- Change: expanded `_tests/test_no_source_only_saves.py` to scan for multiple deprecated tokens, keeping exclusions for ADR/history/cache artefacts.
- Artefact delta: `_tests/test_no_source_only_saves.py`.
- Checks: `python3 -m pytest _tests/test_no_source_only_saves.py` (pass).
- Removal test: reverting would weaken coverage by only blocking a single phrasing of the deprecated command, increasing the chance of reintroducing source-only save language.

## 2025-12-15 – Loop 10 (kind: behaviour/guardrail)
- Focus: silence Talon deprecation warnings and harden history save open/copy flows.
- Change: refactored history save path retrieval into `_last_history_save_path` and switched copy/open/show helpers to use it directly (no action-class indirection), avoiding the deprecated `UserActions.*` attribute access warning. Added a graceful fallback when `app.open` is unavailable and kept notifications/state handling intact.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_open_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_open_last_save_path.py _tests/test_request_history_actions.py _tests/test_no_source_only_saves.py` (pass).
- Removal test: reverting would bring back the deprecated action_class call (warning) and brittle `app.open` handling, risking user-facing errors when the action is unavailable.
