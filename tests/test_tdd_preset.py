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


def test_tdd_desc_no_sentinel_strings():
    """TDD preset desc must be plain prose — no enforcement sentinel strings."""
    desc = _tdd_desc()
    assert "§ blocked:" not in desc
    assert "§ awaiting:" not in desc
    assert "§ no-next-action:" not in desc
    assert "§0 observed" not in desc
    assert "Continuation invariant" not in desc
