"""Utilities for dispatching work to the Talon UI thread."""

from __future__ import annotations

import threading
import time
from collections import deque
from datetime import datetime, timezone
from typing import Callable, Dict

from talon import cron, settings


def _debug(msg: str) -> None:
    try:
        if not settings.get("user.model_debug_pill", True):
            return
    except Exception:
        return
    try:
        print(f"[uiDispatch] {msg}")
    except Exception:
        pass


def _safe_run(fn: Callable[[], None]) -> None:
    try:
        fn()
    except Exception as e:
        _debug(f"ui dispatch fn failed: {e}")
        # Swallow to avoid breaking callers on UI dispatch failure.
        pass


def _run_inline(fn: Callable[[], None], delay_ms: int | float = 0) -> None:
    delay = 0.0
    if delay_ms:
        try:
            delay = float(delay_ms) / 1000.0
        except (TypeError, ValueError):
            delay = 0.0
    if delay > 0:
        time.sleep(delay)
    _safe_run(fn)


def _normalize_delay(delay_ms: object) -> int:
    if isinstance(delay_ms, bool):
        return int(delay_ms)
    if isinstance(delay_ms, (int, float)):
        try:
            value = int(delay_ms)
        except (TypeError, ValueError):
            return 0
        return value if value > 0 else 0
    return 0


def _record_inline(delay_ms: object) -> None:
    delay_key = _normalize_delay(delay_ms)
    now_monotonic = time.monotonic()
    now_wallclock = time.time()
    with _inline_counts_lock:
        _inline_fallback_counts[delay_key] = (
            _inline_fallback_counts.get(delay_key, 0) + 1
        )
        global _inline_fallback_last_timestamp, _inline_fallback_last_wallclock
        _inline_fallback_last_timestamp = now_monotonic
        _inline_fallback_last_wallclock = now_wallclock


def run_on_ui_thread(fn: Callable[[], None], delay_ms: int = 0) -> None:
    """Dispatch a callable to the Talon main thread, with fallback inline."""

    with _queue_lock:
        if _schedule_failed:
            execute_inline = True
        else:
            _queue.append((fn, delay_ms))
            execute_inline = False
    if execute_inline:
        _record_inline(delay_ms)
        _run_inline(fn, delay_ms)
        _maybe_probe_schedule()
    else:
        _schedule_drain()


# --- Internal queue + drain machinery ---

_FALLBACK_PROBE_INTERVAL = 1.0

_queue = deque()
_queue_lock = threading.Lock()
_draining = False
_schedule_failed = False
_fallback_warned = False
_fallback_next_probe = 0.0
_inline_fallback_counts: Dict[int, int] = {}
_inline_fallback_last_timestamp = 0.0
_inline_fallback_last_wallclock = 0.0
_inline_counts_lock = threading.Lock()
_fallback_notified = False


def _snapshot_inline_stats(reset: bool = False) -> dict[str, object]:
    global _inline_fallback_last_timestamp, _inline_fallback_last_wallclock
    with _inline_counts_lock:
        counts = dict(_inline_fallback_counts)
        last = _inline_fallback_last_timestamp
        wall = _inline_fallback_last_wallclock
        if reset:
            _inline_fallback_counts.clear()
            _inline_fallback_last_timestamp = 0.0
            _inline_fallback_last_wallclock = 0.0
    return {"counts": counts, "last": last, "wall": wall}


def _notify_inline_fallback() -> None:
    global _fallback_notified
    if _fallback_notified:
        return
    _fallback_notified = True
    try:
        from .modelHelpers import notify  # type: ignore
    except Exception:
        return
    try:
        notify(
            "Talon UI dispatcher degraded; running inline until cron scheduling recovers."
        )
    except Exception:
        pass


