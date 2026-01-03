"""Package the Go CLI binary and write checksum manifests.

This helper builds the Go CLI under `cmd/bar`, copies the binary to
`bin/bar.bin`, and packages a tarball plus SHA-256 manifest in
`artifacts/cli/`. The tarball includes the compiled binary and the shared
command-surface schema so Talon can install both in a single step.

The packaging step also records a SHA-256 digest for the delegation state
snapshot used by release guardrails, ensuring signature enforcement can detect
stale or tampered delegation telemetry.
"""

from __future__ import annotations

import argparse
import json
import hashlib
import os
import platform
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BIN_DIR = REPO_ROOT / "bin"
SCHEMA_PATH = REPO_ROOT / "docs" / "schema" / "command-surface.json"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "cli"
DELEGATION_STATE_SNAPSHOT_PATH = ARTIFACTS_DIR / "delegation-state.json"
DEFAULT_SIGNATURE_KEY = "adr-0063-cli-release-signature"
SIGNATURE_KEY_ENV = "CLI_RELEASE_SIGNING_KEY"


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


def _build_binary(temp_dir: Path) -> Path:
    output_path = temp_dir / "bar"
    subprocess.run(
        ["go", "build", "-o", str(output_path), "./cmd/bar"],
        cwd=REPO_ROOT,
        check=True,
    )
    return output_path


def _copy_local_binary(built_binary: Path) -> Path:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    bin_path = BIN_DIR / "bar.bin"
    shutil.copy2(built_binary, bin_path)
    bin_path.chmod(0o755)
    return bin_path


def _create_tarball(built_binary: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    tarball_path = output_dir / f"{_target_suffix()}.tar.gz"
    with tarfile.open(tarball_path, "w:gz") as tar:
        tar.add(built_binary, arcname="bar")
        if SCHEMA_PATH.exists():
            tar.add(SCHEMA_PATH, arcname="command-surface.json")
    return tarball_path


def _signing_key() -> str:
    return os.environ.get(SIGNATURE_KEY_ENV, DEFAULT_SIGNATURE_KEY)


def _signature_for(message: str) -> str:
    return hashlib.sha256((_signing_key() + "\n" + message).encode("utf-8")).hexdigest()


def _write_signature(target: Path, message: str) -> Path:
    target.write_text(f"{_signature_for(message)}\n", encoding="utf-8")
    return target


def _write_manifest(tarball: Path) -> Path:
    digest = hashlib.sha256(tarball.read_bytes()).hexdigest()
    manifest_path = tarball.with_name(f"{tarball.name}.sha256")
    recorded = f"{digest}  {tarball.name}"
    manifest_path.write_text(f"{recorded}\n", encoding="utf-8")
    _write_signature(manifest_path.with_suffix(manifest_path.suffix + ".sig"), recorded)
    return manifest_path


def _canonical_state_digest(payload: dict) -> str:
    canonical = dict(payload)
    canonical["updated_at"] = None
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _write_delegation_state_manifest(output_dir: Path) -> Path:
    if not DELEGATION_STATE_SNAPSHOT_PATH.exists():
        raise FileNotFoundError(
            f"delegation state snapshot missing: {DELEGATION_STATE_SNAPSHOT_PATH}"
        )
    snapshot_payload = json.loads(
        DELEGATION_STATE_SNAPSHOT_PATH.read_text(encoding="utf-8")
    )
    if not isinstance(snapshot_payload, dict):
        raise ValueError(
            f"delegation state snapshot must be an object: {DELEGATION_STATE_SNAPSHOT_PATH}"
        )
    digest = _canonical_state_digest(snapshot_payload)
    manifest_path = output_dir / "delegation-state.json.sha256"
    recorded = f"{digest}  {DELEGATION_STATE_SNAPSHOT_PATH.name}"
    manifest_path.write_text(f"{recorded}\n", encoding="utf-8")
    _write_signature(manifest_path.with_suffix(manifest_path.suffix + ".sig"), recorded)
    return manifest_path


def package_cli() -> tuple[Path, Path]:
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        built = _build_binary(temp_dir)
        _copy_local_binary(built)
        tarball = _create_tarball(built, ARTIFACTS_DIR)
        manifest = _write_manifest(tarball)
        _write_delegation_state_manifest(ARTIFACTS_DIR)
    return tarball, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--print-paths",
        action="store_true",
        help="Print the packaged tarball and manifest paths",
    )
    args = parser.parse_args()

    tarball, manifest = package_cli()

    if args.print_paths:
        print(tarball)
        print(manifest)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
