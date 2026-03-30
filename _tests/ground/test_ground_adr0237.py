"""Tests for ADR-0237: observation must execute live running code; reads excluded.

T1 observation-requires-live-execution: tool call must execute live running code;
   reading files, grepping source, or inspecting static artifacts does not qualify.
"""
import unittest

from _tests.ground.ground_test_base import GroundADRTestBase

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_ObservationRequiresLiveExecution(GroundADRTestBase):
    """Observation must execute live running code; static reads excluded."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_tool_call_must_execute_live_code(self):
        self.assertIn(
            "the tool call must execute live running code",
            self.core,
        )

    def test_reading_files_excluded(self):
        self.assertIn(
            "reading files",
            self.core,
        )

    def test_static_artifacts_excluded(self):
        self.assertIn(
            "inspecting static artifacts does not satisfy this requirement",
            self.core,
        )

    def test_propagated_to_prompt(self):
        self.assertIn(
            "the tool call must execute live running code",
            build_ground_prompt(),
        )


if __name__ == "__main__":
    unittest.main()
