#!/usr/bin/env bash
# ground-eval run-agent.sh — invoke haiku agent for a ground protocol compliance scenario
# Usage: bash run-agent.sh <A|B|C|D|E|F|G|H|I>
set -euo pipefail

SCENARIO="${1:-}"
if [[ -z "$SCENARIO" ]]; then
  echo "Usage: run-agent.sh <A|B|C|D|E|F|G|H|I>" >&2
  exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SKILL_DIR/../../../.." && pwd)"
META="$SKILL_DIR/scenarios/$SCENARIO/meta.json"
TRANSCRIPT="/tmp/ground-test-${SCENARIO}/transcript.jsonl"

if [[ ! -f "$META" ]]; then
  echo "Error: scenarios/$SCENARIO/meta.json not found." >&2
  exit 1
fi

mkdir -p "/tmp/ground-test-${SCENARIO}"

NAME=$(jq -r '.name' "$META")
TASK_PROMPT=$(jq -r '.task_prompt' "$META")
EVAL_GATE=$(jq -r '.eval_gate' "$META")
CRITERION=$(jq -r '.target_criteria' "$META")
MAX_TURNS=$(jq -r '.max_turns // "1"' "$META")

# System prompt: raw build_ground_prompt() output — no bar build stack
SYSTEM_PROMPT=$(python3 -c "
import sys
sys.path.insert(0, '$REPO_DIR')
from lib.groundPrompt import build_ground_prompt
print(build_ground_prompt())
")

if [[ -z "$SYSTEM_PROMPT" ]]; then
  echo "Error: build_ground_prompt() returned empty output." >&2
  exit 1
fi

echo "=== Running haiku agent for ground-eval scenario $SCENARIO ==="
echo "Name: $NAME"
echo "Criterion: $CRITERION"
echo "Max turns: $MAX_TURNS"
echo "Task: $TASK_PROMPT"
echo ""

claude -p "$TASK_PROMPT" \
  --system-prompt "$SYSTEM_PROMPT" \
  --model claude-haiku-4-5 \
  --permission-mode bypassPermissions \
  --output-format stream-json \
  --verbose \
  --max-turns "$MAX_TURNS" \
  > "$TRANSCRIPT" 2>&1

echo ""
echo "=== Final agent output ==="
python3 -c "
import sys, json
for line in open('$TRANSCRIPT'):
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
        if obj.get('type') == 'result':
            print(obj.get('result', ''))
    except json.JSONDecodeError:
        pass
"

echo ""
echo "=== Eval gate check: criterion $CRITERION ==="
echo "Gate: $EVAL_GATE"
echo ""
echo "Transcript saved to: $TRANSCRIPT"
