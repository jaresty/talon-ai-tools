import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class MakeGuardrailSkipListFilesTests(unittest.TestCase):
        def test_axis_guardrails_uses_skip_list_files(self) -> None:
            """Guardrail: axis guardrail targets should not require on-disk list files."""

            makefile = (Path(__file__).resolve().parents[1] / "Makefile").read_text(encoding="utf-8")
            self.assertIn("--skip-list-files", makefile)
            self.assertIn("axis-catalog-validate.py --verbose --skip-list-files", makefile)
            for line in makefile.splitlines():
                if "axis-guardrails" in line or "axis-catalog-validate" in line:
                    self.assertNotIn(
                        "GPT/lists",
                        line,
                        "Axis guardrail targets should not depend on tracked GPT/lists path",
                    )

else:

    class MakeGuardrailSkipListFilesTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
