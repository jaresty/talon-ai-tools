import subprocess
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class MakeReadmeAxisRefreshTests(unittest.TestCase):
        def test_make_readme_axis_refresh_runs(self) -> None:
            repo_root = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                ["make", "readme-axis-refresh"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make readme-axis-refresh failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
else:
    if not TYPE_CHECKING:
        class MakeReadmeAxisRefreshTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
