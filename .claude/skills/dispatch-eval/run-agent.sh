#!/usr/bin/env bash
# dispatch-eval run-agent.sh — invoke haiku agent for a dispatch compliance scenario
# Usage: bash run-agent.sh <scenario-letter>
set -euo pipefail

SCENARIO="${1:-}"
if [[ -z "$SCENARIO" ]]; then
  echo "Usage: run-agent.sh <M|N|O|P|Q|R>" >&2
  exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
META="$SKILL_DIR/scenarios/$SCENARIO/meta.json"
DIR="/tmp/dispatch-test-${SCENARIO}"
TRANSCRIPT="$DIR/transcript.jsonl"

if [[ ! -f "$META" ]]; then
  echo "Error: scenarios/$SCENARIO/meta.json not found." >&2
  exit 1
fi

if [[ ! -d "$DIR" ]]; then
  echo "Error: $DIR does not exist. Run setup.sh $SCENARIO first." >&2
  exit 1
fi

TASK_PROMPT=$(jq -r '.task_prompt' "$META")
CRITERION=$(jq -r '.target_criteria' "$META")
EVAL_GATE=$(jq -r '.eval_gate' "$META")
SEQUENCE_NAME=$(jq -r '.sequence_name' "$META")
INNER_SEQUENCE=$(jq -r '.inner_sequence // ""' "$META")
MAX_TURNS=$(jq -r '.max_turns // ""' "$META")
MOCK_AGENTS=$(jq -r '.mock_agents // false' "$META")

# Build the system prompt — lightweight for mock evals, full craft pack otherwise
BAR_CMD="${BAR_CMD:-bar}"
if [[ "$MOCK_AGENTS" == "true" ]]; then
  SYSTEM_PROMPT="You are a protocol compliance agent. Use bar help llm --section sequences to load the dispatch protocol, then follow it exactly."
else
  SYSTEM_PROMPT="$("$BAR_CMD" build make witness ground gate falsify atomic 2>/dev/null)"
  if [[ -z "$SYSTEM_PROMPT" ]]; then
    echo "Error: $BAR_CMD build produced no output." >&2
    exit 1
  fi
fi

# If inner_sequence is set, extract the inner step spec dynamically from bar sequence show
# and substitute it for the {{INNER_STEP_SPEC}} sentinel in task_prompt.
if [[ -n "$INNER_SEQUENCE" ]]; then
  INNER_SPEC="$("$BAR_CMD" sequence show "$INNER_SEQUENCE" 2>/dev/null \
    | awk '/inner mode:/{found=1} found && /^  Step [0-9]/{exit} found{print}' \
    || echo "")"
  TASK_PROMPT="${TASK_PROMPT/\{\{INNER_STEP_SPEC\}\}/$INNER_SPEC}"
fi

# Append the sequence definition so the agent knows exactly what to run
SEQUENCE_DEF=""
if [[ -n "$SEQUENCE_NAME" ]]; then
  SEQUENCE_DEF="$("$BAR_CMD" sequence show "$SEQUENCE_NAME" 2>/dev/null || echo "")"
fi

FULL_PROMPT="Working directory: $DIR

$TASK_PROMPT"

if [[ -n "$SEQUENCE_DEF" ]]; then
  FULL_PROMPT="$FULL_PROMPT

You are executing a bar sequence. The sequence definition is:

$SEQUENCE_DEF

Follow the dispatch protocol exactly as specified in the sequence definition above."
fi

if [[ "$MOCK_AGENTS" != "true" ]]; then
  FULL_PROMPT="$FULL_PROMPT

Use the craft pack discipline (witness ground gate falsify atomic) as defined in your system prompt."
fi

# Mock agent mode: Agent tool unavailable; output <agent-call> blocks instead
ALLOWED_TOOLS="Bash,Read,Edit,Write,Agent"
if [[ "$MOCK_AGENTS" == "true" ]]; then
  ALLOWED_TOOLS="Bash,Read,Edit,Write"
  FULL_PROMPT="$FULL_PROMPT

EVAL NOTE: The Agent tool is not available in this eval. When the protocol requires spawning Agent tool calls, output one <agent-call> block per frame instead. The <prompt> inside each block must be exactly the prompt you would have passed to the Agent tool — the verbatim system prompt for that subagent as determined by the sequence protocol. Do NOT write any files to disk. Format:
<agent-call>
<prompt>exact prompt you would pass to this Agent tool call</prompt>
</agent-call>
Output one block per frame. The eval checks for these blocks as evidence of correct dispatch."
fi

echo "=== Running haiku agent for scenario $SCENARIO ==="
echo "Model: claude-haiku-4-5"
echo "Bar binary: $BAR_CMD"
echo "Working directory: $DIR"
echo "Target criterion: $CRITERION"
echo "Sequence: $SEQUENCE_NAME"
echo "Mock agents: $MOCK_AGENTS"
echo "Task: $TASK_PROMPT"
echo ""

cd "$DIR"
claude -p "$FULL_PROMPT" \
  --system-prompt "$SYSTEM_PROMPT" \
  --model claude-haiku-4-5 \
  --allowedTools "$ALLOWED_TOOLS" \
  --permission-mode bypassPermissions \
  --output-format stream-json \
  --verbose \
  > "$TRANSCRIPT" 2>&1

echo ""
echo "=== Eval gate check: criterion $CRITERION ==="
echo "Gate: $EVAL_GATE"
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
echo ""
echo "=== Manual scoring required ==="
echo "Criterion $CRITERION eval gate: $EVAL_GATE"
echo "Review transcript at: $TRANSCRIPT"
echo "Score PASS or FAIL based on the rubric in ADR-0240."
