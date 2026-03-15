import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:  # pragma: no cover - Talon runtime
    from bootstrap import bootstrap
except ModuleNotFoundError:  # pragma: no cover - Talon runtime
    bootstrap = None
else:  # pragma: no cover - Talon runtime
    bootstrap()


class PromptGrammarPayloadTests(unittest.TestCase):
    @unittest.skipIf(
        bootstrap is None, "Test harness unavailable outside unittest runs"
    )
    def test_payload_contains_expected_sections(self) -> None:
        from talon_user.lib import promptGrammar

        payload = promptGrammar.prompt_grammar_payload()

        self.assertEqual(payload["schema_version"], "1.0")
        self.assertIn("axes", payload)
        self.assertIn("tasks", payload)
        self.assertIn("persona", payload)
        self.assertIn("hierarchy", payload)
        self.assertIn("checksums", payload)

        completeness = payload["axes"]["definitions"]["completeness"]
        self.assertIn("full", completeness)

        persona_presets = payload["persona"]["presets"]
        self.assertIn("teach_junior_dev", persona_presets)

        checksum = payload["checksums"]["axes"]
        self.assertEqual(len(checksum), 64)


class PromptGrammarCliTests(unittest.TestCase):
    @unittest.skipIf(
        bootstrap is None, "Test harness unavailable outside unittest runs"
    )
    def test_cli_writes_prompt_grammar_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "grammar.json"
            subprocess.run(
                [sys.executable, "-m", "prompts.export", "--output", str(output_path)],
                check=True,
            )

            self.assertTrue(output_path.exists(), "CLI should create the output file")

            with output_path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)

        self.assertEqual(data["schema_version"], "1.0")
        self.assertIn("checksums", data)

        reference_key = data.get("reference_key", "")
        self.assertIn(
            "任務", reference_key, "reference_key should contain kanji for TASK"
        )
        self.assertIn(
            "追加", reference_key, "reference_key should contain kanji for ADDENDUM"
        )
        self.assertIn(
            "制約", reference_key, "reference_key should contain kanji for CONSTRAINTS"
        )
        self.assertIn(
            "人格", reference_key, "reference_key should contain kanji for PERSONA"
        )
        self.assertIn(
            "題材", reference_key, "reference_key should contain kanji for SUBJECT"
        )

        axes_kanji = data.get("axes", {}).get("kanji", {})
        self.assertTrue(axes_kanji, "axes should contain kanji mappings (ADR-0143)")
        self.assertIn("scope", axes_kanji, "axes kanji should include scope")
        self.assertIn("channel", axes_kanji, "axes kanji should include channel")

        static_kanji = data.get("tasks", {}).get("kanji", {})
        self.assertTrue(static_kanji, "tasks should contain kanji mappings (ADR-0143)")

        meta_guidance = data.get("meta_interpretation_guidance", "")
        self.assertTrue(
            meta_guidance,
            "grammar JSON should contain a non-empty meta_interpretation_guidance field (ADR-0166)",
        )
        self.assertIn(
            "Model interpretation",
            meta_guidance,
            "meta_interpretation_guidance should reference the '## Model interpretation' heading",
        )
        self.assertNotIn(
            "style",
            meta_guidance,
            "meta_interpretation_guidance must not use 'style' as an example axis — it is not a valid bar axis",
        )
        self.assertNotIn(
            "focus",
            meta_guidance,
            "meta_interpretation_guidance must not use 'focus' as an example token — it is not a valid bar token",
        )
        self.assertIn(
            "token catalog",
            meta_guidance,
            "meta_interpretation_guidance must include a conditional guard requiring access to the bar token catalog before suggesting tokens",
        )
        # Issue 3: "non-pasteable" is undefined jargon — must be replaced with behavioural instruction
        self.assertNotIn(
            "non-pasteable",
            meta_guidance,
            "meta_interpretation_guidance must not use undefined jargon 'non-pasteable'",
        )
        # Issue 2: directional carve-out — meta must acknowledge the directional naming prohibition
        self.assertIn(
            "directional",
            meta_guidance,
            "meta_interpretation_guidance must include a carve-out for the directional 'do not name' rule",
        )
        # Issue 5: retrospective reasoning — avoid claiming to explain live reasoning
        self.assertNotIn(
            "how you interpreted the request and chose your approach",
            meta_guidance,
            "meta_interpretation_guidance must not imply live reasoning is being reported retrospectively",
        )
        # Issue 6: Suggestion is for future prompts, not a critique of current constraints
        self.assertIn(
            "future",
            meta_guidance,
            "meta_interpretation_guidance must clarify the Suggestion line is for future prompts",
        )

        reference_key = data.get("reference_key", "")
        # Issue 1: TASK bullet must not claim unqualified precedence over channels
        self.assertNotIn(
            "Takes precedence over all other categories if conflicts arise",
            reference_key,
            "PROMPT_REFERENCE_KEY TASK bullet must qualify its precedence claim to acknowledge channel override",
        )


if bootstrap is None and not TYPE_CHECKING:  # pragma: no cover - Talon runtime

    class PromptGrammarPayloadTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self) -> None:
            raise NotImplementedError

    class PromptGrammarCliTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self) -> None:
            raise NotImplementedError
