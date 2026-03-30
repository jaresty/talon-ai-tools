"""Test: ground prompt includes intention logging requirement.

This test verifies that the ground protocol requires logging the specific
assertion target and evidence before making file writes.

ADR-0218: Collapsed formulation - targets one assertion per file write,
observes it red before implementing, logs intention, and verifies no other
assertions flip unexpectedly.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.groundPrompt import build_ground_prompt


def test_ground_prompt_requires_intention_logging():
    """Ground prompt must require logging intention before file writes.

    The requirement is:
    1. Before making changes: specify which assertion we're targeting, show evidence it's red
    2. After the change: verify it's green, ensure no other assertions flipped
    """
    prompt = build_ground_prompt()

    # Must mention targeting one specific assertion per file write
    assert (
        "one specific assertion" in prompt.lower() or "target one" in prompt.lower()
    ), "Ground prompt must mention targeting one specific assertion per file write"

    # Must mention observing red/failing before implementing
    assert "observe" in prompt.lower() and (
        "red" in prompt.lower() or "failing" in prompt.lower()
    ), "Ground prompt must mention observing red/failing state before implementing"

    # Must mention logging intention or including observation in the log
    assert ("log" in prompt.lower() and "intention" in prompt.lower()) or (
        "include" in prompt.lower() and "observation" in prompt.lower()
    ), (
        "Ground prompt must mention logging intention or including observation before file write"
    )

    # Must mention checking that more than one assertion didn't flip
    assert (
        "more than that" in prompt.lower()
        or "more than one" in prompt.lower()
        or "no other" in prompt.lower()
    ), "Ground prompt must mention checking that no other assertions flip unexpectedly"


def test_ground_prompt_requires_specific_assertion_targeting():
    """Ground prompt must require targeting specific assertion, not broad changes."""
    prompt = build_ground_prompt()

    # Must mention targeting one specific assertion
    assert (
        "one specific assertion" in prompt.lower()
        or "target one specific" in prompt.lower()
    ), "Ground prompt must mention targeting one specific assertion per change"


def test_ground_prompt_intention_logging_applies_to_implementation():
    """Ground prompt must clarify this applies to implementation, not test code."""
    prompt = build_ground_prompt()

    # Must clarify implementation code is subject to this requirement
    assert "implementation" in prompt.lower() and "test" in prompt.lower(), (
        "Ground prompt must clarify that intention logging applies to implementation code, not tests"
    )
