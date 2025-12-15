import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class GenerateTalonListsTests(unittest.TestCase):
        def test_generate_lists_writes_axis_and_static_prompt_tokens(self) -> None:
            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "generate_talon_lists.py"
            with tempfile.TemporaryDirectory() as tmpdir:
                result = subprocess.run(
                    [sys.executable, str(script), "--out-dir", tmpdir],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).resolve().parents[1]),
                )
                if result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )

                out_dir = Path(tmpdir)
                completeness_list = out_dir / "completenessModifier.talon-list"
                static_prompt_list = out_dir / "staticPrompt.talon-list"
                self.assertTrue(completeness_list.is_file())
                self.assertTrue(static_prompt_list.is_file())

                completeness_text = completeness_list.read_text(encoding="utf-8")
                self.assertIn("full: full", completeness_text)

                static_text = static_prompt_list.read_text(encoding="utf-8")
                self.assertIn("infer: infer", static_text)

        def test_generated_lists_are_self_consistent_under_check(self) -> None:
            """Guardrail: generator --check should pass against its own output."""

            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "generate_talon_lists.py"
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                # Generate baseline
                gen_result = subprocess.run(
                    [sys.executable, str(script), "--out-dir", tmpdir],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).resolve().parents[1]),
                )
                if gen_result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists failed with code {gen_result.returncode}\nstdout:\n{gen_result.stdout}\nstderr:\n{gen_result.stderr}"
                    )
                # Check against the just-generated directory
                check_result = subprocess.run(
                    [sys.executable, str(script), "--out-dir", tmpdir, "--check"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).resolve().parents[1]),
                )
                if check_result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists --check failed unexpectedly\nstdout:\n{check_result.stdout}\nstderr:\n{check_result.stderr}"
                    )

        def test_generate_lists_check_mode_passes(self) -> None:
            """Guardrail: --check should pass when lists match catalog."""
            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "generate_talon_lists.py"
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                gen_result = subprocess.run(
                    [sys.executable, str(script), "--out-dir", tmpdir],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).resolve().parents[1]),
                )
                if gen_result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists failed with code {gen_result.returncode}\nstdout:\n{gen_result.stdout}\nstderr:\n{gen_result.stderr}"
                    )

                result = subprocess.run(
                    [sys.executable, str(script), "--out-dir", tmpdir, "--check"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).resolve().parents[1]),
                )
                if result.returncode != 0:
                    self.fail(
                        f"generate_talon_lists --check failed unexpectedly\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )

        def test_generate_lists_check_mode_fails_on_drift(self) -> None:
            """Guardrail: --check should flag drift when lists differ from catalog."""
            script = Path(__file__).resolve().parents[1] / "scripts" / "tools" / "generate_talon_lists.py"
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_dir = Path(tmpdir)
                out_dir = tmp_dir / "lists"
                out_dir.mkdir()
                (out_dir / "completenessModifier.talon-list").write_text(
                    "list: user.completenessModifier\n-\nfull: full\nextra: extra\n",
                    encoding="utf-8",
                )
                # Create empty placeholders for other lists to avoid FileNotFound.
                for name in [
                    "scopeModifier.talon-list",
                    "methodModifier.talon-list",
                    "formModifier.talon-list",
                    "channelModifier.talon-list",
                    "directionalModifier.talon-list",
                    "staticPrompt.talon-list",
                ]:
                    (out_dir / name).write_text("list: user.placeholder\n-\n", encoding="utf-8")

                result = subprocess.run(
                    [sys.executable, str(script), "--out-dir", str(out_dir), "--check"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).resolve().parents[1]),
                )
                self.assertNotEqual(
                    result.returncode,
                    0,
                    "generate_talon_lists --check should fail when drift is detected",
                )
                self.assertIn("extra", result.stdout + result.stderr)

else:
    class GenerateTalonListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
