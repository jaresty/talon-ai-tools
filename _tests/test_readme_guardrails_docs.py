import subprocess
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class ReadmeGuardrailsDocsTests(unittest.TestCase):
        def test_readme_mentions_guardrail_entrypoints(self) -> None:
            """Guardrail: README should surface guardrail targets and CI helper."""

            readme = (Path(__file__).resolve().parents[1] / "readme.md").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                "axis-guardrails",
                readme,
                "Expected README to mention axis guardrail targets",
            )
            self.assertIn(
                "axis-catalog-validate",
                readme,
                "Expected README to mention catalog validation guardrail primitive",
            )
            self.assertIn(
                "axis-cheatsheet",
                readme,
                "Expected README to mention cheat sheet guardrail primitive",
            )
            self.assertIn(
                "axis-guardrails-ci",
                readme,
                "Expected README to mention CI-friendly guardrails",
            )
            self.assertIn(
                "axis-guardrails-test",
                readme,
                "Expected README to mention full guardrail suite",
            )
            self.assertIn(
                "not tracked",
                readme,
                "Expected README to state axis/static prompt Talon lists are untracked",
            )
            self.assertIn(
                "talon-lists",
                readme,
                "Expected README to mention talon list generation",
            )
            self.assertIn(
                "talon-lists-check",
                readme,
                "Expected README to mention talon list drift check",
            )
            self.assertIn(
                "ci-guardrails",
                readme,
                "Expected README to mention CI guardrails target",
            )
            self.assertIn(
                "guardrails",
                readme,
                "Expected README to mention guardrails alias target",
            )
            self.assertIn(
                "request-history-guardrails",
                readme,
                "Expected README to call out manual history guardrails helper",
            )
            self.assertIn(
                "request-history-guardrails-fast",
                readme,
                "Expected README to cover the fast history summary helper",
            )
            self.assertIn(
                "runs locally only",
                readme,
                "Expected README to note history guardrails require local telemetry",
            )
            self.assertIn(
                "axis-catalog-validate.py --lists-dir",
                readme,
                "Expected README to document ad-hoc lists-dir validation",
            )
            self.assertIn(
                "python3 scripts/tools/axis-catalog-validate.py --lists-dir /path/to/lists --no-skip-list-files",
                readme,
                "Expected README to include an explicit enforced list check example",
            )
            self.assertIn(
                "--no-skip-list-files",
                readme,
                "Expected README to mention opting back into list checks",
            )
            self.assertIn(
                "generate_talon_lists.py",
                readme,
                "Expected README to mention regenerating list files if needed",
            )
            self.assertIn(
                "make help",
                readme,
                "Expected README to reference make help for guardrail targets",
            )
            self.assertEqual(
                readme.count("Axis catalog guardrails:"),
                1,
                "Expected README to contain a single guardrail overview entry",
            )
            self.assertIn(
                "--skip-list-files",
                readme,
                "Expected README to mention catalog-only validation flag",
            )

        def test_readme_axis_cheatsheet_includes_metadata_summary(self) -> None:
            cheat_sheet_path = (
                Path(__file__).resolve().parents[1]
                / "docs"
                / "readme-axis-cheatsheet.md"
            )
            self.assertTrue(
                cheat_sheet_path.exists(),
                "Axis cheat sheet README snapshot missing; regenerate via generate-axis-cheatsheet.py",
            )
            content = cheat_sheet_path.read_text(encoding="utf-8")
            self.assertIn(
                "## Help metadata summary",
                content,
                "Cheat sheet README snapshot missing metadata summary header",
            )
            self.assertIn(
                "Metadata schema version:",
                content,
                "Cheat sheet README snapshot missing schema version line",
            )

else:

    class ReadmeGuardrailsDocsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
