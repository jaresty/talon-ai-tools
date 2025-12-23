import json
import os
import subprocess
import sys
import threading
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class CheckTelemetryExportMarkerTests(unittest.TestCase):
        def _run_helper(
            self,
            marker_path: Path,
            *extra_args: str,
            env_overrides: dict[str, str] | None = None,
        ) -> subprocess.CompletedProcess[str]:
            repo_root = Path(__file__).resolve().parents[1]
            command = [
                sys.executable,
                "scripts/tools/check-telemetry-export-marker.py",
                "--marker",
                str(marker_path),
                "--max-age-minutes",
                "1",
            ]
            command.extend(extra_args)
            env = os.environ.copy()
            pythonpath_entries = [
                str(repo_root / "_tests" / "stubs"),
                str(repo_root),
            ]
            original_pythonpath = env.get("PYTHONPATH", "")
            if original_pythonpath:
                pythonpath_entries.append(original_pythonpath)
            env["PYTHONPATH"] = os.pathsep.join(pythonpath_entries)
            env.setdefault("ALLOW_STALE_TELEMETRY", "")
            if env_overrides:
                env.update(env_overrides)
            return subprocess.run(
                command,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )

        def test_missing_marker_fails_with_instruction(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                result = self._run_helper(marker)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Telemetry export marker missing", result.stderr)
                self.assertIn("model export telemetry", result.stderr)
                self.assertIn("TIP:", result.stderr)

        def test_invalid_marker_prompts_refresh(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.write_text("not json", encoding="utf-8")
                result = self._run_helper(marker)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Unable to parse telemetry export marker", result.stderr)
                self.assertIn("TIP:", result.stderr)

        def test_stale_marker_fails(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                marker.parent.mkdir(parents=True, exist_ok=True)
                stale_time = datetime.now(timezone.utc) - timedelta(hours=3)
                marker.write_text(
                    json.dumps({"exported_at": stale_time.isoformat()}),
                    encoding="utf-8",
                )
                result = self._run_helper(marker)
                self.assertEqual(result.returncode, 2)
                self.assertIn("Telemetry export marker is stale", result.stderr)
                self.assertIn("model export telemetry", result.stderr)

        def test_fresh_marker_passes(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                marker.parent.mkdir(parents=True, exist_ok=True)
                marker.write_text(
                    json.dumps({"exported_at": datetime.now(timezone.utc).isoformat()}),
                    encoding="utf-8",
                )
                result = self._run_helper(marker)
                if result.returncode != 0:
                    self.fail(
                        "helper should succeed when marker is fresh\n"
                        f"exit={result.returncode}\nstdout=\n{result.stdout}\nstderr=\n{result.stderr}"
                    )

        def test_wait_allows_marker_refresh(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"

                def writer() -> None:
                    time.sleep(0.5)
                    marker.write_text(
                        json.dumps(
                            {"exported_at": datetime.now(timezone.utc).isoformat()}
                        ),
                        encoding="utf-8",
                    )

                thread = threading.Thread(target=writer, daemon=True)
                thread.start()
                start = time.time()
                result = self._run_helper(
                    marker,
                    "--wait",
                    "--wait-seconds",
                    "5",
                )
                thread.join(timeout=1)
                duration = time.time() - start
                if result.returncode != 0:
                    self.fail(
                        "helper should succeed after wait\n"
                        f"exit={result.returncode}\nstdout=\n{result.stdout}\nstderr=\n{result.stderr}"
                    )
                self.assertLess(duration, 5.0)
                self.assertTrue(marker.exists())
                payload = json.loads(marker.read_text(encoding="utf-8"))
                self.assertIn("exported_at", payload)
                self.assertIn("Waiting for telemetry export marker", result.stderr)

        def test_wait_times_out_without_refresh(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                result = self._run_helper(
                    marker,
                    "--wait",
                    "--wait-seconds",
                    "1",
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("Waiting for telemetry export marker", result.stderr)
                self.assertIn("model export telemetry", result.stderr)

        def test_allow_env_warns_and_exits_zero(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                result = self._run_helper(
                    marker,
                    env_overrides={"ALLOW_STALE_TELEMETRY": "1"},
                )
                self.assertEqual(result.returncode, 0)
                self.assertIn("ALLOW_STALE_TELEMETRY is set", result.stderr)
                self.assertIn(
                    "skipping telemetry export freshness check", result.stderr
                )
                self.assertIn(str(marker), result.stderr)
