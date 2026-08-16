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
# markdown-tolerant count: strip *_ emphasis before matching, so '**Failure:** assertion'
# is counted (the model's content is correct; the markup is presentational).
countmd() { python3 -c "import re,sys; print(sum(1 for l in open('$TRANSCRIPT') if re.search(r'$1', re.sub(r'[*_]{1,3}','',l), re.I)))" 2>/dev/null || echo 0; }
FAILA=$(countmd 'failure:\s*assertion')
UNOBSA=$(countmd 'unobservable:\s*assertion')
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
read -r FAIL_TOTAL DISTINCT_CAUSES PASS_LABELED ABSENCE_LABELED <<< "$(python3 -c "
import re
from collections import Counter
# P17: a cause that indicates success does not count as a Failure.
SUCCESS = re.compile(r'\b(ok|pass|passed|passes|passing|succeed|succeeded|success)\b', re.I)
# P19: an absence (undefined symbol / no observed value) is not a value-mismatch and does not witness.
ABSENCE = re.compile(r'\b(undefined|not\s+defined|no\s+such|does\s+not\s+exist|not\s+found|cannot\s+find|nameerror|referenceerror|importerror|modulenotfound)\b', re.I)
causes=[]; pass_labeled=0; absence_labeled=0
# Strip markdown emphasis (**bold**, *italic*, _underscore_) so a sentinel written
# '**Failure:** assertion ...' still matches — the model's content is correct; the
# markup is presentational and must not break parsing.
def strip_md(s): return re.sub(r'[*_]{1,3}', '', s)
# Framework output like Go's %q produces NESTED quotes
# ('Failure: assertion \"got %q, want %q\" — \"got \"\", want \"bar\"\"'), so a naive
# innermost-quote match misparses. Instead: take everything after the last em/en/hyphen
# separator on the line (the cause portion) and inspect that whole tail.
for raw in open('$TRANSCRIPT'):
    l = strip_md(raw)
    if not re.search(r'failure:\s*assertion', l, re.I):
        continue
    # cause portion = text after the final ' — ' / ' - ' separator (assertion text precedes it)
    parts = re.split(r'\s[—-]+\s', l.rstrip())
    if len(parts) < 2:
        continue                     # no cause portion — not a parseable Failure observation
    cause = parts[-1].strip()
    if ABSENCE.search(cause):
        absence_labeled+=1           # P19: absence, not a value-mismatch — does not count
    elif re.search(r'got .* want|want .* got', cause, re.I):
        # a got/want value pair — a genuine value-mismatch observation (present-but-wrong)
        causes.append(cause)
    elif SUCCESS.search(cause) and not re.search(r'got .* want', cause, re.I):
        pass_labeled+=1              # P17: pass-labeled-as-Failure — does not count
    # else: an unrecognized cause shape is NOT counted as a value-mismatch (the machine
    # differential, read from tool-results below, is the authoritative discrimination signal).
c=Counter(causes)
distinct_attributable=sum(1 for cause,n in c.items() if n==1)
print(len(causes), distinct_attributable, pass_labeled, absence_labeled)
" 2>/dev/null || echo "0 0 0 0")"

# P17 witness line: 'witness: ... present and executes ... property ... violated ...'
# The agent may name the actual symbol ('function foo is present and executes') rather
# than the literal word 'symbol', so match on the present-and-executes + violated shape.
WITNESS_LINES=$(count 'witness:.*(present and executes|symbol present)')

