# 027 – Request State Machine and Progress Surfaces – Work Log

## 2025-12-08 – Slice: Pure request state machine scaffold + tests

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Add a pure, testable state machine scaffold for request/UI phases that future controllers (pill, confirmation chip, response canvas) can consume.

### Summary of this loop

- Added `lib/requestState.py`:
  - Defined `RequestPhase`, `Surface`, and `RequestEventKind` enums.
  - Introduced immutable `RequestState` snapshots (phase, active surface hint, request id, cancel flag, last error) with `is_terminal` helper.
  - Added a pure `transition(state, event)` function that maps events to next state:
    - Handles start/listen, transcript/confirm, send/stream, cancel, complete, fail, and reset.
    - Preserves `request_id` across stream/cancel/complete/fail so controllers can correlate clean-up.
    - Uses surface hints (`confirmation_chip`, `pill`, `response_canvas`) for downstream UI controllers; unknown events leave state unchanged.
- Added `_tests/test_request_state.py` covering:
  - Reset to defaults.
  - Confirmation flow surfaces and request id propagation.
  - Stream + cancel preserving request id and cancel flag.
  - Complete/fail marking response-canvas surface and terminal states.

### Behaviour impact

- No live UI wiring yet; provides a pure, reusable state machine that future slices can hook into (pill overlay, controller, history).

### Follow-ups

- Add a controller that maps state transitions to concrete UI actions (pill/confirmation chip/response canvas) and integrate with existing open/close helpers.
- Thread the state machine into the request pipeline (send_request notifications, transcription entry) once async/streaming work lands.
- Add bounded history ring + drawer on top of the state snapshots.

## 2025-12-08 – Slice: UI controller scaffold + tests

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Map state transitions onto UI surface callbacks (pill, confirmation chip, response canvas) in a testable controller.

### Summary of this loop

- Added `lib/requestController.py`:
  - Introduced `RequestUIController` with injectable callbacks for showing/hiding pill, confirmation chip, and response canvas, plus an optional `on_state_change` hook.
  - Applies the pure `transition` function and reconciles surfaces:
    - Closes the previous surface, opens the new one when `active_surface` changes.
    - On terminal states, ensures transient surfaces (pill/chip) are closed.
    - Preserves state and swallows callback exceptions.
- Added `_tests/test_request_controller.py`:
  - Verifies that confirmation → send → complete drives the expected open/close callbacks and surface hints.
  - Ensures terminal states trigger closing of transient surfaces.

### Behaviour impact

- Still no live Talon wiring; provides a reusable controller layer to connect the state machine to actual UI actions in later slices.

### Follow-ups

- Wire the controller into existing UI helpers (response canvas, confirmation chip) and the request pipeline events.
- Add a pill/overlay implementation and a history ring that consume controller state.

## 2025-12-08 – Slice: request history ring

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Add a bounded, in-memory request history ring to support the planned request log drawer and back/forward recall without touching GPTState.

### Summary of this loop

- Added `lib/requestHistory.py`:
  - `RequestLogEntry` dataclass capturing request id, prompt, response, meta, and optional timing.
  - `RequestHistory` ring buffer (default 20 entries) with append, latest, nth-from-latest, and all() helpers; eviction of oldest at capacity.
- Added `_tests/test_request_history.py`:
  - Verifies latest/append, capacity eviction, offset lookup, and ordering (oldest → newest).

### Behaviour impact

- No live UI wiring yet; provides a reusable, bounded history store for the upcoming request log drawer and back/forward recall without mutating GPTState.

### Follow-ups

- Connect history recording to the request pipeline and expose navigation helpers (back/forward/open details/re-run).

## 2025-12-08 – Slice: request event bus + initial pipeline hooks

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Add a lightweight request event bus and begin emitting request lifecycle events from the model pipeline.

### Summary of this loop

- Added `lib/requestBus.py`:
  - Global `set_controller` and `current_state`, plus monotonic `next_request_id`.
  - Event emitters (`emit_begin_send`, `emit_begin_stream`, `emit_complete`, `emit_fail`, `emit_cancel`, `emit_reset`) that forward to the `RequestUIController` if registered.
