"""Tests for the TDD preset description in axisConfig.py (CRAFT_PRESETS entry)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import USAGE_PATTERNS


def _tdd_desc():
    for preset in USAGE_PATTERNS:
        if "TDD" in preset.get("title", ""):
            return preset.get("desc", "")
    raise AssertionError("TDD preset not found in USAGE_PATTERNS")


def test_tdd_preset_exists():
    """TDD Enforcement preset must exist in CRAFT_PRESETS."""
    desc = _tdd_desc()
    assert desc != ""


def test_tdd_continuation_blocked_sentinel():
    """Fix 3: § blocked: sentinel must be named as a valid turn-end string."""
    desc = _tdd_desc()
    assert "§ blocked:" in desc


def test_tdd_continuation_awaiting_sentinel():
    """Fix 3: § awaiting: sentinel must be named as a valid turn-end string."""
    desc = _tdd_desc()
    assert "§ awaiting:" in desc


def test_tdd_continuation_no_next_action_sentinel():
    """Fix 3: § no-next-action: sentinel must be named as a valid turn-end string."""
    desc = _tdd_desc()
    assert "§ no-next-action:" in desc


def test_tdd_continuation_satisfied_gate_strings():
    """Fix 3: at least one satisfied-gate string must be named as a continuation trigger."""
    desc = _tdd_desc()
    assert "Gate condition:" in desc or "§0 observed" in desc or "§1 goal derived" in desc
