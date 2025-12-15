# ADR-0054 Work Log

## 2025-12-15 – Loop 1 (kind: status/plan)
- Focus: kick off ADR-0054 execution; no code changes yet.
- Artefacts inspected: `tmp/churn-scan/line-hotspots.json` (top nodes), `docs/adr/0054-concordance-axis-canvas-request-code-quality.md` (decisions/tasks).
- Notes/next slices:
  - Axis SSOT: add shared serializer + regen command; wire `axisConfig`/static prompt builders/README+lists to it; refresh fixtures.
  - Canvas overlays: add overlay helper atop `lib/helpUI.py` for scroll/key/mouse/close; migrate `modelPatternGUI` + `modelPromptPatternGUI` first.
  - Request pipeline: expose lifecycle hooks in `lib/requestController.py`; thread streaming/error/history from `lib/modelHelpers.py` and GPT entrypoints.
- Removal test: dropping this entry would remove the recorded focus and next-slice plan for ADR-0054, increasing ambiguity for follow-up loops.

## 2025-12-15 – Loop 2 (kind: guardrail/tests)
- Focus: Axis registry SSOT guardrail.
- Change: Added `_tests/test_generate_axis_config.py` to ensure `lib/axisConfig.py` stays in sync with the registry-driven generator (`scripts/tools/generate_axis_config.py`), surfacing drift early per ADR-0054 plan.
- Artefact delta: new test file `_tests/test_generate_axis_config.py`.
- Checks: `python3 -m pytest _tests/test_generate_axis_config.py` (pass).
- Removal test: reverting this loop removes the guardrail; drift between axis registry and `axisConfig` would go undetected, weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 3 (kind: guardrail/tests)
- Focus: Axis SSOT generator outputs for downstream consumers.
- Change: Extended `scripts/tools/generate_axis_config.py` with `--json` output (structured axis map) and added JSON drift guardrail in `_tests/test_generate_axis_config.py`.
- Artefact deltas: `scripts/tools/generate_axis_config.py`, `_tests/test_generate_axis_config.py`.
- Checks: `python3 -m pytest _tests/test_generate_axis_config.py` (pass, covers mapping and JSON output).
- Removal test: reverting would drop the structured SSOT output and its guardrail, reducing visibility for tooling that needs the registry map and weakening ADR-0054 axis SSOT plan.

## 2025-12-15 – Loop 4 (kind: behaviour)
- Focus: Canvas overlay helpers for consistent mouse capture.
- Change: Introduced shared helper `lib/overlayHelpers.py` to set canvas mouse-capture flags and applied it to `lib/modelPromptPatternGUI.py` and `lib/requestHistoryDrawer.py` to consolidate duplicated block_mouse handling.
- Artefact deltas: `lib/overlayHelpers.py`, `lib/modelPromptPatternGUI.py`, `lib/requestHistoryDrawer.py`.
- Checks: `python3 -m pytest _tests/test_generate_axis_config.py` (pass; sanity run after changes).
- Removal test: reverting would reintroduce duplicated, inconsistent mouse capture setup across canvases, increasing risk of interaction regressions and weakening the ADR-0054 overlay-alignment goal.

## 2025-12-15 – Loop 5 (kind: behaviour)
- Focus: Extend overlay helper into help hub canvas setup.
- Change: Wired `lib/helpHub.py` canvas creation to use `set_canvas_block_mouse`, reducing bespoke block_mouse/blocks_mouse handling.
- Artefact deltas: `lib/helpHub.py`.
- Checks: `python3 -m pytest _tests/test_generate_axis_config.py` (pass; quick sanity after change).
- Removal test: reverting would leave help hub with bespoke mouse-block handling, diverging from shared overlay helper and increasing maintenance/coordination cost noted in ADR-0054.

## 2025-12-15 – Loop 6 (kind: behaviour)
- Focus: Continue overlay alignment across canvases.
- Change: Applied shared `set_canvas_block_mouse` helper to `lib/modelHelpCanvas.py`, `lib/modelResponseCanvas.py`, and `lib/modelSuggestionGUI.py` to consolidate mouse-capture setup.
- Artefact deltas: `lib/modelHelpCanvas.py`, `lib/modelResponseCanvas.py`, `lib/modelSuggestionGUI.py`.
- Checks: `python3 -m pytest _tests/test_generate_axis_config.py` (pass; sanity after changes).
- Removal test: reverting would reintroduce per-canvas mouse-block logic, undermining ADR-0054’s goal of consistent overlay behaviour and increasing coordination cost.

## 2025-12-15 – Loop 7 (kind: behaviour)
- Focus: Pattern picker overlay alignment.
- Change: Updated `lib/modelPatternGUI.py` to use shared `set_canvas_block_mouse`, eliminating bespoke mouse-block setup.
- Artefact delta: `lib/modelPatternGUI.py`.
- Checks: `python3 -m pytest _tests/test_generate_axis_config.py` (pass; quick sanity after change).
- Removal test: reverting would leave the pattern picker with divergent mouse-capture handling, increasing maintenance drift across canvases flagged by ADR-0054.

## 2025-12-15 – Loop 8 (kind: behaviour)
- Focus: Ensure overlay mouse-capture helper is applied across fallback canvas creation paths.
- Change: Moved mouse-capture setup to run after canvas creation in `lib/modelHelpCanvas.py`, `lib/modelResponseCanvas.py`, `lib/modelSuggestionGUI.py`, `lib/modelPatternGUI.py`, and `lib/modelPromptPatternGUI.py`, covering both primary and fallback creation branches.
- Artefact deltas: `lib/modelHelpCanvas.py`, `lib/modelResponseCanvas.py`, `lib/modelSuggestionGUI.py`, `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`.
- Checks: `python3 -m pytest _tests/test_generate_axis_config.py` (pass; sanity after changes).
- Removal test: reverting would leave fallback canvas branches without consistent mouse-capture setup, reintroducing the coordination gaps ADR-0054 aims to close.

## 2025-12-15 – Loop 9 (kind: behaviour)
- Focus: Align keyboard capture with shared overlay helper across canvases.
- Change: Added `set_canvas_block_keyboard` helper and applied mouse+keyboard blocking post-creation in `lib/helpHub.py`, `lib/modelHelpCanvas.py`, `lib/modelResponseCanvas.py`, `lib/modelSuggestionGUI.py`, `lib/modelPatternGUI.py`, and `lib/modelPromptPatternGUI.py` to cover primary and fallback canvas paths.
- Artefact deltas: `lib/overlayHelpers.py`, `lib/helpHub.py`, `lib/modelHelpCanvas.py`, `lib/modelResponseCanvas.py`, `lib/modelSuggestionGUI.py`, `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`.
- Checks: `python3 -m pytest _tests/test_generate_axis_config.py` (pass; sanity after changes).
- Removal test: reverting would leave keyboard capture inconsistent across overlays, reintroducing the coordination gaps ADR-0054 targets.

## 2025-12-15 – Loop 10 (kind: guardrail/tests)
- Focus: Guardrail for overlay helper behaviour.
- Change: Added `_tests/test_overlay_helpers.py` to assert mouse/keyboard block helpers set available attributes on a dummy canvas.
- Artefact delta: `_tests/test_overlay_helpers.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py` (pass).
- Removal test: reverting would drop coverage of overlay helper behaviour, reducing confidence in the shared overlay alignment under ADR-0054.

## 2025-12-15 – Loop 11 (kind: behaviour)
- Focus: Extend shared overlay helper coverage to remaining canvases.
- Change: Applied mouse+keyboard blocking helpers to `lib/requestHistoryDrawer.py` and `lib/pillCanvas.py`, covering history drawer and progress pill canvases including fallback recreation paths.
- Artefact deltas: `lib/requestHistoryDrawer.py`, `lib/pillCanvas.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py` (pass; sanity after changes).
- Removal test: reverting would leave these canvases with bespoke or missing keyboard/mouse capture, reintroducing coordination gaps against ADR-0054 overlay alignment goals.

## 2025-12-15 – Loop 12 (kind: behaviour/guardrail)
- Focus: Reduce duplication in overlay blocking and guardrail the combined helper.
- Change: Added `apply_canvas_blocking` helper and updated all canvases to use it instead of manual mouse+keyboard calls; extended `_tests/test_overlay_helpers.py` to cover the combined helper.
- Artefact deltas: `lib/overlayHelpers.py`, `lib/helpHub.py`, `lib/modelHelpCanvas.py`, `lib/modelResponseCanvas.py`, `lib/modelSuggestionGUI.py`, `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`, `lib/requestHistoryDrawer.py`, `lib/pillCanvas.py`, `_tests/test_overlay_helpers.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py` (pass).
- Removal test: reverting would bring back duplicated per-canvas blocking logic and drop coverage for the combined helper, increasing coordination cost and risk for ADR-0054 overlay consistency.

## 2025-12-15 – Loop 13 (kind: guardrail/tests)
- Focus: Robustness of shared overlay blocking helper.
- Change: Made overlay helper functions no-op on `None` and added a guardrail test ensuring `apply_canvas_blocking` tolerates `None` inputs.
- Artefact deltas: `lib/overlayHelpers.py`, `_tests/test_overlay_helpers.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py` (pass).
- Removal test: reverting would reintroduce potential None handling errors and remove coverage for this robustness, weakening ADR-0054 overlay helper safety.

## 2025-12-15 – Loop 14 (kind: guardrail/tests)
- Focus: Guardrail entrypoint for overlay helper checks.
- Change: Added `overlay-guardrails` Make target to run `_tests/test_overlay_helpers.py`, making overlay helper coverage easier to invoke alongside existing guardrails.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py` (pass).
- Removal test: reverting would drop the dedicated guardrail target, reducing visibility/usage of overlay helper tests within the guardrails workflow for ADR-0054.

## 2025-12-15 – Loop 15 (kind: guardrail/tests)
- Focus: Surface overlay guardrail target in help output.
- Change: Documented `overlay-guardrails` in `make help` output so the helper suite is visible with other guardrail entrypoints.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py` (pass; sanity after change).
- Removal test: reverting would hide the overlay guardrail entrypoint from `make help`, reducing discoverability/usage tied to ADR-0054 overlay alignment.

## 2025-12-15 – Loop 16 (kind: guardrail/tests)
- Focus: Fold overlay guardrails into the main guardrails target.
- Change: Updated `guardrails` Make target to depend on `overlay-guardrails`, ensuring overlay helper tests run with the broader guardrail suite.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py` (pass).
- Removal test: reverting would exclude overlay helper checks from the default guardrails run, reducing enforcement of ADR-0054 overlay consistency.

## 2025-12-15 – Loop 17 (kind: guardrail/tests)
- Focus: Guardrail that overlay-guardrails target stays healthy.
- Change: Added `_tests/test_make_overlay_guardrails.py` to exercise `make overlay-guardrails` and fail fast if the target regresses.
- Artefact delta: `_tests/test_make_overlay_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop coverage that the overlay guardrail target runs clean, reducing detection of regressions in ADR-0054 overlay helper checks.

## 2025-12-15 – Loop 18 (kind: guardrail/tests)
- Focus: Overlay helper robustness on canvases missing capture attributes.
- Change: Added test ensuring `apply_canvas_blocking` is a no-op on canvases without mouse/keyboard attrs (no implicit attribute injection).
- Artefact delta: `_tests/test_overlay_helpers.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py` (pass).
- Removal test: reverting would lose coverage for missing-attr canvases, increasing risk of accidental attribute injection in ADR-0054 overlay helpers.

## 2025-12-15 – Loop 19 (kind: guardrail/tests)
- Focus: Integrate overlay guardrails into CI guardrail flow.
- Change: Added `overlay-guardrails` dependency to the `ci-guardrails` Make target so overlay helper tests run in the CI guardrail suite.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would omit overlay helper checks from `ci-guardrails`, weakening ADR-0054 guardrail enforcement in CI.

## 2025-12-15 – Loop 20 (kind: behaviour/guardrail)
- Focus: Shared overlay close orchestration helper.
- Change: Added `lib/overlayLifecycle.py` with `close_overlays` and wired `helpHub` to use it for closing overlapping canvases; added `_tests/test_overlay_lifecycle.py` guardrail.
- Artefact deltas: `lib/overlayLifecycle.py`, `lib/helpHub.py`, `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_make_overlay_guardrails.py _tests/test_overlay_lifecycle.py` (pass).
- Removal test: reverting would drop the shared close helper and its coverage, leaving bespoke close orchestration and weakening ADR-0054 overlay alignment goals.

## 2025-12-15 – Loop 21 (kind: guardrail/tests)
- Focus: Keep overlay lifecycle guardrail in the overlay guardrails target.
- Change: Updated `overlay-guardrails` Make target to run both overlay helper and overlay lifecycle tests.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py` (pass).
- Removal test: reverting would omit lifecycle checks from the overlay guardrail target, reducing enforcement of ADR-0054 overlay lifecycle alignment.

## 2025-12-15 – Loop 22 (kind: behaviour/guardrail)
- Focus: Use shared close orchestration in help canvas actions.
- Change: Imported `close_overlays` into `lib/modelHelpCanvas.py` and replaced bespoke close blocks when opening help canvas variants; keeps overlapping overlay shutdown consistent with new lifecycle helper.
- Artefact delta: `lib/modelHelpCanvas.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass; sanity run after change).
- Removal test: reverting would reintroduce bespoke close logic and bypass the shared lifecycle helper, increasing coordination drift against ADR-0054 overlay alignment.

## 2025-12-15 – Loop 23 (kind: behaviour/guardrail)
- Focus: Apply shared close orchestration to pattern GUIs.
- Change: Wired `lib/modelPatternGUI.py` and `lib/modelPromptPatternGUI.py` to use `close_overlays` when opening pattern/prompt pattern canvases, replacing bespoke close try/except blocks.
- Artefact deltas: `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would leave overlapping overlay shutdown bespoke for pattern UIs, undermining ADR-0054 alignment on shared lifecycle handling.

## 2025-12-15 – Loop 24 (kind: behaviour/guardrail)
- Focus: Apply shared close orchestration to suggestion GUI.
- Change: Updated `lib/modelSuggestionGUI.py` to use `close_overlays` when opening the prompt recipe suggestion canvas, replacing bespoke close blocks.
- Artefact delta: `lib/modelSuggestionGUI.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would leave suggestion GUI close orchestration bespoke, increasing coordination drift against ADR-0054 overlay lifecycle alignment.

## 2025-12-15 – Loop 25 (kind: behaviour/guardrail)
- Focus: Apply shared close orchestration to response canvas.
- Change: Imported `close_overlays` in `lib/modelResponseCanvas.py` and close overlapping pattern/prompt/suggestion/help canvases before opening the response canvas.
- Artefact delta: `lib/modelResponseCanvas.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would leave response canvas opening with bespoke/implicit close behavior, undermining ADR-0054 overlay lifecycle alignment.

## 2025-12-15 – Loop 26 (kind: behaviour/guardrail)
- Focus: Apply shared close orchestration to request history drawer.
- Change: Imported `close_overlays` in `lib/requestHistoryDrawer.py` and close overlapping overlays before opening the history drawer.
- Artefact delta: `lib/requestHistoryDrawer.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would leave the history drawer opening without coordinated overlay shutdown, increasing risk of overlapping canvases and weakening ADR-0054 alignment.