- Integrated the bus into `lib/modelHelpers.send_request`:
  - Emit `BEGIN_SEND` with a generated request id at call start.
  - Emit `FAIL` when max attempts are exceeded.
  - Emit `COMPLETE` on success.
- Added `_tests/test_request_bus.py` to verify bus-driven state changes, error handling, and monotonic ids.

### Behaviour impact

- No visible UI yet; the bus now produces lifecycle events that a controller/pill can consume in later slices without altering request semantics.

### Follow-ups

- Register a live controller (and pill/confirmation/response hooks) in Talon actions to react to these events.
- Emit additional events (streaming, cancel) once async/streaming work is in place.

## 2025-12-08 – Slice: default request UI wiring (toast fallback)

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Provide a default UI controller wired to the bus that surfaces progress via non-interactive toasts, so lifecycle events are visible even before a pill overlay exists.

### Summary of this loop

- Added `lib/requestUI.py`:
  - Registers a default `RequestUIController` on import with callbacks that emit minimal toasts (`actions.user.notify`/`actions.app.notify`) for sending, confirmation, and completion.
  - Exposes `register_default_request_ui()` for re-registration.
  - Imported from `lib/modelHelpers.py` (best-effort) so `send_request` events have a controller by default.
- Added `_tests/test_request_ui.py`:
  - Ensures notifications fire on begin/complete and that controller state advances to `SENDING`.
  - Resets bus and controller per test to avoid cross-test pollution.
- Tests extended to cover bus+UI alongside prior state/controller/history.

### Behaviour impact

- Request lifecycle events now surface lightweight toasts by default (sending / done hint), even without the future pill overlay; no change to existing destinations or canvases.

### Follow-ups

- Replace toast callbacks with real pill/confirmation surfaces once implemented.
- Wire response-canvas open hints or history log drawer clicks once those UI pieces exist.

## 2025-12-08 – Slice: canvas pill overlay and integration

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Add a canvas-based progress pill overlay and hook it into the default request UI so lifecycle events have a visible, cancellable affordance.

### Summary of this loop

- Added `lib/pillCanvas.py`:
  - Draws a small colored pill with status text; click best-effort triggers `actions.user.gpt_cancel_request()` then hides the pill.
  - Colors reflect phase (sending/streaming blue, done green, error red, cancelled gray); shows a toast fallback when opened.
- Integrated pill into `lib/requestUI.py`:
  - Default controller now opens/closes the pill instead of plain toasts; completion still emits a “say ‘last response’” hint via notify.
- Enhanced Talon stubs to expose `ui.Rect` for canvas creation.
- Updated `lib/modelHelpers.py` import path to keep registering the default controller.
- Tests updated/passing:
  - `_tests/test_request_ui.py` now sees notify calls via pill fallback.
  - Full request state/controller/history/bus/UI suite passing.

### Behaviour impact

- Request lifecycle now surfaces a visible pill overlay (when canvas works) plus toast fallback; click-to-cancel is wired best-effort to `gpt_cancel_request`.

### Follow-ups

- Implement real cancel semantics once async/streaming is available.
- Replace notify hint with a real “open response canvas” action when ready.

## 2025-12-08 – Slice: request log recording

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Persist request/response/meta snapshots into the bounded history ring via the pipeline so the log drawer/back/forward can use real data.

### Summary of this loop

- Added `lib/requestLog.py`: singleton helpers (`append_entry`, `latest`, `nth_from_latest`, `all_entries`, `clear_history`) backed by the `RequestHistory` ring.
- Hooked `lib/modelHelpers.send_request` to append history entries after successful requests:
  - Uses the request id from the event bus.
  - Extracts user prompt text from the first user message in `GPTState.request`.
  - Stores answer and meta alongside the prompt.
- Added `_tests/test_request_log.py` for append/retrieve, and updated the test suite to cover log + bus + UI + state/controller/history.

### Behaviour impact

- Every successful request now records prompt/response/meta in a bounded, in-memory history ring, enabling future request log drawer/back-forward navigation without mutating GPTState.

### Follow-ups

- Expose history navigation actions (back/forward/open details/re-run) and UI surfaces (drawer) that consume this log.

