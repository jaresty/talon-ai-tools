"""Test for ADR-0219: Ground Protocol Simplification.

Verifies the simplified P1-P6 formulation preserves behavioral invariants.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


def test_collapsed_protocol_preserves_intent_primacy():
    """P1 intent primacy must be preserved in collapsed version."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "intent primacy" in core.lower() or "intent exists" in core.lower(), (
        "Collapsed protocol must preserve intent primacy"
    )


def test_collapsed_protocol_preserves_artifact_type_discipline():
    """P2 one artifact per type must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "artifact type" in core.lower() and "one rung" in core.lower(), (
        "Collapsed protocol must preserve artifact type discipline"
    )


def test_collapsed_protocol_preserves_observable_evidence():
    """P3 observable evidence must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "observable evidence" in core.lower() or "tool execution" in core.lower(), (
        "Collapsed protocol must preserve observable evidence requirement"
    )


def test_collapsed_protocol_preserves_file_edit_protocol():
    """P4 file edit protocol must be preserved including EV/EI distinction."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "file edit" in core.lower() and "protocol" in core.lower(), (
        "Collapsed protocol must preserve file edit protocol"
    )


def test_collapsed_protocol_preserves_derivation_chain():
    """P5 derivation chain must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "derivation" in core.lower() or "derive" in core.lower(), (
        "Collapsed protocol must preserve derivation chain"
    )


def test_collapsed_protocol_preserves_thread_sequencing():
    """P6 thread sequencing must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "thread" in core.lower() and "sequenc" in core.lower(), (
        "Collapsed protocol must preserve thread sequencing"
    )


def test_rung_validity_test_preserved():
    """Rung validity test must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "rung is valid" in core.lower() or "human reviewer" in core.lower(), (
        "Collapsed protocol must preserve rung validity test"
    )


def test_standard_ladder_preserved():
    """Standard ladder (prose -> criteria -> etc) must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "prose" in core.lower() and "criteria" in core.lower(), (
        "Collapsed protocol must preserve standard ladder"
    )


def test_ev_ei_distinction_preserved():
    """EV rung (validation files) vs EI rung (implementation files) distinction must be preserved."""
    core = GROUND_PARTS_MINIMAL["core"]
    assert "validation" in core.lower() and "implementation" in core.lower(), (
        "Collapsed protocol must preserve EV/EI distinction"
    )
