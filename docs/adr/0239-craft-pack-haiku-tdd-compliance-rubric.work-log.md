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

Use bar mint/hollow to derive the precise closure language and determine whether it belongs in atomic's definition, ground's escape-route list, or a new composition rule.
