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
                self.assertIn("Telemetry scheduler stats:", result.stdout)
                self.assertIn("- Scheduler reschedules: 0", result.stdout)
                self.assertIn(
                    "- Scheduler last interval (minutes): none",
                    result.stdout,
                )
                self.assertIn("- Scheduler last reason: none", result.stdout)
                self.assertIn("- Scheduler last timestamp: none", result.stdout)
                self.assertIn("- Scheduler data source: defaults", result.stdout)

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
            self.assertIn("- Scheduler data source: defaults", summary_text)

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

                self.assertIn(
                    "- suggestion skips total: 3",
                    summary_text,
                )
                self.assertIn(
                    "- suggestion skip reasons: streaming_disabled=2, rate_limited=1",
                    summary_text,
                )
                stdout = result.stdout
                self.assertIn("History summary gating status: unknown", stdout)
                self.assertIn(
                    "History summary last drop: Streaming disabled guardrail",
                    stdout,
                )
                self.assertIn(
                    "Streaming gating last drop: Streaming disabled guardrail (code=streaming_disabled)",
                    stdout,
                )
                self.assertIn("Suggestion skip total: 3", stdout)
                self.assertIn(
                    "Suggestion skip reasons: streaming_disabled=2, rate_limited=1",
                    stdout,
                )

                self.assertIn("Streaming gating reasons:", stdout)
                self.assertIn("| Reason | Count |", stdout)
                self.assertIn("Streaming gating sources:", stdout)
                self.assertIn("| Source | Count |", stdout)

                self.assertIn(
                    "Streaming gating summary: status=unknown; total=3; counts=streaming_disabled=2, rate_limited=1; sources=modelHelpCanvas=2, providerCommands=1; last=streaming_disabled (count=2); last_source=n/a; last_message=Streaming disabled guardrail (code=streaming_disabled)",
                    stdout,
                )

                table_lines = [
                    line for line in stdout.splitlines() if line.startswith("|")
                ]
                self.assertEqual(
                    table_lines[:3],
                    [
                        "| Reason | Count |",
                        "| --- | --- |",
                        "| streaming_disabled | 2 |",
                    ],
                    "Expected gating table to list highest counts first",
                )
                self.assertIn("| rate_limited | 1 |", stdout)
                self.assertIn("| modelHelpCanvas | 2 |", stdout)
                self.assertIn("| providerCommands | 1 |", stdout)

                self.assertIn("- streaming status: unknown", summary_text)
                self.assertIn(
                    "- last drop: Streaming disabled guardrail",
                    summary_text,
                )
                self.assertIn(
                    "- streaming last drop: Streaming disabled guardrail (code=streaming_disabled)",
                    summary_text,
                )
                self.assertIn("Streaming gating reasons:", summary_text)
                self.assertIn("| Reason | Count |", summary_text)
                self.assertIn("Streaming gating sources:", summary_text)
                self.assertIn("| Source | Count |", summary_text)
                self.assertIn(
                    "Streaming gating summary: status=unknown; total=3; counts=streaming_disabled=2, rate_limited=1; sources=modelHelpCanvas=2, providerCommands=1; last=streaming_disabled (count=2); last_source=n/a; last_message=Streaming disabled guardrail (code=streaming_disabled)",
                    summary_text,
                )
                telemetry_payload = json.loads(
                    summary_path.with_name(
                        "history-validation-summary.telemetry.json"
                    ).read_text(encoding="utf-8")
                )
                self.assertEqual(
                    telemetry_payload.get("last_drop_message"),
                    "Streaming disabled guardrail",
                )
                self.assertEqual(
                    telemetry_payload.get("last_drop_code"), "streaming_disabled"
                )
                self.assertEqual(
                    telemetry_payload.get("scheduler"),
                    {
                        "reschedule_count": 0,
                        "last_interval_minutes": None,
                        "last_reason": "",
                        "last_timestamp": "",
                    },
                )
                self.assertIn(
                    '"last_drop_message": "Streaming disabled guardrail"',
                    summary_text,
                )
                self.assertIn("- Scheduler reschedules: 0", summary_text)
                self.assertIn(
                    "- Scheduler last interval (minutes): none",
                    summary_text,
                )
                self.assertIn("- Scheduler last reason: none", summary_text)
                self.assertIn("- Scheduler last timestamp: none", summary_text)
                self.assertIn("- Scheduler data source: defaults", summary_text)
                summary_lines = [
                    line for line in summary_text.splitlines() if line.startswith("|")
                ]
                self.assertEqual(
                    summary_lines[:3],
                    [
                        "| Reason | Count |",
                        "| --- | --- |",
                        "| streaming_disabled | 2 |",
                    ],
                    "GitHub summary should list highest counts first",
                )
                self.assertIn("| rate_limited | 1 |", summary_text)
                self.assertIn("| modelHelpCanvas | 2 |", summary_text)
                self.assertIn("| providerCommands | 1 |", summary_text)
                self.assertNotIn("- Streaming gating reasons: none", summary_text)

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
