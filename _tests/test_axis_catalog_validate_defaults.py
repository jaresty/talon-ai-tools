import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class AxisCatalogValidateDefaultsTests(unittest.TestCase):
        def test_defaults_are_catalog_only(self) -> None:
            """Guardrail: default axis-catalog-validate run should skip list files (catalog-only)."""

            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "axis-catalog-validate.py"
            result = subprocess.run(
                [sys.executable, str(script), "--verbose"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            if result.returncode != 0:
                self.fail(
                    f"axis-catalog-validate default run failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            output = result.stdout + result.stderr
            self.assertIn("lists_dir=<skipped>", output)
            self.assertIn("lists_validation=skipped", output)

else:

    class AxisCatalogValidateDefaultsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