## 2025-12-15 – Loop 27 (kind: behaviour/guardrail)
- Focus: Align response canvas interactions with shared lifecycle helper.
- Change: Updated `lib/modelResponseCanvas.py` to close confirmation GUI via `close_overlays` when handling response button actions (paste path), aligning with shared lifecycle orchestration.
- Artefact delta: `lib/modelResponseCanvas.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would reintroduce bespoke confirmation close handling in response canvas interactions, weakening ADR-0054 overlay lifecycle consistency.

## 2025-12-15 – Loop 28 (kind: behaviour/guardrail)
- Focus: Align remaining response canvas actions with shared lifecycle helper.
- Change: Updated response canvas action handlers to close confirmation GUI via `close_overlays` for discard/context/query/thread/analyze/patterns to keep lifecycle handling consistent.
- Artefact delta: `lib/modelResponseCanvas.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would leave mixed bespoke vs shared close handling for confirmation actions, weakening ADR-0054 overlay lifecycle alignment.

## 2025-12-15 – Loop 29 (kind: behaviour/guardrail)
- Focus: Align response canvas toggle with shared lifecycle helper.
- Change: Applied `close_overlays` when opening the response canvas via toggle, matching the open path’s shared close orchestration.
- Artefact delta: `lib/modelResponseCanvas.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would leave the toggle path with bespoke close behaviour, reintroducing overlay overlap risk and weakening ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 30 (kind: behaviour/guardrail)
- Focus: DRY shared overlay close set and apply across response/history flows.
- Change: Added `close_common_overlays` helper; response canvas open/toggle and request history drawer now use it instead of inlined lists. Added guardrail in `_tests/test_overlay_lifecycle.py` to ensure common closers run.
- Artefact deltas: `lib/overlayLifecycle.py`, `lib/modelResponseCanvas.py`, `lib/requestHistoryDrawer.py`, `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would reintroduce duplicated close lists and drop coverage for the shared helper, weakening ADR-0054 overlay lifecycle alignment and maintainability.

## 2025-12-15 – Loop 31 (kind: guardrail/tests)
- Focus: Guardrail for common overlay closer tolerance.
- Change: Added test ensuring `close_common_overlays` no-ops when none of the expected closers exist on the actions object.
- Artefact delta: `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop coverage for missing-attribute tolerance in the shared lifecycle helper, increasing risk of regressions in ADR-0054 overlay alignment.

## 2025-12-15 – Loop 32 (kind: behaviour/guardrail)
- Focus: Use shared common-close set for suggestion GUI.
- Change: Updated `lib/modelSuggestionGUI.py` to call `close_common_overlays` when opening the prompt recipe suggestion canvas, expanding closure to response/help/pattern overlays via the shared set.
- Artefact delta: `lib/modelSuggestionGUI.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would leave suggestion GUI with a narrower bespoke close set, increasing overlay overlap risk and drifting from ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 33 (kind: behaviour/guardrail)
- Focus: Use shared common-close set for help canvas openings.
- Change: Updated help canvas open variants to use `close_common_overlays` instead of bespoke close lists, aligning with shared lifecycle helper coverage.
- Artefact delta: `lib/modelHelpCanvas.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would leave help canvas openings with a narrower bespoke close set, increasing overlay overlap risk and weakening ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 115 (kind: behaviour/guardrail)
- Focus: Last-save-path API clears stale paths and returns canonical existing file.
- Change: `gpt_request_history_last_save_path` now realpaths, verifies the file exists, clears stale state and notifies when missing; updated copy/open/show guards and tests to use canonical paths from real files.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_show_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would allow stale/missing last-save paths to propagate and drop coverage for canonical path handling, weakening ADR-0054 request pipeline observability/resilience.

## 2025-12-15 – Loop 116 (kind: behaviour/guardrail)
- Focus: Missing-history-path UX and canonical return from last-save API.
- Change: `gpt_request_history_last_save_path` now notifies with guidance to rerun `model history save source` when missing, clears stale state on missing files, and still returns canonical paths for existing files; updated copy/open/show guardrails to expect the guidance.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_show_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop the missing-path guidance/clearance and its coverage, weakening ADR-0054 request pipeline resilience and UX for history saves.

## 2025-12-15 – Loop 117 (kind: behaviour/guardrail)
- Focus: Ignore directory paths for last history save and clear stale state.
- Change: `gpt_request_history_last_save_path` now realpaths and returns only existing files, clearing stored state and notifying users to rerun `model history save source` when the path is a directory (or otherwise invalid); added guardrail for directory inputs and kept save helper paths canonical.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would allow directory last-save paths to persist/return and drop coverage for clearing/notification, weakening ADR-0054 request pipeline resilience and UX.

## 2025-12-15 – Loop 118 (kind: behaviour/guardrail)
- Focus: Clear stale provider ids when replaying history entries without a provider.
- Change: `_show_entry` now clears `GPTState.current_provider_id` when the history entry lacks a provider id, preventing stale provider state from leaking across history replays; added guardrail to verify provider state resets.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would allow stale provider ids to persist when replaying history entries without providers and drop coverage, weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 119 (kind: behaviour/guardrail)
- Focus: Hydrate history replay state once (axes/recipe) before directional guard.
- Change: `_show_entry` now normalizes axes or parses recipes once before replay, populates directional tokens on recipe-only entries, and still blocks canvas open when directional is missing while hydrating response/provider state; added guardrail to ensure missing-directional entries hydrate state but do not open the canvas.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would reintroduce double-parsing/partial state on history replay and drop coverage that missing-directional entries hydrate state but skip canvas open, weakening ADR-0054 request pipeline consistency.

## 2025-12-15 – Loop 120 (kind: behaviour/guardrail)
- Focus: Keep history navigation cursor progress when directional is missing, while still blocking canvas open.
- Change: `_show_entry` now reports success even when directional is missing (still not opening the canvas), and prev/next navigation only rewinds the cursor on missing entries. Added guardrail ensuring prev advances to missing-directional entries (with notify) without getting stuck, and next returns to the latest entry.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would reintroduce stuck navigation when an older entry lacks directional, and drop coverage that navigation continues while canvas stays closed, weakening ADR-0054 request replay UX/resilience.

## 2025-12-15 – Loop 121 (kind: behaviour/guardrail)
- Focus: Clarify history list behaviour when entries lack directional lenses.
- Change: `gpt_request_history_list` now notifies when no entries include a directional lens instead of emitting an empty list, guiding users toward fog/fig/dig/ong/rog/bog/jog requirements; added guardrail for the notification path.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop the user-facing guidance when history entries lack directional lenses and remove its coverage, weakening ADR-0054 request pipeline clarity.

## 2025-12-15 – Loop 122 (kind: behaviour/guardrail)
- Focus: Block insertion of directionless history entries by default.
- Change: `requestLog.append_entry/append_entry_from_request` now reject entries missing a directional lens unless explicitly overridden (tests wrap with `require_directional=False`); history summaries consistently skip entries with no directional or no axes; added guardrail ensuring lists notify when no directional entries exist.
- Artefact deltas: `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would allow directionless history entries to be stored, undermine directional guardrails in summaries/replay, and drop coverage of the insertion-time guard.

## 2025-12-15 – Loop 123 (kind: behaviour/guardrail)
- Focus: Notify when dropping directionless history entries at insertion time.
- Change: `requestLog.append_entry` now emits a user-facing notify when an entry is dropped for missing a directional lens, guiding users to rerun with fog/fig/dig/ong/rog/bog/jog; added guardrail to assert the drop-notify path.
- Artefact deltas: `lib/requestLog.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would hide insertion-time feedback for directionless history entries and drop its coverage, weakening ADR-0054 request pipeline guardrails.

## 2025-12-15 – Loop 124 (kind: behaviour/guardrail)
- Focus: Surface directional-drop reason when history is empty.
- Change: Request log now records the last drop reason and resets it on clear; history list uses the recorded drop reason to notify when no entries exist; added guardrail covering the drop notify and list path.
- Artefact deltas: `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop persistence of the drop reason and lose user-facing guidance when the history is empty due to directional drops, weakening ADR-0054 request pipeline clarity.

## 2025-12-15 – Loop 125 (kind: behaviour/guardrail)
- Focus: Make directional-drop guidance single-use to avoid stale repeats.
- Change: Added `consume_last_drop_reason` to request log and wired history list to consume/clear the drop message after notifying, preventing stale directional-drop notices from repeating once addressed; guardrail ensures the second list call falls back to the generic message.
- Artefact deltas: `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would let stale directional-drop messages repeat indefinitely and drop coverage for the single-use guidance, weakening ADR-0054 request pipeline UX clarity.

## 2025-12-15 – Loop 126 (kind: behaviour/guardrail)
- Focus: Surface directional drop reason in the history drawer when empty, consume once.
- Change: History drawer refresh now consumes the recorded drop reason and notifies when no entries are available; request log exposes a `consume_last_drop_reason` helper; guardrail added to ensure the drawer emits the directional guidance and consumes it on use.
- Artefact deltas: `lib/requestLog.py`, `lib/requestHistoryActions.py`, `lib/requestHistoryDrawer.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would hide directional-drop guidance when opening the history drawer after a dropped entry and drop the consumption guardrail, weakening ADR-0054 request pipeline clarity/UX.

## 2025-12-15 – Loop 127 (kind: behaviour/guardrail)
- Focus: Show directional drop guidance inside the history drawer canvas when empty.
- Change: Drawer refresh now captures the drop reason into `HistoryDrawerState.last_message`; the canvas renders that message (or a default) when no entries exist; guardrail covers drop reason consumption and drawer notify path.
- Artefact deltas: `lib/requestLog.py`, `lib/requestHistoryActions.py`, `lib/requestHistoryDrawer.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would remove in-drawer messaging for directional drops and drop its coverage, weakening ADR-0054 request pipeline UX clarity.

## 2025-12-15 – Loop 128 (kind: behaviour/guardrail)
- Focus: Clear stale drop reasons after successful appends and render guidance inline when empty.
- Change: `requestLog.append_entry` now clears `_last_drop_reason` on successful inserts; drawer state tracks last message and renders it when empty. Added guardrail to ensure drop reasons clear after a good append and consume once across list/drawer paths.
- Artefact deltas: `lib/requestLog.py`, `lib/requestHistoryActions.py`, `lib/requestHistoryDrawer.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would let stale directional-drop notices persist after successful writes and remove inline drawer messaging/coverage, weakening ADR-0054 request pipeline clarity/UX.

## 2025-12-15 – Loop 129 (kind: behaviour/guardrail)
- Focus: Add a save-latest CTA to the history drawer and keep it stateful.
- Change: Added `request_history_drawer_save_latest_source` action that saves the latest source, refreshes entries, and shows the drawer; drawer now renders drop guidance inline and clears stale drop reasons after successful appends. Guardrail added to ensure the CTA refreshes entries and displays the new item.
- Artefact deltas: `lib/requestHistoryDrawer.py`, `_tests/test_request_history_drawer.py`, `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would remove the drawer CTA to save latest history, keep stale drop reasons visible, and drop coverage, weakening ADR-0054 request history UX/guardrails.

## 2025-12-15 – Loop 130 (kind: behaviour/guardrail)
- Focus: Drawer UX: save-latest shortcut and inline guidance when empty.
- Change: Added keyboard shortcut `s` in the history drawer to trigger `request_history_drawer_save_latest_source`; drawer canvas now shows drop guidance plus a “Press s to save latest source” hint when empty. Guardrail ensures the CTA refreshes entries and invokes the save flow.
- Artefact deltas: `lib/requestHistoryDrawer.py`, `_tests/test_request_history_drawer.py`, `lib/requestLog.py`, `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would remove the drawer keyboard save shortcut and inline empty-state guidance, weakening ADR-0054 request history UX and its guardrails.

## 2025-12-15 – Loop 131 (kind: behaviour/guardrail)
- Focus: Avoid duplicative voice commands; keep drawer CTA internal.
- Change: Removed the separate Talon command `history drawer save latest`, keeping the existing `history save source` voice entry and wiring the drawer CTA/shortcut to use it internally. Updated Talon grammar guardrail accordingly.
- Artefact deltas: `GPT/request-history.talon`, `_tests/test_request_history_talon_commands.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would reintroduce a redundant voice command, drift from the single canonical save phrase, and drop coverage that the Talon grammar only lists the supported commands.

## 2025-12-15 – Loop 132 (kind: behaviour/docs)
- Focus: Document drawer guidance and shortcut for history saves.
- Change: Updated README history help to note the drawer’s inline guidance when empty and the `s` shortcut that saves the latest source and refreshes the list.
- Artefact delta: `readme.md`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would hide the drawer shortcut/guidance from user docs, reducing discoverability and weakening ADR-0054 UX clarity around history saves.

## 2025-12-15 – Loop 133 (kind: behaviour/guardrail)
- Focus: Respect in-flight guard in drawer save shortcut; avoid double voice commands.
- Change: Drawer save-shortcut guardrailed to ensure `_reject_if_request_in_flight` blocks the save CTA and keeps the drawer hidden when in-flight; removed redundant voice command earlier remains intact. Added guardrail test for the blocked path.
- Artefact deltas: `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop coverage that the drawer save shortcut respects in-flight guardrails, weakening ADR-0054 request pipeline UX safety.

## 2025-12-15 – Loop 134 (kind: behaviour/guardrail)
- Focus: Request lifecycle hooks for history saves via controller/bus.
- Change: Added `HISTORY_SAVED` request event with payload support; `RequestUIController` now accepts an `on_history_save` hook invoked via the request bus (`emit_history_saved`). Added bus/controller guardrails for the new hook and ensured Escape closes the history drawer statefully.
- Artefact deltas: `lib/requestState.py`, `lib/requestController.py`, `lib/requestBus.py`, `_tests/test_request_controller.py`, `_tests/test_request_bus.py`, `lib/requestHistoryDrawer.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py _tests/test_request_controller.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would drop the shared HISTORY_SAVED hook and coverage, limiting future lifecycle integration and removing escape-to-close coverage, weakening ADR-0054 request pipeline alignment and drawer UX safety.

## 2025-12-15 – Loop 135 (kind: behaviour/guardrail)
- Focus: Emit history save lifecycle events and guardrail them.
- Change: History save helper now emits `emit_history_saved(path, request_id)` on success; added guardrail to assert the lifecycle hook is called with the saved path/request id; kept controller/bus hook coverage.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `lib/requestState.py`, `lib/requestController.py`, `lib/requestBus.py`, `_tests/test_request_controller.py`, `_tests/test_request_bus.py`, `lib/requestHistoryDrawer.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_controller.py _tests/test_request_bus.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop the emitted HISTORY_SAVED lifecycle hook from save flow and its coverage, weakening ADR-0054 request lifecycle integration and observability.

