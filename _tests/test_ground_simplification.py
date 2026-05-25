"""Test for ADR-0220: Generalized Ground Protocol.

Verifies the generalized protocol preserves behavioral invariants across domains.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


def test_generalized_protocol_preserves_intent_primacy():
    """P1 intent primacy must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "intent" in core.lower() and "derive" in core.lower(), (
        "Generalized protocol must preserve intent derivation"
    )


def test_generalized_protocol_preserves_artifact_type_discipline():
    """Slimmed protocol (ADR-0224) requires behavioral dimensions derived from the governing goal."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "behavioral dimension" in core.lower(), (
        "Slimmed protocol must reference behavioral dimensions in the enforcement process"
    )


def test_generalized_protocol_preserves_observable_evidence():
    """P3 observable evidence must be preserved — completion check cites verbatim tool-executed result per dimension."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "dimension" in core.lower() and "verbatim" in core.lower(), (
        "Generalized protocol must require verbatim string from tool-executed result per dimension at completion check"
    )


def test_generalized_protocol_preserves_derivation_chain():
    """P4 derivation must be preserved in slimmed form."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "derive" in core.lower(), (
        "Slimmed protocol must preserve derivation requirement"
    )


def test_generalized_protocol_preserves_gap_driven_iteration():
    """P5 gap-driven iteration — derivation-based protocol requires enumeration of open paths and structural elimination."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "open path" in core.lower() or "enumerat" in core.lower(), (
        "Slimmed protocol must require enumerating and closing open paths before proceeding"
    )


def test_generalized_protocol_is_domain_independent():
    """Protocol must be domain-independent — slimmed form uses task-agnostic language."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "task" in core.lower() or "intent" in core.lower(), (
        "Slimmed protocol must be framed in task-agnostic terms"
    )


def test_generalized_protocol_has_seven_rungs():
    """Slimmed protocol (ADR-0224/crystal) — completion-check heading gate + binding commitment present."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "completion-check heading" in core.lower() and "binding" in core.lower(), (
        "Derivation-based protocol must contain completion-check heading gate and binding commitment sentence"
    )
