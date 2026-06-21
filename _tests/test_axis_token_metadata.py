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
        "demo",
        "diagram",
        "draw",
        "formal",
        "gherkin",
        "html",
        "image",
        "jira",
        "ledger",
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
    """ADR-0155 T-7: form axis has structured metadata for all 40 tokens."""

    AXIS = "form"
    EXPECTED_TOKENS = {
        "actions",
        "activities",
        "stage",
        "bug",
        "bullets",
        "cards",
        "chart",
        "case",
        "cheatsheet",
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
        "interactive",
        "log",
        "merge",
        "snap",
        "prep",
        "questions",
        "quiz",
        "scorecard",
        "slides",
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

    def test_cocreate_live_preview_clause(self):
        """cocreate definition must instruct model to start a server, handle existing server, and confirm URL."""
        cocreate = self.meta.get("cocreate", {})
        definition = cocreate.get("definition", "")
        self.assertIn(
            "start a local server",
            definition,
            "cocreate must instruct model to start a local server on first turn",
        )
        self.assertIn(
            "already running",
            definition,
            "cocreate must handle the case where a server is already running",
        )
        self.assertIn(
            "confirm the",
            definition,
            "cocreate must instruct model to confirm the URL before asking what to change next",
        )

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

    def test_quiz_definition_encodes_information_gap_root_criterion(self):
        """quiz definition must encode root criterion: genuine retrieval demand requiring explicit commitment."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "genuine retrieval demand for every concept",
            definition,
            "quiz definition must name the root criterion: genuine retrieval demand requiring reader commitment",
        )

    def test_quiz_definition_encodes_enumeration_instruction(self):
        """quiz definition must instruct model to enumerate named structural escape-route paths."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "enumerate every named structural path",
            definition,
            "quiz definition must instruct model to enumerate named structural paths before generating questions",
        )

    def test_quiz_definition_encodes_gap_reveal_structural_artifact(self):
        """quiz definition must name a structural sentence type for gap-reveal (not a cognitive act)."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "gap-reveal sentence",
            definition,
            "quiz definition must name 'gap-reveal sentence' as a structural artifact, not a cognitive act",
        )

    def test_quiz_definition_encodes_association_structural_artifact(self):
        """quiz definition must name a structural sentence type for association."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "association sentence",
            definition,
            "quiz definition must name 'association sentence' as a structural artifact",
        )

    def test_quiz_definition_encodes_concept_list(self):
        """quiz definition must require pre-declaring a numbered concept list before the first question."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "name the concepts to be covered as a numbered list",
            definition,
            "quiz definition must require enumerating concepts as a named list before the first question",
        )

    def test_quiz_definition_encodes_confirmation_marker(self):
        """quiz definition must name the structural confirmation marker string."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "✓ [concept name]",
            definition,
            "quiz definition must name '✓ [concept name]' as the addressable confirmation marker",
        )

    def test_quiz_definition_encodes_termination_criterion(self):
        """quiz definition must encode termination: every concept has either ✓ or gap-reveal, or explicit decline."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "every concept in the opening list has either a",
            definition,
            "quiz definition must name the dual termination criterion: ✓ marker or gap-reveal sentence per concept",
        )

    def test_quiz_definition_encodes_terminal_declaration(self):
        """quiz definition must require a terminal declaration with evaluator criterion."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "an evaluator determines completeness by comparing the terminal declaration against the opening list",
            definition,
            "quiz definition must require a terminal declaration as a closing structural artifact",
        )

    def test_quiz_definition_encodes_predict_line(self):
        """quiz definition must name Predict: as the structural commitment artifact (GP2 fix)."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "Predict: line",
            definition,
            "quiz definition must name 'Predict: line' as the structural commitment point artifact",
        )

    def test_quiz_definition_encodes_mutual_exclusion(self):
        """quiz ✓ trigger must use allow-list condition (complete/correct prediction), not deny-list 'no gap-reveal written'."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "write a gap-reveal sentence instead of",
            definition,
            "quiz ✓ trigger must name the allow-list condition and explicitly redirect to gap-reveal when any gap exists",
        )

    def test_quiz_definition_encodes_dual_termination_path(self):
        """quiz definition must allow termination when every concept has either ✓ or a gap-reveal (GP3 fix)."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "either a '✓ [concept name]' marker or a gap-reveal sentence",
            definition,
            "quiz definition must name both termination paths: ✓ marker OR gap-reveal sentence per concept",
        )

    def test_quiz_definition_encodes_first_concept_exemption(self):
        """quiz definition must specify first-concept association behavior (Agent 3 failure fix)."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "naming the opening-list number and name of the first concept whose understanding it enables",
            definition,
            "quiz definition must handle the first concept's association sentence — no prior concept exists",
        )

    def test_quiz_definition_encodes_association_tracking_prompt(self):
        """quiz definition must include tracking prompt before association sentence (Agent 2 failure fix)."""
        quiz = self.meta.get("quiz", {})
        definition = quiz.get("definition", "")
        self.assertIn(
            "name the numbers already used in prior association sentences",
            definition,
            "quiz definition must include tracking prompt to prevent number reuse in association sentences",
        )

    def test_quiz_main_definition_encodes_association_tracking_prompt(self):
        """quiz AXIS_KEY_TO_VALUE definition must include association tracking prompt."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "name the numbers already used in prior association sentences",
            definition,
            "quiz main definition must include tracking prompt to prevent number reuse in association sentences",
        )

    def test_quiz_definition_encodes_following_from_line(self):
        """quiz definition must require Following from: line before each question after the first."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "Following from:",
            definition,
            "quiz definition must require 'Following from:' line to chain questions into a sequence",
        )

    def test_quiz_definition_following_from_requires_restatement(self):
        """Following from: line must require a restatement of what the preceding reveal established, not just a quote."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "a one-sentence restatement of what that reveal established",
            definition,
            "quiz Following from: line must require a restatement, making it self-contained without scrolling back",
        )

    def test_quiz_definition_encodes_misconception_line(self):
        """quiz definition must require at least one Misconception: line per quiz."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "Misconception:",
            definition,
            "quiz definition must require 'Misconception:' line naming the specific incorrect belief",
        )

    def test_quiz_definition_encodes_why_line(self):
        """quiz definition must require a Why: line paired with Misconception:."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "Why:",
            definition,
            "quiz definition must require 'Why:' line stating the structural reason the misconception is wrong",
        )

    def test_quiz_definition_encodes_association_name_format(self):
        """quiz definition must require #N (Name): format for association sentences."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "#N (Name):",
            definition,
            "quiz definition must require '#N (Name):' format to include concept name alongside number",
        )

    def test_quiz_definition_encodes_hook_line(self):
        """quiz definition must require Hook: line for every concept except the first and the last."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "Hook:",
            definition,
            "quiz definition must require 'Hook:' line naming an opening-list concept not yet covered",
        )

    def test_quiz_definition_encodes_hook_quotes_phrase_from_answer(self):
        """Hook: clause must require quoting a specific phrase from the current answer, not just naming a concept."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "quoting a specific phrase from the current answer",
            definition,
            "Hook: clause must require quoting a specific phrase from the current answer to prevent inert concept announcements",
        )

    def test_quiz_definition_encodes_path_audit_per_question_check(self):
        """Path audit must require per-question check strings for paths (a) and (c), not global pre-closing intentions."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "before each question",
            definition,
            "quiz path audit must require a per-question check before each question for paths (a) and (c)",
        )

    def test_quiz_definition_encodes_misconception_precommitment(self):
        """Misconception/Why must be pre-committed before the first question to prevent silent omission."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "Before writing any question, name the concept",
            definition,
            "quiz definition must require naming the Misconception/Why concept before the first question",
        )

    def test_quiz_definition_encodes_confirmation_marker_allowlist(self):
        """✓ marker must use an allow-list condition (complete/correct prediction), not a deny-list trigger."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "only when the Predict: line states the complete and correct answer with no correction, addition, or nuance needed",
            definition,
            "quiz ✓ marker must fire on allow-list condition (complete/correct prediction), not deny-list ('no gap-reveal written')",
        )

    def test_quiz_definition_encodes_hook_last_concept_prohibition(self):
        """Hook: scoping must include explicit prohibition after the last concept's answer."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "a Hook: line must not appear after the last concept's answer",
            definition,
            "quiz Hook: scoping must explicitly prohibit Hook: after the last concept's answer",
        )

    def test_quiz_definition_encodes_goal_framing_cycle(self):
        """quiz opening must state the goal as a prediction/reveal/hook cycle."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "the goal is a cycle where each prediction creates a gap to resolve",
            definition,
            "quiz definition must name the goal as a prediction/reveal/hook cycle",
        )

    def test_quiz_definition_encodes_hook_purpose_not_announcement(self):
        """quiz definition must state Hook: opens the next gap rather than announcing the next concept."""
        from lib.axisConfig import AXIS_KEY_TO_VALUE
        definition = AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")
        self.assertIn(
            "opens the next gap rather than announcing the next concept",
            definition,
            "quiz definition must state Hook: purpose as opening next gap, not announcing next concept",
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
        "prism",
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
        "rebase",
        "release",
        "ritual",
        "ladder",
        "sense",
        "reset",
        "redact",
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
        """All 100 method tokens must have metadata entries (enforce added ADR-0231; mu/paradox/mint/root added; gate/chain/atomic added ADR-0224; automate/gloss revived; hollow/distill added; distill removed ADR-0235 — constraints absorbed into hollow; risks/resilience/jobs/product moved out)."""
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

    def test_hollow_deny_list_clause_is_invalid_not_permitted(self):
        """hollow must not list deny-list clause as a permitted type — it must be treated as invalid requiring allow-list conversion."""
        hollow = self.meta.get("hollow", {})
        definition = hollow.get("definition", "")
        # permitted types list must not include deny-list clause
        permitted_idx = definition.find("permitted types are:")
        if permitted_idx != -1:
            # find the end of the permitted types list (next period or closing paren after the list)
            permitted_section = definition[permitted_idx:permitted_idx + 400]
            self.assertNotIn(
                "deny-list clause",
                permitted_section,
                "hollow must not list deny-list clause as a permitted type",
            )
        # definition must name deny-list clause as invalid with allow-list remediation
        self.assertIn(
            "deny-list clause",
            definition,
            "hollow must name deny-list clause so auditors can identify it",
        )
        self.assertIn(
            "allow-list condition",
            definition,
            "hollow must require deny-list clauses to be converted to allow-list conditions",
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
        """atomic must scope each tool call to the first failing-item line in the run result — the scope commitment must reference the first failing item only (hollow audit finding)."""
        atomic = self.meta.get("atomic", {})
        definition = atomic.get("definition", "")
        self.assertTrue(
            "the first failing-item line in the most recent tool-executed run result" in definition or
            "first line beginning with the FAIL signal prefix" in definition,
            "atomic must name the observable that limits the candidate to the first failing item only",
        )

    def test_atomic_candidate_scoped_to_observed_failure(self):
        """atomic's scope commitment must require the literal text of the failing item to appear as a quoted string above the tool call — not a paraphrase (hollow audit finding)."""
        atomic = self.meta.get("atomic", {})
        definition = atomic.get("definition", "")
        self.assertIn(
            "scope commitment",
            definition,
            "atomic must name the scope commitment as the structural gate before each file-modifying tool call",
        )

    def test_atomic_smaller_change_insufficient_against_current_fail(self):
        """atomic must require that paths which cannot be closed by naming a string be eliminated structurally — not just identified (hollow audit finding)."""
        atomic = self.meta.get("atomic", {})
        definition = atomic.get("definition", "")
        self.assertTrue(
            "a path that cannot be closed by naming a string must be eliminated by bringing the system to a state where the commitments can be satisfied structurally" in definition or
            "(i) scope inflation" in definition,
            "atomic must require structural elimination of paths that cannot be closed by naming a string (now via four named escape categories)",
        )

    def test_atomic_governing_test_clause_required(self):
        """atomic must require that the quoted failing-item line comes from a test whose pass/fail state is determined solely by the symbols being modified — a test that passes or fails independently of those symbols does not satisfy the scope commitment (hollow audit finding)."""
        atomic = self.meta.get("atomic", {})
        definition = atomic.get("definition", "")
        self.assertIn(
            "pass/fail state is determined solely by the symbols named in the symbol commitment",
            definition,
            "atomic must name the governing-test constraint: the quoted failing line must be from a test whose outcome depends on the symbols being modified",
        )

    def test_falsify_empty_transcript_gap_closed(self):
        """falsify must block the governed action until a 'Falsify derivation:' block is present in the transcript — the structural gate preventing action without a visible derivation (2026-06-17 rewrite: labeled block replaces closing sentence)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "complete only when a literal block labeled 'Falsify derivation:' containing entries for (a) through (f) appears in the transcript",
            definition,
            "falsify must explicitly block the governed action until derivation and satisfying result are present in the transcript",
        )

    def test_falsify_slower_check_excludes_compiler_artifacts(self):
        """falsify must require that (a) is not separated from (c) by an unrelated behavior — pre-execution failures producing a different signal do not satisfy (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "(a) is not separated from (c) by any line naming a different governed behavior identifier",
            definition,
            "falsify condition must name the observable that excludes pre-execution failures: (a) is not separated from (c) by any line naming a different governed behavior identifier",
        )

    def test_falsify_self_refuting_closes_entry(self):
        """falsify must structurally require that (a) is not separated from (c) by an unrelated behavior signal — non-execution paths are excluded by the separation rule (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "(a) is not separated from (c) by any line naming a different governed behavior identifier",
            definition,
            "falsify must structurally require elimination of non-execution paths — behaviors must produce (a) or (b), not some other signal",
        )

    def test_falsify_direct_invocation_observable(self):
        """falsify must name the observable distinguishing direct invocation from a displayed or predicted result — tool call text naming (d) directly is the structural criterion (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "result was produced by a tool call whose text names (d) directly",
            definition,
            "falsify must name the observable that distinguishes direct invocation: result was produced by a tool call whose text names (d) directly",
        )

    def test_falsify_creation_step_boundary_required(self):
        """falsify's exception clause must name the transcript-observable boundary of 'creation step' — (c) absent before and present after the action (string-absence condition per 2026-06-17 rewrite)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "(c) is absent before the action and present after it",
            definition,
            "falsify must name the creation-step boundary: (c) is absent before the action and present after it — any other governed action is not exempt",
        )

    def test_falsify_no_open_enumeration(self):
        """falsify's derivation instruction must not use open enumeration — 'enumerate every path' is hollow because no string proves enumeration is complete (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertNotIn(
            "enumerate every path",
            definition,
            "falsify must not use open enumeration — replace with bounded four named-signals derivation",
        )

    def test_falsify_four_named_strings_derivation(self):
        """falsify's derivation instruction must use a four named-signals structure — name (a) absence signal, (b) presence signal, (c) behavior identifier, (d) governed action identifier (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "Name — (a)",
            definition,
            "falsify derivation must use four named-signals structure: Name — (a) absence signal (b) presence signal (c) behavior identifier (d) governed action identifier",
        )

    def test_falsify_specificity_constraint(self):
        """falsify must require that (c) identifies each governed behavior individually — a result that fires on any absent behavior regardless of scope does not satisfy this token (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "(c) the string identifying each governed behavior",
            definition,
            "falsify must require (c) to identify each governed behavior specifically — closes the integration-level FAIL scope gap",
        )

    def test_falsify_governing_artifact_not_disposable(self):
        """falsify must require the tool call to name the governed subject directly — closes the disposable-artifact gap in a domain-agnostic way (2026-06-17 rewrite)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "the tool call names the governed subject directly",
            definition,
            "falsify must require the tool call to name the governed subject directly — 'the tool call names the governed subject directly' must appear in the definition",
        )

    def test_falsify_disposable_artifact_constraint_in_primary_condition(self):
        """falsify's PRIMARY condition must name the governed-subject requirement before 'Exception:' — so disposable artifacts are excluded (hollow audit fix)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        exception_start = definition.find("Exception:")
        primary_condition = definition[:exception_start] if exception_start != -1 else definition
        self.assertIn(
            "the tool call names the governed subject directly",
            primary_condition,
            "falsify primary condition must require tool call to name governed subject — allow-list clause must appear before 'Exception:'",
        )

    def test_falsify_governed_action_boundary_named(self):
        """falsify's derivation phase must name 'governed action' as the domain-agnostic boundary — 'file-modifying tool call' couples the token to software contexts (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertIn(
            "before any governed action",
            definition,
            "falsify must name 'governed action' as the domain-agnostic boundary — not 'file-modifying tool call'",
        )
        self.assertNotIn(
            "before any file-modifying tool call",
            definition,
            "falsify must not name 'file-modifying tool call' — this couples the token to software contexts",
        )

    def test_falsify_no_naming_convention_escape(self):
        """falsify must not permit 'derived from it by the test framework naming convention' as a substitute for substring containment — naming convention requires semantic inference (hollow audit finding)."""
        falsify = self.meta.get("falsify", {})
        definition = falsify.get("definition", "")
        self.assertNotIn(
            "derived from it by the test framework naming convention",
            definition,
            "falsify must not permit naming-convention escape route — only substring containment is addressable",
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

    def test_mu_heuristics_include_structural_contradiction_trigger(self):
        """mu must be discoverable via structural contradiction queries — heuristic for code/design diagnosis."""
        mu = self.meta.get("mu", {})
        heuristics = mu.get("heuristics", [])
        self.assertIn(
            "what's the structural contradiction here",
            heuristics,
            "mu must include 'what's the structural contradiction here' as a heuristic for diagnostic discoverability",
        )

    def test_mu_heuristics_include_requirements_conflict_trigger(self):
        """mu must surface when two requirements can't both be true."""
        mu = self.meta.get("mu", {})
        heuristics = mu.get("heuristics", [])
        self.assertIn(
            "find where two requirements can't both be true",
            heuristics,
            "mu must include requirements-conflict heuristic for code/design diagnosis",
        )

    def test_mu_heuristics_include_design_forces_trigger(self):
        """mu must surface when forces are fighting each other in a design."""
        mu = self.meta.get("mu", {})
        heuristics = mu.get("heuristics", [])
        self.assertIn(
            "what forces are fighting each other in this design",
            heuristics,
            "mu must include design-forces heuristic for structural tension diagnosis",
        )

    def test_mu_heuristics_include_condition_naming_trigger(self):
        """mu must surface when the task is to name conditions under which each side breaks the other."""
        mu = self.meta.get("mu", {})
        heuristics = mu.get("heuristics", [])
        self.assertIn(
            "name the condition under which each side breaks the other",
            heuristics,
            "mu must include condition-naming heuristic for structural contradiction analysis",
        )


if __name__ == "__main__":
    unittest.main()