## 2025-12-15 – Loop 136 (kind: behaviour/guardrail)
- Focus: Thread history saves through the request lifecycle and expose closing UX.
- Change: History saves now emit `emit_history_saved(path, request_id)` from the save helper, hitting the controller/bus hook; added guardrail asserting the hook receives the saved path/request id. Added escape key handling in the history drawer to close statefully.
- Artefact deltas: `lib/requestHistoryActions.py`, `lib/requestState.py`, `lib/requestController.py`, `lib/requestBus.py`, `lib/requestHistoryDrawer.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_controller.py`, `_tests/test_request_bus.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_controller.py _tests/test_request_bus.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would sever lifecycle events for history saves and drop escape-to-close coverage, weakening ADR-0054 request lifecycle integration and drawer UX safety.

## 2025-12-15 – Loop 137 (kind: behaviour/guardrail)
- Focus: Integrate request lifecycle bus with streaming/cancel flows.
- Change: Streaming path now emits `emit_complete` when streams finish, and cancel handling now emits `emit_cancel` instead of treating cancels as failures, aligning bus/controller lifecycle with request outcomes.
- Artefact deltas: `lib/modelHelpers.py`.
- Checks: `python3 -m pytest _tests/test_request_controller.py _tests/test_request_bus.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop lifecycle completeness for streaming success and misclassify cancels as failures on the bus, weakening ADR-0054 request pipeline alignment.

## 2025-12-15 – Loop 138 (kind: behaviour/guardrail)
- Focus: Axis catalog serializer for regen/SSOT and lifecycle hook emission in saves.
- Change: Added `serialize_axis_config` to produce a canonical axis payload (SSOT axes + optional Talon list tokens) for regen/export; history saves emit `emit_history_saved` with request id; lifecycle bus now emits cancel/complete in streaming paths. Added guardrails for serializer output, history save hook emission, and lifecycle hook plumbing.
- Artefact deltas: `lib/axisCatalog.py`, `_tests/test_axis_catalog_serializer.py`, `lib/requestHistoryActions.py`, `lib/requestState.py`, `lib/requestController.py`, `lib/requestBus.py`, `lib/requestHistoryDrawer.py`, `lib/modelHelpers.py`, `_tests/test_request_controller.py`, `_tests/test_request_bus.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_axis_catalog_serializer.py _tests/test_request_controller.py _tests/test_request_bus.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop the axis serializer needed for regen, sever history-saved lifecycle emission, and remove lifecycle hooks for streaming cancel/complete, weakening ADR-0054 alignment for axis SSOT and request pipeline.

## 2025-12-15 – Loop 139 (kind: behaviour/guardrail)
- Focus: Expose canonical axis catalog JSON for regen tooling.
- Change: Extended `generate_axis_config.py` with `--catalog-json` (axes + optional Talon list tokens via `serialize_axis_config`) and optional `--lists-dir`; added guardrail for the serializer output and catalog JSON renderer.
- Artefact deltas: `scripts/tools/generate_axis_config.py`, `lib/axisCatalog.py`, `_tests/test_axis_catalog_serializer.py`.
- Checks: `python3 -m pytest _tests/test_axis_catalog_serializer.py _tests/test_request_controller.py _tests/test_request_bus.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would remove the canonical catalog export path used for regen tooling and its coverage, weakening ADR-0054 axis SSOT progress.

## 2025-12-15 – Loop 140 (kind: behaviour/guardrail)
- Focus: Stabilize axis catalog for stub/bootstrap and regen consumers.
- Change: `axis_catalog` now always returns a catalog (even without lists_dir) instead of returning None when lists are absent, keeping Talon settings/bootstrap stable; `generate_axis_config.py` exposes a canonical catalog JSON renderer; added guardrail for serializer + renderer.
- Artefact deltas: `lib/axisCatalog.py`, `lib/talonSettings.py`, `scripts/tools/generate_axis_config.py`, `_tests/test_axis_catalog_serializer.py`.
- Checks: `python3 -m pytest _tests/test_axis_catalog_serializer.py _tests/test_request_controller.py _tests/test_request_bus.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would allow axis_catalog to return None in bootstrap paths and remove the catalog JSON renderer, breaking Talon settings population and regen/SSOT guardrails under ADR-0054.

## 2025-12-15 – Loop 141 (kind: behaviour/guardrail)
- Focus: Regeneration ergonomics for axis SSOT.
- Change: `make axis-regenerate` now also emits `tmp/axisCatalog.json` via the canonical catalog serializer; guardrail updated to expect the catalog JSON and validate its structure.
- Artefact deltas: `Makefile`, `_tests/test_make_axis_regenerate.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py _tests/test_axis_catalog_serializer.py _tests/test_request_controller.py _tests/test_request_bus.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop the catalog JSON artifact from the regen flow and its guardrail, weakening ADR-0054 axis SSOT regeneration/coverage.

## 2025-12-15 – Loop 142 (kind: behaviour/guardrail)
- Focus: Canonical axis catalog export and stability for regen/SSOT.
- Change: `axis_catalog` now always returns a catalog (no None fallthrough), Talon settings tolerate missing catalog gracefully, and `generate_axis_config.py` exposes `--catalog-json` using `serialize_axis_config`; guardrails added for serializer/renderer and regen target updated to emit `tmp/axisCatalog.json`.
- Artefact deltas: `lib/axisCatalog.py`, `lib/talonSettings.py`, `scripts/tools/generate_axis_config.py`, `Makefile`, `_tests/test_axis_catalog_serializer.py`, `_tests/test_make_axis_regenerate.py`.
- Checks: `python3 -m pytest _tests/test_axis_catalog_serializer.py _tests/test_make_axis_regenerate.py _tests/test_request_controller.py _tests/test_request_bus.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would reintroduce None returns from axis_catalog (breaking Talon settings/bootstrap) and remove the canonical catalog export/guardrail from the regen flow, weakening ADR-0054 axis SSOT alignment.

## 2025-12-15 – Loop 143 (kind: behaviour/guardrail)
- Focus: GPT axis catalog fallback covers SSOT axes for regen consumers.
- Change: GPT fallback `axis_catalog` now returns real axis tokens (AXIS_KEY_TO_VALUE) instead of empty axes when the full helper isn’t available, and added a guardrail to assert the fallback includes axes.
- Artefact deltas: `GPT/gpt.py`, `_tests/test_gpt_axis_catalog_fallback.py`.
- Checks: `python3 -m pytest _tests/test_gpt_axis_catalog_fallback.py _tests/test_axis_catalog_serializer.py _tests/test_make_axis_regenerate.py _tests/test_request_controller.py _tests/test_request_bus.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_drawer.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would make GPT’s fallback catalog return empty axes, breaking SSOT consumers when the helper isn’t importable and dropping coverage, weakening ADR-0054 axis registry consistency.

## 2025-12-15 – Loop 144 (kind: behaviour/guardrail)
- Focus: Axis regen produces the catalog-driven cheat sheet artifact.
- Change: `make axis-regenerate` now generates the catalog-based axis cheat sheet (`tmp/readme-axis-cheatsheet.md`) alongside the Python/JSON outputs, and the guardrail test asserts the artifact and its heading/axis section are present.
- Artefact deltas: `Makefile`, `_tests/test_make_axis_regenerate.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would drop the catalog cheat sheet from the regen flow and its guardrail, increasing doc drift risk for ADR-0054’s axis SSOT and reducing visibility into regenerated axis tokens.

## 2025-12-15 – Loop 145 (kind: behaviour/guardrail)
- Focus: Regenerate static prompt docs from the catalog in the axis regen flow.
- Change: Added `scripts/tools/generate_static_prompt_docs.py` and wired `make axis-regenerate` to emit `tmp/static-prompt-docs.md`; guardrail updated to assert the new artifact exists and includes the catalog-fed static prompt defaults/unprofiled prompts note.
- Artefact deltas: `scripts/tools/generate_static_prompt_docs.py`, `Makefile`, `_tests/test_make_axis_regenerate.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would drop catalog-driven static prompt docs from the regen flow and its guardrail, increasing drift risk between SSOT config, static prompt docs, and axis regeneration under ADR-0054.

## 2025-12-15 – Loop 146 (kind: behaviour/guardrail)
- Focus: Catalog-driven README axis list regeneration in the axis regen flow.
- Change: Added `scripts/tools/generate_readme_axis_lists.py` to render README-style axis lines from the catalog and wired `make axis-regenerate` to emit `tmp/readme-axis-lists.md`; guardrail updated to assert the artifact and core axis headings exist.
- Artefact deltas: `scripts/tools/generate_readme_axis_lists.py`, `Makefile`, `_tests/test_make_axis_regenerate.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would drop the catalog-driven README axis list artifact and its guardrail, increasing drift risk between the SSOT and README axis listings under ADR-0054.

## 2025-12-15 – Loop 147 (kind: behaviour/guardrail)
- Focus: README axis lists stay in lockstep with the catalog generator.
- Change: Extended README axis guardrail to compare README axis lines against the catalog-driven generator output, ensuring token sets match per-axis labels.
- Artefact delta: `_tests/test_readme_axis_lists.py`.
- Checks: `python3 -m pytest _tests/test_readme_axis_lists.py` (pass).
- Removal test: reverting would drop the generator-vs-README comparison, increasing risk of README axis drift despite SSOT generation under ADR-0054.

## 2025-12-15 – Loop 148 (kind: behaviour/guardrail)
- Focus: Catalog-driven README axis list generator coverage and guardrail wiring.
- Change: `generate_readme_axis_lists.py` now accepts `--lists-dir` and drives axis lines directly from the catalog; added generator guardrail tests (including lists-dir merge) and wired them into `axis-guardrails-test`.
- Artefact deltas: `scripts/tools/generate_readme_axis_lists.py`, `_tests/test_generate_readme_axis_lists.py`, `_tests/test_readme_axis_lists.py`, `Makefile`.
- Checks: `python3 -m pytest _tests/test_generate_readme_axis_lists.py _tests/test_readme_axis_lists.py` (pass).
- Removal test: reverting would drop generator coverage and guardrail wiring, weakening detection of axis drift in README regeneration and lists-dir-aware SSOT exports under ADR-0054.

## 2025-12-15 – Loop 149 (kind: behaviour/guardrail)
- Focus: Lists-dir aware README axis generator and guardrails.
- Change: Extended README axis generator to accept `--lists-dir` and added guardrail tests for catalog token parity and lists-dir token merges; wired the new guardrail into axis guardrail suite.
- Artefact deltas: `scripts/tools/generate_readme_axis_lists.py`, `_tests/test_generate_readme_axis_lists.py`, `_tests/test_readme_axis_lists.py`, `Makefile`.
- Checks: `python3 -m pytest _tests/test_generate_readme_axis_lists.py _tests/test_readme_axis_lists.py` (pass).
- Removal test: reverting would drop lists-dir-aware README axis generation and guardrails, increasing drift risk between the SSOT and README axis listings under ADR-0054.

## 2025-12-15 – Loop 150 (kind: behaviour/guardrail)
- Focus: Directional axis tokens stay synced between catalog and README.
- Change: Added directional axis output to the README axis generator and updated README to list directional tokens from the catalog; guardrails cover generator output and README parity.
- Artefact deltas: `scripts/tools/generate_readme_axis_lists.py`, `_tests/test_generate_readme_axis_lists.py`, `_tests/test_readme_axis_lists.py`, `GPT/readme.md`.
- Checks: `python3 -m pytest _tests/test_generate_readme_axis_lists.py _tests/test_readme_axis_lists.py` (pass).
- Removal test: reverting would drop directional axis coverage in the generator/README and weaken detection of catalog/README drift for directional tokens under ADR-0054.

## 2025-12-15 – Loop 151 (kind: behaviour/guardrail)
- Focus: Keep README axis lines auto-refreshable from the catalog.
- Change: Added `refresh_readme_axis_section.py` to rewrite README axis lines from the catalog generator, refreshed the README axis block via the script, and tightened the README axis guardrail to require exact line parity with the generator output.
- Artefact deltas: `scripts/tools/refresh_readme_axis_section.py`, `GPT/readme.md`, `_tests/test_readme_axis_lists.py`.
- Checks: `python3 -m pytest _tests/test_generate_readme_axis_lists.py _tests/test_readme_axis_lists.py` (pass).
- Removal test: reverting would drop the refresh helper and strict README parity guardrail, increasing drift risk between the catalog SSOT and README axis listings under ADR-0054.

## 2025-12-15 – Loop 152 (kind: behaviour/guardrail)
- Focus: Provide a guarded regen entrypoint for README axis lines.
- Change: Added `make readme-axis-lines` to emit a catalog-driven README axis snapshot into `tmp/readme-axis-lists.md` and a guardrail test to ensure the target runs and includes directional tokens.
- Artefact deltas: `Makefile`, `_tests/test_make_readme_axis_lines.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_lines.py` (pass).
- Removal test: reverting would drop the regen entrypoint and its guardrail, reducing visibility of catalog-driven README axis snapshots and increasing drift risk under ADR-0054.

## 2025-12-15 – Loop 153 (kind: behaviour/guardrail)
- Focus: Refreshable README axis flow with guarded target.
- Change: Added `make readme-axis-refresh` to rewrite README axis lines from the catalog generator; guardrail ensures the target runs. Refresh helper now tolerates bullet/non-bullet markers for completeness lines.
- Artefact deltas: `Makefile`, `scripts/tools/refresh_readme_axis_section.py`, `_tests/test_make_readme_axis_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_refresh.py` (pass).
- Removal test: reverting would drop the README refresh entrypoint and marker-tolerant helper, reducing maintainers’ ability to keep README axis lines aligned with the catalog under ADR-0054.

## 2025-12-15 – Loop 154 (kind: behaviour/guardrail)
- Focus: Make help surfaces README axis regen entrypoints.
- Change: Added `readme-axis-lines` and `readme-axis-refresh` to `make help` output and extended the guardrail to assert both targets are advertised.
- Artefact deltas: `Makefile`, `_tests/test_make_help_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would hide the README axis regen targets from `make help` and drop coverage, reducing discoverability of the catalog-driven README sync under ADR-0054.

## 2025-12-15 – Loop 155 (kind: behaviour/guardrail)
- Focus: Guardrail for static prompt docs regen entrypoint.
- Change: Added `make static-prompt-docs` target to generate catalog-driven static prompt docs and a guardrail test to ensure the target runs and emits the snapshot; wired the guardrail into `axis-guardrails-test`.
- Artefact deltas: `Makefile`, `_tests/test_make_static_prompt_docs.py`.
- Checks: `python3 -m pytest _tests/test_make_static_prompt_docs.py` (pass).
- Removal test: reverting would drop the static prompt docs regen entrypoint and its guardrail, weakening ADR-0054 SSOT coverage for static prompt documentation regeneration.

