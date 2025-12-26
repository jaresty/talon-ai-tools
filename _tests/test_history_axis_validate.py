import os
import json
import os
import subprocess
import sys
import tempfile
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
            from talon_user.lib.historyLifecycle import clear_history, append_entry  # type: ignore

            clear_history()
            append_entry(
                "rid-summary",
                "prompt",
                "response",
                axes={"directional": ["fog"]},
                persona={
                    "persona_preset_spoken": "mentor",
                    "intent_preset_key": "decide",
                    "intent_preset_label": "Decide",
                    "intent_display": "Decide",
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
            streaming_lines = [
                line for line in lines if line.startswith("Streaming gating summary:")
            ]
            self.assertTrue(streaming_lines, msg=result.stdout)
            self.assertTrue(
                any("status=" in line for line in streaming_lines), msg=result.stdout
            )
            self.assertTrue(
                any("last_message=" in line for line in streaming_lines),
                msg=result.stdout,
            )

            summary_line = next(
                (line for line in lines if line.lstrip().startswith("{")),
                None,
            )
            self.assertIsNotNone(summary_line, msg=result.stdout)
            assert summary_line is not None
            stats = json.loads(summary_line)
            self.assertIn("total_entries", stats)
            self.assertIn("entries_missing_directional", stats)
            streaming_summary = stats.get("streaming_gating_summary", {})
            self.assertIsInstance(streaming_summary, dict)
            self.assertIn("status", streaming_summary)
            self.assertIn("last_message", streaming_summary)
            persona_pairs = stats.get("persona_alias_pairs", {})
            self.assertIn("teach_junior_dev", persona_pairs)
            self.assertEqual(persona_pairs["teach_junior_dev"].get("mentor"), 1)
            intent_pairs = stats.get("intent_display_pairs", {})
            self.assertIn("decide", intent_pairs)
            self.assertEqual(intent_pairs["decide"].get("Decide"), 1)
            clear_history()

        def test_history_stats_flag_noncanonical_intent_key(self) -> None:
            from talon_user.lib import historyLifecycle as history_lifecycle  # type: ignore
            from talon_user.lib.historyLifecycle import clear_history, append_entry  # type: ignore

            clear_history()
            append_entry(
                "rid-alias-intent",
                "prompt",
                "response",
                axes={"directional": ["fog"]},
                persona={
                    "persona_preset_spoken": "mentor",
                    "intent_preset_key": "for deciding",
                    "intent_display": "For deciding",
                },
            )

            stats = history_lifecycle.history_validation_stats()
            self.assertGreaterEqual(stats.get("intent_preset_missing_descriptor", 0), 1)
            self.assertGreaterEqual(stats.get("intent_invalid_tokens", 0), 1)
            clear_history()

        def test_script_fails_when_invalid_intent_tokens_present(self) -> None:
            from talon_user.lib.historyLifecycle import clear_history  # type: ignore

            clear_history()
            env = os.environ.copy()
            env["HISTORY_AXIS_VALIDATE_SIMULATE_INTENT_ALIAS_KEY"] = "1"
            result = subprocess.run(
                [sys.executable, "scripts/tools/history-axis-validate.py", "--summary"],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertNotEqual(result.returncode, 0, msg=result.stdout)
            self.assertIn("Intent invalid tokens", result.stdout)
            clear_history()

        def test_script_summary_path_writes_file(self) -> None:
            from talon_user.lib.historyLifecycle import clear_history  # type: ignore

            clear_history()
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

                with open(summary_path, "r", encoding="utf-8") as fh:
                    stats = json.load(fh)
            self.assertIn("total_entries", stats)
            self.assertIn("entries_missing_directional", stats)
            clear_history()

        def test_script_fails_when_invalid_intent_tokens_present(self) -> None:
            from talon_user.lib.historyLifecycle import clear_history  # type: ignore

            clear_history()
            env = os.environ.copy()
            env["HISTORY_AXIS_VALIDATE_SIMULATE_INTENT_ALIAS_KEY"] = "1"
            result = subprocess.run(
                [sys.executable, "scripts/tools/history-axis-validate.py", "--summary"],
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )
            self.assertNotEqual(result.returncode, 0, msg=result.stdout)
            self.assertIn("Intent invalid tokens", result.stdout)
            clear_history()

        def test_summary_path_includes_gating_last_drop_metadata(self) -> None:
            from talon_user.lib.historyLifecycle import clear_history  # type: ignore

            clear_history()
            with tempfile.TemporaryDirectory() as tmpdir:
                summary_path = os.path.join(tmpdir, "history-summary.json")
                env = os.environ.copy()
                env["HISTORY_AXIS_VALIDATE_SIMULATE_GATING_DROP"] = (
                    "Simulated gating drop for tests"
                )
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

                with open(summary_path, "r", encoding="utf-8") as fh:
                    stats = json.load(fh)
                self.assertEqual(
                    stats.get("gating_drop_last_message"),
                    "Simulated gating drop for tests",
                )
                self.assertEqual(stats.get("gating_drop_last_code"), "in_flight")
                streaming_summary = stats.get("streaming_gating_summary", {})
                self.assertIsInstance(streaming_summary, dict)
                self.assertEqual(
                    streaming_summary.get("last_message"),
                    "Simulated gating drop for tests",
                )
                self.assertEqual(streaming_summary.get("last_code"), "in_flight")
            clear_history()

        def test_script_summary_reports_default_gating_drop_lines(self) -> None:
            env = os.environ.copy()
            env["HISTORY_AXIS_VALIDATE_SIMULATE_GATING_DROP"] = "__DEFAULT__"
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

            stdout = result.stdout.replace("\r\n", "\n")
            expected_message = "GPT: A request is already running; wait for it to finish or cancel it first."
            self.assertIn(
                f"Last gating drop: {expected_message} (code=in_flight)", stdout
            )
            self.assertIn(
                f"Streaming last drop: {expected_message} (code=in_flight)", stdout
            )

            summary_line = next(
                (line for line in stdout.splitlines() if line.startswith("{")), None
            )
            self.assertIsNotNone(summary_line, msg=stdout)
            stats = json.loads(summary_line or "{}")
            self.assertEqual(stats.get("gating_drop_last_message"), expected_message)
            self.assertEqual(stats.get("gating_drop_last_code"), "in_flight")

        def test_summarize_json_outputs_summary(self) -> None:
            with tempfile.TemporaryDirectory() as tmpdir:
                summary_path = Path(tmpdir) / "history-summary.json"
                payload = {
                    "total_entries": 3,
                    "gating_drop_total": 2,
                    "streaming_gating_summary": {
                        "counts": {"in_flight": 2},
                        "last": {"reason": "in_flight", "reason_count": 2},
                        "total": 2,
                    },
                }
                summary_path.write_text(json.dumps(payload), encoding="utf-8")
                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-axis-validate.py",
                        "--summarize-json",
                        str(summary_path),
                        "--summary-format",
                        "streaming",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, msg=result.stderr)
                output = result.stdout.strip()
                expected = (
                    "Streaming gating summary: status=unknown; total=2; "
                    "counts=in_flight=2; sources=none; last=in_flight (count=2); "
                    "last_source=n/a; last_message=none"
                )
                self.assertEqual(output, expected)
                self.assertNotIn("### History Guardrail Summary", result.stdout)

                result_json = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-axis-validate.py",
                        "--summarize-json",
                        str(summary_path),
                        "--summary-format",
                        "json",
                        "--artifact-url",
                        "https://example.com/artifact",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result_json.returncode, 0, msg=result_json.stderr)
                json_output = json.loads(result_json.stdout.strip())
                streaming_summary = json_output.get("streaming_gating_summary")
                self.assertEqual(
                    streaming_summary,
                    {
                        "counts": {"in_flight": 2},
                        "counts_sorted": [{"reason": "in_flight", "count": 2}],
                        "sources": {},
                        "sources_sorted": [],
                        "last": {"reason": "in_flight", "reason_count": 2},
                        "last_source": {},
                        "total": 2,
                        "status": "unknown",
                        "last_message": "",
                        "last_code": "",
                    },
                )
                self.assertEqual(
                    json_output.get("artifact_url"), "https://example.com/artifact"
                )

                result_markdown = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-axis-validate.py",
                        "--summarize-json",
                        str(summary_path),
                        "--artifact-url",
                        "https://example.com/artifact",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(
                    result_markdown.returncode, 0, msg=result_markdown.stderr
                )
                markdown_output = result_markdown.stdout
                self.assertIn("### History Guardrail Summary", markdown_output)
                self.assertIn(
                    "- Streaming gating summary: status=unknown; total=2; counts=in_flight=2; sources=none; last=in_flight (count=2); last_source=n/a; last_message=none",
                    markdown_output,
                )
                self.assertIn("- Last gating drop: none", markdown_output)
                self.assertIn("- Streaming last drop: none", markdown_output)
                self.assertIn("Download artifact", markdown_output)

        def test_script_fails_when_persona_metadata_missing(self) -> None:
            from talon_user.lib.historyLifecycle import clear_history  # type: ignore

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
