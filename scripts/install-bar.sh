#!/usr/bin/env bash
set -euo pipefail

REPO="talonvoice/talon-ai-tools"
BINARY_NAME="bar"
INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"
KEEP_TEMP="${KEEP_TEMP:-0}"
WORKDIR=""
CREATED_WORKDIR=0

print_usage() {
    cat <<'USAGE'
Usage: install-bar.sh [--version vX.Y.Z] [--install-dir DIR]

Flags:
  --version       Release tag to install (defaults to latest).
  --install-dir   Destination directory (defaults to /usr/local/bin or $INSTALL_DIR).
  --keep-temp     Leave downloaded artifacts in place for debugging.

Environment:
  INSTALL_DIR     Overrides the destination directory.
  TMPDIR          Overrides the temporary working directory.
  KEEP_TEMP=1     Disables cleanup of the temporary directory.

The script downloads the release tarball, verifies the SHA-256 checksum, and
installs the binary into the requested directory. It requires curl, tar, and
sha256sum (or shasum on macOS).
USAGE
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

require_commands() {
    local missing=()
    for cmd in "$@"; do
        if ! command_exists "$cmd"; then
            missing+=("$cmd")
        fi
    done
    if ((${#missing[@]} > 0)); then
        printf 'error: missing required command(s): %s\n' "${missing[*]}" >&2
        exit 1
    fi
}

resolve_arch() {
    local arch
    arch=$(uname -m)
    case "$arch" in
    x86_64 | amd64) echo "amd64" ;;
    arm64 | aarch64) echo "arm64" ;;
    *)
        printf 'error: unsupported architecture %s\n' "$arch" >&2
        exit 1
        ;;
    esac
}

resolve_os() {
    local os
    os=$(uname -s)
    case "$os" in
    Linux) echo "linux" ;;
    Darwin) echo "darwin" ;;
    *)
        printf 'error: unsupported operating system %s\n' "$os" >&2
        exit 1
        ;;
    esac
}

fetch_latest_version() {
    require_commands curl
    local latest
    latest=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" | sed -n 's/^  \"tag_name\": \"\(.*\)\",$/\1/p' | head -n1)
    if [[ -z "$latest" ]]; then
        printf 'error: unable to determine latest release tag via GitHub API\n' >&2
        exit 1
    fi
    echo "$latest"
}

sha256_tool() {
    if command_exists sha256sum; then
        echo sha256sum
    elif command_exists shasum; then
        echo "shasum -a 256"
    else
        printf 'error: unable to find sha256sum or shasum\n' >&2
        exit 1
    fi
}

clean_up() {
    if [[ $CREATED_WORKDIR == 1 ]]; then
        if [[ $KEEP_TEMP != 1 ]]; then
            rm -rf "$WORKDIR"
        else
            printf 'info: keeping temporary directory %s\n' "$WORKDIR"
        fi
    fi
}

trap clean_up EXIT

main() {

    local version=""
    local install_dir="$INSTALL_DIR"
    local keep_temp=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
        --version)
            shift
            version="${1:-}"
            [[ -n "$version" ]] || {
                printf 'error: --version requires a value\n' >&2
                exit 1
            }
            ;;
        --install-dir)
            shift
            install_dir="${1:-}"
            [[ -n "$install_dir" ]] || {
                printf 'error: --install-dir requires a value\n' >&2
                exit 1
            }
            ;;
        --keep-temp)
            keep_temp=1
            KEEP_TEMP=1
            ;;
        -h | --help)
            print_usage
            exit 0
            ;;
        *)
            printf 'error: unknown option %s\n' "$1" >&2
            print_usage
            exit 1
            ;;
        esac
        shift || true
    done

    if [[ -z "$version" ]]; then
        version=$(fetch_latest_version)
    fi

    local base_tmp
    base_tmp="${TMPDIR:-/tmp}"
    WORKDIR=$(mktemp -d "${base_tmp}/bar-install.XXXXXX")
    CREATED_WORKDIR=1

    mkdir -p "$install_dir"

    local os arch archive checksum_url base_url archive_name checksum_file
    os=$(resolve_os)
    arch=$(resolve_arch)
    base_url="https://github.com/${REPO}/releases/download/${version}"
    archive_name="${BINARY_NAME}_${version#v}_${os}_${arch}.tar.gz"
    archive="${WORKDIR}/${archive_name}"
    checksum_url="${base_url}/checksums.txt"
    checksum_file="${WORKDIR}/checksums.txt"

    require_commands curl tar
    curl -fsSL "${base_url}/${archive_name}" -o "$archive"
    curl -fsSL "$checksum_url" -o "$checksum_file"

    local checksum_line
    checksum_line=$(grep "${archive_name}" "$checksum_file" || true)
    if [[ -z "$checksum_line" ]]; then
        printf 'error: unable to find checksum for %s\n' "$archive_name" >&2
        exit 1
    fi

    local sha_tool
    sha_tool=$(sha256_tool)
    echo "$checksum_line" | $sha_tool --check --status --ignore-missing
    printf 'info: checksum verified for %s\n' "$archive_name"

    tar -xzf "$archive" -C "$WORKDIR"

    local binary_path
    binary_path=$(find "$WORKDIR" -maxdepth 2 -type f -name "$BINARY_NAME" | head -n1)

    if [[ -z "$binary_path" ]]; then
        printf 'error: unable to find %s binary in archive\n' "$BINARY_NAME" >&2
        exit 1
    fi

    install -m 0755 "$binary_path" "$install_dir/$BINARY_NAME"
    printf 'info: installed %s to %s\n' "$BINARY_NAME" "$install_dir/$BINARY_NAME"
    printf 'info: run `%s --help` to get started.\n' "$BINARY_NAME"

    if ((keep_temp)); then
        printf 'info: temporary artifacts retained in %s
' "$WORKDIR"
    fi
}

main "$@"
