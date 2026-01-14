#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/tools/run-tui2-expect.sh <case>
       scripts/tools/run-tui2-expect.sh --list
       scripts/tools/run-tui2-expect.sh --all
Run Bubble Tea TUI2 expect integration cases.

Examples:
  scripts/tools/run-tui2-expect.sh token-selection-preview
  scripts/tools/run-tui2-expect.sh --list
  scripts/tools/run-tui2-expect.sh --all
EOF
}

if [[ ${1:-} == "--help" ]]; then
    usage
    exit 0
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
CASES_DIR="$REPO_ROOT/tests/integration/tui2/cases"
TMP_DIR="$REPO_ROOT/tests/integration/tui2/tmp"
mkdir -p "$TMP_DIR"

list_cases() {
    if [[ -d $CASES_DIR ]]; then
        find "$CASES_DIR" -maxdepth 1 -name '*.exp' -exec basename {} .exp \; | sort
    fi
}

run_case() {
    local case_name="$1"
    local case_file="$CASES_DIR/$case_name.exp"
    if [[ ! -f $case_file ]]; then
        echo "error: expect case '$case_name' not found at $case_file" >&2
        return 1
    fi

    local args_file="$CASES_DIR/$case_name.args"
    local env_file="$CASES_DIR/$case_name.env"

    local -a extra_args=()
    if [[ -f $args_file ]]; then
        while IFS= read -r line || [[ -n $line ]]; do
            [[ -z $line ]] && continue
            extra_args+=("$line")
        done <"$args_file"
    fi

    local exported_keys=""
    if [[ -f $env_file ]]; then
        while IFS='=' read -r key value; do
            [[ -z $key ]] && continue
            export "$key"="$value"
            exported_keys+=" $key"
        done <"$env_file"
    fi

    local -a cmd_list=($BAR_TUI2_CMD)
    if [[ ${#extra_args[@]} -gt 0 ]]; then
        cmd_list+=("${extra_args[@]}")
    fi

    local log_dir="$TMP_DIR/$case_name"
    mkdir -p "$log_dir"
    local transcript="$log_dir/transcript.log"

    export TUI_EXPECT_CMD="${cmd_list[*]}"
    export TUI_EXPECT_TRANSCRIPT="$transcript"

    /usr/bin/expect "$case_file"
    local status=$?

    if [[ -n $exported_keys ]]; then
        for key in $exported_keys; do
            unset "$key"
        done
    fi

    if [[ $status -ne 0 ]]; then
        echo "Case '$case_name' FAILED (exit $status). Transcript: $transcript" >&2
        cat "$transcript" >&2
        return $status
    fi

    echo "Case '$case_name' passed. Transcript: $transcript"
}

if [[ ${1:-} == "--list" ]]; then
    list_cases
    exit 0
fi

BAR_TUI2_CMD_DEFAULT="go run ./cmd/bar tui2 --grammar cmd/bar/testdata/grammar.json --no-alt-screen"
BAR_TUI2_CMD=${BAR_TUI2_CMD:-$BAR_TUI2_CMD_DEFAULT}

if [[ ${1:-} == "--all" ]]; then
    shift
    cases=()
    while IFS= read -r case_name; do
        [[ -z $case_name ]] && continue
        cases+=("$case_name")
    done < <(list_cases)
    if [[ ${#cases[@]} -eq 0 ]]; then
        echo "No expect cases found under $CASES_DIR" >&2
        exit 1
    fi
    for case_name in "${cases[@]}"; do
        if ! run_case "$case_name"; then
            exit 1
        fi
    done
    exit 0
fi

if [[ $# -lt 1 ]]; then
    usage
    exit 1
fi

run_case "$1"
