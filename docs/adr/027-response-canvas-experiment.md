# 027 – Response Canvas Visibility Experiment Log

## Known facts
- Destination auto-falls back to `window` when no textarea is focused; logs show `destination_kind=window`.
- Streaming enabled; `message_content_len` and `split answer_len/meta_len` confirm non-empty answers and meta.
- Response canvas opens and meta draws, but answer body stays blank in UI.
- Response canvas draw logs show repeated reuse/open events; no chunk logs are emitted (server likely returns full JSON, not SSE).
- `text_to_confirm` is set to the final answer at completion; `model_response_canvas_refresh` runs twice via cron on completion.
- No obvious draw errors; “No element found” appears between completion and canvas reuse, possibly from a Talon element lookup.

## Open questions
1) Is `text_to_confirm`/`last_response` non-empty at draw time when the body is blank?
2) Is a late state transition (e.g. IDLE) clobbering `text_to_confirm` before draw?
3) Does `model_response_canvas_refresh` fire on the main thread, or get skipped due to cron/resource context?
4) Does the “No element found” error reset the canvas/paint state between completion and draw?

## Chosen question
Is `text_to_confirm`/`last_response` non-empty at draw time when the body is blank?

## Hypothesis
The answer text is present in state at completion, but by the time the draw handler runs, `text_to_confirm` has been cleared or the draw is occurring before refresh, so the body renders empty.

## Experiment
- Add a single debug log inside the draw handler that records:
  - `len(text_to_confirm)`, `len(last_response)`, `phase`, `prefer_progress`, `inflight`.
  - A short preview (`[:80]`) of `text_to_confirm` when non-empty.
- Trigger a run with the destination auto-falling back to `window`.
- Collect the draw log line immediately after completion. If lengths are >0 and preview shows content, the draw path has data and the issue is rendering; if lengths are 0, state is being cleared before draw.

## Next steps
- Implement the draw log (if not already present) and capture a failing run’s log.
- Depending on the outcome:
  - If lengths > 0: investigate paint/draw flow or rect visibility.
  - If lengths == 0: trace where `text_to_confirm`/`last_response` are cleared between completion and draw.

## Results – 2025-12-07 21:03–21:09 runs
- Completions show non-empty answers/meta (answer_len ~2–3k, meta_len ~700–900).
- Canvas opens; meta draws; answer body still blank.
- No “response canvas body lengths …” logs appeared after completion, implying the draw handler is not running post-refresh (or the `_debug` path is suppressed).
- Refresh is scheduled via cron; “response canvas open skipped (no response available)” occurs at request start, then canvas opens, but the final redraw still fails to show the body.

### Interpretation
- The draw handler likely isn’t firing after the completion refresh; state has data, but no draw event renders it.

## New question
Is the draw handler being invoked after completion/refresh when using the response canvas for progress?

### Hypothesis
The canvas stays visible but never receives a draw event after we refresh, so the body remains blank despite populated state.

### Next experiment
- Force a hide/show cycle on refresh (set `ResponseCanvasState.showing = False` before show) to guarantee a draw event.
- Add a minimal “draw invoked” log (once per draw) to confirm draw execution post-completion.
- Rerun the no-textarea request; if draw logs appear and lengths are >0, focus on rendering/visibility; if no draw logs, fix the refresh/draw triggering.
