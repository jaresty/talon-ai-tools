import subprocess
import unittest
from pathlib import Path

from .helpers_axis_artifacts import cleanup_axis_regen_outputs


class MakeAxisGuardrailsCiTests(unittest.TestCase):
    def test_make_axis_guardrails_ci_runs_regen(self):
        repo_root = Path(__file__).resolve().parents[1]
        cleanup_axis_regen_outputs(repo_root)
        self.addCleanup(cleanup_axis_regen_outputs, repo_root)
        result = subprocess.run(
            ["make", "axis-guardrails-ci"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.fail(
                "make axis-guardrails-ci failed:\n"
                f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )
        self.assertIn("Axis catalog validation passed.", result.stdout)
        self.assertIn("Axis guardrails (CI-friendly) completed", result.stdout)


if __name__ == "__main__":
    unittest.main()
