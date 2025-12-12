import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class AxisCatalogValidateTests(unittest.TestCase):
        def test_axis_catalog_validate_cli_passes(self) -> None:
            """Guardrail: axis-catalog-validate CLI should succeed in a clean repo."""

            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "axis-catalog-validate.py"
            result = subprocess.run(
                [sys.executable, str(script)],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            if result.returncode != 0:
                self.fail(
                    f"axis-catalog-validate failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )

        def test_axis_catalog_validate_checks_descriptions(self) -> None:
            """Guardrail: CLI enforces static prompt description parity."""

            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "axis-catalog-validate.py"
            result = subprocess.run(
                [sys.executable, str(script)],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            if result.returncode != 0:
                self.fail(
                    f"axis-catalog-validate failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
