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
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BIN_DIR = REPO_ROOT / "bin"
SCHEMA_PATH = REPO_ROOT / "docs" / "schema" / "command-surface.json"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "cli"
DELEGATION_STATE_SNAPSHOT_PATH = ARTIFACTS_DIR / "delegation-state.json"
DEFAULT_SIGNATURE_METADATA_PATH = ARTIFACTS_DIR / "signatures.json"
DEFAULT_SIGNATURE_KEY = "adr-0063-cli-release-signature"
SIGNATURE_KEY_ENV = "CLI_RELEASE_SIGNING_KEY"
DEFAULT_SIGNING_KEY_ID = "local-dev"
SIGNING_KEY_ID_ENV = "CLI_RELEASE_SIGNING_KEY_ID"
SIGNATURE_METADATA_ENV = "CLI_SIGNATURE_METADATA"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from talon import settings as talon_settings  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - Talon settings unavailable outside runtime
    talon_settings = None

try:
    from lib.requestLog import drop_reason_message as _drop_reason_message
except Exception:  # pragma: no cover - defensive import for packaging env
    _drop_reason_message = None

PREFERRED_GO_PATHS = [
    Path("/opt/homebrew/bin/go"),
    Path("/usr/local/bin/go"),
    Path("/usr/local/go/bin/go"),
    Path("/usr/bin/go"),
]


def _settings_value(name: str) -> str | None:
    if talon_settings is None:
        return None
    try:
        value = talon_settings.get(name)
    except Exception:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return None


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
    go_command = _go_command()
    subprocess.run(
        go_command + ["build", "-o", str(output_path), "./cmd/bar"],
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


def _signing_key_id() -> str:
    return os.environ.get(SIGNING_KEY_ID_ENV, DEFAULT_SIGNING_KEY_ID)


def _metadata_path() -> Path:
    return Path(
        os.environ.get(
            SIGNATURE_METADATA_ENV,
            str(DEFAULT_SIGNATURE_METADATA_PATH),
        )
    )


def _go_command() -> list[str]:
    override = os.environ.get("CLI_GO_COMMAND")
    if not override:
        setting_override = _settings_value("user.cli_go_command")
        if setting_override:
            override = setting_override
    if override:
        return shlex.split(str(override))
    discovered = shutil.which("go")
    if discovered:
        return [discovered]
    for candidate in PREFERRED_GO_PATHS:
        if candidate.exists():
            return [str(candidate)]
    raise FileNotFoundError("go")


def _signature_for(message: str) -> str:
    return hashlib.sha256((_signing_key() + "\n" + message).encode("utf-8")).hexdigest()


def _write_signature(target: Path, message: str) -> str:
    signature = _signature_for(message)
    target.write_text(f"{signature}\n", encoding="utf-8")
    return signature


def _write_manifest(tarball: Path) -> tuple[Path, str, str]:
    digest = hashlib.sha256(tarball.read_bytes()).hexdigest()
    manifest_path = tarball.with_name(f"{tarball.name}.sha256")
    recorded = f"{digest}  {tarball.name}"
    manifest_path.write_text(f"{recorded}\n", encoding="utf-8")
    signature = _write_signature(
        manifest_path.with_suffix(manifest_path.suffix + ".sig"), recorded
    )
    return manifest_path, recorded, signature


def _canonical_state_digest(payload: dict) -> str:
    canonical = dict(payload)
    canonical["updated_at"] = None
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _render_recovery_prompt(code: str, details: str) -> str:
    message = ""
    if code and _drop_reason_message is not None:
        try:
            message = _drop_reason_message(code)  # type: ignore[arg-type]
        except Exception:
            message = ""
    if not isinstance(message, str) or not message.strip():
        message = "CLI delegation ready."
    details_text = details.strip()
    if details_text and code in {"cli_recovered", "cli_signature_recovered"}:
        message = f"{message} (previous: {details_text})"
    return message


def _recovery_snapshot_from_payload(payload: dict) -> dict:
    snapshot: dict[str, object] = {"enabled": bool(payload.get("enabled"))}
    code = str(payload.get("recovery_code") or "").strip()
    details = str(payload.get("recovery_details") or "").strip()
    if code:
        snapshot["code"] = code
    if details:
        snapshot["details"] = details
    effective_code = code or "cli_ready"
    snapshot["prompt"] = _render_recovery_prompt(effective_code, details)
    return snapshot


def _write_delegation_state_manifest(output_dir: Path) -> tuple[Path, str, str, dict]:
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
    signature = _write_signature(
        manifest_path.with_suffix(manifest_path.suffix + ".sig"), recorded
    )
    return manifest_path, recorded, signature, snapshot_payload


def _write_signature_metadata(
    tarball_recorded: str,
    tarball_signature: str,
    snapshot_recorded: str,
    snapshot_signature: str,
    snapshot_payload: dict,
) -> Path:
    metadata = {
        "signing_key_id": _signing_key_id(),
        "tarball_manifest": {
            "recorded": tarball_recorded,
            "signature": tarball_signature,
        },
        "delegation_snapshot": {
            "recorded": snapshot_recorded,
            "signature": snapshot_signature,
        },
        "cli_recovery_snapshot": _recovery_snapshot_from_payload(snapshot_payload),
    }
    metadata_path = _metadata_path()
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata_path


def package_cli() -> tuple[Path, Path, Path]:
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        built = _build_binary(temp_dir)
        _copy_local_binary(built)
        tarball = _create_tarball(built, ARTIFACTS_DIR)
        (
            manifest_path,
            manifest_recorded,
            manifest_signature,
        ) = _write_manifest(tarball)
        (
            _,
            snapshot_recorded,
            snapshot_signature,
            snapshot_payload,
        ) = _write_delegation_state_manifest(ARTIFACTS_DIR)
        metadata_path = _write_signature_metadata(
            manifest_recorded,
            manifest_signature,
            snapshot_recorded,
            snapshot_signature,
            snapshot_payload,
        )
    return tarball, manifest_path, metadata_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--print-paths",
        action="store_true",
        help="Print the packaged tarball, manifest, and signature metadata paths",
    )
    args = parser.parse_args()

    tarball, manifest, metadata = package_cli()

    if args.print_paths:
        print(tarball)
        print(manifest)
        print(metadata)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