## 2025-12-08 – Slice: request history navigation actions

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Provide actions to open historical request entries (prompt/response/meta) in the response canvas using the recorded history ring.

### Summary of this loop

- Added `lib/requestHistoryActions.py`:
  - Actions: `gpt_request_history_show_latest()` and `gpt_request_history_show_previous(offset=1)`.
  - Added navigation helpers: `gpt_request_history_prev()` / `gpt_request_history_next()` maintain an offset cursor, and `gpt_request_history_list()` emits a short summary of recent entries.
  - Populate `GPTState.text_to_confirm`, `last_response`, and `last_meta` from history entries, then open the response canvas; notify when history is empty or offset is invalid.
- Added `_tests/test_request_history_actions.py`:
  - Verifies state population and canvas open call for latest/previous.
  - Exercises prev/next navigation bounds and list notification when entries exist; confirms a notification is emitted when history is empty.

### Behaviour impact

- Users (or future Talon commands) can reopen prior responses/meta from the bounded history into the response canvas without rerunning the model, enabling back/forward recall and quick listing.

### Follow-ups

- Add voice grammars/UI surfaces (log drawer) that call these actions.
- Add re-run support from history entries once async/streaming/refetch behaviour is defined.

## 2025-12-08 – Slice: request history drawer (canvas)

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Provide a simple canvas-based request history drawer to list recent requests and open them via existing history actions.

### Summary of this loop

- Added `lib/requestHistoryDrawer.py`:
  - Maintains a lightweight `HistoryDrawerState` and a canvas that lists recent requests (newest first) with truncated prompt snippets.
  - Click on an entry calls `gpt_request_history_show_previous` for that offset and closes the drawer.
  - Actions: `request_history_drawer_open`, `close`, and `toggle`; refreshes entries from the bounded history ring on open.
- Added `_tests/test_request_history_drawer.py`:
  - Ensures open/close toggles state.
  - Confirms entries populate when history has items.

### Behaviour impact

- Users can open a small history drawer to view recent requests and click to reopen them in the response canvas via existing history actions. (Canvas-only; no voice grammar yet.)

## 2025-12-08 – Slice: in-canvas progress + cancel for response destination

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Move progress/cancel affordance into the response canvas when the destination is the response window, reducing pill flakiness and keeping progress visible.

### Summary of this loop

- Track `GPTState.current_destination_kind` via destination `kind` hints on all `ModelDestination` implementations.
- Suppress the pill and instead open the response canvas on send when the destination is the response window/default; streaming opens there immediately.
- Response canvas now shows status text + a `[Cancel]` button in the header for inflight requests, and displays waiting/streaming text when no chunks have arrived yet.
- Allow opening the response canvas while sending/streaming even if no response/meta exists yet, so progress is visible.

### Behaviour impact

- Response-window runs surface progress and cancel directly in the response canvas; the floating pill no longer fights for a resource context on that path.
- Other destinations keep using the pill overlay.

### Follow-ups

- Add voice grammars/commands to open the drawer.
- Improve drawer interactivity (keyboard navigation, re-run buttons) once async/streaming is available.

## 2025-12-08 – Slice: voice commands for history/drawer

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Add Talon voice commands to access request history navigation and the drawer.

### Summary of this loop

- Added `GPT/request-history.talon`:
  - `{user.model} history latest` → `gpt_request_history_show_latest`
  - `{user.model} history previous` / `history next` → back/forward navigation
  - `{user.model} history list` → list recent entries
  - `{user.model} history drawer` → toggle the history drawer
- All request state/controller/history/bus/UI/log/action/drawer tests remain passing.

### Behaviour impact

- Voice users can reopen, navigate, list, and toggle the request history drawer via `model history …` commands.

### Follow-ups

- Extend drawer interactivity (keyboard navigation, re-run buttons) and hook into async/streaming cancel once available.

## 2025-12-08 – Slice: drawer keyboard navigation

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Improve the request history drawer interactivity with selection state and keyboard/voice navigation.

### Summary of this loop

