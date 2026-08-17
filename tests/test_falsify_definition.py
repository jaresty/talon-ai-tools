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
    """P1: guard and artifact may be established in any order."""
    assert "may be established in any order" in _defn()


# --- P2: minimization gate ---

def test_falsify_p2_gate_1_minimization_present():
    """P2: Gate 1 (shrink implementation to guard) is named."""
    defn = _defn()
    assert "Gate 1" in defn
    assert "Shrink the artifact to the guard" in defn


def test_falsify_p2_overreach_requires_executed_attempt():
    """P2: 'Overreach: not found' requires an executed reduction attempt — a bare claim does not satisfy."""
    defn = _defn()
    assert "Overreach: found" in defn
    assert "Overreach: not found" in defn
    assert "Always attempt the simpler artifact" in defn
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
    assert "never satisfied by having searched for a failing application and found none" in _defn()


# --- P7: Gate 3 failure valid only from a committed, re-runnable guard artifact ---

def test_falsify_p7_standing_regression_guard_must_be_committed():
    """P7: a Failure intended as a standing regression guard must be produced by a committed, persisted procedure."""
    defn = _defn()
    assert "committed procedure persisted to a location that re-applies without human initiation" in defn


def test_falsify_p7_inline_one_off_not_a_standing_guard():
    """P7: an inline/ephemeral one-off cannot serve as the standing regression guard (persistence is required for that claim)."""
    assert "not an inline or ephemeral one-off" in _defn()


# --- P20 canonical rule: the guard's own per-assertion pass/fail IS the property state ---

def test_falsify_p28_decollapse_guard_result_not_property_truth():
    """P28 (de-collapse R_A/R_P): A-pass/A-fail are the guard's REPORTED results, not claims about property truth; correspondence deferred to adequacy."""
    defn = _defn()
    assert "an A-pass is the guard's reported pass result for A and an A-fail is the guard's reported failure result for A" in defn
    assert "not independent claims about the truth of any property" in defn


def test_falsify_p28_property_correspondence_is_scope_boundary():
    """P28: correspondence to the property is a scope boundary (deferred to adequacy), not a caveat, and no property-truth is asserted in the token."""
    defn = _defn()
    assert "whether A's result corresponds to the property A is intended to govern is not established by this token" in defn
    assert "that correspondence is established separately by the adequacy check" in defn
    # the collapse wording must be gone
    assert "an A-fail result witnesses it absent" not in defn


def test_falsify_p20_failure_is_a_fail_a_pass_pair():
    """P20: a behavioral assertion is witnessed only by a pair of A-observations — A-fail in one, A-pass in the other."""
    defn = _defn()
    assert "pair of A-observations" in defn
    assert "A's own guard-defined result is a failure, and one in which A's own result is a pass" in defn


def test_falsify_p20_classify_observations_not_failure_modes():
    """P20 (general, not an enumeration): any execution not producing an A result is not an observation of A — regardless of cause or form."""
    defn = _defn()
    assert "An A-observation is an application of the committed guard in which assertion A is evaluated and produces its own guard-defined result" in defn
    assert "not an observation of A and cannot witness A, regardless of the cause or form of the application's outcome" in defn
    # the failure-mode enumeration must be gone (classify observations, not failures)
    assert "compilation failure, timeout, panic" not in defn


def test_falsify_p27_salient_compile_absence_example():
    """P27: the abstract rule carries a salient illustrative example (not an allow-list) naming the tempting new-function compile-absence inference and why it fails."""
    defn = _defn()
    assert "as an illustration of this rule, not an exhaustive list" in defn
    assert "it is not an A-fail, because A never ran — the application disqualified itself as an observation of A" in defn
    assert "A's own assertion applied and reporting failure against a present-but-wrong artifact, which the subject's absence cannot produce" in defn


def test_falsify_p20_producer_is_the_a_fail_execution():
    """P20 (provenance): the A-fail execution immediately precedes Failure:; the A-pass execution is contrast evidence elsewhere."""
    defn = _defn()
    assert "application must immediately precede the" in defn
    assert "application is the contrast evidence" in defn


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


