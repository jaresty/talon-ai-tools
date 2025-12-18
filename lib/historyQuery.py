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
from .requestHistoryActions import (
    axis_snapshot_from_axes as _axis_snapshot_from_axes_impl,
)
from .requestHistoryActions import _directional_tokens_for_entry


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
        axes = getattr(entry, "axes", {}) or {}
        dir_tokens: list[str] = _directional_tokens_for_entry(entry)
        if not dir_tokens:
            # Skip entries without a directional lens to maintain ADR 048 requirements.
            continue
        # Backfill/normalise directional tokens so rendering includes them.
        if isinstance(axes, dict) and dir_tokens:
            axes = dict(axes)
            axes["directional"] = dir_tokens
        prompt = (getattr(entry, "prompt", "") or "").strip().splitlines()[0]
        snippet = prompt[:80] + ("…" if len(prompt) > 80 else "")
        duration_ms = getattr(entry, "duration_ms", None)
        dur = f"{duration_ms}ms" if duration_ms is not None else ""
        request_id = getattr(entry, "request_id", "")
        label = f"{request_id}"
        if dur:
            label = f"{label} ({dur})"
        recipe = (getattr(entry, "recipe", "") or "").strip()
        if axes:
            axes_tokens = _axis_snapshot_from_axes_impl(axes)
            recipe_tokens: list[str] = []
            if recipe:
                static_token = recipe.split(" · ")[0]
                if static_token:
                    recipe_tokens.append(static_token)
            comp = " ".join(axes_tokens.get("completeness", []))
            scope = " ".join(axes_tokens.get("scope", []))
            method = " ".join(axes_tokens.get("method", []))
            form = " ".join(axes_tokens.get("form", []))
            channel = " ".join(axes_tokens.get("channel", []))
            directional = " ".join(axes_tokens.get("directional", []))
            for value in (comp, scope, method, form, channel, directional):
                if value:
                    recipe_tokens.append(value)
            if recipe_tokens:
                recipe = " · ".join(recipe_tokens)
        body = snippet
        if recipe:
            body = f"{recipe} · {snippet}" if snippet else recipe
        provider_id = (getattr(entry, "provider_id", "") or "").strip()
        if provider_id:
            label = f"{label} [{provider_id}]"
        if provider_id:
            body = (
                f"{body} · provider={provider_id}"
                if body
                else f"provider={provider_id}"
            )
        rendered.append((label, body))
    return rendered
