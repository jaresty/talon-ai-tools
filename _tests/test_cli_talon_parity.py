import unittest
from pathlib import Path
import json
import platform
import subprocess

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

CLI_BINARY = Path("bin/bar")
SCHEMA_BUNDLE = Path("docs/schema/command-surface.json")
PACKAGED_CLI_DIR = Path("artifacts/cli")


def _target_suffix() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    arch = arch_map.get(machine, machine)
    return f"bar-{system}-{arch}"


def _packaged_cli_tarball() -> Path:
    return PACKAGED_CLI_DIR / f"{_target_suffix()}.tar.gz"


def _packaged_cli_manifest(tarball: Path) -> Path:
    return tarball.with_name(f"{tarball.name}.sha256")


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
            self.assertEqual(
                payload.get("binary_path"),
                "bin/bar.bin",
                "CLI must report compiled binary path relative to repo root",
            )

        def test_schema_bundle_contains_version_marker(self) -> None:
            self.assertTrue(
                SCHEMA_BUNDLE.exists(),
                "Schema bundle missing; run loop-0006 to restore",
            )

            payload = json.loads(SCHEMA_BUNDLE.read_text(encoding="utf-8"))
            self.assertIn("version", payload)
            self.assertIn("commands", payload)

        def test_packaged_cli_assets_present(self) -> None:
            tarball = _packaged_cli_tarball()
            manifest = _packaged_cli_manifest(tarball)

            missing = [str(path) for path in (tarball, manifest) if not path.exists()]
            if missing:
                self.fail(
                    "Packaged CLI artefacts missing; run "
                    "`python3 scripts/tools/package_bar_cli.py --print-paths` to rebuild. "
                    f"Missing: {', '.join(missing)}"
                )
