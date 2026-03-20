"""Thread 1 validation: lib/groundPrompt.py structure and content."""
import pytest
from lib.groundPrompt import GROUND_PARTS, build_ground_prompt

EXPECTED_KEYS = ["derivation_structure", "gate_validity", "derivation_discipline", "reconciliation_and_completion"]


def test_ground_parts_has_expected_keys():
    assert list(GROUND_PARTS.keys()) == EXPECTED_KEYS


def test_ground_parts_all_nonempty():
    for key in EXPECTED_KEYS:
        assert GROUND_PARTS[key].strip(), f"GROUND_PARTS['{key}'] is empty"


def test_build_ground_prompt_joins_all_parts():
    result = build_ground_prompt()
    for key in EXPECTED_KEYS:
        assert GROUND_PARTS[key] in result


def test_build_ground_prompt_is_space_joined():
    result = build_ground_prompt()
    assert result == " ".join(GROUND_PARTS[k] for k in EXPECTED_KEYS)


def test_derivation_structure_content():
    assert "I is the declared intent" in GROUND_PARTS["derivation_structure"]


def test_formal_notation_r2_requirement():
    ds = GROUND_PARTS["derivation_structure"]
    assert "Formal notation must satisfy R2" in ds, (
        "derivation_structure must state that formal notation must satisfy R2"
    )
    assert "behavioral constraint" in ds, (
        "derivation_structure must mention behavioral constraints for formal notation"
    )
    assert "interface shape" in ds or "structure without encoding invariants" in ds, (
        "derivation_structure must distinguish shape-only notation from complete notation"
    )


def test_gate_validity_content():
    assert "conversation-state condition" in GROUND_PARTS["gate_validity"]


def test_gate_validity_passing_run_is_gap_signal():
    gv = GROUND_PARTS["gate_validity"]
    assert "vacuous" in gv, (
        "gate_validity must state that a passing run without observed failure may be vacuous"
    )
    assert "gap signal" in gv, (
        "gate_validity must name a passing run without prior failure as a gap signal"
    )


def test_derivation_discipline_content():
    assert "Gap-locality" in GROUND_PARTS["derivation_discipline"]


def test_upward_correction_requires_observation_before_loop():
    dd = GROUND_PARTS["derivation_discipline"]
    assert "before correcting" in dd, (
        "derivation_discipline must require emitting the observation before correcting any higher rung"
    )
    assert "observation record is invalid" in dd, (
        "derivation_discipline must state that corrections without an observation record are invalid"
    )


def test_reconciliation_content():
    assert "Intent precedes its representations" in GROUND_PARTS["reconciliation_and_completion"]
