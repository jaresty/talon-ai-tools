import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    @contextmanager
    def isolate_telemetry_dir():
        repo_root = Path(__file__).resolve().parents[1]
        telemetry_dir = repo_root / "artifacts" / "telemetry"
        artifacts_root = telemetry_dir.parent
        backup_dir = None
        try:
            artifacts_root.mkdir(parents=True, exist_ok=True)
            if telemetry_dir.exists():
                backup_dir = Path(
                    tempfile.mkdtemp(
                        prefix="telemetry-backup-", dir=str(artifacts_root)
                    )
                )
                shutil.rmtree(backup_dir)
                telemetry_dir.rename(backup_dir)
            telemetry_dir.mkdir(parents=True, exist_ok=True)
            yield telemetry_dir
        finally:
            shutil.rmtree(telemetry_dir, ignore_errors=True)
            if backup_dir is not None and backup_dir.exists():
                backup_dir.rename(telemetry_dir)

    class MakeRequestHistoryGuardrailsTests(unittest.TestCase):
        def test_make_request_history_guardrails_runs_clean(self) -> None:
            """Guardrail: request-history-guardrails target should run without errors."""

            repo_root = Path(__file__).resolve().parents[1]
            with isolate_telemetry_dir():
                summary_path = (
                    repo_root
                    / "artifacts"
                    / "telemetry"
                    / "history-validation-summary.json"
                )
                summary_dir = summary_path.parent
                summary_dir.mkdir(parents=True, exist_ok=True)
                if summary_path.exists():
                    summary_path.unlink()
                skip_path = summary_path.with_name("suggestion-skip-summary.json")
                skip_payload_seed = {
                    "counts": {"streaming_disabled": 2, "rate_limited": 1},
                    "total_skipped": 3,
                    "reason_counts": [
                        {"reason": "streaming_disabled", "count": 2},
                        {"reason": "rate_limited", "count": 1},
                    ],
                }
                skip_path.write_text(
                    json.dumps(skip_payload_seed, indent=2), encoding="utf-8"
                )
                telemetry_path = summary_path.with_name(
                    "history-validation-summary.telemetry.json"
                )
                if telemetry_path.exists():
                    telemetry_path.unlink()
                streaming_summary_path = summary_path.with_name(
                    "history-validation-summary.streaming.json"
                )
                if streaming_summary_path.exists():
                    streaming_summary_path.unlink()
                env = os.environ.copy()
                env["ALLOW_STALE_TELEMETRY"] = "1"
                result = subprocess.run(
                    ["make", "request-history-guardrails"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    check=False,
                    env=env,
                )
                if result.returncode != 0:
                    self.fail(
                        "make request-history-guardrails failed:\n"
                        f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                lines = [line for line in result.stdout.splitlines() if line.strip()]
                self.assertTrue(lines, "make output unexpectedly empty")
                self.assertIn(
                    "Streaming gating summary: status=unknown; total=0; counts=none; sources=none; last=n/a; last_source=n/a; last_message=none",
                    result.stdout,
                )
                self.assertIn(
                    "Suggestion skip summary (json):",
                    result.stdout,
                )
                self.assertIn("Suggestion skip total: 3", result.stdout)
                self.assertIn(
                    "Suggestion skip reasons: streaming_disabled=2, rate_limited=1",
                    result.stdout,
                )
                self.assertIn("Telemetry scheduler stats:", result.stdout)

                self.assertIn("- Last gating drop: none", result.stdout)
                self.assertIn("- Streaming last drop: none", result.stdout)
                self.assertIn("Suggestion skip summary (json):", result.stdout)
                self.assertIn("Suggestion skip total: 3", result.stdout)
                self.assertIn(
                    "Suggestion skip reasons: streaming_disabled=2, rate_limited=1",
                    result.stdout,
                )
                self.assertTrue(
                    summary_path.exists(),
                    "request-history-guardrails did not produce history-validation-summary.json",
                )
                with summary_path.open("r", encoding="utf-8") as handle:
                    stats = json.load(handle)
                self.assertIn("total_entries", stats)
                self.assertIn("entries_missing_directional", stats)
                self.assertIn("streaming_gating_summary", stats)

                streaming_summary_path = summary_path.with_name(
                    "history-validation-summary.streaming.json"
                )
                self.assertTrue(
                    streaming_summary_path.exists(),
                    "Streaming JSON summary was not produced",
                )
                with streaming_summary_path.open("r", encoding="utf-8") as handle:
                    streaming_data = json.load(handle)
                self.assertEqual(
                    streaming_data.get("streaming_gating_summary"),
                    {
                        "counts": {},
                        "counts_sorted": [],
                        "sources": {},
                        "sources_sorted": [],
                        "last": {},
                        "last_source": {},
                        "total": 0,
                        "status": "unknown",
                        "last_message": "",
                        "last_code": "",
                    },
                )

                telemetry_path = summary_path.with_name(
                    "history-validation-summary.telemetry.json"
                )
                self.assertTrue(
                    telemetry_path.exists(),
                    "Telemetry export was not produced",
                )
                telemetry_payload = json.loads(
                    telemetry_path.read_text(encoding="utf-8")
                )
                self.assertEqual(telemetry_payload.get("total_entries"), 0)
                self.assertEqual(telemetry_payload.get("gating_drop_total"), 0)
                self.assertIn("generated_at", telemetry_payload)
                self.assertEqual(telemetry_payload.get("top_gating_reasons"), [])
                self.assertEqual(telemetry_payload.get("top_gating_sources"), [])
                self.assertEqual(telemetry_payload.get("streaming_status"), "unknown")
                self.assertEqual(telemetry_payload.get("last_drop_message"), "none")
                self.assertIsNone(telemetry_payload.get("last_drop_code"))
                self.assertEqual(
                    telemetry_payload.get("scheduler"),
                    {
                        "reschedule_count": 0,
                        "last_interval_minutes": None,
                        "last_reason": "",
                        "last_timestamp": "",
                    },
                )
                skip_path = summary_path.with_name("suggestion-skip-summary.json")
                self.assertTrue(
                    skip_path.exists(),
                    "Suggestion skip summary was not produced",
                )
                skip_payload = json.loads(skip_path.read_text(encoding="utf-8"))
                self.assertEqual(skip_payload.get("total_skipped"), 3)
                self.assertEqual(
                    skip_payload.get("reason_counts"),
                    [
                        {"reason": "streaming_disabled", "count": 2},
                        {"reason": "rate_limited", "count": 1},
                    ],
                )
                telemetry_skip = telemetry_payload.get("suggestion_skip", {})
                self.assertEqual(telemetry_skip.get("total"), 3)
                self.assertEqual(
                    telemetry_skip.get("reasons"),
                    [
                        {"reason": "streaming_disabled", "count": 2},
                        {"reason": "rate_limited", "count": 1},
                    ],
                )

        def test_make_request_history_guardrails_fast_produces_summary(self) -> None:
            """Guardrail: request-history-guardrails-fast should export the validation summary."""

            repo_root = Path(__file__).resolve().parents[1]
            with isolate_telemetry_dir():
                summary_path = (
                    repo_root
                    / "artifacts"
                    / "telemetry"
                    / "history-validation-summary.json"
                )
                summary_dir = summary_path.parent
                summary_dir.mkdir(parents=True, exist_ok=True)
                if summary_path.exists():
                    summary_path.unlink()
                skip_path = summary_path.with_name("suggestion-skip-summary.json")
                skip_payload_seed = {
                    "counts": {"streaming_disabled": 2, "rate_limited": 1},
                    "total_skipped": 3,
                    "reason_counts": [
                        {"reason": "streaming_disabled", "count": 2},
                        {"reason": "rate_limited", "count": 1},
                    ],
                }
                skip_path.write_text(
                    json.dumps(skip_payload_seed, indent=2), encoding="utf-8"
                )
                telemetry_path = summary_path.with_name(
                    "history-validation-summary.telemetry.json"
                )
                if telemetry_path.exists():
                    telemetry_path.unlink()
                streaming_summary_path = summary_path.with_name(
                    "history-validation-summary.streaming.json"
                )
                if streaming_summary_path.exists():
                    streaming_summary_path.unlink()
                env = os.environ.copy()
                env["ALLOW_STALE_TELEMETRY"] = "1"
                result = subprocess.run(
                    ["make", "request-history-guardrails-fast"],
                    cwd=str(repo_root),
                    capture_output=True,
                    text=True,
                    check=False,
                    env=env,
                )
                if result.returncode != 0:
                    self.fail(
                        "make request-history-guardrails-fast failed:\n"
                        f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                lines = [line for line in result.stdout.splitlines() if line.strip()]
                self.assertTrue(lines, "make output unexpectedly empty")
                self.assertIn(
                    "Streaming gating summary: status=unknown; total=0; counts=none; sources=none; last=n/a; last_source=n/a; last_message=none",
                    result.stdout,
                )
                self.assertIn(
                    "Suggestion skip summary (json):",
                    result.stdout,
                )
                self.assertIn("Suggestion skip total: 3", result.stdout)
                self.assertIn(
                    "Suggestion skip reasons: streaming_disabled=2, rate_limited=1",
                    result.stdout,
                )
                self.assertIn("Telemetry scheduler stats:", result.stdout)

                self.assertIn("- Last gating drop: none", result.stdout)
                self.assertIn("- Streaming last drop: none", result.stdout)
                self.assertIn("Suggestion skip summary (json):", result.stdout)
                self.assertIn("Suggestion skip total: 3", result.stdout)
                self.assertIn(
                    "Suggestion skip reasons: streaming_disabled=2, rate_limited=1",
                    result.stdout,
                )
                self.assertTrue(
                    summary_path.exists(),
                    "request-history-guardrails-fast did not produce history-validation-summary.json",
                )
                with summary_path.open("r", encoding="utf-8") as handle:
                    stats = json.load(handle)
                self.assertIn("total_entries", stats)
                self.assertIn("entries_missing_directional", stats)
                self.assertIn("streaming_gating_summary", stats)

                streaming_summary_path = summary_path.with_name(
                    "history-validation-summary.streaming.json"
                )
                self.assertTrue(
                    streaming_summary_path.exists(),
                    "Streaming JSON summary was not produced (fast target)",
                )
                with streaming_summary_path.open("r", encoding="utf-8") as handle:
                    streaming_data = json.load(handle)
                self.assertEqual(
                    streaming_data.get("streaming_gating_summary"),
                    {
                        "counts": {},
                        "counts_sorted": [],
                        "sources": {},
                        "sources_sorted": [],
                        "last": {},
                        "last_source": {},
                        "total": 0,
                        "status": "unknown",
                        "last_message": "",
                        "last_code": "",
                    },
                )

                telemetry_path = summary_path.with_name(
                    "history-validation-summary.telemetry.json"
                )
                self.assertTrue(
                    telemetry_path.exists(),
                    "Telemetry export was not produced (fast target)",
                )
                telemetry_payload = json.loads(
                    telemetry_path.read_text(encoding="utf-8")
                )
                self.assertEqual(telemetry_payload.get("total_entries"), 0)
                self.assertEqual(telemetry_payload.get("gating_drop_total"), 0)
                self.assertIn("generated_at", telemetry_payload)
                self.assertEqual(telemetry_payload.get("top_gating_reasons"), [])
                self.assertEqual(telemetry_payload.get("top_gating_sources"), [])
                self.assertEqual(telemetry_payload.get("streaming_status"), "unknown")
                self.assertEqual(telemetry_payload.get("last_drop_message"), "none")
                self.assertIsNone(telemetry_payload.get("last_drop_code"))
                self.assertEqual(
                    telemetry_payload.get("scheduler"),
                    {
                        "reschedule_count": 0,
                        "last_interval_minutes": None,
                        "last_reason": "",
                        "last_timestamp": "",
                    },
                )
                skip_path = summary_path.with_name("suggestion-skip-summary.json")
                self.assertTrue(
                    skip_path.exists(),
                    "Suggestion skip summary was not produced (fast target)",
                )
                skip_payload = json.loads(skip_path.read_text(encoding="utf-8"))
                self.assertEqual(skip_payload.get("total_skipped"), 3)
                self.assertEqual(
                    skip_payload.get("reason_counts"),
                    [
                        {"reason": "streaming_disabled", "count": 2},
                        {"reason": "rate_limited", "count": 1},
                    ],
                )
                telemetry_skip = telemetry_payload.get("suggestion_skip", {})
                self.assertEqual(telemetry_skip.get("total"), 3)
                self.assertEqual(
                    telemetry_skip.get("reasons"),
                    [
                        {"reason": "streaming_disabled", "count": 2},
                        {"reason": "rate_limited", "count": 1},
                    ],
                )

else:
    if not TYPE_CHECKING:

        class MakeRequestHistoryGuardrailsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
