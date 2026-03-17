import importlib
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

    def test_axis_regenerate_apply_preserves_category_order(self):
        """AXIS_CATEGORY_ORDER and axis_category_order() must survive axis-regenerate-apply.

        Regression guard: the generator must emit these symbols so they are not
        silently wiped when axisConfig.py is overwritten.
        """
        repo_root = Path(__file__).resolve().parents[1]
        cleanup_axis_regen_outputs(repo_root)
        self.addCleanup(cleanup_axis_regen_outputs, repo_root)

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

        # Re-import axisConfig so we test the on-disk state, not the cached module.
        import lib.axisConfig as _ac
        importlib.reload(_ac)

        self.assertTrue(
            hasattr(_ac, "AXIS_CATEGORY_ORDER"),
            "AXIS_CATEGORY_ORDER must be present in axisConfig.py after axis-regenerate-apply",
        )
        self.assertIsInstance(_ac.AXIS_CATEGORY_ORDER, dict, "AXIS_CATEGORY_ORDER must be a dict")
        self.assertIn(
            "method",
            _ac.AXIS_CATEGORY_ORDER,
            "AXIS_CATEGORY_ORDER must contain 'method' key after axis-regenerate-apply",
        )
        self.assertTrue(
            hasattr(_ac, "axis_category_order"),
            "axis_category_order() must be present in axisConfig.py after axis-regenerate-apply",
        )
        method_order = _ac.axis_category_order("method")
        self.assertIsInstance(method_order, list, "axis_category_order('method') must return a list")
        self.assertGreater(
            len(method_order),
            0,
            "axis_category_order('method') must return a non-empty list after axis-regenerate-apply",
        )
