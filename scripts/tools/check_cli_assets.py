#!/usr/bin/env python3
"""Check presence of CLI binary and shared schema assets for ADR-0063.

The command exits with code 1 when any required artefacts are missing and
prints the missing paths. Once the CLI binary and schema bundle land, this
script should return green and serve as evidence for shared command assets.
"""

from __future__ import annotations

import json
import os
import sys
from hashlib import sha256
from pathlib import Path
import platform

BIN_PATH = Path("bin/bar")
BIN_EXECUTABLE = Path("bin/bar.bin")
SCHEMA_PATH = Path("docs/schema/command-surface.json")
ARTIFACTS_DIR = Path("artifacts/cli")
DELEGATION_STATE_ENV = "CLI_DELEGATION_STATE"
DELEGATION_STATE_PATH = Path(
    os.environ.get(DELEGATION_STATE_ENV, "var/cli-telemetry/delegation-state.json")
)
DELEGATION_STATE_DIGEST_ENV = "CLI_DELEGATION_STATE_DIGEST"
DELEGATION_STATE_DIGEST_PATH = Path(
    os.environ.get(
        DELEGATION_STATE_DIGEST_ENV,
        "artifacts/cli/delegation-state.json.sha256",
    )
)
DELEGATION_STATE_SIGNATURE_ENV = "CLI_DELEGATION_STATE_SIGNATURE"
DEFAULT_SIGNATURE_KEY = "adr-0063-cli-release-signature"
SIGNATURE_KEY_ENV = "CLI_RELEASE_SIGNING_KEY"
SIGNATURE_METADATA_ENV = "CLI_SIGNATURE_METADATA"
SIGNATURE_METADATA_PATH = Path(
    os.environ.get(SIGNATURE_METADATA_ENV, "artifacts/cli/signatures.json")
)
DEFAULT_SIGNING_KEY_ID = "local-dev"
SIGNING_KEY_ID_ENV = "CLI_RELEASE_SIGNING_KEY_ID"
DELEGATION_STATE_SNAPSHOT_ENV = "CLI_DELEGATION_STATE_SNAPSHOT"
DELEGATION_STATE_SNAPSHOT_PATH = Path(
    os.environ.get(
        DELEGATION_STATE_SNAPSHOT_ENV,
        "artifacts/cli/delegation-state.json",
    )
)
DELEGATION_STATE_SIGNATURE_PATH = Path(
    os.environ.get(
        DELEGATION_STATE_SIGNATURE_ENV,
        str(
            DELEGATION_STATE_DIGEST_PATH.with_suffix(
                DELEGATION_STATE_DIGEST_PATH.suffix + ".sig"
            )
        ),
    )
)


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


def _manifest_path() -> Path:
    tarball = _tarball_path()
    return tarball.with_name(f"{tarball.name}.sha256")


def _signing_key() -> str:
    return os.environ.get(SIGNATURE_KEY_ENV, DEFAULT_SIGNATURE_KEY)


def _signature_for(message: str) -> str:
    return sha256((_signing_key() + "\n" + message).encode("utf-8")).hexdigest()


def _signing_key_id() -> str:
    return os.environ.get(SIGNING_KEY_ID_ENV, DEFAULT_SIGNING_KEY_ID)


def _metadata_path() -> Path:
    return Path(os.environ.get(SIGNATURE_METADATA_ENV, str(SIGNATURE_METADATA_PATH)))


def _verify_signature(
    signature_path: Path, recorded: str, label: str
) -> tuple[bool, str]:
    if not signature_path.exists():
        print(f"missing {label} signature: {signature_path}", file=sys.stderr)
        return False, ""
    signature = signature_path.read_text(encoding="utf-8").strip()
    expected = _signature_for(recorded)
    if signature != expected:
        print(
            f"{label} signature mismatch: expected {expected}, got {signature}",
            file=sys.stderr,
        )
        return False, signature
    return True, signature


