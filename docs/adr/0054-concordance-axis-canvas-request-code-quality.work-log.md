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
- Change: `gpt_request_history_last_save_path` now notifies with guidance to rerun `model history save exchange` (renamed from `save source`) when missing, clears stale state on missing files, and still returns canonical paths for existing files; updated copy/open/show guardrails to expect the guidance.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_copy_last_save_path.py`, `_tests/test_request_history_open_last_save_path.py`, `_tests/test_request_history_show_last_save_path.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_copy_last_save_path.py _tests/test_request_history_open_last_save_path.py _tests/test_request_history_show_last_save_path.py _tests/test_readme_history_commands.py _tests/test_run_guardrails_ci_history_docs.py _tests/test_request_history_talon_commands.py _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would drop the missing-path guidance/clearance and its coverage, weakening ADR-0054 request pipeline resilience and UX for history saves.

## 2025-12-15 – Loop 117 (kind: behaviour/guardrail)
- Focus: Ignore directory paths for last history save and clear stale state.
- Change: `gpt_request_history_last_save_path` now realpaths and returns only existing files, clearing stored state and notifying users to rerun `model history save exchange` when the path is a directory (or otherwise invalid); added guardrail for directory inputs and kept save helper paths canonical.
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
- Change: Removed the separate Talon command `history drawer save latest`, keeping the existing `history save exchange` voice entry (renamed from `history save source`) and wiring the drawer CTA/shortcut to use it internally. Updated Talon grammar guardrail accordingly.
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
- Change: Updated `readme.md` to describe `model history save exchange`, `model history copy last save` / `model history open last save` / `model history show last save`.
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
- Change: Updated `readme.md` to describe `model history save exchange`, `model history copy/open/show last save`.
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

## 2025-12-15 – Loop 206 (kind: behaviour/guardrail)
- Focus: Close response canvas on reset/idle to clear streaming UI state.
- Change: RequestUI now closes the response canvas on IDLE/reset via `on_state_change` so stale canvases don’t linger; added guardrail to assert the close is invoked on reset while keeping fallback clears.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_request_ui.py _tests/test_request_bus.py _tests/test_request_controller.py _tests/test_response_canvas_fallback.py _tests/test_model_response_canvas_close.py` (pass).
- Removal test: reverting would leave the response canvas open after resets and drop coverage, risking stale streaming UI and weakening ADR-0054 lifecycle alignment.

## 2025-12-15 – Loop 207 (kind: behaviour/guardrail)
- Focus: Reset response canvas state when hidden externally.
- Change: Response canvas hide handler now also resets `ResponseCanvasState.showing`, `scroll_y`, and `meta_expanded` alongside clearing fallbacks; guardrail updated to assert hide clears state.
- Artefact deltas: `lib/modelResponseCanvas.py`, `_tests/test_model_response_canvas_close.py`.
- Checks: `python3 -m pytest _tests/test_model_response_canvas_close.py _tests/test_request_bus.py _tests/test_request_controller.py _tests/test_request_ui.py _tests/test_response_canvas_fallback.py` (pass).
- Removal test: reverting would leave response canvas state dirty after external hides and drop coverage, risking stale scroll/meta state and weakening ADR-0054 request pipeline UX clarity.

## 2025-12-15 – Loop 208 (kind: guardrail/tests)
- Focus: Enforce directional-axis requirement for request history entries.
- Change: Added requestLog guardrails to assert history entries without a directional lens are dropped by default while preserving explicit opt-out behaviour for callers that need it.
- Artefact deltas: `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass).
- Removal test: reverting would drop the guardrail ensuring non-directional history entries are rejected by default, increasing risk of storing incomplete recipes and losing the coverage that documents the opt-out path.

## 2025-12-15 – Loop 209 (kind: guardrail/tests)
- Focus: Ensure append_entry_from_request enforces directional lenses by default.
- Change: Added tests covering append_entry_from_request to confirm entries without directional axes are dropped with a clear drop reason and that callers can explicitly opt out when needed.
- Artefact deltas: `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass).
- Removal test: reverting would drop coverage for history entries derived from request payloads, risking acceptance of non-directional logs and weakening ADR-0054 request pipeline guardrails.

## 2025-12-15 – Loop 210 (kind: guardrail/tests)
- Focus: Clear fallback caches and close the response canvas when a request is cancelled.
- Change: Request UI now clears all cached fallback text and closes the response canvas on CANCELLED transitions; added guardrail asserting cancel clears fallbacks and closes the canvas.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_request_ui.py` (pass).
- Removal test: reverting would leave cached streaming text and open canvases after cancellation and drop coverage, risking stale UI state and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 211 (kind: guardrail/tests)
- Focus: Ensure error transitions clear fallbacks and close the response canvas.
- Change: Request UI now clears all fallback caches and closes the response canvas on ERROR transitions, with a guardrail covering the error path.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks: `python3 -m pytest _tests/test_request_ui.py` (pass) and `python3 -m pytest` (pass).
- Removal test: reverting would keep fallback text and open canvases after errors and drop coverage, risking stale streaming UI and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 212 (kind: guardrail/tests)
- Focus: Drop request history entries missing request ids before they reach the log.
- Change: requestLog now rejects entries with missing/blank request ids and records a drop reason; added guardrails for both append_entry and append_entry_from_request to assert the drop behaviour.
- Artefact deltas: `lib/requestLog.py`, `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass) and `python3 -m pytest` (pass).
- Removal test: reverting would allow id-less history entries to be stored and drop coverage, risking unusable history entries and weakened ADR-0054 request pipeline hygiene.

## 2025-12-15 – Loop 213 (kind: guardrail/tests)
- Focus: Keep history summaries aligned with directional-lens requirement.
- Change: Added HistoryQuery guardrails to ensure history summaries drop entries missing directional axes and still surface directional/form/channel tokens when present.
- Artefact deltas: `_tests/test_history_query.py`.
- Checks: `python3 -m pytest _tests/test_history_query.py` (pass) and `python3 -m pytest` (pass).
- Removal test: reverting would drop coverage for directional enforcement in history summaries, risking reintroduction of non-directional entries into summary/replay surfaces.

## 2025-12-15 – Loop 214 (kind: guardrail/tests)
- Focus: Lock history summary ordering and required fields.
- Change: Added HistoryQuery guardrail to assert summaries render newest-first and include request ids, durations, directional tokens, and provider ids when present.
- Artefact deltas: `_tests/test_history_query.py`.
- Checks: `python3 -m pytest _tests/test_history_query.py` (pass) and `python3 -m pytest` (pass).
- Removal test: reverting would drop coverage for summary ordering and field completeness, risking regressions where history summaries omit ids/directions or invert order.

## 2025-12-15 – Loop 215 (kind: guardrail/tests)
- Focus: Prevent history replay from mutating GPTState when entries lack a directional lens.
- Change: History replay now bails before hydrating GPTState when an entry is missing directional axes, so navigation skips invalid entries; guardrails updated to assert cursor/navigation behavior and directional token requirements.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass) and `python3 -m pytest` (pass).
- Removal test: reverting would allow non-directional history entries to overwrite GPTState and navigation state, weakening ADR-0054 history guardrails.

## 2025-12-15 – Loop 216 (kind: guardrail/tests)
- Focus: Ensure history replay/state remains stable when skipping non-directional entries.
- Change: History replay now skips mutation when entries lack directional axes and navigation guardrails assert cursor/state stability; tests updated to require directional axes on history entries that hydrate state and to keep cursor state unchanged when skipping invalid entries.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass) and `python3 -m pytest` (pass).
- Removal test: reverting would allow non-directional history entries to mutate GPTState and navigation cursor, risking stale state and violating ADR-048 directional enforcement.

## 2025-12-15 – Loop 217 (kind: guardrail/tests)
- Focus: Allow history replay/navigation to include legacy entries whose recipes carry directional tokens even when axes are absent.
- Change: Directional filtering now recognises directional tokens from the stored recipe when axes are missing; history replay hydrates axes from the recipe where needed. Added guardrails for recipe-driven directional hydration.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass) and `python3 -m pytest` (pass).
- Removal test: reverting would exclude legacy recipe-only entries from history navigation and drop coverage for recipe-driven directional hydration, weakening ADR-048 compliance for older logs.

## 2025-12-15 – Loop 218 (kind: guardrail/tests)
- Focus: Keep history lists/drawer summaries aligned with directional filtering and ordering.
- Change: History list now pulls only directional entries (including recipe-only directionals) and tests assert it filters non-directional entries and orders newest first; drawer summaries updated to backfill directionals from recipes.
- Artefact deltas: `lib/requestHistoryActions.py`, `lib/historyQuery.py`, `_tests/test_request_history_actions.py`, `_tests/test_history_query.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_history_query.py _tests/test_request_history_drawer.py` (pass) and `python3 -m pytest _tests/test_request_history_actions.py` (pass) and `python3 -m pytest` (pass).
- Removal test: reverting would allow non-directional entries into history lists/drawer or mis-order newest-first summaries, weakening ADR-048 guardrails and coverage.

## 2025-12-15 – Loop 219 (kind: guardrail/tests)
- Focus: Surface directional drop reasons when latest history entries are non-directional.
- Change: History replay (`gpt_request_history_show_latest`) now consumes and notifies the last drop reason when no directional entries are present instead of a generic empty message; guardrail added.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass) and `python3 -m pytest _tests/test_history_query.py _tests/test_request_history_drawer.py` (pass) and `python3 -m pytest` (pass).
- Removal test: reverting would hide why replay is blocked when the latest entries lack directionals, weakening ADR-048 guardrails and coverage.

## 2025-12-15 – Loop 220 (kind: guardrail/tests)
- Focus: Request log directional guardrail is case-insensitive and filters drift.
- Change: Request log axis filtering now lowercases tokens before matching so directional axes are kept even when callers supply uppercase tokens; added guardrail covering case-insensitive directional tokens. Ensures hydrated/unknown tokens remain filtered and directional enforcement still applies.
- Artefact deltas: `lib/requestLog.py`, `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_history_query.py` (pass).
- Removal test: reverting would drop acceptance of uppercase directional tokens and remove the guardrail, causing valid requests with capitalised axis tokens to be rejected or stored inconsistently and weakening ADR-048 history guardrails.

## 2025-12-15 – Loop 221 (kind: guardrail/tests)
- Focus: Request log axis filtering is case-insensitive across all axes.
- Change: Request log now lowercases axis tokens before matching for all axes (scope/method/form/channel/directional) to avoid silently dropping uppercase values; added guardrail that mixed-case axis tokens are stored canonicalised. Maintains drift filtering for hydrated/unknown tokens.
- Artefact deltas: `lib/requestLog.py`, `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_history_query.py` (pass).
- Removal test: reverting would reject valid history entries when callers provide uppercase axis tokens and would drop the guardrail, weakening ADR-0054/ADR-048 history axis enforcement.

## 2025-12-15 – Loop 222 (kind: guardrail/tests)
- Focus: History drawer surfaces directional drop reasons when entries are filtered out.
- Change: Drawer refresh now consumes and displays the last drop reason (e.g., missing directional lens) when no entries survive directional filtering; added guardrail that refresh surfaces the drop message instead of silent empty history.
- Artefact deltas: `lib/requestHistoryDrawer.py`, `_tests/test_request_history_drawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_history_query.py` (pass).
- Removal test: reverting would make the history drawer silently empty when entries are dropped for missing directionals, hiding actionable drop reasons and weakening ADR-048 guardrails.

## 2025-12-15 – Loop 223 (kind: guardrail/tests)
- Focus: Preserve drop reason visibility across history surfaces.
- Change: Drawer now peeks at the last drop reason (non-consuming) when no directional entries remain, so other history surfaces can still report the reason; behaviour remains to show a clear directional-lens message if no drop reason exists.
- Artefact deltas: `lib/requestHistoryDrawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py` (pass).
- Removal test: reverting would consume drop reasons in the drawer and hide them from other history actions, reducing visibility into why entries were dropped and weakening ADR-048 guardrails.

## 2025-12-15 – Loop 224 (kind: guardrail/tests)
- Focus: Keep drop reasons visible across history list and drawer surfaces.
- Change: Added guardrail ensuring the history drawer’s peek at the drop reason doesn’t consume it, so `gpt_request_history_list` can still surface the same reason afterward.
- Artefact deltas: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would allow drawer refresh to hide drop reasons from the history list, reducing visibility into why entries were dropped and weakening ADR-048 guardrails.

## 2025-12-15 – Loop 225 (kind: guardrail/tests)
- Focus: History list now peeks (does not consume) drop reasons so other surfaces retain them.
- Change: `gpt_request_history_list` uses `last_drop_reason` instead of consuming; updated guardrails so both drawer and list can surface the same drop reason without clearing it prematurely.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would make history list consume drop reasons, hiding them from other history surfaces and weakening ADR-048 guardrails around directional filtering visibility.

## 2025-12-15 – Loop 226 (kind: guardrail/tests)
- Focus: Drop reasons stay visible across list → drawer flows.
- Change: Added guardrail ensuring a drop reason surfaced by `gpt_request_history_list` remains available for the history drawer refresh to display afterward.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would allow the list view to hide drop reasons from the drawer, reducing visibility into why history entries were filtered and weakening ADR-048 guardrails.

## 2025-12-15 – Loop 227 (kind: guardrail/tests)
- Focus: Keep drop reasons visible across show_latest and list surfaces.
- Change: History latest action now peeks at the last drop reason (non-consuming) and guardrails assert the drop reason remains available for the history list; keeps directional drop messaging consistent across surfaces.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would let show_latest consume drop reasons and hide them from history list, reducing visibility into why entries were filtered and weakening ADR-048 guardrails.

## 2025-12-15 – Loop 228 (kind: guardrail/tests)
- Focus: Ensure navigation surfaces reuse drop reasons when history is empty/filtered.
- Change: History navigation (show_previous/prev) now peeks at the last drop reason when no directional entries are available instead of a generic message; added guardrails confirming drop reasons persist across prev/show_previous and remain visible to other surfaces.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would make navigation hide directional drop reasons, reducing visibility into why history entries were filtered and weakening ADR-048 guardrails.

## 2025-12-15 – Loop 229 (kind: guardrail/tests)
- Focus: Navigation only surfaces drop reasons when history is empty; no stale bleed.
- Change: Navigation now uses a drop-reason-aware notifier only when no directional entries exist; added guardrails to ensure prev/older navigation reports directional drop reasons when history is empty and stays generic when directional history exists.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would let stale drop reasons leak into navigation even when directional history exists, reducing clarity and weakening ADR-048 guardrails.

## 2025-12-15 – Loop 230 (kind: guardrail/tests)
- Focus: History “next” navigation reuses drop reasons when no directional history exists.
- Change: `gpt_request_history_next` now peeks at the last drop reason when history is empty; added guardrail ensuring next surfaces directional drop reasons and remains generic when directional history exists.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would make next navigation hide directional drop reasons or leak stale reasons when directional history exists, weakening ADR-048 guardrails.

## 2025-12-15 – Loop 231 (kind: guardrail/tests)
- Focus: Navigation drop reasons stay scoped to empty history (no stale bleed).
- Change: Added guardrail for “next” ensuring drop reasons only surface when history is empty/filtered and remain generic when directional history exists; removed unused drop-reason consumption import.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would reintroduce stale drop reasons into navigation when directional history exists or hide directional drop messaging when history is empty, weakening ADR-048 guardrails.

## 2025-12-15 – Loop 232 (kind: guardrail/tests)
- Focus: Drop-reason imports trimmed to match non-consuming flows.
- Change: Removed unused `consume_last_drop_reason` import from the history drawer now that all surfaces peek at `last_drop_reason` without consuming it.
- Artefact delta: `lib/requestHistoryDrawer.py`.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py _tests/test_request_history_actions.py _tests/test_history_query.py` (pass).
- Removal test: reverting would reintroduce an unused consuming import, risking accidental consumption paths and increasing drift from the non-consuming drop-reason contract in ADR-048.

## 2025-12-15 – Loop 233 (kind: guardrail/tests)
- Focus: Navigation drop reasons stay scoped to empty history for show_previous.
- Change: Added guardrail ensuring `gpt_request_history_show_previous` reports directional drop reasons only when history is empty/filtered and stays generic when directional history exists.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would risk stale drop reasons bleeding into show_previous when directional history exists or hide directional drop messaging when history is empty, weakening ADR-048 guardrails.

## 2025-12-15 – Loop 234 (kind: guardrail/tests)
- Focus: Drop reasons clear and stay silent after a successful directional append.
- Change: Added guardrail ensuring that after a successful directional append clears the drop reason, `gpt_request_history_show_latest` does not notify using a stale drop reason.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would risk stale drop reasons resurfacing on history show_latest even after valid directional entries exist, weakening ADR-048 guardrails.

## 2025-12-15 – Loop 235 (kind: guardrail/tests)
- Focus: show_latest must not read drop reasons when directional history exists.
- Change: Added guardrail asserting `gpt_request_history_show_latest` does not consult drop reasons when a directional entry is present (drop reason mock unused, notify not called).
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would allow stale drop reasons to be consulted even when valid history exists, risking incorrect notifications and weakening ADR-048 guardrails.

## 2025-12-15 – Loop 236 (kind: guardrail/tests)
- Focus: Prev navigation stays generic when directional history exists.
- Change: Added guardrail ensuring `gpt_request_history_prev` (with directional history present) reports the generic “No older history entry” message and does not expose drop reasons.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would let stale drop reasons leak into prev navigation when directional history exists, weakening ADR-048 guardrails.

