"""Tests for the attributable-coverage preset description in axisConfig.py (CRAFT_PRESETS entry)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import USAGE_PATTERNS


def _coverage_desc():
    for preset in USAGE_PATTERNS:
        if "Attributable Coverage" in preset.get("title", ""):
            return preset.get("desc", "")
    raise AssertionError("Attributable Coverage preset not found in USAGE_PATTERNS")


def test_coverage_preset_exists():
    """The ground+gate+falsify+atomic preset must exist in CRAFT_PRESETS."""
    desc = _coverage_desc()
    assert desc != ""


def test_coverage_desc_no_sentinel_strings():
    """The preset desc must be plain prose — no enforcement sentinel strings."""
    desc = _coverage_desc()
    assert "§ blocked:" not in desc
    assert "§ awaiting:" not in desc
    assert "§ no-next-action:" not in desc
    assert "§0 observed" not in desc
    assert "Continuation invariant" not in desc