## 2025-12-15 – Loop 156 (kind: behaviour/guardrail)
- Focus: Refresh static prompt docs in README and guard the target.
- Change: `static-prompt-docs` now also refreshes the README static prompt section via a new helper; added guardrail for the refresh target and adjusted the helper to use current README anchors.
- Artefact deltas: `Makefile`, `scripts/tools/refresh_static_prompt_readme_section.py`, `_tests/test_make_static_prompt_docs.py`.
- Checks: `python3 -m pytest _tests/test_make_static_prompt_docs.py` (pass).
- Removal test: reverting would drop README static prompt refresh and its guardrail, increasing drift risk between catalog/static prompt docs and README under ADR-0054.

## 2025-12-15 – Loop 157 (kind: behaviour/guardrail)
- Focus: Make help surfaces static prompt docs regen.
- Change: Added `static-prompt-docs` to `make help` and guardrailed its presence so contributors can discover the catalog-driven static prompt docs/README refresh entrypoint.
- Artefact deltas: `Makefile`, `_tests/test_make_help_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would hide the static prompt docs regen target from `make help` and drop coverage, reducing discoverability of the catalog-driven static prompt docs refresh under ADR-0054.

## 2025-12-15 – Loop 158 (kind: behaviour/guardrail)
- Focus: CI guardrails cover README/static prompt regen entrypoints.
- Change: Added README axis snapshot/refresh and static prompt docs regen guardrail tests to `ci-guardrails`, ensuring catalog-driven doc regen targets stay healthy in CI.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_lines.py _tests/test_make_readme_axis_refresh.py _tests/test_make_static_prompt_docs.py` (pass).
- Removal test: reverting would drop these guardrails from CI, reducing SSOT enforcement for README axis/static prompt regeneration under ADR-0054.

## 2025-12-15 – Loop 159 (kind: behaviour/guardrail)
- Focus: Keep static prompt docs regen non-destructive to README.
- Change: `static-prompt-docs` now only generates the catalog snapshot (no README rewrite), clarified help text, and tightened the target guardrail to assert snapshot content without touching README.
- Artefact deltas: `Makefile`, `_tests/test_make_static_prompt_docs.py`.
- Checks: `python3 -m pytest _tests/test_make_static_prompt_docs.py` (pass).
- Removal test: reverting would reintroduce README rewriting in the static-prompt-docs target and weaken the guardrail against snapshot-only regeneration, risking unintended README edits under ADR-0054.

## 2025-12-15 – Loop 160 (kind: behaviour/guardrail)
- Focus: Add an explicit static prompt README refresh target and guard it in CI.
- Change: Introduced `static-prompt-refresh` target to rewrite README static prompt section from the catalog helper; added guardrail test for the target and wired it into axis/CI guardrail suites.
- Artefact deltas: `Makefile`, `scripts/tools/refresh_static_prompt_readme_section.py`, `_tests/test_make_static_prompt_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_static_prompt_refresh.py` (pass).
- Removal test: reverting would drop the refresh target and its guardrails from CI, reducing coverage for keeping README static prompt content aligned with the catalog under ADR-0054.

## 2025-12-15 – Loop 161 (kind: behaviour/guardrail)
- Focus: Make help surfaces the static prompt refresh target.
- Change: Added `static-prompt-refresh` to `make help` output and extended the guardrail to assert it stays advertised so contributors can discover the README static prompt refresh path.
- Artefact deltas: `Makefile`, `_tests/test_make_help_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would hide the static prompt refresh target from `make help` and drop its coverage, reducing discoverability of the catalog-driven README static prompt refresh under ADR-0054.

## 2025-12-15 – Loop 162 (kind: behaviour/guardrail)
- Focus: Make static prompt README refresh safe and guardrailed.
- Change: `static-prompt-refresh` now writes a merged README snapshot to `tmp/static-prompt-readme.md` (non-destructive); the refresh helper supports `--out`, and the guardrail asserts the snapshot is produced with static prompt content. CI/axis guardrails pick up the new test.
- Artefact deltas: `Makefile`, `scripts/tools/refresh_static_prompt_readme_section.py`, `_tests/test_make_static_prompt_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_static_prompt_refresh.py` (pass).
- Removal test: reverting would make the refresh target mutate README directly and drop the snapshot guardrail, increasing risk of unintended README edits while weakening ADR-0054 SSOT enforcement for static prompt docs.

## 2025-12-15 – Loop 163 (kind: behaviour/guardrail)
- Focus: Guard static prompt README snapshot for core content.
- Change: Strengthened the static prompt refresh guardrail to assert the snapshot contains key catalog-driven entries (baseline prompt and defaults line), ensuring the refresh path preserves SSOT content.
- Artefact delta: `_tests/test_make_static_prompt_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_static_prompt_refresh.py` (pass).
- Removal test: reverting would loosen the snapshot guardrail, reducing assurance that the README refresh path carries core static prompt content under ADR-0054.

## 2025-12-15 – Loop 164 (kind: behaviour/guardrail)
- Focus: Embed generator output in static prompt README refresh guardrail.
- Change: Guardrail now asserts the static prompt README snapshot includes the full catalog-driven docs output (substring), keeping the refresh path anchored to the generator text.
- Artefact delta: `_tests/test_make_static_prompt_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_static_prompt_refresh.py` (pass).
- Removal test: reverting would weaken the snapshot guardrail against drift from the generator output, reducing SSOT assurance for static prompt README refresh under ADR-0054.

## 2025-12-15 – Loop 165 (kind: behaviour/guardrail)
- Focus: Protect README from accidental writes during static prompt refresh.
- Change: Strengthened the static-prompt-refresh guardrail to assert the README remains unchanged when the target runs (writes snapshot only), keeping the refresh path non-destructive while still emitting the catalog-derived snapshot content.
- Artefact delta: `_tests/test_make_static_prompt_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_static_prompt_refresh.py` (pass).
- Removal test: reverting would drop the safeguard that prevents the refresh target from mutating README in-place, increasing risk of unintended edits and weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 166 (kind: behaviour/guardrail)
- Focus: Make README axis refresh non-destructive and snapshot-driven.
- Change: `readme-axis-refresh` now writes a catalog-generated snapshot to `tmp/readme-axis-readme.md` via an `--out` flag; added guardrail asserting the snapshot contains generated axis lines and README remains unchanged.
- Artefact deltas: `scripts/tools/refresh_readme_axis_section.py`, `Makefile`, `_tests/test_make_readme_axis_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_refresh.py` (pass).
- Removal test: reverting would make README axis refresh mutate README directly and drop the snapshot guardrail, weakening ADR-0054 SSOT protection for README axis lines.

## 2025-12-15 – Loop 167 (kind: behaviour/guardrail)
- Focus: Exact parity between README axis snapshot and generator output.
- Change: Hardened the README axis refresh guardrail to assert the snapshot’s axis block exactly matches the generator output while keeping README untouched.
- Artefact delta: `_tests/test_make_readme_axis_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_refresh.py` (pass).
- Removal test: reverting would loosen the parity check between the axis snapshot and generator, increasing drift risk in the README refresh path under ADR-0054.

## 2025-12-15 – Loop 168 (kind: behaviour/guardrail)
- Focus: Exact parity for the README axis snapshot target and non-destructive behaviour.
- Change: Strengthened `test_make_readme_axis_lines` to require the generated snapshot matches the axis generator output exactly and leaves README untouched.
- Artefact delta: `_tests/test_make_readme_axis_lines.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_lines.py` (pass).
- Removal test: reverting would weaken the parity/non-destructive guardrail for the README axis snapshot, increasing drift risk against the catalog under ADR-0054.

## 2025-12-15 – Loop 169 (kind: behaviour/guardrail)
- Focus: Lists-dir support for README axis refresh helper.
- Change: README axis refresh helper now accepts `--lists-dir` and threads it to the generator so snapshots can reflect Talon list tokens when provided; guardrail ensures the snapshot parity check remains green.
- Artefact delta: `scripts/tools/refresh_readme_axis_section.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_refresh.py` (pass).
- Removal test: reverting would drop lists-dir support from the refresh helper, reducing SSOT fidelity for README axis snapshots when list tokens are needed under ADR-0054.

## 2025-12-15 – Loop 170 (kind: behaviour/guardrail)
- Focus: README axis generator respects lists-dir tokens.
- Change: README axis generator now prefers catalog `axis_list_tokens` so lists-dir merges appear in generated lines; guardrail added to assert lists-dir tokens (e.g., novel scope entries) surface in the README axis refresh snapshot while leaving README untouched.
- Artefact deltas: `scripts/tools/generate_readme_axis_lists.py`, `_tests/test_make_readme_axis_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_refresh.py` (pass).
- Removal test: reverting would drop lists-dir tokens from README axis snapshots and weaken SSOT alignment for README regeneration under ADR-0054.

## 2025-12-15 – Loop 171 (kind: behaviour/guardrail)
- Focus: lists-dir coverage for README axis snapshot target.
- Change: Added lists-dir guardrail for `readme-axis-lines` generator to ensure list tokens are included when provided and kept parity/non-destructive behaviour.
- Artefact delta: `_tests/test_make_readme_axis_lines.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_lines.py` (pass).
- Removal test: reverting would drop coverage that README axis snapshot generation respects lists-dir tokens, weakening SSOT enforcement for axis regen under ADR-0054.

## 2025-12-15 – Loop 172 (kind: behaviour/guardrail)
- Focus: Parity for README axis refresh snapshots when lists-dir is provided.
- Change: Strengthened the README axis refresh guardrail to compare the snapshot axis block against the lists-dir-aware generator output, ensuring merged list tokens (e.g., custom scope entries) are honored while keeping README untouched.
- Artefact delta: `_tests/test_make_readme_axis_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_refresh.py` (pass).
- Removal test: reverting would loosen coverage for lists-dir parity in the refresh path, increasing drift risk for README axis snapshots under ADR-0054.

## 2025-12-15 – Loop 173 (kind: behaviour/guardrail)
- Focus: Help text reflects snapshot-only README axis refresh.
- Change: Updated `make help` messaging to state `readme-axis-refresh` produces a snapshot (`tmp/readme-axis-readme.md`) without touching README; guardrail remains in place to ensure discoverability.
- Artefact deltas: `Makefile`, `_tests/test_make_help_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would mislead contributors about README axis refresh behaviour and drop the aligned help text, increasing risk of unintended in-place edits against ADR-0054’s SSOT tooling.

## 2025-12-15 – Loop 174 (kind: behaviour/guardrail)
- Focus: Help text reflects snapshot-only static prompt refresh.
- Change: Updated `make help` to clarify `static-prompt-refresh` writes a snapshot (`tmp/static-prompt-readme.md`) without touching README, and adjusted the help guardrail to assert the snapshot wording is present.
- Artefact deltas: `Makefile`, `_tests/test_make_help_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would make static prompt refresh appear in-place and drop the guardrail, increasing risk of inadvertent README edits under ADR-0054.

## 2025-12-15 – Loop 175 (kind: behaviour/docs)
- Focus: Document snapshot-only axis/static prompt regen entrypoints.
- Change: Added README note pointing contributors at `make readme-axis-refresh` and `make static-prompt-refresh` snapshots (written to `tmp/…` without touching README) so doc updates use the catalog-driven outputs.
- Artefact delta: `GPT/readme.md`.
- Checks: not run (doc-only change).
- Removal test: reverting would hide the snapshot workflow from README, reducing discoverability of the non-destructive catalog-driven refresh path under ADR-0054.

## 2025-12-15 – Loop 176 (kind: behaviour/guardrail)
- Focus: Guard static prompt refresh snapshot against drift.
- Change: Added guardrail ensuring `static-prompt-refresh` snapshot block matches the static prompt generator output exactly while keeping README untouched.
- Artefact delta: `_tests/test_make_static_prompt_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_static_prompt_refresh.py` (pass).
- Removal test: reverting would loosen coverage for static prompt snapshot parity, increasing drift risk between the generator and README refresh path under ADR-0054.

## 2025-12-15 – Loop 177 (kind: behaviour/guardrail)
- Focus: Lists-dir aware README axis refresh wiring and guardrail.
- Change: `readme-axis-refresh` now accepts a lists-dir via env (`README_AXIS_LISTS_DIR`) when snapshotting axis lines; guardrail updated to assert lists-dir tokens appear in the snapshot while README stays untouched.
- Artefact deltas: `Makefile`, `scripts/tools/refresh_readme_axis_section.py`, `_tests/test_make_readme_axis_refresh.py`.
- Checks: `python3 -m pytest _tests/test_make_readme_axis_refresh.py` (pass).
- Removal test: reverting would drop lists-dir support from the README axis refresh target and weaken coverage of catalog+list merges in snapshots under ADR-0054.

## 2025-12-15 – Loop 178 (kind: docs/decision)
- Focus: Pause new lists-dir README/static prompt guardrails.
- Change: Recorded decision to stop adding further lists-dir-driven README/static prompt guardrails; keep existing snapshot tooling but avoid expanding guardrail surface unless the ADR explicitly calls for it.
- Artefact delta: this work-log entry.
- Checks: not run (doc-only decision).
- Removal test: dropping this note would remove the explicit pause/decision, risking continued low-value guardrail additions against ADR-0054 intent.

## 2025-12-15 – Loop 179 (kind: docs)
- Focus: Clarify optional lists-dir snapshot usage.
- Change: README now notes that `make readme-axis-refresh` can include list-file tokens via `README_AXIS_LISTS_DIR` or run catalog-only when omitted.
- Artefact delta: `GPT/readme.md`.
- Checks: not run (doc-only update).
- Removal test: reverting would hide how to opt into lists-dir-aware snapshots, reducing clarity for catalog-driven README refresh under ADR-0054.

## 2025-12-15 – Loop 180 (kind: behaviour/guardrail)
- Focus: Expose lists-dir option in help text for axis snapshot refresh.
- Change: `make help` now mentions the optional `README_AXIS_LISTS_DIR` for `readme-axis-refresh` (snapshot-only), and the guardrail asserts this wording so contributors see the env flag.
- Artefact deltas: `Makefile`, `_tests/test_make_help_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would hide the lists-dir env hint from help and drop coverage, reducing discoverability for list-token snapshots under ADR-0054.

## 2025-12-15 – Loop 181 (kind: behaviour/guardrail)
- Focus: One-shot doc snapshot guardrail.
- Change: Added `doc-snapshots` target to emit all catalog-driven README axis/static prompt snapshots into `tmp/` (non-destructive) and a guardrail to ensure the target runs and produces all artifacts.
- Artefact deltas: `Makefile`, `_tests/test_make_doc_snapshots.py`.
- Checks: `python3 -m pytest _tests/test_make_doc_snapshots.py` (pass).
- Removal test: reverting would drop the consolidated snapshot entrypoint and its guardrail, making it easier to miss doc drift under ADR-0054.

