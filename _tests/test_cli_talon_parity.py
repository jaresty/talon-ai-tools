import unittest
from pathlib import Path
import json
import subprocess

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

CLI_BINARY = Path("bin/bar")
SCHEMA_BUNDLE = Path("docs/schema/command-surface.json")


if bootstrap is None:

    class CLITalonParityPlaceholder(unittest.TestCase):
        @unittest.skip("Talon runtime cannot execute CLI parity harness")
        def test_skip_in_talon_runtime(self) -> None:  # pragma: no cover - Talon skip
            pass

else:

    class CLITalonParityTests(unittest.TestCase):
        def test_cli_health_probe_emits_json_status(self) -> None:
            self.assertTrue(
                CLI_BINARY.exists(),
                "CLI binary missing; run loop-0005 to restore bar stub",
            )

            result = subprocess.run(
                [str(CLI_BINARY), "--health"],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertIn("version", payload)
            self.assertEqual(
                payload.get("runtime"),
                "go",
                "CLI runtime must report Go binary; stubbed implementation detected",
            )
            self.assertEqual(
                payload.get("executor"),
                "compiled",
                "CLI must run compiled binary rather than go run stub",
            )

        def test_schema_bundle_contains_version_marker(self) -> None:
            self.assertTrue(
                SCHEMA_BUNDLE.exists(),
                "Schema bundle missing; run loop-0006 to restore",
            )

            payload = json.loads(SCHEMA_BUNDLE.read_text(encoding="utf-8"))
            self.assertIn("version", payload)
            self.assertIn("commands", payload)
