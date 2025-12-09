# 029 – Main-thread canvas control for the progress pill – Work Log

## 2025-12-08 – Slice: UI-thread dispatcher for pill canvas

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Move pill canvas show/hide/rect work onto a main-thread dispatcher so background workers no longer touch Talon canvas APIs directly, per ADR 029.

### Summary of this loop

- Added a small `_run_on_ui_thread` dispatcher in `lib/pillCanvas.py` and routed show/hide/rect application through it to keep canvas lifecycle on the main thread with retry/fallback logging.
- Adjusted `show_pill` to compute the target rect once, schedule main-thread show attempts (immediate + retry), and pass rect into `_show_canvas`; `hide_pill` now dispatches its close call similarly.
- Updated tests in `_tests/test_pill_canvas.py` to assert UI-thread dispatch is invoked for show/hide and still cover placement logic.

### Behaviour impact

- Progress pill canvas creation, positioning, and show/hide now occur on the Talon main thread, reducing “resource context unavailable” errors from background request workers; toast fallback remains unchanged.

### Follow-ups and remaining work

- Consider centralizing other Talon UI surfaces behind the same dispatcher if they can be triggered off-thread.
- Add logging/metrics around pill show/hide failures once available to quantify remaining flake.

## 2025-12-08 – Slice: Ignore stale show callbacks after hide

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Prevent delayed main-thread show callbacks from resurrecting the pill after a hide, keeping canvas lifecycle consistent when called from background threads.

### Summary of this loop

- Added a generation counter to `PillState` and use it to skip scheduled show attempts if a hide has occurred in the meantime.
- `show_pill` now captures the generation and only shows when still current; `hide_pill` bumps the generation to invalidate pending callbacks.
- Added a test to ensure delayed show callbacks are ignored after hide while retaining UI-thread dispatch coverage.

### Behaviour impact

- Background-triggered show calls can no longer race with hide to leave the pill visible; stale scheduled shows are dropped safely.

### Follow-ups

- If further pill flake appears, add logging/metrics around skipped/stale callbacks and consider similar guards for other Talon UI surfaces.

## 2025-12-08 – Slice: Skip redundant pill shows when unchanged

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Reduce unnecessary UI-thread dispatch from background workers by avoiding duplicate pill show scheduling when phase/text are unchanged.

### Summary of this loop

- Added a redundant-show guard in `lib/pillCanvas.py` that skips scheduling when the pill is already showing the same phase/text, keeping dispatcher load lower when workers emit repeated events.
- Tests updated to cover the guard and still confirm UI-thread dispatch attempts.

### Behaviour impact

- Repeated identical show calls no longer enqueue extra main-thread work; the pill remains visible without extra canvas churn.

### Follow-ups

- Monitor if additional debouncing is needed for rapid phase changes (e.g., streaming → done) and consider metrics around skipped dispatches.

## 2025-12-08 – Slice: Compute pill rect on UI-thread show path

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Ensure rect computation and logging for the progress pill occur on the UI-thread show path to keep all canvas-related work off background threads.

### Summary of this loop

- Moved `_default_rect` computation and show debug logging inside the UI-thread `_try_show` callback in `lib/pillCanvas.py`, so background callers no longer touch Talon screen/rect APIs.
- Confirmed behaviour with existing pill tests.

### Behaviour impact

- Canvas rect selection now happens on the main thread alongside show/hide, tightening adherence to Talon’s UI-thread requirements and reducing background access to UI resources.

### Follow-ups

- Consider similar migrations for other UI surfaces if they compute screen geometry off-thread.

## 2025-12-09 – Slice: Status reconciliation and acceptance

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Confirm main-thread dispatch, stale-guard, and redundant-show protections are in place for the pill and mark the ADR accepted.

### Summary of this loop

- Reviewed ADR 029 objectives: main-thread dispatcher for pill canvas lifecycle, thread-safe controller callbacks, toast fallback, and guards against stale/off-thread canvas access.
- Verified implementation covers these: `_run_on_ui_thread` for show/hide/rect, generation guard for stale callbacks, redundant-show skip, UI-thread rect computation, and tests for dispatch/stale handling.
- Ran targeted tests (`python3 -m pytest _tests/test_pill_canvas.py`) to validate the safeguards.
- Updated ADR 029 status to Accepted.

### Behaviour impact

- ADR 029 is now recorded as Accepted with implemented safeguards; no functional changes beyond prior slices.

### Follow-ups

- Optional: extend UI-thread dispatcher pattern to other Talon surfaces if they are ever invoked from background threads; add logging/metrics if flakes reappear.

