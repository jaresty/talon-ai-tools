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
    """P2: Gate 1 (shrink implementation to guard) is named."""
    defn = _defn()
    assert "Gate 1" in defn
    assert "Shrink the implementation to the guard" in defn


def test_falsify_p2_overreach_requires_executed_attempt():
    """P2: 'Overreach: not found' requires an executed reduction attempt — a bare claim does not satisfy."""
    defn = _defn()
    assert "Overreach: found" in defn
    assert "Overreach: not found" in defn
    assert "Always attempt the simpler implementation" in defn
    assert "A bare 'Overreach: not found' with no" in defn


# --- P3: witness-every-assertion gate ---

def test_falsify_p3_gate_2_witness_present():
    """P3: Gate 2 (witness every assertion) is named."""
    defn = _defn()
    assert "Gate 2" in defn
    assert "Witness every assertion" in defn


def test_falsify_p3_every_executable_assertion():
    """P3: every enumerated assertion must be witnessed (Failure pair or structural Unobservable)."""
    defn = _defn()
    assert "every enumerated assertion" in defn
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
    """P5: Unobservable must NOT be satisfied merely by having searched for a failing execution and found none."""
    assert "never satisfied by having searched for a failing execution and found none" in _defn()


# --- P7: Gate 3 failure valid only from a committed, re-runnable guard artifact ---

def test_falsify_p7_guard_must_be_committed_artifact():
    """P7: a Failure observation is valid only when produced by executing a committed, re-runnable guard artifact."""
    defn = _defn()
    assert "committed, re-runnable" in defn


def test_falsify_p7_inline_command_not_valid_guard():
    """P7: an inline/ephemeral command cannot be the guard that produces a valid Failure observation."""
    assert "never from an inline or ephemeral command" in _defn()


# --- P20 canonical rule: the guard's own per-assertion pass/fail IS the property state ---

def test_falsify_p20_guard_defines_observable_predicate():
    """P20 (non-circular): the guard DEFINES the observable predicate — A-pass witnesses property present, A-fail witnesses absent; not 'result is the property'."""
    defn = _defn()
    assert "The guard defines the observable predicate for A" in defn
    assert "an A-pass" in defn and "witnesses the property present" in defn


def test_falsify_p20_failure_is_a_fail_a_pass_pair():
    """P20: a behavioral assertion is witnessed only by a pair of A-observations — A-fail in one, A-pass in the other."""
    defn = _defn()
    assert "pair of A-observations" in defn
    assert "A's own guard-defined result is a failure, and one in which A's own result is a pass" in defn


def test_falsify_p20_classify_observations_not_failure_modes():
    """P20 (general, not an enumeration): any execution not producing an A result is not an observation of A — regardless of cause or form."""
    defn = _defn()
    assert "An A-observation is an execution of the committed guard in which assertion A is evaluated and produces its own guard-defined result" in defn
    assert "not an observation of A and cannot witness A, regardless of the cause or form of the execution's outcome" in defn
    # the failure-mode enumeration must be gone (classify observations, not failures)
    assert "compilation failure, timeout, panic" not in defn


def test_falsify_p20_producer_is_the_a_fail_execution():
    """P20 (provenance): the A-fail execution immediately precedes Failure:; the A-pass execution is contrast evidence elsewhere."""
    defn = _defn()
    assert "execution must immediately precede the" in defn
    assert "execution is the contrast evidence" in defn


def test_falsify_p20_identity_carried_by_guard_output():
    """P20 (identity): the guard's output must identify A (test name/subtest/message), not model attribution."""
    defn = _defn()
    assert "the guard's output must identify A" in defn


def test_falsify_p20_temp_modification_isolates_one_assertion():
    """P20: for an already-passing A, a temporary modification must make A alone fail while others pass."""
    defn = _defn()
    assert "makes A alone fail while every other assertion still passes" in defn


def test_falsify_p20_witness_line_is_projection_only():
    """P20: a 'witness:' line only projects the two results and is not itself evidence."""
    defn = _defn()
    assert "only projects those two results and is not itself evidence" in defn


def test_falsify_p20_structural_bifurcation():
    """P20: a structural assertion is witnessed by Unobservable: structural — the deliberate behavioral/structural fork."""
    defn = _defn()
    assert "A structural assertion" in defn
    assert "Unobservable: assertion" in defn


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
    assert "structural Unobservable assertion is exempt" in defn


# --- P10: visible per-assertion enumeration (non-hollow citation, no count sentinel) ---

def test_falsify_p10_enumerate_each_assertion_verbatim():
    """P10: in Gate 2, emit one verbatim 'Assertion:' line per executable assertion of the guard."""
    defn = _defn()
    assert "one 'Assertion: <verbatim assertion text>' line for each executable assertion" in defn


def test_falsify_p10_assertion_text_verbatim_from_guard():
    """P10: each enumerated assertion is quoted verbatim from the guard's tool-result, not paraphrased."""
    defn = _defn()
    assert "quoted verbatim from the guard's tool-result" in defn


def test_falsify_p10_no_count_sentinel_reintroduced():
    """P10: enumeration must NOT reintroduce the self-declared count sentinel removed in P4."""
    defn = _defn()
    # the enumeration exists but the hollow count tail must stay gone
    assert "one 'Assertion: <verbatim assertion text>' line for each executable assertion" in defn
    assert "Assertion inventory: complete" not in defn


def test_falsify_p11_binding_by_verbatim_identity():
    """P11 (the 1-of-6 fix): every enumerated Assertion must receive its own verbatim-matching Failure/Unobservable before Coverage."""
    defn = _defn()
    assert "binding is by verbatim identity" in defn
    assert "an enumerated assertion with no matching outcome line leaves coverage incomplete" in defn


def test_falsify_p18_explicit_witness_loop_transition():
    """P18: an explicit forward loop — after each outcome, return to the witness step for the NEXT unwitnessed assertion until none remain."""
    defn = _defn()
    assert "return to the witness step for the next unwitnessed assertion" in defn


def test_falsify_p18_loop_terminates_on_empty_unwitnessed_set():
    """P18: the loop terminates only when no enumerated assertion lacks a Failure or structural-Unobservable outcome (structural Unobservable is a legitimate terminal outcome)."""
    defn = _defn()
    assert "do not leave Gate 2 until every enumerated assertion has a matching outcome" in defn


# NOTE: the former P8/P12/P13/P17/P19d tests are collapsed into the P20 canonical rule
# above (guard's own per-assertion pass/fail = property state). Their properties —
# present-but-wrong (A must execute), compile/undefined/panic rejected, temp-violation
# isolation, per-assertion outcome, committed-guard evidence, witness-is-projection —
# are all asserted by the test_falsify_p20_* block. The self-assessed-trigger phrasing
# must still be gone:

def test_falsify_p20_no_self_assessed_trigger_phrasing():
    """The old self-assessed harness trigger phrasing must remain absent."""
    assert "cannot distinguish which assertion failed" not in _defn()


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
