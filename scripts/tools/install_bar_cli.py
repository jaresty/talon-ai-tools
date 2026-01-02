"""Install the bar CLI binary from the packaged tarball.

The installer verifies the SHA-256 checksum recorded in the manifest,
extracts the `bar` binary into `bin/bar.bin`, and keeps permissions aligned
for Talon delegation.
"""

from __future__ import annotations

import argparse
import hashlib
import platform
import shutil
import tarfile
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BIN_DIR = REPO_ROOT / "bin"
TARGET_PATH = BIN_DIR / "bar.bin"
ARTIFACTS_DIR = REPO_ROOT / "artifacts" / "cli"


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


def install_cli(force: bool = False, quiet: bool = False) -> Path:
    tarball = _tarball_path()
    manifest = _manifest_path(tarball)

    if not tarball.exists():
        raise FileNotFoundError(f"missing CLI tarball: {tarball}")
    if not manifest.exists():
        raise FileNotFoundError(f"missing CLI manifest: {manifest}")

    _verify_checksum(tarball, manifest)

    if not force and TARGET_PATH.exists():
        latest_artifact_mtime = max(tarball.stat().st_mtime, manifest.stat().st_mtime)
        if TARGET_PATH.stat().st_mtime >= latest_artifact_mtime:
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
