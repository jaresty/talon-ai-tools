#!/usr/bin/env bash
# extract-sentinels.sh — extract three-gate falsify sentinel lines from a transcript
# Usage: bash extract-sentinels.sh <scenario-letter>
# Output: sentinel lines in order, with line numbers, to stdout
#
# THREE-GATE CONTRACT (post-redesign 2026-08-15):
#   falsify is two retrospective gates over established guards, no forced ordering,
#   no per-property Observing:/Assertion inventory:/witness bookkeeping.
#   Gate 1 (minimization): Overreach: found / Overreach: not found
#   Gate 3 (observed failure): Failure: assertion "..." per executable assertion,
#     or Unobservable: assertion "..." — structural
#   Gate 2 (composition, ground+falsify): coverage against Retained properties:,
#     terminating on a no-change pass; gaps emit Audit: implementation gap and re-enter Ground.
#   Coverage: complete is valid only after Audit: implementation complete.
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

echo "=== Sentinel extraction (three-gate falsify): scenario $SCENARIO ==="
echo ""

# Ground properties block
echo "--- Ground properties block ---"
grep -in "ground properties:" "$TRANSCRIPT" || echo "(absent)"
echo ""

echo "--- Retained properties ---"
grep -in "retained properties:" "$TRANSCRIPT" || echo "(absent)"
echo ""

echo "--- § ground complete ---"
grep -in "ground complete" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Gap observation (opener)
echo "--- Observing gap ---"
grep -in "observing gap:" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Gate 3: per-assertion failure observations (watch-item 1: did every guard fire?)
echo "--- Gate 3: Failure: assertion ---"
grep -in "failure: assertion" "$TRANSCRIPT" || echo "(absent)"
echo ""

echo "--- Gate 3: Unobservable: assertion — structural ---"
grep -in "unobservable: assertion" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Gate 1: minimization / overreach (watch-item 2: did impl do more than guards cover?)
echo "--- Gate 1: Overreach: found ---"
grep -in "overreach: found" "$TRANSCRIPT" || echo "(absent)"
echo ""

echo "--- Gate 1: Overreach: not found ---"
grep -in "overreach: not found" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Gate 2 (composition) + audit
echo "--- Audit: implementation gap ---"
grep -in "audit: implementation gap" "$TRANSCRIPT" || echo "(absent)"
echo ""

echo "--- Audit: implementation complete ---"
grep -in "audit: implementation complete" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Coverage (watch-item 3: did all properties get met?)
echo "--- Coverage ---"
grep -in "coverage: complete" "$TRANSCRIPT" || echo "(absent)"
echo ""

# Summary counts
echo "=== Summary ==="
count() { python3 -c "import re,sys; print(sum(1 for l in open('$TRANSCRIPT') if re.search(r'$1', l, re.I)))" 2>/dev/null || echo 0; }

RETAINED=$(count 'retained properties:')
GROUNDCMP=$(count 'ground complete')
FAILA=$(count 'failure: assertion')
UNOBSA=$(count 'unobservable: assertion')
OVERF=$(count 'overreach: found')
OVERNF=$(count 'overreach: not found')
SURPLUS=$(count 'audit: implementation surplus')
# P10/P11: enumerated 'Assertion:' lines and their property tags '[P N.m]'
ASSERT_LINES=$(count "^\s*\**assertion(\s*\[|:)")
ASSERT_TAGGED=$(count "assertion\s*\[p\s*\d")
AUDITGAP=$(count 'audit: implementation gap')
AUDITCMP=$(count 'audit: implementation complete')
COV=$(count 'coverage: complete')

