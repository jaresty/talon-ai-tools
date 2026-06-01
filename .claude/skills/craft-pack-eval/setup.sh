#!/usr/bin/env bash
# craft-pack-eval setup.sh — scaffold a tmp scenario from scenarios/<X>/
# SSOT: .claude/skills/craft-pack-eval/scenarios/<X>/
# Usage: bash setup.sh <scenario-letter>
set -euo pipefail

SCENARIO="${1:-}"
if [[ -z "$SCENARIO" ]]; then
  echo "Usage: setup.sh <A|B|C|D|E|F|G|H|I|J|K>" >&2
  exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
SCENARIO_DIR="$SKILL_DIR/scenarios/$SCENARIO"

if [[ ! -d "$SCENARIO_DIR" ]]; then
  echo "Error: scenario directory not found: $SCENARIO_DIR" >&2
  echo "Valid scenarios: $(ls "$SKILL_DIR/scenarios/" | tr '\n' ' ')" >&2
  exit 1
fi

META="$SCENARIO_DIR/meta.json"
if [[ ! -f "$META" ]]; then
  echo "Error: meta.json not found in $SCENARIO_DIR" >&2
  exit 1
fi

NO_CODE=$(jq -r '.no_code // false' "$META")
MODULE=$(jq -r '.module // ""' "$META")
EXPECT=$(jq -r '.expect' "$META")
TASK_PROMPT=$(jq -r '.task_prompt' "$META")
NAME=$(jq -r '.name' "$META")

DIR="/tmp/haiku-test-${SCENARIO}"
rm -rf "$DIR"
mkdir -p "$DIR"

# Copy all non-meta files from scenario directory
find "$SCENARIO_DIR" -maxdepth 1 -type f ! -name 'meta.json' -exec cp {} "$DIR/" \;
chmod +x "$DIR"/*.sh 2>/dev/null || true

cd "$DIR"

# Save task prompt for run-agent.sh
echo "TASK_PROMPT=$(printf '%q' "$TASK_PROMPT")" > .task-prompt

echo "=== Scenario $SCENARIO: $NAME ==="
echo "Directory: $DIR"
echo ""

if [[ "$NO_CODE" == "true" ]]; then
  echo "=== No-code scenario — skipping go test ==="
  echo "ready"
  echo ""
  echo "=== Gate check: expecting '$EXPECT' ==="
  echo "PASS: pre-state output contains expected string"
else
  echo "Module: $MODULE"
  go mod init "$MODULE" > /dev/null 2>&1

  echo "=== Pre-state run ==="
  PRE_STATE_OUTPUT=$(go test ./... 2>&1 || true)
  echo "$PRE_STATE_OUTPUT"

  echo ""
  echo "=== Gate check: expecting '$EXPECT' ==="
  if echo "$PRE_STATE_OUTPUT" | grep -qF "$EXPECT"; then
    echo "PASS: pre-state output contains expected string"
  else
    echo "FAIL: pre-state output does not contain '$EXPECT'" >&2
    exit 1
  fi
fi

echo ""
echo "Setup complete: $DIR"
