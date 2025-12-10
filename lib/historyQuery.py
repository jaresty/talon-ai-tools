from __future__ import annotations

"""HistoryQuery façade over request history helpers.

This module provides a small, testable surface for history-related queries
called out in ADR-0037. It delegates to the pure helpers defined in
`requestHistoryActions` and `requestHistoryDrawer` without adding new
behaviour.
"""

from collections.abc import Sequence
from typing import List, Tuple

from .requestHistoryActions import history_axes_for as _history_axes_for_impl
from .requestHistoryActions import history_summary_lines as _history_summary_lines_impl


def history_axes_for(axes: dict[str, list[str]]) -> dict[str, list[str]]:
    """HistoryQuery façade: normalise stored history axes.

    Thin wrapper over `requestHistoryActions.history_axes_for` so callers can
    treat HistoryQuery as the single entrypoint for axis token filtering.
    """

    return _history_axes_for_impl(axes)


def history_summary_lines(entries: Sequence[object]) -> list[str]:
    """HistoryQuery façade: format recent history entries into summary lines.

    Delegates to `requestHistoryActions.history_summary_lines`.
    """

    return _history_summary_lines_impl(entries)


def history_drawer_entries_from(entries: Sequence[object]) -> List[Tuple[str, str]]:
    """HistoryQuery façade: render entries for the history drawer.

    This mirrors the existing requestHistoryDrawer formatting so callers can
    depend on HistoryQuery as the single source of truth for history drawer
    labels and bodies.
    """

    rendered: List[Tuple[str, str]] = []
    for entry in entries:
        prompt = (getattr(entry, "prompt", "") or "").strip().splitlines()[0]
        snippet = prompt[:80] + ("…" if len(prompt) > 80 else "")
        duration_ms = getattr(entry, "duration_ms", None)
        dur = f"{duration_ms}ms" if duration_ms is not None else ""
        request_id = getattr(entry, "request_id", "")
        label = f"{request_id}"
        if dur:
            label = f"{label} ({dur})"
        recipe = (getattr(entry, "recipe", "") or "").strip()
        body = snippet
        if recipe:
            body = f"{recipe} · {snippet}" if snippet else recipe
        rendered.append((label, body))
    return rendered
