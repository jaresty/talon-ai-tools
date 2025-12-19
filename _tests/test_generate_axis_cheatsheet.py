import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class GenerateAxisCheatSheetTests(unittest.TestCase):
        def test_generate_axis_cheatsheet_includes_catalog_tokens(self) -> None:
            """Guardrail: cheat sheet generator emits catalog-backed sections/tokens."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "generate-axis-cheatsheet.py"
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = Path(tmpdir) / "cheatsheet.md"
                result = subprocess.run(
                    [sys.executable, str(script), "--out", str(out_path)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).resolve().parents[1]),
                )
                if result.returncode != 0:
                    self.fail(
                        f"generate-axis-cheatsheet failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                content = out_path.read_text(encoding="utf-8")
                self.assertIn("Completeness (`completenessModifier`)", content)
                self.assertIn("Scope (`scopeModifier`)", content)
                self.assertIn("Method (`methodModifier`)", content)
                self.assertIn("Form (`formModifier`)", content)
                self.assertIn("Channel (`channelModifier`)", content)
                self.assertIn("Direction (`directionalModifier`)", content)

        def test_generate_axis_cheatsheet_tokens_match_catalog(self) -> None:
            """Guardrail: cheat sheet tokens mirror axis_catalog tokens."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "generate-axis-cheatsheet.py"
            )
            from talon_user.lib.axisCatalog import axis_catalog
            from talon_user.lib.requestLog import axis_snapshot_from_axes

            catalog = axis_catalog()
            axes = catalog.get("axes", {}) or {}
            axis_lists = catalog.get("axis_list_tokens", {}) or {}

            def expected_tokens(axis: str) -> set[str]:
                token_candidates: list[str] = []
                token_candidates.extend(axis_lists.get(axis, []) or [])
                token_candidates.extend((axes.get(axis) or {}).keys())
                seen: set[str] = set()
                for token in token_candidates:
                    snapshot = axis_snapshot_from_axes({axis: [token]})
                    canonical = snapshot.get(axis, []) or []
                    if canonical:
                        for value in canonical:
                            if value not in seen:
                                seen.add(value)
                        continue
                    cleaned = str(token).strip()
                    if not cleaned or cleaned.lower().startswith("important:"):
                        continue
                    lowered = cleaned.lower()
                    if lowered not in seen:
                        seen.add(lowered)
                return seen

            with tempfile.TemporaryDirectory() as tmpdir:
                out_path = Path(tmpdir) / "cheatsheet.md"
                result = subprocess.run(
                    [sys.executable, str(script), "--out", str(out_path)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(Path(__file__).resolve().parents[1]),
                )
                if result.returncode != 0:
                    self.fail(
                        f"generate-axis-cheatsheet failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                content = out_path.read_text(encoding="utf-8")
                for axis, heading in (
                    ("completeness", "Completeness (`completenessModifier`):"),
                    ("scope", "Scope (`scopeModifier`):"),
                    ("method", "Method (`methodModifier`):"),
                    ("form", "Form (`formModifier`):"),
                    ("channel", "Channel (`channelModifier`):"),
                    ("directional", "Direction (`directionalModifier`):"),
                ):
                    line = next(
                        (ln for ln in content.splitlines() if heading in ln), ""
                    )
                    self.assertTrue(line, f"Missing heading for {axis}")
                    tokens = {
                        part.strip(" `")
                        for part in line.split(":")[1].split(",")
                        if part.strip(" `")
                    }
                    self.assertSetEqual(
                        tokens,
                        expected_tokens(axis),
                        f"Cheat sheet tokens for {axis} differ from canonical snapshot",
                    )
