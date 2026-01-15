"""Utilities for dispatching work to the Talon UI thread."""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Callable

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


def run_on_ui_thread(fn: Callable[[], None], delay_ms: int = 0) -> None:
    """Dispatch a callable to the Talon main thread, with fallback inline."""

    with _queue_lock:
        if _schedule_failed:
            execute_inline = True
        else:
            _queue.append((fn, delay_ms))
            execute_inline = False
    if execute_inline:
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


def _schedule_drain() -> None:
    global _schedule_failed, _fallback_warned, _fallback_next_probe
    try:
        cron.after("0ms", _drain_queue)
        if _schedule_failed:
            _debug("cron dispatch recovered; resuming scheduled UI drain")
        _schedule_failed = False
        _fallback_warned = False
        _fallback_next_probe = 0.0
    except Exception as e:
        if not _schedule_failed and not _fallback_warned:
            _debug(f"cron dispatch failed ({e}); draining UI work inline")
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


# Test helper to flush queued work synchronously.
def _drain_for_tests() -> None:
    _drain_queue_inline()


def ui_dispatch_fallback_active() -> bool:
    with _queue_lock:
        return _schedule_failed


__all__ = ["run_on_ui_thread", "ui_dispatch_fallback_active"]
