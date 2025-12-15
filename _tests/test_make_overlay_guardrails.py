import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class MakeOverlayGuardrailsTests(unittest.TestCase):
        def test_make_overlay_guardrails_runs_clean(self) -> None:
            """Guardrail: overlay helper target should run without errors."""

            repo_root = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                ["make", "overlay-guardrails"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make overlay-guardrails failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
