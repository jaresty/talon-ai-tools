"""Install the bar CLI binary from the packaged tarball.

The installer verifies the SHA-256 checksum recorded in the manifest,
extracts the `bar` binary into `bin/bar.bin`, and keeps permissions aligned
for Talon delegation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BIN_DIR = REPO_ROOT / "bin"
TARGET_PATH = BIN_DIR / "bar.bin"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "cli"
SNAPSHOT_PATH = ARTIFACTS_DIR / "delegation-state.json"
SNAPSHOT_DIGEST_PATH = ARTIFACTS_DIR / "delegation-state.json.sha256"
DELEGATION_STATE_SIGNATURE_ENV = "CLI_DELEGATION_STATE_SIGNATURE"
DEFAULT_SIGNATURE_KEY = "adr-0063-cli-release-signature"
SIGNATURE_KEY_ENV = "CLI_RELEASE_SIGNING_KEY"
SIGNATURE_METADATA_ENV = "CLI_SIGNATURE_METADATA"
SIGNATURE_METADATA_PATH = Path(
    os.environ.get(SIGNATURE_METADATA_ENV, "artifacts/cli/signatures.json")
)
DEFAULT_SIGNING_KEY_ID = "local-dev"
SIGNING_KEY_ID_ENV = "CLI_RELEASE_SIGNING_KEY_ID"
SIGNATURE_TELEMETRY_ENV = "CLI_SIGNATURE_TELEMETRY"
SIGNATURE_TELEMETRY_PATH = Path(
    os.environ.get(
        SIGNATURE_TELEMETRY_ENV,
        "var/cli-telemetry/signature-metadata.json",
    )
)
RUNTIME_DIR = REPO_ROOT / "var" / "cli-telemetry"
RUNTIME_STATE_PATH = RUNTIME_DIR / "delegation-state.json"


class ReleaseSignatureError(RuntimeError):
    """Raised when release artefact signature validation fails."""


__all__ = ["install_cli", "ReleaseSignatureError"]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:  # Ensure Talon stubs resolve when running outside tests.
    from _tests import bootstrap as _tests_bootstrap  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    _tests_bootstrap = None
else:  # pragma: no cover - bootstrap only mutates sys.path
    try:
        _tests_bootstrap.bootstrap()
    except Exception:
        pass


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


def _tarball_path() -> Path:
    return ARTIFACTS_DIR / f"{_target_suffix()}.tar.gz"


def _manifest_path(tarball: Path) -> Path:
    return tarball.with_name(f"{tarball.name}.sha256")


def _read_manifest(manifest: Path) -> tuple[str, str]:
    contents = manifest.read_text(encoding="utf-8").strip()
    if not contents:
        raise RuntimeError(f"manifest empty: {manifest}")
    digest, _, filename = contents.partition("  ")
    digest = digest.strip()
    filename = filename.strip()
    if len(digest) != 64:
        raise RuntimeError(f"manifest digest invalid: {manifest}")
    return digest, filename or ""


def _verify_checksum(tarball: Path, manifest: Path) -> None:
    digest, filename = _read_manifest(manifest)
    if filename and filename != tarball.name:
        raise RuntimeError(
            f"manifest filename mismatch: expected {tarball.name}, got {filename}"
        )
    computed = hashlib.sha256(tarball.read_bytes()).hexdigest()
    if computed != digest:
        raise RuntimeError(
            f"checksum mismatch for {tarball}: expected {digest}, got {computed}"
        )


def _signing_key() -> str:
    return os.environ.get(SIGNATURE_KEY_ENV, DEFAULT_SIGNATURE_KEY)


def _signing_key_id() -> str:
    return os.environ.get(SIGNING_KEY_ID_ENV, DEFAULT_SIGNING_KEY_ID)


def _metadata_path() -> Path:
    return Path(os.environ.get(SIGNATURE_METADATA_ENV, str(SIGNATURE_METADATA_PATH)))


def _signature_for(message: str) -> str:
    return hashlib.sha256((_signing_key() + "\n" + message).encode("utf-8")).hexdigest()


def _verify_signature_file(path: Path, recorded: str, label: str) -> str:
    if not path.exists():
        raise ReleaseSignatureError(f"missing {label} signature: {path}")
    signature = path.read_text(encoding="utf-8").strip()
    expected_signature = _signature_for(recorded)
    if signature != expected_signature:
        raise ReleaseSignatureError(
            f"{label} signature mismatch: expected {expected_signature}, got {signature}"
        )
    return signature


def _canonical_state_digest(payload: dict) -> str:
    canonical = dict(payload)
    canonical["updated_at"] = None
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _load_snapshot_payload() -> dict:
    if not SNAPSHOT_PATH.exists():
        raise ReleaseSignatureError(f"missing delegation snapshot: {SNAPSHOT_PATH}")
    payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ReleaseSignatureError(
            f"delegation snapshot invalid (expected object): {SNAPSHOT_PATH}"
        )
    return payload


def _snapshot_signature_path() -> Path:
    env_override = os.environ.get(DELEGATION_STATE_SIGNATURE_ENV)
    if env_override:
        return Path(env_override)
    return SNAPSHOT_DIGEST_PATH.with_suffix(SNAPSHOT_DIGEST_PATH.suffix + ".sig")


def _verify_snapshot(payload: dict) -> tuple[str, str, str]:
    if not SNAPSHOT_DIGEST_PATH.exists():
        raise ReleaseSignatureError(
            f"missing delegation snapshot manifest: {SNAPSHOT_DIGEST_PATH}"
        )
    digest, filename = _read_manifest(SNAPSHOT_DIGEST_PATH)
    expected_name = SNAPSHOT_PATH.name
    if filename and filename != expected_name:
        raise ReleaseSignatureError(
            f"snapshot manifest filename mismatch: expected {expected_name}, got {filename}"
        )
    canonical = _canonical_state_digest(payload)
    if digest != canonical:
        raise ReleaseSignatureError(
            f"delegation snapshot digest mismatch: expected {digest}, got {canonical}"
        )

    recorded = f"{digest}  {expected_name}"
    signature_path = _snapshot_signature_path()
    signature = _verify_signature_file(signature_path, recorded, "delegation snapshot")

    return digest, recorded, signature


def _load_signature_metadata() -> dict:
    path = _metadata_path()
    if not path.exists():
        raise ReleaseSignatureError(f"missing signature metadata: {path}")
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        raise ReleaseSignatureError(
            f"invalid signature metadata: {path} ({exc})"
        ) from exc
    if not isinstance(metadata, dict):
        raise ReleaseSignatureError(
            f"invalid signature metadata: {path} (expected object)"
        )
    return metadata


def _load_existing_signature_telemetry() -> dict | None:
    if not SIGNATURE_TELEMETRY_PATH.exists():
        return None
    try:
        payload = json.loads(SIGNATURE_TELEMETRY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(payload, dict):
        return payload
    return None


def _write_signature_telemetry(
    tarball_recorded: str,
    tarball_signature: str,
    snapshot_recorded: str,
    snapshot_signature: str,
) -> None:
    payload = {
        "status": "green",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "signing_key_id": _signing_key_id(),
        "tarball_manifest": {
            "recorded": tarball_recorded,
            "signature": tarball_signature,
        },
        "delegation_snapshot": {
            "recorded": snapshot_recorded,
            "signature": snapshot_signature,
        },
    }
    previous = _load_existing_signature_telemetry()
    if previous:
        payload["previous"] = previous
    SIGNATURE_TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SIGNATURE_TELEMETRY_PATH.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def _verify_signature_metadata(
    tarball_recorded: str,
    tarball_signature: str,
    snapshot_recorded: str,
    snapshot_signature: str,
) -> None:
    metadata = _load_signature_metadata()
    key_id = metadata.get("signing_key_id")
    expected_id = _signing_key_id()
    if key_id != expected_id:
        raise ReleaseSignatureError(
            "signature metadata signing_key_id mismatch: "
            f"expected {expected_id}, got {key_id}"
        )

    tarball_meta = metadata.get("tarball_manifest") or {}
    if tarball_meta.get("recorded") != tarball_recorded:
        raise ReleaseSignatureError("tarball metadata recorded digest mismatch")
    if tarball_meta.get("signature") != tarball_signature:
        raise ReleaseSignatureError("tarball metadata signature mismatch")
    if tarball_meta.get("signature") != _signature_for(tarball_recorded):
        raise ReleaseSignatureError("tarball metadata signature invalid for key")

    snapshot_meta = metadata.get("delegation_snapshot") or {}
    if snapshot_meta.get("recorded") != snapshot_recorded:
        raise ReleaseSignatureError("snapshot metadata recorded digest mismatch")
    if snapshot_meta.get("signature") != snapshot_signature:
        raise ReleaseSignatureError("snapshot metadata signature mismatch")
    if snapshot_meta.get("signature") != _signature_for(snapshot_recorded):
        raise ReleaseSignatureError("snapshot metadata signature invalid for key")


def _install_snapshot(payload: dict, digest: str) -> None:
    try:
        from lib import cliDelegation
    except Exception as exc:  # pragma: no cover - import depends on runtime
        raise ReleaseSignatureError(
            f"failed to import cliDelegation for snapshot hydration ({exc})"
        )

    cliDelegation.apply_release_snapshot(payload)

    if not RUNTIME_STATE_PATH.exists():
        raise ReleaseSignatureError(
            f"hydrated delegation state missing after install: {RUNTIME_STATE_PATH}"
        )
    hydrated = json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
    if not isinstance(hydrated, dict):
        raise ReleaseSignatureError(
            "hydrated delegation state invalid (expected object)"
        )
    canonical = _canonical_state_digest(hydrated)
    if canonical != digest:
        raise ReleaseSignatureError(
            "hydrated delegation state digest mismatch: "
            f"expected {digest}, got {canonical}"
        )


def install_cli(force: bool = False, quiet: bool = False) -> Path:
    tarball = _tarball_path()
    manifest = _manifest_path(tarball)

    if not tarball.exists():
        raise FileNotFoundError(f"missing CLI tarball: {tarball}")
    if not manifest.exists():
        raise FileNotFoundError(f"missing CLI manifest: {manifest}")

    snapshot_payload = _load_snapshot_payload()
    (
        snapshot_digest,
        snapshot_recorded,
        snapshot_signature,
    ) = _verify_snapshot(snapshot_payload)

    _verify_checksum(tarball, manifest)
    manifest_recorded = manifest.read_text(encoding="utf-8").strip()
    manifest_signature = _verify_signature_file(
        manifest.with_suffix(manifest.suffix + ".sig"),
        manifest_recorded,
        "tarball manifest",
    )

    _verify_signature_metadata(
        manifest_recorded,
        manifest_signature,
        snapshot_recorded,
        snapshot_signature,
    )

    if not force and TARGET_PATH.exists():
        latest_artifact_mtime = max(
            tarball.stat().st_mtime,
            manifest.stat().st_mtime,
            SNAPSHOT_PATH.stat().st_mtime,
            SNAPSHOT_DIGEST_PATH.stat().st_mtime,
        )
        if TARGET_PATH.stat().st_mtime >= latest_artifact_mtime:
            _install_snapshot(snapshot_payload, snapshot_digest)
            _write_signature_telemetry(
                manifest_recorded,
                manifest_signature,
                snapshot_recorded,
                snapshot_signature,
            )
            if not quiet:
                print(f"CLI binary already installed at {TARGET_PATH}")
            return TARGET_PATH

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        with tarfile.open(tarball, "r:gz") as archive:
            try:
                member = archive.getmember("bar")
            except KeyError as exc:  # pragma: no cover - packaging contract
                raise RuntimeError("packaged CLI tarball missing 'bar' entry") from exc
            archive.extract(member, path=tmp_path)
        extracted = tmp_path / "bar"
        if not extracted.exists():  # pragma: no cover - defensive
            raise RuntimeError("extracted CLI binary missing after tar unpack")

        BIN_DIR.mkdir(parents=True, exist_ok=True)
        if TARGET_PATH.exists():
            if force:
                TARGET_PATH.unlink()
            elif not quiet:
                print(f"overwriting existing {TARGET_PATH}")
        shutil.copy2(extracted, TARGET_PATH)
        TARGET_PATH.chmod(0o755)

    _install_snapshot(snapshot_payload, snapshot_digest)
    _write_signature_telemetry(
        manifest_recorded,
        manifest_signature,
        snapshot_recorded,
        snapshot_signature,
    )

    if not quiet:
        print(f"installed CLI binary to {TARGET_PATH}")
    return TARGET_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify checksum and manifest without installing",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing binary even if present",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output",
    )
    args = parser.parse_args()

    tarball = _tarball_path()
    manifest = _manifest_path(tarball)

    try:
        if args.verify_only:
            _verify_checksum(tarball, manifest)
            if not args.quiet:
                print("checksum verified")
            return 0
        install_cli(force=args.force, quiet=args.quiet)
        return 0
    except Exception as exc:  # pragma: no cover - CLI surface
        print(f"install failed: {exc}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
