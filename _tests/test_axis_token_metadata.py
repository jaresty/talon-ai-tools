"""Specifying tests for AXIS_TOKEN_METADATA (ADR-0155).

One describe-block per axis migration loop (T-3 through T-8).
Each block verifies coverage, schema conformance, and key distinctions.
"""

import unittest

from lib.axisConfig import AXIS_TOKEN_METADATA, AXIS_KEY_TO_VALUE


class CompletenessAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-3: completeness axis has structured metadata for all 7 tokens."""

    AXIS = "completeness"
    EXPECTED_TOKENS = {"deep", "full", "gist", "max", "minimal", "narrow", "skim"}

    def setUp(self):
        self.meta = AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_completeness_metadata_covers_all_tokens(self):
        """All 7 completeness tokens must have metadata entries — no silent omissions."""
        self.assertEqual(
            set(self.meta.keys()),
            self.EXPECTED_TOKENS,
            f"completeness metadata keys mismatch — "
            f"missing: {self.EXPECTED_TOKENS - set(self.meta.keys())}, "
            f"extra: {set(self.meta.keys()) - self.EXPECTED_TOKENS}",
        )

    def test_completeness_metadata_schema_conformance(self):
        """Each completeness token must have definition (str) + heuristics (list) + distinctions (list)."""
        for token, data in self.meta.items():
            with self.subTest(token=token):
                self.assertIn("definition", data, f"{token} must have definition")
                self.assertIn("heuristics", data, f"{token} must have heuristics")
                self.assertIn("distinctions", data, f"{token} must have distinctions")
                self.assertIsInstance(data["definition"], str, f"{token} definition must be str")
                self.assertTrue(data["definition"].strip(), f"{token} definition must not be empty")
                self.assertIsInstance(data["heuristics"], list, f"{token} heuristics must be list")
                self.assertGreater(len(data["heuristics"]), 0, f"{token} must have at least one heuristic")
                self.assertIsInstance(data["distinctions"], list, f"{token} distinctions must be list")
                for d in data["distinctions"]:
                    self.assertIn("token", d, f"{token} distinction must have token key")
                    self.assertIn("note", d, f"{token} distinction must have note key")

    def test_gist_distinguishes_from_skim(self):
        """gist must distinguish itself from skim (gist=brief but complete; skim=light pass)."""
        gist = self.meta.get("gist", {})
        distinction_tokens = [d["token"] for d in gist.get("distinctions", [])]
        self.assertIn("skim", distinction_tokens, "gist distinctions must reference skim")

    def test_full_distinguishes_from_max_and_deep(self):
        """full must distinguish from both max and deep."""
        full = self.meta.get("full", {})
        distinction_tokens = [d["token"] for d in full.get("distinctions", [])]
        self.assertIn("max", distinction_tokens, "full distinctions must reference max")
        self.assertIn("deep", distinction_tokens, "full distinctions must reference deep")


if __name__ == "__main__":
    unittest.main()
