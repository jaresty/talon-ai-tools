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

    class RunGuardrailsCITests(unittest.TestCase):
        def test_run_guardrails_ci_script(self) -> None:
            """Guardrail: CI helper script should run guardrails successfully."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            repo_root = Path(__file__).resolve().parents[1]
            with isolate_telemetry_dir():
                summary_path = (
                    repo_root
                    / "artifacts"
                    / "telemetry"
                    / "history-validation-summary.json"
                )
                if summary_path.exists():
                    summary_path.unlink()
                result = subprocess.run(
                    ["/bin/bash", str(script), "axis-guardrails-ci"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(repo_root),
                )
            if result.returncode != 0:
                self.fail(
                    f"run_guardrails_ci.sh failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn(
                "Axis catalog validation passed",
                result.stdout,
                "Expected guardrail script to run catalog validation",
            )
            self.assertIn(
                "Running guardrails target: axis-guardrails-ci", result.stdout
            )
            self.assertIn(
                "target axis-guardrails-ci does not require it",
                result.stdout,
                "Expected optional summary message for axis guardrails target",
            )
            self.assertIn(
                "History summary not required for target axis-guardrails-ci; no job summary entry created.",
                result.stdout,
            )

        def test_run_guardrails_ci_help(self) -> None:
            """Guardrail: CI helper script should expose help/usage."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            result = subprocess.run(
                ["/bin/bash", str(script), "--help"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            if result.returncode != 0:
                self.fail(
                    f"run_guardrails_ci.sh --help failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn("Usage: scripts/tools/run_guardrails_ci.sh", result.stdout)
            self.assertIn("catalog-only", result.stdout)
            self.assertIn("GUARDRAILS_TARGET", result.stdout)
            self.assertIn("axis-guardrails-ci", result.stdout)

        def test_run_guardrails_ci_env_override(self) -> None:
            """Guardrail: CI helper should honor GUARDRAILS_TARGET when no arg is provided."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            env = os.environ.copy()
            env["GUARDRAILS_TARGET"] = "axis-guardrails-ci"

            result = subprocess.run(
                ["/bin/bash", str(script)],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
                env=env,
            )
            if result.returncode != 0:
                self.fail(
                    f"run_guardrails_ci.sh with GUARDRAILS_TARGET failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn(
                "Axis catalog validation passed",
                result.stdout,
                "Expected guardrail script to run catalog validation via env target",
            )
            self.assertIn(
                "Running guardrails target: axis-guardrails-ci", result.stdout
            )

        def test_run_guardrails_ci_history_target_produces_summary(self) -> None:
            """Guardrail: history guardrail target should emit and persist the summary."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
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
                streaming_summary_path = summary_path.with_name(
                    "history-validation-summary.streaming.json"
                )
                if streaming_summary_path.exists():
                    streaming_summary_path.unlink()
                telemetry_path = summary_path.with_name(
                    "history-validation-summary.telemetry.json"
                )
                if telemetry_path.exists():
                    telemetry_path.unlink()
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
                streak_path = summary_path.with_name("cli-warning-streak.json")
                streak_state = {
                    "streak": 2,
                    "last_reason": "missing",
                    "last_command": "python3 scripts/tools/check-telemetry-export-marker.py",
                    "updated_at": "2025-12-23T02:12:00Z",
                }
                streak_path.write_text(
                    json.dumps(streak_state, indent=2), encoding="utf-8"
                )

                env = os.environ.copy()
                env["ALLOW_STALE_TELEMETRY"] = "1"
                result = subprocess.run(
                    ["/bin/bash", str(script), "request-history-guardrails"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(repo_root),
                    env=env,
                )
                if result.returncode != 0:
                    self.fail(
                        "run_guardrails_ci.sh request-history-guardrails failed with code "
                        f"{result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                    )
                self.assertIn(
                    "History validation summary (JSON):",
                    result.stdout,
                    "Expected CI helper to log the saved history summary",
                )
                self.assertTrue(
                    summary_path.exists(),
                    "run_guardrails_ci.sh did not write the history summary artifact",
                )
                with summary_path.open("r", encoding="utf-8") as handle:
                    stats = json.load(handle)
                self.assertIn("gating_drop_counts", stats)
                self.assertIn(
                    "History summary stats: total_entries=0 gating_drop_total=0",
                    result.stdout,
                )
                self.assertIn(
                    "History summary gating status: unknown",
                    result.stdout,
                )
                self.assertIn(
                    "History summary last drop: none",
                    result.stdout,
                )
                self.assertIn(
                    "Streaming gating last drop: none",
                    result.stdout,
                )
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
                self.assertIn(
                    "- Streak alert: 2 consecutive warnings (reason: missing)",
                    result.stdout,
                )
                self.assertIn("Telemetry export streak state:", result.stdout)
                self.assertIn(
                    "- Telemetry export warning streak: 2",
                    result.stdout,
                )
                self.assertIn(
                    "- Telemetry export last reason: missing",
                    result.stdout,
                )
                self.assertIn(
                    "- Telemetry export last updated: 2025-12-23T02:12:00Z",
                    result.stdout,
                )
                self.assertIn(
                    "- Telemetry export last command: python3 scripts/tools/check-telemetry-export-marker.py",
                    result.stdout,
                )
                self.assertIn("Telemetry scheduler stats:", result.stdout)
                self.assertIn("- Scheduler reschedules: 0", result.stdout)
                self.assertIn(
                    "- Scheduler last interval (minutes): none",
                    result.stdout,
                )
                self.assertIn("- Scheduler last reason: none", result.stdout)
                self.assertIn("- Scheduler last timestamp: none", result.stdout)
                self.assertIn(
                    "- Scheduler data source: defaults (missing)",
                    result.stdout,
                )
                self.assertIn(
                    "WARNING: Scheduler telemetry missing; run `model export telemetry` inside Talon to populate stats.",
                    result.stdout,
                )

                self.assertIn(
                    "- Streaming gating summary: status=unknown; total=0; counts=none; sources=none; last=n/a; last_source=n/a; last_message=none",
                    result.stdout,
                )
                self.assertIn("- Last gating drop: none", result.stdout)
                self.assertIn("- Streaming last drop: none", result.stdout)
                self.assertIn(
                    "- Artifact link unavailable outside GitHub Actions.",
                    result.stdout,
                )
                self.assertIn("### History Guardrail Summary", result.stdout)
                self.assertIn(
                    "History summary recorded at artifacts/telemetry/history-validation-summary.json; job summary will reference this file when running in GitHub Actions.",
                    result.stdout,
                )

                streaming_summary_path = summary_path.with_name(
                    "history-validation-summary.streaming.json"
                )
                self.assertTrue(
                    streaming_summary_path.exists(),
                    "run_guardrails_ci.sh did not produce streaming JSON summary",
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
                    "run_guardrails_ci.sh did not produce telemetry export",
                )
                telemetry_payload = json.loads(
                    telemetry_path.read_text(encoding="utf-8")
                )
                self.assertEqual(telemetry_payload.get("total_entries"), 0)
                self.assertEqual(telemetry_payload.get("gating_drop_total"), 0)
                self.assertIn("generated_at", telemetry_payload)
                self.assertEqual(telemetry_payload.get("top_gating_reasons"), [])
                self.assertEqual(telemetry_payload.get("top_gating_sources"), [])
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
                telemetry_skip = telemetry_payload.get("suggestion_skip", {})
                self.assertEqual(telemetry_skip.get("total"), 3)
                self.assertEqual(
                    telemetry_skip.get("reasons"),
                    [
                        {"reason": "streaming_disabled", "count": 2},
                        {"reason": "rate_limited", "count": 1},
                    ],
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

                self.assertIn(
                    "Telemetry summary saved at artifacts/telemetry/history-validation-summary.telemetry.json",
                    result.stdout,
                )
                self.assertIn(
                    "Streaming JSON summary recorded at artifacts/telemetry/history-validation-summary.streaming.json; job summary will reference this file when running in GitHub Actions.",
                    result.stdout,
                )
                self.assertIn("- Scheduler reschedules: 0", result.stdout)
                self.assertIn(
                    "- Scheduler last interval (minutes): none",
                    result.stdout,
                )
                self.assertIn("- Scheduler last reason: none", result.stdout)
                self.assertIn("- Scheduler last timestamp: none", result.stdout)

        def test_run_guardrails_ci_writes_job_summary(self) -> None:
            """Guardrail: CI helper should append history summary to GitHub step summary when provided."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
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
                streaming_summary_path = summary_path.with_name(
                    "history-validation-summary.streaming.json"
                )
                if streaming_summary_path.exists():
                    streaming_summary_path.unlink()
                telemetry_path = summary_path.with_name(
                    "history-validation-summary.telemetry.json"
                )
                if telemetry_path.exists():
                    telemetry_path.unlink()
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
                streak_path = summary_path.with_name("cli-warning-streak.json")
                streak_state = {
                    "streak": 2,
                    "last_reason": "missing",
                    "last_command": "python3 scripts/tools/check-telemetry-export-marker.py",
                    "updated_at": "2025-12-23T02:12:00Z",
                }
                streak_path.write_text(
                    json.dumps(streak_state, indent=2), encoding="utf-8"
                )
                with tempfile.TemporaryDirectory() as tmpdir:
                    step_summary_path = Path(tmpdir) / "gha-summary.md"
                    env = os.environ.copy()
                    env["ALLOW_STALE_TELEMETRY"] = "1"
                    env["GITHUB_STEP_SUMMARY"] = str(step_summary_path)
                    env.setdefault("GITHUB_SERVER_URL", "https://github.com")

                    env["GITHUB_REPOSITORY"] = "example/repo"
                    env["GITHUB_RUN_ID"] = "12345"
                    result = subprocess.run(
                        ["/bin/bash", str(script), "request-history-guardrails"],
                        check=False,
                        capture_output=True,
                        text=True,
                        cwd=str(repo_root),
                        env=env,
                    )
                    if result.returncode != 0:
                        self.fail(
                            "run_guardrails_ci.sh request-history-guardrails failed with code "
                            f"{result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                        )
                    self.assertTrue(
                        step_summary_path.exists(),
                        "run_guardrails_ci.sh did not append to the GitHub step summary file",
                    )
                    summary_text = step_summary_path.read_text(encoding="utf-8")

            self.assertIn(
                "- suggestion skip reasons: streaming_disabled=2, rate_limited=1",
                summary_text,
            )
            self.assertIn("### Scheduler Telemetry", summary_text)
            self.assertIn("- Scheduler reschedules: 0", summary_text)
            self.assertIn(
                "- Scheduler last interval (minutes): none",
                summary_text,
            )
            self.assertIn("- Scheduler last reason: none", summary_text)
            self.assertIn("- Scheduler last timestamp: none", summary_text)
            self.assertIn("- Scheduler data source: defaults (missing)", summary_text)
            self.assertIn(
                "WARNING: Scheduler telemetry missing; run `model export telemetry` inside Talon to populate stats.",
                summary_text,
            )
            self.assertIn("### Telemetry Export Streak", summary_text)
            self.assertIn(
                "| Telemetry export streak | 2 consecutive warnings (reason: missing) |",
                summary_text,
            )
            self.assertIn("Telemetry export streak state:", summary_text)
            self.assertIn("- Telemetry export warning streak: 2", summary_text)

            self.assertIn("- Telemetry export last reason: missing", summary_text)
            self.assertIn(
                "- Telemetry export last command: python3 scripts/tools/check-telemetry-export-marker.py",
                summary_text,
            )
            self.assertIn(
                "- Telemetry export last updated: 2025-12-23T02:12:00Z",
                summary_text,
            )

        def test_run_guardrails_ci_fast_target_writes_target_line(self) -> None:
            """Guardrail: fast history target should label the guardrail target in summaries."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            repo_root = Path(__file__).resolve().parents[1]
            with isolate_telemetry_dir():
                summary_dir = repo_root / "artifacts" / "telemetry"
                summary_dir.mkdir(parents=True, exist_ok=True)
                summary_path = summary_dir / "history-validation-summary.json"
                streaming_summary_path = (
                    summary_dir / "history-validation-summary.streaming.json"
                )
                telemetry_path = (
                    summary_dir / "history-validation-summary.telemetry.json"
                )
                skip_path = summary_dir / "suggestion-skip-summary.json"
                streak_path = summary_dir / "cli-warning-streak.json"

                for path in (
                    summary_path,
                    streaming_summary_path,
                    telemetry_path,
                    skip_path,
                    streak_path,
                ):
                    if path.exists():
                        path.unlink()

                # Seed suggestion skip + streak artefacts to avoid CLI fallbacks.
                skip_payload_seed = {
                    "counts": {"streaming_disabled": 1},
                    "total_skipped": 1,
                    "reason_counts": [
                        {"reason": "streaming_disabled", "count": 1},
                    ],
                }
                skip_path.write_text(
                    json.dumps(skip_payload_seed, indent=2), encoding="utf-8"
                )
                streak_state = {
                    "streak": 0,
                    "last_reason": None,
                    "last_command": "python3 scripts/tools/check-telemetry-export-marker.py",
                    "updated_at": "2025-12-23T02:12:00Z",
                }
                streak_path.write_text(
                    json.dumps(streak_state, indent=2), encoding="utf-8"
                )

                # Provide a no-op make so the script relies on the prepared artefacts.
                with tempfile.TemporaryDirectory() as tmpdir:
                    fake_make = Path(tmpdir) / "make"
                    fake_make.write_text(
                        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
                    )
                    fake_make.chmod(0o755)
                    step_summary_path = Path(tmpdir) / "gha-summary.md"
                    env = os.environ.copy()
                    env["ALLOW_STALE_TELEMETRY"] = "1"
                    env["PATH"] = f"{tmpdir}{os.pathsep}{env.get('PATH', '')}"
                    env["GITHUB_STEP_SUMMARY"] = str(step_summary_path)
                    env.setdefault("GITHUB_SERVER_URL", "https://github.com")
                    env["GITHUB_REPOSITORY"] = "example/repo"
                    env["GITHUB_RUN_ID"] = "67890"

                    result = subprocess.run(
                        ["/bin/bash", str(script), "request-history-guardrails-fast"],
                        check=False,
                        capture_output=True,
                        text=True,
                        cwd=str(repo_root),
                        env=env,
                    )

                    if result.returncode != 0:
                        self.fail(
                            "run_guardrails_ci.sh request-history-guardrails-fast failed with code "
                            f"{result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                        )
                    self.assertTrue(
                        step_summary_path.exists(),
                        "run_guardrails_ci.sh did not append to the GitHub step summary file for the fast target",
                    )
                    summary_text = step_summary_path.read_text(encoding="utf-8")

            self.assertIn(
                "History guardrail target: request-history-guardrails-fast",
                result.stdout,
            )
            self.assertIn(
                "- guardrail target: request-history-guardrails-fast",
                summary_text,
            )

        def test_run_guardrails_ci_gating_reasons_table_with_counts(self) -> None:
            """Guardrail: summary table should render when gating counts exist."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            repo_root = Path(__file__).resolve().parents[1]
            with isolate_telemetry_dir():
                summary_dir = repo_root / "artifacts" / "telemetry"
                summary_dir.mkdir(parents=True, exist_ok=True)
                summary_path = summary_dir / "history-validation-summary.json"
                streaming_summary_path = (
                    summary_dir / "history-validation-summary.streaming.json"
                )

                summary_data = {
                    "total_entries": 5,
                    "gating_drop_counts": {
                        "streaming_disabled": 2,
                        "rate_limited": 1,
                    },
                    "gating_drop_total": 3,
                    "gating_drop_last_message": "Streaming disabled guardrail",
                    "gating_drop_last_code": "streaming_disabled",
                    "streaming_gating_summary": {
                        "counts": {
                            "rate_limited": 1,
                            "streaming_disabled": 2,
                        },
                        "sources": {
                            "modelHelpCanvas": 2,
                            "providerCommands": 1,
                        },
                        "total": 3,
                        "last": {
                            "reason": "streaming_disabled",
                            "reason_count": 2,
                        },
                        "last_message": "Streaming disabled guardrail",
                        "last_code": "streaming_disabled",
                    },
                    "scheduler": {
                        "reschedule_count": 4,
                        "last_interval_minutes": 45,
                        "last_reason": "summary fallback",
                        "last_timestamp": "2025-12-23T01:10:00Z",
                    },
                }

                summary_path.write_text(
                    json.dumps(summary_data, indent=2), encoding="utf-8"
                )

                if streaming_summary_path.exists():
                    streaming_summary_path.unlink()
                telemetry_path = (
                    summary_dir / "history-validation-summary.telemetry.json"
                )
                if telemetry_path.exists():
                    telemetry_path.unlink()
                skip_path = summary_dir / "suggestion-skip-summary.json"
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
                streak_path = summary_dir / "cli-warning-streak.json"
                streak_state = {
                    "streak": 3,
                    "last_reason": "stale",
                    "last_command": "python3 scripts/tools/check-telemetry-export-marker.py --wait",
                    "updated_at": "2025-12-23T01:50:00Z",
                }
                streak_path.write_text(
                    json.dumps(streak_state, indent=2), encoding="utf-8"
                )

                summary_text = ""
                with tempfile.TemporaryDirectory() as tmpdir:
                    fake_make = Path(tmpdir) / "make"
                    fake_make.write_text(
                        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
                    )
                    fake_make.chmod(0o755)
                    step_summary_path = Path(tmpdir) / "gha-summary.md"
                    env = os.environ.copy()
                    env["ALLOW_STALE_TELEMETRY"] = "1"
                    env["PATH"] = f"{tmpdir}{os.pathsep}{env.get('PATH', '')}"
                    env["GITHUB_STEP_SUMMARY"] = str(step_summary_path)
                    env["SCHEDULER_STALE_THRESHOLD_MINUTES"] = "5"
                    env["SCHEDULER_STALE_NOW"] = "2025-12-23T01:55:00Z"
                    result = subprocess.run(
                        ["/bin/bash", str(script), "request-history-guardrails"],
                        check=False,
                        capture_output=True,
                        text=True,
                        cwd=str(repo_root),
                        env=env,
                    )
                    if result.returncode != 0:
                        self.fail(
                            "run_guardrails_ci.sh request-history-guardrails failed with code "
                            f"{result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                        )
                    self.assertTrue(
                        step_summary_path.exists(),
                        "run_guardrails_ci.sh did not append to the GitHub step summary file",
                    )
                    summary_text = step_summary_path.read_text(encoding="utf-8")

            stdout = result.stdout
            self.assertIn(
                "- suggestion skips total: 3",
                summary_text,
            )
            self.assertIn(
                "- suggestion skip reasons: streaming_disabled=2, rate_limited=1",
                summary_text,
            )
            self.assertIn("### Scheduler Telemetry", summary_text)
            self.assertIn("- Scheduler reschedules: 4", summary_text)
            self.assertIn(
                "- Scheduler last interval (minutes): 45",
                summary_text,
            )
            self.assertIn(
                "- Scheduler last reason: summary fallback",
                summary_text,
            )
            self.assertIn(
                "- Scheduler last timestamp: 2025-12-23T01:10:00Z",
                summary_text,
            )
            self.assertIn(
                "- Scheduler data source: summary (non-default, stale)",
                summary_text,
            )
            self.assertIn("### Telemetry Export Streak", summary_text)
            self.assertIn(
                "Telemetry export streak state:",
                summary_text,
            )
            self.assertIn(
                "- Telemetry export warning streak: 3",
                summary_text,
            )
            self.assertIn(
                "- Telemetry export last reason: stale",
                summary_text,
            )
            self.assertIn(
                "- Telemetry export last updated: 2025-12-23T01:50:00Z",
                summary_text,
            )
            self.assertIn(
                "- Telemetry export last command: python3 scripts/tools/check-telemetry-export-marker.py --wait",
                summary_text,
            )
            self.assertIn(
                "- Streak alert: 3 consecutive warnings (reason: stale)",
                summary_text,
            )
            self.assertIn(
                "- Scheduler data source: summary (non-default, stale)",
                stdout,
            )
            self.assertIn(
                "Telemetry export streak state:",
                stdout,
            )
            self.assertIn(
                "- Telemetry export warning streak: 3",
                stdout,
            )
            self.assertIn(
                "- Telemetry export last reason: stale",
                stdout,
            )
            self.assertIn(
                "- Telemetry export last updated: 2025-12-23T01:50:00Z",
                stdout,
            )
            self.assertIn(
                "- Telemetry export last command: python3 scripts/tools/check-telemetry-export-marker.py --wait",
                stdout,
            )
            self.assertIn(
                "- Streak alert: 3 consecutive warnings (reason: stale)",
                stdout,
            )
            self.assertIn(
                "WARNING: Scheduler telemetry uses summary (non-default, stale); refresh Talon exports.",
                summary_text,
            )
            self.assertIn(
                "WARNING: Scheduler telemetry uses summary (non-default, stale); refresh Talon exports.",
                stdout,
            )
            summary_lines = [
                line for line in summary_text.splitlines() if line.startswith("|")
            ]

            self.assertEqual(
                summary_lines[:3],
                [
                    "| Alert | Detail |",
                    "| --- | --- |",
                    "| Telemetry export streak | 3 consecutive warnings (reason: stale) |",
                ],
            )
            reason_header_idx = summary_lines.index("| Reason | Count |", 3)
            self.assertEqual(
                summary_lines[reason_header_idx : reason_header_idx + 3],
                [
                    "| Reason | Count |",
                    "| --- | --- |",
                    "| streaming_disabled | 2 |",
                ],
                "GitHub summary should list highest counts first",
            )
            self.assertIn("| rate_limited | 1 |", summary_text)
            source_header_idx = summary_lines.index(
                "| Source | Count |", reason_header_idx + 3
            )
            self.assertEqual(
                summary_lines[source_header_idx : source_header_idx + 3],
                [
                    "| Source | Count |",
                    "| --- | --- |",
                    "| modelHelpCanvas | 2 |",
                ],
            )
            self.assertIn("| providerCommands | 1 |", summary_text)
            self.assertNotIn("- Streaming gating reasons: none", summary_text)

        def test_run_guardrails_ci_warns_on_invalid_scheduler_timestamp(self) -> None:
            """Guardrail: warn when scheduler timestamp cannot be parsed."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            repo_root = Path(__file__).resolve().parents[1]
            with isolate_telemetry_dir():
                summary_dir = repo_root / "artifacts" / "telemetry"
                summary_dir.mkdir(parents=True, exist_ok=True)
                summary_path = summary_dir / "history-validation-summary.json"
                streaming_summary_path = (
                    summary_dir / "history-validation-summary.streaming.json"
                )

                summary_data = {
                    "total_entries": 1,
                    "gating_drop_counts": {},
                    "gating_drop_total": 0,
                    "streaming_gating_summary": {
                        "counts": {},
                        "sources": {},
                        "total": 0,
                        "last": {},
                        "last_message": "",
                        "last_code": "",
                    },
                    "scheduler": {
                        "reschedule_count": 2,
                        "last_interval_minutes": 30,
                        "last_reason": "summary fallback",
                        "last_timestamp": "invalid-timestamp",
                    },
                }

                summary_path.write_text(
                    json.dumps(summary_data, indent=2), encoding="utf-8"
                )

                if streaming_summary_path.exists():
                    streaming_summary_path.unlink()
                telemetry_path = (
                    summary_dir / "history-validation-summary.telemetry.json"
                )
                if telemetry_path.exists():
                    telemetry_path.unlink()
                skip_path = summary_dir / "suggestion-skip-summary.json"
                skip_payload_seed = {
                    "counts": {},
                    "total_skipped": 0,
                    "reason_counts": [],
                }
                skip_path.write_text(
                    json.dumps(skip_payload_seed, indent=2), encoding="utf-8"
                )

                summary_text = ""
                with tempfile.TemporaryDirectory() as tmpdir:
                    fake_make = Path(tmpdir) / "make"
                    fake_make.write_text(
                        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
                    )
                    fake_make.chmod(0o755)
                    step_summary_path = Path(tmpdir) / "gha-summary.md"
                    env = os.environ.copy()
                    env["ALLOW_STALE_TELEMETRY"] = "1"
                    env["PATH"] = f"{tmpdir}{os.pathsep}{env.get('PATH', '')}"
                    env["GITHUB_STEP_SUMMARY"] = str(step_summary_path)
                    result = subprocess.run(
                        ["/bin/bash", str(script), "request-history-guardrails"],
                        check=False,
                        capture_output=True,
                        text=True,
                        cwd=str(repo_root),
                        env=env,
                    )
                    if result.returncode != 0:
                        self.fail(
                            "run_guardrails_ci.sh request-history-guardrails failed with code "
                            f"{result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                        )
                    self.assertTrue(
                        step_summary_path.exists(),
                        "run_guardrails_ci.sh did not append to the GitHub step summary file",
                    )
                    summary_text = step_summary_path.read_text(encoding="utf-8")

                stdout = result.stdout
                self.assertIn(
                    "- Scheduler last timestamp: invalid-timestamp",
                    summary_text,
                )
                self.assertIn(
                    "- Scheduler data source: summary (non-default, invalid-timestamp)",
                    summary_text,
                )
                self.assertIn(
                    "- Scheduler data source: summary (non-default, invalid-timestamp)",
                    stdout,
                )
                self.assertIn(
                    "WARNING: Scheduler telemetry uses summary (non-default, invalid-timestamp); refresh Talon exports.",
                    summary_text,
                )
                self.assertIn(
                    "WARNING: Scheduler telemetry uses summary (non-default, invalid-timestamp); refresh Talon exports.",
                    stdout,
                )
                self.assertIn(
                    "WARNING: Scheduler telemetry timestamp 'invalid-timestamp' could not be parsed; refresh Talon exports.",
                    summary_text,
                )
                self.assertIn(
                    "WARNING: Scheduler telemetry timestamp 'invalid-timestamp' could not be parsed; refresh Talon exports.",
                    stdout,
                )

        def test_run_guardrails_ci_invalid_target(self) -> None:
            """Guardrail: CI helper should fail clearly on invalid targets."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            result = subprocess.run(
                ["/bin/bash", str(script), "nonexistent-target"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            self.assertNotEqual(result.returncode, 0, "Expected invalid target to fail")
            self.assertIn(
                "Running guardrails target: nonexistent-target", result.stdout
            )
            # Make consistently reports missing targets; assert a hint is present.
            self.assertTrue(
                "No rule" in result.stderr or "unknown target" in result.stderr.lower(),
                f"Expected make to report missing target; stderr was:\n{result.stderr}",
            )

else:

    class RunGuardrailsCITests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
