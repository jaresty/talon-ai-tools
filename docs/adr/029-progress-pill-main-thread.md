# 029 – Main-thread canvas control for the progress pill

## Status
Accepted

## Context
- Talon canvases must be created, shown, hidden, and closed on the main thread; doing so from worker threads throws “resource context unavailable” errors and can leave canvases stuck open or uninitialized.
- Our request pipeline emits UI events from background threads (streaming worker / async send) and currently calls `show_pill` / `hide_pill` directly, so pill open/close sometimes fails or flakes depending on timing.
- The request UI controller (ADR 027) is meant to be thread-agnostic, but the pill callbacks pierce that abstraction by touching canvas APIs directly.
- We also reposition the pill per-show, which compounds the threading risk because rect assignment recreates canvases.

## Decision
- Route all pill canvas lifecycle calls (create/show/hide/rect updates) through a tiny main-thread dispatcher and forbid direct canvas access from worker threads.
- Keep the controller callbacks (`show_pill`, `hide_pill`) thread-safe: they enqueue work onto the main thread and return immediately; background callers never touch canvas objects.
- Preserve a toast fallback for cases where main-thread scheduling fails so progress remains visible even if the canvas cannot be manipulated.
- Align this with ADR 027 surfaces: the controller continues to orchestrate when the pill should show/hide, but the canvas work happens only on the main thread.

## Rationale
- Canvas APIs are UI-thread-only in Talon; enforcing a single-threaded boundary avoids intermittent “resource context” failures and prevents leaked canvases or stuck overlays.
- A dispatcher keeps request/state code simple and testable while isolating UI resource handling.
- A best-effort fallback maintains user feedback even when canvas scheduling fails or is unsupported in an environment.

## Implementation notes
- Add a main-thread dispatcher helper (e.g., `run_on_ui_thread(fn, delay_ms=0)`) in `pillCanvas` that wraps `cron.after`/`app.notify_wait` as needed; reuse it for both show and hide, plus rect updates and recreate paths.
- Update `show_pill` / `hide_pill` to queue canvas operations onto the main thread; ensure double-invocation is idempotent and that hide waits for any pending show before closing.
- Guard rect application/recreation with the same dispatcher to avoid cross-thread mutations of `canvas.rect` or `canvas.close()`.
- Ensure controller wiring in `requestUI` keeps using these wrappers; background workers remain unchanged except for removing any direct canvas calls.
- Tests: extend pill/request UI tests to assert the dispatcher is invoked (stubbed) and that background-thread calls do not touch canvas mocks directly; run with `python3 -m pytest`.

## Consequences
- Small scheduling delay (one tick) before the pill appears/hides, but predictable and thread-safe behaviour replaces flaky failures.
- Canvas operations are centralized, making it easier to add metrics/logging around show/hide failures and to swap out the dispatcher if Talon threading requirements change.
- The fallback toast path becomes the only behaviour when main-thread dispatch is unavailable, keeping users informed even without the pill overlay.
