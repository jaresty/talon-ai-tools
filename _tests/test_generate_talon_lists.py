import importlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING
from types import SimpleNamespace
from unittest.mock import patch

if not TYPE_CHECKING:

    class GenerateTalonListsTests(unittest.TestCase):
        def test_generate_lists_writes_axis_and_static_prompt_tokens(self) -> None:
            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "generate_talon_lists.py"
            )
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
                persona_list = out_dir / "personaPreset.talon-list"
                intent_list = out_dir / "intentPreset.talon-list"
                self.assertTrue(completeness_list.is_file())
                self.assertTrue(static_prompt_list.is_file())
                self.assertTrue(persona_list.is_file())
                self.assertTrue(intent_list.is_file())

                completeness_text = completeness_list.read_text(encoding="utf-8")
                self.assertIn("full: full", completeness_text)

                static_text = static_prompt_list.read_text(encoding="utf-8")
                self.assertIn("make: make", static_text)

                persona_text = persona_list.read_text(encoding="utf-8").lower()
                self.assertIn("teach junior dev: teach_junior_dev", persona_text)

                intent_text = intent_list.read_text(encoding="utf-8").lower()
                self.assertIn("decide: decide", intent_text)
                self.assertNotIn("teach / explain:", intent_text)
                self.assertNotIn("for deciding:", intent_text)

        def test_generate_lists_prefers_orchestrator_metadata(self) -> None:
            script_module = importlib.import_module(
                "scripts.tools.generate_talon_lists"
            )
            orchestrator = SimpleNamespace(
                persona_presets={
                    "teach_junior_dev": SimpleNamespace(
                        key="teach_junior_dev",
                        label="Teach Junior Dev",
                        spoken="Teach junior dev",
                    )
                },
                persona_aliases={"coach": "teach_junior_dev"},
                intent_presets={
                    "decide": SimpleNamespace(
                        key="decide",
                        label="Decide",
                        intent="guide choice",
                    )
                },
                intent_aliases={"guide choice": "decide"},
                intent_synonyms={},
                intent_display_map={"decide": "Guide choice"},
                axis_tokens={},
                axis_alias_map={},
            )
            empty_maps = SimpleNamespace(
                persona_presets={},
                persona_preset_aliases={},
                intent_presets={},
                intent_display_map={},
            )
            axis_catalog_data = {"axes": {}, "axis_list_tokens": {}}
            static_catalog_data = {"talon_list_tokens": []}
            with (
                patch.object(
                    script_module,
                    "get_persona_intent_orchestrator",
                    return_value=orchestrator,
                    create=True,
                ),
                patch.object(
                    script_module, "persona_intent_maps", return_value=empty_maps
                ),
                patch.object(
                    script_module, "axis_catalog", return_value=axis_catalog_data
                ),
                patch.object(
                    script_module,
                    "static_prompt_catalog",
                    return_value=static_catalog_data,
                ),
            ):
                with tempfile.TemporaryDirectory() as tmpdir:
                    out_dir = Path(tmpdir)
                    script_module.generate(out_dir)
                    persona_text = (
                        (out_dir / "personaPreset.talon-list").read_text(
                            encoding="utf-8"
                        )
                    ).lower()
                    intent_text = (
                        (out_dir / "intentPreset.talon-list").read_text(
                            encoding="utf-8"
                        )
                    ).lower()
                    self.assertIn("teach junior dev: teach_junior_dev", persona_text)
                    self.assertIn("coach: teach_junior_dev", persona_text)
                    self.assertIn("guide choice: decide", intent_text)
                    self.assertIn("decide: decide", intent_text)

        def test_generated_lists_are_self_consistent_under_check(self) -> None:
            """Guardrail: generator --check should pass against its own output."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "generate_talon_lists.py"
            )
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
            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "generate_talon_lists.py"
            )
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
            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "generate_talon_lists.py"
            )
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
                    "personaPreset.talon-list",
                    "intentPreset.talon-list",
                ]:
                    (out_dir / name).write_text(
                        "list: user.placeholder\n-\n", encoding="utf-8"
                    )

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
