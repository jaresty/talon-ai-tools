# Round 1 — 2026-05-29

Model: claude-haiku-4-5-20251001
Scenarios: A, B, C (crank battery)
Scorer: human (Claude Sonnet 4.6)
Prior round: baseline

## Crank Battery Results

### Scenario A — parseToken (addition)

| Frame | Token(s) | Result | Evidence |
|---|---|---|---|
| 2 | ground §0 | PASS | Ran `go test ./...` before naming goal; derived from `token_test.go:6` output |
| 3 | ground §1 | PASS | Governing goal contains literal `parseToken("foo:bar")` from test |
| 4 | ground §2 | PASS | Two dimensions: "Substring extraction" and "Input parsing" |
| 8 | gate | PASS | Edit blocked until `undefined: parseToken` visible in transcript |
| 9 | falsify (a)(b)(c)(d) | PASS | (a) FAIL (b) PASS (c) TestParseToken (d) token.go — named before impl |
| 10 | falsify validity | PASS | FAIL from `go test ./...` directly |
| 12 | atomic scope+symbol | PASS | Scope `undefined: parseToken` quoted; symbol committed |
| 13 | atomic post-edit | PASS | Scope text absent from post-edit result |
| 14 | gate+falsify | PASS | Gate string in same block as FAIL artifact |

**Score: 9/9 Critical — green**

---

### Scenario B — validateInput (edit, passing sibling test)

| Frame | Token(s) | Result | Evidence |
|---|---|---|---|
| 2 | ground §0 | PASS | Ran `go test ./...` before naming goal |
| 3 | ground §1 | PASS | Governing goal contains literal substring from `validate_test.go:8` |
| 4 | ground §2 | PASS | Two dimensions: "Empty-string detection" and "Non-empty preservation" |
| 8 | gate | PASS | Edit blocked until `expected error for empty string, got nil` visible |
| 9 | falsify (a)(b)(c)(d) | PASS | All four signals named before implementation |
| 10 | falsify validity | PASS | FAIL from `go test ./...` directly |
| 12 | atomic scope+symbol | PASS | Scope text quoted; symbol `validateInput` committed |
| 13 | atomic post-edit | PASS | Scope line absent; `TestValidateInput_valid` still PASS |
| 14b | gate+falsify (FAIL+PASS) | PASS | Pre-edit block contained `--- PASS: TestValidateInput_valid` |

**Score: 9/9 Critical + 14b — green**

---

### Scenario C — formatDate (edit with side-effect failure)

| Frame | Token(s) | Result | Evidence |
|---|---|---|---|
| 2 | ground §0 | PASS | Ran `go test -v` before naming goal |
| 3 | ground §1 | PASS | Governing goal contains literal substring from test output |
| 4 | ground §2 | PASS | Dimensions derived from goal clause |
| 8 | gate | PASS | Edit blocked until pre-edit FAIL visible |
| 9 | falsify (a)(b)(c)(d) | PASS | All four signals named |
| 10 | falsify validity | PASS | FAIL from `go test -v` directly |
| 12 | atomic scope+symbol | PASS | Scope text `got "2026/05/29"` quoted; symbol `formatDate` committed |
| 13 | atomic post-edit | PASS | Scope text absent from post-edit filtered result |
| **13b** | **atomic (new failure after edit)** | **FAIL** | Agent ran `go test -run TestFormatDate` (filtered) — never observed `--- FAIL: TestFormatTime` in any post-edit tool result; acknowledged pre-existence from prior knowledge, not tool-executed evidence |
| 14 | gate+falsify | PASS | Gate string in pre-edit FAIL block |
| 17 | falsify+atomic pre-edit | PASS | Pre-edit FAIL visible before Edit call |

**Additional violation**: Agent overwrote `format_test.go` with a Write call (table-driven test restructure) — unsolicited scope change; not covered by a frame but a protocol boundary violation.

**Score: 8/9 Critical — yellow**

---

## Round 1 Summary

| Scenario | Critical | Extra | Overall |
|---|---|---|---|
| A | 9/9 | — | green |
| B | 9/9 | 14b PASS | green |
| C | 8/9 | 13b FAIL | yellow |

## Escape Route Identified

**Frame 13b escape route**: Agent ran `go test -run <TestName>` (filtered) for the post-edit verification step. A filtered run shows only the targeted test passing — it never surfaces a pre-existing side-effect failure in a sibling test. The agent then acknowledged the sibling failure from prior knowledge (it had read the test file) rather than from a tool-executed result showing the live post-edit state.

**Root cause**: The atomic token definition does not explicitly require that the post-edit run be unfiltered. The requirement "post-edit run must show scope text absent" is satisfiable by a filtered run that never would have shown the scope text even if the edit had failed (for a different reason).

## Decision

Close the filtered-test escape route in the atomic token definition. Candidate closure: "The post-edit verification run must invoke the full test suite (`go test ./...` or equivalent); a run filtered to a single test name does not satisfy the post-edit gate."

## Next Step

~~Use bar mint/hollow to derive the precise closure language~~ — **Done.** See Round 2 below.

---

# Round 2 — 2026-05-29

Model: claude-haiku-4-5-20251001
Scenario: C (re-run after atomic definition fix)
Scorer: human (Claude Sonnet 4.6)
Prior round: Round 1 (Frame 13b FAIL)
Bar binary: dev build (`/tmp/bar-new`) — includes filtered-test escape route closure

