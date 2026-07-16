"""Tests for ground token definition — assert new structural clauses present, old underenforced clauses absent."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.groundPrompt import build_ground_prompt


def _ground_def() -> str:
    return build_ground_prompt()


def test_ground_definition_contains_implementation_permitted():
    """New definition requires gate string '§ implementation permitted' — absent from old definition.
    Closes D1: gate was prose instruction, not a transcript-inspectable string."""
    assert "§ implementation permitted" in _ground_def()


def test_ground_definition_contains_enumeration_complete():
    """New definition requires gate string '§5 enumeration complete' — absent from old definition.
    Closes CL1/D3: drops weaker 'at least one per section' floor, replaces with gate string."""
    assert "§5 enumeration complete" in _ground_def()


def test_ground_definition_contains_markdown_heading_form():
    """New definition specifies heading form as markdown '## ' — absent from old definition.
    Closes G1: 'literal heading' was undefined, allowing inline bold as escape."""
    assert "markdown" in _ground_def()


def test_ground_definition_contains_transcript_inspectable():
    """New definition names root criterion as 'transcript-inspectable' — absent from old definition.
    Closes the root criterion gap: compliance must be verifiable without intent assessment."""
    assert "transcript-inspectable" in _ground_def()


# Gate string tests — each FAILS against old definition, PASSES after new definition is implemented.

def test_ground_gate_D2_nonsoft_heading():
    """D2: non-software §0 satisfied by '§0 Path B: [scenario]' sentinel (not ## heading)."""
    assert "§0 Path B:" in _ground_def()


def test_ground_gate_D3_goal_before_tool_result():
    """D3: governing goal must not appear before §0 observed — stronger than old tool-result check."""
    assert "must not appear before '§0 observed'" in _ground_def()


def test_ground_gate_D4_dimensions_ordering():
    """D4: behavioral dimensions heading must not appear before §1 goal derived in transcript."""
    assert "must not appear before '§1b candidates'" in _ground_def()


def test_ground_gate_G1_enforcement_before_edit():
    """G1: enforcement sequence heading must appear before first file-modifying tool call regardless of § implementation permitted."""
    assert "must appear before the first file-modifying tool call regardless of whether" in _ground_def()


def test_ground_gate_G2_completion_ordering():
    """G2: completion check heading must not appear before enforcement sequence in transcript."""
    assert "'## Completion check' must not appear before '## Enforcement sequence'" in _ground_def()


def test_ground_gate_C2_yield_gate():
    """C2: yield gate — any post-permitted turn yielding to user must contain completion check first."""
    assert "after '§ implementation permitted' has appeared in the transcript" in _ground_def()
    assert "must contain '## Completion check' before that question or closing text" in _ground_def()


def test_ground_gate_C2b_citation_post_permitted():
    """C2b: §4 citations must reference tool-result blocks produced after § implementation permitted."""
    assert "produced after '§ implementation permitted'" in _ground_def()


def test_ground_gate_C2c_prose_citation_fallback():
    """C2c: when no tool results exist after § implementation permitted, cite response text directly."""
    assert "substring of the response text produced in this turn" in _ground_def()


def test_ground_gate_CL2_completion_check_tool_result():
    """CL2: §4 coverage verified sentinel — write when every covered dimension cites a substring."""
    assert "§4 coverage verified" in _ground_def()
    assert "when every covered dimension cites such a substring, write '§4 coverage verified'" in _ground_def()


# §1 means-test clause tests — each FAILS against old definition, PASSES after new §1 is implemented.

def test_ground_gate_S1_means_test_sentence_form():
    """S1: §1 requires means-test sentence form immediately below heading."""
    assert "The goal [text] could be achieved by:" in _ground_def()


def test_ground_gate_S1_hypothetical_fallback():
    """S1: §1 requires [hypothetical] fallback when no concrete alternative can be named."""
    assert "[hypothetical]" in _ground_def()


def test_ground_gate_S1_sentinel():
    """S1: sentinel string '§1 goal derived' must appear in definition."""
    assert "§1 goal derived" in _ground_def()


def test_ground_gate_S1_behavioral_dimensions_gate():
    """S1: ## Behavioral dimensions must not appear before §1 goal derived in transcript."""
    assert "must not appear before '§1b candidates'" in _ground_def()


def test_ground_gate_S1_selection_criterion_revised():
    """S1: tie-breaking criterion replaced — now selects goal whose means-test names more concrete alternative."""
    assert "more concrete alternative than those listed in §0" in _ground_def()


# §2 observable-field clause tests — each FAILS against old definition, PASSES after new §2 is implemented.

def test_ground_gate_S2_observable_field_tag():
    """S2: each dimension must end with [observable: <string>] tag."""
    assert "[observable:" in _ground_def()


def test_ground_gate_S2_observable_prose_path():
    """S2: [observable: prose] is the correct tag when no tool-result blocks appear above §2."""
    assert "[observable: prose]" in _ground_def()


def test_ground_gate_S2_sentinel():
    """S2: sentinel string '§2 dimensions closed' must appear in definition."""
    assert "§2 dimensions closed" in _ground_def()


def test_ground_gate_S2_enforcement_sequence_gate():
    """S2: ## Enforcement sequence must not appear before §2 dimensions closed in transcript."""
    assert "must not appear before '§2 dimensions closed'" in _ground_def()


def test_ground_gate_S4_sentinel():
    """S4: sentinel string '§4 coverage verified' must appear in definition."""
    assert "§4 coverage verified" in _ground_def()


def test_ground_gate_S4_path_enumeration_gate():
    """S4: ## Path enumeration must not appear before ## Enforcement sequence in transcript."""
    assert "must not appear before '## Enforcement sequence'" in _ground_def()


# §0 observed sentinel tests — FAIL against current definition, PASS after implementation.

def test_ground_gate_S0_observed_sentinel():
    """S0: sentinel string '§0 observed' must appear in definition."""
    assert "§0 observed" in _ground_def()


def test_ground_gate_S0_observed_conditioned_on_artifact():
    """S0: §0 observed must not appear before tool-result block or ## heading above it."""
    assert "must not appear before" in _ground_def() and "§0 observed" in _ground_def()
    assert "§0 observed" in _ground_def()


def test_ground_gate_S1_governing_goal_requires_S0():
    """S1: ## Governing goal must not appear before §0 observed in transcript."""
    assert "must not appear before '§0 observed'" in _ground_def()


def test_ground_gate_S1_text_verbatim_in_tool_result():
    """S1: [text] must appear verbatim as substring of §0 tool-result block."""
    assert "[text]` must appear verbatim as a substring of the §0 tool-result block" in _ground_def()


# Derivation framing tests — FAIL against current definition, PASS after implementation.

def test_ground_derivation_no_fixed_step_count():
    """Derivation framing: no rung has a fixed step count."""
    assert "no rung has a fixed step count" in _ground_def()


def test_ground_derivation_unbounded():
    """Derivation framing: §2 derivation is explicitly unbounded."""
    assert "unbounded" in _ground_def()


def test_ground_gate_S2_reader_uncertainty_replaces_implied():
    """S2: dimensions must trace to §1a decomposition or §1b candidates items."""
    assert "§1b candidates list" in _ground_def()


# Two-path §0 structure tests — FAIL against current definition, PASS after implementation.

def test_ground_attractor_tool_executed_event():
    """Attractor: rung satisfied only by tool-executed event — inference/prediction do not satisfy."""
    assert "inference, prediction, and prior knowledge do not satisfy" in _ground_def()


def test_ground_gate_path_a_classification_criterion():
    """Path A/B: explicit classification criterion — behavioral artifact triggers Path A."""
    assert "executes the subject system and returns its live output" in _ground_def()


def test_ground_gate_S0_path_b_sentinel():
    """Path B §0: 'S0 Path B:' literal sentinel satisfies §0 for non-software subjects."""
    assert "§0 Path B:" in _ground_def()


def test_ground_gate_S1_derived_text_marker():
    """Path B §1: '[derived: text]' marker for non-verbatim goal derivation."""
    assert "[derived: text]" in _ground_def()


def test_ground_gate_deprecated_heading_path_removed():
    """Deprecated: ## heading path for non-software §0 must be removed."""
    assert "an observation not under such a heading does not satisfy §0" not in _ground_def()


def test_ground_completion_check_requires_implementation_permitted():
    """§4: ## Completion check must not appear before § implementation permitted — closes early-exit escape."""
    assert "must not appear before '§ implementation permitted'" in _ground_def()


def test_ground_sentinels_scoped_to_current_invocation():
    """Sentinels from prior ground invocations must not satisfy current invocation rungs."""
    assert "most recent '=== TOKENS'" in _ground_def()


def test_ground_implementation_permitted_same_turn():
    """§ implementation permitted must anchor tool call to same response turn — cross-turn escape closed."""
    assert "user message appearing between" in _ground_def()


def test_ground_implementation_permitted_immediacy():
    """§ implementation permitted must appear immediately before the (i) line — five-line block composition."""
    assert "immediately before the `(i)` line" in _ground_def()
    assert "each file-modifying tool call" in _ground_def()


def test_ground_path_enumeration_gate_enforcement_sequence():
    """§5 must gate on ## Enforcement sequence, not §4 coverage verified — closes circular deadlock."""
    ground = _ground_def()
    assert "'## Path enumeration' must not appear before '## Enforcement sequence'" in ground, (
        "§5 gate must reference '## Enforcement sequence', not '§4 coverage verified' — "
        "the old gate created a circular deadlock"
    )
    assert "'## Path enumeration' must not appear before '§4 coverage verified'" not in ground, (
        "old deadlock gate string must be absent from ground definition"
    )


def test_ground_path_enumeration_gate_axisconfig():
    """axisConfig.py ground description must also gate §5 on ## Enforcement sequence."""
    from lib.axisConfig import AXIS_KEY_TO_VALUE
    ground = AXIS_KEY_TO_VALUE["method"]["ground"]
    assert "'## Path enumeration' must not appear before '## Enforcement sequence'" in ground, (
        "axisConfig ground must gate §5 on '## Enforcement sequence', not '§4 coverage verified'"
    )
    assert "'## Path enumeration' must not appear before '§4 coverage verified'" not in ground, (
        "old deadlock gate string must be absent from axisConfig ground description"
    )