## 2025-12-15 – Loop 182 (kind: behaviour/guardrail)
- Focus: Discoverability of doc snapshot entrypoint in help text.
- Change: Added `doc-snapshots` to `make help` and extended the help guardrail to assert its presence.
- Artefact deltas: `Makefile`, `_tests/test_make_help_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would hide the consolidated doc snapshot target from help and drop its coverage, reducing discoverability of the snapshot workflow under ADR-0054.

## 2025-12-15 – Loop 183 (kind: behaviour/guardrail)
- Focus: Parity guardrails for consolidated doc snapshots.
- Change: Strengthened `doc-snapshots` guardrail to assert axis/static prompt snapshots match generator output and leave README untouched.
- Artefact delta: `_tests/test_make_doc_snapshots.py`.
- Checks: `python3 -m pytest _tests/test_make_doc_snapshots.py` (pass).
- Removal test: reverting would weaken parity coverage for the consolidated snapshot target, increasing drift risk for README axis/static prompt snapshots under ADR-0054.

## 2025-12-15 – Loop 184 (kind: docs)
- Focus: Make snapshot entrypoints clearer in README.
- Change: README now notes `make doc-snapshots` as the one-shot way to generate axis/static prompt snapshots (with optional `README_AXIS_LISTS_DIR` for axis tokens) while keeping README untouched.
- Artefact delta: `GPT/readme.md`.
- Checks: not run (doc-only update).
- Removal test: reverting would hide the consolidated snapshot workflow from README, reducing discoverability for ADR-0054 doc regen.

## 2025-12-15 – Loop 185 (kind: behaviour/guardrail)
- Focus: CI guardrails include doc snapshot parity.
- Change: Added `test_make_doc_snapshots` to the `ci-guardrails` target so CI enforces the consolidated doc snapshot parity/non-destructive guardrail.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_make_doc_snapshots.py` (pass).
- Removal test: reverting would drop doc snapshot parity from CI, increasing drift risk for README axis/static prompt snapshots under ADR-0054.

## 2025-12-15 – Loop 134 (kind: behaviour/guardrail)
- Focus: Drawer UX improvements: escape-to-close and testable key handler.
- Change: Added Escape/Esc key handling to close the history drawer and ensured state flips even when stubs lack the action. Exposed last key handler for tests and added guardrail for the escape-to-close path.
- Artefact deltas: `lib/requestHistoryDrawer.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_request_history_talon_commands.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop escape-to-close support and its coverage, weakening ADR-0054 request history UX and keyboard ergonomics.

## 2025-12-15 – Loop 66 (kind: guardrail/tests)
- Focus: Ensure history source save respects configured directory.
- Change: Tightened `test_history_save_latest_source_writes_markdown_with_prompt` to assert saved files land under the configured `user.model_source_save_directory`, ensuring request history saves respect the setting.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_latest_source_writes_markdown_with_prompt` (pass); related history guardrails remain green.
- Removal test: reverting would drop coverage that history saves respect the configured base directory, weakening ADR-0054’s request pipeline resilience around history export paths.

## 2025-12-15 – Loop 67 (kind: guardrail/tests)
- Focus: Request pipeline resilience for history saves on directory failures.
- Change: Added guardrail ensuring `_save_history_prompt_to_file` notifies and aborts without writing when directory creation fails.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_handles_directory_creation_failure` (pass).
- Removal test: reverting would drop coverage for directory-creation failures, weakening ADR-0054’s request pipeline resilience guardrails for history saves.

## 2025-12-15 – Loop 68 (kind: guardrail/tests)
- Focus: Request pipeline resilience for empty history prompts.
- Change: Added guardrail ensuring `gpt_request_history_save_latest_source` notifies and writes nothing when the latest history entry lacks a prompt.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_latest_source_handles_empty_prompt` (pass).
- Removal test: reverting would drop coverage for empty-prompt saves, weakening ADR-0054’s request pipeline resilience for history export paths.

## 2025-12-15 – Loop 69 (kind: guardrail/tests)
- Focus: History save slug/contract guardrail.
- Change: Added test ensuring `gpt_request_history_save_latest_source` produces filenames that include request id and directional slug tokens.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_filename_includes_request_and_directional_slug` (pass).
- Removal test: reverting would drop coverage for filename slug contract (request id + directional token), weakening ADR-0054’s request pipeline resilience guardrails for history exports.

## 2025-12-15 – Loop 70 (kind: guardrail/tests)
- Focus: Notification contract for history saves.
- Change: Added guardrail ensuring `gpt_request_history_save_latest_source` notifies with a message containing the saved filename/path.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_notify_path_includes_filename` (pass).
- Removal test: reverting would drop coverage for the notification content on history saves, weakening ADR-0054’s request pipeline guardrails for user-visible confirmation of saves.

## 2025-12-15 – Loop 71 (kind: guardrail/tests)
- Focus: Request pipeline guardrail for saving during in-flight requests.
- Change: Added test ensuring `gpt_request_history_save_latest_source` short-circuits when `_reject_if_request_in_flight` is true, preventing save attempts mid-flight.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_blocks_when_request_in_flight` (pass).
- Removal test: reverting would drop coverage for in-flight save blocking, weakening ADR-0054’s request pipeline resilience guardrails.

## 2025-12-15 – Loop 72 (kind: behaviour/guardrail)
- Focus: History save metadata completeness (request pipeline resilience).
- Change: `gpt_request_history_save_latest_source` now writes `provider_id` into saved history headers for better traceability; added guardrail test covering provider header emission.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_includes_provider_id_in_header` (pass; related save guardrails remain green).
- Removal test: reverting would drop provider metadata from saved history files and remove its coverage, weakening ADR-0054’s request pipeline traceability/guardrails.

## 2025-12-15 – Loop 73 (kind: guardrail/tests)
- Focus: History save timestamp contract (UTC).
- Change: Added guardrail ensuring saved history files record `saved_at` in UTC (Z-suffixed) to keep request traceability consistent.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_uses_utc_timestamp` (pass).
- Removal test: reverting would drop coverage for UTC timestamps in history saves, weakening ADR-0054’s request pipeline traceability guardrails.

## 2025-12-15 – Loop 74 (kind: behaviour/guardrail)
- Focus: History save slug/metadata completeness with provider context.
- Change: History save filenames now include provider id in the slug, and saved headers already include provider_id for traceability; added guardrail to ensure provider slugs appear in filenames.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_filename_includes_provider_slug` (pass; related provider/header/slug guardrails remain green).
- Removal test: reverting would drop provider id from history save filenames and remove coverage, weakening ADR-0054’s request pipeline traceability/guardrails for exported history files.

## 2025-12-15 – Loop 75 (kind: guardrail/tests)
- Focus: Request pipeline guardrails across in-flight vs terminal saves.
- Change: Added tests ensuring history saves are blocked when `current_state` reports an in-flight phase and allowed after terminal phases, while preserving existing provider slug/header behaviour.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_blocks_when_current_state_in_flight _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_succeeds_after_terminal_phase` (pass; related provider/header/slug guardrails remain green).
- Removal test: reverting would drop guardrails for in-flight save blocking and terminal-phase allow paths, weakening ADR-0054’s request pipeline resilience around history exports.

## 2025-12-15 – Loop 76 (kind: guardrail/tests)
- Focus: End-to-end notification after terminal-phase history save.
- Change: Added guardrail ensuring `gpt_request_history_save_latest_source` emits a “Saved history source” notification when saves occur after a terminal request phase.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_notifies_after_terminal_phase` (pass).
- Removal test: reverting would drop coverage for post-terminal save notifications, weakening ADR-0054’s request pipeline guardrails for user-visible history export confirmations.

## 2025-12-15 – Loop 77 (kind: behaviour/guardrail)
- Focus: Prevent history save filename collisions on repeat saves.
- Change: History saves now de-duplicate filenames by appending numeric suffixes when a filename already exists; added guardrail ensuring repeated saves produce unique files (even when saving the latest entry twice).
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_creates_unique_files_for_multiple_entries` (pass; related save guardrails remain green).
- Removal test: reverting would reintroduce filename collisions on repeated saves and drop coverage, risking overwritten history exports and weakening ADR-0054’s request pipeline resilience.

## 2025-12-15 – Loop 78 (kind: guardrail/tests)
- Focus: End-to-end save flow across in-flight → terminal phases.
- Change: Added guardrail ensuring history saves are blocked during in-flight phases and succeed after a terminal phase within the same sequence.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_sequence_inflight_then_terminal` (pass; related save guardrails remain green).
- Removal test: reverting would drop coverage for the phase-transition save flow, weakening ADR-0054’s request pipeline guardrails around history export sequencing.

## 2025-12-15 – Loop 79 (kind: guardrail/tests)
- Focus: History save headers align with axes tokens.
- Change: Added guardrail asserting saved history files include axis token headers for completeness/scope/method/form/channel/directional.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_writes_axes_headers` (pass; related save guardrails remain green).
- Removal test: reverting would drop coverage that saved files carry axis headers, weakening ADR-0054’s request pipeline traceability for history exports.

## 2025-12-15 – Loop 80 (kind: guardrail/tests)
- Focus: Wire history save guardrails into guardrail targets.
- Change: Added `request-history-guardrails` Make target running `_tests/test_request_history_actions.py` and included it in `ci-guardrails`, `guardrails`, and `make help` for visibility.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would drop request history guardrails from guardrail targets, reducing enforcement of ADR-0054 request pipeline resilience checks.

## 2025-12-15 – Loop 81 (kind: guardrail/tests)
- Focus: Guardrail target health for request-history guardrails.
- Change: Added `_tests/test_make_request_history_guardrails.py` to assert `make request-history-guardrails` runs clean; included the test in `ci-guardrails` target.
- Artefact deltas: `_tests/test_make_request_history_guardrails.py`, `Makefile`.
- Checks: `python3 -m pytest _tests/test_make_request_history_guardrails.py` (pass).
- Removal test: reverting would drop coverage of the request-history guardrail target and remove it from CI guardrail runs, weakening ADR-0054 enforcement of history save/resilience checks.

## 2025-12-15 – Loop 82 (kind: guardrail/docs)
- Focus: CI helper usage reflects request-history guardrails.
- Change: Updated `scripts/tools/run_guardrails_ci.sh` usage to note the default guardrails target now runs overlay lifecycle/helper and request-history guardrails.
- Artefact delta: `scripts/tools/run_guardrails_ci.sh`.
- Checks: `python3 -m pytest _tests/test_make_request_history_guardrails.py` (pass; guardrail target sanity).
- Removal test: reverting would hide the expanded guardrail scope from CI helper usage, risking omission of request-history guardrails when invoking defaults under ADR-0054.

## 2025-12-15 – Loop 83 (kind: guardrail/tests)
- Focus: Discoverability guardrail for request-history guardrails.
- Change: Added `_tests/test_make_request_history_guardrails.py` to ensure the target stays runnable and extended `make help` guardrail to assert `request-history-guardrails` is documented.
- Artefact deltas: `_tests/test_make_request_history_guardrails.py`, `_tests/test_make_help_guardrails.py`, `Makefile`.
- Checks: `python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop coverage for the request-history guardrail target and its discoverability, weakening ADR-0054 enforcement of history save/resilience guardrails.

## 2025-12-15 – Loop 84 (kind: guardrail/tests)
- Focus: Fast request-history guardrail entrypoint.
- Change: Added `request-history-guardrails-fast` Make target (runs a slim subset of history save guardrails) and guardrail test `_tests/test_make_request_history_guardrails_fast.py`; surfaced the target in `make help`.
- Artefact deltas: `Makefile`, `_tests/test_make_request_history_guardrails_fast.py`.
- Checks: `python3 -m pytest _tests/test_make_request_history_guardrails_fast.py` (pass; target sanity).
- Removal test: reverting would drop the fast guardrail entrypoint and its coverage, reducing discoverability of a quick history guardrail run and weakening ADR-0054 guardrail ergonomics.

## 2025-12-15 – Loop 85 (kind: guardrail/tests)
- Focus: Keep fast request-history guardrail target discoverable.
- Change: Extended `make help` guardrail to assert the fast request-history guardrail target is listed.
- Artefact delta: `_tests/test_make_help_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop coverage for help text discoverability of the fast history guardrail, weakening ADR-0054 guardrail ergonomics.

## 2025-12-15 – Loop 86 (kind: behaviour/guardrail)
- Focus: History save API returns saved path and dedupe-safe saving.
- Change: `_save_history_prompt_to_file` and `gpt_request_history_save_latest_source` now return the saved path (or None on block/failure), and filenames are deduped when saving repeatedly; tests updated to assert return value and guard blocking returns None.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would drop the return-path contract and its guardrails, weakening ADR-0054’s request pipeline resilience and making save callers blind to dedupe outcomes.

## 2025-12-15 – Loop 87 (kind: guardrail/tests)
- Focus: History save no-history return contract.
- Change: Added guardrail ensuring `gpt_request_history_save_latest_source` returns None and notifies when no history entries exist.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_latest_source_returns_none_when_no_history` (pass).
- Removal test: reverting would drop coverage for the no-history return contract, weakening ADR-0054 request pipeline guardrails for history export caller behaviour.

## 2025-12-15 – Loop 88 (kind: guardrail/tests)
- Focus: History save return-path uniqueness with dedupe.
- Change: Added guardrail asserting repeated saves return unique paths (deduped filenames) and both files exist.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_returns_unique_paths_on_dedupe` (pass).
- Removal test: reverting would drop coverage for deduped return paths, weakening ADR-0054 request pipeline guardrails for history save collision handling.

## 2025-12-15 – Loop 89 (kind: status/blocker)
- Focus: Pause request-history guardrail churn and pivot to behavioural slice.
- Change: No code/tests this loop. Recorded blocker to stop adding guardrail plumbing for history saves and instead take a behavioural slice (e.g., surface returned save path to callers or adjust UI/telemetry) before any further guardrail additions.
- Artefact delta: this work-log entry.
- Checks: Not run (status-only); prior guardrail suite remained green in Loop 88.
- Removal test: dropping this entry would remove the explicit pause and next-slice intent, risking continued low-value guardrail churn contrary to ADR-0054 goals.

## 2025-12-15 – Loop 90 (kind: behaviour/guardrail)
- Focus: History save return contract surfaced to state.
- Change: `gpt_request_history_save_latest_source` now returns the saved path and records it on `GPTState.last_history_save_path`; returns None on block/failure. Added guardrails covering success, empty-prompt/empty-history, in-flight blocks, and deduped saves.
- Artefact deltas: `lib/requestHistoryActions.py`, `lib/modelState.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would drop the return-path contract and its guardrails, weakening ADR-0054 request pipeline resilience and observability for history saves.

