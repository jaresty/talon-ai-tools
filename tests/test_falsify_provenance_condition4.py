"""Tests asserting the revised condition (4) of the assertion-target provenance exception.

Each test must FAIL before the edit and PASS after.

Gap: condition (4) currently requires the failure line to contain (d), the chain
identifier, or the message literal — in addition to (a)+(c). This blocks behavioral
failures (e.g. UI test: "Unable to find element") where the failure line naturally
describes missing behavior, not implementation symbol names. The fix: under the
provenance exception, satisfying (a)+(c) is sufficient for condition (4); no additional
string on the failure line is required. (d), identifier, and message-literal paths
remain as alternatives, not as requirements.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_condition4_ac_sufficient():
    assert "the executor result block satisfies the base (a) and (c) requirements — no additional requirement that the failure line contain (d) or the chain identifier applies under this exception" in defn()

def test_condition4_message_label_extension_removed():
    # message-label extension was superseded by the prose-origin gate
    assert "string literal that appears verbatim as the message argument to the assertion call expression in the governing artifact" not in defn()