## 2025-12-10 – Slice: Post-acceptance check (no further in-repo work)

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Confirm no remaining in-repo tasks for ADR 029 after acceptance and note optional future monitoring only.

### Summary of this loop

- Re-reviewed ADR 029 scope and implementation: UI-thread dispatcher, stale guard, redundant-show guard, UI-thread rect computation, toast fallback, and tests are in place.
- No additional code changes required; keeping an eye on optional metrics/dispatcher reuse as future work only.

### Behaviour impact

- No functional change; ADR remains Accepted with no remaining in-repo tasks.

### Follow-ups

- Only if pill flake resurfaces: add logging/metrics or extend dispatcher to other UI surfaces.

## 2025-12-10 – Slice: Extend main-thread dispatch to request UI surfaces

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Ensure request UI surface callbacks also marshal to the Talon main thread and keep tests resilient to pill state reuse.

### Summary of this loop

- Wrapped request UI callbacks (`_show_pill`, `_hide_pill`, response-canvas open, help-hub close) in a UI-thread dispatcher so background request events no longer invoke Talon UI actions directly (`lib/requestUI.py`).
- Added a test to assert UI-thread dispatch is used for canvas destinations and reset `PillState` between request UI tests to avoid redundant-show skipping (`_tests/test_request_ui.py`).
- Ran targeted tests for request UI and pill canvas.

### Behaviour impact

- Request UI surface calls now respect the main-thread boundary, aligning the controller with ADR 029 and reducing off-thread UI risks.

### Follow-ups

- Optional: add logging/metrics if UI dispatch fails; consider sharing the dispatcher utility across other Talon UI modules.

## 2025-12-10 – Slice: Shared UI-thread dispatcher utility

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Centralize UI-thread dispatching in a shared helper and use it for both pill canvas and request UI surfaces.

### Summary of this loop

- Added `lib/uiDispatch.py` with `run_on_ui_thread`, wrapping `cron.after` with fallback.
- Updated `lib/pillCanvas.py` and `lib/requestUI.py` to use the shared dispatcher instead of per-module implementations.
- Adjusted tests to patch the shared dispatcher entrypoints.

### Behaviour impact

- Dispatcher logic is now centralized, reducing duplication and keeping all pill/request UI work on the Talon main thread.

### Follow-ups

- Optional: reuse the dispatcher in other Talon UI modules and add logging/metrics on dispatch failures if flakes resurface.

## 2025-12-10 – Slice: Guard UI-thread dispatcher with tests

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Add coverage for the shared UI-thread dispatcher to ensure it schedules work via `cron.after` and falls back inline on failure.

### Summary of this loop

- Added `lib/uiDispatch.py` tests to verify `run_on_ui_thread` uses `cron.after` with delays and executes callbacks even when scheduling raises.
- Confirmed pill/request UI tests still pass with the shared dispatcher.

### Behaviour impact

- No behavioural change; dispatcher now has targeted tests, reducing regression risk for pill/request UI main-thread routing.

### Follow-ups

- Optional: add logging/metrics around dispatch failures or reuse the dispatcher in other Talon UI modules.

## 2025-12-10 – Slice: Add debug logging to UI dispatcher

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Provide lightweight debug visibility (opt-in) for UI-thread dispatch failures while retaining silent swallow semantics for callers.

### Summary of this loop

- Added a `_debug` helper in `lib/uiDispatch.py` (gated by `user.model_debug_pill`) to log when `cron.after` scheduling fails or a dispatched callable raises.
- Extended dispatcher tests to cover swallowing exceptions.

### Behaviour impact

- No behavioural change by default; when `user.model_debug_pill` is enabled, dispatch failures now log to help diagnose UI-thread issues without breaking callers.

### Follow-ups

- If more visibility is needed, consider routing debug logs to a central logger or adding counters/metrics when available.

## 2025-12-10 – Slice: Response canvas refresh via UI dispatcher

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Ensure response canvas refresh/open operations triggered at request completion use the shared UI-thread dispatcher and are covered by tests.

### Summary of this loop

- Replaced direct `cron.after` scheduling in `lib/modelHelpers.py` with calls to the shared `run_on_ui_thread`, wrapping refresh/open in exception-safe helpers.
- Added tests (`_tests/test_model_helpers_response_canvas.py`) to assert UI-thread dispatch is used (including retries) and that refresh/open exceptions are swallowed.
- Ran targeted test suite for the dispatcher, request UI, pill canvas, and the new refresh tests.

