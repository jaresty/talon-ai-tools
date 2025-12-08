# 027 – Request State Machine, Progress Surfaces, and Cancel Path

- Status: Accepted  
- Date: 2025-12-08  
- Context: `talon-ai-tools` GPT request lifecycle and UI feedback (canvas/non-canvas destinations)  
- Related ADRs:  
  - 006 – Pattern picker and recap  
  - 019 – Meta interpretation channel and surfaces  
  - 020 – Richer meta interpretation structure  
  - 022 – Canvas quick help GUI  
  - 023 – Canvas response viewer  
  - 024 – Canvas migration for dialog GUIs  
  - 025 – Canvas dialog layout and scrolling  

## Problem

- Requests are synchronous and block Talon input. Voice is not listening while a request is in flight, so a spoken “cancel” cannot fire.  
- Progress is opaque for non-canvas destinations (direct paste/typed/clipboard). Users see only coarse notifications.  
- There is no single controller for request/UI state; each surface opens/closes itself, which risks modal clashes and makes back/cancel brittle.  
- The meta/details view is discoverable mainly via the response canvas; direct destinations give no guided way back to it.  
- Streaming is unsupported, so long responses offer no intermediate feedback.

## Decision

We will introduce a small request/UI state machine, a lightweight progress “pill” overlay, and clearer reconnection to the response canvas, in two phases:

### Phase 1: State + feedback while still synchronous

- Add a dedicated request/UI state machine (idle → listening → transcribing → confirming → sending → done/error; optional streaming once available) plus “active surface” tracking.  
- Centralise modal control: a controller maps state → surfaces to show/hide (pattern picker, confirmation chip, response canvas, pill) and closes conflicting surfaces automatically.  
- Add a compact canvas “pill” overlay near the mic area that reflects request state (Preparing/Sending/Done/Error). Click/hover closes the pill; when streaming arrives, click triggers cancel.  
- Add post-insert reminders for non-canvas destinations: a toast such as “Model done. Say ‘last response’ or click to open details,” where click opens the response canvas.  
- Add a tiny pre-flight confirmation chip after transcription (Send/Edit/Cancel with short timeout) to give users an escape while voice is still active.

### Phase 2: Async + streaming + real cancel

- Move request execution off the main Talon thread (worker thread/async + queue). Track `request_id` and `cancel_requested`.  
- Wire the pill’s click (and a keybinding) to set `cancel_requested` and terminate the in-flight request; update state machine to `cancelled`.  
- Add streaming support: push deltas into `GPTState.text_to_confirm`, refresh the response canvas, and update the pill to “Streaming…”.  
- Keep the same state machine/controller so UI logic does not splinter.

## Rationale

- A single source of truth for request/UI state prevents overlapping modals and makes cancel/back deterministic.  
- The pill gives universal progress visibility, even when the destination pastes directly or the response canvas stays closed.  
- A post-insert reminder and “View details” click keep the meta channel and response canvas discoverable without forcing UI changes on destinations.  
- Phasing lets us ship immediate UX wins (state + pill + reminders) before the heavier async/streaming refactor.

## Implementation sketch

- New module: `lib/requestState.py` (name TBD) holding the enum state, active surface, request_id, cancel flag, and a pure transition table; unit tests cover transitions (cancel/back from each state, modal stack behaviour).  
- Controller: a small helper that listens for state changes and calls existing open/close actions for pattern picker, confirmation chip, response canvas, pill.  
- Pill: a tiny canvas overlay with draw + mouse handlers; text/color by state; optional dismiss timeout on Done/Error.  
- Hook points: refactor `lib/modelHelpers.send_request` notifications to emit state events; transcription/confirmation entrypoints emit `start_listen`, `got_transcript`, `confirm_send`, etc.  
- Post-insert reminder: after direct destinations, issue a toast with a click handler to open `model_response_canvas_open()`.  
- Async/streaming: wrap `send_request` in a worker; check `cancel_requested` after each chunk; on cancel/timeout/error, raise state events that clear the pill and close transient surfaces.

### Optional extension: request log + back/forward recall

- Add a lightweight “request log drawer” (canvas or imgui) that lists recent requests with state, duration, and timestamps.  
- Provide back/forward navigation actions to reopen prior responses/meta in the response canvas (or browser) without re-running them.  
- The drawer listens to the same state events; entries link to “open details” (canvas) and “re-run” (using stored prompt/messages).

## Consequences

- Slightly higher complexity up front, but clearer, testable control over modal flows.  
- Users get immediate state feedback (pill/toasts) without changing their destination choice.  
- Future features (true cancel, streaming) slot into the same state machine without rewriting UI code.

## Implementation details and mitigations

- **Async/cancel shape**: Use a worker thread + queue to run `send_request`; marshal UI updates back to the main thread via a small dispatcher. Best-effort cancel: store `request_id` + `cancel_requested`; drop deltas after cancel, and use short per-chunk timeouts (or closing the `requests` session) to return promptly. Voice cancel only works once requests are off the main thread.  
- **Controller migration**: Wrap existing open/close helpers (response canvas, pattern pickers, quick help) behind the controller first; avoid rewriting every call site. The controller issues open/close; the helpers keep their internals.  
- **Pill/toast fallback**: Prefer a tiny canvas pill; when canvas interactivity is unreliable, fall back to a non-interactive toast text (“Model: sending… say ‘last response’ to inspect”). Clicking the pill cancels only when async is enabled; otherwise it just dismisses.  
- **Post-insert reminder**: Because `notify` isn’t clickable, use a small canvas toast for “say ‘last response’ or click to open details”; provide a non-clickable text fallback when the canvas toast isn’t available.  
- **History storage**: Keep a bounded in-memory ring (e.g., last N requests) with prompt, response, meta, timestamps, and duration. Do not persist to disk. Reopening a prior entry should not mutate `GPTState.last_*` until the user explicitly chooses to show it in the response canvas; re-run uses stored messages.  
- **Streaming shape**: When enabled, call the model with streaming and parse deltas; append to `GPTState.text_to_confirm` in the worker and send state events to refresh the response canvas. Honor `cancel_requested` between chunks. If streaming is unavailable, remain on the synchronous path.  
- **Tests**: Add unit tests for state transitions (including cancel/back), controller open/close decisions, bounded history ring + replay, and pill state mapping. Canvas/human UI can stay under pragma:no cover; logic and state should be tested via stubs.

## Current status

- Implemented: request state machine + controller, pill/toast/imgui progress surfaces, cancel intent + short-circuit (including post-response cancel check), async pipeline/orchestrator adoption with toggleable blocking, request history/log/drawer with voice + keyboard navigation, post-insert reminders for non-canvas destinations, and optional streaming (stream=True) with UTF-8 incremental decode and per-chunk append into `GPTState.text_to_confirm` plus canvas open on first chunk.
- Tests: full suite passing (`python3 -m pytest`).
