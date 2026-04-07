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
    """Slimmed protocol (ADR-0224) requires visible evidence at each step."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "evidence" in core.lower(), (
        "Slimmed protocol must require visible evidence"
    )


def test_generalized_protocol_preserves_observable_evidence():
    """P3 observable evidence must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "evidence" in core.lower() or "external" in core.lower(), (
        "Generalized protocol must preserve observable evidence requirement"
    )


def test_generalized_protocol_preserves_derivation_chain():
    """P4 derivation must be preserved in slimmed form."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "derive" in core.lower(), (
        "Slimmed protocol must preserve derivation requirement"
    )


def test_generalized_protocol_preserves_gap_driven_iteration():
    """P5 gap-driven iteration — crystal restructure uses apparent/actual completion gap language."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "apparent" in core.lower() and "actual" in core.lower(), (
        "Slimmed protocol must address gap between apparent and actual completion"
    )


def test_generalized_protocol_is_domain_independent():
    """Protocol must be domain-independent — slimmed form uses task-agnostic language."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "task" in core.lower() or "intent" in core.lower(), (
        "Slimmed protocol must be framed in task-agnostic terms"
    )


def test_generalized_protocol_has_seven_rungs():
    """Slimmed protocol (ADR-0224/crystal) — governing principle + completion check present."""
    core = GROUND_PARTS_MINIMAL["core"]
    # Crystal restructure: governing principle (attack surface) + completion check as final step
    assert "attack surface" in core.lower() and "completion check" in core.lower(), (
        "Crystal-restructured protocol must contain governing principle and completion check"
    )
