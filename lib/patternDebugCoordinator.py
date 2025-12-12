from __future__ import annotations

from typing import Optional

from .modelPatternGUI import PATTERNS, PatternDomain, pattern_debug_snapshot


def pattern_debug_catalog(
    domain: Optional[PatternDomain] = None,
) -> list[dict[str, object]]:
    """Return debug snapshots for all patterns, optionally filtered by domain.

    This helper is a small coordinator-style façade for the Pattern Debug & GPT
    Action domain. Callers (GUIs, GPT actions, tests) can obtain a stable list
    of pattern debug snapshots without reimplementing iteration or filtering
    logic around ``PATTERNS``.
    """

    snapshots: list[dict[str, object]] = []
    for pattern in PATTERNS:
        if domain is not None and pattern.domain != domain:
            continue
        snapshot = pattern_debug_snapshot(pattern.name)
        if snapshot:
            snapshots.append(snapshot)
    return snapshots
