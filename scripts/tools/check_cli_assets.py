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
from datetime import datetime, timezone
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
SIGNATURE_TELEMETRY_ENV = "CLI_SIGNATURE_TELEMETRY"
SIGNATURE_TELEMETRY_PATH = Path(
    os.environ.get(
        SIGNATURE_TELEMETRY_ENV,
        "var/cli-telemetry/signature-metadata.json",
    )
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
REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from lib.requestLog import drop_reason_message as _drop_reason_message
except Exception:  # pragma: no cover - defensive import for guard script
    _drop_reason_message = None
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
) -> tuple[bool, str, list[str]]:
    issues: list[str] = []
    if not signature_path.exists():
        message = f"missing {label} signature: {signature_path}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", issues
    signature = signature_path.read_text(encoding="utf-8").strip()
    expected = _signature_for(recorded)
    if signature != expected:
        message = f"{label} signature mismatch: expected {expected}, got {signature}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, signature, issues
    return True, signature, issues


def _check_manifest() -> tuple[bool, str, str, list[str]]:
    tarball = _tarball_path()
    manifest = _manifest_path()
    ok = True
    issues: list[str] = []

    if not tarball.exists():
        message = f"missing: {tarball}"
        print(message, file=sys.stderr)
        issues.append(message)
        ok = False
    if not manifest.exists():
        message = f"missing: {manifest}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues

    if not ok:
        return False, "", "", issues

    recorded = manifest.read_text(encoding="utf-8").strip()
    if not recorded:
        message = f"empty manifest: {manifest}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues

    digest, _, filename = recorded.partition("  ")
    if not digest or len(digest) != 64:
        message = f"invalid manifest contents: {manifest}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, recorded, "", issues

    if filename and filename != tarball.name:
        message = f"manifest filename mismatch: expected {tarball.name}, got {filename}"
        print(message, file=sys.stderr)
        issues.append(message)
        ok = False

    computed = sha256(tarball.read_bytes()).hexdigest()
    if digest != computed:
        message = f"checksum mismatch for {tarball}: expected {digest}, got {computed}"
        print(message, file=sys.stderr)
        issues.append(message)
        ok = False

    signature_path = manifest.with_suffix(manifest.suffix + ".sig")
    sig_ok, signature, sig_issues = _verify_signature(
        signature_path, recorded, "tarball manifest"
    )
    issues.extend(sig_issues)
    if not sig_ok:
        ok = False

    return ok, recorded, signature, issues


