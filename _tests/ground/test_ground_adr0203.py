"""ADR-0203: Close four escape routes identified in SWE transcript analysis.

Thread 1: similarity-argument completion prohibition
Thread 2: thread-complete-without-green-run explicit block
Thread 3: unlabeled prose mid-cycle prohibition
Thread 4: V-emitted-without-file-write gate
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestSimilarityArgumentCompletion(unittest.TestCase):
    """Thread 1: declaring a thread complete via cross-thread similarity is prohibited."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_similarity_argument_prohibited(self):
        self.assertIn(
            "similarity",
            self.prompt,
            "Protocol must prohibit declaring a thread complete via similarity argument",
        )

    def test_each_thread_requires_own_descent(self):
        self.assertIn(
            "each thread requires its own full descent",
            self.prompt,
            "Protocol must require each thread to complete its own full OBR descent",
        )


class TestThreadCompleteWithoutGreenRun(unittest.TestCase):
    """Thread 2: most-recent exec_observed must show zero failures before Thread N complete."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_most_recent_exec_observed_must_pass(self):
        self.assertIn(
            "most recent \U0001f534 Execution observed: in the current cycle shows any test failure",
            self.prompt,
            "Protocol must reference the most recent exec_observed in the current cycle as the Thread N complete block gate",
        )

    def test_no_prose_reasoning_lifts_block(self):
        self.assertIn(
            "no intervening prose, reasoning, or cross-thread argument lifts this block",
            self.prompt,
            "Protocol must state that no prose or reasoning lifts the Thread N complete block",
        )


class TestUnlabeledProseMidCycle(unittest.TestCase):
    """Thread 3: prose reasoning between rung labels is a protocol violation."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_unlabeled_prose_prohibited(self):
        self.assertIn(
            "prose reasoning, debugging narration, planning, or any other unlabeled text between rung labels",
            self.prompt,
            "Protocol must explicitly prohibit unlabeled prose between rung labels",
        )

    def test_content_must_be_rung_artifact_type(self):
        self.assertIn(
            "must be of that rung's artifact type",
            self.prompt,
            "Protocol must require all inter-label content to be of the rung's artifact type",
        )


class TestVCompleteWithoutFileWrite(unittest.TestCase):
    """Thread 4: V sentinel requires a file-write tool call result in the current response."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_file_write_required_before_v_complete(self):
        self.assertIn(
            "file-write tool call result",
            self.prompt,
            "Protocol must require a file-write tool call result before V complete",
        )

    def test_prose_claim_does_not_satisfy_v_gate(self):
        self.assertIn(
            "artifact content appearing in prose without a file-write tool call does not satisfy this gate",
            self.prompt,
            "Protocol must state prose artifact claim does not satisfy the V gate",
        )


if __name__ == "__main__":
    unittest.main()
