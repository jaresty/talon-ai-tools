"""gpt_busy Talon tag — set while a GPT model request is actively in-flight.

Toggled by update(), which is called from requestUI._on_state_change so the
tag mirrors the request phase without any additional subscription machinery.

On module load (including Talon reload) the tag is always cleared so a crashed
or interrupted request cannot leave commands permanently disabled.

ADR-035, ADR-0080 Workstream 3.
"""

from __future__ import annotations

from .historyLifecycle import RequestPhase, RequestState

try:
    from talon import Module, Context  # type: ignore

    mod = Module()
    ctx = Context()
    mod.tag("gpt_busy", desc="Set while a GPT model request is actively in-flight.")
except Exception:
    # Test harness: Talon runtime unavailable; provide minimal stubs.
    from types import SimpleNamespace

    ctx = SimpleNamespace(tags=[])  # type: ignore[assignment]


_ACTIVE_PHASES = frozenset(
    {
        RequestPhase.SENDING,
        RequestPhase.STREAMING,
        RequestPhase.TRANSCRIBING,
        RequestPhase.LISTENING,
        RequestPhase.CONFIRMING,
    }
)


def update(state: RequestState) -> None:
    """Set or clear user.gpt_busy based on the current request phase."""
    try:
        if getattr(state, "phase", None) in _ACTIVE_PHASES:
            ctx.tags = ["user.gpt_busy"]
        else:
            ctx.tags = []
    except Exception:
        pass


# Clear tag on module load / Talon reload to avoid stuck-busy state.
try:
    ctx.tags = []
except Exception:
    pass