## 2025-12-15 – Loop 237 (kind: guardrail/tests)
- Focus: Clearing history resets drop reasons and prevents stale notifications.
- Change: Added guardrail ensuring `clear_history` resets drop reasons so `gpt_request_history_list` shows the generic “No request history available” after a drop, preventing stale directional messages post-clear.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would risk stale drop reasons surfacing after clearing history, weakening ADR-048 guardrails.

## 2025-12-15 – Loop 238 (kind: guardrail/tests)
- Focus: History list ignores drop reasons when directional entries exist.
- Change: Added guardrail asserting `gpt_request_history_list` does not consult drop reasons when directional entries are present, preventing stale drop messaging when history is available.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would allow stale drop reasons to surface even when valid directional history exists, weakening ADR-048 guardrails.

## 2025-12-15 – Loop 239 (kind: guardrail/tests)
- Focus: Drop reasons are non-consuming and request history list stays clean.
- Change: `consume_last_drop_reason` is now non-consuming (aligned to the new peek contract) and request log tests rely on `last_drop_reason`; added guardrail that drop reasons remain cleared after successful append/history clear while list doesn’t surface stale drops.
- Artefact deltas: `lib/requestLog.py`, `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would reintroduce a consuming drop-reason helper and weaken coverage that drop reasons stay cleared or non-stale, undermining ADR-048 guardrails.

## 2025-12-15 – Loop 240 (kind: guardrail/tests)
- Focus: Keep consume_last_drop_reason consuming while preserving peek contract elsewhere.
- Change: Restored `consume_last_drop_reason` to clear the stored reason while keeping `last_drop_reason` for peeking; request log guardrails updated to cover both paths.
- Artefact deltas: `lib/requestLog.py`, `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would make consume non-consuming again, risking stale drop reasons persisting for callers that expect consumption and weakening ADR-048 drop-reason hygiene.

## 2025-12-15 – Loop 241 (kind: guardrail/tests)
- Focus: Peek-vs-consume contract on drop reasons is explicitly guarded.
- Change: Added guardrail to assert `last_drop_reason` is peek-only while `consume_last_drop_reason` still clears the reason, keeping both behaviours covered.
- Artefact deltas: `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would drop coverage of the peek vs consume contract for drop reasons, increasing risk of stale or disappearing drop messages and weakening ADR-048 guardrails.

## 2025-12-15 – Loop 242 (kind: guardrail/tests)
- Focus: Directional append clears prior drop reasons in request log.
- Change: Added guardrail ensuring a subsequent directional append clears any prior drop reason so consumers don’t surface stale drop messages.
- Artefact delta: `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would allow stale drop reasons to persist after valid entries, weakening ADR-048 drop-reason hygiene.

## 2025-12-15 – Loop 243 (kind: guardrail/tests)
- Focus: Consume drop reasons remains idempotent alongside peek contract.
- Change: Added guardrail asserting `consume_last_drop_reason` clears once and subsequent consumes return empty while `last_drop_reason` stays empty.
- Artefact delta: `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would weaken coverage of the consume-vs-peek contract and could let stale drop reasons persist or reappear, weakening ADR-048 guardrails.

## 2025-12-15 – Loop 244 (kind: guardrail/tests)
- Focus: Directional append clears prior drop reasons and consume is idempotent.
- Change: Added guardrail that a directional append clears any earlier drop reason and that `consume_last_drop_reason` only clears once, leaving no stale drop reason for later consumes.
- Artefact delta: `_tests/test_request_log.py`.
- Checks: `python3 -m pytest _tests/test_request_log.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would risk stale drop reasons persisting across valid appends or being re-consumed multiple times, weakening ADR-048 drop-reason hygiene.

## 2025-12-15 – Loop 245 (kind: guardrail/tests)
- Focus: Axis SSOT regen entrypoint that exercises all generators together.
- Change: Added `scripts/tools/axis_regen_all.py` to regenerate axisConfig/catalog/README list/cheatsheet/static prompt docs into `tmp/` and guardrail tests to ensure outputs are produced and the Make target runs.
- Artefact deltas: `scripts/tools/axis_regen_all.py`, `_tests/test_axis_regen_all.py`, `_tests/test_make_axis_regen_all.py`, `Makefile`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py` (pass); `python3 -m pytest _tests/test_request_log.py` (pass); `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would drop the all-in-one axis regen helper/guardrails and Make target, making it harder to exercise the axis SSOT generators together as called for by ADR-0054.

## 2025-12-15 – Loop 246 (kind: guardrail/tests)
- Focus: Axis guardrails run the all-in-one SSOT regen helper.
- Change: `axis-guardrails` now depends on `axis-regenerate-all`, and help text documents the target. Added guardrail for `axis-guardrails-ci` to ensure regen runs in the CI guardrail flow.
- Artefact deltas: `Makefile`, `_tests/test_make_axis_guardrails_ci.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_guardrails_ci.py` (pass); `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py` (pass); `python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would drop regen from the axis guardrail target/CI guardrail flow and lose coverage that the all-in-one SSOT regen still runs cleanly, weakening ADR-0054 axis SSOT enforcement.

## 2025-12-15 – Loop 247 (kind: guardrail/tests)
- Focus: Regen helper now snapshots README axis section alongside other SSOT outputs.
- Change: `axis_regen_all.py` now refreshes the README axis section snapshot into `tmp/readme-axis-readme.md`; guardrails updated to assert the snapshot is generated and the Make target covers it.
- Artefact deltas: `scripts/tools/axis_regen_all.py`, `_tests/test_axis_regen_all.py`, `_tests/test_make_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py` (pass); `python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would drop the README axis snapshot from the regen helper/guardrails, reducing coverage of SSOT outputs the ADR calls for.

## 2025-12-15 – Loop 248 (kind: guardrail/tests)
- Focus: Regen helper includes static prompt README snapshot; guardrails cover it.
- Change: `axis_regen_all.py` now refreshes the static prompt README section into `tmp/static-prompt-readme.md`; guardrails updated and Make axis guardrails already run regen.
- Artefact deltas: `scripts/tools/axis_regen_all.py`, `_tests/test_axis_regen_all.py`, `_tests/test_make_axis_regen_all.py`, `Makefile`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py` (pass); `python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would drop the static prompt README snapshot from regen and its guardrails, reducing coverage of SSOT outputs needed for ADR-0054.

## 2025-12-15 – Loop 249 (kind: guardrail/tests)
- Focus: Regen helper stable after README restoration; add static prompt README snapshot guardrail.
- Change: Ensured `axis_regen_all.py` now refreshes the static prompt README section; guardrails updated to expect `tmp/static-prompt-readme.md`. Restored `GPT/readme.md` to keep markers intact after a failed refresh and reran regen/tests to green.
- Artefact deltas: `scripts/tools/axis_regen_all.py`, `_tests/test_axis_regen_all.py`, `_tests/test_make_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py` (pass); `python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would drop the static prompt README snapshot from regen and its guardrails and risk breakage when markers drift, weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 250 (kind: behaviour/guardrail)
- Focus: Keep README instructions aligned with the SSOT regen workflow.
- Change: Added README note describing `make axis-regenerate-all` as the all-in-one SSOT regen entrypoint (axis config/catalog, README axis/cheatsheet, static prompt docs/README snapshots).
- Artefact delta: `GPT/readme.md`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass); `python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would hide the consolidated regen entrypoint from the README, reducing discoverability of the SSOT workflow called for in ADR-0054.

## 2025-12-15 – Loop 251 (kind: behaviour/guardrail)
- Focus: Document how to apply SSOT README snapshots safely.
- Change: README now instructs using `make axis-regenerate-all` and comparing the generated README axis/static prompt snapshots in `tmp/` before updating tracked sections, clarifying the SSOT apply workflow.
- Artefact delta: `GPT/readme.md`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass); `python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would remove guidance on reviewing/applying SSOT-generated README snapshots, increasing risk of drift and weakening ADR-0054 SSOT alignment.

## 2025-12-15 – Loop 252 (kind: guardrail/tests)
- Focus: Guardrail README markers used by SSOT refresh scripts.
- Change: Added test to ensure README axis/static prompt section markers exist; README updated with static prompt section headings to satisfy the guardrail.
- Artefact deltas: `_tests/test_readme_markers.py`, `GPT/readme.md`.
- Checks: `python3 -m pytest _tests/test_readme_markers.py _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass); `python3 -m pytest _tests/test_request_log.py _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (pass).
- Removal test: reverting would drop coverage that README keeps the markers required by SSOT refresh scripts, risking future regen failures and weakening ADR-0054 alignment.

## 2025-12-15 – Loop 246 (kind: guardrail/tests)
- Focus: Axis guardrails run the all-in-one SSOT regen helper.
- Change: `axis-guardrails` now depends on `axis-regenerate-all`; help text documents the new target. This keeps regen in the standard guardrail flow.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py` (pass).
- Removal test: reverting would drop the all-in-one regen from the axis guardrail target, reducing coverage of the SSOT regeneration workflow called for by ADR-0054.

## 2025-12-15 – Loop 246 (kind: guardrail/tests)
- Focus: Axis guardrail target now exercises the all-in-one regen helper.
- Change: `axis-guardrails` target depends on `axis-regenerate-all` so the SSOT regeneration runs alongside catalog validation/cheatsheet; guardrail Make test still covers the target.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_make_axis_regen_all.py` (pass).
- Removal test: reverting would drop the regen helper from the guardrails target, reducing coverage of the axis SSOT regeneration workflow called out in ADR-0054.

## 2025-12-15 – Loop 250 (kind: behaviour/guardrail)
- Focus: Apply refreshed README axis/static prompt sections from SSOT helpers.
- Change: Regenerated and applied the README axis lines and static prompt sections in `GPT/readme.md` via the catalog-driven refresh scripts; regen helper extended earlier remains green.
- Artefact delta: `GPT/readme.md`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py` (pass).
- Removal test: reverting would desynchronise README sections from the catalog-driven SSOT outputs, weakening ADR-0054 alignment and dropping the refreshed doc content applied in this loop.

## 2025-12-15 – Loop 253 (kind: guardrail/tests)
- Focus: Keep axisConfig regeneration faithful to helper functions.
- Change: Extended `generate_axis_config.py` to emit the `axis_key_to_value_map`/`axis_docs_for`/`axis_docs_index` helpers so regenerated axisConfig files match the tracked module; added a guardrail to assert the generated axisConfig still contains these helpers.
- Artefact deltas: `scripts/tools/generate_axis_config.py`, `_tests/test_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass).
- Removal test: reverting would drop generator coverage of the axis helper functions and the guardrail ensuring they remain in regenerated outputs, reintroducing drift risk between axisConfig.py and the SSOT regen flow.

## 2025-12-15 – Loop 254 (kind: guardrail/tests)
- Focus: Detect drift between tracked axisConfig and SSOT regen output.
- Change: Added a guardrail that regenerates axisConfig and compares it byte-for-byte to the tracked `lib/axisConfig.py`, ensuring the SSOT generator stays aligned; re-ran regen to populate tmp outputs.
- Artefact delta: `_tests/test_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py` (pass).
- Removal test: reverting would remove the drift check, so generator or manual edits could diverge from the tracked axisConfig without detection, weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 255 (kind: guardrail/tests)
- Focus: Ensure axis guardrails run the SSOT regen tests.
- Change: `axis-guardrails-test` now runs the axis regen guardrail suite (`_tests/test_axis_regen_all.py`, `_tests/test_make_axis_regen_all.py`, `_tests/test_make_axis_guardrails_ci.py`) in addition to existing catalog/cheatsheet checks; help text updated to reflect the stricter coverage.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass).
- Removal test: reverting would drop the regen guardrail tests from the axis guardrails target, allowing SSOT regen drift to slip past the standard guardrail flow and weakening ADR-0054 enforcement.

## 2025-12-15 – Loop 256 (kind: guardrail/tests)
- Focus: Guardrail the generated axis catalog payload to include axis list tokens.
- Change: Added a test that regenerates the axis catalog JSON and asserts it contains both `axes` and `axis_list_tokens` entries for all core axes with non-empty tokens, strengthening SSOT drift detection.
- Artefact delta: `_tests/test_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py` (pass).
- Removal test: reverting would drop coverage that the SSOT catalog JSON retains axis list tokens, weakening the axis registry contract enforced by ADR-0054.

## 2025-12-15 – Loop 257 (kind: guardrail/tests)
- Focus: Ensure SSOT catalog JSON includes static prompt payloads.
- Change: Extended `serialize_axis_config` to emit static prompt catalog/descriptions/profiles alongside axes/list tokens, and added a guardrail asserting regenerated `axisCatalog.json` contains populated static prompt sections.
- Artefact deltas: `lib/axisCatalog.py`, `_tests/test_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass).
- Removal test: reverting would strip static prompt data from the catalog export and its guardrail, reducing SSOT coverage of static prompts and weakening ADR-0054 alignment.

## 2025-12-15 – Loop 258 (kind: guardrail/tests)
- Focus: Treat the axis catalog JSON as the single SSOT (axes + static prompts).
- Change: Regenerated SSOT export now includes static prompt data by default and is validated in the regen guardrail; reran regen/tests to ensure the catalog carries axes, list tokens, and static prompt sections together.
- Artefact deltas: `lib/axisCatalog.py`, `_tests/test_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass).
- Removal test: reverting would drop static prompt sections from the SSOT catalog JSON and its guardrail, weakening ADR-0054’s axis registry coverage across static prompts.

## 2025-12-15 – Loop 259 (kind: guardrail/tests)
- Focus: Keep README regeneration instructions outside the autogenerated static prompt section and restore required markers.
- Change: Added an `SSOT regeneration` section before the static prompt content, updated the static prompt docs generator to emit the required snapshot/detail headings, and refreshed the README static prompt section to align with the generator.
- Artefact deltas: `GPT/readme.md`, `scripts/tools/generate_static_prompt_docs.py`.
- Checks: `python3 -m pytest _tests/test_readme_markers.py` (pass); `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass); `python3 scripts/tools/refresh_static_prompt_readme_section.py`.
- Removal test: reverting would reintroduce drift between README and the generator (dropping required markers/headings or losing SSOT regen guidance), weakening SSOT/ADR-0054 guardrails.

## 2025-12-15 – Loop 260 (kind: guardrail/tests)
- Focus: Guardrail static prompt sections in the axis catalog validator.
- Change: Axis catalog validation now errors when static prompt sections (`static_prompts`, `static_prompt_descriptions`, `static_prompt_profiles`) are missing; added tests to cover both failure and pass cases via direct validator invocation.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would allow catalog exports to omit static prompt data without detection, weakening SSOT coverage for static prompts under ADR-0054.

## 2025-12-15 – Loop 261 (kind: guardrail/tests)
- Focus: Ensure axis guardrail target runs the new static prompt catalog validator test.
- Change: Added `_tests/test_axis_catalog_validate_static_prompts.py` to the `axis-guardrails-test` Make target so the static prompt catalog presence checks run with the rest of the axis guardrails.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would omit the static prompt catalog guardrail from the axis guardrails suite, weakening SSOT enforcement for static prompts under ADR-0054.

## 2025-12-15 – Loop 262 (kind: guardrail/tests)
- Focus: Run static prompt catalog guardrail in CI guardrails target.
- Change: Added `_tests/test_axis_catalog_validate_static_prompts.py` to the `ci-guardrails` test set so CI runs the static prompt catalog presence checks alongside other axis guardrails.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would skip the static prompt catalog guardrail in CI, allowing missing static prompt sections to slip past ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 263 (kind: guardrail/tests)
- Focus: Guard static prompt docs regen for required headings.
- Change: Added a guardrail that regenerates static prompt docs via `axis_regen_all` and asserts the output contains the expected snapshot/detail headings.
- Artefact delta: `_tests/test_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py` (pass).
- Removal test: reverting would allow regenerated static prompt docs to omit required headings, risking README refresh failures and weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 264 (kind: guardrail/tests)
- Focus: Make axis catalog validation resilient and failing when static prompt sections are missing, including via CLI.
- Change: Hardened axis catalog validation to tolerate missing static prompt keys gracefully and still report drift, and added a CLI-focused guardrail to ensure the validator exits non-zero when static prompt sections are absent.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would allow missing static prompt sections to raise key errors or pass silently instead of producing actionable failures, weakening ADR-0054 SSOT enforcement for static prompts.

## 2025-12-15 – Loop 265 (kind: guardrail/tests)
- Focus: Keep axis catalog JSON generation explicitly exporting static prompt data.
- Change: `generate_axis_config.py` now explicitly passes `include_static_prompts=True` when rendering the catalog JSON to avoid regressions if defaults change; regen guardrails rerun and remain green.
- Artefact delta: `scripts/tools/generate_axis_config.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would rely on implicit defaults for static prompt export, making it easier for future changes to drop static prompt data from `axisCatalog.json` unnoticed, weakening ADR-0054 SSOT coverage.

## 2025-12-15 – Loop 266 (kind: guardrail/tests)
- Focus: Guard static prompt catalog contents for expected profiles.
- Change: Added a guardrail that regenerates `axisCatalog.json` via `axis_regen_all` and asserts the `static_prompts` section includes known profiles (e.g., `describe`) in addition to the existing presence checks.
- Artefact delta: `_tests/test_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would allow the static prompt catalog to drop core profiles without detection, weakening SSOT enforcement under ADR-0054.

## 2025-12-15 – Loop 267 (kind: guardrail/tests)
- Focus: Guard `make axis-regenerate-all` output for static prompt catalog contents.
- Change: Extended the Make target guardrail to parse `axisCatalog.json` generated by `make axis-regenerate-all` and assert it includes static prompts (with `describe`) and axis list tokens.
- Artefact delta: `_tests/test_make_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would let the Make-based regen target drop static prompt/catalog content without detection, weakening the SSOT guardrails under ADR-0054.

## 2025-12-15 – Loop 268 (kind: guardrail/tests)
- Focus: Guard axis regen Make target for static prompt profile presence.
- Change: Added a guardrail to the Make-based regen test to assert the `static_prompts` section includes the `describe` profile and that axis list tokens are present after running `axis-regenerate-all`.
- Artefact delta: `_tests/test_make_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regen_all.py` (pass); `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would allow the Make regen target to omit core static prompt profiles or list tokens without detection, weakening ADR-0054 SSOT guardrails.

