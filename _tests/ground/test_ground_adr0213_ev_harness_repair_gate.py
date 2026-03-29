"""
ADR-0213: EV harness error at step 3 — import failure must re-enter at step (2a).

Criterion: When a harness error at EV step 3 is an import failure, the repair
must re-enter at step (2a) of the current EV cycle; a freeform stub write that
does not go through the import-check gate is a protocol violation.
"""

import pytest
from lib.groundPrompt import build_ground_prompt


PROMPT = build_ground_prompt()


def test_import_failure_routes_to_step_2a():
    """Import failure at step 3 must route back to step (2a), not allow freeform repair."""
    assert "import failure" in PROMPT and "re-enter" in PROMPT or \
           "import failure at" in PROMPT or \
           "re-enter at step (2a)" in PROMPT


def test_freeform_stub_at_step_3_is_violation():
    """A freeform stub write at step 3 bypassing the import-check gate must be a protocol violation."""
    assert "freeform stub" in PROMPT or "bypassing the import-check gate" in PROMPT or \
           "without going through" in PROMPT