def _schedule_drain() -> None:
    global _schedule_failed, _fallback_warned, _fallback_next_probe, _fallback_notified
    try:
        cron.after("0ms", _drain_queue)
        if _schedule_failed:
            _debug("cron dispatch recovered; resuming scheduled UI drain")
        _schedule_failed = False
        _fallback_warned = False
        _fallback_next_probe = 0.0
        _fallback_notified = False
    except Exception as e:
        if not _schedule_failed and not _fallback_warned:
            _debug(f"cron dispatch failed ({e}); draining UI work inline")
            _notify_inline_fallback()
            _fallback_warned = True
        _schedule_failed = True
        _fallback_next_probe = time.monotonic() + _FALLBACK_PROBE_INTERVAL
        _drain_queue_inline()


def _drain_queue() -> None:
    global _draining
    with _queue_lock:
        if _draining:
            return
        _draining = True
    try:
        while True:
            with _queue_lock:
                if not _queue:
                    break
                fn, delay_ms = _queue.popleft()
            if delay_ms and isinstance(delay_ms, (int, float)) and delay_ms > 0:
                try:
                    cron.after(f"{int(delay_ms)}ms", lambda fn=fn: _safe_run(fn))
                except Exception as e:
                    _debug(f"cron dispatch (delay) failed ({e}); running inline")
                    _safe_run(fn)
            else:
                _safe_run(fn)
    finally:
        with _queue_lock:
            _draining = False


def _drain_queue_inline() -> None:
    """Drain queued tasks inline (used only in tests)."""
    global _draining
    with _queue_lock:
        if _draining:
            return
        _draining = True
    try:
        while True:
            try:
                fn, delay_ms = _queue.popleft()
            except IndexError:
                break
            _record_inline(delay_ms)
            _run_inline(fn, delay_ms)
    finally:
        with _queue_lock:
            _draining = False


def _maybe_probe_schedule() -> None:
    if not _schedule_failed:
        return
    now = time.monotonic()
    if now < _fallback_next_probe:
        return
    # Attempt to reschedule; `_schedule_drain` will update probe timing.
    _schedule_drain()


def ui_dispatch_inline_stats(*, reset: bool = False) -> dict[str, object]:
    snapshot = _snapshot_inline_stats(reset=reset)
    counts: Dict[str, int] = {}
    total = 0
    for delay_value, count in snapshot.get("counts", {}).items():
        try:
            delay_key = int(delay_value)
        except (TypeError, ValueError):
            continue
        try:
            count_value = int(count)
        except (TypeError, ValueError):
            continue
        if count_value <= 0:
            continue
        counts[str(delay_key)] = count_value
        total += count_value

    last_monotonic_raw = snapshot.get("last")
    try:
        last_monotonic_value = float(last_monotonic_raw)
    except (TypeError, ValueError):
        last_monotonic_value = 0.0
    if last_monotonic_value < 0:
        last_monotonic_value = 0.0

    last_wall_raw = snapshot.get("wall")
    try:
        last_wall_value = float(last_wall_raw)
    except (TypeError, ValueError):
        last_wall_value = 0.0

    last_wall_iso = ""
    if last_wall_value > 0:
        try:
            last_wall_iso = datetime.fromtimestamp(
                last_wall_value, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            last_wall_iso = ""

    seconds_since_last: float | None = None
    if last_monotonic_value > 0:
        try:
            current_monotonic = time.monotonic()
        except Exception:
            current_monotonic = 0.0
        if current_monotonic >= last_monotonic_value > 0:
            seconds_since_last = current_monotonic - last_monotonic_value

    return {
        "counts": counts,
        "total": total,
        "last_monotonic": last_monotonic_value,
        "last_wall_time": last_wall_iso,
        "seconds_since_last": seconds_since_last,
        "active": ui_dispatch_fallback_active(),
    }


# Test helper to flush queued work synchronously.
def _drain_for_tests() -> None:
    _drain_queue_inline()


def ui_dispatch_fallback_active() -> bool:
    with _queue_lock:
        return _schedule_failed


__all__ = [
    "run_on_ui_thread",
    "ui_dispatch_fallback_active",
    "ui_dispatch_inline_stats",
]