def _check_manifest() -> tuple[bool, str, str]:
    tarball = _tarball_path()
    manifest = _manifest_path()
    ok = True

    if not tarball.exists():
        print(f"missing: {tarball}", file=sys.stderr)
        ok = False
    if not manifest.exists():
        print(f"missing: {manifest}", file=sys.stderr)
        return False, "", ""

    if not ok:
        return False, "", ""

    recorded = manifest.read_text(encoding="utf-8").strip()
    if not recorded:
        print(f"empty manifest: {manifest}", file=sys.stderr)
        return False, "", ""

    digest, _, filename = recorded.partition("  ")
    if not digest or len(digest) != 64:
        print(f"invalid manifest contents: {manifest}", file=sys.stderr)
        return False, recorded, ""

    if filename and filename != tarball.name:
        print(
            f"manifest filename mismatch: expected {tarball.name}, got {filename}",
            file=sys.stderr,
        )
        ok = False

    computed = sha256(tarball.read_bytes()).hexdigest()
    if digest != computed:
        print(
            f"checksum mismatch for {tarball}: expected {digest}, got {computed}",
            file=sys.stderr,
        )
        ok = False

    signature_path = manifest.with_suffix(manifest.suffix + ".sig")
    sig_ok, signature = _verify_signature(signature_path, recorded, "tarball manifest")
    if not sig_ok:
        ok = False

    return ok, recorded, signature


def _canonical_state_digest(payload: dict) -> str:
    canonical = dict(payload)
    canonical["updated_at"] = None
    return sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _check_delegation_state() -> tuple[bool, str, str]:
    path = DELEGATION_STATE_PATH
    snapshot_path = DELEGATION_STATE_SNAPSHOT_PATH
    digest_path = DELEGATION_STATE_DIGEST_PATH
    signature_path = DELEGATION_STATE_SIGNATURE_PATH
    if not path.exists():
        print(f"missing delegation state: {path}", file=sys.stderr)
        return False, "", ""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        print(f"invalid delegation state: {path} ({exc})", file=sys.stderr)
        return False, "", ""

    if not isinstance(payload, dict):
        print(f"invalid delegation state: {path} (expected object)", file=sys.stderr)
        return False, "", ""

    enabled = payload.get("enabled")
    failure_count = payload.get("failure_count")
    failure_threshold = payload.get("failure_threshold")
    reason = str(payload.get("reason") or "").strip()

    if not isinstance(enabled, bool):
        print(
            f"invalid delegation state: {path} (enabled must be boolean)",
            file=sys.stderr,
        )
        return False, "", ""

    if not isinstance(failure_count, int) or failure_count < 0:
        print(
            f"invalid delegation state: {path} (failure_count must be >= 0)",
            file=sys.stderr,
        )
        return False, "", ""

    if not isinstance(failure_threshold, int) or failure_threshold <= 0:
        print(
            f"invalid delegation state: {path} (failure_threshold must be > 0)",
            file=sys.stderr,
        )
        return False, "", ""

    if not enabled:
        detail = reason or "delegation disabled"
        print(
            f"delegation disabled according to state {path}: {detail}",
            file=sys.stderr,
        )
        return False, "", ""

    if failure_count:
        print(
            "delegation state reports outstanding failures "
            f"({failure_count}/{failure_threshold}) in {path}",
            file=sys.stderr,
        )
        return False, "", ""

    events = payload.get("events", [])
    if not isinstance(events, list):
        print(
            f"invalid delegation state: {path} (events must be a list)",
            file=sys.stderr,
        )
        return False, "", ""

    runtime_digest = _canonical_state_digest(payload)

    if not snapshot_path.exists():
        print(
            f"missing delegation state snapshot: {snapshot_path}",
            file=sys.stderr,
        )
        return False, "", ""

    try:
        snapshot_payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        print(
            f"invalid delegation state snapshot: {snapshot_path} ({exc})",
            file=sys.stderr,
        )
        return False, "", ""

    if not isinstance(snapshot_payload, dict):
        print(
            f"invalid delegation state snapshot: {snapshot_path} (expected object)",
            file=sys.stderr,
        )
        return False, "", ""

    snapshot_digest = _canonical_state_digest(snapshot_payload)

    if not digest_path.exists():
        print(
            f"missing delegation state digest: {digest_path}",
            file=sys.stderr,
        )
        return False, "", ""

    recorded = digest_path.read_text(encoding="utf-8").strip()
    if not recorded:
        print(
            f"empty delegation state digest: {digest_path}",
            file=sys.stderr,
        )
        return False, "", ""

    digest, _, filename = recorded.partition("  ")
    if not digest or len(digest) != 64:
        print(
            f"invalid delegation state digest: {digest_path}",
            file=sys.stderr,
        )
        return False, recorded, ""

    expected_name = snapshot_path.name
    if filename and filename != expected_name:
        print(
            f"delegation state digest filename mismatch: expected {expected_name}, got {filename}",
            file=sys.stderr,
        )
        return False, recorded, ""

    if digest != snapshot_digest:
        print(
            "delegation state snapshot digest mismatch: "
            f"expected {digest}, got {snapshot_digest}",
            file=sys.stderr,
        )
        return False, recorded, ""

    if digest != runtime_digest:
        print(
            "runtime delegation state digest mismatch: "
            f"expected {digest}, got {runtime_digest}",
            file=sys.stderr,
        )
        return False, recorded, ""

    sig_ok, signature = _verify_signature(
        signature_path,
        recorded,
        "delegation state",
    )
    if not sig_ok:
        return False, recorded, signature

    return True, recorded, signature


