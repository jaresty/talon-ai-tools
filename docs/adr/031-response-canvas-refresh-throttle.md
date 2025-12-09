# 031 – Response Canvas Refresh Throttle and Simplification

- Status: Accepted  
- Date: 2025-12-08  
- Context: Response canvas redraw cadence during streaming and completion  
- Related ADRs:  
  - 022 – Canvas Quick Help GUI  
  - 023 – Canvas Response Viewer  
  - 027 – Request State Machine and Progress Surfaces  

---

## Context

We added multiple `model_response_canvas_refresh` calls (0ms/50ms stagger, per-chunk streaming refreshes, open+refresh fallbacks) while chasing a draw-timing bug. The result is over-refreshing: extra CPU, potential flicker, and redundant UI-thread work. The canvas already pulls state from `GPTState.text_to_confirm`/`last_meta`; we only need refreshes to trigger draws, not on every chunk.

Risks if we simply delete refreshes:
- First paint could be empty if `model_response_canvas_open` doesn’t trigger a draw.
- Streaming progress could look frozen without occasional refreshes.
- Non-stream fallbacks (servers ignoring `stream`) might never paint without one refresh.
- Final state could stay stale if completion lands while the canvas is showing but no refresh runs.

## Decision

Reduce refresh frequency while keeping safety:

1) **Open+single refresh helper**: `_refresh_response_canvas` is idempotent and minimal—open if needed, issue **one** refresh, no staggered retries.  
2) **Streaming throttle**: Open on the first chunk; refresh throttled at ≥250 ms instead of per-chunk; always one final refresh at completion if the canvas is showing.  
3) **Non-stream fallback**: When the server ignores streaming and we parse a full JSON once, do a single open+refresh after setting `text_to_confirm`.  
4) **Error/cancel**: Avoid extra refresh spam; rely on state clears or a single refresh only when the canvas is showing.

## Consequences

Positive:
- Lower UI-thread churn and less flicker from redundant refreshes.
- Streaming remains visibly live with throttled refreshes.
- Final answer still repaints deterministically.

Negative / mitigations:
- If `model_response_canvas_open` does not trigger an initial draw, the first frame could be blank—mitigated by the single refresh in the helper.
- Very long streams may look slightly less granular; throttle can be tuned if needed.
- Legacy workarounds for Talon draw timing are removed; if regressions reappear, we may need targeted retries instead of blanket multi-refresh bursts.***