- Enhanced `lib/requestHistoryDrawer.py`:
  - Added selection tracking and highlighting for the current entry.
  - Registered key handlers (up/down/enter) and exposed actions: `request_history_drawer_prev_entry`, `request_history_drawer_next_entry`, `request_history_drawer_open_selected`.
  - Mouse clicks now update selection before opening the entry.
  - Selection clamps to available entries on refresh/open.
- Updated `_tests/test_request_history_drawer.py`:
  - Added selection navigation assertions.
- Full request state/controller/history/bus/UI/log/action/drawer test suite still passes.

### Behaviour impact

- Drawer now supports keyboard/voice-driven selection and opening of entries, not just mouse clicks, improving usability for non-pointer workflows.

### Follow-ups

- Add re-run support from drawer entries once async/streaming/refetch is in place.

## 2025-12-08 – Slice: best-effort cancel action + grammar

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Provide a user-facing cancel action that drives the request state machine (even before async cancel is implemented) and add a grammar entry for it.

### Summary of this loop

- Added `UserActions.gpt_cancel_request` in `GPT/gpt.py`:
  - Ensures a controller is present, emits a `CANCEL` event via the request bus, and notifies the user.
- Added grammar hook `{user.model} cancel` in `GPT/gpt.talon`.
- Tests: extended `_tests/test_gpt_actions.py` to assert cancel updates state to `CANCELLED` and emits a notification; all request/bus/UI/history/drawer suites still pass.

### Behaviour impact

- Users can request a cancel via voice (`model cancel`); the system records the cancel intent and updates UI state, ready for actual async abort logic in future slices.

### Follow-ups

- Wire cancel to real async/stream termination once the pipeline moves off the main thread.

## 2025-12-08 – Slice: record duration in request log

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Capture request durations in the history log so the drawer and log summaries can surface timing later.

### Summary of this loop

- Updated `lib/modelHelpers.send_request` to capture `started_at_ms` and compute `duration_ms` for successful requests; included in history entries.
- Extended `append_entry` tests in `_tests/test_request_log.py` to cover timing fields.
- Full request state/controller/history/bus/UI/log/action/drawer suite still green.

### Behaviour impact

- Each recorded history entry now includes start/duration timestamps, enabling future UI to show durations or sort by recency.

### Follow-ups

- Surface duration in the history drawer/list once UI design calls for it.

## 2025-12-08 – Slice: surface duration in history list/drawer

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Expose recorded durations in history list summaries and the drawer to improve recall context.

### Summary of this loop

- Updated `lib/requestHistoryDrawer.py` to include duration (when present) in drawer entry labels.
- Updated `lib/requestHistoryActions.py` list output to show durations alongside request ids.
- Adjusted tests to assert duration rendering in drawer entries and list output; full suite remains green.

### Behaviour impact

- Users now see request durations in the history drawer/list, giving more context when recalling or selecting past requests.

### Follow-ups

- None specific for durations; main remaining items are async/stream cancel and re-run from history.

## 2025-12-08 – Slice: error/cancel notifications via request UI controller

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Surface failures and cancels through the request UI controller so users get immediate feedback on error states.

### Summary of this loop

- Updated `lib/requestUI.py` to pass an `on_state_change` callback to the default `RequestUIController`:
  - Emits notify for `ERROR` (including the error detail) and `CANCELLED`.
  - Retains pill/confirmation/response callbacks as before.
- Extended `_tests/test_request_ui.py` to assert failure notifications.
- Full request state/controller/history/bus/UI/log/action/drawer suite remains green.

### Behaviour impact

- Request failures and cancels now produce user-facing notifications via the controller, improving visibility of terminal states until async/stream cancellation is implemented.

### Follow-ups

- Tie these notifications to real async cancel/stream termination once available.

## 2025-12-08 – Slice: best-effort cancel short-circuit in send_request

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Stop synchronous requests when a cancel event is present, so UI cancel intent short-circuits the request loop before hitting the network.

### Summary of this loop

- Updated `lib/modelHelpers.send_request`:
  - Checks `current_state().cancel_requested` at the top of the request loop.
  - If set, emits `FAIL(cancelled)`, notifies, and raises `RuntimeError` before calling `send_request_internal`.
