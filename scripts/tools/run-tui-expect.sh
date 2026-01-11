#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/tools/run-tui-expect.sh <case> [-- list]
Run a Bubble Tea TUI expect integration case.

Examples:
  scripts/tools/run-tui-expect.sh launch-status
  scripts/tools/run-tui-expect.sh --list
EOF
}

if [[ ${1:-} == "--help" ]]; then
    usage
    exit 0
fi

REPO_ROOT=$(git rev-parse --show-toplevel)
CASES_DIR="$REPO_ROOT/tests/integration/tui/cases"
TMP_DIR="$REPO_ROOT/tests/integration/tui/tmp"
mkdir -p "$TMP_DIR"

if [[ ${1:-} == "--list" ]]; then
    if [[ -d $CASES_DIR ]]; then
        find "$CASES_DIR" -name '*.exp' -maxdepth 1 -exec basename {} .exp \; | sort
    fi
    exit 0
fi

if [[ $# -lt 1 ]]; then
    usage >&2
    exit 1
fi

CASE="$1"
CASE_FILE="$CASES_DIR/$CASE.exp"
if [[ ! -f $CASE_FILE ]]; then
    echo "error: expect case '$CASE' not found at $CASE_FILE" >&2
    exit 1
fi

ARGS_FILE="$CASES_DIR/$CASE.args"
ENV_FILE="$CASES_DIR/$CASE.env"

BAR_TUI_CMD_DEFAULT="go run ./cmd/bar tui --grammar cmd/bar/testdata/grammar.json --no-alt-screen"
BAR_TUI_CMD=${BAR_TUI_CMD:-$BAR_TUI_CMD_DEFAULT}

EXTRA_ARGS=()
if [[ -f $ARGS_FILE ]]; then
    mapfile -t EXTRA_ARGS <"$ARGS_FILE"
fi

if [[ -f $ENV_FILE ]]; then
    while IFS='=' read -r key value; do
        [[ -z $key ]] && continue
        export "$key"="$value"
    done <"$ENV_FILE"
fi

CMD_LIST=($BAR_TUI_CMD)
if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
    CMD_LIST+=("${EXTRA_ARGS[@]}")
fi

LOG_DIR="$TMP_DIR/$CASE"
mkdir -p "$LOG_DIR"
TRANSCRIPT="$LOG_DIR/transcript.log"
DEBUG_LOG="$LOG_DIR/palette.log"

export TUI_EXPECT_CMD="${CMD_LIST[*]}"
export TUI_EXPECT_TRANSCRIPT="$TRANSCRIPT"
export TUI_EXPECT_DEBUG_LOG="$DEBUG_LOG"
export TUI_EXPECT_FIXTURES="$REPO_ROOT/tests/integration/tui/fixtures"

/usr/bin/expect "$CASE_FILE"
STATUS=$?
if [[ $STATUS -ne 0 ]]; then
    echo "Case '$CASE' FAILED (exit $STATUS). Transcript: $TRANSCRIPT" >&2
    exit $STATUS
fi

echo "Case '$CASE' passed. Transcript: $TRANSCRIPT"