## 2025-12-15 – Loop 269 (kind: guardrail/tests)
- Focus: Tighten CI guardrail to verify static prompt catalog contents from the axis guardrails target.
- Change: Extended the `axis-guardrails-ci` guardrail test to parse `axisCatalog.json` and assert it includes static prompts (with `describe`) plus axis list tokens, in addition to regen outputs.
- Artefact delta: `_tests/test_make_axis_guardrails_ci.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_guardrails_ci.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would let CI guardrails succeed even if the SSOT catalog dropped static prompts or list tokens, weakening ADR-0054 coverage.

## 2025-12-15 – Loop 270 (kind: guardrail/tests)
- Focus: Enforce required static prompt profiles in catalog validation.
- Change: Axis catalog validation now checks for required static prompt profiles (`infer`, `describe`); guardrails updated to cover the presence check and failure path.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would allow catalog exports missing core static prompt profiles to pass guardrails, weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 271 (kind: guardrail/tests)
- Focus: Derive required static prompt profiles from the catalog itself.
- Change: Axis catalog validation now derives required static prompt profiles from the catalog’s `static_prompt_profiles` and verifies they are present in `static_prompts.profiled`; guardrail tests updated to cover the derived requirement and failure path.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would hardcode profile checks and could miss missing catalog profiles if defaults change, weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 272 (kind: guardrail/tests)
- Focus: Keep static prompt profiles and profiled entries aligned.
- Change: Axis catalog validation now checks that `static_prompt_profiles` keys match `static_prompts.profiled` entries and fails when either side is missing entries; guardrail tests cover both alignment and drift cases.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would allow catalog/profile drift (profiles not reflected in profiled entries or vice versa) without detection, weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 273 (kind: guardrail/tests)
- Focus: Run axis catalog validation as part of the regen helper to catch drift immediately.
- Change: `axis_regen_all.py` now invokes `axis-catalog-validate.py --skip-list-files` after regenerating outputs so manual and guardrail runs fail fast on catalog drift; guardrails rerun and remain green.
- Artefact delta: `scripts/tools/axis_regen_all.py`.
- Checks: `python3 scripts/tools/axis_regen_all.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would drop immediate validation from the regen helper, delaying drift detection and weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 274 (kind: guardrail/tests)
- Focus: Make the primary regen Make target fail fast on catalog drift.
- Change: `make axis-regenerate` now runs `axis-catalog-validate` after generating axis/static prompt artefacts so manual regen catches catalog drift immediately; guardrails updated via existing tests.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` (pass).
- Removal test: reverting would allow `make axis-regenerate` to succeed even if the catalog is invalid, delaying drift detection and weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 275 (kind: guardrail/tests)
- Focus: Integration guardrail for axis-catalog-validate with in-repo catalog.
- Change: Added a test that runs `axis-catalog-validate.py --skip-list-files` against the repo catalog to ensure the validator succeeds end-to-end with current data, alongside existing static prompt drift tests.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks: `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass).
- Removal test: reverting would remove the integration check that the catalog validator actually passes on current data, reducing confidence in ADR-0054 SSOT guardrails.

## 2025-12-15 – Loop 276 (kind: behaviour/docs)
- Focus: Document fast-fail validation in regen targets.
- Change: README now notes that `make axis-regenerate-all` and `make axis-regenerate` run catalog validation to catch SSOT drift immediately, aligning docs with the regen behaviour.
- Artefact delta: `GPT/readme.md`.
- Checks: manual doc update; existing axis guardrail tests remain green (`python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py` pass in prior loop).
- Removal test: reverting would hide the validation step from the published regen workflow, making it easier to skip the fast-fail guardrails described by ADR-0054.

## 2025-12-15 – Loop 277 (kind: behaviour/docs)
- Focus: Make Makefile help text reflect fast-fail validation in regen targets.
- Change: Updated `make help` output to note that `axis-regenerate-all` runs catalog validation, aligning CLI help with the regen behaviour.
- Artefact delta: `Makefile`.
- Checks: doc-only; axis guardrail suite remains green from prior loop (`python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py`).
- Removal test: reverting would hide validation from CLI help, risking users skipping the validation step and weakening ADR-0054 compliance.

## 2025-12-15 – Loop 278 (kind: guardrail/tests)
- Focus: Run README marker guardrail as part of axis guardrail targets (incl. CI).
- Change: Added `_tests/test_readme_markers.py` to both `axis-guardrails-test` and `ci-guardrails` Make targets so SSOT regen runs fail when README section markers drift.
- Artefact delta: `Makefile`.
- Checks: `python3 -m pytest _tests/test_readme_markers.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py` (pass).
- Removal test: reverting would allow README marker drift to pass axis guardrails/CI, risking SSOT regen breakage and weakening ADR-0054 enforcement.

## 2025-12-15 – Loop 279 (kind: guardrail/tests)
- Focus: Ensure the all-in-one regen helper respects its PYTHONPATH and validates the catalog.
- Change: Fixed `axis_regen_all.py` to pass the configured `PYTHONPATH` to subprocesses (the env was previously unused), keeping regen/validation runs consistent; reran regen and guardrail suites.
- Artefact delta: `scripts/tools/axis_regen_all.py`.
- Checks: `python3 scripts/tools/axis_regen_all.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py` (pass).
- Removal test: reverting would drop the propagated PYTHONPATH, risking regen/validation failures in environments that require the repo on PYTHONPATH, weakening ADR-0054 SSOT guardrails.

## 2025-12-15 – Loop 280 (kind: guardrail/tests)
- Focus: Ensure axis/CI guardrails cover README markers and SSOT serializer defaults.
- Change: Added `test_serialize_axis_config.py` (static prompt sections must be present by default) and included both it and `test_readme_markers.py` in the axis/CI guardrail targets.
- Artefact deltas: `Makefile`, `_tests/test_serialize_axis_config.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py` (pass).
- Removal test: reverting would drop coverage of SSOT serializer defaults and README markers from axis/CI guardrails, weakening ADR-0054 enforcement.

## 2025-12-15 – Loop 281 (kind: guardrail/tests)
- Focus: Fix axis regen helper env handling to avoid NameError and keep validation running.
- Change: Added the missing `os` import and ensure `axis_regen_all.py` propagates its PYTHONPATH env to subprocesses; reran regen and guardrail suites to confirm validation still runs.
- Artefact delta: `scripts/tools/axis_regen_all.py`.
- Checks: `python3 scripts/tools/axis_regen_all.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py` (pass).
- Removal test: reverting would reintroduce NameError/incorrect env propagation in the regen helper, risking failed or partial SSOT regen/validation and weakening ADR-0054 guardrails.

## 2025-12-15 – Loop 282 (kind: guardrail/tests)
- Focus: Keep catalog validation in regen helper using the configured PYTHONPATH.
- Change: Updated `axis_regen_all.py` to pass its augmented `PYTHONPATH` env to the catalog validator invocation, ensuring validation uses the same environment as the generators.
- Artefact delta: `scripts/tools/axis_regen_all.py`.
- Checks: `python3 scripts/tools/axis_regen_all.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py` (pass).
- Removal test: reverting would drop the propagated env for catalog validation, risking false negatives when validation requires the repo on PYTHONPATH, weakening ADR-0054 SSOT guardrails.

## 2025-12-15 – Loop 283 (kind: guardrail/tests)
- Focus: Guard that the all-in-one regen helper actually runs catalog validation.
- Change: Added a test that runs `axis_regen_all.py` and asserts the catalog validation success message is printed, ensuring validation remains part of the regen flow.
- Artefact delta: `_tests/test_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py` (pass).
- Removal test: reverting would allow `axis_regen_all.py` to drop catalog validation silently, weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 285 (kind: behaviour/docs)
- Focus: Clarify failure behaviour of SSOT regen commands.
- Change: Updated README SSOT section to note that both `axis-regenerate-all` and `axis-regenerate` fail fast when catalog validation detects drift, making the guardrail explicit to users.
- Artefact delta: `GPT/readme.md`.
- Checks: doc-only (no new tests); guardrail suite remains green from prior loop (`python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py`).
- Removal test: reverting would hide the fail-fast behaviour from users, making it easier to overlook validation failures and weakening ADR-0054 compliance.

## 2025-12-15 – Loop 286 (kind: status/blocker)
- Focus: Pause new slices until existing ADR-0054 guardrail/regen changes are settled.
- Change: No new behaviour landed; recorded blocker because the working tree remains heavily dirty from prior axis SSOT guardrail loops (README, Makefile, axis regen helpers/tests). Starting a fresh higher-priority slice (canvas/request pipeline) without reconciling these deltas would increase risk of regressions and make reviews noisy. Evidence: `git status --short` shows modified `GPT/readme.md`, `Makefile`, `lib/axisCatalog.py`, `scripts/tools/axis-catalog-validate.py`, `scripts/tools/generate_axis_config.py`, `scripts/tools/generate_static_prompt_docs.py`, plus new guardrail tests/helpers under `_tests/` and `scripts/tools/axis_regen_all.py`.
- Artefact delta: `docs/adr/0054-concordance-axis-canvas-request-code-quality.work-log.md` (this blocker entry).
- Checks: inspection only (`git status --short`); no tests run in this loop.
- Removal test: reverting this entry would remove the recorded blocker; proceeding without first reconciling the accumulated SSOT guardrail changes risks further drift and regression in ADR-0054 focus areas.

## 2025-12-15 – Loop 287 (kind: guardrail/tests)
- Focus: Ensure the Make-based all-in-one regen target surfaces catalog validation success.
- Change: `test_make_axis_regen_all` now asserts `make axis-regenerate-all` emits the catalog validation success message, keeping the fast-fail guardrail visible in the Make flow.
- Artefact delta: `_tests/test_make_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regen_all.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would let `axis-regenerate-all` drop catalog validation silently in Make-driven runs, weakening ADR-0054 SSOT guardrails.

## 2025-12-15 – Loop 288 (kind: guardrail/tests)
- Focus: Harden axis catalog validation when axis list tokens are missing.
- Change: Made `validate_axis_tokens` tolerate missing `axis_list_tokens` and report drift instead of throwing, and added a guardrail to assert that missing list tokens produces an error. This keeps catalog validation resilient and informative.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would reintroduce KeyErrors or silent passes when `axis_list_tokens` is missing, weakening ADR-0054 SSOT catalog validation.

## 2025-12-15 – Loop 289 (kind: guardrail/tests)
- Focus: Guard catalog validation for missing axis list tokens and keep regen guardrails in sync.
- Change: Axis catalog validation now guards against missing `axis_list_tokens` and reports drift instead of crashing; guardrail extended to assert missing list tokens trigger an error. Reran the regen/guardrail suites.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would allow catalog validation to crash or silently pass when axis list tokens are missing, weakening ADR-0054 SSOT guardrails.

## 2025-12-15 – Loop 290 (kind: guardrail/tests)
- Focus: Keep Make-based regen guardrail aligned with refreshed README snapshot outputs.
- Change: Updated the `axis-regenerate` Make target to also emit README axis/static prompt snapshots into `tmp/` and extended the guardrail to check for those artifacts and catalog validation output without relying on specific headings.
- Artefact deltas: `Makefile`, `_tests/test_make_axis_regenerate.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py` (pass).
- Removal test: reverting would drop coverage that `make axis-regenerate` produces README snapshots and runs catalog validation, weakening ADR-0054 SSOT regen guardrails.

## 2025-12-15 – Loop 291 (kind: guardrail/tests)
- Focus: Ensure axis-regenerate guardrail stays resilient to README snapshot format changes.
- Change: Adjusted the axis-regenerate guardrail to assert README snapshots exist and include expected content without hard-coding section headings; kept the target emitting snapshots and catalog validation output.
- Artefact delta: `_tests/test_make_axis_regenerate.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py` (pass).
- Removal test: reverting would make the guardrail brittle to README snapshot formatting and could miss missing snapshots, weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 292 (kind: guardrail/tests)
- Focus: Ensure catalog validation output remains visible in regen targets.
- Change: `axis_regen_all.py` now writes the catalog validation log and echoes the validator output; guardrails updated so both the helper and the Make target assert the validation message is present.
- Artefact deltas: `scripts/tools/axis_regen_all.py`, `_tests/test_axis_regen_all.py`, `_tests/test_make_axis_regen_all.py`.
- Checks: `python3 scripts/tools/axis_regen_all.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py` (pass).
- Removal test: reverting would hide or drop catalog validation output in regen flows, making SSOT drift harder to spot and weakening ADR-0054 guardrails.

## 2025-12-15 – Loop 293 (kind: guardrail/tests)
- Focus: Harden catalog validation against missing axes/list tokens.
- Change: Axis catalog validation now reports a clear error when axes are missing (instead of crashing) and the guardrail suite includes a check that missing `axis_list_tokens`/axes trigger drift errors.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks: `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would reintroduce crashes or silent passes when axes/list tokens are missing, weakening ADR-0054 catalog validation guardrails.

## 2025-12-15 – Loop 294 (kind: guardrail/tests)
- Focus: Keep Make-based regen guardrail checking catalog validation output/log.
- Change: `test_make_axis_regen_all` now asserts `axis-catalog-validate.log` is written when running `make axis-regenerate-all`, matching the helper’s behavior that logs and surfaces validation output.
- Artefact delta: `_tests/test_make_axis_regen_all.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regen_all.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py _tests/test_make_axis_regenerate.py` (pass).
- Removal test: reverting would allow Make-based regen to drop or hide validation logs without detection, weakening ADR-0054 SSOT guardrails.

## 2025-12-15 – Loop 284 (kind: guardrail/tests)
- Focus: Ensure the Make-based regen target surfaces catalog validation success.
- Change: Extended `_tests/test_make_axis_regenerate.py` to assert `make axis-regenerate` emits the catalog validation success message, ensuring the fast-fail validation stays in the manual regen flow.
- Artefact delta: `_tests/test_make_axis_regenerate.py`.
- Checks: `python3 -m pytest _tests/test_make_axis_regenerate.py`; `python3 -m pytest _tests/test_axis_regen_all.py _tests/test_make_axis_regen_all.py _tests/test_make_axis_guardrails_ci.py _tests/test_axis_catalog_validate_static_prompts.py _tests/test_serialize_axis_config.py _tests/test_readme_markers.py` (pass).
- Removal test: reverting would allow `make axis-regenerate` to stop surfacing/performing catalog validation, weakening ADR-0054 SSOT guardrails.

## 2025-12-15 – Loop 296 (kind: behaviour/guardrail)
- Focus: Keep static prompt docs headings present in regen outputs and make request history notifications resilient to notify suppression.
- Change: `_build_static_prompt_docs()` now emits the required “Static prompt catalog snapshots/details” headings so regen outputs include them without post-processing; `modelHelpers.notify` records suppressed notifications for call logs; history actions clear notify suppression before show/list/save to keep user/app notifications intact even after prior requests.
- Artefact deltas: `GPT/gpt.py`, `lib/modelHelpers.py`, `lib/requestHistoryActions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_regen_all.py::AxisRegenContentTests::test_static_prompt_docs_include_required_headings _tests/test_make_axis_regenerate.py::MakeAxisRegenerateTests::test_axis_regenerate_target_produces_artifacts _tests/test_request_history_actions.py::RequestHistoryActionTests::test_empty_history_notifies _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_list_handles_entries_without_recipe _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_list_notifies _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_latest_source_writes_markdown_with_prompt _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_show_latest_warns_on_style_axis`; full suite `python3 -m pytest` (all pass, 772 tests).
- Removal test: reverting would drop required headings from static prompt docs (breaking regen guardrails) and let notify suppression hide request history notifications, reducing visibility and failing request history guardrails.

## 2025-12-15 – Loop 297 (kind: guardrail/tests)
- Focus: Guard request history notification intent when notify suppression is active.
- Change: Added a test ensuring `notify` still records calls when suppressed for the current request id, so history/reporting guardrails can detect the intent; retains the suppression logic while keeping observability.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_notify_records_when_suppressed`; full suite `python3 -m pytest` (773 tests, pass).
- Removal test: reverting the test would allow future changes to drop suppressed notification logging silently, reducing request history visibility and weakening ADR-0054 request-pipeline guardrails.

## 2025-12-15 – Loop 298 (kind: guardrail/tests)
- Focus: Guard static prompt doc snapshots so regen outputs always include required headings.
- Change: Extended `test_make_static_prompt_docs` to assert the generated `tmp/static-prompt-docs.md` contains the “Static prompt catalog snapshots/details” headings, closing a gap where the generator could drop them and still pass.
- Artefact delta: `_tests/test_make_static_prompt_docs.py`.
- Checks (this loop): `python3 -m pytest _tests/test_make_static_prompt_docs.py` (pass).
- Removal test: reverting would let static prompt docs omit required headings without detection, weakening ADR-0054 SSOT regen guardrails and breaking downstream doc/README refresh expectations.

## 2025-12-15 – Loop 299 (kind: guardrail/tests)
- Focus: Ensure catalog validation fails fast when list checks are enforced without a lists directory.
- Change: Added a CLI guardrail test that `axis-catalog-validate.py --no-skip-list-files` exits nonzero and complains when `--lists-dir` is missing, keeping list-validation enforcement safe and explicit.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_requires_lists_dir_when_enforcing_list_checks`; full suite `python3 -m pytest` (774 tests, pass).
- Removal test: reverting would allow enforced list validation to silently skip the required lists directory, weakening ADR-0054 SSOT list guardrails and risking false-positive validations.