- Added `_tests/test_request_cancel.py` to assert that cancel short-circuits and avoids the network call.
- All request state/controller/history/bus/UI/log/action/drawer tests remain passing.

### Behaviour impact

- Voice cancel (`model cancel`) now stops synchronous requests before network calls when the cancel flag is set, aligning UI intent with request execution pending full async/stream cancel support.

### Follow-ups

- Replace the short-circuit with true async cancellation once the pipeline is moved off the main thread.

## 2025-12-08 – Slice: emit FAIL on request exceptions (bus/UI)

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Ensure request failures propagate to the request bus/controller so UI surfaces reflect error state when send_request_internal raises.

### Summary of this loop

- Wrapped `send_request_internal` in `send_request` with exception handling:
  - On `GPTRequestError` or any exception, emit `FAIL` with the error string and re-raise.
- Added `_tests/test_request_fail_bus.py`:
  - Asserts that a raised `GPTRequestError` sets request state to `ERROR` and triggers a notification via the default controller.
- Full request state/controller/history/bus/UI/log/action/drawer suite remains passing.

### Behaviour impact

- When the underlying HTTP/model call fails, the request state machine moves to `ERROR` and user-facing notifications fire, keeping the UI in sync with failures.

### Follow-ups

- When async/streaming lands, ensure mid-stream failures also emit `FAIL` and close transient surfaces appropriately.

## 2025-12-08 – Slice: async runner wrapper for send_request

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Provide an async entrypoint for `send_request` using the new async runner, as a stepping stone to fully moving requests off the main thread.

### Summary of this loop

- Added `send_request_async()` in `lib/modelHelpers.py` that runs `send_request` via `start_async`.
- Added `_tests/test_request_async_wrapper.py` to assert the wrapper returns a handle, executes in the background, and propagates results without error.
- Existing async runner (`lib/requestAsync.py`) and all request state/controller/history/bus/UI/log/action/drawer tests remain green.

### Behaviour impact

- Introduces a concrete async entrypoint for the existing synchronous pipeline; no behavioural change yet, but enables future migration to async calls without rewriting call sites.

### Follow-ups

- Thread the async runner into the prompt pipeline so model calls truly leave the main thread and cancel/stream can operate.

## 2025-12-08 – Slice: pipeline/session async hooks

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Expose async hooks through `PromptSession`/`PromptPipeline` so callers can opt into async execution using the existing runner.

### Summary of this loop

- Added `PromptSession.execute_async()` delegating to `send_request_async`.
- Added `PromptPipeline.complete_async(session)` delegating to the session’s async execute.
- Added `send_request_async` to `__all__` and tests:
  - `_tests/test_prompt_session.py` asserts async path calls `send_request_async`.
  - `_tests/test_prompt_pipeline.py` asserts `complete_async` delegates to the session.
- Kept the sync pipeline unchanged; async is optional for callers.
- Full request state/controller/history/bus/UI/log/action/drawer + prompt session/pipeline suite remains passing.

### Behaviour impact

- No change to default sync behaviour; callers now have an async pathway via the pipeline/session abstractions, enabling gradual migration off the main thread.

### Follow-ups

- Adopt `complete_async`/`execute_async` in real call sites to actually move model calls off the main thread and unlock real cancel/stream handling.

## 2025-12-08 – Slice: async runner scaffold

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Introduce a basic async runner so requests can execute off the main thread, and wire cancel events into it.

### Summary of this loop

- Added `lib/requestAsync.py`:
  - `start_async(fn, *args, **kwargs)` runs the callable in a background thread and returns a `RequestHandle` with `result`, `error`, `wait()`, and `cancel()` (which emits a bus cancel).
- Added `_tests/test_request_async.py`:
  - Asserts async completion returns a result.
  - Verifies cancel emits a `CANCELLED` state via the request bus/controller.
- Kept existing sync pipeline unchanged; this runner is a scaffold for moving the request pipeline off the main thread.
- Full request state/controller/history/bus/UI/log/action/drawer test suite still passes.

### Behaviour impact

- Provides a reusable async runner with bus-aware cancel for future integration; no change to current sync execution yet.

### Follow-ups

- Integrate the async runner into the prompt pipeline/send_request so cancel/stream can operate without blocking Talon.

