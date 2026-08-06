#!/usr/bin/env bash
# extract-sentinels.sh — extract ground+falsify sentinel lines from a transcript
# Usage: bash extract-sentinels.sh <scenario-letter>
# Output: sentinel lines in order, with line numbers, to stdout
set -euo pipefail

SCENARIO="${1:-}"
if [[ -z "$SCENARIO" ]]; then
  echo "Usage: extract-sentinels.sh <A|B|C|...>" >&2
  exit 1
fi

TRANSCRIPT="/tmp/haiku-test-${SCENARIO}/assistant-text.md"
JSONL="/tmp/haiku-test-${SCENARIO}/transcript.jsonl"
if [[ ! -f "$TRANSCRIPT" ]]; then
  if [[ -f "$JSONL" ]]; then
    python3 -c "
import json, sys
lines = []
for line in open('$JSONL'):
    obj = json.loads(line)
    if obj.get('type') == 'assistant':
        for block in obj.get('message', {}).get('content', []):
            if block.get('type') == 'text':
                lines.append(block['text'])
print('\n'.join(lines))
" > "$TRANSCRIPT"
  else
    echo "Error: $TRANSCRIPT not found. Run setup.sh and run-agent.sh first." >&2
    exit 1
  fi
fi

echo "=== Sentinel extraction: scenario $SCENARIO ==="
echo ""

# Ground properties block
echo "--- Ground properties block ---"
grep -in "ground properties:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# All property [N]: lines
echo "--- Properties ---"
grep -in "\bproperty \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Interpretation line
echo "--- Interpretation ---"
grep -in "interpretation:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Step (1): Observing
echo "--- (1) Observing ---"
grep -in "observing: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Step (2): Assertion inventory
echo "--- (2) Assertion inventory ---"
grep -in "property \[.*\] assertion \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Step (2): Assertion inventory complete
echo "--- (2) Assertion inventory ---"
grep -in "assertion inventory:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Step (2): Quoted test
echo "--- (2) Quoted test ---"
grep -in "quoted test:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Step (3): Test blind-spot
echo "--- (3) Test blind-spot ---"
grep -in "test blind-spot:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Step (4): Failure or Unobservable
echo "--- (4) Failure ---"
grep -in "failure: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""
echo "--- (4) Unobservable ---"
grep -in "unobservable: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Step (4): Assertion witnesses
echo "--- (4) Assertion witnesses ---"
grep -in "assertion witnesses:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Step (5): Quoted implementation
echo "--- (5) Quoted implementation ---"
grep -in "quoted implementation:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Step (6): Implementation overreach
echo "--- (6) Implementation overreach ---"
grep -in "implementation overreach:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Coverage
echo "--- Coverage ---"
grep -in "coverage: \(complete\|gap\)" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Summary counts
echo "=== Summary ==="
PROPS=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^[-\s]*\*{0,2}property \[\d+\w*\]:', l.strip(), re.I)))" 2>/dev/null || echo 0)
OBS=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^#{0,6}\s*\*{0,2}Observing:?\*{0,2}:? property \[', l, re.I)))" 2>/dev/null || echo 0)
QTST=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^\*{0,2}Quoted test:?\*{0,2}:?', l, re.I)))" 2>/dev/null || echo 0)
TBSP=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^\*{0,2}Test blind-spot:?\*{0,2}:?', l, re.I)))" 2>/dev/null || echo 0)
FAIL=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^\*{0,2}Failure:?\*{0,2}:? property \[', l, re.I)))" 2>/dev/null || echo 0)
UNOBS=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^\*{0,2}Unobservable:?\*{0,2}:? property \[', l, re.I)))" 2>/dev/null || echo 0)
QIMP=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^\*{0,2}Quoted implementation:?\*{0,2}:?', l, re.I)))" 2>/dev/null || echo 0)
IBSP=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^\*{0,2}Implementation overreach:?\*{0,2}:?', l, re.I)))" 2>/dev/null || echo 0)
COV=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^#{0,6}\s*\*{0,2}Coverage:?\*{0,2}:? (complete|gap)', l, re.I)))" 2>/dev/null || echo 0)
AINV=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'assertion inventory: complete', l, re.I)))" 2>/dev/null || echo 0)
AWIT=$(python3 -c "import re; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'assertion witnesses: complete', l, re.I)))" 2>/dev/null || echo 0)

echo "Properties defined:              $PROPS"
echo "(1) Observing: lines:            $OBS"
echo "(2) Assertion inventory complete: $AINV"
echo "(2) Quoted test: lines:          $QTST"
echo "(3) Test blind-spot: lines:      $TBSP"
echo "(4) Failure: lines:              $FAIL"
echo "(4) Unobservable: lines:         $UNOBS"
echo "(4) Assertion witnesses complete: $AWIT"
echo "(5) Quoted implementation: lines: $QIMP"
echo "(6) Implementation overreach:    $IBSP"
echo "Coverage: lines:                 $COV"
echo ""

# Compliance check — use Observing: count as cycle denominator.
# Observing: is emitted exactly once per retained property and cannot be inflated
# by guard iteration (a property may have multiple Quoted test: lines when the
# blind-spot check triggers guard revision). Quoted test count must be >= Observing
# count (each property needs at least one guard) but may exceed it.
# Assertion inventory: complete must precede each Quoted test: (checked by count parity).
# Assertion witnesses: complete must follow each Failure:/Unobservable: (checked by count parity).
CYCLES="$OBS"
RESOLVED=$((FAIL + UNOBS))
if [[ "$CYCLES" -gt 0 \
  && "$AINV" -ge "$CYCLES" \
  && "$QTST" -ge "$CYCLES" \
  && "$TBSP" -ge "$CYCLES" \
  && "$RESOLVED" -ge "$CYCLES" \
  && "$AWIT" -ge "$RESOLVED" \
  && "$QIMP" -ge "$CYCLES" \
  && "$IBSP" -ge "$CYCLES" \
  && "$COV" -ge 1 ]]; then
  echo "PASS: sentinel counts consistent (cycles=$CYCLES, all 6 steps complete, coverage=$COV)"
else
  echo "FAIL: sentinel gap detected"
  [[ "$CYCLES" -eq 0 ]]           && echo "  - No Observing: lines found — no cycles completed"
  [[ "$AINV" -lt "$CYCLES" ]]     && echo "  - (2) Missing Assertion inventory: complete lines ($AINV of $CYCLES cycles)"
  [[ "$QTST" -lt "$CYCLES" ]]     && echo "  - (2) Missing Quoted test: lines ($QTST of $CYCLES cycles)"
  [[ "$TBSP" -lt "$CYCLES" ]]     && echo "  - (3) Missing Test blind-spot: lines ($TBSP of $CYCLES cycles)"
  [[ "$RESOLVED" -lt "$CYCLES" ]] && echo "  - (4) Missing Failure:/Unobservable: lines ($RESOLVED of $CYCLES cycles)"
  [[ "$AWIT" -lt "$RESOLVED" ]]   && echo "  - (4) Missing Assertion witnesses: complete lines ($AWIT of $RESOLVED resolved cycles)"
  [[ "$QIMP" -lt "$CYCLES" ]]     && echo "  - (5) Missing Quoted implementation: lines ($QIMP of $CYCLES cycles)"
  [[ "$IBSP" -lt "$CYCLES" ]]     && echo "  - (6) Missing Implementation overreach: lines ($IBSP of $CYCLES cycles)"
  [[ "$COV" -lt 1 ]]              && echo "  - Missing Coverage: sentinel"
fi
