"""Tests asserting key literal strings for the prose-origin gate.

Each test must FAIL before the edit and PASS after.

Root principle: a string that appears in executor output only because the agent
wrote it as a literal in an artifact carries no evidential weight. The prose-origin
gate disqualifies any string from satisfying derivation gates if it appears in a
Write or Edit tool call before its first appearance in an executor result block.

The message-label extension (condition 4 of provenance exception) is removed because
it is exactly the prose-originated string attack — the agent writes the label before
any executor produces it.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_prose_origin_gate_label():
    assert "Prose-origin gate" in defn()

def test_prose_origin_gate_write_edit_precedes():
    assert "appears verbatim in the content of a Write or Edit tool call in this transcript that precedes the first executor result block in this transcript containing that string" in defn()

def test_prose_origin_gate_applies_to_all_gates():
    assert "does not satisfy any derivation gate — including (a), (c), (d), the allow-list, and the failure line" in defn()

def test_prose_origin_gate_bootstrap_exception():
    assert "strings governed by the Bootstrap exception" in defn()

def test_prose_origin_gate_creation_step_exception():
    assert "strings that satisfy the creation-step exception's absent/present condition" in defn()

def test_message_label_extension_removed():
    # The message-label extension is prose-originated by definition and must be removed
    assert "the message argument satisfies this only when it appears as a string literal (not a variable or computed expression) in the content of a Write or Edit tool call whose path argument matches the governing artifact file path" not in defn()
