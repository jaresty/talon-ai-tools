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
    """Dimension A: tool call must name the governed subject directly."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the tool call names the governed subject directly" in defn


def test_falsify_retroactive_clause():
    """Dimension B: definition must name the revert-run-restore path for the retroactive case."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "If implementation already exists: revert the implementation" in defn


def test_falsify_separation_rule():
    """Dim 3: (a)+(c) separation rule replaces consecutive-lines — closes C2."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(a) is not separated from (c) by any line naming a different governed behavior identifier" in defn


def test_falsify_creation_step_string_absence():
    """Dim 1: creation-step exception gated on (c) string absence/presence."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(c) is absent before the action and present after it" in defn


def test_falsify_symbol_substring():
    """Dim 4: (d) must be a literal substring of the symbol name — closes Gap 2."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "which must be a literal substring of the symbol name added or modified by the governed action" in defn


def test_falsify_old_file_nonexistence_clause_absent():
    """Dim 2: old file-nonexistence proxy condition must be gone."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "does not appear as the target of any Write or Edit tool call at any earlier position in the transcript" not in defn


def test_falsify_derivation_block_label():
    """D1: derivation block label 'Falsify derivation:' must appear in definition."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "Falsify derivation:" in defn


def test_falsify_execution_layer_agnostic():
    """D2: domain-agnostic layer description present; software taxonomy absent."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the layer at which the governed behavior manifests" in defn
    assert "one of: unit, integration, end-to-end, or static-content" not in defn


def test_falsify_executor_agnostic():
    """D3: domain-agnostic executor constraint present; software deny-list absent."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "a tool call whose output could be produced by reading or inspecting the subject at rest does not satisfy this requirement" in defn
    assert "grep, cat, head, tail, sed, awk, and find" not in defn


def test_falsify_layer_gate():
    """D4: layer gate clause must be explicit — closes G2."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "Layer gate: the executor named in (f) must operate at the layer named in (e)" in defn


def test_falsify_domain_agnostic_layer():
    """DA-D1: domain-agnostic layer description present; software taxonomy absent."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the layer at which the governed behavior manifests" in defn
    assert "one of: unit, integration, end-to-end, or static-content" not in defn


def test_falsify_domain_agnostic_executor():
    """DA-D2: domain-agnostic executor constraint present; software deny-list absent."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "a tool call whose output could be produced by reading or inspecting the subject at rest does not satisfy this requirement" in defn
    assert "grep, cat, head, tail, sed, awk, and find" not in defn


def test_falsify_domain_agnostic_subject():
    """DA-D3: domain-agnostic subject reference present; file-path clause absent."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the tool call names the governed subject directly" in defn
    assert "the tool call names a file whose path appears as the target of a prior Write, Edit, or tool-executed directory-listing result" not in defn
