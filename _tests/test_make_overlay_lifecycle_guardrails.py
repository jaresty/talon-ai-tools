import subprocess
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class MakeOverlayLifecycleGuardrailsTests(unittest.TestCase):
        def test_make_overlay_lifecycle_guardrails_runs_clean(self) -> None:
            repo_root = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                ["make", "overlay-lifecycle-guardrails"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make overlay-lifecycle-guardrails failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
