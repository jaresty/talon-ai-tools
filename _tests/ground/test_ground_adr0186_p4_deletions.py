"""ADR-0186 Phase 4: P4-derivative prose deleted from ground prompt.

Only phrases fully subsumed by P4's type-based closed action set are deleted.
L31 (pre-existence gate) is NOT deleted — it specifies the exec_observed format
requirement which P4 does not cover.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestP4DerivativePhraseDeleted(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_l35_no_other_edits_at_ev_deleted(self):
        self.assertNotIn(
            "any edit to any other file at the EV rung is a protocol violation",
            self.prompt,
            "L35 explicit no-other-edits rule must be deleted — P4 EV type constraint subsumes it",
        )

    def test_l35_modifying_test_file_at_ev_deleted(self):
        self.assertNotIn(
            "modifying a previously-written test file at the EV rung",
            self.prompt,
            "L35 test-file-modification rule must be deleted — P4 EV type constraint subsumes it",
        )

    def test_meta_test_forward_gate_deleted(self):
        self.assertNotIn(
            "when any EI-rung edit targets a file that served as the EV artifact in any prior cycle",
            self.prompt,
            "Meta-test forward gate must be deleted — P4 EI type constraint subsumes it",
        )


if __name__ == "__main__":
    unittest.main()
