import subprocess
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class MakeReadmeAxisLinesTests(unittest.TestCase):
        def test_make_readme_axis_lines_target_generates_snapshot(self) -> None:
            repo_root = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                ["make", "readme-axis-lines"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make readme-axis-lines failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            snapshot = repo_root / "tmp" / "readme-axis-lists.md"
            self.assertTrue(snapshot.exists(), "Expected tmp/readme-axis-lists.md to be generated")
            text = snapshot.read_text(encoding="utf-8")
            self.assertIn("Directional (`directionalModifier`)", text)
else:
    if not TYPE_CHECKING:
        class MakeReadmeAxisLinesTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