## 2025-12-15 – Loop 91 (kind: behaviour/guardrail)
- Focus: Clear stale history save path on failure/block; expose path return contract in tests.
- Change: `_save_history_prompt_to_file` now clears `GPTState.last_history_save_path` on nil prompt/no history/dir or write failure, and `gpt_request_history_save_latest_source` clears on in-flight blocks. Guardrails updated to assert state resets and return values in these scenarios.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would reintroduce stale last-history save paths on failure and drop coverage for the return-path/state-reset contract, weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 92 (kind: behaviour/guardrail)
- Focus: Expose last history save path to callers.
- Change: Added `gpt_request_history_last_save_path` action that returns the last saved history path (or notifies/None when missing). Guardrails cover available/missing cases.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would drop the caller-visible save-path action and its coverage, weakening ADR-0054 request pipeline observability for history exports.

## 2025-12-15 – Loop 93 (kind: status/blocker)
- Focus: Pause further history guardrail churn; plan UI surfacing of save path.
- Change: No code/tests this loop. Recorded blocker to shift from helper/tests to a behavioural slice that surfaces `last_history_save_path` in UI/telemetry (e.g., copy/link command) before adding more guardrail plumbing.
- Artefact delta: this work-log entry.
- Checks: Not run (status-only; prior suite green in Loop 92).
- Removal test: dropping this entry would remove the explicit pause and next-slice intent, risking continued guardrail churn without UI integration of the save-path contract under ADR-0054.

## 2025-12-15 – Loop 94 (kind: behaviour/guardrail)
- Focus: Surface last history save path to users and expose API.
- Change: Added `gpt_request_history_copy_last_save_path` action, wired to `model history copy last save` command, and added guardrails for available/missing path copy flows. Also ensure save-path state clears on failure/block.
- Artefact deltas: `lib/requestHistoryActions.py`, `lib/modelState.py`, `GPT/request-history.talon`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py` (pass).
- Removal test: reverting would drop the user-facing copy action, path-state reset on failures, and coverage for copy/notify flows, weakening ADR-0054 request pipeline observability and ergonomics.

## 2025-12-15 – Loop 95 (kind: guardrail/tests)
- Focus: Copy action fallback path guardrail.
- Change: Added guardrail ensuring the copy-last-save-path action falls back to `actions.user.paste` when clipboard copy fails while still notifying and returning the path.
- Artefact delta: `_tests/test_request_history_copy_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_copy_last_save_path.py` (pass; full history guardrail suite also green).
- Removal test: reverting would drop coverage for the clipboard-fallback path, weakening ADR-0054 request pipeline ergonomics guardrails for history save visibility.

## 2025-12-15 – Loop 96 (kind: behaviour/guardrail)
- Focus: User-facing open/copy surfacing of last history save path.
- Change: Added `gpt_request_history_open_last_save_path` action and Talon command (`model history open last save`) to open the saved file; copy action retains clipboard fallback. Added guardrails for available/missing open flows.
- Artefact deltas: `lib/requestHistoryActions.py`, `GPT/request-history.talon`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py` (pass).
- Removal test: reverting would drop the user-facing open action and its coverage, weakening ADR-0054’s request pipeline ergonomics and visibility of saved history files.

## 2025-12-15 – Loop 97 (kind: guardrail/tests)
- Focus: Guardrail for open-last-save path notification flow.
- Change: Added tests ensuring open-last-save path notifies/returns None when missing and opens/notifies when available.
- Artefact delta: `_tests/test_request_history_open_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_open_last_save_path.py` (pass; full history guardrail suite also green).
- Removal test: reverting would drop coverage for open-path notify flow, weakening ADR-0054 request pipeline guardrails for user-visible save access.

## 2025-12-15 – Loop 98 (kind: status/blocker)
- Focus: Pause history guardrail churn; plan next behavioural integration.
- Change: No code/tests this loop. Recorded blocker to avoid further copy/open guardrail additions and instead integrate the saved-path actions into UI/telemetry in the next behavioural slice.
- Artefact delta: this work-log entry.
- Checks: Not run (status-only; prior history guardrail suite green in Loop 97).
- Removal test: dropping this entry would remove the explicit pause/next-step intent, risking continued guardrail churn without UI integration per ADR-0054.

## 2025-12-15 – Loop 99 (kind: behaviour/guardrail)
- Focus: User-visible last history save path (show/open/copy commands).
- Change: Added `gpt_request_history_show_last_save_path` action and Talon command (`model history show last save`) to notify/return the last saved path; kept copy/open actions and ensured missing-path notifications. Added guardrails for show/open flows.
- Artefact deltas: `lib/requestHistoryActions.py`, `GPT/request-history.talon`, `_tests/test_request_history_show_last_save_path.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py` (pass).
- Removal test: reverting would drop the user-facing show command and coverage for show/open flows, reducing ADR-0054 visibility/ergonomics around saved history files.

## 2025-12-15 – Loop 100 (kind: behaviour/docs)
- Focus: Document history save/show/copy/open commands in README.
- Change: Updated `readme.md` to describe `model history save source`, `model history copy last save` / `model history open last save` / `model history show last save`.
- Artefact delta: `readme.md`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass; ensures help text still includes guardrail targets).
- Removal test: reverting would hide the new history save/copy/open/show commands from README, reducing discoverability and weakening ADR-0054 UI integration.

## 2025-12-15 – Loop 101 (kind: behaviour/guardrail)
- Focus: Robust open-last-save UX with missing-file handling and show command.
- Change: `open` now checks file existence, clears stale path, and notifies when missing; added guardrails for open/show flows.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_show_last_save_path.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py` (pass).
- Removal test: reverting would drop missing-file handling and show/open coverage, weakening ADR-0054 ergonomics and guardrails for saved history visibility.

## 2025-12-15 – Loop 102 (kind: guardrail/tests)
- Focus: README discoverability for history save/copy/open/show commands.
- Change: Added `_tests/test_readme_history_commands.py` to guard that README mentions the history save/copy/open/show commands.
- Artefact delta: `_tests/test_readme_history_commands.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py` (pass).
- Removal test: reverting would drop coverage ensuring README documents the history save/copy/open/show commands, weakening ADR-0054 UI/doc alignment for history features.

## 2025-12-15 – Loop 103 (kind: guardrail/tests)
- Focus: CI helper usage mentions request-history guardrails.
- Change: Added `_tests/test_run_guardrails_ci_history_docs.py` to assert `scripts/tools/run_guardrails_ci.sh --help` documents request-history guardrails.
- Artefact delta: `_tests/test_run_guardrails_ci_history_docs.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py` (pass).
- Removal test: reverting would drop coverage that CI helper usage advertises request-history guardrails, reducing discoverability and weakening ADR-0054 guardrail ergonomics.

## 2025-12-15 – Loop 104 (kind: guardrail/docs)
- Focus: CI helper usage mentions fast history guardrail target.
- Change: Updated `scripts/tools/run_guardrails_ci.sh` usage text to note `request-history-guardrails[-fast]` and extended CI helper doc guardrail to assert mention of the fast target.
- Artefact deltas: `scripts/tools/run_guardrails_ci.sh`, `_tests/test_run_guardrails_ci_history_docs.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py` (pass).
- Removal test: reverting would hide the fast history guardrail mention and drop its coverage, reducing discoverability for ADR-0054 request-history guardrails in CI helper usage.

## 2025-12-15 – Loop 105 (kind: guardrail/tests)
- Focus: Talon grammar discoverability for history save/copy/open/show commands.
- Change: Added `_tests/test_request_history_talon_commands.py` to assert `GPT/request-history.talon` includes save/copy/open/show commands.
- Artefact delta: `_tests/test_request_history_talon_commands.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py` (pass).
- Removal test: reverting would drop coverage ensuring the Talon grammar exposes the history commands, weakening ADR-0054 discoverability guardrails.

## 2025-12-15 – Loop 106 (kind: guardrail/tests)
- Focus: Make help lists fast history guardrail target.
- Change: Extended `test_make_help_guardrails` to assert `request-history-guardrails-fast` appears in `make help`.
- Artefact delta: `_tests/test_make_help_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop coverage that `make help` advertises the fast history guardrail target, reducing discoverability and weakening ADR-0054 guardrail ergonomics.

## 2025-12-15 – Loop 107 (kind: behaviour/cleanup)
- Focus: Remove unscoped history “open save dir” command and docs.
- Change: Removed the `model history open save dir` command/action/tests/README mention added earlier outside ADR-0054 scope; kept existing save/copy/open/show path flows.
- Artefact deltas: `GPT/request-history.talon`, `lib/requestHistoryActions.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_readme_history_commands.py`, `readme.md`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would reintroduce an unplanned history command and doc entry outside ADR-0054 scope and drop the cleanup guardrails.

## 2025-12-15 – Loop 108 (kind: behaviour/guardrail)
- Focus: History save path should be absolute even with relative base dir.
- Change: History save paths are now stored/written as absolute paths (abspath of base + filename), and guardrail added to ensure saves from relative settings return absolute paths and track the saved file.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would allow relative history save paths when using relative base dirs and drop coverage for absolute path tracking, weakening ADR-0054 request pipeline resilience/observability.

## 2025-12-15 – Loop 109 (kind: behaviour/guardrail)
- Focus: Normalize history save base dir to absolute for consistency and reporting.
- Change: `_save_history_prompt_to_file` now normalizes the base dir to an absolute path before directory creation and path construction, keeping saved paths consistent when settings use relative values.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would reintroduce relative base dir handling for history saves, causing inconsistent saved paths and weakening ADR-0054 request pipeline guardrails/observability.

## 2025-12-15 – Loop 110 (kind: behaviour/guardrail)
- Focus: Absolute save paths end-to-end for relative base dirs.
- Change: Save helper now uses an absolute base dir before path construction, and added a guardrail asserting relative base settings still produce absolute saved paths.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would allow relative save paths when using relative base dirs and drop coverage for absolute path enforcement, weakening ADR-0054 request pipeline resilience/observability.

## 2025-12-15 – Loop 111 (kind: behaviour/guardrail)
- Focus: Canonicalize history save paths (realpath) for consistency.
- Change: History save base dir and final path now use `os.path.realpath` to avoid symlink/relative drift; guardrail updated to assert absolute, canonical paths are returned/tracked.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop path canonicalisation and its coverage, allowing symlink/relative drift and weakening ADR-0054 request pipeline observability.

## 2025-12-15 – Loop 112 (kind: behaviour/guardrail)
- Focus: Canonicalize and track history save paths via last_save_path API.
- Change: `gpt_request_history_last_save_path` now returns/records canonical `realpath`; added guardrail for canonical path when last path was relative, and ensured base dirs are canonicalized.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_show_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would reintroduce non-canonical/mixed save paths and drop coverage for the canonical return contract, weakening ADR-0054 request pipeline observability.

## 2025-12-15 – Loop 113 (kind: behaviour/guardrail)
- Focus: Canonicalize history save base/paths end-to-end.
- Change: History save helper now realpaths the base dir and final path; guardrail updated to expect canonical paths when base setting is relative.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_show_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop canonicalization of history save base/paths, allowing symlink/relative drift and weakening ADR-0054 request pipeline observability.

## 2025-12-15 – Loop 114 (kind: behaviour/guardrail)
- Focus: Clean last-save-path API to return existing canonical paths only.
- Change: `gpt_request_history_last_save_path` now realpaths and clears/notes missing files; added guardrail ensuring canonical returns and state reset when the path is gone.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_show_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would allow stale/missing last-save paths to be returned and drop coverage for canonical/missing-path handling, weakening ADR-0054 request pipeline observability.
## 2025-12-15 – Loop 97 (kind: guardrail/tests)
- Focus: Guardrail for open-last-save path notification flow.
- Change: Added tests ensuring open-last-save path notifies/returns None when missing and opens/notifies when available after refactoring open ordering.
- Artefact delta: `_tests/test_request_history_open_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_open_last_save_path.py` (pass; full history guardrail suite also green).
- Removal test: reverting would drop coverage for open-path notify flow, weakening ADR-0054 request pipeline guardrails for user-visible save access.

## 2025-12-15 – Loop 98 (kind: status/blocker)
- Focus: Pause history guardrail churn; plan next behavioural integration.
- Change: No code/tests this loop. Recorded blocker to avoid further copy/open guardrail additions and instead integrate the saved-path actions into UI/telemetry (e.g., help text or UI link) in the next behavioural slice.
- Artefact delta: this work-log entry.
- Checks: Not run (status-only; prior history guardrail suite green in Loop 97).
- Removal test: dropping this entry would remove the explicit pause/next-step intent, risking continued guardrail churn without UI integration per ADR-0054.

## 2025-12-15 – Loop 99 (kind: behaviour/guardrail)
- Focus: User-visible last history save path (show/open/copy commands).
- Change: Added `gpt_request_history_show_last_save_path` action and Talon command (`model history show last save`) to notify/return the last saved path; kept copy/open actions and ensured missing-path notifications. Added guardrails for show/open flows.
- Artefact deltas: `lib/requestHistoryActions.py`, `GPT/request-history.talon`, `_tests/test_request_history_show_last_save_path.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py` (pass).
- Removal test: reverting would drop the user-facing show command and coverage for show/open flows, reducing ADR-0054 visibility/ergonomics around saved history files.

## 2025-12-15 – Loop 100 (kind: behaviour/docs)
- Focus: Document history save/show/copy/open commands in README.
- Change: Updated `readme.md` to describe `model history save source`, `model history copy/open/show last save`.
- Artefact delta: `readme.md`.
- Checks: `python3 -m pytest _tests/test_make_help_guardrails.py` (pass; ensures help text still includes guardrail targets).
- Removal test: reverting would hide the new history save/copy/open/show commands from README, reducing discoverability and weakening ADR-0054 UI integration.

## 2025-12-15 – Loop 89 (kind: status/blocker)
- Focus: Pause request-history guardrail churn and pivot to behavioural slice.
- Change: No code/tests this loop. Recorded blocker to stop adding guardrail plumbing for history saves and instead take a behavioural slice (e.g., surface returned save path to callers or adjust UI/telemetry) before any further guardrail additions.
- Artefact delta: `docs/adr/0054-concordance-axis-canvas-request-code-quality.work-log.md` (this entry).
- Checks: Not run (status-only); prior guardrail suite remained green in Loop 88.
- Removal test: dropping this entry would remove the explicit pause and next-slice intent, risking continued low-value guardrail churn contrary to ADR-0054 goals.

## 2025-12-15 – Loop 90 (kind: behaviour/guardrail)
- Focus: History save return contract surfaced to state.
- Change: `gpt_request_history_save_latest_source` now returns the saved path and records it on `GPTState.last_history_save_path`; returns None on block/failure. Added guardrails covering success, empty-prompt/empty-history, in-flight blocks, and deduped saves.
- Artefact deltas: `lib/requestHistoryActions.py`, `lib/modelState.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would drop the return-path contract/state tracking and its coverage, weakening ADR-0054 request pipeline resilience and observability for history saves.

## 2025-12-15 – Loop 62 (kind: guardrail/tests)
- Focus: Axis SSOT regen guardrail and JSON artefact.
- Change: Extended `axis-regenerate` to emit a JSON map (`tmp/axisConfig.json`) alongside Python/Markdown outputs and added `_tests/test_make_axis_regenerate.py` to run the target and assert artefacts are produced.
- Artefact deltas: `Makefile`, `_tests/test_make_axis_regenerate.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would drop the JSON regen output and its guardrail, reducing visibility into SSOT exports and weakening ADR-0054’s axis regeneration contract.

