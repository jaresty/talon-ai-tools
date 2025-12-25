import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class GPTReadmeAxisListsTests(unittest.TestCase):
        def test_gpt_readme_states_axis_lists_untracked(self) -> None:
            """Guardrail: GPT README should describe catalog-driven, untracked axis/static lists."""

            readme = (
                Path(__file__).resolve().parents[1] / "GPT" / "readme.md"
            ).read_text(encoding="utf-8")
            self.assertIn(
                "catalog",
                readme,
                "Expected GPT README to reference the catalog as SSOT",
            )
            self.assertIn(
                "no longer tracked",
                readme,
                "Expected GPT README to state axis/static prompt .talon-lists are untracked",
            )
            self.assertIn(
                "make talon-lists",
                readme,
                "Expected GPT README to mention optional talon-lists helper",
            )
            self.assertIn(
                "talon-lists-check",
                readme,
                "Expected GPT README to mention talon-lists drift check helper",
            )
            self.assertIn(
                "--skip-list-files",
                readme,
                "Expected GPT README to mention catalog-only validation flag",
            )
            self.assertIn(
                "--no-skip-list-files",
                readme,
                "Expected GPT README to document opting back into list checks",
            )
            self.assertIn(
                "--lists-dir",
                readme,
                "Expected GPT README to note lists-dir is required when enforcing list checks",
            )
            self.assertIn(
                "axis-catalog-validate.py --lists-dir /path/to/lists --no-skip-list-files",
                readme,
                "Expected GPT README to include an explicit enforced list check example",
            )
            self.assertIn(
                "generate_talon_lists.py",
                readme,
                "Expected GPT README to hint at regenerating list files before enforced checks",
            )

        def test_gpt_module_uses_lifecycle_axis_snapshot(self) -> None:
            import talon_user.GPT.gpt as gpt_module  # type: ignore
            import talon_user.lib.historyLifecycle as history_lifecycle  # type: ignore

            self.assertIs(
                getattr(gpt_module, "axis_snapshot_from_axes"),
                history_lifecycle.axes_snapshot_from_axes,
                "GPT module should reuse lifecycle axis snapshots",
            )

else:

    class GPTReadmeAxisListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
