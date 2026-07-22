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
    """Dimension A: named governing artifact identifier must appear as literal string in executor invocation."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "whose file path — the path passed as an argument to the executor invocation, not a package name or directory — appears as a literal string in the named executor invocation" in defn


def test_falsify_retroactive_clause():
    """Dimension B: universal (g) requirement covers the retroactive case — observed FAIL before every governed artifact-producing action."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(g) is required for every governed artifact-producing action in the current session" in defn


def test_falsify_separation_rule():
    """Dim 3: (a)+(c) separation rule within (g) — tightened to name (c) explicitly."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "whose content contains (c) for a different governed behavior" in defn


def test_falsify_creation_step_string_absence():
    """Dim 1: creation-step exception gated on (c) string absence/presence."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(c) is absent before the action and present after it" in defn


def test_falsify_symbol_substring():
    """Dim 4: (d) governed symbol must appear as a substring of the failure line in (g)."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "which must appear as a substring of the failure line in (g)" in defn


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
    """D3: executor constraint requires output only producible by governed assertion reaching execution; no software deny-list."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the executor must produce output that could only exist if the governed assertion reached execution" in defn
    assert "grep, cat, head, tail, sed, awk, and find" not in defn


def test_falsify_layer_gate():
    """D4: layer classification derives from governed symbol presence in test body."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "if the governed symbol name appears as a token in a call expression in the test body — where the call expression is not nested inside another call expression that names a different symbol — the layer is 'unit'" in defn


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
    """DA-D3: named executor invocation required; no file-path clause."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "named executor invocation" in defn
    assert "the tool call names a file whose path appears as the target of a prior Write, Edit, or tool-executed directory-listing result" not in defn


def test_falsify_tool_call_result_block():
    """Gap close: (g) must be an executor result block, not authored prose."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the content of an executor result block appearing in the transcript" in defn


def test_falsify_assertion_body_substring():
    """Gap close G2/D2: failure line must contain (d) as substring AND include assertion body substring."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the failure line contains (d) as a substring" in defn
    assert "failure line whose content includes a substring from the governed assertion call expression" in defn


def test_falsify_separation_constraint_tightened():
    """Gap close: separation constraint names (c) explicitly, not 'governing behavior identifier'."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "whose content contains (c) for a different governed behavior" in defn


def test_falsify_creation_step_per_governed_behavior():
    """Gap close D1: creation-step exception is per governed behavior, not per file-write."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "per governed behavior" in defn


def test_falsify_creation_step_confirmation_run_passes():
    """Gap close C2: creation-step confirmation run must produce (c) and not (a)."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "and not (a)" in defn


def test_falsify_perturbation_layer_gate():
    """Gap close C1: perturbation result must appear before revert action."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the perturbation result must appear before the revert action" in defn


def test_falsify_revert_verbatim_quote():
    """Gap close D3: pre-perturbation run result must be quoted verbatim before revert."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "quoted verbatim" in defn


# Domain-agnostic rewrite tests — FAIL against old definition, PASS after new definition applied.

def test_falsify_governed_artifact_producing_action_defined():
    """Scope: 'governed artifact-producing action' must be defined in the definition."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "governed artifact-producing action" in defn


def test_falsify_named_governing_artifact():
    """G4: 'named governing artifact' replaces 'named-file artifact'."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "named governing artifact" in defn


def test_falsify_named_executor():
    """G2/CL2: 'named executor' replaces 'executor command' throughout."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "named executor" in defn


def test_falsify_does_not_persist_beyond_session():
    """Scope: session-persistence criterion makes scope boundary explicit."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "does not persist beyond the current session" in defn


def test_falsify_no_named_executor_excludes_subject():
    """Scope: absence of named executor is an explicit exclusion criterion."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "no named executor exists" in defn


def test_falsify_artifact_identifier_must_differ():
    """CL1: artifact identifier separation replaces file-path separation."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "Artifact identifier must differ" in defn


def test_falsify_every_governed_artifact_producing_action():
    """D1: 'every governed artifact-producing action' replaces 'every action that modifies the implementation'."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "every governed artifact-producing action" in defn
    assert "every action that modifies the implementation" not in defn


def test_falsify_unguarded_behaviors_require_separate_fail():
    """D2: closing (g) for one behavior does not require covering unguarded behaviors — each requires its own governing FAIL."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "unguarded behaviors require separate governing" in defn


def test_falsify_rationale_opener_tool_result_block_scoped():
    """Rationale opener: FAIL history must be scoped to a tool-result block in this transcript, not assertion-satisfiable."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "tool-result block in this transcript" in defn


def test_falsify_rationale_opener_starts_with_the_response():
    """Rationale opener: definition must begin with 'The response' per token convention."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert defn.startswith("The response")


def test_falsify_gap_artifact_label_present():
    """Artifact gap: Gap artifact: label must be named as the required block when (g) is unavailable."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "Gap artifact:" in defn


def test_falsify_g_unavailable_is_incomplete():
    """Artifact gap: (g) observed FAIL result: unavailable must be named as the incomplete-derivation trigger."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(g) observed FAIL result: unavailable" in defn


def test_falsify_gap_artifact_gates_file_modifying_calls():
    """Artifact gap: no file-modifying tool call may appear before the tool call that produces the named artifact."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "no file-modifying tool call may appear before the tool call that produces the named artifact" in defn


def test_falsify_serialization_gate():
    """(f2) serialization gate clause must appear in the falsify definition."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(f2) serialization gate" in defn


def test_falsify_serialization_gate_structural_rule():
    """Serialization gate uses structural rule, not deny-list — 'string/byte/text representation' must appear."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "string/byte/text representation" in defn
