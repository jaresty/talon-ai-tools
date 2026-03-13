"""Specifying tests for AXIS_TOKEN_METADATA (ADR-0155).

One describe-block per axis migration loop (T-3 through T-8).
Each block verifies coverage, schema conformance, and key distinctions.
"""

import unittest

from lib.axisConfig import AXIS_TOKEN_METADATA


class CompletenessAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-3: completeness axis has structured metadata for all 7 tokens."""

    AXIS = "completeness"
    EXPECTED_TOKENS = {
        "deep",
        "full",
        "gist",
        "grow",
        "max",
        "minimal",
        "narrow",
        "skim",
    }

    def setUp(self):
        self.meta = AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_completeness_metadata_covers_all_tokens(self):
        """All 8 completeness tokens must have metadata entries — no silent omissions."""
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
                self.assertIsInstance(
                    data["definition"], str, f"{token} definition must be str"
                )
                self.assertTrue(
                    data["definition"].strip(), f"{token} definition must not be empty"
                )
                self.assertIsInstance(
                    data["heuristics"], list, f"{token} heuristics must be list"
                )
                self.assertGreater(
                    len(data["heuristics"]),
                    0,
                    f"{token} must have at least one heuristic",
                )
                self.assertIsInstance(
                    data["distinctions"], list, f"{token} distinctions must be list"
                )
                for d in data["distinctions"]:
                    self.assertIn(
                        "token", d, f"{token} distinction must have token key"
                    )
                    self.assertIn("note", d, f"{token} distinction must have note key")

    def test_gist_distinguishes_from_skim(self):
        """gist must distinguish itself from skim (gist=brief but complete; skim=light pass)."""
        gist = self.meta.get("gist", {})
        distinction_tokens = [d["token"] for d in gist.get("distinctions", [])]
        self.assertIn(
            "skim", distinction_tokens, "gist distinctions must reference skim"
        )

    def test_full_distinguishes_from_max_and_deep(self):
        """full must distinguish from both max and deep."""
        full = self.meta.get("full", {})
        distinction_tokens = [d["token"] for d in full.get("distinctions", [])]
        self.assertIn("max", distinction_tokens, "full distinctions must reference max")
        self.assertIn(
            "deep", distinction_tokens, "full distinctions must reference deep"
        )


class ChannelAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-4: channel axis has structured metadata for all 18 tokens."""

    AXIS = "channel"
    EXPECTED_TOKENS = {
        "adr",
        "code",
        "codetour",
        "diagram",
        "gherkin",
        "html",
        "image",
        "jira",
        "notebook",
        "plain",
        "presenterm",
        "remote",
        "shellscript",
        "sketch",
        "slack",
        "svg",
        "sync",
        "video",
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
                self.assertTrue(
                    data["definition"].strip(), f"{token} definition must not be empty"
                )
                self.assertGreater(
                    len(data["heuristics"]),
                    0,
                    f"{token} must have at least one heuristic",
                )

    def test_sketch_distinguishes_from_diagram(self):
        """sketch must distinguish from diagram (sketch=D2; diagram=Mermaid)."""
        sketch = self.meta.get("sketch", {})
        distinction_tokens = [d["token"] for d in sketch.get("distinctions", [])]
        self.assertIn(
            "diagram", distinction_tokens, "sketch distinctions must reference diagram"
        )

    def test_presenterm_distinguishes_from_sync(self):
        """presenterm must distinguish from sync (presenterm=deck artifact; sync=session plan)."""
        presenterm = self.meta.get("presenterm", {})
        distinction_tokens = [d["token"] for d in presenterm.get("distinctions", [])]
        self.assertIn(
            "sync", distinction_tokens, "presenterm distinctions must reference sync"
        )


class DirectionalAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-5: directional axis has structured metadata for all 16 tokens."""

    AXIS = "directional"
    EXPECTED_TOKENS = {
        "bog",
        "dig",
        "dip bog",
        "dip ong",
        "dip rog",
        "fig",
        "fip bog",
        "fip ong",
        "fip rog",
        "fly bog",
        "fly ong",
        "fly rog",
        "fog",
        "jog",
        "ong",
        "rog",
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
                self.assertTrue(
                    data["definition"].strip(), f"{token} definition must not be empty"
                )
                self.assertGreater(
                    len(data["heuristics"]),
                    0,
                    f"{token} must have at least one heuristic",
                )

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
    """ADR-0155 T-6: scope axis has structured metadata for all 14 tokens."""

    AXIS = "scope"
    EXPECTED_TOKENS = {
        "act",
        "agent",
        "assume",
        "cross",
        "dam",
        "fail",
        "good",
        "mean",
        "motifs",
        "stable",
        "struct",
        "thing",
        "time",
        "view",
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
        self.assertIn(
            "struct", distinction_tokens, "cross must distinguish from struct"
        )
        self.assertIn(
            "motifs", distinction_tokens, "cross must distinguish from motifs"
        )


class FormAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-7: form axis has structured metadata for all 39 tokens."""

    AXIS = "form"
    EXPECTED_TOKENS = {
        "actions",
        "activities",
        "bug",
        "bullets",
        "cards",
        "case",
        "checklist",
        "cocreate",
        "commit",
        "contextualise",
        "coupling",
        "direct",
        "facilitate",
        "faq",
        "formats",
        "ghost",
        "indirect",
        "ladder",
        "log",
        "merge",
        "prep",
        "questions",
        "quiz",
        "recipe",
        "scaffold",
        "socratic",
        "spike",
        "story",
        "table",
        "taxonomy",
        "test",
        "tight",
        "timeline",
        "twin",
        "variants",
        "vet",
        "visual",
        "walkthrough",
        "wardley",
        "wasinawa",
    }

    def setUp(self):
        self.meta = AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_form_metadata_covers_all_tokens(self):
        """All 39 form tokens must have metadata entries."""
        self.assertEqual(
            set(self.meta.keys()),
            self.EXPECTED_TOKENS,
            f"form metadata keys mismatch — "
            f"missing: {self.EXPECTED_TOKENS - set(self.meta.keys())}, "
            f"extra: {set(self.meta.keys()) - self.EXPECTED_TOKENS}",
        )

    def test_form_metadata_schema_conformance(self):
        """Each form token must have definition + heuristics + distinctions."""
        for token, data in self.meta.items():
            with self.subTest(token=token):
                self.assertIn("definition", data)
                self.assertIn("heuristics", data)
                self.assertIn("distinctions", data)
                self.assertTrue(data["definition"].strip())
                self.assertGreater(len(data["heuristics"]), 0)

    def test_direct_distinguishes_from_indirect(self):
        """direct must distinguish from indirect."""
        direct = self.meta.get("direct", {})
        distinction_tokens = [d["token"] for d in direct.get("distinctions", [])]
        self.assertIn(
            "indirect", distinction_tokens, "direct must distinguish from indirect"
        )

    def test_visual_distinguishes_from_diagram(self):
        """visual must distinguish from diagram channel."""
        visual = self.meta.get("visual", {})
        distinction_tokens = [d["token"] for d in visual.get("distinctions", [])]
        self.assertIn(
            "diagram", distinction_tokens, "visual must distinguish from diagram"
        )

    def test_socratic_distinguishes_from_questions(self):
        """socratic must distinguish from questions form."""
        socratic = self.meta.get("socratic", {})
        distinction_tokens = [d["token"] for d in socratic.get("distinctions", [])]
        self.assertIn(
            "questions", distinction_tokens, "socratic must distinguish from questions"
        )


class MethodAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-8: method axis has structured metadata for all 82 tokens."""

    AXIS = "method"
    EXPECTED_TOKENS = {
        "abduce",
        "actors",
        "adversarial",
        "afford",
        "align",
        "amorph",
        "analog",
        "analysis",
        "argue",
        "balance",
        "bias",
        "boom",
        "bound",
        "calc",
        "cite",
        "clash",
        "cluster",
        "compare",
        "control",
        "converge",
        "crystal",
        "deduce",
        "depends",
        "mint",
        "diagnose",
        "dimension",
        "domains",
        "drift",
        "effects",
        "enforce",
        "experimental",
        "field",
        "flow",
        "gap",
        "ground",
        "grove",
        "induce",
        "inversion",
        "jobs",
        "mapping",
        "meld",
        "melody",
        "mesh",
        "mark",
        "migrate",
        "mod",
        "models",
        "objectivity",
        "operations",
        "order",
        "origin",
        "observe",
        "perturb",
        "polar",
        "preserve",
        "prioritize",
        "probability",
        "product",
        "pulse",
        "reify",
        "release",
        "ritual",
        "resilience",
        "reset",
        "rigor",
        "risks",
        "robust",
        "root",
        "seep",
        "sever",
        "shear",
        "shift",
        "simulation",
        "snag",
        "split",
        "spur",
        "sweep",
        "systemic",
        "thrust",
        "trace",
        "triage",
        "unknowns",
        "verify",
        "yield",
    }

    def setUp(self):
        self.meta = AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_method_metadata_covers_all_tokens(self):
        """All 82 method tokens must have metadata entries."""
        self.assertEqual(
            set(self.meta.keys()),
            self.EXPECTED_TOKENS,
            f"method metadata keys mismatch — "
            f"missing: {self.EXPECTED_TOKENS - set(self.meta.keys())}, "
            f"extra: {set(self.meta.keys()) - self.EXPECTED_TOKENS}",
        )

    def test_method_metadata_schema_conformance(self):
        """Each method token must have definition + heuristics + distinctions."""
        for token, data in self.meta.items():
            with self.subTest(token=token):
                self.assertIn("definition", data)
                self.assertIn("heuristics", data)
                self.assertIn("distinctions", data)
                self.assertTrue(data["definition"].strip())
                self.assertGreater(len(data["heuristics"]), 0)

    def test_abduce_distinguishes_from_diagnose(self):
        """abduce must distinguish from diagnose (abduce=compare hypotheses; diagnose=narrow to one)."""
        abduce = self.meta.get("abduce", {})
        distinction_tokens = [d["token"] for d in abduce.get("distinctions", [])]
        self.assertIn(
            "diagnose", distinction_tokens, "abduce must distinguish from diagnose"
        )

    def test_diagnose_distinguishes_from_abduce(self):
        """diagnose must distinguish from abduce."""
        diagnose = self.meta.get("diagnose", {})
        distinction_tokens = [d["token"] for d in diagnose.get("distinctions", [])]
        self.assertIn(
            "abduce", distinction_tokens, "diagnose must distinguish from abduce"
        )

    def test_compare_distinguishes_from_converge(self):
        """compare must distinguish from converge."""
        compare = self.meta.get("compare", {})
        distinction_tokens = [d["token"] for d in compare.get("distinctions", [])]
        self.assertIn(
            "converge", distinction_tokens, "compare must distinguish from converge"
        )


if __name__ == "__main__":
    unittest.main()
