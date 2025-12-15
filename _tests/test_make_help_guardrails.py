import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class MakeHelpGuardrailsTests(unittest.TestCase):
        def test_make_help_lists_guardrail_targets(self) -> None:
            """Ensure `make help` includes guardrail targets for discoverability."""

            repo_root = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                ["make", "help"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(repo_root),
            )
            if result.returncode != 0:
                self.fail(
                    f"`make help` failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
            output = result.stdout
            self.assertIn("axis-catalog-validate", output)
            self.assertIn(
                "skip",
                output,
                "Expected axis-catalog-validate help entry to mention skip/no-skip list checks",
            )
            self.assertIn("axis-cheatsheet", output)
            self.assertIn("axis-guardrails", output)
            self.assertIn("axis-guardrails-ci", output)
            self.assertIn("axis-guardrails-test", output)
            self.assertIn("talon-lists", output)
            self.assertIn("talon-lists-check", output)
            self.assertIn("optional: export axis/static prompt Talon lists locally", output)
            self.assertIn("optional: drift-check local Talon lists", output)
            self.assertIn("untracked", output, "Expected make help to mention talon-lists outputs are untracked")
            self.assertIn("lists-dir", output, "Expected make help to mention lists-dir when enforcing list checks")
            self.assertIn("ci-guardrails", output)
            self.assertIn("guardrails", output)
            self.assertIn("run_guardrails_ci.sh [--help]", output)
            self.assertIn("GUARDRAILS_TARGET", output)
            self.assertIn("request-history-guardrails", output)
            self.assertIn("request-history-guardrails-fast", output)
            self.assertIn("request-history-guardrails-fast", output)
            self.assertIn("readme-axis-lines", output)
            self.assertIn("readme-axis-refresh", output)
            self.assertIn("README_AXIS_LISTS_DIR", output)
            self.assertIn("static-prompt-docs", output)
            self.assertIn("static-prompt-refresh", output)
            self.assertIn("README snapshot", output)
            self.assertIn("doc-snapshots", output)

else:

    class MakeHelpGuardrailsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