def _canonical_state_digest(payload: dict) -> str:
    canonical = dict(payload)
    canonical["updated_at"] = None
    return sha256(
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


def _check_delegation_state() -> tuple[bool, str, str, list[str], dict, dict]:
    path = DELEGATION_STATE_PATH
    snapshot_path = DELEGATION_STATE_SNAPSHOT_PATH
    digest_path = DELEGATION_STATE_DIGEST_PATH
    signature_path = DELEGATION_STATE_SIGNATURE_PATH
    issues: list[str] = []

    if not path.exists():
        message = f"missing delegation state: {path}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        message = f"invalid delegation state: {path} ({exc})"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    if not isinstance(payload, dict):
        message = f"invalid delegation state: {path} (expected object)"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    enabled = payload.get("enabled")
    failure_count = payload.get("failure_count")
    failure_threshold = payload.get("failure_threshold")
    reason = str(payload.get("reason") or "").strip()

    if not isinstance(enabled, bool):
        message = f"invalid delegation state: {path} (enabled must be boolean)"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    if not isinstance(failure_count, int) or failure_count < 0:
        message = f"invalid delegation state: {path} (failure_count must be >= 0)"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    if not isinstance(failure_threshold, int) or failure_threshold <= 0:
        message = f"invalid delegation state: {path} (failure_threshold must be > 0)"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    if not enabled:
        detail = reason or "delegation disabled"
        message = f"delegation disabled according to state {path}: {detail}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    if isinstance(failure_count, int) and failure_count:
        message = (
            "delegation state reports outstanding failures "
            f"({failure_count}/{failure_threshold}) in {path}"
        )
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    events = payload.get("events", [])
    if not isinstance(events, list):
        message = f"invalid delegation state: {path} (events must be a list)"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    runtime_digest = _canonical_state_digest(payload)

    if not snapshot_path.exists():
        message = f"missing delegation state snapshot: {snapshot_path}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    try:
        snapshot_payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        message = f"invalid delegation state snapshot: {snapshot_path} ({exc})"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    if not isinstance(snapshot_payload, dict):
        message = (
            f"invalid delegation state snapshot: {snapshot_path} (expected object)"
        )
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    snapshot_digest = _canonical_state_digest(snapshot_payload)

    if not digest_path.exists():
        message = f"missing delegation state digest: {digest_path}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    recorded = digest_path.read_text(encoding="utf-8").strip()
    if not recorded:
        message = f"empty delegation state digest: {digest_path}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, "", "", issues, {}, {}

    digest, _, filename = recorded.partition("  ")
    if not digest or len(digest) != 64:
        message = f"invalid delegation state digest: {digest_path}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, recorded, "", issues, {}, {}

    expected_name = snapshot_path.name
    if filename and filename != expected_name:
        message = (
            "delegation state digest filename mismatch: "
            f"expected {expected_name}, got {filename}"
        )
        print(message, file=sys.stderr)
        issues.append(message)
        return False, recorded, "", issues, {}, {}

    if digest != snapshot_digest:
        message = (
            "delegation state snapshot digest mismatch: "
            f"expected {digest}, got {snapshot_digest}"
        )
        print(message, file=sys.stderr)
        issues.append(message)
        return False, recorded, "", issues, {}, {}

    if digest != runtime_digest:
        message = (
            "runtime delegation state digest mismatch: "
            f"expected {digest}, got {runtime_digest}"
        )
        print(message, file=sys.stderr)
        issues.append(message)
        return False, recorded, "", issues, {}, {}

    runtime_recovery = _recovery_snapshot_from_payload(payload)
    snapshot_recovery = _recovery_snapshot_from_payload(snapshot_payload)
    if runtime_recovery != snapshot_recovery:
        message = "delegation recovery snapshot mismatch between runtime and release"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, recorded, "", issues, snapshot_payload, payload

    sig_ok, signature, sig_issues = _verify_signature(
        signature_path,
        recorded,
        "delegation state",
    )
    issues.extend(sig_issues)
    if not sig_ok:
        return False, recorded, signature, issues, snapshot_payload, payload

    return True, recorded, signature, issues, snapshot_payload, payload


def _check_metadata(
    tarball_recorded: str,
    tarball_signature: str,
    snapshot_recorded: str,
    snapshot_signature: str,
    snapshot_payload: dict,
) -> tuple[bool, dict | None, list[str]]:
    path = _metadata_path()
    issues: list[str] = []
    if not path.exists():
        message = f"missing signature metadata: {path}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, None, issues
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        message = f"invalid signature metadata: {path} ({exc})"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, None, issues
    if not isinstance(metadata, dict):
        message = f"invalid signature metadata: {path} (expected object)"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, None, issues

    expected_id = _signing_key_id()
    actual_id = metadata.get("signing_key_id")
    if actual_id != expected_id:
        message = (
            "signature metadata signing_key_id mismatch: "
            f"expected {expected_id}, got {actual_id}"
        )
        print(message, file=sys.stderr)
        issues.append(message)
        return False, metadata, issues

    tarball_meta = metadata.get("tarball_manifest") or {}
    if tarball_meta.get("recorded") != tarball_recorded:
        message = "signature metadata tarball recorded mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, metadata, issues
    if tarball_meta.get("signature") != tarball_signature:
        message = "signature metadata tarball signature mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, metadata, issues
    if tarball_meta.get("signature") != _signature_for(tarball_recorded):
        message = "signature metadata tarball signature invalid"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, metadata, issues

    snapshot_meta = metadata.get("delegation_snapshot") or {}
    if snapshot_meta.get("recorded") != snapshot_recorded:
        message = "signature metadata snapshot recorded mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, metadata, issues
    if snapshot_meta.get("signature") != snapshot_signature:
        message = "signature metadata snapshot signature mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, metadata, issues
    if snapshot_meta.get("signature") != _signature_for(snapshot_recorded):
        message = "signature metadata snapshot signature invalid"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, metadata, issues

    expected_recovery = _recovery_snapshot_from_payload(snapshot_payload)
    recovery_meta = metadata.get("cli_recovery_snapshot")
    if not isinstance(recovery_meta, dict):
        message = "signature metadata recovery snapshot missing"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, metadata, issues
    if recovery_meta != expected_recovery:
        message = "signature metadata recovery snapshot mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, metadata, issues

    return True, metadata, issues


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_signature_telemetry() -> tuple[bool, dict | None, list[str]]:
    path = SIGNATURE_TELEMETRY_PATH
    issues: list[str] = []
    if not path.exists():
        return True, None, issues
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        message = f"signature telemetry invalid JSON: {path} ({exc})"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, None, issues
    if not isinstance(payload, dict):
        message = f"signature telemetry invalid payload: {path}"
        print(message, file=sys.stderr)
        issues.append(message)
        return False, None, issues
    return True, payload, issues


def _check_signature_telemetry(
    metadata: dict,
    tarball_recorded: str,
    tarball_signature: str,
    snapshot_recorded: str,
    snapshot_signature: str,
    snapshot_payload: dict,
) -> tuple[bool, dict, dict | None, list[str]]:
    issues: list[str] = []
    expected = {
        "signing_key_id": metadata.get("signing_key_id"),
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

    read_ok, previous, read_issues = _read_signature_telemetry()
    issues.extend(read_issues)
    if not read_ok:
        return False, expected, previous, issues

    if previous is None:
        return True, expected, None, issues

    ok = True

    if previous.get("signing_key_id") != expected["signing_key_id"]:
        message = "signature telemetry signing_key_id mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        ok = False

    prev_tarball = previous.get("tarball_manifest") or {}
    if prev_tarball.get("recorded") != expected["tarball_manifest"]["recorded"]:
        message = "signature telemetry tarball recorded mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        ok = False
    if prev_tarball.get("signature") != expected["tarball_manifest"]["signature"]:
        message = "signature telemetry tarball signature mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        ok = False

    prev_snapshot = previous.get("delegation_snapshot") or {}
    if prev_snapshot.get("recorded") != expected["delegation_snapshot"]["recorded"]:
        message = "signature telemetry snapshot recorded mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        ok = False
    if prev_snapshot.get("signature") != expected["delegation_snapshot"]["signature"]:
        message = "signature telemetry snapshot signature mismatch"
        print(message, file=sys.stderr)
        issues.append(message)
        ok = False

    expected_recovery = expected.get("cli_recovery_snapshot")
    previous_recovery = previous.get("cli_recovery_snapshot") if previous else None
    if previous_recovery != expected_recovery:
        if previous_recovery is None:
            message = (
                "signature telemetry recovery snapshot missing; rerun "
                "`python3 scripts/tools/package_bar_cli.py --print-paths` to refresh packaging artefacts"
            )
        else:
            message = (
                "signature telemetry recovery snapshot mismatch; rerun "
                "`python3 scripts/tools/package_bar_cli.py --print-paths` to refresh packaging artefacts"
            )
        print(message, file=sys.stderr)
        issues.append(message)
        ok = False

    return ok, expected, previous, issues


def _write_signature_telemetry(
    expected: dict | None,
    previous: dict | None,
    issues: list[str],
    ok: bool,
) -> None:
    payload: dict = {
        "status": "green" if ok else "red",
        "generated_at": _timestamp(),
    }
    if expected is not None:
        payload.update(expected)
    if previous is not None:
        payload["previous"] = previous
    if issues:
        payload["issues"] = list(issues)

    try:
        SIGNATURE_TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        SIGNATURE_TELEMETRY_PATH.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
    except Exception:
        pass


def main() -> int:
    required = (BIN_PATH, BIN_EXECUTABLE, SCHEMA_PATH)
    missing = [path for path in required if not path.exists()]
    issues: list[str] = []
    ok = True
    if missing:
        for path in missing:
            message = f"missing: {path}"
            print(message, file=sys.stderr)
            issues.append(message)
        ok = False

    manifest_ok, manifest_recorded, manifest_signature, manifest_issues = (
        _check_manifest()
    )
    issues.extend(manifest_issues)
    if not manifest_ok:
        ok = False

    (
        snapshot_ok,
        snapshot_recorded,
        snapshot_signature,
        snapshot_issues,
        snapshot_payload,
        runtime_payload,
    ) = _check_delegation_state()
    issues.extend(snapshot_issues)
    if not snapshot_ok:
        ok = False

    metadata_ok = False
    metadata: dict | None = None
    if manifest_ok and snapshot_ok:
        metadata_ok, metadata, metadata_issues = _check_metadata(
            manifest_recorded,
            manifest_signature,
            snapshot_recorded,
            snapshot_signature,
            snapshot_payload,
        )
        issues.extend(metadata_issues)
        if not metadata_ok:
            ok = False

    telemetry_ok = True
    expected_payload: dict | None = None
    previous_payload: dict | None = None
    if metadata_ok and metadata is not None:
        telemetry_ok, expected_payload, previous_payload, telemetry_issues = (
            _check_signature_telemetry(
                metadata,
                manifest_recorded,
                manifest_signature,
                snapshot_recorded,
                snapshot_signature,
                snapshot_payload,
            )
        )
        issues.extend(telemetry_issues)
        if not telemetry_ok:
            ok = False

    if ok:
        print("all CLI assets present")
        print(f"cli_tarball={_tarball_path()}")
        print(f"cli_manifest={_manifest_path()}")
        print(f"cli_signatures={_metadata_path()}")

    _write_signature_telemetry(
        expected_payload,
        previous_payload,
        issues if not ok else [],
        ok,
    )

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
