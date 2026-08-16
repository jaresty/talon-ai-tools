"""Tests for the falsify token definition — three-gate retrospective form.

falsify is now two retrospective gates over established guards:
  Gate 1 (minimization) and Gate 3 (observed failure by perturbation),
with no forced per-property ordering and no self-declared count/correspondence
bookkeeping. The coverage-against-retained-properties gate (Gate 2) lives in the
ground+falsify composition, not in this token.

Each test asserts a property (P1..P7) of the definition string. They must FAIL
against the old six-step forward-walk definition and PASS after the redesign.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def _defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


# --- Shared framing ---

def test_falsify_rationale_opener():
    """Definition still opens with the regression-detection rationale."""
    defn = _defn()
    assert defn.startswith("The response observes each gap between intent and current state")
    assert "detect regression without human initiation" in defn


# --- P1: no inter-property ordering clause ---

def test_falsify_p1_no_forced_ordering_clause():
    """P1: the forced 'K < N' inter-property ordering clause must be gone."""
    assert "where K < N" not in _defn()


def test_falsify_p1_no_may_be_emitted_only_after():
    """P1: no clause ordering one property's cycle after another's completion."""
    assert "may be emitted only after every property" not in _defn()


def test_falsify_p1_any_order_permitted():
    """P1: test and implementation may be written in any order."""
    assert "may be written in any order" in _defn()


# --- P2: minimization gate ---

def test_falsify_p2_gate_1_minimization_present():
    """P2: Gate 1 minimization is named."""
    defn = _defn()
    assert "Gate 1" in defn
    assert "Minimization" in defn


def test_falsify_p2_overreach_proven_by_perturbation():
    """P2: overreach must be proven by perturbation observed in a tool-result, not asserted."""
    defn = _defn()
    assert "Overreach: found" in defn
    assert "Overreach: not found" in defn
    assert "perturbing whatever is necessary" in defn


# --- P3: observed-failure gate ---

def test_falsify_p3_gate_3_observed_failure_present():
    """P3: Gate 3 (token) observed-failure is named."""
    defn = _defn()
    assert "Gate 3" in defn
    assert "Observed failure" in defn


def test_falsify_p3_every_executable_assertion():
    """P3: every executable assertion must be observed failing against a violating state."""
    defn = _defn()
    assert "every executable assertion" in defn
    assert "Failure: assertion" in defn


def test_falsify_p3_blind_spot_constructions_named():
    """P3: proxy/non-exercising, durability, and ephemeral blind-spot constructions must be checked."""
    defn = _defn()
    assert "blind spot" in defn
    assert "durability" in defn
    assert "ephemeral" in defn


# --- P4: no self-declared count/correspondence bookkeeping ---

def test_falsify_p4_no_assertion_inventory_count_sentinel():
    """P4: the self-declared inventory count sentinel must be gone."""
    assert "Assertion inventory: complete" not in _defn()


def test_falsify_p4_no_assertion_witnesses_count_sentinel():
    """P4: the self-declared witness count sentinel must be gone."""
    assert "Assertion witnesses: complete" not in _defn()


def test_falsify_p4_no_observation_correspondence_sentinel():
    """P4: the observation-correspondence harness sentinel must be gone."""
    assert "Observation correspondence:" not in _defn()


# --- P5: Unobservable gated on structural subject, not a demonstrated negative ---

def test_falsify_p5_unobservable_requires_structural_subject():
    """P5: Unobservable is admitted only when the guarded property's subject is the artifact's own text/structure."""
    defn = _defn()
    assert "Unobservable: assertion" in defn
    assert "structural" in defn
    assert "artifact's own text or structure as its primary subject" in defn


def test_falsify_p5_unobservable_not_by_demonstrated_negative():
    """P5: Unobservable must NOT be satisfied merely by having searched for a violating state and found none."""
    assert "never satisfied by having searched for a violating state and found none" in _defn()


# --- P7: Gate 3 failure valid only from a committed, re-runnable guard artifact ---

def test_falsify_p7_guard_must_be_committed_artifact():
    """P7: a Failure observation is valid only when produced by executing a committed, re-runnable guard artifact."""
    defn = _defn()
    assert "committed, re-runnable" in defn


def test_falsify_p7_inline_command_not_valid_guard():
    """P7: an inline/ephemeral command cannot be the guard that produces a valid Failure observation."""
    assert "never from an inline or ephemeral command" in _defn()


# --- P8: Gate 3 must discriminate per assertion — whole-symbol absence does not witness all ---

def test_falsify_p8_positive_discrimination_criterion():
    """P8 (allow-list): Gate 3 states the positive criterion — symbol present and executes, this property violated, others could hold, cause attributable to this assertion alone."""
    defn = _defn()
    assert "the governed symbol is present and executes" in defn
    assert "every" in defn and "other retained assertion's property could simultaneously hold" in defn
    assert "attributable to this assertion alone" in defn


def test_falsify_p8_stated_as_positive_test_not_denylist():
    """P8: the criterion is framed as a positive test each assertion must pass, not an enumeration of forbidden failure types."""
    defn = _defn()
    assert "This is the positive test each assertion must pass" in defn


def test_falsify_p8_shared_cause_falls_outside_by_construction():
    """P8: a shared failure cause fails the positive test (not attributable to one assertion), so it falls outside without being enumerated as forbidden."""
    defn = _defn()
    assert "not attributable to any one of them" in defn


# --- P9: verdict-follows-execution — gate verdicts follow a tool-result, not a mental act ---

def test_falsify_p9_verdict_follows_tool_result():
    """P9: a gate verdict is valid only when it follows a tool-result block that mechanically produces it."""
    defn = _defn()
    assert "immediately follows a tool-result block" in defn


def test_falsify_p9_verdict_not_from_description_alone():
    """P9: a verdict emitted from description/analysis alone, not a preceding tool-result, does not satisfy the token."""
    defn = _defn()
    assert "from description or analysis alone" in defn


def test_falsify_p9_conditioned_on_tool_availability():
    """P9: the execution requirement is conditioned on tool-call availability (unsatisfiable-in-no-tool-context guard, GAP-4)."""
    defn = _defn()
    assert "when tool calls are available" in defn


def test_falsify_p9_structural_unobservable_exempt():
    """P9: P5 structural Unobservable is exempt — text-about-text properties have no execution to anchor to."""
    defn = _defn()
    assert "a structural Unobservable assertion is exempt" in defn


# --- P10: visible per-assertion enumeration (non-hollow citation, no count sentinel) ---

def test_falsify_p10_enumerate_each_assertion_verbatim():
    """P10: before Gate 3, emit one verbatim 'Assertion:' line per executable assertion of the guard."""
    defn = _defn()
    assert "one 'Assertion:' line for each executable assertion" in defn


def test_falsify_p10_assertion_text_verbatim_from_guard():
    """P10: each enumerated assertion is quoted verbatim from the guard's tool-result, not paraphrased."""
    defn = _defn()
    assert "quoted verbatim from the established guard's tool-result" in defn


