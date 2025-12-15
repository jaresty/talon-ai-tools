import subprocess
import unittest
from pathlib import Path
from typing import TYPE_CHECKING
import tempfile
import os

if not TYPE_CHECKING:
    try:
        from bootstrap import bootstrap
    except ModuleNotFoundError:
        bootstrap = None
    else:
        bootstrap()

    from scripts.tools.generate_readme_axis_lists import render_readme_axis_lines

    class MakeReadmeAxisRefreshTests(unittest.TestCase):
        def test_make_readme_axis_refresh_runs(self) -> None:
            repo_root = Path(__file__).resolve().parents[1]
            readme_path = repo_root / "GPT" / "readme.md"
            before = readme_path.read_text(encoding="utf-8")
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
            snapshot = repo_root / "tmp" / "readme-axis-readme.md"
            self.assertTrue(snapshot.exists(), "Expected tmp/readme-axis-readme.md to be generated")
            text = snapshot.read_text(encoding="utf-8")
            expected_lines = render_readme_axis_lines().strip().splitlines()
            lines = text.splitlines()
            try:
                start_idx = next(i for i, line in enumerate(lines) if line.startswith("Completeness (`completenessModifier`)"))
                end_idx = next(i for i, line in enumerate(lines[start_idx:]) if line.startswith("  - Additional form/channel notes:"))
                end_idx = start_idx + end_idx
            except StopIteration:
                self.fail("Could not locate axis block markers in README snapshot")
            snapshot_block = lines[start_idx:end_idx]
            self.assertEqual(
                expected_lines,
                snapshot_block,
                "Axis lines in snapshot should match generator output exactly",
            )
            after = readme_path.read_text(encoding="utf-8")
            self.assertEqual(before, after, "readme-axis-refresh should not modify README in-place")

        def test_readme_axis_refresh_respects_lists_dir(self) -> None:
            """Snapshot should merge list tokens when lists_dir is provided."""

            repo_root = Path(__file__).resolve().parents[1]
            readme_path = repo_root / "GPT" / "readme.md"
            before = readme_path.read_text(encoding="utf-8")
            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                scope_list = lists_dir / "scopeModifier.talon-list"
                scope_list.write_text("list: user.scopeModifier\nnovel: novel\n", encoding="utf-8")
                out_path = Path(tmpdir) / "snapshot.md"
                result = subprocess.run(
                    ["make", "readme-axis-refresh"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    check=False,
                    env={"README_AXIS_LISTS_DIR": str(lists_dir), **dict(os.environ)},
                )
                if result.returncode != 0:
                    self.fail(
                        "readme-axis-refresh with lists-dir failed:\n"
                        f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                text = (repo_root / "tmp" / "readme-axis-readme.md").read_text(encoding="utf-8")
                lines = text.splitlines()
                try:
                    start_idx = next(i for i, line in enumerate(lines) if line.startswith("Completeness (`completenessModifier`)"))
                    end_idx = next(i for i, line in enumerate(lines[start_idx:]) if line.startswith("  - Additional form/channel notes:"))
                    end_idx = start_idx + end_idx
                except StopIteration:
                    self.fail("Could not locate axis block markers in README snapshot (lists-dir)")
                snapshot_block = lines[start_idx:end_idx]
                expected_lines = render_readme_axis_lines(lists_dir=lists_dir).strip().splitlines()
                self.assertEqual(
                    expected_lines,
                    snapshot_block,
                    "Axis lines in lists-dir snapshot should match generator output",
                )
                self.assertIn("`novel`", "\n".join(snapshot_block), "Expected lists-dir token to appear in snapshot")
            after = readme_path.read_text(encoding="utf-8")
            self.assertEqual(before, after, "lists-dir refresh should not modify README in-place")
else:
    if not TYPE_CHECKING:
        class MakeReadmeAxisRefreshTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