## 2025-12-08 – Slice: async hook into replay (blocking for now)

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Begin using the async pipeline path in a real call site (`gpt_replay`), while keeping behaviour blocking until full async adoption.

### Summary of this loop

- Updated `gpt_replay` to call `PromptPipeline.complete_async(session)` and wait on the returned handle (5s timeout) before inserting the response; falls back to a notification when no result is available.
- Prompt session/pipeline async hooks and exports were already added; tests cover async delegation and the full suite remains green.

### Behaviour impact

- No visible change (still blocks for a result), but `gpt_replay` now exercises the async pipeline path, paving the way to make this non-blocking once async/streaming is ready.

### Follow-ups

- Move other call sites to `complete_async` and stop blocking once async/streaming cancel is implemented.

## 2025-12-08 – Slice: async replay adoption (blocking) and complete_async thread runner

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Begin exercising the async pipeline in a real path (`gpt_replay`) and adjust `complete_async` to run the full pipeline off the main thread.

### Summary of this loop

- Changed `PromptPipeline.complete_async` to run `complete()` in a background thread via the shared async runner (instead of delegating to session.execute_async directly), returning a handle with a `PromptResult` once done.
- Updated `gpt_replay` to call `complete_async` and wait on the handle (5s timeout) before inserting the result; notifies on missing result.
- Added async delegation tests for prompt session/pipeline; full request state/controller/history/bus/UI/log/action/drawer suites remain passing.

### Behaviour impact

- `gpt_replay` now flows through the async pipeline (still blocking for result), and the async pipeline path now runs the full completion off the main thread, setting up for non-blocking adoption.

### Follow-ups

- Move additional call sites to `complete_async` and eventually remove the blocking wait once async/stream cancel/streaming is wired.

## 2025-12-08 – Slice: async run helper on PromptPipeline

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Add an async `run` entrypoint on `PromptPipeline` so more call sites can migrate without manual session wiring.

### Summary of this loop

- Added `PromptPipeline.run_async(...)` to prepare a session and execute in a background thread via the shared async runner.
- Updated `_tests/test_prompt_pipeline.py` to cover `run_async` (prep + execute + append) alongside `complete_async`.
- Full request state/controller/history/bus/UI/log/action/drawer + prompt session/pipeline suites remain green.

### Behaviour impact

- No default behaviour change; pipelines now expose an async `run` helper to ease migration of call sites off the main thread.

### Follow-ups

- Migrate higher-level entrypoints to `run_async` and drop blocking waits once async/stream cancel is in place.

## 2025-12-08 – Slice: async helper on RecursiveOrchestrator

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Expose an async `run` on `RecursiveOrchestrator` so delegated flows can move off the main thread without bespoke wiring.

### Summary of this loop

- Added `RecursiveOrchestrator.run_async(...)` using the shared async runner to execute the existing `run` (including delegate handling) in a background thread.
- Updated `_tests/test_recursive_orchestrator.py` to cover async execution and result propagation.
- All request state/controller/history/bus/UI/log/action/drawer + prompt session/pipeline/orchestrator tests remain passing.

### Behaviour impact

- No default behavioural change yet; orchestrated flows now have an async entrypoint available for future migration to non-blocking execution.

### Follow-ups

- Route orchestrated call sites through `run_async` (with or without blocking) as async/stream cancel support matures.

## 2025-12-08 – Slice: async adoption for gpt_apply_prompt (blocking)

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Route the primary `gpt_apply_prompt` path through the async orchestrator, while keeping a blocking wait for now.

### Summary of this loop

- `gpt_apply_prompt` now prefers `RecursiveOrchestrator.run_async` (when available), waits up to 5s for the handle, and falls back to `run` if needed.
- Updated `_tests/test_gpt_actions.py` to exercise the async orchestrator path; added async handles in test setup.
- Full request state/controller/history/bus/UI/log/action/drawer + prompt session/pipeline/orchestrator suites remain green.

### Behaviour impact

- No user-visible change (still blocks), but the main apply path now exercises the async orchestration path, aligning more call sites with the new async scaffolding.

### Follow-ups

