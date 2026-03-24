"""Tests for groundPrompt — sentinel gates and ADR-0179 axiom-first formulation."""
from lib.groundPrompt import SENTINEL_TEMPLATES, build_ground_prompt


def test_manifest_declared_sentinel_present():
    """SENTINEL_TEMPLATES contains a 'manifest_declared' sentinel."""
    assert "manifest_declared" in SENTINEL_TEMPLATES


def test_ground_entered_sentinel_present():
    """SENTINEL_TEMPLATES contains a 'ground_entered' sentinel."""
    assert "ground_entered" in SENTINEL_TEMPLATES


def test_hard_stop_sentinel_present():
    """Rendered ground prompt contains HARD STOP text."""
    assert "HARD STOP" in build_ground_prompt()


def test_hard_stop_signals_upward_return_not_termination():
    """HARD STOP description specifies upward return to criteria, not termination."""
    text = build_ground_prompt()
    hard_stop_idx = text.index("HARD STOP")
    nearby = text[hard_stop_idx:hard_stop_idx + 300]
    assert "no further content" not in nearby


def test_axiom_a1_present():
    """ADR-0179: rendered prompt states A1 (epistemic authority — tool-executed events only)."""
    text = build_ground_prompt()
    assert "A1" in text, (
        "expected 'A1' in rendered ground prompt — "
        "axiom-first formulation must name A1 explicitly"
    )


def test_axiom_r2_present():
    """ADR-0179: rendered prompt states R2 as a named axiom (not only in sentinel text)."""
    text = build_ground_prompt()
    # "R2" already appears in sentinel text; require it to appear before the sentinel block
    sentinel_block_marker = "Sentinel formats"
    sentinel_idx = text.index(sentinel_block_marker) if sentinel_block_marker in text else len(text)
    pre_sentinel = text[:sentinel_idx]
    assert "R2" in pre_sentinel, (
        "expected 'R2' in the axiom/rule section of the rendered prompt (before sentinel block) — "
        "axiom-first formulation must name R2 as a derivation rule"
    )
