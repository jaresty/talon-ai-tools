#!/usr/bin/env bash
# Emergent requirement test for a method token pair (ADR-0227 Loop-C).
# Uses bar's comparison feature to render each variant side-by-side.
#
# Usage: scripts/composition-check.sh <tokenA> <tokenB> [task]
# Example: scripts/composition-check.sh ground formal probe
#
# Output: three sections —
#   1. method=A variant (CONSTRAINTS for A alone)
#   2. method=B variant (CONSTRAINTS for B alone)
#   3. method=A+B combined prompt (full co-presence output)
#
# Emergent requirement test: does the A+B combined output contain a behavioral
# requirement absent from both the A variant and the B variant?

set -euo pipefail

A="${1:?Usage: composition-check.sh <tokenA> <tokenB> [task]}"
B="${2:?Usage: composition-check.sh <tokenA> <tokenB> [task]}"
TASK="${3:-probe}"

echo "=== Composition check: $A + $B (task=$TASK) ==="
echo ""
echo "--- Variants (A alone vs B alone): ---"
bar build diff "method=$A,$B" 2>&1
echo ""
echo "--- Combined (A+B co-presence): ---"
bar build "$TASK" "$A" "$B" 2>&1
echo ""
echo "=== Emergent requirement test ==="
echo "Does the combined output contain a behavioral requirement absent from both variants above?"
echo "If yes: draft composition prose and add to lib/compositionConfig.py"
echo "If no:  mark pair as 'additive' in docs/composition-candidates.md"