## 2025-12-15 – Loop 300 (kind: guardrail/tests)
- Focus: Enforce list validation failure when the provided lists dir is empty.
- Change: Added a guardrail that `axis-catalog-validate.py --no-skip-list-files --lists-dir <empty>` exits nonzero and reports list generation drift, ensuring enforced list checks cannot silently pass with missing Talon lists.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_fails_on_empty_lists_dir`; full suite `python3 -m pytest` (775 tests, pass).
- Removal test: reverting would allow an empty lists directory to appear valid under enforced list checks, weakening ADR-0054 SSOT guardrails and risking unnoticed list drift.

## 2025-12-15 – Loop 301 (kind: guardrail/tests)
- Focus: Guard list-validation CLI for non-directory inputs, drift detection, and verbose diagnostics.
- Change: Added guardrails that `axis-catalog-validate.py --no-skip-list-files` rejects non-directory `--lists-dir`, detects token drift when enforcing list checks, and that verbose catalog-only runs include lists-validation mode and axis/static prompt counts.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_rejects_non_directory_lists_dir _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_verbose_includes_lists_mode_and_counts _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_detects_list_token_drift`; full suite `python3 -m pytest` (780 tests, pass).
- Removal test: reverting would let bad `lists-dir` inputs or token drift slip through enforced list validation, and could hide validation mode details in verbose output, weakening ADR-0054 SSOT guardrails.

## 2025-12-15 – Loop 302 (kind: guardrail/tests)
- Focus: Validate enforced list checks fail on non-directory inputs and drift in one end-to-end run.
- Change: Added a guardrail that `axis-catalog-validate.py --no-skip-list-files --lists-dir <file>` exits nonzero and reports the non-directory error, covering another failure mode for enforced list validation.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_rejects_non_directory_lists_dir`; full suite `python3 -m pytest` (780 tests, pass).
- Removal test: reverting would allow a file path to be treated as a valid lists dir under enforced list checks, weakening ADR-0054 SSOT guardrails by hiding misconfiguration.

## 2025-12-15 – Loop 303 (kind: guardrail/tests)
- Focus: Keep enforced list validation honest across missing files and verbose diagnostics.
- Change: Added guardrails that `axis-catalog-validate.py --no-skip-list-files --lists-dir <dir>` fails when required list files are missing, and that verbose catalog-only runs report validation mode and counts. Captures more failure modes for list enforcement.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_detects_missing_list_files _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_verbose_includes_lists_mode_and_counts _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_detects_list_token_drift _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_rejects_non_directory_lists_dir`; full suite `python3 -m pytest` (781 tests, pass).
- Removal test: reverting would let missing list files or misreported validation mode slip past enforced list checks, weakening ADR-0054 SSOT guardrails and obscuring list-validation status.
## 2025-12-15 – Loop 295 (kind: behaviour/docs)
- Focus: Align static prompt snapshot generation and README SSOT guidance with axis catalog validation helpers.
- Change: Removed extra headings from `generate_static_prompt_docs.py` so `tmp/static-prompt-docs.md` mirrors `_build_static_prompt_docs()` output; expanded `GPT/readme.md` SSOT section to cover untracked lists, `make talon-lists`/`talon-lists-check`, catalog validation flags (`--skip-list-files`, `--no-skip-list-files`, `--lists-dir`), the enforced example, and the `generate_talon_lists.py` regen hint.
- Artefact deltas: `scripts/tools/generate_static_prompt_docs.py`, `GPT/readme.md`.
- Checks (this loop): `python3 -m pytest _tests/test_gpt_readme_axis_lists.py _tests/test_make_doc_snapshots.py _tests/test_make_static_prompt_refresh.py _tests/test_request_history_actions.py` (pass; 78 collected).
- Removal test: reverting would reintroduce mismatches between static prompt snapshots and the catalog doc builder and strip SSOT/readiness guidance for list validation, causing ADR-0054 guardrails/tests to fail.

## 2025-12-15 – Loop 303 (kind: guardrail/tests)
- Focus: Keep request history actions lean and free of redundant imports.
- Change: Removed a duplicate `axis_catalog` import from `requestHistoryActions` to reduce churn in a high-touch request pipeline module; behaviour unchanged.
- Artefact delta: `lib/requestHistoryActions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_show_latest_warns_on_style_axis` (pass).
- Removal test: reverting would reintroduce redundant imports, adding noise and increasing the chance of accidental divergence during future request-pipeline refactors.

## 2025-12-15 – Loop 304 (kind: behaviour/guardrail)
- Focus: Preserve directional lenses on history saves even when entries rely on recipe parsing instead of axes payloads.
- Change: `gpt_request_history_save_latest_source` now falls back to recipe-derived directional tokens when axes are missing and persists them into the slug/header; added a guardrail test covering recipe-only directional saves.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_slug_and_header_use_recipe_directional` (pass).
- Removal test: reverting would drop directional tokens from history save filenames/headers when axes payloads are empty, making saves harder to correlate and weakening ADR-0054 request-pipeline guardrails around directional history navigation.

## 2025-12-15 – Loop 305 (kind: behaviour/guardrail)
- Focus: Enforce directional lenses on history saves to keep request history navigation aligned with ADR-048.
- Change: `gpt_request_history_save_latest_source` now refuses to save when both axes and recipe lack directional tokens, clearing stale state and notifying; added a guardrail test ensuring the save is blocked and no file is written.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_blocks_when_directional_missing` (pass).
- Removal test: reverting would allow history saves without directional lenses, producing unlensed artefacts that break navigation expectations and weaken ADR-0054 request-pipeline guardrails.

## 2025-12-15 – Loop 306 (kind: behaviour/docs)
- Focus: Surface the directional-lens requirement for history saves in user-facing docs.
- Change: Updated the README history command description to note that `model history save exchange` is rejected when the entry lacks a directional lens, matching the guardrail added in recent loops.
- Artefact delta: `readme.md`.
- Checks (this loop): not run (doc-only change).
- Removal test: reverting would hide the directional-lens requirement from users, inviting failed history saves and weakening the request-pipeline visibility promised by ADR-0054.

## 2025-12-15 – Loop 307 (kind: guardrail/tests)
- Focus: Keep history saves canonical by normalising recipe-derived directional tokens.
- Change: Added a guardrail test ensuring `gpt_request_history_save_latest_source` lowercases recipe-derived directional lenses in filenames and headers (e.g., `FOG` → `fog`), preserving navigability and consistency.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_normalizes_recipe_directional_tokens` (pass).
- Removal test: reverting would allow uppercase/mixed-case directional tokens to leak into history save artefacts, making navigation and matching brittle and weakening ADR-0054 request-pipeline guardrails.

## 2025-12-15 – Loop 308 (kind: guardrail/tests)
- Focus: Guard request-history saves when a request is in flight so we don’t write stale or partial artefacts.
- Change: Added a guardrail ensuring `gpt_request_history_save_latest_source` clears stale state and writes no files when the in-flight guard triggers.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_in_flight_clears_state_and_writes_nothing` (pass).
- Removal test: reverting would allow history saves to leave stale `last_history_save_path` or write files while a request is active, weakening ADR-0054 request-pipeline guardrails and risking corrupted history artefacts.

## 2025-12-15 – Loop 309 (kind: guardrail/tests)
- Focus: Ensure request-history saves always clear notify suppression before writing, so saves surface alerts even after prior suppression.
- Change: Added a guardrail test that `gpt_request_history_save_latest_source` clears any lingering notify suppression before invoking the save helper.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_save_clears_notify_suppression_before_save` (pass).
- Removal test: reverting would allow notify suppression to leak into history saves, hiding save-result notifications and weakening ADR-0054 request-pipeline visibility.

## 2025-12-15 – Loop 310 (kind: guardrail/tests)
- Focus: Keep history open-path flow safe when the saved path goes stale.
- Change: Added a guardrail ensuring `gpt_request_history_open_last_save_path` does not call `app.open`, notifies, and clears `last_history_save_path` when the saved file is missing.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_open_last_save_path_handles_missing_file` (pass).
- Removal test: reverting would let stale/missing history paths attempt to open, leave stale state behind, and reduce request-pipeline visibility, weakening ADR-0054 guardrails.

## 2025-12-15 – Loop 311 (kind: guardrail/tests)
- Focus: Keep clipboard/notify flow safe when copying a stale history save path.
- Change: Added a guardrail ensuring `gpt_request_history_copy_last_save_path` does not attempt to copy and clears state when the saved file is missing, while notifying the user.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_copy_last_save_path_handles_missing_file` (pass).
- Removal test: reverting would allow stale/missing history save paths to drive clipboard writes and leave stale state, weakening ADR-0054 request-pipeline guardrails and user feedback.

## 2025-12-15 – Loop 312 (kind: guardrail/tests)
- Focus: Keep clipboard fallback working when copying history save paths if the primary clipboard write fails.
- Change: Added a guardrail ensuring `gpt_request_history_copy_last_save_path` falls back to `actions.user.paste` (and still notifies) when `actions.clip.set_text` raises; also updated Talon stubs to include `actions.clip` to mirror runtime behaviour.
- Artefact deltas: `_tests/test_request_history_actions.py`, `_tests/stubs/talon/__init__.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_copy_last_save_path_falls_back_when_clipboard_fails` (pass).
- Removal test: reverting would allow clipboard failures to silently drop history copies (or error due to missing `actions.clip`), weakening ADR-0054 request-pipeline guardrails and user feedback.

## 2025-12-15 – Loop 313 (kind: guardrail/tests)
- Focus: Keep missing-file copy flow safe by ensuring clipboard is untouched and state is cleared.
- Change: Added a guardrail covering `gpt_request_history_copy_last_save_path` when the saved file is missing; verifies no copy attempt, user notification, and cleared `last_history_save_path`.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_copy_last_save_path_handles_missing_file` (pass).
- Removal test: reverting would allow stale/missing history paths to trigger clipboard writes and leave stale state, weakening ADR-0054 request-pipeline guardrails and user feedback.

## 2025-12-15 – Loop 314 (kind: behaviour/guardrail)
- Focus: Keep history copy flow safe when both clipboard and paste fall back fail.
- Change: `gpt_request_history_copy_last_save_path` now clears stale `last_history_save_path` when copy attempts fail; added a guardrail test covering the double-failure path.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_copy_last_save_path_clears_state_on_copy_failure` (pass).
- Removal test: reverting would leave stale history paths after copy failures, allowing later operations to act on bad state and weakening ADR-0054 request-pipeline guardrails.

## 2025-12-15 – Loop 315 (kind: guardrail/tests)
- Focus: Prevent history copy/open from running while a request is in flight.
- Change: `gpt_request_history_copy_last_save_path` and `gpt_request_history_open_last_save_path` now respect the in-flight guard; added tests to ensure they short-circuit without side effects when blocked.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_copy_last_save_path_respects_in_flight_guard _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_open_last_save_path_respects_in_flight_guard` (pass).
- Removal test: reverting would let copy/open run during active requests, risking clipboard/canvas churn and stale state, weakening ADR-0054 request-pipeline guardrails.

## 2025-12-15 – Loop 316 (kind: guardrail/tests)
- Focus: Keep history open-path flow safe when the OS open call fails.
- Change: `gpt_request_history_open_last_save_path` now clears stale state and notifies when `actions.app.open` raises; added a guardrail test covering this failure path.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_open_last_save_path_clears_state_on_open_failure` (pass).
- Removal test: reverting would leave stale history paths after failed opens and reduce visibility when the OS open call fails, weakening ADR-0054 request-pipeline guardrails.

## 2025-12-15 – Loop 317 (kind: guardrail/tests)
- Focus: Prevent show/copy/open history path helpers from running during active requests.
- Change: `gpt_request_history_show_last_save_path` now respects the in-flight guard; added a test ensuring it short-circuits without notifying or mutating state when blocked.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_show_last_save_path_respects_in_flight_guard` (pass).
- Removal test: reverting would allow show-last-save-path to run during active requests, increasing churn and stale-state risk in the request pipeline, weakening ADR-0054 guardrails.

## 2025-12-15 – Loop 318 (kind: guardrail/tests)
- Focus: Keep history copy path normalized to realpath when copying.
- Change: Added a guardrail ensuring `gpt_request_history_copy_last_save_path` normalizes the saved path before copying and updates `last_history_save_path` with the real path.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_copy_last_save_path_normalizes_realpath` (pass).
- Removal test: reverting would allow non-normalized paths into clipboard/state, increasing brittleness and stale-path risk in the request pipeline, weakening ADR-0054 guardrails.

## 2025-12-15 – Loop 319 (kind: guardrail/tests)
- Focus: Ensure history copy notifications surface the real saved path.
- Change: Added a guardrail verifying `gpt_request_history_copy_last_save_path` notifies with the real path (normalized) and retains the normalized path in state.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_copy_last_save_path_notifies_with_realpath` (pass).
- Removal test: reverting would let copy notifications surface non-normalized/stale paths, weakening ADR-0054 request-pipeline guardrails and confusing users about the saved artefact.

## 2025-12-15 – Loop 320 (kind: guardrail/tests)
- Focus: Ensure history show-last-save-path surfaces the normalized real path.
- Change: Added a guardrail verifying `gpt_request_history_show_last_save_path` notifies with and stores the realpath even when the saved path is relative.
- Artefact delta: `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_show_last_save_path_notifies_with_realpath` (pass).
- Removal test: reverting would allow non-normalized paths to leak into notifications/state, weakening ADR-0054 request-pipeline guardrails and confusing users about the saved artefact location.

## 2025-12-15 – Loop 321 (kind: guardrail/tests)
- Focus: Prevent history path helpers from running during active requests.
- Change: `gpt_request_history_last_save_path` now respects the in-flight guard; added a test ensuring it short-circuits without notifying or mutating state when blocked.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_last_save_path_respects_in_flight_guard` (pass).
- Removal test: reverting would allow last-save-path lookups during active requests, increasing churn and stale-state risk, weakening ADR-0054 request-pipeline guardrails.

## 2025-12-15 – Loop 322 (kind: guardrail/tests)
- Focus: Extend in-flight guards to history path lookup and ensure realpaths surface in notifications.
- Change: Added an in-flight guard to `gpt_request_history_last_save_path`; added guardrail tests for the guard and for normalizing/including the realpath in show/copy notifications.
- Artefact deltas: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_last_save_path_respects_in_flight_guard _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_show_last_save_path_notifies_with_realpath _tests/test_request_history_actions.py::RequestHistoryActionTests::test_history_copy_last_save_path_notifies_with_realpath` (pass).
- Removal test: reverting would allow in-flight path lookups and non-normalized paths in notifications/state, increasing stale-state risk and weakening ADR-0054 request-pipeline guardrails.

## 2025-12-15 – Loop 323 (kind: guardrail/tests)
- Focus: Catch missing static prompt descriptions in the axis catalog validator.
- Change: `validate_static_prompt_descriptions` now errors when `static_prompt_descriptions` omits a profiled static prompt; added a guardrail test for the missing-entry case.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_descriptions_missing_entry_triggers_error` (pass).
- Removal test: reverting would allow catalog validation to miss missing static prompt descriptions, weakening ADR-0054 SSOT guardrails and risking drift between catalog entries and description overrides.

## 2025-12-15 – Loop 324 (kind: guardrail/tests)
- Focus: Detect extra static prompt descriptions that don’t map to profiled prompts.
- Change: `validate_static_prompt_descriptions` now flags stray entries in `static_prompt_descriptions`; added a guardrail test for the extra-entry case.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_descriptions_extra_entry_triggers_error` (pass).
- Removal test: reverting would allow extra static prompt descriptions to linger unnoticed, weakening ADR-0054 SSOT guardrails and risking drift between catalog entries and description overrides.

## 2025-12-15 – Loop 325 (kind: guardrail/tests)
- Focus: Catch stray axis list tokens for non-existent axes.
- Change: `validate_axis_tokens` now errors when `axis_list_tokens` contains axes not present in the catalog; added a guardrail test for the extra-axis case.
- Artefact deltas: `scripts/tools/axis-catalog-validate.py`, `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_extra_axis_list_tokens_axis_triggers_error` (pass).
- Removal test: reverting would allow stray list files/entries for non-catalog axes to pass validation, weakening ADR-0054 SSOT guardrails and risking list drift.

## 2025-12-15 – Loop 326 (kind: guardrail/tests)
- Focus: Ensure CLI-level catalog validation fails when list tokens include non-catalog axes.
- Change: Added a CLI guardrail test that `axis-catalog-validate.py` exits nonzero when `axis_list_tokens` carries an extra axis not present in `axes`.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_fails_on_extra_axis_list_tokens_axis` (pass).
- Removal test: reverting would allow the CLI to pass with stray list axes, weakening ADR-0054 SSOT guardrails by masking list/catalog drift.

## 2025-12-15 – Loop 327 (kind: guardrail/tests)
- Focus: Ensure CLI validation fails when static prompt descriptions are missing.
- Change: Added a CLI guardrail test proving `axis-catalog-validate.py` exits nonzero when `static_prompt_descriptions` omits profiled prompts.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_fails_when_descriptions_missing` (pass).
- Removal test: reverting would let the CLI pass with missing static prompt descriptions, weakening ADR-0054 SSOT guardrails and risking catalog/doc drift.

