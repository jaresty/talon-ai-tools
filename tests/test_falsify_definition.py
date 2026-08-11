"""Tests for the falsify token definition — spike/craft-token-refactor six-step cycle form."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def _defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


# --- Absence tests (old labeling scheme must be gone) ---

def test_falsify_old_file_nonexistence_clause_absent():
    """Old 'file path as literal string in executor invocation' clause must be absent."""
    assert "whose file path — the path passed as an argument to the executor invocation" not in _defn()


def test_falsify_rationale_opener_starts_with_the_response():
    """Definition must open with 'The response'."""
    assert _defn().startswith("The response")


# --- Six-step cycle sentinels present ---

def test_falsify_observing_sentinel():
    """Step (1): Observing: property sentinel must be required."""
    assert "Observing: property" in _defn()


def test_falsify_quoted_test_sentinel():
    """Step (2): Quoted test: sentinel must be required."""
    assert "Quoted test:" in _defn()


def test_falsify_test_blind_spot_sentinel():
    """Step (3): Test blind-spot: sentinel must be required."""
    assert "Test blind-spot:" in _defn()


def test_falsify_failure_sentinel():
    """Step (4): Failure: property sentinel must be required."""
    assert "Failure: property" in _defn()


def test_falsify_unobservable_sentinel():
    """Step (4): Unobservable: property sentinel as last-resort must be present."""
    assert "Unobservable: property" in _defn()


def test_falsify_quoted_implementation_sentinel():
    """Step (5): Quoted implementation: sentinel must be required."""
    assert "Quoted implementation:" in _defn()


def test_falsify_quoted_implementation_verbatim_in_following_tool_call():
    """property [1]: Quoted implementation: content must appear verbatim in the immediately following modification tool call."""
    assert "does not appear verbatim as literal artifact text in the immediately following modification tool call does not satisfy this token" in _defn()


def test_falsify_quoted_implementation_rejects_paraphrase():
    """property [2]: a purpose/effect/plan paraphrase does not satisfy Quoted implementation:."""
    assert "a description of the change's purpose, effect, or plan" in _defn()


def test_falsify_implementation_overreach_sentinel():
    """Step (6): Implementation overreach: sentinel must be required."""
    assert "Implementation overreach:" in _defn()


def test_falsify_coverage_sentinel():
    """Coverage: sentinel must be required after all properties complete."""
    assert "Coverage:" in _defn()


# --- Key semantic invariants ---

def test_falsify_regression_guard_required():
    """A regression guard must be established for each property."""
    assert "regression guard" in _defn()


def test_falsify_governed_artifact_generalized():
    """Step (5) target is the governed artifact, not specifically the implementation."""
    assert "governed artifact" in _defn()


def test_falsify_temporary_violating_state():
    """Pre-satisfied properties must construct a temporary violating state."""
    assert "temporary" in _defn()


def test_falsify_unobservable_is_last_resort():
    """Unobservable: is a last resort, not an easy escape."""
    assert "last resort" in _defn()


def test_falsify_universality_no_exemption():
    """No property class may abbreviate or skip steps."""
    assert "without abbreviation" in _defn()


# --- Assertion witness classification (step 4 extension) ---

def test_falsify_assertion_witness_sentinel():
    """Step (4): witness classification sentinel must be present."""
    assert "Assertion witnesses: complete" in _defn()


def test_falsify_assertion_witness_classifications():
    """Witness classifications Failure, Success, Unobservable must all be named (Unreached replaced by Unobservable)."""
    defn = _defn()
    assert "witness: Failure" in defn
    assert "witness: Success" in defn
    assert "witness: Unobservable" in defn


def test_falsify_assertion_witness_at_least_one_failure():
    """At least one Failure witness required — no-failure execution does not satisfy step (4)."""
    assert "classified Failure does not satisfy step (4)" in _defn()


def test_falsify_assertion_witness_verbatim_attribution():
    """Failure witness observed text must appear verbatim in the corresponding tool-result block."""
    assert "not present verbatim in the corresponding tool-result block does not satisfy this token" in _defn()


def test_falsify_assertion_witness_replays_assertion_text():
    """Each witness line must quote the verbatim assertion text from the inventory."""
    defn = _defn()
    assert "verbatim assertion text" in defn
    assert "assertion inventory order" in defn


def test_falsify_assertion_witness_unreached_requires_reason():
    """Unobservable witness must be justified by a verbatim tool-result excerpt."""
    assert "Unobservable is the last resort and must be justified by a verbatim tool-result excerpt" in _defn()


def test_falsify_assertion_witness_count_matches_inventory():
    """Witness count must equal the inventory count."""
    assert "a witness count that differs from the inventory count does not satisfy this token" in _defn()


def test_falsify_assertion_witness_before_step_5():
    """Witness block must precede step (5)."""
    defn = _defn()
    assert defn.index("Assertion witnesses: complete") < defn.index("(5) identify the governed artifact")


def test_falsify_failure_must_immediately_follow_tool_result():
    """Failure: line must immediately follow the execution tool-result block — no narrative permitted."""
    assert "the text immediately following the execution tool-result block must be the Failure: line for property [N]" in _defn()


def test_falsify_failure_narrative_substitution_forbidden():
    """Prose explanation, causal argument, or reference to prior failure does not satisfy Failure:."""
    assert "no narrative, causal argument, prose explanation, reference to a prior failure, or other content may appear between the tool-result block and the Failure: line" in _defn()


def test_falsify_failure_not_immediately_following_fails():
    """A Failure: line not immediately following a tool-result block does not satisfy the token."""
    assert "a Failure: line that does not immediately follow a tool-result block does not satisfy this token" in _defn()


# --- Governed artifact scope (step 5): the artifact the guard governs, never the guard itself ---

def test_falsify_governed_artifact_menu_clause_absent():
    """The permissive menu-of-artifact-types clause must be gone from step (5)."""
    assert (
        "the governed artifact may be the implementation, the regression guard, "
        "a configuration file, or another explicitly governed artifact"
    ) not in _defn()


def test_falsify_governed_artifact_is_what_guard_governs():
    """Step (5) must scope the governed artifact to what the established guard governs, never the guard itself."""
    defn = _defn()
    assert "the governed artifact is the artifact that the established regression guard governs" in defn
    assert "it is never the guard itself" in defn
