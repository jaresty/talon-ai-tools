import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class GuardrailTargetsNoTalonListsTests(unittest.TestCase):
        def test_axis_guardrail_targets_do_not_depend_on_talon_lists(self) -> None:
            """Guardrail: guardrail targets should not depend on talon-lists generation."""

            makefile = (Path(__file__).resolve().parents[1] / "Makefile").read_text(encoding="utf-8")
            for target in ("axis-guardrails", "axis-guardrails-ci", "axis-guardrails-test", "ci-guardrails"):
                with self.subTest(target=target):
                    lines = [line for line in makefile.splitlines() if line.strip().startswith(f"{target}:")]
                    self.assertTrue(lines, f"Expected to find target {target} in Makefile")
                    for line in lines:
                        self.assertNotIn(
                            "talon-lists",
                            line,
                            f"{target} should not depend on talon-lists (untracked helpers)",
                        )

else:

    class GuardrailTargetsNoTalonListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
