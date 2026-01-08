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
        self.assertIn("static_prompts", payload)
        self.assertIn("persona", payload)
        self.assertIn("hierarchy", payload)
        self.assertIn("checksums", payload)

        completeness = payload["axes"]["definitions"]["completeness"]
        self.assertIn("full", completeness)

        persona_presets = payload["persona"]["presets"]
        self.assertIn("coach_junior", persona_presets)

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


if bootstrap is None and not TYPE_CHECKING:  # pragma: no cover - Talon runtime

    class PromptGrammarPayloadTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self) -> None:
            raise NotImplementedError

    class PromptGrammarCliTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self) -> None:
            raise NotImplementedError
