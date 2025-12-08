"""Async request runner scaffolding."""

from __future__ import annotations

import threading
from typing import Any, Callable, Optional

from .requestBus import emit_cancel


class RequestHandle:
    def __init__(self, thread: threading.Thread):
        self._thread = thread
        self.result: Any = None
        self.error: Optional[BaseException] = None
        self._done = threading.Event()

    def wait(self, timeout: Optional[float] = None) -> bool:
        finished = self._done.wait(timeout)
        return finished

    def cancel(self) -> None:
        """Best-effort cancel: emit cancel event and do not join the worker."""
        emit_cancel()

    @property
    def done(self) -> bool:
        return self._done.is_set()

    def _set_result(self, result: Any) -> None:
        self.result = result
        self._done.set()

    def _set_error(self, error: BaseException) -> None:
        self.error = error
        self._done.set()


def start_async(fn: Callable, *args, **kwargs) -> RequestHandle:
    """Run fn(*args, **kwargs) in a background thread and return a handle."""
    handle: RequestHandle

    def _runner():
        try:
            res = fn(*args, **kwargs)
            handle._set_result(res)
        except BaseException as exc:  # noqa: BLE001
            handle._set_error(exc)

    thread = threading.Thread(target=_runner, daemon=True)
    handle = RequestHandle(thread)
    thread.start()
    return handle


__all__ = ["start_async", "RequestHandle"]