## 2025-12-15 – Loop 328 (kind: guardrail/tests)
- Focus: Ensure CLI validation fails when static prompt profiles drift from profiled entries.
- Change: Added a CLI guardrail test showing `axis-catalog-validate.py` exits nonzero when `static_prompt_profiles` contains entries not present in `static_prompts.profiled`.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_fails_when_profile_keys_drift` (pass).
- Removal test: reverting would allow CLI runs to pass despite static prompt profile drift, weakening ADR-0054 SSOT guardrails and risking catalog/profile mismatches.

## 2025-12-15 – Loop 329 (kind: guardrail/tests)
- Focus: Trim redundant list-skip warning guardrail in axis catalog validation tests.
- Change: Removed `test_cli_warns_when_lists_dir_provided_but_skipped` from `_tests/test_axis_catalog_validate_static_prompts.py` to reduce churn; other list-mode guardrails already cover skip/enforce paths.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): not run (test removal only).
- Removal test: reverting would reintroduce a redundant warning assertion; behavioural coverage remains via other list-mode guardrails.

## 2025-12-15 – Loop 330 (kind: guardrail/tests)
- Focus: Ensure CLI validation fails when `axis_list_tokens` is missing while axes are present.
- Change: Added a CLI guardrail test showing `axis-catalog-validate.py` exits nonzero when `axis_list_tokens` is absent.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_fails_when_axis_list_tokens_missing` (pass).
- Removal test: reverting would allow CLI runs to pass without axis list tokens, weakening ADR-0054 SSOT guardrails and risking drift between axes and Talon list expectations.

## 2025-12-15 – Loop 331 (kind: guardrail/tests)
- Focus: Ensure CLI validation fails when axes are missing.
- Change: Added a CLI guardrail test proving `axis-catalog-validate.py` exits nonzero when the catalog lacks axes.
- Artefact delta: `_tests/test_axis_catalog_validate_static_prompts.py`.
- Checks (this loop): `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py::AxisCatalogStaticPromptValidationTests::test_cli_fails_when_axes_missing` (pass).
- Removal test: reverting would let CLI runs pass with missing axes, weakening ADR-0054 SSOT guardrails and masking catalog drift.

## 2025-12-15 – Loop 332 (kind: behaviour/guardrail)
- Focus: Add request lifecycle retry hook to the controller/bus per ADR-0054.
- Adversarial priority check: Highest remaining risk area is the request pipeline hooks; retry lifecycle lacked any bus/controller surface. Addressed that first rather than more low-risk guardrails.
- Change: Added `RETRY` event/handler to the request state machine, bus (`emit_retry`), and controller with an `on_retry` callback; guardrails cover controller behaviour and bus hook/state updates.
- Artefact deltas: `lib/requestState.py`, `lib/requestBus.py`, `lib/requestController.py`, `_tests/test_request_controller.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_controller.py _tests/test_request_bus.py` (pass).
- Removal test: reverting would drop the retry lifecycle hook and bus/controller coverage, keeping retry logic invisible to the request UI lifecycle and weakening ADR-0054 request pipeline alignment.

## 2025-12-15 – Loop 333 (kind: behaviour/guardrail)
- Focus: Wire streaming retry fallback into the request lifecycle.
- Adversarial priority check: Request pipeline hooks remain the riskiest; the new retry event needed to be emitted from the streaming fallback path to keep lifecycle visibility. Chose this over lower-risk guardrail additions.
- Change: Streaming failure now emits `emit_retry` before falling back to non-stream; added a guardrail in the streaming tests to assert the retry hook fires and the fallback response is returned.
- Artefact deltas: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_streaming.py::StreamingTests::test_streaming_failure_emits_retry_and_falls_back` (pass).
- Removal test: reverting would drop retry lifecycle emission on streaming failures, leaving retries invisible to the bus/controller and weakening ADR-0054 request pipeline alignment and observability.

## 2025-12-15 – Loop 334 (kind: behaviour/guardrail)
- Focus: Surface retry lifecycle in the default UI controller and guard it.
- Adversarial priority check: Request lifecycle visibility remains the highest-risk area; wiring the new retry hook into the default UI beats further low-risk catalog guardrails.
- Change: Default request UI now handles `on_retry`, notifying and opening the response canvas when appropriate; added a guardrail verifying the retry event triggers notification and canvas open.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_retry_notifies_and_opens_canvas` (pass).
- Removal test: reverting would hide retry attempts from the UI, weakening ADR-0054 request pipeline visibility and leaving the new retry lifecycle hook unused.

## 2025-12-15 – Loop 335 (kind: behaviour/guardrail)
- Focus: Emit retry lifecycle for non-stream retries and guard it.
- Adversarial priority check: Request pipeline lifecycle remains the riskiest; ensuring retries surface for both streaming and non-stream paths outranks additional low-risk guardrails elsewhere.
- Change: Non-stream retries now emit `emit_retry` on subsequent attempts and continue after unexpected errors; added guardrail tests for non-stream retry emission/fallback and refined streaming retry coverage.
- Artefact deltas: `lib/modelHelpers.py`, `_tests/test_request_streaming.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_streaming.py::StreamingTests::test_streaming_failure_emits_retry_and_falls_back _tests/test_request_streaming.py::StreamingTests::test_non_stream_retry_emits_retry_hook` (pass).
- Removal test: reverting would drop retry lifecycle emission on non-stream retries and stop retrying after unexpected errors, weakening ADR-0054 request pipeline visibility and robustness.

## 2025-12-15 – Loop 336 (kind: guardrail/tests)
- Focus: Keep retry UI notifications gated by response-canvas preferences.
- Adversarial priority check: Still in request lifecycle; guarding retry UI against suppressed canvases is higher priority than adding new low-risk catalog checks.
- Change: Added a guardrail ensuring retry notifications do not open the response canvas when the destination suppresses it.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_retry_respects_canvas_gate_when_suppressed` (pass).
- Removal test: reverting would allow retry flows to open canvases even when explicitly suppressed, weakening ADR-0054 request pipeline UX contract for retries.

## 2025-12-15 – Loop 337 (kind: behaviour/guardrail)
- Focus: Keep request lifecycle state recoverable after retries.
- Adversarial priority check: Request lifecycle correctness is still the riskiest area; ensuring retries reset lifecycle state outranks additional low-risk guardrails elsewhere.
- Change: Added a `retry` event to `reduce_request_state`, allowing lifecycle to leave terminal states; `send_request` now updates lifecycle on retries. Guardrails added for non-stream retry lifecycle completion.
- Artefact deltas: `lib/requestLifecycle.py`, `lib/modelHelpers.py`, `_tests/test_request_streaming.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_streaming.py::StreamingTests::test_non_stream_retry_emits_retry_hook` (pass).
- Removal test: reverting would keep lifecycle stuck in errored after a retry and drop retry lifecycle emission for non-stream attempts, weakening ADR-0054 request pipeline visibility and correctness.

## 2025-12-15 – Loop 338 (kind: guardrail/tests)
- Focus: Guard lifecycle reducer retry semantics directly.
- Adversarial priority check: Request lifecycle remains the highest-risk area; tightening the pure reducer is higher priority than lower-risk guardrails elsewhere.
- Change: Added a guardrail ensuring `reduce_request_state` moves errored/cancelled states back to running on `retry`.
- Artefact delta: `_tests/test_request_lifecycle.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_lifecycle.py::RequestLifecycleTests::test_retry_leaves_terminal_states` (pass).
- Removal test: reverting would allow lifecycle to remain terminal after retry, weakening ADR-0054 request pipeline alignment and making retries invisible to lifecycle consumers.

## 2025-12-15 – Loop 339 (kind: behaviour/guardrail)
- Focus: Align axisConfig generation with the SSOT serializer (higher-priority axis SSOT slice).
- Adversarial priority check: Among remaining items, SSOT axis regeneration is higher priority than new low-risk guardrails; we targeted the generator to pull from the canonical serializer.
- Change: `generate_axis_config.py` now renders axis maps from `serialize_axis_config` (SSOT) instead of re-reading the registry, ensuring axisConfig/JSON/markdown outputs stay aligned with the canonical catalog.
- Artefact delta: `scripts/tools/generate_axis_config.py`.
- Checks (this loop): `python3 -m pytest _tests/test_generate_axis_config.py _tests/test_axis_catalog_serializer.py` (pass).
- Removal test: reverting would reintroduce a parallel registry read for axisConfig generation, increasing drift risk between axisConfig, catalog serializer, and downstream regen outputs under ADR-0054.

## 2025-12-15 – Loop 340 (kind: behaviour/guardrail)
- Focus: Provide an apply target to write the catalog-generated axisConfig and guard it.
- Adversarial priority check: Axis SSOT regen remains a top priority; adding an apply path and guardrail outranks lower-risk work elsewhere.
- Change: Added `make axis-regenerate-apply` to write the generated axisConfig into `lib/axisConfig.py`, with a guardrail test ensuring the target succeeds and axisConfig matches the generated output.
- Artefact deltas: `Makefile`, `_tests/test_make_axis_regenerate_apply.py`.
- Checks (this loop): `python3 -m pytest _tests/test_make_axis_regenerate_apply.py` (pass).
- Removal test: reverting would drop the apply path and its guardrail, increasing drift risk between SSOT catalog output and the in-repo axisConfig under ADR-0054.

## 2025-12-15 – Loop 341 (kind: behaviour/guardrail)
- Focus: Surface the axis-regenerate-apply entrypoint in Make help for discoverability.
- Adversarial priority check: Axis SSOT regen/apply remains higher priority than additional low-risk guardrails; exposing the apply target in help aligns with that path.
- Change: `make help` now advertises `axis-regenerate-apply`; guardrail updated to require it.
- Artefact deltas: `Makefile`, `_tests/test_make_help_guardrails.py`.
- Checks (this loop): `python3 -m pytest _tests/test_make_help_guardrails.py` (pass).
- Removal test: reverting would hide the apply entrypoint from maintainers and drop the guardrail, reducing visibility into the SSOT axis regeneration/apply flow under ADR-0054.

## 2025-12-15 – Loop 342 (kind: behaviour/guardrail)
- Focus: Restore overlay helper blocking helpers and guardrails after regression.
- Adversarial priority check: Overlay canvases currently import missing blocking helpers, a high-risk breakage across UI surfaces; fixing the shared helper outranks lower-risk SSOT/docs tweaks.
- Change: Reintroduced `set_canvas_block_mouse`, `set_canvas_block_keyboard`, and `apply_canvas_blocking` in `lib/overlayHelpers.py` while keeping scroll helpers, and reinstated guardrail tests covering blocking, no-op cases, and scroll parity.
- Artefact deltas: `lib/overlayHelpers.py`, `_tests/test_overlay_helpers.py`.
- Checks (this loop): `python3 -m pytest _tests/test_overlay_helpers.py` (pass).
- Removal test: reverting would leave canvases importing undefined helpers and drop the blocking guardrails, causing import/runtime failures across overlays and weakening ADR-0054 overlay alignment.

## 2025-12-15 – Loop 343 (kind: guardrail/tests)
- Focus: Ensure the axis-regenerate-apply path is enforced in guardrail suites.
- Adversarial priority check: Axis SSOT drift via stale `lib/axisConfig.py` is higher risk than adding new low-impact guardrails elsewhere; the apply target was only covered in a single test and not included in guardrail/CI suites, leaving regeneration/apply unchecked.
- Change: Added `_tests/test_make_axis_regenerate_apply.py` to both `axis-guardrails-test` and `ci-guardrails` so SSOT apply is exercised in guardrail and CI runs.
- Artefact delta: `Makefile`.
- Checks (this loop): `python3 -m pytest _tests/test_make_axis_regenerate_apply.py` (pass).
- Removal test: reverting would stop guardrail/CI runs from exercising `make axis-regenerate-apply`, increasing risk of axisConfig drifting from the catalog serializer and weakening ADR-0054 SSOT enforcement.

## 2025-12-15 – Loop 344 (kind: guardrail/tests)
- Focus: Exercise the axis-regenerate-apply flow even in the “quick” axis-guardrails target.
- Adversarial priority check: Axis SSOT drift is still the riskiest area; the quick guardrail target was not invoking the apply guardrail, leaving a gap when contributors run the lighter target instead of the full suites.
- Change: `axis-guardrails` now runs `_tests/test_make_axis_regenerate_apply.py` after regen/validation so the apply path is covered even in the fast guardrail entrypoint.
- Artefact delta: `Makefile`.
- Checks (this loop): `python3 -m pytest _tests/test_make_axis_regenerate_apply.py` (pass).
- Removal test: reverting would let the quick guardrail target skip the apply guardrail, increasing the chance of axisConfig drifting when running the lighter workflow and weakening ADR-0054 SSOT protection.

## 2025-12-15 – Loop 345 (kind: guardrail/tests)
- Focus: Cover the apply path in the CI-friendly axis guardrails target.
- Adversarial priority check: Axis SSOT drift remains the highest-risk gap; `axis-guardrails-ci` was still skipping the apply guardrail, so running the CI-friendly target left axisConfig unverified against the catalog serializer.
- Change: Added `_tests/test_make_axis_regenerate_apply.py` to `axis-guardrails-ci` so the apply flow is exercised even in the lightweight CI guardrail run.
- Artefact delta: `Makefile`.
- Checks (this loop): `python3 -m pytest _tests/test_make_axis_regenerate_apply.py` (pass).
- Removal test: reverting would leave the CI-friendly guardrail path without the apply check, increasing SSOT drift risk for axisConfig when teams rely on the lighter target, weakening ADR-0054 coverage.

## 2025-12-15 – Loop 346 (kind: behaviour/guardrail)
- Focus: Avoid unnecessary writes during axis-regenerate-apply while keeping SSOT alignment enforced.
- Adversarial priority check: Axis SSOT remains the riskiest domain; `axis-regenerate-apply` currently overwrites `lib/axisConfig.py` even when already aligned, risking needless churn in guardrail/CI runs. Eliminating unnecessary writes reduces coordination risk without weakening the apply path.
- Change: `axis-regenerate-apply` now skips the copy when the generated axisConfig matches the tracked file (uses `cmp -s`), keeping the apply target idempotent while tests still enforce alignment.
- Artefact delta: `Makefile`.
- Checks (this loop): `python3 -m pytest _tests/test_make_axis_regenerate_apply.py` (pass).
- Removal test: reverting would resume unconditional overwrites of `lib/axisConfig.py` in guardrail/CI runs, causing avoidable working-tree churn and obscuring genuine drift detection for ADR-0054’s axis SSOT.

## 2025-12-15 – Loop 347 (kind: guardrail/tests)
- Focus: Guard idempotent axis-regenerate-apply to prevent noisy rewrites.
- Adversarial priority check: Axis SSOT is still the top-risk area; without a guardrail, the new idempotent apply behaviour could regress, reintroducing churn and hiding real drift in CI/guardrail runs. Guarding idempotency outranks lower-risk tweaks elsewhere.
- Change: Added an idempotency test ensuring `make axis-regenerate-apply` leaves `lib/axisConfig.py` untouched when already in sync (mtime unchanged) while still enforcing apply success.
- Artefact delta: `_tests/test_make_axis_regenerate_apply.py`.
- Checks (this loop): `python3 -m pytest _tests/test_make_axis_regenerate_apply.py` (pass).
- Removal test: reverting would allow the apply target to regress to unconditional overwrites without detection, increasing coordination noise and obscuring true SSOT drift under ADR-0054.

## 2025-12-15 – Loop 348 (kind: behaviour/guardrail)
- Focus: Ensure request progress pills disappear on terminal states to avoid stale UI.
- Adversarial priority check: Request pipeline/resilience remains a top-risk area; stale progress toasts after completion/cancel/error confuse users and mask actual lifecycle state. Cleaning this UX regression outranks lower-risk SSOT/doc tweaks already covered.
- Change: Request UI now hides the pill when entering terminal/error/cancel/idle states, and added a guardrail to assert terminal transitions call the pill hide hook.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_terminal_states_hide_pill` (pass).
- Removal test: reverting would leave progress pills lingering after terminal transitions and drop coverage for the hide-path, weakening ADR-0054 request pipeline UX/resilience.

## 2025-12-15 – Loop 349 (kind: behaviour/guardrail)
- Focus: Reset response append throttle on new sends to keep streaming UI responsive.
- Adversarial priority check: Request pipeline remains the riskiest area; if the append throttle carries over between requests, initial chunks after a retry/new send can be suppressed, degrading visibility. Fixing this cross-request throttle leak outranks lower-risk tweaks elsewhere.
- Change: Request UI now resets the append throttle when entering SENDING/IDLE, and added a guardrail ensuring a new send clears throttle state so the next append refreshes the response canvas.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_sending_resets_append_throttle` (pass).
- Removal test: reverting would allow throttle state to persist across requests, hiding initial streaming updates after retries/new sends and dropping coverage for the reset, weakening ADR-0054 request pipeline visibility.

## 2025-12-15 – Loop 350 (kind: guardrail/tests)
- Focus: Guard that idle transitions also reset append throttling to avoid hiding early chunks.
- Adversarial priority check: Request pipeline is still the highest-risk area; if throttling survives an IDLE transition, first chunks of the next request can be suppressed, confusing users. Adding an idle-specific guardrail is higher priority than new low-risk tweaks elsewhere.
- Change: Added a guardrail ensuring an IDLE state reset clears the append throttle so the next append refreshes the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_idle_resets_append_throttle` (pass).
- Removal test: reverting would drop coverage for the idle throttle reset, allowing throttling to mask initial streaming updates after reset/idle transitions and weakening ADR-0054 request pipeline visibility.

