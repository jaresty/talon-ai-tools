"""Specifying tests for AXIS_TOKEN_METADATA (ADR-0155).

One describe-block per axis migration loop (T-3 through T-8).
Each block verifies coverage, schema conformance, and key distinctions.
"""

import unittest

from lib.axisConfig import axis_token_metadata as _axis_token_metadata

_AXIS_TOKEN_METADATA = _axis_token_metadata()


class CompletenessAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-3: completeness axis has structured metadata for all 9 tokens (triage moved from method)."""

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
        "triage",
        "zoom",
    }

    def setUp(self):
        self.meta = _AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_completeness_metadata_covers_all_tokens(self):
        """All 9 completeness tokens must have metadata entries — no silent omissions."""
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

    def test_triage_in_completeness_not_method(self):
        """triage must be a completeness token, not a method token (moved in ADR-0163)."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE

        self.assertIn(
            "triage",
            AXIS_KEY_TO_VALUE.get("completeness", {}),
            "triage must be in completeness AXIS_KEY_TO_VALUE",
        )
        self.assertNotIn(
            "triage",
            AXIS_KEY_TO_VALUE.get("method", {}),
            "triage must NOT be in method AXIS_KEY_TO_VALUE",
        )

    def test_triage_distinguishes_from_grow(self):
        """triage must distinguish from grow (triage=stakes-weighted depth; grow=demand-driven depth)."""
        triage = self.meta.get("triage", {})
        distinction_tokens = [d["token"] for d in triage.get("distinctions", [])]
        self.assertIn(
            "grow", distinction_tokens, "triage distinctions must reference grow"
        )


class ChannelAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-4: channel axis has structured metadata for all 20 tokens."""

    AXIS = "channel"
    EXPECTED_TOKENS = {
        "adr",
        "code",
        "codetour",
        "diagram",
        "draw",
        "formal",
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
        "store",
        "svg",
        "sync",
        "video",
    }

    def setUp(self):
        self.meta = _AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_channel_metadata_covers_all_tokens(self):
        """All 20 channel tokens must have metadata entries."""
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
        self.meta = _AXIS_TOKEN_METADATA.get(self.AXIS, {})

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
    """ADR-0155 T-6: scope axis has structured metadata for all 15 tokens (storage added)."""

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
        "storage",
        "stable",
        "struct",
        "thing",
        "time",
        "view",
    }

    def setUp(self):
        self.meta = _AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_scope_metadata_covers_all_tokens(self):
        """All 15 scope tokens must have metadata entries."""
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

    def test_storage_distinguishes_from_stable(self):
        """storage must distinguish from stable (storage=what must be made durable; stable=what IS currently stable)."""
        persist = self.meta.get("storage", {})
        distinction_tokens = [d["token"] for d in persist.get("distinctions", [])]
        self.assertIn(
            "stable", distinction_tokens, "persist must distinguish from stable"
        )


class FormAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-7: form axis has structured metadata for all 38 tokens."""

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
        "log",
        "merge",
        "snap",
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
        "walkthrough",
        "wardley",
        "wasinawa",
    }

    def setUp(self):
        self.meta = _AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_form_metadata_covers_all_tokens(self):
        """All 38 form tokens must have metadata entries."""
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

    def test_socratic_distinguishes_from_questions(self):
        """socratic must distinguish from questions form."""
        socratic = self.meta.get("socratic", {})
        distinction_tokens = [d["token"] for d in socratic.get("distinctions", [])]
        self.assertIn(
            "questions", distinction_tokens, "socratic must distinguish from questions"
        )


class MethodAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-8: method axis has structured metadata for all 86 tokens (enforce/observe retired ADR-0162; triage moved to completeness, automate added; ladder/visual moved from form; behave added; survive added; enter added)."""

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
        "behave",
        "bias",
        "boom",
        "bound",
        "calc",
        "cite",
        "clash",
        "collapse",
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
        "automate",
        "effects",
        "enter",
        "experimental",
        "field",
        "flow",
        "fourfold",
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
        "orbit",
        "order",
        "origin",
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
        "ladder",
        "resilience",
        "sense",
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
        "square",
        "spur",
        "survive",
        "sweep",
        "systemic",
        "thrust",
        "trace",
        "unknowns",
        "verify",
        "visual",
        "yield",
    }

    def setUp(self):
        self.meta = _AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_method_metadata_covers_all_tokens(self):
        """All 88 method tokens must have metadata entries (enforce/observe retired ADR-0162; triage moved to completeness, automate added; ladder/visual moved from form; survive added; fourfold/orbit/square added)."""
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

    def test_ground_definition_states_governing_principle(self):
        """ground definition must state the evaluation-independence principle: V can be
        evaluated against O without consulting I, and label the enumerated ladder as its
        instantiation, not as the rule itself.

        ADR-0174: minimal spec experiment — evaluation-independence ("without consulting I")
        and ladder-as-instantiation ("instantiates") are intentionally omitted from the
        minimal spec. This test is relaxed to only check for the sentinel checkpoint phrase,
        which is present in both full and minimal specs. Re-tighten if experiment restores
        full spec.
        """
        ground = self.meta.get("ground", {})
        definition = ground.get("definition", "")
        self.assertIn(
            "Validation artifact V complete",
            definition,
            "ground definition must require the checkpoint phrase",
        )

    def test_ground_definition_ladder_present(self):
        """ground definition must still contain the full enumerated ladder."""
        ground = self.meta.get("ground", {})
        definition = ground.get("definition", "")
        for rung in [
            "prose",
            "criteria",
            "formal notation",
            "executable validation",
            "validation run observation",
            "executable implementation",
            "observed running behavior",
        ]:
            self.assertIn(rung, definition, f"ground ladder must include rung: {rung}")


if __name__ == "__main__":
    unittest.main()