# --- P23: provenance closure — every evidentiary reference quotes its qualifying observation record ---

def test_falsify_p23_provenance_closure_general_rule():
    """P23: identity + A-fail + A-pass must quote verbatim the qualifying observation record; one general rule, not per-artifact cases."""
    defn = _defn()
    assert "Provenance closure" in defn
    assert "must quote verbatim the text of the qualifying observation record that establishes it" in defn


def test_falsify_p23_authored_prose_is_not_evidence():
    """P23: a result or identity typed as prose not verbatim in a cited qualifying observation record is not evidence."""
    defn = _defn()
    assert "typed as prose that does not appear verbatim in a cited qualifying observation record is not evidence" in defn


# --- P24: capability is not evidence — qualifying observation record + Unwitnessed third state ---

def test_falsify_p24_capability_is_not_evidence():
    """P24: what witnesses is an available qualifying observation record, not whether a tool call occurred this turn."""
    defn = _defn()
    assert "Capability is not evidence" in defn
    assert "available qualifying observation record" in defn


def test_falsify_p24_qualifying_record_defined():
    """P24: a qualifying observation record is guard-produced, carries guard+assertion identity + A-result, transcript-present; prose is never one."""
    defn = _defn()
    assert "A qualifying observation record is a transcript-present record produced by the committed guard artifact" in defn
    assert "model prose is never one" in defn


def test_falsify_p24_prior_record_usable_without_tools():
    """P24: when tools are unavailable, may cite qualifying records already present but must not synthesize/infer/narrate."""
    defn = _defn()
    assert "when it is unavailable it may cite qualifying observation records already present but must not synthesize, infer, or narrate an observation" in defn


def test_falsify_p24_unwitnessed_third_state():
    """P24: a behavioral assertion with no qualifying record is Unwitnessed (not structural Unobservable), and blocks Coverage."""
    defn = _defn()
    assert "Unwitnessed: assertion" in defn
    assert "observation unavailable" in defn
    assert "neither Failure nor structural Unobservable" in defn


def test_falsify_p24_unwitnessed_blocks_coverage():
    """P24: an Unwitnessed assertion leaves coverage incomplete."""
    defn = _defn()
    assert "'Unwitnessed: … — observation unavailable' assertion leaves coverage incomplete" in defn


# --- P25: uniform execution-unavailable state at every gate (untested != not-found/false/unobservable) ---

def test_falsify_p25_gate1_overreach_untested():
    """P25: Gate 1 Overreach is execution-dependent — no execution → 'Overreach: untested', never 'not found'."""
    defn = _defn()
    assert "Overreach: untested — observation unavailable" in defn
    assert "untested is never 'not found'" in defn


def test_falsify_p25_coverage_incomplete_terminal_honesty():
    """P25: no execution → honest terminal state 'Coverage: incomplete — observation unavailable', not a claimed completion."""
    defn = _defn()
    assert "Coverage: incomplete — observation unavailable" in defn
    assert "not a claimed completion" in defn


def test_falsify_p25_may_construct_but_not_claim_observed():
    """P25: without execution the protocol may construct guards/perturbations/expected outcomes but not represent any execution-dependent verdict as observed."""
    defn = _defn()
    assert "may not represent any observation-dependent verdict as observed" in defn


def test_falsify_p20_structural_bifurcation():
    """P20: a structural assertion is witnessed by Unobservable: structural — the deliberate behavioral/structural fork."""
    defn = _defn()
    assert "A structural assertion" in defn
    assert "Unobservable: assertion" in defn


# --- P9: verdict-follows-execution — gate verdicts follow a tool-result, not a mental act ---

def test_falsify_p9_verdict_follows_tool_result():
    """P9: a gate verdict is valid only when it follows a tool-result block that mechanically produces it."""
    defn = _defn()
    assert "immediately follows a result record" in defn


def test_falsify_p9_verdict_not_from_description_alone():
    """P9: a verdict emitted from description/analysis alone, not a preceding tool-result, does not satisfy the token."""
    defn = _defn()
    assert "from description or analysis alone" in defn