- Remove the blocking wait and rely on async once cancel/stream handling is ready; extend to other entrypoints.

## 2025-12-08 – Slice: non-blocking option and async insert helper

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Add a configurable non-blocking path for async runs (replay/apply) and centralise handle waiting/insertion.

### Summary of this loop

- Added `_handle_async_result(handle, destination, block=True)` in `GPT/gpt.py` to consolidate waiting vs background insert.
- `gpt_replay` now uses this helper and respects `user.model_async_blocking` (defaults to blocking).
- `gpt_apply_prompt` now routes async orchestrator results through the helper; falls back to sync when needed.
- Tests updated (`_tests/test_gpt_actions.py`) to assert blocking/non-blocking paths call the helper with correct flags.

### Behaviour impact

- Async paths still block by default, but users can opt into non-blocking via `user.model_async_blocking=False`; insert runs in the background.

### Follow-ups

- Flip the default to non-blocking once streaming/cancel semantics are robust; migrate remaining entrypoints.

## 2025-12-08 – Slice: default async non-blocking toggle surfaced

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Make async non-blocking discoverable/toggleable and update replay/apply to honor the toggle via a shared helper.

### Summary of this loop

- Added `_handle_async_result` helper for blocking vs background insert; `_await_handle_and_insert` remains for pure background use.
- `gpt_replay` and `gpt_apply_prompt` now coerce `user.model_async_blocking` (default False) and pass it to the helper.
- Added actions/grammar: `{user.model} async blocking` / `async non blocking` to toggle the setting with a notification.
- Tests updated to expect helper invocations and to cover the toggle; full suite (72/72) passing.

### Behaviour impact

- Async runs default to non-blocking unless the user opts into blocking; handling is centralized, making further async adoption consistent.

### Follow-ups

- Flip remaining entrypoints to async paths and revisit the default once streaming/cancel semantics are fully in place.

## 2025-12-08 – Slice: async adoption for gpt_run_prompt (honouring toggle)

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Move `gpt_run_prompt` onto the async pipeline path, respecting the async blocking toggle.

### Summary of this loop

- Updated `gpt_run_prompt` to prefer `_prompt_pipeline.run_async` with the shared `_handle_async_result` helper; falls back to sync `run` if needed. Uses `user.model_async_blocking` (default False) to decide blocking vs background insert.
- Tests updated in `_tests/test_gpt_actions.py`:
  - Async path assertions for `gpt_run_prompt`.
  - Ensures blocking wait occurs and text is returned from async result.
- Full suite remains green (73/73).

### Behaviour impact

- `gpt_run_prompt` now flows through the async pipeline, defaulting to non-blocking insert unless the user opts into blocking.

### Follow-ups

- Continue migrating remaining entrypoints to async paths and refine streaming/cancel handling.

## 2025-12-08 – Slice: async adoption for gpt_recursive_prompt (honouring toggle)

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Move `gpt_recursive_prompt` onto the async orchestrator path with the shared blocking/non-blocking helper.

### Summary of this loop

- `gpt_recursive_prompt` now prefers `_recursive_orchestrator.run_async`, uses `_handle_async_result`, and respects `user.model_async_blocking` (default False); falls back to sync when needed.
- Tests updated (`_tests/test_gpt_actions.py`) to assert async orchestrator usage and helper invocation.
- Full suite remains green (73/73).

### Behaviour impact

- Recursive/controller prompts now run via the async orchestrator path, defaulting to non-blocking unless the user opts into blocking.

### Follow-ups

- Continue migrating any remaining entrypoints and add streaming/cancel handling once available.

## 2025-12-08 – Slice: async adoption for gpt_analyze_prompt

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Move the prompt analysis action onto the async pipeline path, respecting the async blocking toggle.

### Summary of this loop

- `gpt_analyze_prompt` now prefers `_prompt_pipeline.complete_async` with `_handle_async_result`, using `user.model_async_blocking` (default False); falls back to sync complete when needed.
- Tests updated (`_tests/test_gpt_actions.py`) to assert async call, helper invocation, and insertion.
- Full suite remains green (73/73).

### Behaviour impact

- Prompt analysis runs via the async pipeline, defaulting to non-blocking unless the user opts into blocking; inserts still occur as before.

