"""Tests for the falsify token definition in axisConfig.py.

These tests assert the presence of specific key phrases in the falsify definition:
- Dimension A: allow-list clause for persistent artifacts (Gap 1)
- Dimension B: revert-run-restore clause for the retroactive case (Gap 2+3)

Each test FAILS against the old definition (which uses a deny-list clause and a
counterfactual retrospective check) and PASSES after the new definition is applied.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def test_falsify_allow_list_clause():
    """Dimension A: executor invocation must name the governed subject (via layer gate)."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the governed symbol name must appear in the executor invocation for (g)" in defn


def test_falsify_retroactive_clause():
    """Dimension B: universal (g) requirement covers the retroactive case — observed FAIL before every implementation action."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(g) is required for every action that modifies the implementation" in defn


def test_falsify_separation_rule():
    """Dim 3: (a)+(c) separation rule within (g) — closes C2."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(a) is not separated from (c) in (g) by any line naming a different governed behavior identifier" in defn


def test_falsify_creation_step_string_absence():
    """Dim 1: creation-step exception gated on (c) string absence/presence."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(c) is absent before the action and present after it" in defn


def test_falsify_symbol_substring():
    """Dim 4: (d) must appear as a substring in the symbol name — closes Gap 2."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "which must appear as a substring in the name of the symbol added or modified" in defn


def test_falsify_old_file_nonexistence_clause_absent():
    """Dim 2: old file-nonexistence proxy condition must be gone."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "does not appear as the target of any Write or Edit tool call at any earlier position in the transcript" not in defn


def test_falsify_derivation_block_label():
    """D1: derivation block label 'Falsify derivation:' must appear in definition."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "Falsify derivation:" in defn


def test_falsify_execution_layer_agnostic():
    """D2: layer classification derived from test body structure; no hardcoded taxonomy."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the layer classification" in defn
    assert "one of: unit, integration, end-to-end, or static-content" not in defn


def test_falsify_executor_agnostic():
    """D3: executor constraint requires output only producible by exercising behavior; no software deny-list."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the executor must produce output that could only exist if the governed behavior was exercised" in defn
    assert "grep, cat, head, tail, sed, awk, and find" not in defn


def test_falsify_layer_gate():
    """D4: layer gate clause must be explicit — derives from (e) unit/integration binary."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "Layer gate: if (e) is 'unit', the governed symbol name must appear in the executor invocation for (g)" in defn


def test_falsify_domain_agnostic_layer():
    """DA-D1: layer derived from test body structure; no hardcoded software taxonomy."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the layer classification" in defn
    assert "one of: unit, integration, end-to-end, or static-content" not in defn


def test_falsify_domain_agnostic_executor():
    """DA-D2: executor constraint uses 'executed-artifact result'; no tool-call software deny-list."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "executed-artifact result" in defn
    assert "grep, cat, head, tail, sed, awk, and find" not in defn


def test_falsify_domain_agnostic_subject():
    """DA-D3: layer gate names governed symbol in executor invocation; no file-path clause."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "executor invocation for (g)" in defn
    assert "the tool call names a file whose path appears as the target of a prior Write, Edit, or tool-executed directory-listing result" not in defn