def test_falsify_p9_conditioned_on_tool_availability():
    """P9: the execution requirement is conditioned on tool-call availability (unsatisfiable-in-no-tool-context guard, GAP-4)."""
    defn = _defn()
    assert "when the observation capability is available" in defn


def test_falsify_p9_structural_unobservable_exempt():
    """P9: P5 structural Unobservable is exempt — text-about-text properties have no execution to anchor to."""
    defn = _defn()
    assert "structural Unobservable assertion is exempt" in defn


# --- P10: visible per-assertion enumeration (non-hollow citation, no count sentinel) ---

def test_falsify_p10_enumerate_each_assertion_verbatim():
    """P10: in Gate 2, emit one verbatim 'Assertion:' line per executable assertion of the guard."""
    defn = _defn()
    assert "one 'Assertion: <verbatim assertion text>' line for each assertion" in defn


def test_falsify_p10_assertion_text_verbatim_from_guard():
    """P10: each enumerated assertion is quoted verbatim from the guard's tool-result, not paraphrased."""
    defn = _defn()
    assert "quoted verbatim from the guard's result record" in defn


def test_falsify_p10_no_count_sentinel_reintroduced():
    """P10: enumeration must NOT reintroduce the self-declared count sentinel removed in P4."""
    defn = _defn()
    # the enumeration exists but the hollow count tail must stay gone
    assert "one 'Assertion: <verbatim assertion text>' line for each assertion" in defn
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


# --- Fix 2 (assertion-binding): a guard observation must evaluate the enumerated
# assertion and produce that assertion's own result. Retrieving a fact is not
# witnessing. This restores the falsify/verify/ground orthogonality boundary that
# the software medium enforced implicitly and the domain-agnostic genus dropped. ---

def test_falsify_assertion_binding_procedure_evaluates_assertion():
    """A witness requires the procedure to evaluate the enumerated assertion and produce its own result."""
    defn = _defn()
    assert "evaluates that assertion and produces an assertion-specific result" in defn
    assert "Information merely retrieved, inferred, or cited by the procedure is not itself the assertion's result" in defn


def test_falsify_assertion_binding_boundary_sentence_verbatim():
    """The retrieve-vs-witness boundary sentence must appear verbatim so examples cannot blur research into witnessing."""
    assert "Retrieving evidence for an assertion is not the same operation as witnessing the assertion" in _defn()


# --- Fix 1 (provenance discovery): 'observation unavailable' is valid only as the
# residue of inspecting the available observation records — not a first-move
# declaration. Generalized past 'transcript' (records store is domain-agnostic). ---

def test_falsify_provenance_discovery_inspect_before_unavailable():
    """Before declaring observation unavailable, inspect the available observation records for a qualifying one."""
    defn = _defn()
    assert "inspect the available observation records for a qualifying record" in defn
    assert "only when no qualifying record is found may the unavailable state be emitted" in defn


# --- Fix 3 (counterfactual-independence): what makes an observation a witness is
# that the procedure could have produced the violating result — operationally shown
# by perturbing the relevant state and observing the result flip, not asserted. The
# software "committed re-runnable artifact" encoded this only implicitly. ---

def test_falsify_counterfactual_independence_is_the_witness_property():
    """A witness requires the procedure could have produced the violating result — shown by the perturbation flip."""
    defn = _defn()
    assert "could have produced the violating result" in defn
    assert "not constructed from the conclusion it is meant to evaluate" in defn


# --- Fix 4 (persistence is a separable capability): regression-persistence
# (re-application without human initiation) may be present or absent. A one-time
# assertion-bound, counterfactually-independent observation is a valid witness NOW;
# only the regression-detection claim depends on persistence. This prevents the
# definition from being read as "witness == persisted software artifact". ---

def test_falsify_persistence_is_a_separable_capability():
    """Persistence is separable: a one-time observation still witnesses; only regression detection needs persistence."""
    defn = _defn()
    assert "Regression-persistence is a separable capability that may be present or absent" in defn
    assert "a one-time application that is assertion-bound and counterfactually independent still witnesses its assertion" in defn
