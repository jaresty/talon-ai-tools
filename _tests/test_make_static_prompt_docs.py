import subprocess
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class MakeStaticPromptDocsTests(unittest.TestCase):
        def test_make_static_prompt_docs_generates_output(self) -> None:
            repo_root = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                ["make", "static-prompt-docs"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make static-prompt-docs failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            output_path = repo_root / "tmp" / "static-prompt-docs.md"
            self.assertTrue(output_path.exists(), "Expected tmp/static-prompt-docs.md to be generated")
            text = output_path.read_text(encoding="utf-8")
            self.assertIn("Other static prompts", text)
            self.assertIn("defaults:", text)
else:
    if not TYPE_CHECKING:
        class MakeStaticPromptDocsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
