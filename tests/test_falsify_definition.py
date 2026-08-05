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
