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


def test_ground_falsify_carries_coverage_gate():
    """P6a: ground+falsify must carry the Coverage gate — coverage of the artifact against each retained property."""
    prose = _get_entry("ground+falsify")
    assert "Coverage gate" in prose
    assert "Retained properties:" in prose


def test_ground_falsify_gate_2_terminates_on_no_change_pass():
    """P6a: Gate 2's loop terminates on a pass that changes nothing (fixed point)."""
    prose = _get_entry("ground+falsify")
    assert "no guard revision and no artifact change" in prose


def test_ground_falsify_frozen_property_set():
    """P6a: the retained property set is frozen during the Gate 2 loop; missing properties re-enter Ground."""
    prose = _get_entry("ground+falsify")
    assert "frozen" in prose
    assert "Audit: implementation gap" in prose


def test_ground_falsify_gate_2_both_directions():
    """P6a': Gate 2 checks the implementation against properties in BOTH directions — nothing more or less."""
    prose = _get_entry("ground+falsify")
    assert "nothing more or less" in prose


def test_ground_falsify_gate_2_less_strengthens_guard():
    """P6a': when the implementation does LESS than a property, strengthen the guard and re-run Gate 1."""
    prose = _get_entry("ground+falsify")
    assert "strengthen the guard" in prose


def test_ground_falsify_gate_2_more_surfaces_surplus():
    """P6a': when the implementation does MORE than the properties, emit Audit: implementation surplus and classify."""
    prose = _get_entry("ground+falsify")
    assert "Audit: implementation surplus" in prose


def test_ground_falsify_gate_2_surplus_classified_not_auto_weakened():
    """P6a': the surplus is classified (promote to property OR weaken guard) — never silently auto-weakened."""
    prose = _get_entry("ground+falsify")
    assert "if the behavior is required" in prose
    assert "weaken the guard" in prose


def test_ground_falsify_gate_2_classification_follows_execution():
    """P9 (composition): the surplus classification is valid only when backed by an executed discriminator, not asserted."""
    prose = _get_entry("ground+falsify")
    assert "executed discriminator" in prose


# --- P11: assertion↔property map — each assertion tagged with the property it tests; bijection ---

def test_ground_falsify_p11_assertion_tagged_with_property():
    """P11: each enumerated assertion must name the retained property [N] it tests."""
    prose = _get_entry("ground+falsify")
    assert "tag each 'Assertion:' line enumerated in Gate 3 with the retained property" in prose


def test_ground_falsify_p11_bijection_both_directions():
    """P11: the map must be a bijection — every property has ≥1 assertion (not less), every assertion maps to a property (not more)."""
    prose = _get_entry("ground+falsify")
    assert "every retained property has at least one assertion" in prose
    assert "every assertion maps to a retained property" in prose


def test_ground_falsify_p11_unmatched_is_surplus_or_gap():
    """P11: an assertion with no property is surplus; a property with no assertion is a coverage gap."""
    prose = _get_entry("ground+falsify")
    assert "An assertion that maps to no retained property is surplus" in prose
    assert "a retained property with no assertion is a coverage gap" in prose


def test_ground_falsify_ordering_before_falsify_artifact():
    """ground+falsify still requires Ground to reach § ground complete before any falsify artifact."""
    prose = _get_entry("ground+falsify")
    assert "ground complete" in prose


def test_ground_falsify_no_old_six_step_reference():
    """The old token-side six-step/audit machinery reference must be gone from the composition."""
    prose = _get_entry("ground+falsify")
    assert "six-step cycle" not in prose
    assert "Observing: property" not in prose


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
