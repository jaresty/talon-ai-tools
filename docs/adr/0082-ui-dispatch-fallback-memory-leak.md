# 082 – Harden UI dispatch fallback when Talon scheduling fails

## Status
Proposed

## Context
- Overnight Talon sessions with no explicit requests still grew past 35 GB of RAM.
- Background surfaces (progress pill, response canvas, history drawer, Help Hub) call `run_on_ui_thread` to queue repaint and refresh work on the main thread.
- `run_on_ui_thread` enqueues work into an in-process deque and uses `cron.after("0ms", _drain_queue)` to hand control back to Talon.
- When Talon rejects the `cron.after` call (for example during sleep or when the engine is pausing), `_schedule_failed` flips to `True`, but the implementation only logs a debug message and returns without draining.
- Subsequent background activity keeps appending to `_queue` even though the drain never runs again; the deque accumulates closures indefinitely and leaks memory.
- ADR 029 moved pill management to the main thread assuming this dispatcher would stay bounded; losing the drain breaks that guarantee and cascades into every caller that relies on it.

## Decision
- Treat a failed `cron.after` as a signal to run queued work inline instead of abandoning it: immediately drain `_queue` synchronously inside the `except` block.
- Short-circuit future enqueues while `_schedule_failed` is set: new `run_on_ui_thread` calls drain inline rather than growing the deque until the dispatcher successfully schedules again.
- Surface a one-time warning (debug log + optional telemetry counter) so operators can see that Talon refused main-thread scheduling and that the dispatcher fell back to inline execution.
- Expose a helper (`ui_dispatch_fallback_active()`) for tests and diagnostics so callers can assert whether they are on the degraded path.

## Rationale
- Inline draining preserves correctness with bounded memory use—the queue cannot grow without limit because every enqueue either schedules a drain or performs it immediately.
- Guarding against repeated scheduling attempts prevents thrashing the Talon cron API when it is already rejecting calls.
- A visible warning helps correlate degraded UI responsiveness with Talon runtime state and guides operators toward restarting Talon when necessary.
- Tests can assert the degraded mode without depending on private globals, keeping the dispatcher observable and maintainable.

## Implementation Notes
- Update `_schedule_drain` to call `_drain_queue_inline()` inside the failure path, set `_schedule_failed = True`, and skip the early return that currently leaks work.
- In `run_on_ui_thread`, detect `_schedule_failed` before appending; if the flag is set, execute `_safe_run` (respecting `delay_ms`) inline under the queue lock instead of enqueuing.
- Reset `_schedule_failed` to `False` once a `cron.after` succeeds so future calls re-use the scheduled drain path.
- Add a lightweight counter or debug print that fires only the first time per session we enter fallback mode to avoid log spam.
- Extend dispatcher unit tests to simulate `cron.after` raising and confirm that queued work drains, `_queue` stays empty, and future calls run inline until scheduling recovers.

## Consequences
- Inline fallback may make UI callbacks run on background threads during Talon downtime, trading thread isolation for stability; callers already handle best-effort execution, and the alternative was an unbounded leak.
- Operators may experience brief jitter when Talon resumes, but they gain better visibility into dispatcher degradation.
- Future surfaces should treat degraded mode as a signal to prefer toast notifications or defer non-critical UI work; the helper makes that gate explicit.
- The ADR closes the memory leak while keeping ADR 029’s main-thread guarantees intact whenever Talon cron scheduling is available.
