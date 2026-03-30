"""Test: ground prompt includes intention logging sentinel and perturb guidance for backfill.

ADR-0218: Intention logging sentinel for implementation file writes.
ADR-0242: Perturb guidance for backfill cases where tests can't be seen red.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.groundPrompt import SENTINEL_TEMPLATES, _SENTINEL_GATES, build_ground_prompt


def test_intention_logging_sentinel_exists():
    """Ground prompt must include a sentinel for intention logging before implementation file writes.

    The sentinel should:
    1. Log which assertion is being targeted
    2. Include the red observation (evidence it currently fails)
    3. Be emitted BEFORE the file write
    """
    prompt = build_ground_prompt()

    # Must have a sentinel specifically for logging intention
    # Should mention logging intention + red observation before file write
    assert (
        "log" in prompt.lower()
        and ("intention" in prompt.lower() or "target" in prompt.lower())
        and "red" in prompt.lower()
    ), (
        "Ground prompt must have a sentinel that logs intention + red observation before file write"
    )


def test_perturb_guidance_for_backfill():
    """Ground prompt must include perturb guidance for backfill cases.

    When backfilling tests for code that already works, we can't see tests red.
    The solution is to perturb (break) the implementation to see the test fail,
    then fix it. This should be explicitly stated.
    """
    prompt = build_ground_prompt()

    # Must mention perturb for backfill case
    assert "perturb" in prompt.lower(), (
        "Ground prompt must mention perturb for backfill cases where tests can't be seen red"
    )

    # Must connect perturb to the backfill scenario
    assert (
        "backfill" in prompt.lower()
        or "already" in prompt.lower()
        or "existing" in prompt.lower()
    ) and "test" in prompt.lower(), (
        "Ground prompt must connect perturb to the backfill scenario (existing code, can't see tests red)"
    )


def test_intent_achieved_sentinel_exists():
    """Ground prompt must include a sentinel for demonstrating intent achieved after implementation.

    After each file write, we need to show that the validation passes (green state).
    This demonstrates that the targeted assertion now passes. This is distinct from
    impl_intent which logs BEFORE the write - we need a SEPARATE sentinel for AFTER.
    """
    # Must have a distinct sentinel for showing green state AFTER file write
    assert "impl_intent_achieved" in SENTINEL_TEMPLATES, (
        "Ground prompt must have a separate impl_intent_achieved sentinel to show green state after file write"
    )


def test_impl_intent_requires_test_assertion():
    """impl_intent must require evidence from an actual test assertion, not just any failure.

    The evidence must come from running the test/validation file, not from arbitrary tool output.
    """
    gate = _SENTINEL_GATES.get("impl_intent", "")

    # Must explicitly require test assertion - not just "assertion" generically
    assert "test assertion" in gate.lower(), (
        "impl_intent gate must explicitly require evidence from a test assertion (not generic assertion)"
    )