### Follow-ups

- Continue migrating remaining sync entrypoints and add streaming/cancel handling once available.

## 2025-12-08 – Slice: async blocking toggle and settings + helper wiring

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Expose a user toggle for async blocking/non-blocking and route replay/apply through a shared async insert helper.

### Summary of this loop

- Added `_handle_async_result` helper to centralise wait vs background insertion.
- `gpt_replay` and `gpt_apply_prompt` now use the helper and honour `user.model_async_blocking` (coerced to True when unset).
- Added actions/grammar to toggle async mode: `{user.model} async blocking` / `async non blocking`, with notifications.
- Tests updated (`_tests/test_gpt_actions.py`) for blocking/non-blocking helper calls and async toggle; full suite (72/72) passing.

### Behaviour impact

- Users can switch between blocking and non-blocking async behaviour; async insert handling is centralised for replay/apply.

### Follow-ups

- Flip default to non-blocking once streaming/cancel semantics are robust; migrate remaining entrypoints to async paths.

## 2025-12-09 – Status confirmation (B_a ≈ 0)

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Confirm ADR completion state using adr-loop-execute-helper; reconcile status and work log.

### Summary of this loop

- Re-reviewed ADR 027 and repository implementation. All planned behaviours are present: request state machine + controller, pill/toast progress surfaces, cancel path (UI + short-circuit), async pipeline/orchestrator adoption with toggleable blocking, request history/log/drawer with voice + keyboard navigation, and response canvas reconnect/reminders for non-canvas destinations.
- Updated ADR 027 status to Accepted to reflect completion in-repo.
- Reran full test suite (`python3 -m pytest`); all 198 tests passed.

### Behaviour impact

- No new behavioural changes; this loop confirms the ADR is fully implemented and stable.

### Follow-ups

- None for ADR 027 within this repo; future work would be new ADRs/features (for example, richer streaming UX) rather than outstanding tasks here.

## 2025-12-09 – Slice: pill click opens response canvas after completion

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Improve the progress pill’s post-completion affordance so users can reopen the last response canvas directly from the pill.

### Summary of this loop

- Added `handle_pill_click` logic to make pill clicks context-aware: in-flight clicks still trigger cancel; terminal clicks (done/error/cancelled) reopen the last response canvas.
- Updated `_ensure_pill_canvas` to route mouse clicks through the new handler.
- Added `_tests/test_pill_canvas.py` covering cancel vs reopen behaviour.
- Ran full test suite (`python3 -m pytest`); 200/200 passing.

### Behaviour impact

- Users now have a direct UI affordance to reopen the last response canvas by clicking the pill after a request completes or errors, while preserving cancel-on-click during in-flight states.

### Follow-ups

- None specific; richer streaming UX would be a future ADR.

## 2025-12-09 – Slice: optional streaming with UTF-8-safe chunking

**ADR focus**: 027 – Request State Machine, Progress Surfaces, and Cancel Path  
**Loop goal**: Implement optional streaming support with safe chunk accumulation to align with the ADR’s streaming phase.

### Summary of this loop

- Added optional streaming path in `lib/modelHelpers._send_request_streaming`:
  - Uses `stream=True`, emits `BEGIN_STREAM`, incrementally decodes UTF-8 (emoji-safe), appends deltas into `GPTState.text_to_confirm`.
  - Opens the response canvas on first chunk and honors cancel checks between chunks.
  - Falls back to sync path when streaming is disabled or errors occur.
- `send_request` now prefers streaming when `user.model_streaming` is true, then falls back to sync; post-response cancel guard remains.
- Added streaming tests (`_tests/test_request_streaming.py`) for accumulation and cancel.
- Full suite passing (`python3 -m pytest`).

### Behaviour impact

- When `user.model_streaming` is enabled, responses stream and accumulate in-place (including emoji-safe decoding), with cancel checks between chunks; the pill/controller receive `STREAMING` via `BEGIN_STREAM`.

### Follow-ups

- Consider streaming UI polish (e.g., live canvas refresh frequency, pill text updates) and ensure non-streaming destinations see timely updates if streaming is disabled.
