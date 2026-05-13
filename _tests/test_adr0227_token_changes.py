"""Tests for ADR-0227 non-deferred token changes.

Behaviors under test:
1. ground: evidence quality — criterion that has only ever passed is not evidence
2. ground: termination trigger — completion check fires when governing artifact cycle exhausted
3. atomic: canonical term "governing output" used instead of "failure message"
4. chain: canonical term "governing output" used for implementation step predecessor
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt
from lib.axisConfig import AXIS_KEY_TO_VALUE


def _falsify() -> str:
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def _ground() -> str:
    return build_ground_prompt()


def _atomic() -> str:
    return AXIS_KEY_TO_VALUE["method"]["atomic"]


def _chain() -> str:
    return AXIS_KEY_TO_VALUE["method"]["chain"]


# --- ground: evidence quality (Decision 3) ---

def test_falsify_evidence_quality_requires_criterion_to_have_failed():
    """falsify must state that a criterion which has only ever passed provides no coverage guarantee.

    ADR-0227 Decision 3: the coverage guarantee clause belongs in falsify (not ground)
    because it is about falsifiability — a passing artifact is not evidence of enforcement.
    """
    text = _falsify()
    assert "only ever passed" in text or "coverage guarantee" in text or "FAIL tool result" in text, (
        "falsify must require a prior FAIL result demonstrating absence detection "
        "(ADR-0227 Decision 3)"
    )


# --- ground: termination trigger (Decision 4) ---

def test_ground_states_completion_check_trigger_condition():
    """ground must name when the completion check fires relative to a governing artifact cycle.

    ADR-0227 Decision 4: ground should state that the completion check fires
    when the governing artifact cycle reports no remaining failures.
    """
    text = _ground()
    assert (
        "governing artifact" in text and
        ("no remaining failures" in text or "reports no failures" in text or
         "cycle" in text and "completion check" in text)
    ), (
        "ground must state the trigger condition for the completion check "
        "relative to a governing artifact cycle (ADR-0227 Decision 4)"
    )


# --- atomic: governing output vocabulary (Decision 5) ---

def test_atomic_uses_governing_output_term():
    """atomic must use 'governing output' as the canonical term.

    ADR-0227 Decision 5: 'failure message' → 'governing output' in atomic.
    """
    text = _atomic()
    assert "governing output" in text, (
        "atomic must use 'governing output' as the canonical term for the "
        "artifact output that opens the current implementation step (ADR-0227 Decision 5)"
    )


def test_atomic_defines_governing_output_on_first_use():
    """atomic must define 'governing output' on first use.

    ADR-0227 Decision 5: governing output is defined as 'the first reported
    failure from the governing artifact'.
    """
    text = _atomic()
    assert "governing output" in text and (
        "first reported failure" in text or
        "reported failure from the governing artifact" in text or
        "first failure from a tool-executed run result" in text or
        "first failure signal from a tool-executed run result" in text
    ), (
        "atomic must define 'governing output' on first use as the first "
        "failure from the governing artifact (ADR-0227 Decision 5)"
    )


# --- chain: governing output vocabulary (Decision 5) ---

def test_chain_uses_governing_output_for_implementation_step_predecessor():
    """chain must use 'governing output' for the implementation step predecessor.

    ADR-0227 Decision 5: chain uses 'governing output' for the artifact output
    that serves as the predecessor for implementation steps (when gate is present).
    """
    text = _chain()
    assert "governing output" in text, (
        "chain must use 'governing output' for the implementation step predecessor "
        "artifact (ADR-0227 Decision 5)"
    )
