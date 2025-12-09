## 2025-12-08 – Slice: throttle and simplify response canvas refreshes

**Focus**: Implement the ADR-031 refresh simplification (single open+refresh helper; throttled streaming refresh; single completion refresh).

- Simplified `_refresh_response_canvas` to a single UI-dispatched open+refresh (no multi-staggered retries).
- Streaming path now opens on the first chunk, refreshes with a 250 ms throttle, and falls back to the simplified helper for non-stream fallbacks and completion.
- Non-stream fallback paths now use the shared helper instead of manual open+refresh bursts.
- Guardrails: updated `_tests/test_model_helpers_response_canvas.py` to match the new single-dispatch behaviour; refreshed axis mapping tests still green.

Next steps:
- Consider a small throttle test harness for streaming refresh cadence if flakiness appears.
- Remove temporary axis-mapping miss logs once samples mapping stabilises.
