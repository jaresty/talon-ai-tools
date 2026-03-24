"""Tests for C25–C28 ground protocol escape-route closures."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestC25NoEditThreadComplete(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c25_no_edit_thread_complete_prohibited(self):
        self.assertIn(
            "no implementation file was created or modified for this thread",
            self.core,
            "C25: Thread N complete gate must prohibit emission when no implementation edit was made in this cycle")

    def test_c25_positioned_in_thread_complete_section(self):
        c25_idx = self.core.index(
            "no implementation file was created or modified for this thread")
        tc_idx = self.core.index("\u2705 Thread N complete may not be emitted unless")
        self.assertGreater(c25_idx, tc_idx - 200,
            "C25: no-edit prohibition must appear near the Thread N complete gate")


class TestC26BlankOBSProhibited(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c26_blank_obs_prohibited(self):
        self.assertIn(
            "empty or blank",
            self.core,
            "C26: OBS gate must explicitly prohibit empty/blank verbatim output blocks")

    def test_c26_positioned_in_obs_section(self):
        c26_idx = self.core.index("empty or blank")
        obs_idx = self.core.index("Upon writing the observed running behavior label")
        thread_complete_idx = self.core.index("\u2705 Thread N complete may not be emitted")
        self.assertGreater(c26_idx, obs_idx,
            "C26: blank-OBS prohibition must appear after the OBS rung label")
        self.assertLess(c26_idx, thread_complete_idx,
            "C26: blank-OBS prohibition must appear before the Thread N complete gate")


class TestC27RealEndpointOBS(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c27_mock_does_not_satisfy_endpoint_obs(self):
        self.assertIn(
            "mocked",
            self.core,
            "C27: OBS gate must state that a mocked network call does not satisfy the gate when the criterion names a real endpoint")

    def test_c27_positioned_in_obs_section(self):
        c27_idx = self.core.index("mocked")
        obs_idx = self.core.index("Upon writing the observed running behavior label")
        thread_complete_idx = self.core.index("\u2705 Thread N complete may not be emitted")
        self.assertGreater(c27_idx, obs_idx,
            "C27: mock-endpoint prohibition must appear after the OBS rung label")
        self.assertLess(c27_idx, thread_complete_idx,
            "C27: mock-endpoint prohibition must appear before the Thread N complete gate")


class TestC28TestFailureDismissal(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c28_failing_test_must_be_fixed_or_acknowledged(self):
        self.assertIn(
            "every failing test must be fixed or explicitly acknowledged",
            self.core,
            "C28: protocol must require all failing tests to be fixed or explicitly acknowledged before Thread N complete or Manifest exhausted")

    def test_c28_dismissal_prohibited(self):
        self.assertIn(
            "dismissing a failing test as unrelated without an explicit written acknowledgment is a protocol violation",
            self.core,
            "C28: must explicitly prohibit dismissing a failing test as unrelated without acknowledgment")


if __name__ == "__main__":
    unittest.main()
