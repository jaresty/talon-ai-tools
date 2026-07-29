#!/usr/bin/env bash
# ground-eval setup.sh — scaffold a tmp scenario from scenarios/<X>/
# Usage: bash setup.sh <A|B|C|D|E|F|G|H|I>
set -euo pipefail

SCENARIO="${1:-}"
if [[ -z "$SCENARIO" ]]; then
  echo "Usage: setup.sh <A|B|C|D|E|F|G|H|I>" >&2
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
SETUP_FILES=$(jq -r '.setup_files // {} | to_entries[] | "\(.key)\t\(.value)"' "$META")

DIR="/tmp/ground-test-${SCENARIO}"
rm -rf "$DIR"
mkdir -p "$DIR"

cd "$DIR"

# Write any setup files declared in meta.json
if [[ -n "$SETUP_FILES" ]]; then
  while IFS=$'\t' read -r filename content; do
    echo "$content" > "$DIR/$filename"
  done <<< "$SETUP_FILES"
fi

echo "=== Scenario $SCENARIO: $NAME ==="
echo "Directory: $DIR"
echo ""
echo "ready"
echo ""
echo "Setup complete: $DIR"
