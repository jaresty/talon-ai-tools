import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class AxisCatalogValidateHelpTests(unittest.TestCase):
        def test_help_mentions_catalog_only_defaults(self) -> None:
            """Guardrail: axis-catalog-validate --help should explain catalog-only defaults."""

            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "axis-catalog-validate.py"
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            if result.returncode != 0:
                self.fail(
                    f"axis-catalog-validate --help failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            output = result.stdout
            self.assertIn("--lists-dir", output)
            self.assertIn("default: none", output.lower(), "Expected help to note lists-dir default is none (catalog-only).")
            self.assertIn("--skip-list-files", output, "Expected help to mention skip-list-files default.")
            self.assertIn("--no-skip-list-files", output, "Expected help to document opting back into list checks.")
            self.assertIn("requires --lists-dir", output, "Expected help to mention lists-dir is required when enforcing list checks.")
            self.assertIn("generate_talon_lists.py", output, "Expected help to hint at regenerating Talon lists when enforcing list checks.")

else:

    class AxisCatalogValidateHelpTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
