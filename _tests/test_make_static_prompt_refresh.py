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

    from talon_user.GPT.gpt import _build_static_prompt_docs

    class MakeStaticPromptRefreshTests(unittest.TestCase):
        def test_make_static_prompt_refresh_runs(self) -> None:
            repo_root = Path(__file__).resolve().parents[1]
            readme_path = repo_root / "GPT" / "readme.md"
            before = readme_path.read_text(encoding="utf-8")
            result = subprocess.run(
                ["make", "static-prompt-refresh"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make static-prompt-refresh failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            snapshot = repo_root / "tmp" / "static-prompt-readme.md"
            self.assertTrue(
                snapshot.exists(),
                "Expected tmp/static-prompt-readme.md to be generated",
            )
            text = snapshot.read_text(encoding="utf-8")
            self.assertIn("Other static prompts", text)
            self.assertIn(
                "- make: The response produces content that did not previously exist, creating something new that matches required properties.",
                text,
            )
            self.assertIn("(defaults: completeness=gist", text)
            expected = _build_static_prompt_docs()
            self.assertIn(
                expected.strip(),
                text,
                "Snapshot should embed the static prompt docs generator output",
            )
            after = readme_path.read_text(encoding="utf-8")
            self.assertEqual(
                before,
                after,
                "static-prompt-refresh target should not modify README in-place",
            )

        def test_static_prompt_snapshot_matches_generator_block(self) -> None:
            """Snapshot static prompt block should match generator output exactly."""

            repo_root = Path(__file__).resolve().parents[1]
            out_path = Path(repo_root) / "tmp" / "static-prompt-readme.md"
            result = subprocess.run(
                ["make", "static-prompt-refresh"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make static-prompt-refresh failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            text = out_path.read_text(encoding="utf-8")
            lines = text.splitlines()
            self.assertIn("## Static prompt catalog snapshots", text)
            self.assertIn("## Static prompt catalog details", text)
            try:
                start_idx = next(
                    i for i, line in enumerate(lines) if line.strip() == "## Help"
                )
                end_idx = next(
                    i
                    for i, line in enumerate(lines[start_idx:], start=start_idx)
                    if line.strip().startswith("### Meta interpretation channel")
                )
            except StopIteration:
                self.fail("Could not locate static prompt block in snapshot")
            block = "\n".join(lines[start_idx + 1 : end_idx]).strip()
            expected = _build_static_prompt_docs().strip()
            self.assertEqual(
                expected,
                block,
                "Static prompt snapshot block should match generator output",
            )
else:
    if not TYPE_CHECKING:

        class MakeStaticPromptRefreshTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
