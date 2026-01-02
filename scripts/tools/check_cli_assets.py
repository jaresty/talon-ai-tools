#!/usr/bin/env python3
"""Check presence of CLI binary and shared schema assets for ADR-0063.

The command exits with code 1 when any required artefacts are missing and
prints the missing paths. Once the CLI binary and schema bundle land, this
script should return green and serve as evidence for shared command assets.
"""

from __future__ import annotations

import sys
from hashlib import sha256
from pathlib import Path
import platform

BIN_PATH = Path("bin/bar")
BIN_EXECUTABLE = Path("bin/bar.bin")
SCHEMA_PATH = Path("docs/schema/command-surface.json")
ARTIFACTS_DIR = Path("artifacts/cli")


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


def _check_manifest() -> bool:
    tarball = _tarball_path()
    manifest = _manifest_path()
    ok = True

    if not tarball.exists():
        print(f"missing: {tarball}", file=sys.stderr)
        ok = False
    if not manifest.exists():
        print(f"missing: {manifest}", file=sys.stderr)
        return False

    if not ok:
        return False

    recorded = manifest.read_text(encoding="utf-8").strip()
    if not recorded:
        print(f"empty manifest: {manifest}", file=sys.stderr)
        return False

    digest, _, filename = recorded.partition("  ")
    if not digest or len(digest) != 64:
        print(f"invalid manifest contents: {manifest}", file=sys.stderr)
        return False

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
    return ok


def main() -> int:
    required = (BIN_PATH, BIN_EXECUTABLE, SCHEMA_PATH)
    missing = [path for path in required if not path.exists()]
    ok = True
    if missing:
        for path in missing:
            print(f"missing: {path}", file=sys.stderr)
        ok = False

    if not _check_manifest():
        ok = False

    if ok:
        print("all CLI assets present")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
