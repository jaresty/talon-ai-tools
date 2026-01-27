import os
import pathlib
import subprocess
import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent

if bootstrap is not None:

    class BarCompletionCLITests(unittest.TestCase):
        maxDiff = None

        def _run(self, command: list[str]) -> subprocess.CompletedProcess[str]:
            result = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                self.fail(
                    "Command failed with exit code "
                    f"{result.returncode}: {' '.join(command)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                )
            return result

        def test_bar_completion_fish_generates_script(self) -> None:
            result = self._run(
                [
                    "go",
                    "run",
                    "./cmd/bar",
                    "completion",
                    "fish",
                    "--grammar",
                    "cmd/bar/testdata/grammar.json",
                ]
            )
            self.assertIn(
                "__fish_bar_completions",
                result.stdout,
                "Fish completion script should include helper function heading",
            )

        def test_bar_internal_complete_returns_suggestions(self) -> None:
            result = self._run(
                [
                    "go",
                    "run",
                    "./cmd/bar",
                    "__complete",
                    "bash",
                    "1",
                    "bar",
                ]
            )
            suggestions = []
            raw_suggestions = []
            raw_values = []
            for line in result.stdout.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                raw_suggestions.append(stripped)
                value = stripped.split("\t", 1)[0]
                raw_values.append(value)
                suggestions.append(value.strip())

            self.assertIn(
                "build",
                suggestions,
                "__complete helper should list available commands",
            )

            self.assertIn(
                "tui",
                suggestions,
                "__complete helper should list the Bubble Tea command",
            )

            self.assertTrue(
                all(v == v.strip() for v in raw_values),
                "completion values should not include trailing spaces",
            )

            self.assertTrue(
                all("\t" in item for item in raw_suggestions),
                "metadata columns should be present in completion output",
            )

        def test_bar_internal_complete_tui_flags(self) -> None:
            result = self._run(
                [
                    "go",
                    "run",
                    "./cmd/bar",
                    "__complete",
                    "bash",
                    "2",
                    "bar",
                    "tui",
                    "-",
                ]
            )

            values = []
            for line in result.stdout.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                value = stripped.split("\t", 1)[0]
                values.append(value)

            for expected in ["--grammar", "--fixture", "--no-alt-screen", "--env"]:
                self.assertIn(
                    expected,
                    values,
                    f"expected {expected!r} flag for bar tui completions",
                )

            for forbidden in ["--prompt", "--input", "--output", "--json"]:
                self.assertNotIn(
                    forbidden,
                    values,
                    f"did not expect {forbidden!r} to appear for bar tui completions",
                )

        def test_bar_internal_complete_uses_slug_values(self) -> None:
            tokens = [
                "bar",
                "build",
                "todo",
                "full",
                "focus",
                "system",
                "steps",
                "analysis",
                "checklist",
                "slack",
                "fog",
                "",
            ]
            index = str(len(tokens) - 1)
            result = self._run(
                [
                    "go",
                    "run",
                    "./cmd/bar",
                    "__complete",
                    "bash",
                    index,
                    *tokens,
                ]
            )

            values = []
            for line in result.stdout.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                value = stripped.split("\t", 1)[0]
                values.append(value)

            self.assertIn(
                "as-teacher",
                values,
                "persona voice suggestions should emit slug values without trailing space",
            )

        def test_bar_internal_complete_emits_channel_and_directional(self) -> None:
            tokens = [
                "bar",
                "build",
                "todo",
                "focus",
                "announce",
            ]
            result = self._run(
                [
                    "go",
                    "run",
                    "./cmd/bar",
                    "__complete",
                    "bash",
                    "5",
                    *tokens,
                ]
            )

            values = []
            for line in result.stdout.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                value = stripped.split("\t", 1)[0]
                values.append(value)

            self.assertIn(
                "slack",
                values,
                "channel suggestions should appear even before selecting a channel",
            )
            self.assertIn(
                "fly-rog",
                values,
                "directional suggestions should remain available alongside channel options",
            )

        def test_bar_internal_complete_optional_axes_without_static(self) -> None:
            result = self._run(
                [
                    "go",
                    "run",
                    "./cmd/bar",
                    "__complete",
                    "bash",
                    "2",
                    "bar",
                    "build",
                    "",
                ]
            )

            values = []
            for line in result.stdout.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                value = stripped.split("\t", 1)[0]
                values.append(value)

            for expected in [
                "full",
                "thing",
                "steps",
                "adr",
                "slack",
                "fly-rog",
            ]:
                self.assertIn(
                    expected,
                    values,
                    f"optional suggestion {expected!r} should be present",
                )

            self.assertIn(
                "make",
                values,
                "static suggestions should remain available",
            )
            static_index = values.index("make")
            for expected in [
                "full",
                "thing",
                "steps",
                "adr",
                "slack",
                "fly-rog",
            ]:
                self.assertGreater(
                    values.index(expected),
                    static_index,
                    f"{expected!r} should appear after static prompts",
                )

            ordered = [
                "full",
                "focus",
                "analysis",
                "checklist",
                "slack",
                "fly-rog",
            ]

            for earlier, later in zip(ordered, ordered[1:]):
                if earlier in values and later in values:
                    self.assertLess(
                        values.index(earlier),
                        values.index(later),
                        f"{earlier!r} should appear before {later!r}",
                    )


else:
    if not TYPE_CHECKING:

        class BarCompletionCLITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