echo "Retained properties: lines:      $RETAINED"
echo "§ ground complete:               $GROUNDCMP"
echo "Gate 3 Failure: assertion:       $FAILA"
echo "Gate 3 Unobservable: assertion:  $UNOBSA"
echo "Gate 1 Overreach: found:         $OVERF"
echo "Gate 1 Overreach: not found:     $OVERNF"
echo "Audit: implementation gap:       $AUDITGAP"
echo "Audit: implementation surplus:   $SURPLUS  (informational — Gate 2 'more' direction)"
echo "Enumerated Assertion: lines:     $ASSERT_LINES  (P10 — visible per-assertion enumeration)"
echo "Property-tagged assertions:      $ASSERT_TAGGED  (P11 — assertion↔property map)"
echo "Audit: implementation complete:  $AUDITCMP"
echo "Coverage: complete:              $COV"
echo ""

# Per-assertion discrimination (allow-list criterion, P8).
# An assertion is validly witnessed only when its observed failure cause is
# ATTRIBUTABLE TO IT ALONE — i.e. distinct from every other assertion's cause.
# We compute this positively: extract the quoted observed-cause from each
# 'Failure: assertion "<assertion>" — "<cause>"' line and count how many causes
# are unique (appear exactly once). A shared cause (e.g. one compile error
# 'undefined: parseToken' reused across N assertions) collapses to a single
# unique cause and therefore witnesses at most one assertion, not N.
read -r FAIL_TOTAL DISTINCT_CAUSES PASS_LABELED <<< "$(python3 -c "
import re
from collections import Counter
# P17: a cause that indicates success does not count as a Failure.
SUCCESS = re.compile(r'\b(ok|pass|passed|passes|passing|succeed|succeeded|success)\b', re.I)
causes=[]; pass_labeled=0
for l in open('$TRANSCRIPT'):
    # accept an optional property tag '[P1.1]' between 'assertion' and the quoted
    # assertion text, e.g. 'Failure: assertion [P1.1] — \"...\"' or 'Failure: assertion \"...\" — \"...\"'
    m=re.search(r'failure:\s*assertion\s*(?:\[[^\]]*\]\s*)?[—-]*\s*.*?[—-]+\s*[\"\x60](.*?)[\"\x60]', l, re.I)
    if m:
        cause=m.group(1).strip()
        if SUCCESS.search(cause):
            pass_labeled+=1          # P17: pass-labeled-as-Failure — does not count
        else:
            causes.append(cause)
c=Counter(causes)
distinct_attributable=sum(1 for cause,n in c.items() if n==1)
print(len(causes), distinct_attributable, pass_labeled)
" 2>/dev/null || echo "0 0 0")"

# P17 witness line: 'witness: ... present and executes ... property ... violated ...'
# The agent may name the actual symbol ('function foo is present and executes') rather
# than the literal word 'symbol', so match on the present-and-executes + violated shape.
WITNESS_LINES=$(count 'witness:.*(present and executes|symbol present)')

echo "Gate 3 Failure: assertion (parsed, pass-labeled excluded): $FAIL_TOTAL"
echo "  pass-labeled-as-Failure (P17, rejected): $PASS_LABELED"
echo "  witness-validity lines (P17): $WITNESS_LINES"
echo "Gate 3 distinct-cause (attributable): $DISTINCT_CAUSES"
echo ""

# Compliance check — three-gate contract.
# Watch-item 1 (every guard DISTINGUISHED, not merely fired): every parsed
#   Failure: assertion must have a cause attributable to it alone — DISTINCT_CAUSES
#   must equal FAIL_TOTAL (no shared cause). Unobservable: structural assertions
#   are exempt (their justification is the structural subject, not a failure state).
#   At least one Gate-3 observation must exist overall.
# Watch-item 2 (no uncovered overreach): Gate 1 reached 'Overreach: not found'.
# Watch-item 3 (all properties met): Coverage: complete present, preceded by
#   Audit: implementation complete.
OBSERVED=$((FAILA + UNOBSA))
# Discrimination is judged on PARSED failures. There is no vacuous-pass escape:
# a run must produce at least one parseable, distinctly-attributed Failure
# observation (or be an all-structural-Unobservable run). If raw Failure: lines
# exist but none parse (FAIL_TOTAL=0 while FAILA>0), the failures are malformed —
# that is a FAIL, not a pass. Structural Unobservable-only runs (UNOBSA>0, FAILA=0)
# are the only way to have zero parsed failures and still pass.
DISCRIMINATED=0
if [[ "$FAIL_TOTAL" -ge 1 && "$DISTINCT_CAUSES" -eq "$FAIL_TOTAL" ]]; then
  DISCRIMINATED=1               # every parsed failure attributable to one assertion
