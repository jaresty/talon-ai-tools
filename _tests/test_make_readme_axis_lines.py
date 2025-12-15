import subprocess
import unittest
from pathlib import Path
from typing import TYPE_CHECKING
import tempfile

if not TYPE_CHECKING:
    try:
        from bootstrap import bootstrap
    except ModuleNotFoundError:
        bootstrap = None
    else:
        bootstrap()

    from scripts.tools.generate_readme_axis_lists import render_readme_axis_lines

    class MakeReadmeAxisLinesTests(unittest.TestCase):
        def test_make_readme_axis_lines_target_generates_snapshot(self) -> None:
            repo_root = Path(__file__).resolve().parents[1]
            readme_path = repo_root / "GPT" / "readme.md"
            before = readme_path.read_text(encoding="utf-8")
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
            expected_lines = render_readme_axis_lines().strip().splitlines()
            self.assertEqual(
                expected_lines,
                text.strip().splitlines(),
                "Snapshot should match generator output exactly",
            )
            after = readme_path.read_text(encoding="utf-8")
            self.assertEqual(before, after, "readme-axis-lines should not modify README in-place")

        def test_readme_axis_lines_respects_lists_dir(self) -> None:
            repo_root = Path(__file__).resolve().parents[1]
            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                lists_dir.mkdir(parents=True, exist_ok=True)
                scope_list = lists_dir / "scopeModifier.talon-list"
                scope_list.write_text("list: user.scopeModifier\nnovel: novel\n", encoding="utf-8")
                out_path = lists_dir / "snapshot.md"
                result = subprocess.run(
                    [
                        "python3",
                        "scripts/tools/generate_readme_axis_lists.py",
                        "--out",
                        str(out_path),
                        "--lists-dir",
                        str(lists_dir),
                    ],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    self.fail(
                        "generate_readme_axis_lists with lists-dir failed:\n"
                        f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                text = out_path.read_text(encoding="utf-8")
                self.assertIn("`novel`", text, "Expected lists-dir token to appear in axis snapshot")
else:
    if not TYPE_CHECKING:
        class MakeReadmeAxisLinesTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
