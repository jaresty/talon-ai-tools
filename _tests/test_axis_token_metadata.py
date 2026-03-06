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


class ChannelAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-4: channel axis has structured metadata for all 18 tokens."""

    AXIS = "channel"
    EXPECTED_TOKENS = {
        "adr", "code", "codetour", "diagram", "gherkin", "html", "image",
        "jira", "notebook", "plain", "presenterm", "remote", "shellscript",
        "sketch", "slack", "svg", "sync", "video",
    }

    def setUp(self):
        self.meta = AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_channel_metadata_covers_all_tokens(self):
        """All 18 channel tokens must have metadata entries."""
        self.assertEqual(
            set(self.meta.keys()),
            self.EXPECTED_TOKENS,
            f"channel metadata keys mismatch — "
            f"missing: {self.EXPECTED_TOKENS - set(self.meta.keys())}, "
            f"extra: {set(self.meta.keys()) - self.EXPECTED_TOKENS}",
        )

    def test_channel_metadata_schema_conformance(self):
        """Each channel token must have definition + heuristics + distinctions."""
        for token, data in self.meta.items():
            with self.subTest(token=token):
                self.assertIn("definition", data, f"{token} must have definition")
                self.assertIn("heuristics", data, f"{token} must have heuristics")
                self.assertIn("distinctions", data, f"{token} must have distinctions")
                self.assertTrue(data["definition"].strip(), f"{token} definition must not be empty")
                self.assertGreater(len(data["heuristics"]), 0, f"{token} must have at least one heuristic")

    def test_sketch_distinguishes_from_diagram(self):
        """sketch must distinguish from diagram (sketch=D2; diagram=Mermaid)."""
        sketch = self.meta.get("sketch", {})
        distinction_tokens = [d["token"] for d in sketch.get("distinctions", [])]
        self.assertIn("diagram", distinction_tokens, "sketch distinctions must reference diagram")

    def test_presenterm_distinguishes_from_sync(self):
        """presenterm must distinguish from sync (presenterm=deck artifact; sync=session plan)."""
        presenterm = self.meta.get("presenterm", {})
        distinction_tokens = [d["token"] for d in presenterm.get("distinctions", [])]
        self.assertIn("sync", distinction_tokens, "presenterm distinctions must reference sync")


class DirectionalAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-5: directional axis has structured metadata for all 16 tokens."""

    AXIS = "directional"
    EXPECTED_TOKENS = {
        "bog", "dig", "dip bog", "dip ong", "dip rog",
        "fig", "fip bog", "fip ong", "fip rog",
        "fly bog", "fly ong", "fly rog",
        "fog", "jog", "ong", "rog",
    }

    def setUp(self):
        self.meta = AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_directional_metadata_covers_all_tokens(self):
        """All 16 directional tokens must have metadata entries."""
        self.assertEqual(
            set(self.meta.keys()),
            self.EXPECTED_TOKENS,
            f"directional metadata keys mismatch — "
            f"missing: {self.EXPECTED_TOKENS - set(self.meta.keys())}, "
            f"extra: {set(self.meta.keys()) - self.EXPECTED_TOKENS}",
        )

    def test_directional_metadata_schema_conformance(self):
        """Each directional token must have definition + heuristics + distinctions."""
        for token, data in self.meta.items():
            with self.subTest(token=token):
                self.assertIn("definition", data)
                self.assertIn("heuristics", data)
                self.assertIn("distinctions", data)
                self.assertTrue(data["definition"].strip(), f"{token} definition must not be empty")
                self.assertGreater(len(data["heuristics"]), 0, f"{token} must have at least one heuristic")

    def test_bog_distinguishes_from_rog_and_ong(self):
        """bog must distinguish from both rog and ong (bog = full horizontal span)."""
        bog = self.meta.get("bog", {})
        distinction_tokens = [d["token"] for d in bog.get("distinctions", [])]
        self.assertIn("rog", distinction_tokens, "bog must distinguish from rog")
        self.assertIn("ong", distinction_tokens, "bog must distinguish from ong")

    def test_fig_distinguishes_from_fog_and_dig(self):
        """fig must distinguish from both fog and dig (fig = full vertical span)."""
        fig = self.meta.get("fig", {})
        distinction_tokens = [d["token"] for d in fig.get("distinctions", [])]
        self.assertIn("fog", distinction_tokens, "fig must distinguish from fog")
        self.assertIn("dig", distinction_tokens, "fig must distinguish from dig")


class ScopeAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-6: scope axis has structured metadata for all 13 tokens."""

    AXIS = "scope"
    EXPECTED_TOKENS = {
        "act", "agent", "assume", "cross", "fail", "good",
        "mean", "motifs", "stable", "struct", "thing", "time", "view",
    }

    def setUp(self):
        self.meta = AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_scope_metadata_covers_all_tokens(self):
        """All 13 scope tokens must have metadata entries."""
        self.assertEqual(
            set(self.meta.keys()),
            self.EXPECTED_TOKENS,
            f"scope metadata keys mismatch — "
            f"missing: {self.EXPECTED_TOKENS - set(self.meta.keys())}, "
            f"extra: {set(self.meta.keys()) - self.EXPECTED_TOKENS}",
        )

    def test_scope_metadata_schema_conformance(self):
        """Each scope token must have definition + heuristics + distinctions."""
        for token, data in self.meta.items():
            with self.subTest(token=token):
                self.assertIn("definition", data)
                self.assertIn("heuristics", data)
                self.assertIn("distinctions", data)
                self.assertTrue(data["definition"].strip())
                self.assertGreater(len(data["heuristics"]), 0)

    def test_act_distinguishes_from_thing(self):
        """act must distinguish from thing (act=what entities do; thing=what entities exist)."""
        act = self.meta.get("act", {})
        distinction_tokens = [d["token"] for d in act.get("distinctions", [])]
        self.assertIn("thing", distinction_tokens, "act must distinguish from thing")

    def test_cross_distinguishes_from_struct_and_motifs(self):
        """cross must distinguish from both struct and motifs."""
        cross = self.meta.get("cross", {})
        distinction_tokens = [d["token"] for d in cross.get("distinctions", [])]
        self.assertIn("struct", distinction_tokens, "cross must distinguish from struct")
        self.assertIn("motifs", distinction_tokens, "cross must distinguish from motifs")


if __name__ == "__main__":
    unittest.main()