## 2025-12-15 – Loop 63 (kind: guardrail/tests)
- Focus: Keep axis regen guardrail wired into guardrail suites.
- Change: Added `_tests/test_make_axis_regenerate.py` to `axis-guardrails-test` and `ci-guardrails` targets so SSOT regen stays exercised in guardrail runs.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would drop the regen guardrail from guardrail targets, reducing enforcement of ADR-0054’s axis SSOT regeneration contract.

## 2025-12-15 – Loop 64 (kind: guardrail/tests)
- Focus: Request pipeline in-flight guardrails for history actions.
- Change: Added tests to cover `_request_is_in_flight` phase handling and `_reject_if_request_in_flight` notification/short-circuiting in `_tests/test_request_history_actions.py`.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_request_is_in_flight_handles_request_phases _tests/test_request_history_actions.py::RequestHistoryActionTests::test_reject_if_request_in_flight_notifies_and_blocks` (pass).
- Removal test: reverting would drop coverage for request in-flight detection and guard behaviour, weakening ADR-0054’s request pipeline resilience guardrails around history actions.

## 2025-12-15 – Loop 65 (kind: guardrail/tests)
- Focus: Request pipeline save-dir guardrail for history actions.
- Change: Added tests ensuring `_model_source_save_dir` prefers the user setting (expanding `~`) and falls back to the repo Talon root when unset.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_model_source_save_dir_prefers_setting_and_expands_user _tests/test_request_history_actions.py::RequestHistoryActionTests::test_model_source_save_dir_falls_back_to_repo_talon_root` (pass).
- Removal test: reverting would drop coverage for history save-dir resolution, weakening ADR-0054’s request pipeline resilience guardrails around history save/export flows.

## 2025-12-15 – Loop 66 (kind: guardrail/tests)
- Focus: Ensure history source save respects configured directory.
- Change: Tightened `test_history_save_latest_source_writes_markdown_with_prompt` to assert saved files land under the configured `user.model_source_save_directory`.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_latest_source_writes_markdown_with_prompt` (pass); prior related guardrail tests remain green.
- Removal test: reverting would drop coverage that history saves respect the configured base directory, weakening ADR-0054’s request pipeline resilience around history export paths.

## 2025-12-15 – Loop 52 (kind: guardrail/tests)
- Focus: Guardrail that Makefile guardrails targets retain overlay lifecycle wiring.
- Change: Added `_tests/test_guardrails_overlay_targets.py` to assert `guardrails`/`ci-guardrails` include overlay lifecycle guardrails.
- Artefact delta: `_tests/test_guardrails_overlay_targets.py`.
- Checks: `python3 -m pytest _tests/test_guardrails_overlay_targets.py` (pass).
- Removal test: reverting would drop coverage ensuring guardrail targets keep overlay lifecycle/tests wired, weakening ADR-0054 enforcement.

## 2025-12-15 – Loop 53 (kind: guardrail/tests)
- Focus: Guardrail that `make overlay-lifecycle-guardrails` remains healthy.
- Change: Added `_tests/test_make_overlay_lifecycle_guardrails.py` to run the target and fail fast on regressions.
- Artefact delta: `_tests/test_make_overlay_lifecycle_guardrails.py`.
- Checks: `python3 -m pytest _tests/test_make_overlay_lifecycle_guardrails.py` (pass).
- Removal test: reverting would drop coverage of the lifecycle guardrail target itself, weakening ADR-0054 enforcement.

## 2025-12-15 – Loop 54 (kind: guardrail/tests)
- Focus: Guardrail that excludes apply to base closers.
- Change: Added test ensuring `close_common_overlays` respects `exclude` for default closers (e.g., skips response when excluded).
- Artefact delta: `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop coverage for exclude handling on base closers, weakening ADR-0054 lifecycle helper robustness.

## 2025-12-15 – Loop 55 (kind: guardrail/tests)
- Focus: Reconfirm lifecycle guardrail health after recent Makefile wiring.
- Change: No code changes; reran lifecycle guardrail suite to ensure green after target wiring.
- Artefact delta: this work-log entry.
- Checks: `python3 -m pytest _tests/test_overlay_lifecycle.py` (pass).
- Removal test: dropping this entry would remove the confirmation that lifecycle guardrails remained green after Makefile wiring.

## 2025-12-15 – Loop 56 (kind: behaviour/guardrail)
- Focus: Close overlapping overlays before showing confirmation/response surface.
- Change: `confirmation_gui_append` now calls `close_common_overlays` (excluding self-close) before opening the response canvas, reducing overlapping overlays when confirmation flows are triggered.
- Artefact delta: `lib/modelConfirmationGUI.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py _tests/test_guardrails_overlay_targets.py _tests/test_make_overlay_lifecycle_guardrails.py` (pass).
- Removal test: reverting would drop shared lifecycle close when opening confirmation/response surfaces, reintroducing overlay overlap risk and weakening ADR-0054 alignment.

## 2025-12-15 – Loop 57 (kind: behaviour/guardrail)
- Focus: Ensure confirmation close clears other overlays.
- Change: `confirmation_gui_close` now uses `close_common_overlays` (excluding self-close) instead of bespoke response-only close, so confirmation shutdown clears overlapping overlays consistently.
- Artefact delta: `lib/modelConfirmationGUI.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py _tests/test_guardrails_overlay_targets.py _tests/test_make_overlay_lifecycle_guardrails.py` (pass).
- Removal test: reverting would leave confirmation close bespoke and risk leaving other overlays open, weakening ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 58 (kind: guardrail/tests)
- Focus: Guardrail for confirmation close using shared lifecycle helper.
- Change: Added `_tests/test_model_confirmation_overlay_lifecycle.py` to assert `confirmation_gui_close` invokes `close_common_overlays` (with proper exclude) and clears confirmation state without invoking bespoke response close.
- Artefact delta: `_tests/test_model_confirmation_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_model_confirmation_overlay_lifecycle.py` (pass).
- Removal test: reverting would drop coverage for confirmation close lifecycle orchestration, increasing regression risk for ADR-0054 alignment.

## 2025-12-15 – Loop 59 (kind: behaviour/guardrail)
- Focus: Guardrail for response toggle lifecycle orchestration.
- Change: Added `_tests/test_model_response_overlay_lifecycle.py` to assert `model_response_canvas_toggle` invokes `close_common_overlays` with the right excludes and drives show/hide.
- Artefact delta: `_tests/test_model_response_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_model_response_overlay_lifecycle.py` (pass).
- Removal test: reverting would drop coverage for response toggle lifecycle orchestration, weakening ADR-0054 alignment.

## 2025-12-15 – Loop 60 (kind: behaviour/guardrail)
- Focus: Guardrail for request history overlay lifecycle orchestration.
- Change: Added `_tests/test_request_history_overlay_lifecycle.py` to assert `request_history_drawer_open` invokes `close_common_overlays` and sets up the canvas state (show flag).
- Artefact delta: `_tests/test_request_history_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_request_history_overlay_lifecycle.py` (pass).
- Removal test: reverting would drop coverage for request history overlay lifecycle orchestration, weakening ADR-0054 alignment.

## 2025-12-15 – Loop 61 (kind: behaviour/guardrail)
- Focus: Guardrail for suggestion overlay lifecycle orchestration.
- Change: Added `_tests/test_model_suggestion_overlay_lifecycle.py` to assert suggestion GUI open calls `close_common_overlays`, sets tags, and shows the canvas.
- Artefact delta: `_tests/test_model_suggestion_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_model_suggestion_overlay_lifecycle.py` (pass).
- Removal test: reverting would drop coverage for suggestion overlay lifecycle orchestration, weakening ADR-0054 alignment.

## 2025-12-15 – Loop 34 (kind: behaviour/guardrail)
- Focus: Extend common-close helper and add exclusion guardrail.
- Change: Added `exclude` support to `close_common_overlays`, applied it in response canvas open/toggle to avoid self-closing, and added a guardrail test for exclusion handling.
- Artefact deltas: `lib/overlayLifecycle.py`, `lib/modelResponseCanvas.py`, `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop exclusion handling and its coverage, reintroducing duplicated close lists and potential self-close side effects, weakening ADR-0054 overlay lifecycle alignment.

## 2025-12-15 – Loop 35 (kind: behaviour/guardrail)
- Focus: Include confirmation GUI in the shared common-close set.
- Change: Added `confirmation_gui_close` to `close_common_overlays` and updated guardrail expectations to ensure it is invoked when present.
- Artefact deltas: `lib/overlayLifecycle.py`, `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would omit confirmation GUI from the shared close set and drop coverage, increasing overlay overlap risk and weakening ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 36 (kind: behaviour/guardrail)
- Focus: Use shared common-close set in pattern/prompt pattern openings and keep guardrails green.
- Change: Swapped bespoke close blocks for `close_common_overlays` in `lib/modelPatternGUI.py` and `lib/modelPromptPatternGUI.py`; the common closer set now also covers confirmation GUI, with guardrail coverage.
- Artefact deltas: `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would reintroduce bespoke close lists for pattern UIs and drop shared coverage for confirmation closure, weakening ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 37 (kind: behaviour/guardrail)
- Focus: Use shared common-close set for help hub overlaps.
- Change: Updated `_close_overlapping_surfaces` in `lib/helpHub.py` to use `close_common_overlays` (excluding help hub/response self-close) instead of bespoke lists.
- Artefact delta: `lib/helpHub.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would bring back bespoke overlap handling for help hub and drop shared lifecycle coverage, increasing overlay overlap risk against ADR-0054 alignment.

## 2025-12-15 – Loop 38 (kind: behaviour/guardrail)
- Focus: Formalize common overlay closer set with coverage.
- Change: Added `COMMON_OVERLAY_CLOSERS` constant to `lib/overlayLifecycle.py`, wired `close_common_overlays` to use it, and extended guardrail tests to assert membership (including confirmation/response).
- Artefact deltas: `lib/overlayLifecycle.py`, `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would lose the canonical closer set and its coverage, reintroducing implicit lists and weakening ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 39 (kind: guardrail/tests)
- Focus: Robustness when actions object is missing for common close helper.
- Change: Made `close_common_overlays` no-op when actions_obj is None and added guardrail coverage.
- Artefact deltas: `lib/overlayLifecycle.py`, `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would reintroduce a potential None-handling failure path and drop coverage, weakening ADR-0054 lifecycle robustness.

## 2025-12-15 – Loop 40 (kind: guardrail/tests)
- Focus: Guardrail for common overlay closer set integrity.
- Change: Added test ensuring `COMMON_OVERLAY_CLOSERS` contains unique entries (no duplicates), keeping the shared lifecycle set stable.
- Artefact delta: `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop coverage for closer set integrity, increasing risk of accidental duplicates in the shared lifecycle list under ADR-0054.

## 2025-12-15 – Loop 41 (kind: guardrail/tests)
- Focus: Guardrail for non-callable attributes in common closers.
- Change: Added test to ensure `close_common_overlays` ignores non-callable attributes on the actions object (still executing callable closers).
- Artefact delta: `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop coverage for non-callable tolerance, increasing risk of regressions in ADR-0054 overlay lifecycle helper.

## 2025-12-15 – Loop 42 (kind: guardrail/tests)
- Focus: Guardrail to ensure unlisted callables are ignored by common closer helper.
- Change: Added test asserting `close_common_overlays` only calls the configured common closers and ignores other callables on the actions object.
- Artefact delta: `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop coverage for ignoring unlisted callables, increasing risk of regressions in ADR-0054 overlay lifecycle helper.

## 2025-12-15 – Loop 43 (kind: guardrail/tests)
- Focus: Allow optional extra closers in shared lifecycle helper.
- Change: Added `extra` support to `close_common_overlays` and guardrail coverage to ensure extras are invoked (while still tolerating non-callables/duplicates via existing tests).
- Artefact deltas: `lib/overlayLifecycle.py`, `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop the extensibility and its coverage, reducing flexibility for ADR-0054 overlay lifecycle alignment.

## 2025-12-15 – Loop 44 (kind: guardrail/tests)
- Focus: Ensure exclusion applies to extra closers.
- Change: Added guardrail test that `close_common_overlays` respects the exclude set even for extra closers.
- Artefact delta: `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop coverage for exclude handling with extras, increasing risk of regressions in ADR-0054 overlay lifecycle helper.

## 2025-12-15 – Loop 45 (kind: guardrail/tests)
- Focus: Deduplicate common/extra closers.
- Change: Updated `close_common_overlays` to dedupe by name (including extras) and added guardrail ensuring duplicates are not invoked twice.
- Artefact deltas: `lib/overlayLifecycle.py`, `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would reintroduce potential double-invocation of shared closers and drop coverage, weakening ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 46 (kind: guardrail/tests)
- Focus: Provide a dedicated overlay lifecycle guardrail target.
- Change: Added `overlay-lifecycle-guardrails` Make target (runs lifecycle guardrail tests) and documented it in `make help`.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_overlay_lifecycle.py` (pass).
- Removal test: reverting would remove the dedicated lifecycle guardrail entrypoint, reducing discoverability/enforcement of ADR-0054 lifecycle checks.

## 2025-12-15 – Loop 47 (kind: guardrail/tests)
- Focus: Run lifecycle guardrails in default guardrails/CI targets.
- Change: `guardrails` and `ci-guardrails` now depend on `overlay-lifecycle-guardrails` so lifecycle tests run in the standard guardrail flow.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop lifecycle guardrails from default guardrails/CI targets, weakening ADR-0054 enforcement.

## 2025-12-15 – Loop 48 (kind: guardrail/docs)
- Focus: Reflect overlay guardrails in CI helper usage.
- Change: Updated `scripts/tools/run_guardrails_ci.sh` usage text to note the default guardrails target now runs overlay lifecycle/helper guardrails.
- Artefact delta: `scripts/tools/run_guardrails_ci.sh`.
- Checks: not run (doc-only change); prior guardrail suite remained green in Loop 47.
- Removal test: reverting would hide the expanded guardrail scope from the CI helper usage docs, risking missed overlay guardrails when invoking defaults.

## 2025-12-15 – Loop 49 (kind: guardrail/tests)
- Focus: Guardrail for non-callable extras in common overlay closers.
- Change: Added test ensuring `close_common_overlays` ignores non-callable extra entries while still invoking valid closers.
- Artefact delta: `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop coverage for non-callable extras, increasing risk of regressions in ADR-0054 overlay lifecycle helper.

