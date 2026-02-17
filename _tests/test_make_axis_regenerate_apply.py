import subprocess
import sys
import unittest
from pathlib import Path

from .helpers_axis_artifacts import cleanup_axis_regen_outputs


class MakeAxisRegenerateApplyTests(unittest.TestCase):
    def test_axis_regenerate_apply_updates_axis_config(self):
        repo_root = Path(__file__).resolve().parents[1]
        cleanup_axis_regen_outputs(repo_root)
        self.addCleanup(cleanup_axis_regen_outputs, repo_root)
        axis_config = repo_root / "lib" / "axisConfig.py"
        generated = repo_root / "tmp" / "axisConfig.generated.py"

        result = subprocess.run(
            ["make", "axis-regenerate-apply"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.fail(
                f"make axis-regenerate-apply failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )

        self.assertTrue(
            axis_config.exists(), "axisConfig.py should be present after apply"
        )
        self.assertTrue(
            generated.exists(), "tmp/axisConfig.generated.py should exist after apply"
        )
        axis_text = axis_config.read_text(encoding="utf-8")
        gen_text = generated.read_text(encoding="utf-8")
        self.assertEqual(
            axis_text,
            gen_text,
            "axisConfig.py should match the generated axisConfig output after apply",
        )

    def test_axis_regenerate_apply_is_idempotent_when_already_synced(self):
        repo_root = Path(__file__).resolve().parents[1]
        cleanup_axis_regen_outputs(repo_root)
        self.addCleanup(cleanup_axis_regen_outputs, repo_root)
        axis_config = repo_root / "lib" / "axisConfig.py"
        generated = repo_root / "tmp" / "axisConfig.generated.py"
        self.assertTrue(
            axis_config.exists(),
            "axisConfig.py should exist before running make target",
        )

        result = subprocess.run(
            ["make", "axis-regenerate-apply"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.fail(
                f"make axis-regenerate-apply failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )

        # Verify the generated output matches axisConfig.py (idempotent behavior)
        self.assertTrue(
            generated.exists(), "tmp/axisConfig.generated.py should exist after apply"
        )
        axis_text = axis_config.read_text(encoding="utf-8")
        gen_text = generated.read_text(encoding="utf-8")
        self.assertEqual(
            axis_text,
            gen_text,
            "axisConfig.py should match generated output when already in sync",
        )
