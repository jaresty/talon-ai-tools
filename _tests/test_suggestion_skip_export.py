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
except ModuleNotFoundError:  # pragma: no cover - Talon runtime fallback
    bootstrap = None
else:  # pragma: no cover - import side-effects only
    bootstrap()


if bootstrap is not None and not TYPE_CHECKING:

    class SuggestionSkipExportTests(unittest.TestCase):
        def test_exports_counts_to_output_file(self) -> None:
            counts = {
                "missing_directional": 2,
                "unknown_persona": 1,
                "unknown_intent": 0,
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = tempfile.NamedTemporaryFile(dir=tmpdir, delete=False)
                output_path.close()

                metadata_path = Path(tmpdir) / "signatures.json"
                metadata_payload = {
                    "cli_recovery_snapshot": {
                        "enabled": True,
                        "code": "cli_ready",
                        "details": "release metadata verified",
                        "prompt": "Ready to delegate.",
                    }
                }
                metadata_path.write_text(json.dumps(metadata_payload), encoding="utf-8")
                env = os.environ.copy()
                env["CLI_SIGNATURE_METADATA"] = str(metadata_path)

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/suggestion-skip-export.py",
                        "--counts",
                        json.dumps(counts),
                        "--output",
                        output_path.name,
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=env,
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"export failed: {result.stdout}\n{result.stderr}",
                )
                payload = json.loads(Path(output_path.name).read_text(encoding="utf-8"))
                self.assertEqual(payload.get("total_skipped"), 3)
                self.assertEqual(
                    payload.get("reason_counts"),
                    [
                        {"reason": "missing_directional", "count": 2},
                        {"reason": "unknown_persona", "count": 1},
                    ],
                )
                self.assertEqual(
                    payload.get("counts"),
                    {
                        "missing_directional": 2,
                        "unknown_persona": 1,
                        "unknown_intent": 0,
                    },
                )
                self.assertEqual(
                    payload.get("cli_recovery_snapshot"),
                    {
                        "enabled": True,
                        "code": "cli_ready",
                        "details": "release metadata verified",
                        "prompt": "Ready to delegate.",
                    },
                )

        def test_stdout_mode_returns_json_payload(self) -> None:
            with tempfile.TemporaryDirectory() as tmpdir:
                metadata_path = Path(tmpdir) / "signatures.json"
                metadata_payload = {
                    "cli_recovery_snapshot": {
                        "enabled": False,
                        "code": "cli_ready",
                        "details": "",
                        "prompt": "Recovery prompt from metadata.",
                    }
                }
                metadata_path.write_text(json.dumps(metadata_payload), encoding="utf-8")
                env = os.environ.copy()
                env["CLI_SIGNATURE_METADATA"] = str(metadata_path)

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/suggestion-skip-export.py",
                        "--counts",
                        json.dumps({}),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=env,
                )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload.get("total_skipped"), 0)
            self.assertEqual(payload.get("reason_counts"), [])
            self.assertEqual(payload.get("counts"), {})
            self.assertEqual(
                payload.get("cli_recovery_snapshot"),
                {
                    "enabled": False,
                    "code": "cli_ready",
                    "prompt": "Recovery prompt from metadata.",
                },
            )

else:
    if not TYPE_CHECKING:

        class SuggestionSkipExportTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
