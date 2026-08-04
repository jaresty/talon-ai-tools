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

# Ground properties block — the header line
echo "--- Ground properties block ---"
grep -n "^Ground properties:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# All property [N]: lines
echo "--- Properties ---"
grep -n "^property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Interpretation line
echo "--- Interpretation ---"
grep -n "^Interpretation:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Observing lines
echo "--- Observing ---"
grep -n "^Observing: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Failure lines
echo "--- Failure ---"
grep -n "^Failure: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Blind-spot lines
echo "--- Blind-spot ---"
grep -n "^Blind-spot: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Unobservable lines
echo "--- Unobservable ---"
grep -n "^Unobservable: property \[" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Coverage
echo "--- Coverage ---"
grep -n "^Coverage:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Summary counts
echo "=== Summary ==="
PROPS=$(grep -c "^property \[" "$TRANSCRIPT" 2>/dev/null || echo 0)
OBS=$(grep -c "^Observing: property \[" "$TRANSCRIPT" 2>/dev/null || echo 0)
FAIL=$(grep -c "^Failure: property \[" "$TRANSCRIPT" 2>/dev/null || echo 0)
BLIND=$(grep -c "^Blind-spot: property \[" "$TRANSCRIPT" 2>/dev/null || echo 0)
UNOBS=$(grep -c "^Unobservable: property \[" "$TRANSCRIPT" 2>/dev/null || echo 0)
COV=$(grep -c "^Coverage:" "$TRANSCRIPT" 2>/dev/null || echo 0)

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
