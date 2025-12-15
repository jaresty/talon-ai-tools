import subprocess
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    try:
        from bootstrap import bootstrap
    except ModuleNotFoundError:
        bootstrap = None
    else:
        bootstrap()

    from scripts.tools.generate_readme_axis_lists import render_readme_axis_lines
    from talon_user.GPT.gpt import _build_static_prompt_docs

    class MakeDocSnapshotsTests(unittest.TestCase):
        def test_doc_snapshots_target_generates_all_outputs(self) -> None:
            repo_root = Path(__file__).resolve().parents[1]
            readme_path = repo_root / "GPT" / "readme.md"
            before_readme = readme_path.read_text(encoding="utf-8")
            result = subprocess.run(
                ["make", "doc-snapshots"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make doc-snapshots failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            outputs = [
                repo_root / "tmp" / "readme-axis-lists.md",
                repo_root / "tmp" / "readme-axis-readme.md",
                repo_root / "tmp" / "static-prompt-docs.md",
                repo_root / "tmp" / "static-prompt-readme.md",
            ]
            for path in outputs:
                self.assertTrue(path.exists(), f"Expected snapshot at {path}")
            # Axis snapshot parity.
            axis_snapshot = outputs[0].read_text(encoding="utf-8").strip().splitlines()
            expected_axis = render_readme_axis_lines().strip().splitlines()
            self.assertEqual(expected_axis, axis_snapshot, "Axis snapshot should match generator output")
            # README axis snapshot parity.
            axis_readme_snapshot = outputs[1].read_text(encoding="utf-8").strip().splitlines()
            try:
                start_idx = next(i for i, line in enumerate(axis_readme_snapshot) if line.startswith("Completeness (`completenessModifier`)"))
                end_idx = next(i for i, line in enumerate(axis_readme_snapshot[start_idx:]) if line.startswith("  - Additional form/channel notes:"))
                end_idx = start_idx + end_idx
            except StopIteration:
                self.fail("Could not locate axis block in README axis snapshot")
            self.assertEqual(expected_axis, axis_readme_snapshot[start_idx:end_idx])
            # Static prompt snapshot parity.
            static_snapshot = outputs[2].read_text(encoding="utf-8").strip()
            static_readme_snapshot = outputs[3].read_text(encoding="utf-8").splitlines()
            try:
                sp_start = next(i for i, line in enumerate(static_readme_snapshot) if line.strip() == "## Help")
                sp_end = next(i for i, line in enumerate(static_readme_snapshot[sp_start:], start=sp_start) if line.strip().startswith("### Meta interpretation channel"))
            except StopIteration:
                self.fail("Could not locate static prompt block in README snapshot")
            static_block = "\n".join(static_readme_snapshot[sp_start + 1 : sp_end]).strip()
            expected_static = _build_static_prompt_docs().strip()
            self.assertEqual(expected_static, static_snapshot)
            self.assertEqual(expected_static, static_block)
            after_readme = readme_path.read_text(encoding="utf-8")
            self.assertEqual(before_readme, after_readme, "doc-snapshots should not modify README in-place")
else:
    if not TYPE_CHECKING:
        class MakeDocSnapshotsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