elif [[ "$FAILA" -eq 0 && "$UNOBSA" -ge 1 ]]; then
  DISCRIMINATED=1               # all-structural-Unobservable run — no failures to discriminate
fi
# P17 witness-validity gate: every parsed Failure must carry a witness line, and no
# pass-labeled failure may be present. Witnessed iff a witness line exists per parsed
# Failure (>= FAIL_TOTAL) and no pass-labeled Failure was found.
WITNESSED=0
if [[ "$FAIL_TOTAL" -eq 0 || ( "$WITNESS_LINES" -ge "$FAIL_TOTAL" && "$PASS_LABELED" -eq 0 ) ]]; then
  WITNESSED=1
fi
if [[ "$OBSERVED" -ge 1 \
  && "$DISCRIMINATED" -eq 1 \
  && "$WITNESSED" -eq 1 \
  && "$OVERNF" -ge 1 \
  && "$AUDITCMP" -ge 1 \
  && "$COV" -ge 1 ]]; then
  echo "PASS: three-gate sentinels consistent (observed=$OBSERVED, distinct-cause=$DISTINCT_CAUSES/$FAIL_TOTAL, witness=$WITNESS_LINES, Gate 1 clean, audit complete, coverage=$COV)"
else
  echo "FAIL: sentinel gap detected"
  [[ "$OBSERVED" -lt 1 ]]  && echo "  - Watch-item 1: no Gate-3 observation (Failure:/Unobservable: assertion) — no guard observed firing"
  [[ "$WITNESSED" -eq 0 && "$PASS_LABELED" -gt 0 ]] && echo "  - P17: $PASS_LABELED 'Failure:' line(s) whose cause indicates success (ok/PASS/passed) — a pass does not witness absence"
  [[ "$WITNESSED" -eq 0 && "$WITNESS_LINES" -lt "$FAIL_TOTAL" ]] && echo "  - P17: only $WITNESS_LINES witness-validity line(s) for $FAIL_TOTAL Failure(s) — each Failure must carry a checkable witness line"
  [[ "$DISCRIMINATED" -eq 0 && "$FAILA" -gt 0 && "$FAIL_TOTAL" -eq 0 ]] && echo "  - Watch-item 1: $FAILA raw 'Failure:' line(s) present but none parse as 'Failure: assertion [tag] — \"cause\"' — malformed/narrated failures do not witness discrimination"
  [[ "$DISCRIMINATED" -eq 0 && "$FAIL_TOTAL" -ge 1 ]] && echo "  - Watch-item 1: assertions not discriminated — only $DISTINCT_CAUSES of $FAIL_TOTAL failure causes are attributable to a single assertion; a shared cause (e.g. one compile error across all) does not witness each property"
  [[ "$OVERNF" -lt 1 ]]    && echo "  - Watch-item 2: no 'Overreach: not found' — Gate 1 minimization never reached a clean verdict"
  [[ "$OVERF" -gt 0 && "$OVERNF" -lt 1 ]] && echo "  - Watch-item 2: 'Overreach: found' emitted but never resolved to 'Overreach: not found'"
  [[ "$AUDITCMP" -lt 1 ]]  && echo "  - Watch-item 3: missing 'Audit: implementation complete' (required before Coverage: complete)"
  [[ "$COV" -lt 1 ]]       && echo "  - Watch-item 3: missing 'Coverage: complete'"
fi
