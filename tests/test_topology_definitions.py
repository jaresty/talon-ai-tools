import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def test_topology_definitions_exist():
    assert "topology" in AXIS_KEY_TO_VALUE
    tokens = AXIS_KEY_TO_VALUE["topology"]
    assert set(tokens.keys()) == {"witness", "audit", "blind", "relay", "solo", "live"}


def test_topology_definitions_no_intent_qualifiers():
    intent_qualifiers = {"important", "major", "key", "sufficient", "essential", "structurally"}
    tokens = AXIS_KEY_TO_VALUE["topology"]
    for token, definition in tokens.items():
        words = set(definition.lower().split())
        found = intent_qualifiers & words
        assert not found, (
            f"topology/{token} contains intent-qualifier word(s) {found!r} "
            f"that require evaluator judgment to assess compliance"
        )
