#!/usr/bin/env bash
# dispatch-eval setup.sh — scaffold a tmp scenario from scenarios/<X>/
# SSOT: .claude/skills/dispatch-eval/scenarios/<X>/
# Usage: bash setup.sh <scenario-letter>
set -euo pipefail

SCENARIO="${1:-}"
if [[ -z "$SCENARIO" ]]; then
  echo "Usage: setup.sh <M|N|O|P|Q|R|S|T|U|V|W|X|Y>" >&2
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

NAME=$(jq -r '.name' "$META")
TASK_PROMPT=$(jq -r '.task_prompt' "$META")

DIR="/tmp/dispatch-test-${SCENARIO}"
rm -rf "$DIR"
mkdir -p "$DIR"

cd "$DIR"

echo "=== Scenario $SCENARIO: $NAME ==="
echo "Directory: $DIR"
echo ""
echo "ready"
echo ""
echo "Setup complete: $DIR"
