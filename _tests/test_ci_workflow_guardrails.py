import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class CiWorkflowGuardrailsTests(unittest.TestCase):
        def test_ci_runs_guardrails_and_tests(self) -> None:
            """Ensure CI runs guardrails and the regular test suite."""

            repo_root = Path(__file__).resolve().parents[1]
            workflow = repo_root / ".github" / "workflows" / "test.yml"
            self.assertTrue(workflow.exists(), "Expected CI workflow file to exist")
            contents = workflow.read_text()
            self.assertIn("make ci-guardrails", contents, "CI should run guardrails")
            self.assertIn(
                "python3 -m unittest discover -s tests -v",
                contents,
                "CI should run the main test suite via python3 -m unittest",
            )

else:

    class CiWorkflowGuardrailsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