def _check_metadata(
    tarball_recorded: str,
    tarball_signature: str,
    snapshot_recorded: str,
    snapshot_signature: str,
) -> bool:
    path = _metadata_path()
    if not path.exists():
        print(f"missing signature metadata: {path}", file=sys.stderr)
        return False
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        print(
            f"invalid signature metadata: {path} ({exc})",
            file=sys.stderr,
        )
        return False
    if not isinstance(metadata, dict):
        print(
            f"invalid signature metadata: {path} (expected object)",
            file=sys.stderr,
        )
        return False

    expected_id = _signing_key_id()
    actual_id = metadata.get("signing_key_id")
    if actual_id != expected_id:
        print(
            "signature metadata signing_key_id mismatch: "
            f"expected {expected_id}, got {actual_id}",
            file=sys.stderr,
        )
        return False

    tarball_meta = metadata.get("tarball_manifest") or {}
    if tarball_meta.get("recorded") != tarball_recorded:
        print("signature metadata tarball recorded mismatch", file=sys.stderr)
        return False
    if tarball_meta.get("signature") != tarball_signature:
        print("signature metadata tarball signature mismatch", file=sys.stderr)
        return False
    if tarball_meta.get("signature") != _signature_for(tarball_recorded):
        print("signature metadata tarball signature invalid", file=sys.stderr)
        return False

    snapshot_meta = metadata.get("delegation_snapshot") or {}
    if snapshot_meta.get("recorded") != snapshot_recorded:
        print("signature metadata snapshot recorded mismatch", file=sys.stderr)
        return False
    if snapshot_meta.get("signature") != snapshot_signature:
        print("signature metadata snapshot signature mismatch", file=sys.stderr)
        return False
    if snapshot_meta.get("signature") != _signature_for(snapshot_recorded):
        print("signature metadata snapshot signature invalid", file=sys.stderr)
        return False

    return True


def main() -> int:
    required = (BIN_PATH, BIN_EXECUTABLE, SCHEMA_PATH)
    missing = [path for path in required if not path.exists()]
    ok = True
    if missing:
        for path in missing:
            print(f"missing: {path}", file=sys.stderr)
        ok = False

    manifest_ok, manifest_recorded, manifest_signature = _check_manifest()
    if not manifest_ok:
        ok = False

    snapshot_ok, snapshot_recorded, snapshot_signature = _check_delegation_state()
    if not snapshot_ok:
        ok = False

    if manifest_ok and snapshot_ok:
        if not _check_metadata(
            manifest_recorded,
            manifest_signature,
            snapshot_recorded,
            snapshot_signature,
        ):
            ok = False

    if ok:
        print("all CLI assets present")
        print(f"cli_tarball={_tarball_path()}")
        print(f"cli_manifest={_manifest_path()}")
        print(f"cli_signatures={_metadata_path()}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
