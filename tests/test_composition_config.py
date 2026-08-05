"""Tests for composition config entries in compositionConfig.py."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.compositionConfig import COMPOSITIONS


def _get_entry(name):
    for entry in COMPOSITIONS:
        if entry["name"] == name:
            return entry["prose"]
    return None


def _names():
    return {entry["name"] for entry in COMPOSITIONS}


# --- Removed entries must not exist ---

def test_gate_falsify_entry_absent():
    """gate+falsify composition entry was removed (absorbed by falsify definition)."""
    assert _get_entry("gate+falsify") is None


def test_gate_atomic_entry_absent():
    """gate+atomic composition entry was removed (absorbed by atomic definition)."""
    assert _get_entry("gate+atomic") is None


def test_falsify_atomic_entry_absent():
    """falsify+atomic composition entry was removed (absorbed by falsify/atomic definitions)."""
    assert _get_entry("falsify+atomic") is None


def test_atomic_ground_entry_absent():
    """atomic+ground composition entry was removed."""
    assert _get_entry("atomic+ground") is None


def test_ground_gate_falsify_atomic_chain_entry_absent():
    """ground+gate+falsify+atomic+chain multi-token entry was removed."""
    assert _get_entry("ground+gate+falsify+atomic+chain") is None


# --- Present entries have non-empty prose ---

def test_ground_falsify_entry_present():
    """ground+falsify entry must exist with non-empty prose."""
    prose = _get_entry("ground+falsify")
    assert prose is not None, "ground+falsify entry not found"
    assert len(prose) > 0


def test_ground_falsify_references_six_step_cycle():
    """ground+falsify prose must reference the full falsify six-step cycle."""
    prose = _get_entry("ground+falsify")
    assert "six-step cycle" in prose or "Observing:" in prose


def test_ground_falsify_references_coverage_sentinel():
    """ground+falsify must gate Coverage: on all properties completing."""
    prose = _get_entry("ground+falsify")
    assert "Coverage:" in prose


def test_falsify_chain_entry_present():
    """falsify+chain entry must exist with non-empty prose."""
    prose = _get_entry("falsify+chain")
    assert prose is not None, "falsify+chain entry not found"
    assert len(prose) > 0


def test_probe_falsify_entry_present():
    """probe+falsify entry must exist."""
    prose = _get_entry("probe+falsify")
    assert prose is not None, "probe+falsify entry not found"
    assert len(prose) > 0


def test_all_entries_have_prose():
    """Every composition entry must have non-empty prose."""
    for entry in COMPOSITIONS:
        assert entry.get("prose"), f"Entry '{entry['name']}' has empty or missing prose"
