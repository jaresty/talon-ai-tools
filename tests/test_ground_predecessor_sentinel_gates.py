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


def test_atomicity_test_sentinel_required_before_atomic_declaration():
    """§ atomicity test: sentinel must appear before property [Na]: atomic —."""
    core = _core()
    assert "'§ atomicity test:'" in core
    assert "'property [Na]: atomic —' line that does not have a '§ atomicity test:' line" in core


def test_atomic_restatement_notation_class_requirement():
    """atomic restatement must use same notation class as parent property [N]:."""
    core = _core()
    assert "same notation class" in core
