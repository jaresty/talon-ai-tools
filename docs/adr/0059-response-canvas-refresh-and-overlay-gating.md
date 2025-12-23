# 0059 – Response canvas refresh and overlay gating cleanup

## Status
Accepted

## Context
- Telemetry exports from `model run …` streaming sessions show repeated `in_flight` drops attributed to GUI surfaces (`modelHelpCanvas`, `modelPatternGUI`, `modelPromptPatternGUI`, `modelSuggestionGUI`) even when those canvases were never opened. The drops are emitted via `close_common_overlays` inside `model_response_canvas_open/refresh`, which call each GUI closer while a request is still in flight (`lib/modelResponseCanvas.py:1917`, `lib/overlayLifecycle.py:39`). Every closer calls `_reject_if_request_in_flight()` → `try_begin_request`, inflating gating stats and reintroducing history noise that ADR-0058 tried to eliminate.
- The response canvas refresh helper hides and reopens the window after each stream completes (`model_response_canvas_refresh`), which looks like a close/reopen cycle. The hide/show sequence also resets scroll state to the top, so users reading a long answer lose their position.
- Suggestion telemetry confirmed the same behaviour: the response canvas opens for streaming progress, closes when the refresh runs, then reopens immediately—even when the window was previously hidden on purpose. This contradicts Prompts UX ADRs that expect manual closes to be respected.

## Decision
- **Bypass gating checks for automatic overlay closes**: change the helper-level `_reject_if_request_in_flight()` guards used by overlay closers so passive closes never call `try_begin_request`. Only user-driven overlay opens/closes should surface gating drops.
- **Respect manual response-canvas state**: track whether the canvas was showing before the final refresh. If the user hid the window (or the destination is Silent/Suggest), skip reopening on completion.
- **Avoid disruptive refreshes**: skip the hide/show cycle when the canvas is already visible so the view stays put and the user’s scroll position is preserved.
- **Treat the refresh helper as idempotent**: only run the expensive overlay/refresh logic when the canvas actually needs a redraw, keeping telemetry quiet for non-canvas destinations.

## Rationale
- Eliminating synthetic gating drops keeps telemetry actionable and honours ADR-0056/0058 guardrails about accurate in-flight reporting.
- Stabilising the response canvas aligns with ADR-023/031 expectations that users can read long responses without unexpected jumps or pop-under behaviour.
- Respecting the current visibility state avoids surprising UI toggles and keeps Silent/Suggest destinations unobtrusive.

## Implementation Plan
1. Update `overlayLifecycle.close_common_overlays` (or each GUI closer) to short-circuit when invoked during an in-flight request and the intent is a passive close. Maintain existing safeguards for direct user actions.
2. Extend `model_response_canvas_open/refresh` to detect manual hides (`ResponseCanvasState.showing`, `GPTState.response_canvas_showing`) and skip reopening the window when it was closed, or when the destination kind signals Silent/Suggest.
3. Adjust `model_response_canvas_refresh` to no-op when the canvas is already visible (or redraw without hide/show) so the viewport and scroll position remain stable.
4. Gate `_refresh_response_canvas()` in `modelHelpers.send_request` behind a new `should_refresh_canvas` flag (`False` for suggest/silent/manual-hide scenarios).
5. Add regression tests covering: (a) no gating drops recorded when `close_common_overlays` runs during streaming; (b) refresh preserves scroll; (c) manual hide stays hidden after completion.

## Definition of Done
- New behaviour documented in the response-canvas tests (`_tests/test_model_response_canvas.py`, `_tests/test_model_helpers_response_canvas.py`).
- Gating telemetry exports after streaming runs show zero synthetic GUI drops when no overlays were opened.
- Manual close followed by streaming completion leaves the canvas hidden.
- `python3 -m pytest` (or targeted suites) passes.

## Verification
- `python3 -m pytest _tests/test_overlay_lifecycle.py::OverlayLifecycleTests::test_common_overlay_closers_do_not_call_gating`
- `python3 -m pytest _tests/test_model_helpers_response_canvas.py`
- `python3 -m pytest _tests/test_model_response_canvas.py`

## Consequences
- Telemetry dashboards regain signal for genuine overlay conflicts or in-flight rejections.
- Users no longer experience jarring reopens or refresh-triggered scroll jumps when streaming responses finish.
- Close guards still protect against overlapping overlays but without polluting gating drops.
