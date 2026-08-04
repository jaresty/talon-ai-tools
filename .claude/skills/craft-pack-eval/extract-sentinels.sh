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
if [[ ! -f "$TRANSCRIPT" ]]; then
  echo "Error: $TRANSCRIPT not found. Run setup.sh and run-agent.sh first." >&2
  exit 1
fi

echo "=== Sentinel extraction: scenario $SCENARIO ==="
echo ""

# Ground properties block — the header line (allow optional markdown: ## or **)
echo "--- Ground properties block ---"
grep -in "ground properties:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# All property [N]: lines (allow optional ** bold markers)
echo "--- Properties ---"
grep -in "\bproperty \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Interpretation line
echo "--- Interpretation ---"
grep -in "interpretation:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Observing lines
echo "--- Observing ---"
grep -in "observing: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Failure lines
echo "--- Failure ---"
grep -in "failure: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Blind-spot lines
echo "--- Blind-spot ---"
grep -in "blind-spot: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Unobservable lines
echo "--- Unobservable ---"
grep -in "unobservable: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Coverage (complete or gap both valid resolutions)
echo "--- Coverage ---"
grep -in "coverage: \(complete\|gap\)" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Summary counts — use python3 to avoid grep -c platform differences
echo "=== Summary ==="
PROPS=$(python3 -c "import re,sys; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'^\**property \[', l.strip())))" 2>/dev/null || echo 0)
OBS=$(python3 -c "import re,sys; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'Observing: property \[', l, re.I)))" 2>/dev/null || echo 0)
FAIL=$(python3 -c "import re,sys; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'Failure: property \[', l, re.I)))" 2>/dev/null || echo 0)
BLIND=$(python3 -c "import re,sys; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'Blind-spot: property \[', l, re.I)))" 2>/dev/null || echo 0)
UNOBS=$(python3 -c "import re,sys; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'Unobservable: property \[', l, re.I)))" 2>/dev/null || echo 0)
COV=$(python3 -c "import re,sys; lines=open('$TRANSCRIPT').readlines(); print(sum(1 for l in lines if re.search(r'Coverage: (complete|gap)', l, re.I)))" 2>/dev/null || echo 0)

echo "Properties defined:     $PROPS"
echo "Observing: lines:       $OBS"
echo "Failure: lines:         $FAIL"
echo "Blind-spot: lines:      $BLIND"
echo "Unobservable: lines:    $UNOBS"
echo "Coverage: lines:        $COV"
echo ""

# Basic compliance check
RESOLVED=$((BLIND + UNOBS))
if [[ "$PROPS" -gt 0 && "$OBS" -ge "$PROPS" && "$RESOLVED" -ge "$PROPS" && "$COV" -ge 1 ]]; then
  echo "PASS: sentinel counts consistent (properties=$PROPS, observing=$OBS, resolved=$RESOLVED, coverage=$COV)"
else
  echo "FAIL: sentinel gap detected"
  [[ "$OBS" -lt "$PROPS" ]] && echo "  - Missing Observing: lines ($OBS of $PROPS)"
  [[ "$RESOLVED" -lt "$PROPS" ]] && echo "  - Missing Blind-spot:/Unobservable: lines ($RESOLVED of $PROPS)"
  [[ "$COV" -lt 1 ]] && echo "  - Missing Coverage: line"
fi
