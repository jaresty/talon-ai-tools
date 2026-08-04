"""Tests for ground token definition — spike/craft-token-refactor branch."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.groundPrompt import build_ground_prompt


def _core() -> str:
    return build_ground_prompt()


def test_ground_properties_block_required_before_action():
    """Ground properties block must precede any test, implementation, tool call, or task reasoning."""
    core = _core()
    assert "before any test, implementation step, tool call, or task reasoning begins" in core


def test_interpretation_line_required_for_ambiguous_requests():
    """Ambiguous requests must declare chosen interpretation before first property."""
    core = _core()
    assert "'Interpretation: <chosen interpretation>'" in core
    assert "all subsequent properties are derived exclusively from this interpretation" in core


def test_properties_derivable_from_interpretation():
    """Every property must be derivable from the explicit constraints of the chosen interpretation."""
    core = _core()
    assert "Every property must be derivable from the explicit constraints of the chosen interpretation" in core
    assert "out of scope and must not appear in the block" in core


def test_split_test_sentinel_present():
    """§ split test: sentinel must be present."""
    core = _core()
    assert "§ split test:" in core


def test_split_test_quotes_verbatim():
    """Split test must quote provisional definitions verbatim."""
    core = _core()
    assert "quoted definitions must match the immediately preceding provisional definitions verbatim" in core


def test_split_test_atomic_no_valid_split_form():
    """If no valid split exists, emit atomic no valid split form."""
    core = _core()
    assert "atomic, no valid split: <reason>" in core
    assert "The quoted definition must match the retained property verbatim" in core


def test_split_recursion_until_atomic():
    """Continue recursively until every retained property has a split test concluding atomic."""
    core = _core()
    assert "Continue recursively until every retained property has a split test concluding 'atomic, no valid split.'" in core


def test_completeness_check_sentinel_present():
    """§ completeness check: sentinel must be present."""
    core = _core()
    assert "§ completeness check:" in core


def test_completeness_check_quotes_request_constraints():
    """§ completeness check must quote request constraints verbatim."""
    core = _core()
    assert "request constraints must be quoted verbatim from the chosen interpretation" in core


def test_completeness_check_quotes_all_properties():
    """§ completeness check must include every retained atomic property expression."""
    core = _core()
    assert "every retained atomic property expression must appear exactly once, separated by ' / '" in core
    assert "omits the request constraints or omits any retained property expression does not satisfy this requirement" in core


def test_properties_complete_no_sentinel():
    """§ properties complete? no must be emitted when a gap is found."""
    core = _core()
    assert "§ properties complete? no" in core


def test_properties_complete_yes_sentinel():
    """§ properties complete? yes gates completion — requires preceding completeness check."""
    core = _core()
    assert "§ properties complete? yes" in core
    assert "a '§ properties complete? yes' line without a preceding completeness check does not satisfy this protocol" in core


def test_observational_independence_check():
    """Observational independence must be verified after completeness."""
    core = _core()
    assert "observationally independent" in core
    assert "observationally redundant and must be removed or merged" in core


def test_completion_conditions_enumerated():
    """Ground properties block completion requires all five conditions simultaneously."""
    core = _core()
    assert "they are derived from the chosen interpretation" in core
    assert "they are atomic" in core
    assert "they collectively cover every explicit request constraint" in core
    assert "they are observationally independent" in core
    assert "they introduce no out-of-scope constraints" in core