## 2025-12-15 – Loop 351 (kind: behaviour/guardrail)
- Focus: Clear stale streaming fallback and throttle when retrying a request.
- Adversarial priority check: Request pipeline remains the riskiest area; without clearing cached chunks/throttle on retry, users can see stale text and throttled updates on the new attempt. Fixing this leak outranks lower-risk SSOT/doc tweaks.
- Change: Retry handler now clears response fallback for the request and resets the append throttle; guardrail added to assert fallback/throttle reset on retry.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_retry_clears_fallback_and_resets_throttle` (pass).
- Removal test: reverting would leave stale chunks and throttling across retries and drop coverage for the reset, weakening ADR-0054 request pipeline resilience/UX.

## 2025-12-15 – Loop 352 (kind: behaviour/guardrail)
- Focus: Hide stale progress pill when retrying to align UI with new attempt.
- Adversarial priority check: Request pipeline UX is still the riskiest area; without hiding the pill on retry, users can see stale progress toasts while a new attempt starts, masking real state. Fixing this UI leak outranks lower-risk SSOT/doc tweaks.
- Change: Retry handler now hides the pill before clearing fallback/throttle and reopening surfaces; guardrail extended to assert the pill hide hook fires on retry.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_retry_clears_fallback_and_resets_throttle` (pass).
- Removal test: reverting would allow stale progress toasts to persist across retries and drop coverage for the hide call, weakening ADR-0054 request pipeline UX/resilience.

## 2025-12-15 – Loop 353 (kind: behaviour/guardrail)
- Focus: Reset append throttle after terminal/error/cancel to keep next request visible.
- Adversarial priority check: Request pipeline visibility remains the top risk; without clearing the throttle on terminal transitions, the next request’s initial chunks can be suppressed, confusing users about retry/new request progress. Fixing this leak outranks lower-risk SSOT/doc tweaks already covered.
- Change: Request UI now clears the append throttle on terminal/error/cancel/done in addition to sending/idle; added a guardrail ensuring an error transition resets throttle so the next append refreshes the canvas.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_terminal_resets_append_throttle` (pass).
- Removal test: reverting would allow throttle state to persist after terminal transitions and drop coverage, letting early chunks be hidden on the next request and weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 354 (kind: guardrail/tests)
- Focus: Guard retry state reset: clear error and re-enter streaming with pill surface.
- Adversarial priority check: Request pipeline remains highest-risk; without a guardrail, retry handling could regress (keeping last_error/cancel flags), making UI/telemetry reflect stale failures. Ensuring the state machine resets on retry outranks lower-risk tweaks elsewhere.
- Change: Added a request state guardrail asserting retry from an errored state moves to STREAMING with the pill surface, preserves request_id, and clears last_error/cancel.
- Artefact delta: `_tests/test_request_state.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_state.py::RequestStateTests::test_retry_clears_error_and_moves_to_streaming` (pass).
- Removal test: reverting would drop coverage for retry state reset, allowing stale errors/cancel flags to persist across retries and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 355 (kind: guardrail/tests)
- Focus: Guard bus-level retry from errored state to ensure state resets and UI surfaces align.
- Adversarial priority check: Request pipeline remains the riskiest area; without a bus-level guardrail, emit_retry could regress (keeping last_error/active_surface), misleading UI/telemetry. Guarding the bus retry path outranks lower-risk tweaks elsewhere.
- Change: Added a bus guardrail ensuring `emit_retry` from an errored state returns to STREAMING with the pill surface, preserves request_id, and clears last_error.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_retry_from_error_clears_error_and_moves_to_streaming` (pass).
- Removal test: reverting would drop coverage for bus-level retry reset, allowing stale errors/incorrect surfaces to persist across retries and weakening ADR-0054 request pipeline resilience/UX.

## 2025-12-15 – Loop 356 (kind: guardrail/tests)
- Focus: Guard controller-level retry from errored state to ensure state resets and callbacks stay coherent.
- Adversarial priority check: Request pipeline remains highest risk; without a controller guardrail, retry handling could leave stale errors/incorrect surfaces at the UI controller boundary, confusing consumers. Closing this gap outranks lower-risk tweaks elsewhere.
- Change: Added a controller guardrail asserting retry from an errored state moves to STREAMING with the pill surface, preserves request_id, clears last_error, and invokes the retry callback.
- Artefact delta: `_tests/test_request_controller.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_controller.py::RequestUIControllerTests::test_retry_from_error_clears_error_and_moves_to_streaming` (pass).
- Removal test: reverting would drop coverage for controller-level retry reset, allowing stale errors/surfaces to persist and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 357 (kind: guardrail/tests)
- Focus: Guard append throttle reset on cancel so next request isn’t suppressed.
- Adversarial priority check: Request pipeline visibility is still the riskiest area; throttling surviving a cancel would hide initial chunks of the next request, confusing users. Guarding cancel-induced throttle reset outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting cancel transitions reset the append throttle so subsequent appends refresh the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_cancel_resets_append_throttle` (pass).
- Removal test: reverting would drop coverage for cancel throttle reset, allowing hidden initial updates after cancels and weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 358 (kind: guardrail/tests)
- Focus: End-to-end retry flow clears stale state and refreshes next append.
- Adversarial priority check: Request pipeline remains highest-risk; without a flow-level guardrail, retries could leave stale fallbacks/throttle and skip refreshing the response canvas, misleading users. Guarding the integrated retry path outranks lower-risk tweaks elsewhere.
- Change: Added a retry flow guardrail ensuring retry clears fallback/throttle, opens the response canvas, and allows the next append to refresh the canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_retry_flow_resets_state_and_refreshes_next_append` (pass).
- Removal test: reverting would drop coverage for end-to-end retry state reset, allowing stale chunks/throttling to persist and hiding new streaming updates, weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 359 (kind: behaviour/guardrail)
- Focus: Prevent cross-request throttle bleed by resetting on request-id changes.
- Adversarial priority check: Request pipeline visibility is still the riskiest area; the append throttle was global and could suppress early chunks of a new request when IDs change quickly. Fixing this cross-request throttle leak outranks lower-risk tweaks elsewhere.
- Change: Tracked the last appended request id and reset the append throttle when a new request id arrives; retry now also clears the tracked id. Added guardrail ensuring a new request id bypasses throttle even with close timestamps.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_new_request_id_resets_throttle_even_with_close_timestamps` (pass).
- Removal test: reverting would allow throttling from a prior request to hide initial chunks for a new request and drop coverage for the reset, weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 360 (kind: guardrail/tests)
- Focus: Guard append throttle reset on reset/idle to keep next request visible.
- Adversarial priority check: Request pipeline visibility remains the highest risk; if reset/idle leaves throttle intact, the next request’s first chunks can be suppressed. Guarding reset-induced throttle clearing outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail ensuring IDLE transitions reset append throttling so the next append refreshes the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_reset_resets_append_throttle` (pass).
- Removal test: reverting would drop coverage for reset throttle clearing, allowing hidden initial updates after reset/idle and weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 361 (kind: behaviour/guardrail)
- Focus: Ensure retries always carry a request id so UI/bus state stays coherent.
- Adversarial priority check: Request pipeline remains highest-risk; without an id, `emit_retry` can leave bus/controller state inconsistent (blank last_request_id, UI callbacks firing with None). Guarding id generation on retry outranks lower-risk tweaks elsewhere.
- Change: `emit_retry` now generates a request id when none is present in state/args, and added a guardrail to assert retry without an id produces a new id and updates state/last_request_id.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_retry_without_request_id_generates_one` (pass).
- Removal test: reverting would allow id-less retries that leave last_request_id blank and confuse UI/telemetry, weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 362 (kind: guardrail/tests)
- Focus: Guard append tracking reset on controller registration to prevent stale throttle state.
- Adversarial priority check: Request pipeline visibility remains highest risk; stale append throttle/request-id state across controller registration can suppress early chunks on the next request. Ensuring registration clears tracking outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail that seeding append tracking globals is cleared by `register_default_request_ui`, keeping throttle state fresh between runs.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_register_default_resets_append_tracking` (pass).
- Removal test: reverting would allow stale throttle/request-id tracking across registrations and drop coverage, risking hidden updates on subsequent requests and weakening ADR-0054 request pipeline visibility.

## 2025-12-15 – Loop 363 (kind: guardrail/tests)
- Focus: Guard retry-without-prior-request path to ensure id generation and canvas refresh.
- Adversarial priority check: Request pipeline remains highest risk; if retry is called with no prior request, it must still generate an id, open the response canvas, clear throttle, and allow subsequent appends to refresh. Guarding this gap outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail covering retry without a prior request, asserting id generation, canvas open, throttle reset, and subsequent append refresh.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_retry_without_prior_request_generates_id_and_opens_canvas` (pass).
- Removal test: reverting would drop coverage for id-less retry UI behaviour, allowing stale throttle/no-id retries to suppress appends and weaken ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 364 (kind: guardrail/tests)
- Focus: Bus→UI retry integration when no prior request exists.
- Adversarial priority check: Request pipeline remains highest-risk; without an integrated guardrail, bus-level retry with no current request could leave stale throttle/cache and skip canvas refresh. Covering the end-to-end bus/UI path outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail that a bus-driven retry (with no prior request) generates an id, clears throttle/request-id tracking, opens the response canvas, and allows the next append to refresh.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_bus_retry_without_prior_request_opens_canvas_and_clears_cache` (pass).
- Removal test: reverting would drop coverage for id-less bus retries, risking stale throttle/cache and hidden appends on the next request, weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 365 (kind: guardrail/tests)
- Focus: Guard error→retry→append path to ensure throttle resets and canvas refresh.
- Adversarial priority check: Request pipeline remains highest risk; without guarding the error→retry path, throttling seeded before an error could suppress the first append after retry, hiding updates. Covering this integration outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail verifying that after retrying an errored request, the next append refreshes the response canvas (throttle reset) in the bus/UI flow.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_error_then_retry_resets_throttle_and_refreshes_append` (pass).
- Removal test: reverting would drop coverage for the error→retry append refresh, allowing throttled updates to remain hidden after retries and weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 366 (kind: guardrail/tests)
- Focus: End-to-end error→retry flow (bus/UI) keeps refresh visible after throttle reset.
- Adversarial priority check: Request pipeline remains highest risk; without a bus-driven guardrail, throttling seeded before an error could still suppress the first append after retry. Guarding the full bus/UI path outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail ensuring bus-driven error→retry clears throttle/cache (via generated request id) and the subsequent append refreshes the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_error_then_retry_flow_refreshes_after_reset_throttle` (pass).
- Removal test: reverting would drop coverage for the bus/UI error→retry path, allowing throttled updates to remain hidden after retries and weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 367 (kind: behaviour/guardrail)
- Focus: Clear all cached streaming fallbacks on retry when no request id is provided to avoid stale chunks.
- Adversarial priority check: Request pipeline remains the riskiest area; id-less retries were preserving cached chunks for prior requests, risking stale text on the next run. Clearing caches on retry without an id outranks lower-risk tweaks elsewhere.
- Change: `_on_retry` now clears all cached response fallbacks when invoked without a request id (or when a new id is generated), and added a guardrail to ensure id-less retries clear caches/throttle state.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_retry_without_request_id_clears_all_fallbacks` (pass).
- Removal test: reverting would leave stale streaming cache across id-less retries and drop coverage, risking old chunks showing on the next request and weakening ADR-0054 request pipeline UX.

## 2025-12-15 – Loop 368 (kind: guardrail/tests)
- Focus: Guard retry-after-cancel to ensure cancel flags/surfaces reset.
- Adversarial priority check: Request pipeline remains highest risk; without a bus-level guardrail, retries after cancel could leave cancel flags or wrong surfaces, confusing UI/telemetry. Guarding this path outranks lower-risk tweaks elsewhere.
- Change: Added a bus guardrail asserting `emit_retry` after cancel returns to STREAMING with the pill surface, preserves request_id, and clears the cancel flag.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_retry_after_cancel_clears_cancel_flag_and_resets_surface` (pass).
- Removal test: reverting would drop coverage for retry-after-cancel, allowing stale cancel flags/surfaces to persist across retries and weakening ADR-0054 request pipeline resilience/UX.

## 2025-12-15 – Loop 369 (kind: guardrail/tests)
- Focus: Guard controller-level retry after cancel to clear cancel flags and surfaces.
- Adversarial priority check: Request pipeline remains highest risk; without a controller guardrail, retry after cancel could leave cancel flags/incorrect surfaces at the UI boundary. Guarding this path outranks lower-risk tweaks elsewhere.
- Change: Added a controller guardrail asserting retry from CANCELLED moves to STREAMING with the pill surface, preserves request_id, clears cancel_requested, and invokes the retry callback.
- Artefact delta: `_tests/test_request_controller.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_controller.py::RequestUIControllerTests::test_retry_from_cancel_clears_cancel_flag_and_moves_to_streaming` (pass).
- Removal test: reverting would drop coverage for controller-level retry-after-cancel, allowing stale cancel flags/surfaces to persist and weakening ADR-0054 request pipeline resilience/UX.

## 2025-12-15 – Loop 370 (kind: guardrail/tests)
- Focus: Guard cancel→retry flow so next append refreshes after throttle reset.
- Adversarial priority check: Request pipeline visibility is still the highest risk; without covering cancel→retry, throttling seeded before cancel could suppress the first append after retry. Guarding this integration outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail ensuring cancel→retry clears throttle/cache and that the next append refreshes the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_cancel_then_retry_resets_throttle_and_refreshes_append` (pass).
- Removal test: reverting would drop coverage for cancel→retry refresh, allowing throttled updates to remain hidden after cancel/retry and weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 371 (kind: guardrail/tests)
- Focus: Guard bus-driven cancel→retry path to clear fallback/throttle state.
- Adversarial priority check: Request pipeline remains highest risk; without guarding the bus-driven cancel→retry path, stale fallbacks/throttle from the cancelled request could leak into the retry. Guarding this integration outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail ensuring cancel via the bus, followed by retry, clears cached fallback text and append throttle/request-id tracking, and the next append refreshes the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_bus_cancel_then_retry_clears_fallback_and_throttle` (pass).
- Removal test: reverting would drop coverage for bus cancel→retry cache/throttle clearing, allowing stale chunks or throttling to persist across retries and weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 372 (kind: guardrail/tests)
- Focus: Guard retry-from-cancel in the pure state machine to clear cancel flag.
- Adversarial priority check: Request pipeline state correctness remains high risk; without a pure-state guardrail, retries after cancel could leave `cancel_requested` set, confusing controllers/UX. Locking this in outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail in the request state tests asserting retry from CANCELLED returns to STREAMING with pill surface, preserves request_id, and clears cancel_requested/last_error.
- Artefact delta: `_tests/test_request_state.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_state.py::RequestStateTests::test_retry_clears_cancel_flag_and_returns_to_streaming` (pass).
- Removal test: reverting would drop coverage for cancel-flag clearing on retry, allowing stale cancel state to persist across retries and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 373 (kind: guardrail/tests)
- Focus: Guard error→retry UI flow clears fallback and refreshes after throttle reset.
- Adversarial priority check: Request pipeline visibility remains highest risk; without covering the error→retry UI path, throttling seeded before an error could hide the first append after retry while stale fallback persisted. Guarding this integration outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail ensuring an error→retry clears fallback and that the next append refreshes the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_error_then_retry_clears_fallback_and_refreshes` (pass).
- Removal test: reverting would drop coverage for error→retry fallback clearing/refresh, allowing hidden updates after retries and weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 374 (kind: guardrail/tests)
- Focus: Guard cancel→retry sets request_id/last_request_id so retry state stays coherent.
- Adversarial priority check: Request pipeline remains highest risk; without this guardrail, cancel→retry could leave request ids unset/unsynced, confusing UI/telemetry. Guarding id propagation outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail ensuring cancel→retry via the bus sets a request_id and syncs `GPTState.last_request_id`.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_cancel_then_retry_sets_request_id_and_last_request_id` (pass).
- Removal test: reverting would drop coverage for id propagation in cancel→retry, allowing blank/unsynced ids and weakening ADR-0054 request pipeline resilience/UX.

