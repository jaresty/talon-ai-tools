"""
ADR-0212: EV import-check gate — step (2b) blocked until import check passes.

Criterion: The EV rung description requires the import check to pass before
step (2b) assertion bodies may be written; advancing to (2b) while the import
check is failing is named a protocol violation.
"""

import pytest
from lib.groundPrompt import build_ground_prompt


PROMPT = build_ground_prompt()


def test_import_gate_pass_required_before_2b():
    """The prompt must state the import check must pass before (2b) begins."""
    # ADR-0214: phrasing changed to 'advancing to (2b) while the import check is failing is a protocol violation'
    assert (
        "must pass before step (2b)" in PROMPT
        or "import check must pass before" in PROMPT
        or "advancing to (2b) while the import check is failing" in PROMPT
    )


def test_advancing_to_2b_with_failing_import_is_violation():
    """Advancing to (2b) while import check fails must be named a protocol violation."""
    assert "advancing to (2b) while the import check is failing is a protocol violation" in PROMPT
