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
    """P2 one artifact per type must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "artifact type" in core.lower() or "one artifact" in core.lower(), (
        "Generalized protocol must preserve artifact type discipline"
    )


def test_generalized_protocol_preserves_observable_evidence():
    """P3 observable evidence must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "evidence" in core.lower() or "external" in core.lower(), (
        "Generalized protocol must preserve observable evidence requirement"
    )


def test_generalized_protocol_preserves_derivation_chain():
    """P4 derivation chain must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "derivation" in core.lower() or "cite" in core.lower(), (
        "Generalized protocol must preserve derivation chain"
    )


def test_generalized_protocol_preserves_gap_driven_iteration():
    """P5 gap-driven iteration must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "gap" in core.lower() and (
        "challenge" in core.lower() or "refine" in core.lower()
    ), "Generalized protocol must preserve gap-driven iteration"


def test_generalized_protocol_is_domain_independent():
    """Protocol must be domain-independent."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "domain" in core.lower() or "software" in core.lower(), (
        "Generalized protocol must mention domain independence"
    )


def test_generalized_protocol_has_seven_rungs():
    """Protocol must have the 7-rung ladder."""
    core = GROUND_PARTS_MINIMAL["core"]
    rung_count = core.lower().count("rung")
    assert rung_count >= 7, (
        f"Generalized protocol must define 7 rungs, found {rung_count}"
    )