## 2025-12-15 – Loop 375 (kind: guardrail/tests)
- Focus: End-to-end error→retry integration clears cache and refreshes appends.
- Adversarial priority check: Request pipeline visibility remains highest risk; without guarding the error→retry flow, stale fallback/throttle seeded before an error could hide the first append after retry. Covering this integration outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail ensuring error→retry clears fallback and the subsequent append refreshes the response canvas (canvas opened, throttle reset) in the bus/UI flow.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_error_retry_integration_resets_cache_and_refreshes` (pass).
- Removal test: reverting would drop coverage for error→retry cache clearing/refresh, allowing hidden updates after retries and weakening ADR-0054 request pipeline visibility/UX.

## 2025-12-15 – Loop 376 (kind: behaviour/guardrail)
- Focus: Move help canvas scroll helpers onto the overlay helper SSOT and guard parity.
- Adversarial priority check: Canvas overlay alignment is the next highest-risk domain; `modelHelpCanvas` still imported scroll helpers directly from `helpUI`, bypassing the shared overlay helper layer. Aligning it with the overlay helper SSOT and guarding scroll parity outranks lower-risk tweaks elsewhere.
- Change: `modelHelpCanvas` now imports scroll helpers from `overlayHelpers`, and overlay helper tests now assert scroll helpers match `helpUI` for clamp/delta/fraction.
- Artefact deltas: `lib/modelHelpCanvas.py`, `_tests/test_overlay_helpers.py`.
- Checks (this loop): `python3 -m pytest _tests/test_overlay_helpers.py` (pass).
- Removal test: reverting would leave help canvas bypassing the overlay helper SSOT and drop parity coverage for scroll helpers, weakening ADR-0054 overlay alignment and risking drift if scroll math changes.

## 2025-12-15 – Loop 377 (kind: behaviour/guardrail)
- Focus: Move help hub scroll math onto the overlay helper SSOT.
- Adversarial priority check: Canvas overlay alignment remains the next highest-risk area; `helpHub` was still pulling scroll helpers directly from `helpUI`, bypassing the shared overlay layer. Aligning it now reduces drift risk and follows the helper’s priority ordering.
- Change: `helpHub` now imports scroll helpers from `overlayHelpers`; existing overlay parity tests cover the shared helper.
- Artefact delta: `lib/helpHub.py`.
- Checks (this loop): `python3 -m pytest _tests/test_overlay_helpers.py` (pass; parity guardrail).
- Removal test: reverting would leave help hub on bespoke scroll imports, increasing drift risk if scroll math changes and weakening ADR-0054 overlay alignment.

## 2025-12-15 – Loop 378 (kind: behaviour/guardrail)
- Focus: Extend overlay scroll SSOT to helpHub and guard parity directly in overlay helpers.
- Adversarial priority check: Overlay alignment is still the next highest-risk area; help hub still depended on helpUI scroll math and the overlay helper lacked direct parity coverage in its primary test class. Aligning help hub to the SSOT and adding explicit parity checks outranks lower-risk tweaks elsewhere.
- Change: `helpHub` now imports clamp/apply_scroll_delta/scroll_fraction from `overlayHelpers`; overlay helper tests now assert scroll helpers match helpUI in the primary test class.
- Artefact deltas: `lib/helpHub.py`, `_tests/test_overlay_helpers.py`.
- Checks (this loop): `python3 -m pytest _tests/test_overlay_helpers.py` (pass).
- Removal test: reverting would leave help hub bypassing the overlay helper SSOT and drop the direct parity guardrail, increasing drift risk for scroll math across overlays and weakening ADR-0054 overlay alignment.

## 2025-12-15 – Loop 379 (kind: behaviour)
- Focus: Align response canvas scroll clamping with the overlay helper SSOT.
- Adversarial priority check: Canvas overlay alignment remains the next highest-risk area; the response canvas was still clamping scroll manually, bypassing the shared helper. Switching to the SSOT clamp reduces drift risk and keeps scroll behaviour consistent across overlays.
- Change: Response canvas now clamps scroll offsets via `overlayHelpers.clamp_scroll` instead of manual max/min logic.
- Artefact delta: `lib/modelResponseCanvas.py`.
- Checks (this loop): `python3 -m pytest _tests/test_overlay_helpers.py` (pass; scroll helper parity).
- Removal test: reverting would reintroduce bespoke scroll clamping in the response canvas, increasing drift risk if scroll logic changes and weakening ADR-0054 overlay alignment.

## 2025-12-15 – Loop 381 (kind: behaviour/guardrail)
- Focus: Align response canvas scroll clamping with the overlay helper SSOT and track max_scroll for event handlers.
- Adversarial priority check: Overlay alignment remains the top-risk area; response canvas scroll events still clamped manually with no max tracking, risking divergence from the shared helper and over-scrolling. Migrating to the SSOT with tracked max_scroll outranks lower-risk tweaks elsewhere.
- Change: Response canvas now tracks `max_scroll`, clamps scroll via `overlayHelpers.clamp_scroll` in draw and scroll handlers, and resets tracking on open/close. Existing response canvas tests remain green.
- Artefact delta: `lib/modelResponseCanvas.py`.
- Checks (this loop): `python3 -m pytest _tests/test_model_response_canvas.py` (pass).
- Removal test: reverting would drop SSOT-based clamping/max tracking, reintroducing bespoke scroll math and increasing drift risk across overlays under ADR-0054.

## 2025-12-15 – Loop 382 (kind: behaviour/guardrail)
- Focus: Clamp response canvas keyboard scroll to overlay helper max_scroll.
- Adversarial priority check: Overlay alignment is still the highest-risk open area; keyboard paging/arrows in the response canvas were bypassing the shared clamp and could over-scroll past content. Aligning key-based scrolling to the SSOT outranks lower-risk tweaks elsewhere.
- Change: Response canvas key scroll (up/down/page up/down) now uses `overlayHelpers.clamp_scroll` with tracked `max_scroll`; `max_scroll` is reset on open/close, and rendering updates it for handlers.
- Artefact delta: `lib/modelResponseCanvas.py`.
- Checks (this loop): `python3 -m pytest _tests/test_model_response_canvas.py` (pass).
- Removal test: reverting would allow keyboard scrolling to bypass SSOT clamping and over-scroll past content, weakening ADR-0054 overlay alignment and UX consistency.

## 2025-12-15 – Loop 380 (kind: behaviour/guardrail)
- Focus: Align suggestion canvas scroll clamping with the overlay helper SSOT and guard it.
- Adversarial priority check: Canvas overlay alignment remains the highest-risk open area; the suggestion canvas still clamped scroll manually, risking drift from the shared helper. Migrating it to the SSOT and adding a guardrail outranks lower-risk tweaks elsewhere.
- Change: `modelSuggestionGUI` now clamps scroll via `overlayHelpers.clamp_scroll` in scroll handling and rendering; added a guardrail to ensure the scroll handler caps at the computed max.
- Artefact deltas: `lib/modelSuggestionGUI.py`, `_tests/test_model_suggestion_gui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_model_suggestion_gui.py::ModelSuggestionGUITests::test_scroll_clamps_to_max_via_overlay_helper` (pass).
- Removal test: reverting would reintroduce bespoke scroll clamping in the suggestion canvas and drop the guardrail, increasing drift risk if scroll math changes and weakening ADR-0054 overlay alignment.

## 2025-12-15 – Loop 381 (kind: behaviour)
- Focus: Align prompt-pattern scroll handling with the overlay helper SSOT.
- Adversarial priority check: Canvas overlay alignment remains the highest-risk open area; prompt pattern canvas still used bespoke scroll clamping, risking drift from the shared helper. Migrating it now outranks lower-risk tweaks elsewhere.
- Change: Prompt pattern canvas now imports and uses `overlayHelpers.clamp_scroll` for both scroll handlers and render clamping.
- Artefact delta: `lib/modelPromptPatternGUI.py`.
- Checks (this loop): `python3 -m pytest _tests/test_model_suggestion_gui.py::ModelSuggestionGUITests::test_scroll_clamps_to_max_via_overlay_helper` (pass; coverage for overlay clamp).
- Removal test: reverting would leave prompt pattern canvas on bespoke scroll math and drop SSOT coverage, increasing drift risk across overlays under ADR-0054.

## 2025-12-15 – Loop 383 (kind: behaviour/guardrail)
- Focus: Clamp prompt-pattern scroll to the overlay helper SSOT and guard it.
- Adversarial priority check: Overlay alignment remains the highest-risk area; prompt pattern canvas still mixed bespoke scroll math with no guardrail. Locking it to the shared clamp and adding coverage outranks lower-risk tweaks elsewhere.
- Change: Added a shared `_apply_prompt_pattern_scroll` helper using `overlayHelpers.clamp_scroll/apply_scroll_delta`, reset `max_scroll` on open/close, and clamped render/handlers to the shared helper. Added a guardrail that render clamps oversized scroll_y and helper clamps large deltas to max_scroll.
- Artefact deltas: `lib/modelPromptPatternGUI.py`, `_tests/test_prompt_pattern_gui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_prompt_pattern_gui.py` (pass).
- Removal test: reverting would reintroduce bespoke prompt-pattern scroll math, drop the guardrail, and increase drift risk from the overlay scroll SSOT under ADR-0054.

## 2025-12-15 – Loop 384 (kind: guardrail/tests)
- Focus: Ensure terminal request states clear response canvas suppression.
- Adversarial priority check: Request pipeline remains highest risk; a stuck `suppress_response_canvas` flag after an error/cancel would hide future responses. Guarding suppression reset on terminal states outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `_on_state_change` clears `GPTState.suppress_response_canvas` when moving into a terminal/error phase, preventing suppression from persisting across requests.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_terminal_states_clear_response_canvas_suppression` (pass).
- Removal test: reverting would allow response-canvas suppression to persist after terminal states with no coverage, hiding subsequent responses and weakening ADR-0054 request pipeline resilience/UX.

## 2025-12-15 – Loop 385 (kind: guardrail/tests)
- Focus: Ensure cancel paths also clear response canvas suppression.
- Adversarial priority check: Request pipeline remains highest risk; cancel paths share suppression reset code but lacked coverage. Guarding cancel→reset outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `_on_state_change` clears `GPTState.suppress_response_canvas` on CANCELLED states, preventing suppression from persisting after cancels.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_cancel_clears_response_canvas_suppression` (pass).
- Removal test: reverting would drop coverage that cancel clears suppression, allowing hidden responses if suppression stays set after cancel, weakening ADR-0054 request pipeline resilience/UX.

## 2025-12-15 – Loop 386 (kind: guardrail/tests)
- Focus: Keep suppression reset covered on cancel/error paths in request UI.
- Adversarial priority check: Request pipeline still highest risk; suppression reset is critical for visibility. Extending coverage to ensure both ERROR and CANCEL states clear suppression remains higher priority than lower-risk overlay tweaks.
- Change: Clarified duplicate guardrail for suppression reset across terminal paths; re-ran targeted test for cancel reset to ensure stability.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_cancel_clears_response_canvas_suppression` (pass).
- Removal test: reverting would drop the targeted guardrail run, weakening confidence that suppression reset remains enforced on cancel/error paths in the request pipeline.

## 2025-12-15 – Loop 387 (kind: guardrail/tests)
- Focus: Bus-level cancel clears suppression so next responses render.
- Adversarial priority check: Request pipeline remains highest risk; without integration coverage, a stuck `suppress_response_canvas` after bus-driven cancel could hide future responses. Guarding the bus→UI path outranks lower-risk work elsewhere.
- Change: Added an integration guardrail that sets suppression, runs a bus cancel, asserts suppression clears, and verifies the next begin/append refreshes the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_cancel_via_bus_clears_suppression_and_allows_next_append` (pass).
- Removal test: reverting would drop coverage that bus-driven cancels clear suppression and allow subsequent response refreshes, risking hidden responses and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 388 (kind: guardrail/tests)
- Focus: Error→retry clears suppression and keeps responses visible.
- Adversarial priority check: Request pipeline still highest risk; without integration coverage, a stuck `suppress_response_canvas` after an error→retry could hide subsequent responses. Guarding the bus/UI error→retry path outranks lower-risk work elsewhere.
- Change: Added a guardrail that seeds suppression, emits an error on a request, asserts suppression clears, then retries and appends to verify response canvas open/refresh still occur.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_error_then_retry_keeps_response_canvas_visible` (pass).
- Removal test: reverting would drop coverage that error→retry clears suppression and refreshes responses, risking hidden responses and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 389 (kind: guardrail/tests)
- Focus: Error→new request clears suppression so future responses render.
- Adversarial priority check: Request pipeline remains highest risk; without coverage, a stuck `suppress_response_canvas` after an error could hide subsequent requests. Guarding the error→new request path outranks lower-risk work elsewhere.
- Change: Added a guardrail that seeds suppression, emits an error, asserts suppression clears, then begins a fresh request and appends to verify the response canvas refreshes.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_error_then_new_request_clears_suppression_and_refreshes` (pass).
- Removal test: reverting would drop coverage that errors clear suppression before new requests, risking hidden responses and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 390 (kind: behaviour/guardrail)
- Focus: Clear suppression on begin_stream and guard streaming visibility.
- Adversarial priority check: Request pipeline still highest risk; without clearing suppression on BEGIN_STREAM, a prior suppression could hide streaming responses. Guarding this path outranks lower-risk tweaks elsewhere.
- Change: `_on_state_change` now resets suppression when entering STREAMING, and a guardrail asserts begin_stream clears suppression and allows subsequent appends to refresh the response canvas.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_begin_stream_clears_suppression_and_refreshes` (pass).
- Removal test: reverting would allow STREAMING to inherit suppression, risking hidden responses on streaming-only starts and dropping the guardrail, weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 391 (kind: behaviour/guardrail)
- Focus: Clear suppression on early phases (listening/transcribing/confirming) to avoid hidden responses later.
- Adversarial priority check: Request pipeline remains highest risk; suppression lingering from prior runs could persist through start_listen/confirm flows. Guarding early-phase resets outranks lower-risk work elsewhere.
- Change: `_on_state_change` now clears throttles/suppression for LISTENING/TRANSCRIBING/CONFIRMING phases; added a guardrail asserting LISTENING clears `suppress_response_canvas`.
- Artefact deltas: `lib/requestUI.py`, `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_listening_state_clears_suppression` (pass).
- Removal test: reverting would let suppression/throttle persist into early phases with no coverage, risking hidden response canvases later and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 392 (kind: guardrail/tests)
- Focus: Confirming phase clears suppression before send.
- Adversarial priority check: Request pipeline still highest risk; confirming can precede sends, and stuck suppression could hide responses. Guarding confirming-phase reset outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `_on_state_change` clears `suppress_response_canvas` when entering CONFIRMING.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_confirming_state_clears_suppression` (pass).
- Removal test: reverting would drop coverage that confirming clears suppression, risking hidden responses for confirmed sends and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 393 (kind: guardrail/tests)
- Focus: Transcribing phase clears suppression before send.
- Adversarial priority check: Request pipeline remains highest risk; suppression must clear at every early phase. Covering transcribing matches the helper’s priority on risky, central flows.
- Change: Added a guardrail asserting `_on_state_change` clears `suppress_response_canvas` when entering TRANSCRIBING.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_transcribing_state_clears_suppression` (pass).
- Removal test: reverting would drop coverage that transcribing clears suppression, risking hidden responses in speech-driven flows and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 394 (kind: guardrail/tests)
- Focus: End-to-end listen→confirm→send clears suppression and refreshes responses.
- Adversarial priority check: Request pipeline is still highest risk; without an integration guardrail, suppression could persist through early phases and hide streaming. Guarding the full flow outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail walking LISTENING→CONFIRMING→SENDING with suppression seeded, asserting suppression clears and the subsequent append refreshes the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_listen_to_send_flow_clears_suppression_and_refreshes` (pass).
- Removal test: reverting would drop the end-to-end suppression-reset guardrail, risking hidden responses across the listen/confirm/send path and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 395 (kind: guardrail/tests)
- Focus: Bus begin_send clears suppression so responses render.
- Adversarial priority check: Request pipeline remains highest risk; bus-driven begin_send must clear suppression before streaming. Guarding this entrypoint outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail that seeds suppression, emits begin_send via the bus, asserts suppression clears, and verifies the subsequent append refreshes the response canvas.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_bus_begin_send_clears_suppression_and_refreshes` (pass).
- Removal test: reverting would drop coverage that bus begin_send clears suppression, risking hidden responses on new requests and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 396 (kind: guardrail/tests)
- Focus: Bus reset clears suppression before the next request.
- Adversarial priority check: Request pipeline remains highest risk; a bus reset that leaves suppression set would hide subsequent responses. Guarding reset outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail seeding suppression, emitting reset, asserting suppression clears, then beginning a new request and appending to verify the response canvas refreshes.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_bus_reset_clears_suppression_and_next_append_refreshes` (pass).
- Removal test: reverting would drop coverage that reset clears suppression, risking hidden responses after resets and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 397 (kind: guardrail/tests)
- Focus: DONE phase clears suppression and allows next responses to render.
- Adversarial priority check: Request pipeline remains highest risk; DONE transitions must not leave suppression set. Guarding this terminal phase outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail seeding suppression, applying a DONE state change, asserting suppression clears, then starting a new request and appending to verify the response canvas refreshes.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_done_state_clears_suppression_and_allows_refresh` (pass).
- Removal test: reverting would drop coverage that DONE clears suppression, risking hidden responses after successful requests and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 398 (kind: guardrail/tests)
- Focus: Bus COMPLETE clears suppression so next responses render.
- Adversarial priority check: Request pipeline remains highest risk; bus-driven COMPLETE must clear suppression or later responses could be hidden. Guarding this integration outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail seeding suppression, emitting begin_send + complete via the bus, asserting suppression clears, then starting a new request and appending to verify the response canvas refreshes.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_bus_complete_clears_suppression_and_allows_refresh` (pass).
- Removal test: reverting would drop coverage that bus COMPLETE clears suppression, risking hidden responses after successful completions and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 399 (kind: guardrail/tests)
- Focus: Bus reset clears `last_request_id` so IDs don’t leak across requests.
- Adversarial priority check: Request pipeline remains highest risk; stale `last_request_id` after reset could mis-associate telemetry/UX. Guarding the reset path outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_reset` clears `GPTState.last_request_id` after a prior begin_send.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_reset_clears_last_request_id` (pass).
- Removal test: reverting would drop coverage for clearing `last_request_id` on reset, risking leaked request IDs across requests and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 400 (kind: guardrail/tests)
- Focus: Bus begin_stream sets last_request_id for downstream consumers.
- Adversarial priority check: Request pipeline still highest risk; begin_stream must propagate request ids for telemetry/UI coherence. Guarding id propagation outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_begin_stream` seeds `GPTState.last_request_id` with the generated request id.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_begin_stream_sets_last_request_id` (pass).
- Removal test: reverting would drop coverage for id propagation on begin_stream, risking stale/blank ids in downstream consumers and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 401 (kind: guardrail/tests)
- Focus: Bus begin_send propagates explicit request ids to `last_request_id`.
- Adversarial priority check: Request pipeline remains highest risk; explicit begin_send ids must be recorded for telemetry/UI consumers. Guarding this propagation outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_begin_send` with an explicit id sets `GPTState.last_request_id`.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_begin_send_with_explicit_id_sets_last_request_id` (pass).
- Removal test: reverting would drop coverage for explicit-id propagation on begin_send, risking stale/blank ids in downstream consumers and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 402 (kind: guardrail/tests)
- Focus: Default UI registration clears suppression flag.
- Adversarial priority check: Request pipeline remains highest risk; if `register_default_request_ui` leaves suppression set, future responses could stay hidden. Guarding the reset at registration outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `register_default_request_ui` clears `GPTState.suppress_response_canvas` when seeded true.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_register_default_clears_suppression_flag` (pass).
- Removal test: reverting would drop coverage that registration clears suppression, risking hidden responses after controller re-registration and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 403 (kind: guardrail/tests)
- Focus: Bus COMPLETE with explicit id sets `last_request_id`.
- Adversarial priority check: Request pipeline remains highest risk; losing ids on COMPLETE would break telemetry/UX coherence. Guarding id propagation on COMPLETE outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_complete(request_id=rid)` sets `GPTState.last_request_id` and drives state to DONE.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_complete_sets_last_request_id_with_explicit_id` (pass).
- Removal test: reverting would drop coverage that COMPLETE propagates ids/state, risking stale/blank ids in downstream consumers and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 404 (kind: guardrail/tests)
- Focus: IDLE state clears suppression and allows next responses to render.
- Adversarial priority check: Request pipeline remains highest risk; IDLE transitions are common and must not leave suppression set. Guarding this terminal-to-reset phase outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail seeding suppression, applying an IDLE state change, asserting suppression clears, then starting a new request and appending to verify the response canvas refreshes.
- Artefact delta: `_tests/test_request_ui.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_ui.py::RequestUITests::test_idle_state_clears_suppression_and_allows_refresh` (pass).
- Removal test: reverting would drop coverage that IDLE clears suppression, risking hidden responses after reset/idle transitions and weakening ADR-0054 request pipeline resilience.