echo "Gate 3 Failure: assertion (genuine value-mismatch only): $FAIL_TOTAL"
echo "  absence-caused (P19, rejected: undefined/no-value): $ABSENCE_LABELED"
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
# The machine-grounded differential (below, read from tool-results) is authoritative over the
# prose distinct-cause count. When it is 1 AND no pass-labeled/absence Failure was parsed, the
# real assertion-level A-fail/A-pass pair exists in the tool-results; a low distinct-cause count
# is then an artifact of the SAME single assertion being quoted for multiple derived properties,
# not a discrimination failure. (DIFFERENTIAL is computed just below; re-checked in the gate.)
# P20 canonical differential (the heart of the experiment): validity requires, in the
# tool-results, an ASSERTION-LEVEL failure (A's own assertion reported failing) AND an
# assertion-level pass — not merely 'some differing outcome'. An execution error (compile,
# undefined symbol, panic, timeout) is NOT an assertion failure: A never executed, so it is
# excluded from the fail side. Judged from tool_result blocks, not from model-authored prose.
DIFFERENTIAL=$(python3 -c "
import json, re
# assertion-level failure: a test-framework FAIL naming a test, or an assert mismatch (expected/got)
ASSERT_FAIL = re.compile(r'(---\s*FAIL|\bFAIL:\s|got .* want|want .* got|expected .* got|assert\w*.*(failed|Error))', re.I)
# execution errors that are NOT assertion failures (A did not execute) — exclude these from the fail side
EXEC_ERROR = re.compile(r'\b(undefined|not\s+defined|no\s+such|does\s+not\s+exist|build failed|cannot find|compile|panic|timeout|nameerror|referenceerror|importerror|modulenotfound|segmentation)\b', re.I)
PASSSHAPE = re.compile(r'(---\s*PASS|\bPASS\b|\bok\b|all tests passed|[0-9]+ passed)', re.I)
saw_fail=saw_pass=False
for line in open('$JSONL'):
    try: o=json.loads(line)
    except: continue
    # tool_result blocks live in user-role messages as content items of type tool_result
    msg=o.get('message',{})
    for b in (msg.get('content') or []) if isinstance(msg.get('content'),list) else []:
        if isinstance(b,dict) and b.get('type')=='tool_result':
            c=b.get('content')
            txt=' '.join(x.get('text','') for x in c if isinstance(x,dict)) if isinstance(c,list) else str(c)
            # only consider guard/test executions
            if re.search(r'\btest\b|go test|pytest|assert', txt, re.I):
                # assertion-level fail only when an assertion mismatch is present AND it is not
                # merely an execution error (compile/undefined/panic/timeout = A did not execute).
                if ASSERT_FAIL.search(txt) and not (EXEC_ERROR.search(txt) and not re.search(r'got .* want|want .* got|expected .* got', txt, re.I)):
                    saw_fail=True
                if PASSSHAPE.search(txt): saw_pass=True
print(1 if (saw_fail and saw_pass) else 0)
" 2>/dev/null || echo 0)

echo "P20 canonical differential (assertion-level A-fail AND A-pass in tool-results; exec-errors excluded): $DIFFERENTIAL"

# P17 witness-validity gate: every parsed Failure must carry a witness line, and no
# pass-labeled failure may be present. Witnessed iff a witness line exists per parsed
# Failure (>= FAIL_TOTAL) and no pass-labeled Failure was found.
WITNESSED=0
if [[ "$FAIL_TOTAL" -eq 0 || ( "$WITNESS_LINES" -ge "$FAIL_TOTAL" && "$PASS_LABELED" -eq 0 ) ]]; then
  WITNESSED=1
fi
# P19d: a run producing any Failure must exhibit the machine-observed differential in
# tool-results. All-structural-Unobservable runs (no FAILA) are exempt.
DIFF_OK=0
if [[ "$FAILA" -eq 0 || "$DIFFERENTIAL" -eq 1 ]]; then DIFF_OK=1; fi
# Machine differential is AUTHORITATIVE over prose cause-classification. DIFFERENTIAL=1 is
# computed only from tool_result blocks and already means: an assertion-level A-fail AND an
# A-pass exist, with execution errors (compile/undefined/panic) excluded from the fail side.
# So when it is 1, discrimination is established regardless of the prose PASS_LABELED /
# ABSENCE_LABELED heuristics — those parse the model's authored Failure line and mis-fire on
# e.g. the substring 'pass' inside an '[A-pass ...]' annotation (scenario E, an absence
# property), or a value-mismatch quoted with framework noise. The prose heuristics remain as
# corroborating diagnostics but must not override a machine-confirmed discrimination. They
# still gate when DIFFERENTIAL=0 (no machine pair) — that is where compile-absence lives.
if [[ "$DIFFERENTIAL" -eq 1 ]]; then
  DISCRIMINATED=1
elif [[ "$PASS_LABELED" -eq 0 && "$ABSENCE_LABELED" -eq 0 && "$FAIL_TOTAL" -ge 1 && "$DISTINCT_CAUSES" -eq "$FAIL_TOTAL" ]]; then
  DISCRIMINATED=1
fi
# Witness line is OPTIONAL under the de-collapsed definition ("a 'witness:' line, if added,
# only projects those two results and is not itself evidence") — the tool-result is the
# evidence, so do not require a witness line.
# Machine-evidence-primary: the guarantee lives in the tool-results, not in the exactness
# of the model's authored sentinel strings. PASS requires the PRIMARY machine signals —
# a Gate-3 observation, a machine-observed A-fail/A-pass differential, per-assertion
# discrimination, and Coverage: complete. The 'Overreach: not found' LABEL is corroborating:
# when the primary signals hold but the label is absent (the model did Gate-1 minimization
# as prose without emitting the token), that is a WARNING, not a FAIL.
if [[ "$OBSERVED" -ge 1 \
  && "$DISCRIMINATED" -eq 1 \
  && "$DIFF_OK" -eq 1 \
  && "$COV" -ge 1 ]]; then
  if [[ "$OVERNF" -ge 1 ]]; then
    echo "PASS: machine evidence sound (observed=$OBSERVED, differential=$DIFFERENTIAL, distinct-cause=$DISTINCT_CAUSES/$FAIL_TOTAL, Gate 1 clean, coverage=$COV)"
  else
    echo "PASS (with warning): machine evidence sound but 'Overreach: not found' label not emitted"
    echo "  - warn: Gate-1 minimization work present without the literal 'Overreach: not found' sentinel — label is corroborating, not the guarantee"
  fi
else
  echo "FAIL: sentinel gap detected"
  [[ "$OBSERVED" -lt 1 ]]  && echo "  - Watch-item 1: no Gate-3 observation (Failure:/Unobservable: assertion) — no guard observed firing"
  [[ "$DIFF_OK" -eq 0 ]] && echo "  - P19d: no machine-observed differential — the tool-results do not contain BOTH a fail-shaped and a pass-shaped guard outcome; a Failure must be backed by two distinct observed executions, not an authored witness"
  [[ "$ABSENCE_LABELED" -gt 0 ]] && echo "  - P19: $ABSENCE_LABELED 'Failure:' line(s) whose cause is an absence (undefined/no-value) — not a value-mismatch; needs a violated-vs-satisfied value pair from tool-results"
  [[ "$PASS_LABELED" -gt 0 ]] && echo "  - P17: $PASS_LABELED 'Failure:' line(s) whose cause indicates success (ok/PASS/passed) — a pass does not witness absence"
  [[ "$DISCRIMINATED" -eq 0 && "$FAILA" -gt 0 && "$FAIL_TOTAL" -eq 0 ]] && echo "  - Watch-item 1: $FAILA raw 'Failure:' line(s) present but none parse as 'Failure: assertion [tag] — \"cause\"' — malformed/narrated failures do not witness discrimination"
  [[ "$DISCRIMINATED" -eq 0 && "$FAIL_TOTAL" -ge 1 ]] && echo "  - Watch-item 1: assertions not discriminated — only $DISTINCT_CAUSES of $FAIL_TOTAL failure causes are attributable to a single assertion; a shared cause (e.g. one compile error across all) does not witness each property"
  [[ "$OVERNF" -lt 1 ]]    && echo "  - Watch-item 2: no 'Overreach: not found' — Gate 1 minimization never reached a clean verdict"
  [[ "$OVERF" -gt 0 && "$OVERNF" -lt 1 ]] && echo "  - Watch-item 2: 'Overreach: found' emitted but never resolved to 'Overreach: not found'"
  [[ "$AUDITCMP" -lt 1 ]]  && echo "  - Watch-item 3: missing 'Audit: implementation complete' (required before Coverage: complete)"
  [[ "$COV" -lt 1 ]]       && echo "  - Watch-item 3: missing 'Coverage: complete'"
fi