### Behaviour impact

- Response canvas refresh/open now respects the main-thread boundary via the shared dispatcher, reducing off-thread UI calls when requests complete.

### Follow-ups

- Optional: add logging/metrics around refresh failures if they recur; consider applying dispatcher to other canvas/UI actions with `cron.after` calls.

## 2025-12-11 – Slice: No further in-repo work (status check)

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Confirm remaining in-repo scope is exhausted after dispatcher unification and response-canvas routing.

### Summary of this loop

- Re-reviewed ADR 029 scope and recent slices (shared dispatcher, stale/redundant guards, request UI dispatch, response-canvas dispatch and tests).
- Identified no additional in-repo changes needed; any further work would be optional observability/metrics or dispatcher reuse elsewhere.

### Behaviour impact

- None; status-only confirmation.

### Follow-ups

- Optional/outer scope only: metrics/logging or applying the dispatcher to unrelated Talon UI helpers if needed.

## 2025-12-11 – Slice: Default-enable pill debug logging

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Make pill/UI-thread debug logging opt-out so smoke testing is easier by default.

### Summary of this loop

- Switched `user.model_debug_pill` default to on in the debug helpers (`lib/pillCanvas.py`, `lib/uiDispatch.py`) and surfaced it in `talon-ai-settings.talon.example` as enabled (set to 0 to silence).
- Reran dispatcher tests.

### Behaviour impact

- Pill/UI-thread debug logs are now enabled by default; users can set `user.model_debug_pill = 0` to disable them.

### Follow-ups

- If logs are too noisy in some environments, consider downgrading to off by default or adding a throttle; otherwise no further action.

## 2025-12-11 – Slice: Queue-based UI dispatcher to avoid resource context errors

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Ensure UI work dispatched from worker threads is executed on a main-thread cron drain to avoid “No active resource context” errors when creating the pill canvas.

### Summary of this loop

- Reworked `lib/uiDispatch.py` to queue UI tasks with a cron-driven drain, so worker threads enqueue work and the cron drain executes it on the main thread; retains inline fallback on scheduling failure and opt-in debug logging.
- Updated tests to use the new drain helper and validated pill/request UI + response-canvas dispatch paths.
- Tests run: `python3 -m pytest _tests/test_ui_dispatch.py _tests/test_model_helpers_response_canvas.py _tests/test_request_ui.py _tests/test_pill_canvas.py`.

### Behaviour impact

- UI work (pill canvas creation/show/hide, response-canvas refresh) now executes via a main-thread cron drain even when called from worker threads, addressing resource-context errors and reducing notification-only fallback.

### Follow-ups

- If canvas still fails in specific environments, add instrumentation to confirm cron drain is running; consider a small interval-based drain to further decouple from worker timing.

## 2025-12-11 – Slice: Precreate pill canvas on Talon ready event

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Create the pill canvas on Talon’s ready event (main thread) so later worker-thread shows reuse an existing canvas instead of failing to acquire a resource context.

### Summary of this loop

- Added an `app.register("ready", ...)` hook in `lib/pillCanvas.py` to precreate the pill canvas at startup on the main thread, improving the odds that subsequent show calls from worker threads reuse an existing canvas.
- Reran pill/request UI/dispatcher tests to ensure no regressions.

### Behaviour impact

- The pill canvas is now instantiated on Talon ready; worker-thread shows should reuse it rather than creating from the worker context, reducing “No active resource context” errors.

### Follow-ups

- If failures persist, consider a periodic main-thread heartbeat to recreate the canvas when needed and add instrumentation to confirm ready hooks fire in the user’s environment.

## 2025-12-11 – Slice: Drop inline UI fallback and add warmup interval

**ADR focus**: 029 – Main-thread canvas control for the progress pill  
**Loop goal**: Prevent worker threads from running UI work inline when cron scheduling fails, and add a short warmup interval on app ready to create the pill canvas on the main thread.

### Summary of this loop

- Updated `run_on_ui_thread` to drop inline execution when cron scheduling fails, keeping UI work off worker threads.
- Added a warmup interval at Talon ready that repeatedly attempts pill canvas creation on the main thread until it succeeds.
- Reran dispatcher/pill/request UI tests.

### Behaviour impact

- UI work will no longer run inline on worker threads; pill canvas creation gets a main-thread warmup attempt shortly after Talon starts, reducing resource-context errors.

### Follow-ups

- If canvas creation still fails in some environments, consider a longer/periodic heartbeat or explicit instrumentation of cron drain and warmup success.