## 2025-12-15 – Loop 405 (kind: guardrail/tests)
- Focus: Bus cancel preserves last_request_id for downstream consumers.
- Adversarial priority check: Request pipeline remains highest risk; losing the request id on cancel would confuse telemetry/UX. Guarding id persistence on cancel outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_cancel(request_id=rid)` keeps `GPTState.last_request_id` set to the cancelled request id.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_cancel_preserves_last_request_id` (pass).
- Removal test: reverting would drop coverage that cancel preserves the request id, risking blank/stale ids in downstream consumers and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 406 (kind: guardrail/tests)
- Focus: Bus FAIL sets last_request_id to the failing request.
- Adversarial priority check: Request pipeline remains highest risk; losing ids on FAIL would break telemetry/UX coherence. Guarding id propagation on FAIL outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_fail(request_id=rid)` sets `GPTState.last_request_id` and leaves state in ERROR.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_fail_sets_last_request_id` (pass).
- Removal test: reverting would drop coverage that FAIL propagates ids/state, risking stale/blank ids in downstream consumers and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 407 (kind: behaviour/guardrail)
- Focus: Bus history_saved propagates last_request_id for telemetry/UX coherence.
- Adversarial priority check: Request pipeline remains highest risk; history_saved was not updating `last_request_id`, risking stale ids. Guarding id propagation here outranks lower-risk tweaks elsewhere.
- Change: `emit_history_saved` now records `last_request_id` for the saved request id; updated guardrails to assert controller hook calls and last_request_id updates for explicit/default ids.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_history_saved_calls_controller_hook _tests/test_request_bus.py::RequestBusTests::test_emit_history_saved_defaults_request_id` (pass).
- Removal test: reverting would drop id propagation on history saves and its guardrails, risking stale/blank ids for downstream consumers and weakening ADR-0054 request pipeline correctness/telemetry.

## 2025-12-15 – Loop 408 (kind: guardrail/tests)
- Focus: Bus begin_stream with explicit id sets `last_request_id`.
- Adversarial priority check: Request pipeline remains highest risk; explicit begin_stream ids must propagate for telemetry/UI coherence. Guarding this path outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_begin_stream(request_id=rid)` sets `GPTState.last_request_id` to the explicit id.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_begin_stream_with_explicit_id_sets_last_request_id` (pass).
- Removal test: reverting would drop coverage for explicit-id propagation on begin_stream, risking stale/blank ids downstream and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 409 (kind: behaviour/guardrail)
- Focus: Ensure history_saved events always propagate request ids (generate when missing).
- Adversarial priority check: Request pipeline remains highest risk; history_saved without a request id left `last_request_id` blank, breaking telemetry/UX coherence. Guarding id generation/propagation here outranks lower-risk tweaks elsewhere.
- Change: `emit_history_saved` now generates a request id when none is present, sets `last_request_id`, and guardrails assert controller hooks receive the id and `last_request_id` is updated for both explicit and generated paths.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_history_saved_calls_controller_hook _tests/test_request_bus.py::RequestBusTests::test_emit_history_saved_defaults_request_id _tests/test_request_bus.py::RequestBusTests::test_emit_history_saved_generates_request_id_when_missing` (pass).
- Removal test: reverting would drop id generation/propagation on history saves and its guardrails, risking blank/stale ids in downstream consumers and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 410 (kind: behaviour/guardrail)
- Focus: Do not clear last_request_id on fail/cancel when request id missing.
- Adversarial priority check: Request pipeline remains highest risk; fail/cancel without request ids were clearing `last_request_id`, risking blank telemetry/UX. Guarding this propagation outranks lower-risk tweaks elsewhere.
- Change: Fail/cancel/complete now only update `last_request_id` when an id is present (no longer clear on None). Added guardrails ensuring fail/cancel without ids preserve the prior id while still setting it when provided.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_fail_without_id_preserves_last_request_id _tests/test_request_bus.py::RequestBusTests::test_emit_cancel_without_id_preserves_last_request_id` (pass).
- Removal test: reverting would reintroduce last_request_id clearing on fail/cancel without ids and drop guardrails, risking blank/stale ids in downstream consumers and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 411 (kind: guardrail/tests)
- Focus: Bus COMPLETE without id preserves last_request_id.
- Adversarial priority check: Request pipeline remains highest risk; COMPLETE events without ids could clear `last_request_id`. Guarding this propagation outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_complete()` without an id preserves the prior `last_request_id`.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_complete_without_id_preserves_last_request_id` (pass).
- Removal test: reverting would drop coverage that COMPLETE without ids preserves last_request_id, risking blank/stale ids and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 412 (kind: guardrail/tests)
- Focus: History saves generate/request ids even without a controller.
- Adversarial priority check: Request pipeline remains highest risk; history_saved with no active controller/request would leave `last_request_id` blank. Guarding id generation in this edge path outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_history_saved` generates and records a request id when no controller/request is present.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_history_saved_without_controller_generates_request_id` (pass).
- Removal test: reverting would drop coverage that history saves generate ids in controller-less contexts, risking blank ids and weakening ADR-0054 request pipeline correctness/telemetry.

## 2025-12-15 – Loop 414 (kind: guardrail/tests)
- Focus: History saves with explicit ids set last_request_id even without a controller.
- Adversarial priority check: Request pipeline remains highest risk; history_saved with explicit ids must be recorded even if the controller is absent. Guarding this edge path outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_history_saved(request_id=rid)` sets `last_request_id` to the explicit id when no controller is registered.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_history_saved_with_explicit_id_without_controller_sets_last_request_id` (pass).
- Removal test: reverting would drop coverage that explicit history saves record ids when the controller is missing, risking blank/stale ids and weakening ADR-0054 request pipeline correctness/telemetry.

## 2025-12-15 – Loop 415 (kind: guardrail/tests)
- Focus: Reset clears last_request_id even when no controller is registered.
- Adversarial priority check: Request pipeline remains highest risk; stale ids after reset with no controller would confuse downstream consumers. Guarding this edge reset path outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_reset` clears `last_request_id` when no controller is set.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_reset_clears_last_request_id_without_controller` (pass).
- Removal test: reverting would drop coverage that reset clears ids in controller-less contexts, risking stale ids and weakening ADR-0054 request pipeline correctness/telemetry.

## 2025-12-15 – Loop 416 (kind: guardrail/tests)
- Focus: begin_send sets last_request_id even when no controller is registered.
- Adversarial priority check: Request pipeline remains highest risk; begin_send without a controller must still record request ids for telemetry/UX. Guarding this edge path outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_begin_send` generates an id and sets `last_request_id` when no controller is registered.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_begin_send_without_controller_sets_last_request_id` (pass).
- Removal test: reverting would drop coverage that begin_send records ids without a controller, risking blank/stale ids and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 417 (kind: guardrail/tests)
- Focus: begin_stream sets last_request_id even when no controller is registered.
- Adversarial priority check: Request pipeline remains highest risk; begin_stream without a controller must still record request ids for telemetry/UX. Guarding this edge path outranks lower-risk tweaks elsewhere.
- Change: Added a guardrail asserting `emit_begin_stream` generates an id and sets `last_request_id` when no controller is registered.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_begin_stream_without_controller_sets_last_request_id` (pass).
- Removal test: reverting would drop coverage that begin_stream records ids without a controller, risking blank/stale ids and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 418 (kind: behaviour/guardrail)
- Focus: Generate request ids for complete/fail/cancel when none exists, even without a controller.
- Adversarial priority check: Request pipeline remains highest risk; complete/fail/cancel without ids (and without a controller/request) left `last_request_id` blank, breaking telemetry/UX coherence. Guarding id generation here outranks lower-risk tweaks elsewhere.
- Change: `emit_complete`/`emit_fail`/`emit_cancel` now generate a request id when none is present and always set `last_request_id`; added guardrails asserting these events generate/record ids when no controller is registered.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_complete_without_id_generates_request_id_without_controller _tests/test_request_bus.py::RequestBusTests::test_emit_fail_without_id_generates_request_id_without_controller _tests/test_request_bus.py::RequestBusTests::test_emit_cancel_without_id_generates_request_id_without_controller` (pass).
- Removal test: reverting would drop id generation/propagation for complete/fail/cancel in controller-less contexts and drop guardrails, risking blank/stale ids in downstream consumers and weakening ADR-0054 request pipeline correctness/telemetry.

## 2025-12-15 – Loop 419 (kind: behaviour/guardrail)
- Focus: Append events generate/propagate request ids when missing.
- Adversarial priority check: Request pipeline remains highest risk; append without request ids left `last_request_id` blank and sent id-less events. Aligning append with other bus events outranks lower-risk tweaks elsewhere.
- Change: `emit_append` now generates a request id when missing and always updates `last_request_id`; guardrails updated to assert append without ids generates/records ids and explicit ids still set `last_request_id`.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_append_without_id_generates_request_id_and_updates_last_request_id _tests/test_request_bus.py::RequestBusTests::test_emit_append_defaults_request_id` (pass).
- Removal test: reverting would drop id generation/propagation on append and its guardrails, risking blank/stale ids in downstream consumers and weakening ADR-0054 request pipeline correctness/telemetry.

## 2025-12-15 – Loop 420 (kind: status/blocker)
- Focus: Adversarial review for remaining high-priority slices.
- Adversarial priority check: Request pipeline id/suppression guardrails now cover begin_send/stream, retry, complete/fail/cancel/history_saved/append (explicit/missing ids, with/without controller), and UI suppression across all phases. No higher-risk, non-duplicative slice remains that would change behaviour/tests without contriving scenarios already guarded.
- Change: No new code/tests/docs; recorded that no substantial in-repo slice remains for ADR-0054 this loop after adversarial scan of request bus/UI surfaces.
- Artefacts inspected: `lib/requestBus.py`, `_tests/test_request_bus.py`, `lib/requestUI.py` (re-read for remaining unguarded paths).
- Checks: Not run (no behavioural changes).
- Removal test: reverting this entry would remove the documented adversarial review/outcome, but since no code/tests changed, behaviour would be unchanged; future loops should pick a new ADR or await a new high-risk gap.

## 2025-12-15 – Loop 421 (kind: behaviour/guardrail)
- Focus: Ensure bus handles events without a controller while keeping request ids.
- Adversarial priority check: Request pipeline correctness remains highest risk; without a controller, bus events returned empty states and could drop request ids, breaking telemetry/UX. Guarding this edge path outranks lower-risk tweaks elsewhere.
- Change: `_handle` now returns a state that carries the event’s request id when no controller is registered, and `emit_append` generates a request id when missing. Added guardrail asserting history_saved without a controller returns a state with a generated request id and updates `last_request_id`.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_handle_without_controller_returns_state_with_request_id` (pass).
- Removal test: reverting would drop id propagation for controller-less handling and append generation, risking blank request ids in edge contexts and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 422 (kind: behaviour/guardrail)
- Focus: Append events without a controller generate and return request ids.
- Adversarial priority check: Request pipeline remains highest risk; append without a controller could return id-less states and leave `last_request_id` blank. Guarding this edge path outranks lower-risk tweaks elsewhere.
- Change: Added guardrail that append with no controller generates a request id, returns it in state, and records it as `last_request_id`.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_append_without_controller_generates_request_id_and_returns_state` (pass).
- Removal test: reverting would drop coverage for controller-less append id generation, risking blank/stale ids in downstream consumers and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 423 (kind: behaviour/guardrail)
- Focus: Maintain request-state transitions and ids when no controller is registered.
- Adversarial priority check: Request pipeline remains highest risk; without a controller, bus state stayed idle and dropped ids, breaking telemetry/UX. Guarding default-state transitions/ids outranks lower-risk tweaks elsewhere.
- Change: `_handle` now updates a retained `_last_state` via `transition` when no controller is set, so begin_send moves to SENDING and subsequent events retain ids; guardrails assert controller-less begin_send/append/history_saved return states with ids and keep `last_request_id` aligned.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_handle_without_controller_returns_state_with_request_id _tests/test_request_bus.py::RequestBusTests::test_emit_append_without_controller_generates_request_id_and_returns_state _tests/test_request_bus.py::RequestBusTests::test_begin_send_advances_state_without_controller` (pass).
- Removal test: reverting would drop controller-less state transitions/id retention, risking idle/stale state and blank request ids in edge contexts, weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 424 (kind: behaviour/guardrail)
- Focus: Controller-less complete/fail/cancel advance state and keep request ids.
- Adversarial priority check: Request pipeline remains highest risk; terminal transitions without a controller could leave state idle and ids blank. Guarding these paths outranks lower-risk tweaks elsewhere.
- Change: Added guardrail asserting controller-less complete/fail/cancel transitions advance to DONE/ERROR/CANCELLED, retain last_error, and keep `last_request_id` from the originating request.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_complete_fail_cancel_transition_without_controller` (pass).
- Removal test: reverting would drop coverage for controller-less terminal transitions, risking idle/stale state and blank request ids in edge contexts and weakening ADR-0054 request pipeline correctness.

## 2025-12-15 – Loop 425 (kind: behaviour/guardrail)
- Focus: Lifecycle status advances without a controller and retains request ids.
- Adversarial priority check: Request pipeline remains highest risk; lifecycle_status_for must stay coherent when no controller is registered. Guarding lifecycle progression without a controller outranks lower-risk tweaks elsewhere.
- Change: Added guardrail asserting controller-less lifecycle progression: begin_send→running, begin_stream→streaming, complete→completed, fail→errored, cancel→cancelled while keeping last_request_id.
- Artefact delta: `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_lifecycle_state_advances_without_controller` (pass).
- Removal test: reverting would drop coverage for lifecycle progression without a controller, risking stale/idle lifecycle states and weakening ADR-0054 request pipeline correctness/telemetry.

## 2025-12-15 – Loop 426 (kind: behaviour/guardrail)
- Focus: Reset bus-retained state when detaching controllers.
- Adversarial priority check: Request pipeline remains highest risk; detaching the controller could leave stale request state/ids in the bus. Guarding this reset outranks lower-risk tweaks elsewhere.
- Change: `set_controller(None)` now resets the retained bus state; added guardrail asserting controller-less state resets to IDLE/empty after detaching.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_set_controller_none_resets_retained_state` (pass).
- Removal test: reverting would allow stale request state/ids to persist after controller detachment and drop the guardrail, weakening ADR-0054 request pipeline correctness in controller-less transitions.

## 2025-12-15 – Loop 427 (kind: status/adversarial)
- Focus: Adversarial completion check and acceptance.
- Adversarial priority check: Scanned ADR objectives (axis SSOT, overlay canvases, request pipeline). Plausible high-risk slices reviewed: axis regen/README/static prompt drift (guarded by regen/README tests), overlay scroll/block/close consistency (shared helpers + parity tests), request pipeline suppression/id propagation across all events with/without controllers (extensive guardrails). No unguarded, non-duplicative in-repo slices remain.
- Change: Marked ADR status Accepted in `docs/adr/0054-concordance-axis-canvas-request-code-quality.md`.
- Artefacts inspected: `docs/adr/0054-concordance-axis-canvas-request-code-quality.md`, `docs/adr/0054-concordance-axis-canvas-request-code-quality.work-log.md`, `lib/requestBus.py`, `_tests/test_request_bus.py`, `lib/requestUI.py` (re-read for gaps).
- Checks: Not run (status change only; adversarial review).
- Removal test: reverting would drop the recorded acceptance and adversarial completion rationale; behaviour remains unchanged.
## 2025-12-15 – Loop 413 (kind: behaviour/guardrail)
- Focus: Append events propagate request ids correctly without clearing them.
- Adversarial priority check: Request pipeline remains highest risk; append without request ids was clearing `last_request_id`, risking blank telemetry/UX. Guarding append propagation outranks lower-risk tweaks elsewhere.
- Change: `emit_append` now only updates `last_request_id` when an id is present (no clearing on None). Added guardrails ensuring append without an id preserves the prior id and append with an explicit id updates it.
- Artefact deltas: `lib/requestBus.py`, `_tests/test_request_bus.py`.
- Checks (this loop): `python3 -m pytest _tests/test_request_bus.py::RequestBusTests::test_emit_append_without_id_preserves_last_request_id _tests/test_request_bus.py::RequestBusTests::test_emit_append_with_explicit_id_sets_last_request_id` (pass).
- Removal test: reverting would reintroduce last_request_id clearing on id-less append and drop guardrails, risking blank/stale ids in downstream consumers and weakening ADR-0054 request pipeline correctness.
