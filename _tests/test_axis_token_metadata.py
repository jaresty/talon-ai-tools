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
        "taper",
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
    """ADR-0155 T-4: channel axis has structured metadata for all 23 tokens."""

    AXIS = "channel"
    EXPECTED_TOKENS = {
        "adr",
        "agent",
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
        "skill",
        "slack",
        "store",
        "svg",
        "sync",
        "video",
        "zettel",
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
    """ADR-0155 T-6: scope axis has structured metadata for all 18 tokens (lever added; jobs/product moved from method)."""

    AXIS = "scope"
    EXPECTED_TOKENS = {
        "act",
        "authority",
        "assume",
        "cross",
        "dam",
        "fail",
        "good",
        "jobs",
        "mean",
        "motifs",
        "product",
        "storage",
        "stable",
        "lever",
        "struct",
        "thing",
        "time",
        "view",
    }

    def setUp(self):
        self.meta = _AXIS_TOKEN_METADATA.get(self.AXIS, {})

    def test_scope_metadata_covers_all_tokens(self):
        """All 18 scope tokens must have metadata entries."""
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
        "log",
        "merge",
        "snap",
        "prep",
        "questions",
        "quiz",
        "scorecard",
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

    def test_socratic_distinguishes_from_questions(self):
        """socratic must distinguish from questions form."""
        socratic = self.meta.get("socratic", {})
        distinction_tokens = [d["token"] for d in socratic.get("distinctions", [])]
        self.assertIn(
            "questions", distinction_tokens, "socratic must distinguish from questions"
        )


class MethodAxisMetadataTests(unittest.TestCase):
    """ADR-0155 T-8: method axis has structured metadata for all 99 tokens (enforce added ADR-0231; mu/paradox/mint/root added; gate/chain/atomic added ADR-0224; automate/gloss revived; gloss/mu/paradox AXIS_TOKEN_METADATA entries added; falsify added ADR-0227; risks/resilience/jobs/product moved out)."""

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
        "atomic",
        "automate",
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
        "effects",
        "enforce",
        "enter",
        "experimental",
        "field",
        "flow",
        "fourfold",
        "chain",
        "falsify",
        "gap",
        "gate",
        "gloss",
        "grain",
        "ground",
        "grove",
        "hollow",
        "induce",
        "inversion",
        "lateral",
        "mapping",
        "meld",
        "melody",
        "mesh",
        "mark",
        "migrate",
        "mod",
        "models",
        "mu",
        "objectivity",
        "operations",
        "orbit",
        "order",
        "origin",
        "paradox",
        "perturb",
        "polar",
        "preserve",
        "prioritize",
        "probability",
        "pulse",
        "reify",
        "release",
        "ritual",
        "ladder",
        "sense",
        "reset",
        "rigor",
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
        """All 98 method tokens must have metadata entries (enforce added ADR-0231; mu/paradox/mint/root added; gate/chain/atomic added ADR-0224; automate/gloss revived; hollow/distill added; distill removed ADR-0235 — constraints absorbed into hollow; risks/resilience/jobs/product moved out)."""
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
        """Ground definition must require evidence before claiming completion."""
        ground = self.meta.get("ground", {})
        definition = ground.get("definition", "")
        self.assertIn(
            "derive",
            definition,
            "ground definition must derive sentinels from principles",
        )

    def test_ground_definition_ladder_present(self):
        """ground definition must still contain the full enumerated ladder."""
        ground = self.meta.get("ground", {})
        # ADR-0217: ladder rungs are derived from P1-P6, not explicitly stated.
        # This echo check removed - trust derivation, not explicit strings.

    def test_hollow_allowlist_clause_names_governed_action(self):
        """hollow's allow-list clause must name 'where a clause names an action' so the allow-list is verifiable as governing the correct action (hollow self-audit finding)."""
        hollow = self.meta.get("hollow", {})
        definition = hollow.get("definition", "")
        self.assertIn(
            "where a clause names an action",
            definition,
            "hollow allow-list clause must name the governed action to be verifiable by inspection",
        )

    def test_hollow_structural_vocabulary_requirement(self):
        """hollow's vocabulary requirement must name an observable distinguishing structural from domain-specific terms (hollow self-audit finding)."""
        hollow = self.meta.get("hollow", {})
        definition = hollow.get("definition", "")
        self.assertIn(
            "meaning does not change when the instruction's subject matter changes",
            definition,
            "hollow vocabulary clause must name the observable that distinguishes compliant from non-compliant terms",
        )

    def test_atomic_candidate_limited_to_first_failure(self):
        """atomic must explicitly limit the candidate to the first failure only — other failures in the same result may not expand the candidate (hollow audit finding)."""
        atomic = self.meta.get("atomic", {})
        definition = atomic.get("definition", "")
        self.assertIn(
            "other failures visible in the same result are not in scope for this step",
            definition,
            "atomic must name the observable that limits the candidate to the first failure only",
        )

    def test_atomic_candidate_scoped_to_observed_failure(self):
        """atomic's candidate change must be scoped to the specific error or assertion in the governing FAIL — changes that fix unobserved assertions are not permitted (hollow audit finding)."""
        atomic = self.meta.get("atomic", {})
        definition = atomic.get("definition", "")
        self.assertIn(
            "a failure not yet observed in a prior tool-executed run result has not been shown to govern",
            definition,
            "atomic must explicitly prohibit changes that fix assertions not present in the governing FAIL result",
        )

    def test_atomic_smaller_change_insufficient_against_current_fail(self):
        """atomic must require that the smaller change's insufficiency be demonstrated against the current FAIL only — future failures may not be cited (hollow audit finding)."""
        atomic = self.meta.get("atomic", {})
        definition = atomic.get("definition", "")
        self.assertIn(
            "an insufficiency claim is not permitted until a tool-executed result showing the smaller change appears above it in the transcript",
            definition,
            "atomic must require a tool-executed run of the smaller change before an insufficiency claim is permitted",
        )

    def test_falsify_empty_transcript_gap_closed(self):
        """falsify must block file modifications when no execution result exists in the transcript — the 'would change the outcome of any execution result' condition is vacuously ungoverned when the result set is empty (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "if no execution result exists in the transcript above that tool call, the tool call is not permitted",
            definition,
            "falsify must explicitly block file modifications when no execution result exists in the transcript",
        )

    def test_falsify_slower_check_excludes_compiler_artifacts(self):
        """falsify's slower-check clause must require a named runnable test case producing a named failure message, not 'test or assertion' which admits compiler checks and type annotations (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "produces a named failure message",
            definition,
            "falsify slower-check clause must name the observable that excludes compiler artifacts",
        )

    def test_falsify_self_refuting_closes_entry(self):
        """falsify's self-refuting description clause must name a structural gate preventing a candidate check from appearing after a self-refuting description (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "no candidate check may be named until a non-self-refuting slower check appears",
            definition,
            "falsify self-refuting clause must structurally prevent candidate check from appearing after invalidation",
        )

    def test_falsify_direct_invocation_observable(self):
        """falsify's FAIL source clause must name the observable distinguishing direct artifact invocation from a tool call that reads or displays prior execution output (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "directly invokes the artifact's execution",
            definition,
            "falsify must name the observable that distinguishes direct invocation from status display",
        )

    def test_hollow_root_criterion_encodes_domain_scope(self):
        """hollow's root criterion sentence must name its domain of application so the domain-agnostic language clause is derivable from the criterion rather than independently asserted (ADR-0235 mint/root/collapse finding)."""
        hollow = self.meta.get("hollow", {})
        definition = hollow.get("definition", "")
        root_criterion_sentence = definition.split(".")[0] if "." in definition else definition
        self.assertIn(
            "any domain where instructions govern model behavior",
            root_criterion_sentence,
            "hollow root criterion must name its domain of application within the criterion sentence itself",
        )


if __name__ == "__main__":
    unittest.main()
