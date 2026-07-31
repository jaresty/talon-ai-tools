"""Tests for predecessor-sentinel gates on ## Enforcement sequence and ## Path enumeration."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.groundPrompt import GROUND_PARTS_MINIMAL


def _core() -> str:
    return GROUND_PARTS_MINIMAL["core"]


def test_enforcement_sequence_gated_on_properties_complete():
    """## Enforcement sequence must not appear before § properties complete."""
    core = _core()
    assert "'## Enforcement sequence' must not appear before '§ properties complete'" in core


def test_enforcement_complete_sentinel_present():
    """§ enforcement complete sentinel must exist to close ## Enforcement sequence."""
    core = _core()
    assert "§ enforcement complete" in core


def test_enforcement_check_required_before_enforcement_complete():
    """§ enforcement check: must be required before § enforcement complete."""
    core = _core()
    assert "'§ enforcement complete' is valid only after a valid '§ enforcement check:' line has appeared" in core


def test_path_enumeration_gated_on_enforcement_complete():
    """## Path enumeration must not appear before § enforcement complete."""
    core = _core()
    assert "'## Path enumeration' must not appear before '§ enforcement complete'" in core


def test_enumeration_complete_gated_on_enforcement_complete():
    """§5 enumeration complete must not appear before § enforcement complete."""
    core = _core()
    assert "'§5 enumeration complete' must not appear before '§ enforcement complete'" in core


def test_completion_check_gated_on_enumeration_complete():
    """## Completion check must not appear before §5 enumeration complete."""
    core = _core()
    assert "'## Completion check' must not appear before '§5 enumeration complete'" in core


def test_split_test_sentinel_required_before_sub_properties():
    """§ split test: sentinel must appear after each property [N]: before sub-properties."""
    core = _core()
    assert "'§ split test:'" in core
    assert "'property [Na]:' line that does not have a '§ split test:' line above it does not satisfy" in core


def test_sub_property_logical_equivalence_definition():
    """conjunction of sub-properties must describe same set of instances as parent."""
    core = _core()
    assert "strict subset" in core and "strict superset" in core


def test_atomicity_test_positive_trigger():
    """after each property [N]: line, immediately write § split test: to attempt decomposition."""
    core = _core()
    assert "after writing each 'property [N]:' line, immediately write '§ split test:" in core


def test_formalization_complete_positive_trigger():
    """after valid alternative satisfier: and § ambiguity test:, immediately write § formalization complete."""
    core = _core()
    assert "immediately write '§ formalization complete'" in core


def test_properties_complete_positive_trigger():
    """after § properties check:, immediately write § properties complete."""
    core = _core()
    assert "immediately write '§ properties complete'" in core


def test_enforcement_sequence_positive_trigger():
    """after § properties complete, immediately write ## Enforcement sequence."""
    core = _core()
    assert "after '§ properties complete', immediately write '## Enforcement sequence'" in core


def test_path_enumeration_positive_trigger():
    """after § enforcement complete, immediately write ## Path enumeration."""
    core = _core()
    assert "after '§ enforcement complete', immediately write '## Path enumeration'" in core


def test_completion_check_positive_trigger():
    """after §5 enumeration complete, immediately write ## Completion check."""
    core = _core()
    assert "after '§5 enumeration complete', immediately write '## Completion check'" in core
