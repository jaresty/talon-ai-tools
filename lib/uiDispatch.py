"""Utilities for dispatching work to the Talon UI thread."""

from __future__ import annotations

import threading
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


def run_on_ui_thread(fn: Callable[[], None], delay_ms: int = 0) -> None:
    """Dispatch a callable to the Talon main thread, with fallback inline."""

    with _queue_lock:
        _queue.append((fn, delay_ms))
    _schedule_drain()


# --- Internal queue + drain machinery ---

_queue = deque()
_queue_lock = threading.Lock()
_draining = False
_schedule_failed = False


def _schedule_drain() -> None:
    global _schedule_failed
    try:
        cron.after("0ms", _drain_queue)
    except Exception as e:
        _schedule_failed = True
        _debug(f"cron dispatch failed ({e}); dropping queued UI work")
        return


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
                fn, _ = _queue.popleft()
            except IndexError:
                break
            _safe_run(fn)
    finally:
        with _queue_lock:
            _draining = False


def _safe_run(fn: Callable[[], None]) -> None:
    try:
        fn()
    except Exception as e:
        _debug(f"ui dispatch fn failed: {e}")
        # Swallow to avoid breaking callers on UI dispatch failure.
        pass


# Test helper to flush queued work synchronously.
def _drain_for_tests() -> None:
    _drain_queue_inline()


__all__ = ["run_on_ui_thread"]