def test_falsify_p10_no_count_sentinel_reintroduced():
    """P10: enumeration must NOT reintroduce the self-declared count sentinel removed in P4."""
    defn = _defn()
    # the enumeration exists but the hollow count tail must stay gone
    assert "one 'Assertion:' line for each executable assertion" in defn
    assert "Assertion inventory: complete" not in defn


# --- P12: anchor the discriminating construction (recovered from old def) ---

def test_falsify_p12_failure_follows_violating_state_execution():
    """P12: the Failure observation must follow the tool-result of executing the guard against the constructed present-but-wrong state."""
    defn = _defn()
    assert "against the constructed present-but-wrong state" in defn


def test_falsify_p12_compile_absence_rejected():
    """P12: a successful compilation, build output, or whole-symbol/undefined error does not satisfy Gate 3 (token observed-failure)."""
    defn = _defn()
    assert "does not satisfy Gate 3" in defn
    assert "whole-symbol or undefined error" in defn


def test_falsify_p12_already_satisfied_temporary_violation():
    """P12: for an already-satisfied property, construct a temporary violating modification, execute, then restore."""
    defn = _defn()
    assert "construct a temporary violating modification" in defn
    assert "then restore" in defn


def test_falsify_p12_per_assertion_outcome_unconditional():
    """P13: the per-assertion outcome is unconditionally required — the tool result must produce an outcome attributable to each assertion alone, regardless of whether the model recognizes any insufficiency."""
    defn = _defn()
    assert "regardless of whether the model recognizes" in defn
    assert "an outcome attributable to that assertion alone" in defn


def test_falsify_p13_evidence_condition_constrains_evidence_not_mechanism():
    """P13: the requirement constrains the evidence (per-assertion outcome); the harness is only one example mechanism, and a framework that already reports per-assertion results satisfies it directly."""
    defn = _defn()
    assert "framework already reports per-assertion results satisfies this directly" in defn
    assert "any execution mechanism that does" in defn
    # the old self-assessed trigger phrasing must be gone
    assert "cannot distinguish which assertion failed" not in defn
    assert "per-assertion outcomes" in defn


# --- P6b: the coverage/retained-property gate does NOT live in the token ---

def test_falsify_p6b_no_retained_property_coverage_gate_in_token():
    """P6b: the coverage gate / retained-property coverage belongs to the composition, not the falsify token."""
    defn = _defn()
    assert "Retained properties:" not in defn
    assert "Coverage gate" not in defn


# --- Old forward-walk machinery must be gone ---

def test_falsify_old_six_step_observing_sentinel_absent():
    """The old 'Observing: property [N]' six-step opener must be gone."""
    assert "Observing: property" not in _defn()


def test_falsify_old_quoted_test_sentinel_absent():
    """The old 'Quoted test:' sentinel must be gone."""
    assert "Quoted test:" not in _defn()


def test_falsify_old_implementation_overreach_sentinel_absent():
    """The old 'Implementation overreach:' sentinel is replaced by Gate 1 'Overreach:'."""
    assert "Implementation overreach:" not in _defn()
