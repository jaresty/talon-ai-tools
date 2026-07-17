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
    """P1 governing goal derivation must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "governing goal" in core.lower() and "derive" in core.lower(), (
        "Generalized protocol must preserve governing goal derivation"
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
    """Protocol must be domain-independent — slimmed form uses task-agnostic exit strings."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "§ blocked" in core or "§ awaiting" in core or "§ no-next-action" in core, (
        "Slimmed protocol must be framed in task-agnostic terms (§ blocked / §aawaiting / § no-next-action exit strings)"
    )


def test_generalized_protocol_has_seven_rungs():
    """Slimmed protocol (ADR-0224/crystal) — completion check heading gate + permit-sentinel ordering gate present."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "## Completion check" in core and "must not appear before '§ implementation permitted'" in core, (
        "Derivation-based protocol must gate ## Completion check after § implementation permitted sentinel"
    )


def test_ground_gate_D2_dimension_kind_constraint():
    """D2: §2 dimensions must name a property of the response, not an artifact, state, or fix description."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "property of the response" in core, (
        "§2 must require each dimension to name a property of the response"
    )
    assert "not an artifact" in core or "not an artifact, state" in core, (
        "§2 must explicitly exclude artifact/state/fix-description as valid dimensions"
    )


def test_ground_gate_D2_dimension_count_constraint():
    """D2: §2 must require at least two dimensions."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "at least two" in core, (
        "§2 must require at least two dimensions to be listed"
    )


def test_ground_gate_D2_dimension_independence_constraint():
    """D2: §2 dimensions must be independently violatable."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "satisfy it while failing" in core or "satisfy" in core and "failing at least one other" in core, (
        "§2 must require each dimension to be independently satisfiable (satisfiable while others fail)"
    )
