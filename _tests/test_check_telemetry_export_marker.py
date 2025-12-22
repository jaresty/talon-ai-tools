import json
import os
import subprocess
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class CheckTelemetryExportMarkerTests(unittest.TestCase):
        def _run_helper(
            self, marker_path: Path, *extra_args: str
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
            return subprocess.run(
                command,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )

        def test_auto_export_populates_missing_marker(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                result = self._run_helper(marker)
                if result.returncode != 0:
                    self.fail(
                        "helper should auto-export missing marker\n"
                        f"exit={result.returncode}\nstdout=\n{result.stdout}\nstderr=\n{result.stderr}"
                    )
                self.assertTrue(marker.exists(), "auto-export did not create marker")
                payload = json.loads(marker.read_text(encoding="utf-8"))
                self.assertIn("exported_at", payload)

        def test_auto_export_refreshes_stale_marker(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                marker.parent.mkdir(parents=True, exist_ok=True)
                stale_time = datetime.now(timezone.utc) - timedelta(hours=2)
                marker.write_text(
                    json.dumps({"exported_at": stale_time.isoformat()}),
                    encoding="utf-8",
                )
                result = self._run_helper(marker)
                if result.returncode != 0:
                    self.fail(
                        "helper should refresh stale marker\n"
                        f"exit={result.returncode}\nstdout=\n{result.stdout}\nstderr=\n{result.stderr}"
                    )
                payload = json.loads(marker.read_text(encoding="utf-8"))
                refreshed_at = datetime.fromisoformat(payload["exported_at"])
                self.assertGreater(refreshed_at, stale_time)

        def test_disabled_auto_export_fails_when_marker_missing(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                result = self._run_helper(marker, "--no-auto-export")
                self.assertEqual(result.returncode, 2)
                self.assertIn("model export telemetry", result.stderr)
                self.assertIn("TIP:", result.stderr)

        def test_disabled_auto_export_reports_tip_for_stale_marker(self) -> None:
            with TemporaryDirectory() as tmpdir:
                marker = Path(tmpdir) / "talon-export-marker.json"
                marker.parent.mkdir(parents=True, exist_ok=True)
                stale_time = datetime.now(timezone.utc) - timedelta(hours=3)
                marker.write_text(
                    json.dumps({"exported_at": stale_time.isoformat()}),
                    encoding="utf-8",
                )
                result = self._run_helper(marker, "--no-auto-export")
                self.assertEqual(result.returncode, 2)
                self.assertIn("stale", result.stderr)
                self.assertIn("TIP:", result.stderr)
