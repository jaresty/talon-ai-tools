"""Specifying validation: model run grammar is gated behind not user.gpt_busy
(ADR-035, ADR-0080 Workstream 3 grammar gating loop).

Invariants:
  1. GPT/gpt-run-commands.talon exists and declares `not user.gpt_busy` context.
  2. The primary `{user.model} run` rules are in the gated file.
  3. Non-run commands (`model cancel`, `model help`) are NOT in the gated file
     so they remain available during in-flight requests.
  4. `{user.model} run` lines are NOT present in the ungated gpt.talon
     (they have been moved to the gated file).
"""

import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:

    class GptRunBusyGuardTests(unittest.TestCase):
        @classmethod
        def setUpClass(cls) -> None:
            root = Path(__file__).resolve().parents[1]
            cls.gpt_talon = (root / "GPT" / "gpt.talon").read_text(encoding="utf-8")
            gated_path = root / "GPT" / "gpt-run-commands.talon"
            cls.gated_talon = gated_path.read_text(encoding="utf-8") if gated_path.exists() else ""
            cls.gated_exists = gated_path.exists()

        def test_gated_file_exists(self) -> None:
            """GPT/gpt-run-commands.talon must exist."""
            self.assertTrue(self.gated_exists, "GPT/gpt-run-commands.talon does not exist")

        def test_gated_file_declares_not_gpt_busy_context(self) -> None:
            """Gated file must have 'not user.gpt_busy' context header."""
            self.assertIn(
                "not user.gpt_busy",
                self.gated_talon,
                "gpt-run-commands.talon must declare 'not user.gpt_busy' context",
            )

        def test_primary_run_rule_in_gated_file(self) -> None:
            """The main `{user.model} run <user.applyPromptConfiguration>` rule must
            be in the gated file."""
            self.assertIn(
                "run <user.applyPromptConfiguration>",
                self.gated_talon,
                "primary run rule missing from gpt-run-commands.talon",
            )

        def test_run_preset_rule_in_gated_file(self) -> None:
            """`model run … preset` must be in the gated file."""
            self.assertIn(
                "run [<user.modelSimpleSource>] [<user.modelDestination>] preset",
                self.gated_talon,
                "preset run rule missing from gpt-run-commands.talon",
            )

        def test_cancel_not_in_gated_file(self) -> None:
            """`model cancel` must NOT be in the gated file — it must stay available
            during in-flight requests."""
            self.assertNotIn(
                "cancel",
                self.gated_talon,
                "model cancel must not be in the gated file",
            )

        def test_run_rules_removed_from_ungated_gpt_talon(self) -> None:
            """`{user.model} run` rules must be removed from gpt.talon so they
            don't fire without the busy-tag context guard."""
            for line in self.gpt_talon.splitlines():
                stripped = line.strip()
                # Ignore comment lines and blank lines.
                if not stripped or stripped.startswith("#"):
                    continue
                self.assertFalse(
                    "} run " in stripped or stripped.endswith("} run"),
                    f"Found run rule still in gpt.talon: {line!r}",
                )

else:
    if not TYPE_CHECKING:

        class GptRunBusyGuardTests(unittest.TestCase):  # type: ignore[no-redef]
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
