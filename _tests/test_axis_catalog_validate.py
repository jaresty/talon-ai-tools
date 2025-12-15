import subprocess
import sys
import unittest
import tempfile
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

        def test_axis_catalog_validate_respects_lists_dir(self) -> None:
            """CLI should fail when provided a drifted lists directory."""

            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "axis-catalog-validate.py"
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_lists = Path(tmpdir)

                # Write a drifted completeness list (missing tokens).
                (tmp_lists / "completenessModifier.talon-list").write_text(
                    "list: user.completenessModifier\n-\nfull: full\n", encoding="utf-8"
                )
                # Seed empty placeholders for other lists.
                for name in [
                    "scopeModifier.talon-list",
                    "methodModifier.talon-list",
                    "formModifier.talon-list",
                    "channelModifier.talon-list",
                    "directionalModifier.talon-list",
                    "staticPrompt.talon-list",
                ]:
                    (tmp_lists / name).write_text("list: user.placeholder\n-\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(script), "--lists-dir", str(tmp_lists), "--no-skip-list-files"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            self.assertNotEqual(
                result.returncode,
                0,
                "axis-catalog-validate should fail when lists drift from catalog",
            )
            self.assertIn("errors:", result.stdout + result.stderr)

        def test_axis_catalog_validate_verbose_outputs_summary(self) -> None:
            """CLI --verbose should print a short summary on success."""

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
                    f"axis-catalog-validate --verbose failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn("Axis catalog validation passed.", result.stdout)
            self.assertIn("Axes=", result.stdout)
            self.assertIn("lists_dir=<skipped>", result.stdout)
            self.assertIn("lists_validation=skipped", result.stdout)
