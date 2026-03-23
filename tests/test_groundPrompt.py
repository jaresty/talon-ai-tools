"""Tests for groundPrompt sentinel gate additions (orbit/reify/mint analysis)."""
from lib.groundPrompt import GROUND_PARTS, SENTINEL_TEMPLATES


def _full_text() -> str:
    return " ".join(GROUND_PARTS.values())


def test_manifest_declared_sentinel_present():
    """Thread 1: SENTINEL_TEMPLATES contains a 'manifest_declared' sentinel blocking descent into criteria."""
    assert "manifest_declared" in SENTINEL_TEMPLATES, (
        "expected 'manifest_declared' key in SENTINEL_TEMPLATES — "
        "manifest gate must be sentinel-enforced, not prose-only"
    )


def test_ground_entered_sentinel_present():
    """Thread 2: SENTINEL_TEMPLATES contains a 'ground_entered' sentinel gating the first rung."""
    assert "ground_entered" in SENTINEL_TEMPLATES, (
        "expected 'ground_entered' key in SENTINEL_TEMPLATES — "
        "first-rung entry must be sentinel-enforced"
    )


def test_hard_stop_sentinel_present():
    """Thread 3: ground description contains HARD STOP text at observation gap."""
    assert "HARD STOP" in _full_text(), (
        "expected 'HARD STOP' in ground description — "
        "'stop there' prose is insufficient; must be a sentinel that blocks forward motion"
    )