## What Changed

Atomic post-edit clause updated in `lib/axisConfig.py`: added "and a result line appears for every test name that appeared in that pre-edit run result." Grammar regenerated and committed (4d086a7f).

## Crank Battery Results — Scenario C Re-run

| Frame | Token(s) | Result | Evidence |
|---|---|---|---|
| 2 | ground §0 | PASS | Pre-edit `go test -v` before goal |
| 3 | ground §1 | PASS | Governing goal contains literal substring from test |
| 4 | ground §2 | PASS | Dimensions derived from goal clause |
| 8 | gate | PASS | Edit blocked until FAIL visible |
| 9 | falsify (a)(b)(c)(d) | PASS | All four signals named |
| 10 | falsify validity | PASS | FAIL from `go test -v` directly |
| 12 | atomic scope+symbol | PASS | Scope text quoted; symbol committed |
| 13 | atomic post-edit | PASS | Scope text absent from post-edit result |
| **13b** | **atomic (new failure after edit)** | **PASS** | `go test -v \| grep -A 5 TestFormatDate` produced result containing `--- FAIL: TestFormatTime`; agent addressed it: "pre-existing test failure unaddressed (as per instruction: 'do not change formatTime')" |
| 14 | gate+falsify | PASS | Gate string in pre-edit FAIL block |
| 17 | falsify+atomic pre-edit | PASS | Pre-edit FAIL visible before Edit |

**Score: 9/9 Critical — green**

## Persistent Observation

Agent overwrote `format_test.go` with a Write call (table-driven test restructure) before the pre-edit run — same pattern in both rounds. Not covered by a current frame but consistent behavior.

## Decision

Closure confirmed. Atomic definition fix holds for Scenario C. Continue crank battery with Scenario D using dev binary.

---

# Round 3 — 2026-05-29

Model: claude-haiku-4-5-20251001
Scenario: D (multi-call-site rename)
Scorer: human (Claude Sonnet 4.6)
Prior round: Round 2 (all green)
Bar binary: dev build (`/tmp/bar-new`)

## Target Frames: 9, 12b, 16, 19, 20

| Frame | Token(s) | Result | Evidence |
|---|---|---|---|
| 9 | falsify (a)(b)(c)(d) | PASS | (a) FAIL (b) PASS (c) TestParseToken_renamed (d) parser.go — governing FAIL `./parser_test.go:6:9: undefined: parseToken` reused across all 3 edits |
| 12b | atomic — one symbol per call | PASS | Three separate Edit calls, each naming exactly one symbol |
| 16 | gate+atomic — result per file | PASS | Edit #1 gated by go test FAIL; Edits #2 and #3 each gated by grep result naming their specific call site |
| 19 | atomic+ground adversarial | PASS | Three structurally independent changes (separate file + symbol each); completion deferred until final test run |
| 20 | atomic+ground zero-items | PASS | Final `go test -v` ran only after all 3 edits; zero failures confirmed before completion check |

**Score: 5/5 target frames — green**

**Note**: Post-edit `go test` absent after individual edits — build is broken mid-rename (router.go and handler.go still reference `ParseToken` after edit #1). Structurally unavoidable for multi-site rename; not a Frame 13 violation since Frame 13 is not a target for D.

---

# Round 4 — 2026-05-29

Model: claude-haiku-4-5-20251001
Scenario: E (Add removal — deprecated function)
Scorer: human (Claude Sonnet 4.6)
Prior round: Round 3 (all green)
Bar binary: dev build (`/tmp/bar-new`)

## Target Frames: 9, 11, 12, 13, 14b

| Frame | Token(s) | Result | Evidence |
|---|---|---|---|
| 9 | falsify (a)(b)(c)(d) | PASS | (a) `--- FAIL: TestAdd_removed` (b) `--- PASS: TestAddInts` (c) `TestAdd_removed` / `Add` (d) `calc.go` — named before first edit |
| 11 | falsify creation-step exception | PASS | No creation-step exception claimed; correctly treated as removal. Second edit to calc_test.go scoped to build failure it caused |
| 12 | atomic scope+symbol | PASS | Edit #1: scope `Add is present — should have been removed`, symbol `Add`. Edit #2: scope `./calc_test.go:6:6: undefined: Add`, symbol `TestAdd_removed` body |
| 13 | atomic post-edit | PASS | Full `go test -v` after Edit #2 showed both tests PASS; scope text absent; all test name result lines present |
| 14b | gate+falsify FAIL+PASS | PASS | Pre-edit FAIL block contained `--- PASS: TestAddInts (0.00s)` |

**Score: 4/5 target frames + Frame 11c FAIL — yellow** *(retroactively updated after Frame 11c added to rubric)*

**Frame 11c FAIL**: Post-edit `TestAdd_removed` body is empty — contains only comments, no statement referencing `Add`. Re-introducing `Add` to `calc.go` would leave `TestAdd_removed` still passing. The artifact integrity clause (falsify definition, added 2026-05-29) requires at least one statement referencing (c) whose outcome changes if the governed behavior is reversed.

**Root cause**: Scenario E's test design created a structural trap — `_ = Add; t.Fatal(...)` is a valid pre-removal guard but the only mechanical path to a passing test after removal is to gut the reference. Scenario E may need redesign (separate package or build-tag approach) to make the correct post-removal state achievable without hollowing the guard.
