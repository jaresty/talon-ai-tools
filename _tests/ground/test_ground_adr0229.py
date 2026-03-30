"""Tests for ADR-0229: write_authorized gate requires cited artifact type to match the file.

T1 write-authorized-type-crosscheck: gate text requires the cited artifact type to match
   the artifact type of the named file as determined by the rung table.
"""
import unittest

from _tests.ground.ground_test_base import GroundADRTestBase

from lib.groundPrompt import _SENTINEL_GATES, build_ground_prompt


class TestThread1_WriteAuthorizedTypeCrosscheck(GroundADRTestBase):
    """write_authorized gate requires cited type to match the actual file's artifact type."""

    def setUp(self):
        self.gate = _SENTINEL_GATES["write_authorized"]
        self.prompt = build_ground_prompt()

    def test_gate_requires_cited_type_matches_file(self):
        self.assertDetects("cited artifact type must match", self.gate)

    def test_gate_references_rung_table_as_authority(self):
        self.assertIn("rung table", self.gate)

    def test_gate_voids_on_type_mismatch(self):
        self.assertIn("does not match the file being written", self.gate)

    def test_gate_propagated_to_prompt(self):
        self.assertIn("cited artifact type must match", self.prompt)


if __name__ == "__main__":
    unittest.main()
