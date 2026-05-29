#!/usr/bin/env bash
# craft-pack-eval run-agent.sh — invoke haiku agent for a scenario
# Usage: bash run-agent.sh <scenario-letter>
set -euo pipefail

SCENARIO="${1:-}"
if [[ -z "$SCENARIO" ]]; then
  echo "Usage: run-agent.sh <A|B|C|D|E|F|G|H>" >&2
  exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
META="$SKILL_DIR/scenarios/$SCENARIO/meta.json"
DIR="/tmp/haiku-test-${SCENARIO}"
TRANSCRIPT="$DIR/transcript.jsonl"
TOOL_RESULT_MARKER='"type":"tool_result"'

if [[ ! -f "$META" ]]; then
  echo "Error: scenarios/$SCENARIO/meta.json not found." >&2
  exit 1
fi

if [[ ! -d "$DIR" ]]; then
  echo "Error: $DIR does not exist. Run setup.sh $SCENARIO first." >&2
  exit 1
fi

# Load task prompt from SSOT: scenarios/<X>/meta.json
TASK_PROMPT=$(jq -r '.task_prompt' "$META")

# Build the craft-pack system prompt
# Override with BAR_CMD=/path/to/bar to use a dev build
BAR_CMD="${BAR_CMD:-bar}"
SYSTEM_PROMPT="$("$BAR_CMD" build make witness ground gate falsify atomic 2>/dev/null)"
if [[ -z "$SYSTEM_PROMPT" ]]; then
  echo "Error: $BAR_CMD build make witness ground gate falsify atomic produced no output." >&2
  exit 1
fi

FULL_PROMPT="Working directory: $DIR

$TASK_PROMPT

Use the craft pack discipline (witness ground gate falsify atomic) as defined in your system prompt."

echo "=== Running haiku agent for scenario $SCENARIO ==="
echo "Model: claude-haiku-4-5"
echo "Bar binary: $BAR_CMD"
echo "Working directory: $DIR"
echo "Task: $TASK_PROMPT"
echo ""

cd "$DIR"
claude -p "$FULL_PROMPT" \
  --system-prompt "$SYSTEM_PROMPT" \
  --model claude-haiku-4-5 \
  --allowedTools "Bash,Read,Edit,Write" \
  --permission-mode bypassPermissions \
  --output-format stream-json \
  --verbose \
  > "$TRANSCRIPT" 2>&1

echo ""
echo "=== Gate check: expecting tool_result in transcript ==="
if grep -q "$TOOL_RESULT_MARKER" "$TRANSCRIPT"; then
  TOOL_RESULT_COUNT=$(grep -c "$TOOL_RESULT_MARKER" "$TRANSCRIPT" || true)
  echo "PASS: transcript contains $TOOL_RESULT_COUNT tool_result block(s)"
else
  echo "FAIL: transcript contains no tool_result blocks — agent made no tool calls" >&2
  echo "Transcript saved to: $TRANSCRIPT" >&2
  exit 1
fi

echo ""
echo "Transcript saved to: $TRANSCRIPT"
echo ""
echo "=== Final agent output ==="
cat "$TRANSCRIPT" \
  | python3 -c "
import sys, json
for line in sys.stdin:
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
