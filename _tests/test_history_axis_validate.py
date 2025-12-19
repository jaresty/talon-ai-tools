import os
import subprocess
import sys
import tempfile
import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:

    class HistoryAxisValidateTests(unittest.TestCase):
        def test_script_passes_with_clean_history(self) -> None:
            env = os.environ.copy()
            env.pop("HISTORY_AXIS_VALIDATE_SIMULATE_PERSONA_FAILURE", None)
            result = subprocess.run(
                [sys.executable, "scripts/tools/history-axis-validate.py"],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn(
                "History axis validation passed",
                result.stdout,
            )
            self.assertIn(
                "docs/help now consume the shared AxisSnapshot façade",
                result.stdout,
            )

        def test_script_summary_outputs_stats(self) -> None:
            from talon_user.lib.requestLog import clear_history, append_entry  # type: ignore

            clear_history()
            append_entry(
                "rid-summary",
                "prompt",
                "response",
                axes={"directional": ["fog"]},
                persona={
                    "persona_preset_spoken": "mentor",
                    "intent_display": "For deciding",
                },
            )
            env = os.environ.copy()
            env["HISTORY_AXIS_VALIDATE_SIMULATE_PERSONA_ALIAS"] = "1"
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/tools/history-axis-validate.py",
                    "--summary",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            lines = [line for line in result.stdout.splitlines() if line.strip()]
            self.assertGreaterEqual(len(lines), 2)
            import json

            summary_line = next(
                (line for line in lines if line.lstrip().startswith("{")),
                None,
            )
            self.assertIsNotNone(summary_line, msg=result.stdout)
            stats = json.loads(summary_line)
            self.assertIn("total_entries", stats)
            self.assertIn("entries_missing_directional", stats)
            persona_pairs = stats.get("persona_alias_pairs", {})
            self.assertIn("teach_junior_dev", persona_pairs)
            self.assertEqual(persona_pairs["teach_junior_dev"].get("mentor"), 1)
            intent_pairs = stats.get("intent_display_pairs", {})
            self.assertIn("decide", intent_pairs)
            self.assertEqual(intent_pairs["decide"].get("For deciding"), 1)
            clear_history()

        def test_script_summary_path_writes_file(self) -> None:
            from talon_user.lib.requestLog import clear_history, append_entry  # type: ignore

            clear_history()
            append_entry(
                "rid-summary-path",
                "prompt",
                "response",
                axes={"directional": ["fog"]},
            )
            with tempfile.TemporaryDirectory() as tmpdir:
                summary_path = os.path.join(tmpdir, "history-summary.json")
                env = os.environ.copy()
                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-axis-validate.py",
                        "--summary-path",
                        summary_path,
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=env,
                )
                self.assertEqual(result.returncode, 0, msg=result.stderr)
                self.assertTrue(os.path.exists(summary_path))
                import json

                with open(summary_path, "r", encoding="utf-8") as fh:
                    stats = json.load(fh)
                self.assertIn("total_entries", stats)
                self.assertIn("entries_missing_directional", stats)
            clear_history()

        def test_script_fails_when_persona_metadata_missing(self) -> None:
            from talon_user.lib.requestLog import clear_history  # type: ignore

            clear_history()

            env = os.environ.copy()
            env["HISTORY_AXIS_VALIDATE_SIMULATE_PERSONA_FAILURE"] = "1"
            result = subprocess.run(
                [sys.executable, "scripts/tools/history-axis-validate.py"],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("persona snapshot", result.stderr)
            clear_history()

else:
    if not TYPE_CHECKING:

        class HistoryAxisValidateTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass


if __name__ == "__main__":
    unittest.main()
