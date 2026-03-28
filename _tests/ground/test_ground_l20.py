"""Test for L20: exec_observed may not be written without a real tool call.

The escape route: the model generates the entire ground protocol as prose,
including fake exec_observed blocks, without making any actual tool calls.
The A1 axiom requires tool-executed events but has no hard gate preventing
the model from writing the sentinel as generated text.

L20 closes this by requiring that if no tool call has been made in the current
response, writing exec_observed is a protocol violation — the model must stop
and make the tool call first.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL20ExecObservedToolCallGate(unittest.TestCase):
    """L20: exec_observed may not be written without a real tool call."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l20_no_tool_call_blocks_exec_observed(self):
        """If no tool call has been made in this response, exec_observed is blocked."""
        self.assertIn(
            "no tool call has been made in the current response",
            self.core,
            "L20: must explicitly state that exec_observed is blocked when no tool call exists",
        )

    def test_l20_requires_stop_before_tool_call(self):
        """When no tool call exists, model must stop and make the tool call first."""
        idx = self.core.find("no tool call has been made in the current response")
        self.assertGreater(idx, -1, "L20 gate sentence must be present")
        segment = self.core[idx:idx+300]
        self.assertIn(
            "stop",
            segment,
            "L20: gate must require stopping and making the tool call before writing the sentinel",
        )

    def test_l20_generated_text_does_not_satisfy(self):
        """Generated text that resembles tool output does not satisfy exec_observed."""
        self.assertIn(
            "generated text that resembles tool output does not satisfy",
            self.core,
            "L20: must explicitly state that generated text resembling output is not a valid exec_observed",
        )

    def test_l20_positioned_near_exec_observed_rule(self):
        """L20 gate must appear near the exec_observed definition."""
        exec_obs_idx = self.core.index(
            "\U0001f534 Execution observed: requires: (1) a preceding tool call"
        )
        gate_idx = self.core.find("no tool call has been made in the current response")
        self.assertGreater(gate_idx, -1, "L20 gate sentence must be present")
        self.assertLess(abs(gate_idx - exec_obs_idx), 600,
            "L20: gate must appear near the exec_observed definition")


if __name__ == "__main__":
    unittest.main()