## 2025-12-15 – Loop 50 (kind: guardrail/tests)
- Focus: Guardrail for close order and exclusion with extras.
- Change: Added guardrail ensuring `close_common_overlays` maintains declared order and ignores non-callable/extra-excluded entries.
- Artefact delta: `_tests/test_overlay_lifecycle.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would drop coverage for ordering and exclusion-with-extras, weakening ADR-0054 lifecycle helper robustness.

## 2025-12-15 – Loop 51 (kind: status/blocker)
- Focus: Pause guardrail churn; queue interaction-focused slices.
- Change: No code/tests this loop. Recorded blocker to pivot from lifecycle helper guardrails to behaviour checks (e.g., interaction tests for overlay toggle/close flows and confirmation GUI orchestration). Next loop should land an interaction slice or targeted behavioural test before adding more guardrail plumbing.
- Artefact delta: this work-log entry.
- Checks: Not run (status-only).
- Removal test: dropping this entry would remove the explicit pause/blocker and next-slice intent, risking continued low-value guardrail churn contrary to ADR-0054 goals.

## 2025-12-15 – Loop 50 (kind: status/blocker)
- Focus: Pause guardrail plumbing; plan interaction-focused slices.
- Change: No code changes this loop. Recorded blocker to shift away from helper guardrail churn and identify next behavioural slices (e.g., interaction checks for toggle/close flows, confirmation GUI integration).
- Artefact delta: `docs/adr/0054-concordance-axis-canvas-request-code-quality.work-log.md` (this entry).
- Checks: Not run (status-only loop); prior guardrail suite green in Loop 49.
- Removal test: dropping this entry would remove the explicit pause/blocker note, risking continued low-value guardrail churn without interaction-level progress.

## 2025-12-15 – Loop 33 (kind: behaviour/guardrail)
- Focus: Use shared common-close set for help canvas openings.
- Change: Updated help canvas open variants to use `close_common_overlays` instead of bespoke close lists, aligning with shared lifecycle helper coverage.
- Artefact delta: `lib/modelHelpCanvas.py`.
- Checks: `python3 -m pytest _tests/test_overlay_helpers.py _tests/test_overlay_lifecycle.py _tests/test_make_overlay_guardrails.py` (pass).
- Removal test: reverting would leave help canvas openings with a narrower bespoke close set, increasing overlay overlap risk and weakening ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 186 (kind: behaviour/guardrail)
- Focus: Keep the history drawer in sync with request lifecycle history saves.
- Change: Added a guarded drawer refresh action that rerenders entries only when showing and wired the default RequestUI on_history_save hook to invoke it so HISTORY_SAVED events refresh the drawer via the controller. Added guardrail tests for the refresh action and the UI hook.
- Artefact deltas: `lib/requestHistoryDrawer.py`, `lib/requestUI.py`, `_tests/test_request_history_drawer.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py _tests/test_request_ui.py` (pass).
- Removal test: reverting would drop lifecycle-driven drawer refresh and its coverage, leaving HISTORY_SAVED events unable to update an open drawer and reducing ADR-0054 request pipeline alignment/guardrails.

## 2025-12-15 – Loop 187 (kind: behaviour/guardrail)
- Focus: Default request id for history-saved lifecycle hook.
- Change: `emit_history_saved` now falls back to the current request id when callers omit it, so on_history_save consumers receive stable ids; added guardrails in the request bus and UI hook to assert the request id is populated.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_request_bus.py _tests/test_request_ui.py _tests/test_request_history_drawer.py` (pass).
- Removal test: reverting would drop the request-id defaulting and its coverage, leaving HISTORY_SAVED events without stable request ids for lifecycle hooks, weakening ADR-0054 request pipeline observability.

## 2025-12-15 – Loop 188 (kind: behaviour/guardrail)
- Focus: Expose request lifecycle append events to the controller.
- Change: Added `APPEND` request events and `emit_append` so streaming chunks carry request ids to controller hooks; RequestUIController now supports an `on_append` callback, and streaming appends emit the event. Guardrails cover controller/bus handling and ensure append hooks fire with defaulted request ids.
- Artefact deltas: `lib/requestState.py`, `lib/requestController.py`, `lib/requestBus.py`, `lib/modelHelpers.py`, `_tests/test_request_controller.py`, `_tests/test_request_bus.py`.
- Checks: `python3 -m pytest _tests/test_request_bus.py _tests/test_request_controller.py _tests/test_request_ui.py _tests/test_request_history_drawer.py` (pass).
- Removal test: reverting would drop append lifecycle events and their coverage, leaving streaming UI/hooks blind to per-chunk updates and weakening ADR-0054 request pipeline lifecycle alignment.

## 2025-12-15 – Loop 189 (kind: behaviour/guardrail)
- Focus: Wire append lifecycle events into the default UI for streaming refresh.
- Change: Default RequestUI now registers an `on_append` hook that refreshes the response canvas on streaming chunks; added guardrail to assert the append event triggers the refresh.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_request_ui.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would drop the UI hook for append events and its coverage, leaving streaming append lifecycle signals unused by the default UI and weakening ADR-0054 request pipeline alignment.

## 2025-12-15 – Loop 190 (kind: behaviour/guardrail)
- Focus: Throttle streaming-driven UI refresh to avoid canvas churn.
- Change: Added append refresh throttling and empty-chunk guard in default RequestUI so response canvas refreshes at most every 150ms during streaming; guardrail asserts throttling/ignore-empty behaviour.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_request_ui.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would remove throttling and its coverage, increasing canvas refresh churn on every chunk and weakening ADR-0054 request pipeline UX stability.

## 2025-12-15 – Loop 191 (kind: behaviour/guardrail)
- Focus: Avoid streaming refresh when the response canvas is suppressed or not the target.
- Change: Gated append-driven response canvas refresh on destination preference/suppression flags (mirrors modelHelpers’ gating) and removed a duplicate handler; added guardrail ensuring suppressed destinations skip refresh.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_request_ui.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would reintroduce response canvas refreshes for non-canvas destinations and a duplicate handler, increasing risk of unnecessary UI churn and divergence from ADR-0054 request pipeline intent.

## 2025-12-15 – Loop 192 (kind: behaviour/guardrail)
- Focus: Keep streaming chunks visible in the response canvas before snapshots exist.
- Change: Added a response canvas fallback buffer keyed by request id, populated via append lifecycle events; the canvas now renders cached chunks when snapshots are empty and clears the buffer on terminal states. Guardrails assert chunk caching, throttling, suppression gating, and terminal clearing.
- Artefact deltas: `lib/responseCanvasFallback.py`, `lib/requestUI.py`, `lib/modelHelpers.py`, `lib/modelResponseCanvas.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_request_ui.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would drop cached streaming text before snapshots exist and its coverage, making the response canvas show “awaiting chunk” despite in-flight chunks and weakening ADR-0054 request pipeline UX clarity.

## 2025-12-15 – Loop 193 (kind: guardrail/tests)
- Focus: Bound response canvas fallback buffer growth and clear helpers.
- Change: Capped cached streaming fallback text at 8000 chars per request (tail retained), added clear-all helper, and guardrails for append/clear/limit behaviour.
- Artefact deltas: `lib/responseCanvasFallback.py`, `_tests/test_response_canvas_fallback.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_response_canvas_fallback.py _tests/test_request_ui.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would allow unbounded fallback growth and drop coverage for append/clear limits, weakening ADR-0054 request pipeline resilience and UI stability for streaming previews.

## 2025-12-15 – Loop 194 (kind: guardrail/tests)
- Focus: Ensure suppressed destinations skip streaming fallback/cache.
- Change: Guardrail confirms append-driven refresh is skipped when response canvas is suppressed/non-target and that no fallback text is cached in that case.
- Artefact deltas: `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_response_canvas_fallback.py _tests/test_request_ui.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would drop coverage for suppressed destinations, risking unnecessary refresh/cache churn when the response canvas is not the target, weakening ADR-0054 request pipeline UX alignment.

## 2025-12-15 – Loop 195 (kind: guardrail/tests)
- Focus: Prevent streaming fallback cache from lingering when canvas suppressed.
- Change: Strengthened guardrail to assert that suppressed destinations skip both refresh and fallback caching during append events, so hidden canvases do not accumulate stale buffers.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_response_canvas_fallback.py _tests/test_request_ui.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would drop coverage that suppressed canvases avoid caching, increasing risk of stale fallback buffers and unintended UI churn against ADR-0054 request pipeline goals.

## 2025-12-15 – Loop 196 (kind: behaviour/guardrail)
- Focus: Clear streaming fallback buffers when closing the response canvas.
- Change: Response canvas close now clears cached fallback text for the last request; added guardrail to assert close hides the canvas and clears the fallback buffer.
- Artefact deltas: `lib/modelResponseCanvas.py`, `_tests/test_model_response_canvas_close.py`.
- Checks: `python3 -m pytest _tests/test_model_response_canvas_close.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would leave cached streaming text after closing the canvas and drop coverage, risking stale fallback text on reopen and weakening ADR-0054 request pipeline UX clarity.

## 2025-12-15 – Loop 197 (kind: behaviour/guardrail)
- Focus: Reset streaming fallbacks when a new send starts.
- Change: RequestUI now clears all fallback buffers on SENDING phase transitions so cached chunks from prior requests don’t leak into new sessions; guardrail asserts fallback caches clear on sending while append throttling remains intact.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_response_canvas_fallback.py _tests/test_request_ui.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would let streaming fallback text persist across new sends and drop coverage, risking stale chunk previews and weakening ADR-0054 request pipeline UX/guardrails.

## 2025-12-15 – Loop 198 (kind: behaviour/guardrail)
- Focus: Clear streaming fallback when the response canvas is closed or toggled shut.
- Change: Response canvas toggle/close now clears cached fallback text for the last request; added guardrail to assert fallback clearing when closing via the toggle path.
- Artefact deltas: `lib/modelResponseCanvas.py`, `_tests/test_model_response_canvas_close.py`.
- Checks: `python3 -m pytest _tests/test_model_response_canvas_close.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would leave cached streaming text after closing/toggling the response canvas and drop coverage, risking stale fallback text on reopen and weakening ADR-0054 request pipeline UX clarity.

## 2025-12-15 – Loop 199 (kind: behaviour/guardrail)
- Focus: Ensure reset events trigger cleanup hooks even from idle.
- Change: RequestUIController now reconciles/executes on_state_change for RESET even when the state is already idle, so cleanup hooks (including fallback clears) fire reliably; added guardrail for the RESET callback path.
- Artefact deltas: `lib/requestController.py`, `_tests/test_request_controller.py`.
- Checks: `python3 -m pytest _tests/test_request_controller.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py _tests/test_model_response_canvas_close.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would skip on_state_change on reset-from-idle, leaving cleanup hooks (like fallback clears) dormant and weakening ADR-0054 lifecycle/reset guardrails.

## 2025-12-15 – Loop 200 (kind: behaviour/guardrail)
- Focus: Keep last_request_id in sync for lifecycle consumers even outside send_request.
- Change: requestBus now records `GPTState.last_request_id` on begin_send/begin_stream, aligning fallback/preview consumers with lifecycle ids even when callers drive the bus directly; guardrails added for the bus id update.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks: `python3 -m pytest _tests/test_request_bus.py _tests/test_request_controller.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py _tests/test_model_response_canvas_close.py` (pass).
- Removal test: reverting would leave `last_request_id` unset for bus-driven sends/streams, risking stale or missing streaming previews and weakening ADR-0054 request pipeline alignment.

## 2025-12-15 – Loop 201 (kind: behaviour/guardrail)
- Focus: Clear last_request_id on reset to avoid stale streaming context.
- Change: requestBus now clears `GPTState.last_request_id` on reset and added guardrail to assert begin_send/stream set it and reset clears it; keeps downstream streaming/fallback consumers from reading stale ids after reset.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks: `python3 -m pytest _tests/test_request_bus.py _tests/test_request_controller.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py _tests/test_model_response_canvas_close.py` (pass).
- Removal test: reverting would leave stale `last_request_id` across resets and drop coverage, risking incorrect streaming previews and weakening ADR-0054 request pipeline lifecycle hygiene.

## 2025-12-15 – Loop 202 (kind: behaviour/guardrail)
- Focus: Keep lifecycle ids present for complete/fail/cancel when callers omit them.
- Change: requestBus now defaults COMPLETE/FAIL/CANCEL events to the current request id and updates `last_request_id`, ensuring downstream lifecycle consumers retain ids even when callers omit them; added guardrail for the default-id path.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks: `python3 -m pytest _tests/test_request_bus.py _tests/test_request_controller.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py _tests/test_model_response_canvas_close.py` (pass).
- Removal test: reverting would drop default id propagation on lifecycle events and its coverage, weakening ADR-0054 request pipeline observability for downstream hooks/streaming previews.

## 2025-12-15 – Loop 203 (kind: behaviour/guardrail)
- Focus: Keep streaming append events aligned with lifecycle ids.
- Change: `emit_append` now updates `last_request_id` even when callers omit the request id, so append-driven consumers (fallbacks, previews) stay aligned with the current request; guardrail added to assert append defaulting updates the tracked id.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks: `python3 -m pytest _tests/test_request_bus.py _tests/test_request_controller.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py _tests/test_model_response_canvas_close.py` (pass).
- Removal test: reverting would let append events leave `last_request_id` stale when request ids are omitted, weakening ADR-0054 streaming lifecycle alignment.

## 2025-12-15 – Loop 204 (kind: behaviour/guardrail)
- Focus: Clear streaming fallback buffers when the response canvas is hidden externally.
- Change: Response canvas now registers a hide handler even on pre-existing canvases and exposes it for testability; guardrail asserts hide events clear cached fallback text.
- Artefact deltas: `lib/modelResponseCanvas.py`, `_tests/test_model_response_canvas_close.py`.
- Checks: `python3 -m pytest _tests/test_model_response_canvas_close.py _tests/test_request_bus.py _tests/test_request_controller.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py` (pass).
- Removal test: reverting would leave cached fallback text when the canvas is hidden outside the toggle/close paths and drop coverage, risking stale streaming previews and weakening ADR-0054 request pipeline UX clarity.

## 2025-12-15 – Loop 205 (kind: behaviour/guardrail)
- Focus: Hide events also reset response canvas state flag.
- Change: Response canvas hide handler now marks `ResponseCanvasState.showing` false when the canvas hides (even externally) and the guardrail asserts this path, keeping state/fallbacks in sync when hidden outside toggle/close flows.
- Artefact deltas: `lib/modelResponseCanvas.py`, `_tests/test_model_response_canvas_close.py`.
- Checks: `python3 -m pytest _tests/test_model_response_canvas_close.py _tests/test_request_bus.py _tests/test_request_controller.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py` (pass).
- Removal test: reverting would leave `showing` true after external hides and drop coverage, risking stale state/fallback coupling and weakening ADR-0054 request pipeline UX alignment.
