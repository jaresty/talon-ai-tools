"""Tests for falsify token definition rewrite (token-rewrite sequence).

Gaps closed:
- D1: 'has been observed' replaces 'can observe' (actuality not potential)
- D3/G1: (e) unit/integration binary derived from test body, not self-declared
- G3/C1: (g) observed FAIL result required before implementation; exception is creation step only
- Domain: 'executed-artifact result' replaces 'tool call result block' (domain-agnostic)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def _falsify() -> str:
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_falsify_requires_observed_actuality_not_potential():
    """falsify opening sentence must require observed actuality, not potential observability.

    Gap D1: old definition said 'can observe the absence' (potential). New definition
    must say 'has been observed to detect the absence' (actuality).
    """
    text = _falsify()
    assert "has been observed to detect the absence" in text, (
        "falsify must require 'has been observed to detect the absence' — "
        "observed actuality, not potential observability (gap D1)"
    )


def test_falsify_derivation_block_extends_to_g():
    """falsify derivation block must cover entries (a) through (g), not just (a) through (f).

    Gap D1/new requirement: (g) is the observed FAIL result, required before any
    implementation action. The derivation block header must name (g).
    """
    text = _falsify()
    assert "(a) through (g)" in text, (
        "falsify derivation block must extend to (g) — "
        "old definition only required (a) through (f) (gap D1)"
    )


def test_falsify_uses_executed_artifact_result_not_tool_call():
    """falsify must use domain-agnostic 'executed-artifact result', not 'tool call result block'.

    Domain-scope finding: 'tool call result block' presupposes a software runtime.
    'executed-artifact result' covers any executor (test runner, proof checker, policy harness).
    """
    text = _falsify()
    assert "executed-artifact result" in text, (
        "falsify must use 'executed-artifact result' instead of 'tool call result block' "
        "to remain domain-agnostic"
    )


def test_falsify_defines_g_as_observed_fail_result():
    """falsify must define (g) as the observed FAIL result entry.

    New requirement: (g) names the verbatim FAIL excerpt that must appear in the transcript
    after writing the governing artifact and before modifying the implementation.
    """
    text = _falsify()
    assert "(g) the observed FAIL result" in text or "(g)" in text and "observed FAIL result" in text, (
        "falsify must define (g) as the observed FAIL result — "
        "verbatim excerpt required before implementation tool call"
    )


def test_falsify_e_derives_unit_integration_from_test_body():
    """falsify must derive (e) layer classification from whether symbol appears in test body.

    Gap D3/G1: old (e) was self-declared with no constraint. New (e) is a structural binary:
    'unit' if governed symbol name appears as direct call in test body; 'integration' if not.
    """
    text = _falsify()
    assert "layer is 'unit'" in text or 'layer is "unit"' in text, (
        "falsify (e) must define the 'unit' layer classification derived from test body "
        "— governed symbol name appears as direct call (gap D3/G1)"
    )
    assert "layer is 'integration'" in text or 'layer is "integration"' in text, (
        "falsify (e) must define the 'integration' layer classification derived from test body "
        "— governed symbol name does not appear in test body (gap D3/G1)"
    )


def test_falsify_import_error_exclusion():
    """falsify (g) must explicitly exclude collection-phase/import-phase error outputs.

    Gap D1/C1/D2/G1: the (a)-(c) ordering proxy is satisfied by ImportError outputs
    without the executor having reached any assertion. The new sentence closes this:
    a failure line naming only a file path, module path, or import location does not
    satisfy (g) regardless of whether (a) precedes (c).
    """
    text = _falsify()
    assert "failure line contains a substring from the governed assertion call expression" in text, (
        "falsify must require failure line to contain a substring from the governed assertion call expression "
        "— closes import-error escape route (D1/C1/D2/G1)"
    )


def test_falsify_no_assertion_substring_exclusion():
    """falsify must state the domain-agnostic negative: no assertion substring means (g) not satisfied.

    Gap D2: the allow-list clause (assertion substring required) is the closure mechanism.
    The negative form must appear explicitly so it applies across all executor domains,
    not just Python/pytest (which have 'import locations').
    """
    text = _falsify()
    assert "a failure line that contains no such substring does not satisfy (g)" in text, (
        "falsify must state 'a failure line that contains no such substring does not satisfy (g)' "
        "— domain-agnostic negative closes D2 without enumerating software-specific error types"
    )


def test_falsify_creation_step_requires_executor_run():
    """falsify creation step exception must require executor invocation against governing artifact.

    Gap D1/C1/D2/C2: the (c)-absent-before/present-after check admits implementation-only
    writes that introduce (c) without writing the governing artifact. The new clause closes
    this: after the creation step action, the executor must produce a tool-executed result
    containing (c) when invoked against the governing artifact.
    """
    text = _falsify()
    assert (
        "executor invocation against the governing artifact immediately following the action "
        "produces a tool-executed result containing (c)" in text
    ), (
        "falsify creation step must require executor invocation producing (c) in result — "
        "closes implementation-bundling escape route (D1/C1/D2/C2)"
    )
