#!/usr/bin/env bash
# Emergent requirement test for a method token pair (ADR-0227 Loop-C).
# Usage: scripts/composition-check.sh <tokenA> <tokenB> [task]
# Example: scripts/composition-check.sh sim check show

set -euo pipefail

A="${1:?Usage: composition-check.sh <tokenA> <tokenB> [task]}"
B="${2:?Usage: composition-check.sh <tokenA> <tokenB> [task]}"
TASK="${3:-show}"

extract_constraints() {
    awk '/^=== CONSTRAINTS/{p=1; next} p && /^=== [A-Z]/{exit} p{print}'
}

echo "=== Emergent requirement test: $A + $B (task=$TASK) ==="

CONSTRAINTS_A=$(bar build "$TASK" "$A" 2>&1 | extract_constraints)
CONSTRAINTS_B=$(bar build "$TASK" "$B" 2>&1 | extract_constraints)
CONSTRAINTS_AB=$(bar build "$TASK" "$A" "$B" 2>&1 | extract_constraints)

echo ""
echo "--- Lines unique to A+B (not in A-only or B-only): ---"
comm -23 \
    <(echo "$CONSTRAINTS_AB" | sort) \
    <({ echo "$CONSTRAINTS_A"; echo "$CONSTRAINTS_B"; } | sort -u)

echo ""
echo "(If empty: behavior is additive — no composition warranted.)"
