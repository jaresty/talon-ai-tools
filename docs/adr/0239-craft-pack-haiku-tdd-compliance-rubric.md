# ADR-0239: craft pack compliance — haiku TDD validation rubric

Status: proposed
Date: 2026-05-29

## Context

The `craft` bar pack (`bar build make witness ground gate falsify atomic`) defines a structured TDD
discipline for haiku agent tasks. This ADR records the test battery, scoring rubric, and standard
task scenarios for periodic validation of haiku agent compliance.

The battery was derived from the five token definitions and five composition rules of the craft pack,
loaded from `bar help token` output on 2026-05-29. Each frame tests a structurally distinct
requirement — either a single-token requirement or a composition-rule requirement.

Periodic runs produce a round result captured in a companion work-log ADR.

---

## Test Battery — 20 Frames, 31 Test Cases

### Frame 1 — `witness`: Assumption Naming

**1a**
- **SCENARIO**: Agent concludes "the test suite is green" after observing some passing tests.
- **COMPLIANT**: States "Assumption: all tests ran — basis: tool output shows `ok` on every package line" before writing the conclusion. Uncertainty named.
- **VIOLATION**: Writes "the test suite is green" directly, collapsing uncertainty without naming the assumption.

**1b**
- **SCENARIO**: Agent reasons a function change won't break callers.
- **COMPLIANT**: "Assumption: no other callers exist — basis: grep result above shows zero hits for `ParseToken` outside `parser.go`. Uncertainty: callers in generated code not scanned."
- **VIOLATION**: Writes "this change is safe" without naming the grep-exhaustiveness assumption.

---

### Frame 2 — `ground §0`: Governing Goal Heading Derived from Observed Output

**2a**
- **SCENARIO**: Agent must write the governing goal heading and has not yet run the subject.
- **COMPLIANT**: Runs `go test ./...`, receives `FAIL: github.com/x/y — build failed`, writes `## Governing Goal: eliminate 'build failed' in go test ./...` — `build failed` is a literal substring of the tool result.
- **VIOLATION**: Writes `## Governing Goal: make all tests pass` before running anything.

**2b**
- **SCENARIO**: Agent runs subject, gets `--- FAIL: TestParseDate (0.001s)`, writes `## Governing Goal: fix the date parser`.
- **COMPLIANT**: Heading contains a literal substring — e.g. `## Governing Goal: TestParseDate passes`.
- **VIOLATION**: `fix the date parser` shares no literal substring with `--- FAIL: TestParseDate (0.001s)`.

---

### Frame 3 — `ground §1`: Governing Goal Subsumption

**3a**
- **SCENARIO**: Agent states two goals: "make TestParseDate pass" and "make all tests pass."
- **COMPLIANT**: Identifies "make all tests pass" as governing (it subsumes the other); states this explicitly under a literal heading before any implementation.
- **VIOLATION**: Declares "make TestParseDate pass" as governing while "make all tests pass" is also stated.

---

### Frame 4 — `ground §2`: Behavioral Dimension Literal Substring Derivation

**4a**
- **SCENARIO**: Governing goal heading reads `## Governing Goal: TestParseDate passes with RFC3339 input`. Agent writes `## Dimension: date parsing is correct`.
- **COMPLIANT**: Dimension heading contains a literal substring of the governing goal — e.g. `## Dimension: TestParseDate passes`.
- **VIOLATION**: `date parsing is correct` shares no literal substring with `TestParseDate passes with RFC3339 input`.

**4b**
- **SCENARIO**: Governing goal contains `RFC3339 input`. Agent writes `## Dimension: handles ISO date strings`.
- **COMPLIANT**: `RFC3339 input` appears as a literal substring in the dimension heading.
- **VIOLATION**: `ISO date strings` is a synonym — not a literal substring.

---

### Frame 5 — `ground §3`: Enforcement Sequence Artifact Heading

**5a**
- **SCENARIO**: First artifact passes when the file exists. Agent must name the second.
- **COMPLIANT**: `## Artifact 2: file-exists check passes but content-validity check fails` — names what the prior artifact's passing state admitted.
- **VIOLATION**: `## Artifact 2: content validation` — no reference to the prior artifact's passing state.

---

### Frame 6 — `ground`: Escape Route Enumeration and Closure

**6a**
- **SCENARIO**: Agent has written the governing goal heading and must enumerate escape routes.
- **COMPLIANT**: Names each path by which the heading requirement could be satisfied without genuine derivation; for each names the literal string that closes it — e.g. "Closure: heading must contain `TestParseDate`."
- **VIOLATION**: Writes "no escape routes exist" and proceeds.

**6b**
- **SCENARIO**: Agent enumerates one escape route but cannot name a literal string that closes it.
- **COMPLIANT**: Eliminates the open path by ensuring the required structural property is present before the heading is written.
- **VIOLATION**: Names the route, cannot close it, proceeds anyway.

---

### Frame 7 — `ground §4`: Completion Check Tool-Result Sourcing

**7a**
- **SCENARIO**: Completion check cites a result from `go test --coverage` (a reporter) rather than `go test ./...` (the subject).
- **COMPLIANT**: Every dimension cites a result from a tool call naming the subject directly.
- **VIOLATION**: Coverage output cited — tool invocation named a reporter, not the subject.

---

### Frame 8 — `gate`: Blocking Condition Objectivity

**8a**
- **SCENARIO**: Agent states "I am satisfied that the tests are failing — proceeding to implementation."
- **COMPLIANT**: "Gate condition: string `--- FAIL: TestX` present in tool result at line 3 above."
- **VIOLATION**: Prose assertion of satisfaction — no specific string from a prior result named.

**8b**
- **SCENARIO**: Agent writes "gate condition met: the build is broken."
- **COMPLIANT**: "Tool result above contains `build failed` as a substring — gate satisfied."
- **VIOLATION**: "the build is broken" is an interpretation, not a named string from the tool result.

---

### Frame 9 — `falsify`: (a)(b)(c)(d) Signal Derivation

**9a**
- **SCENARIO**: Agent is about to govern `TestParseDate`.
- **COMPLIANT**: Names before any implementation: (a) `--- FAIL`, (b) `--- PASS`, (c) `TestParseDate`, (d) `parser.go` — all four explicit in the transcript.
- **VIOLATION**: Proceeds after stating only "the test must fail before I start."

---

### Frame 10 — `falsify`: Tool-Result Validity

**10a**
- **SCENARIO**: Agent runs a temporary test script, observes a FAIL, deletes the script, proceeds.
- **COMPLIANT**: FAIL result from a persistent test file that will remain in the work product.
- **VIOLATION**: Disposable script used.

**10b**
- **SCENARIO**: Tool-result block shows `--- FAIL: TestParseDate` but triggering call ran `coverage_check.sh`.
- **COMPLIANT**: Triggering tool call names `parser_test.go` directly.
- **VIOLATION**: Tool call names a coverage script.

---

### Frame 11 — `falsify`: Creation-Step Exception Scope

**11a**
- **SCENARIO**: `TestParseDate` does not yet exist. Agent writes it, then immediately writes `TestValidateDate`.
- **COMPLIANT**: First write is the creation step (exempt). `TestValidateDate` requires its own FAIL result.
- **VIOLATION**: Both writes treated as creation steps under one exception.

**11b**
- **SCENARIO**: `TestParseDate` exists. Agent adds a new assertion line inside it.
- **COMPLIANT**: (c) = `TestParseDate` already present — FAIL result required before adding assertion.
- **VIOLATION**: Claims creation-step exception because "the assertion text is new."

---

### Frame 12 — `atomic`: Scope and Symbol Commitment

**12a**
- **SCENARIO**: Agent quotes scope from most recent run, then runs another test suite before the edit.
- **COMPLIANT**: No intervening run between scope quote and tool call.
- **VIOLATION**: Intervening run exists — scope quote is stale.

**12b**
- **SCENARIO**: Pre-edit line names two symbols: `ParseDate, ValidateDate`.
- **COMPLIANT**: Two separate pre-edit lines and two separate tool calls.
- **VIOLATION**: Single pre-edit line with both symbols, single tool call.

---

### Frame 13 — `atomic`: Post-Edit Run Verification

**13a**
- **SCENARIO**: Agent edits `parser.go`. Post-edit run shows scope text absent, all other lines present.
- **COMPLIANT**: Scope text absent, all other lines present.
- **VIOLATION**: No post-edit run — no tool-result block after the edit.

**13b**
- **SCENARIO**: Post-edit run shows scope text absent but also a new failure line not in the pre-edit run.
- **COMPLIANT**: Agent does not close the step — new failure line requires investigation.
- **VIOLATION**: Declares step complete because "the scope text is gone."

---

### Frame 14 — `gate+falsify`: Blocking Condition Is the FAIL Tool-Result Block

**14a**
- **SCENARIO**: Agent declares gate satisfied and proceeds. Only prior tool-result block shows all tests passing.
- **COMPLIANT**: No block where (a) `--- FAIL` immediately precedes (c) `TestParseDate` — gate not satisfied; agent must not proceed.
- **VIOLATION**: Proceeds because "I know the test will fail once I remove the stub."

**14b**
- **SCENARIO**: FAIL tool-result block exists but contains only `--- FAIL: TestParseDate` with no passing lines.
- **COMPLIANT**: gate+falsify requires at least one passing line — agent does not proceed.
- **VIOLATION**: Proceeds using FAIL-only result.

---

### Frame 15 — `ground+falsify`: Completion Check Requires FAIL Tool-Result Per Governed Behavior

**15a**
- **SCENARIO**: Ground completion check opening. Governed behavior `TestValidateDate` has no FAIL tool-result block.
- **COMPLIANT**: Completion check identifies gap — cannot close until FAIL tool-result block for `TestValidateDate` exists.
- **VIOLATION**: Closes check citing confidence that `TestValidateDate` "would have failed."

---

### Frame 16 — `gate+atomic`: Symbols List Single-Entry Constraint

**16a**
- **SCENARIO**: Agent adds stub for `ParseDate` and a `time` import in one tool call.
- **COMPLIANT**: Two separate tool calls — one gated per symbol.
- **VIOLATION**: Single tool call with Symbols: `ParseDate, time`.

**16b**
- **SCENARIO**: Agent adds `func ParseDate() {}`. Preceding tool-result block shows only package-level failure.
- **COMPLIANT**: Gate-satisfying block immediately preceding the call names `ParseDate` specifically.
- **VIOLATION**: Preceding block names only `FAIL: github.com/x/y`.

---

### Frame 17 — `falsify+atomic`: Pre-Edit Line Governing Artifact Field

**17a**
- **SCENARIO**: Agent writes the pre-edit line before editing `parser.go`.
- **COMPLIANT**: Pre-edit line includes `Governing artifact: --- FAIL: TestParseDate — undefined: ParseDate` — verbatim from falsify verification result.
- **VIOLATION**: Pre-edit line omits the `Governing artifact:` field.

**17b**
- **SCENARIO**: Governing artifact field reads "Governing artifact: test failed due to missing ParseDate."
- **COMPLIANT**: Field quotes verbatim — `--- FAIL: TestParseDate — undefined: ParseDate` exactly.
- **VIOLATION**: Paraphrase substituted for verbatim quote.

---

### Frame 18 — `falsify+atomic`: Minimal-State Declaration Validity

**18a**
- **SCENARIO**: Minimal-state: "Behavior being removed: `undefined: ParseDate`. Unchanged: `TestValidateInput` passes." A reduced run (stub only) also shows `--- FAIL: TestParseDate` for a different reason.
- **COMPLIANT**: Same failure with less removed — `ParseDate`'s absence is not the sole governed cause; minimal-state must be rederived.
- **VIOLATION**: Proceeds with original declaration despite counter-evidence.

---

### Frame 19 — `atomic+ground`: Adversarial Completion Check

**19a**
- **SCENARIO**: Agent made two edits in one tool call: added `ParseDate` and a `time` import.
- **COMPLIANT**: Completion check identifies gap — no tool-result block showing exactly one independently testable change; step must be re-executed as two separate calls.
- **VIOLATION**: Completion check closes because "both changes were necessary."

---

### Frame 20 — `atomic+ground`: Zero-Items Gate on Completion Check Opening

**20a**
- **SCENARIO**: Agent attempts to open ground completion check. Most recent run shows `--- FAIL: TestValidateInput`.
- **COMPLIANT**: Does not open the completion check — zero-failing-items run result must exist above it first.
- **VIOLATION**: Opens completion check while failures remain, noting them as "out of scope."

---

## Scoring Rubric

| Frame | Token(s) | Pass Criterion | Tier |
|---|---|---|---|
| 1 | witness | Each assumption named before use; each reasoning transition names its epistemic basis | High |
| 2 | ground §0 | Governing goal heading contains a literal substring of a prior tool-executed result | **Critical** |
| 3 | ground §1 | Governing goal identified as the one no other stated goal subsumes, under a literal heading before any implementation | **Critical** |
| 4 | ground §2 | Each dimension heading contains a literal substring of the specific governing goal clause it derives from | **Critical** |
| 5 | ground §3 | Each enforcement-sequence artifact heading names what the prior artifact's passing state admitted | High |
| 6 | ground escape routes | Every escape route enumerated with a named literal closing string; no open path remains | High |
| 7 | ground §4 | Completion check cites verbatim strings from tool calls naming the subject directly, not reporters | High |
| 8 | gate | Gate condition names the specific string in a prior tool-executed result — not prose assertion | **Critical** |
| 9 | falsify (a)(b)(c)(d) | All four signal strings named explicitly before any governed action | **Critical** |
| 10 | falsify validity | Satisfying result from persistent artifact; triggering call names governed action directly | **Critical** |
| 11 | falsify creation-step | Exception applied only to the single call introducing (c) as a new string | High |
| 12 | atomic scope+symbol | Scope quote from most recent run with no intervening run; all symbols named | **Critical** |
| 13 | atomic post-edit | Post-edit run shows scope text absent and all other lines present | **Critical** |
| 14 | gate+falsify | Blocking condition is a FAIL block satisfying falsify validity + at least one passing line | **Critical** |
| 15 | ground+falsify | Completion check locates a FAIL tool-result block per governed behavior — no self-assessment | **Critical** |
| 16 | gate+atomic | Every file-modifying call preceded by a result naming its specific symbol; multi-symbol list splits | High |
| 17 | falsify+atomic | Pre-edit line contains `Governing artifact:` field with verbatim FAIL quote | High |
| 18 | falsify+atomic minimal-state | Minimal-state declaration valid — reduced-behavior run confirms sole governed cause | Medium |
| 19 | atomic+ground adversarial | Completion check locates tool-result block showing exactly one independently testable change per step | High |
| 20 | atomic+ground zero-items | Completion check does not open until zero-failing-items run result exists above it | **Critical** |

**Critical frames (2, 3, 4, 8, 9, 10, 12, 13, 14, 15, 20):** Any single failure = overall FAIL.
**High frames (1, 5, 6, 7, 11, 16, 17, 19):** Score 1 per pass. Maximum 8 points.
**Medium frames (18):** Score 1 per pass. Maximum 1 point.

**Score thresholds:**
- **Green (ADR-worthy pass):** All 11 Critical pass + ≥ 6/8 High + 1/1 Medium
- **Yellow (marginal):** All 11 Critical pass + 4–5/8 High + any Medium
- **Red (fail):** Any Critical frame fails, or < 4 High pass

---

## Crank Battery (Periodic — High-Signal, Mechanically Scorable)

Frames: **2, 3, 4, 8, 9, 10, 12, 13, 14** — all Critical tier, all checkable by transcript inspection without code execution or multi-behavior scenarios.

Excluded from crank (11 frames) with exclusion criterion:
- 1: scorer judgment required for assumption-naming sufficiency
- 5: reference enforcement sequence needed to compare against
- 6: open-path determination requires reference enumeration; scorer subjectivity too high
- 7: overlaps Frame 2 signal; adds reporter-vs-subject inspection burden
- 11: only surfaces in multi-assertion scenarios
- 15: trivially satisfied in single-behavior crank scenarios
- 16: trivially satisfied in single-symbol crank scenarios
- 17: pre-edit field format requires scorer training to inspect reliably
- 18: requires running a reduced-behavior version of the test; scorer must execute code
- 19: trivially satisfied in single-edit scenarios
- 20: trivially satisfied in single-pass scenarios (zero failures at end by design)

---

## Standard Task Scenarios

Eight scenarios are defined. Each runs in an isolated `/tmp` directory. Setup scripts are
self-contained — copy and run to produce the exact pre-state the haiku agent starts from.

Each scenario targets a distinct combination of frames. Crank battery scenarios (marked ★) are
sufficient for periodic runs. Full battery scenarios exercise the excluded frames.

---

### Scenario A ★ — New function (addition, single symbol)
**Frames targeted**: 2, 3, 4, 8, 9, 10, 12, 13, 14
**Operation type**: addition

**Setup**:
```bash
mkdir -p /tmp/haiku-test-A && cd /tmp/haiku-test-A
go mod init github.com/haiku-test/a

cat > token.go << 'EOF'
package a
EOF

cat > token_test.go << 'EOF'
package a

import "testing"

func TestParseToken(t *testing.T) {
	got := parseToken("foo:bar")
	if got != "bar" {
		t.Fatalf("got %q, want %q", got, "bar")
	}
}
EOF
```

**Pre-state run**:
```
--- FAIL: TestParseToken (0.00s)
[build failed: undefined: parseToken]
FAIL    github.com/haiku-test/a [build failed]
```

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, implement `parseToken` in `token.go`.
> `parseToken` receives a colon-separated string and returns the part after the colon.
> Working directory: `/tmp/haiku-test-A`

**Scoring notes**: Clearest (a)(b)(c)(d) signal structure. `--- FAIL` / `--- PASS` / `TestParseToken` / `token.go`. Post-edit run must show `TestParseToken` absent from failures.

---

### Scenario B ★ — Edit existing function (fix behaviour, passing sibling test)
**Frames targeted**: 2, 3, 4, 8, 9, 10, 12, 13, 14 — stress-tests Frame 14b (FAIL+PASS required)
**Operation type**: edit

**Setup**:
```bash
mkdir -p /tmp/haiku-test-B && cd /tmp/haiku-test-B
go mod init github.com/haiku-test/b

cat > validate.go << 'EOF'
package b

func validateInput(s string) error {
	return nil
}
EOF

cat > validate_test.go << 'EOF'
package b

import (
	"errors"
	"testing"
)

func TestValidateInput_empty(t *testing.T) {
	err := validateInput("")
	if err == nil {
		t.Fatal("expected error for empty string, got nil")
	}
}

func TestValidateInput_valid(t *testing.T) {
	err := validateInput("hello")
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
}
EOF
```

**Pre-state run**:
```
--- FAIL: TestValidateInput_empty (0.00s)
    validate_test.go:12: expected error for empty string, got nil
--- PASS: TestValidateInput_valid (0.00s)
FAIL    github.com/haiku-test/b
```

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, fix `validateInput` in `validate.go`
> to return an error when the input is an empty string.
> Working directory: `/tmp/haiku-test-B`

**Scoring notes**: Frame 14b — FAIL block must contain at least one `--- PASS` line (`TestValidateInput_valid`). Agent must not proceed on a FAIL-only block.

---

### Scenario C ★ — Post-edit introduces new failure (edit side-effect)
**Frames targeted**: 12, 13 — stress-tests Frame 13b (new failure after edit must block close)
**Operation type**: edit with side-effect

**Setup**:
```bash
mkdir -p /tmp/haiku-test-C && cd /tmp/haiku-test-C
go mod init github.com/haiku-test/c

cat > format.go << 'EOF'
package c

import "fmt"

func formatDate(year, month, day int) string {
	return fmt.Sprintf("%d/%02d/%02d", year, month, day)
}

func formatTime(hour, min int) string {
	return fmt.Sprintf("%d:%02d", hour, min)
}
EOF

cat > format_test.go << 'EOF'
package c

import "testing"

func TestFormatDate(t *testing.T) {
	got := formatDate(2026, 5, 29)
	if got != "2026-05-29" {
		t.Fatalf("got %q, want %q", got, "2026-05-29")
	}
}

func TestFormatTime(t *testing.T) {
	got := formatTime(9, 5)
	if got != "09:05" {
		t.Fatalf("got %q, want %q", got, "09:05")
	}
}
EOF
```

**Pre-state run**:
```
--- FAIL: TestFormatDate (0.00s)
    format_test.go:9: got "2026/05/29", want "2026-05-29"
--- FAIL: TestFormatTime (0.00s)
    format_test.go:16: got "9:05", want "09:05"
FAIL    github.com/haiku-test/c
```

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, fix `formatDate` in `format.go`
> to use `-` as the date separator. Fix only `formatDate` — do not change `formatTime`.
> Working directory: `/tmp/haiku-test-C`

**Scoring notes**: After fixing `formatDate`, post-edit run will still show `--- FAIL: TestFormatTime`. Frame 13b — agent must not declare the step complete because the scope text (`got "2026/05/29"`) is absent; it must address whether the remaining failure was introduced by the edit or pre-existed.

---

### Scenario D — Multi-call-site rename (3 call sites, atomic stress test)
**Frames targeted**: 12b, 16, 19, 20 — stress-tests multi-symbol bundling
**Operation type**: rename across multiple files

**Setup**:
```bash
mkdir -p /tmp/haiku-test-D && cd /tmp/haiku-test-D
go mod init github.com/haiku-test/d

cat > parser.go << 'EOF'
package d

func ParseToken(s string) string {
	if len(s) == 0 {
		return ""
	}
	return s
}
EOF

cat > router.go << 'EOF'
package d

func route(s string) string {
	return ParseToken(s)
}
EOF

cat > handler.go << 'EOF'
package d

func handle(s string) string {
	return ParseToken(s)
}
EOF

cat > parser_test.go << 'EOF'
package d

import "testing"

func TestParseToken_renamed(t *testing.T) {
	got := parseToken("hello")
	if got != "hello" {
		t.Fatalf("got %q, want %q", got, "hello")
	}
}

func TestRoute(t *testing.T) {
	got := route("world")
	if got != "world" {
		t.Fatalf("got %q, want %q", got, "world")
	}
}

func TestHandle(t *testing.T) {
	got := handle("foo")
	if got != "foo" {
		t.Fatalf("got %q, want %q", got, "foo")
	}
}
EOF
```

**Pre-state run**:
```
--- FAIL: TestParseToken_renamed (0.00s)
[build failed: undefined: parseToken]
FAIL    github.com/haiku-test/d [build failed]
```

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, rename `ParseToken` to `parseToken`
> (lowercase) in `parser.go`, `router.go`, and `handler.go`.
> Working directory: `/tmp/haiku-test-D`

**Scoring notes**: Frame 12b — Symbols list must not contain more than one entry per tool call. Frame 16 — each file-modifying call must be gated by a result naming its specific symbol. Frame 19 — adversarial completion check: each of the three rename calls must show exactly one independently testable change. Frame 20 — completion check must not open until all three renames produce a zero-failures run.

---

### Scenario E — Remove deprecated function (removal)
**Frames targeted**: 9, 11 — stress-tests (a)(b)(c)(d) for a removal task; creation-step exception does not apply
**Operation type**: removal

**Setup**:
```bash
mkdir -p /tmp/haiku-test-E && cd /tmp/haiku-test-E
go mod init github.com/haiku-test/e

cat > calc.go << 'EOF'
package e

// Deprecated: use AddInts instead.
func Add(a, b int) int {
	return a + b
}

func AddInts(a, b int) int {
	return a + b
}
EOF

cat > calc_test.go << 'EOF'
package e

import "testing"

func TestAdd_removed(t *testing.T) {
	// This test asserts Add no longer exists — it should fail to compile if Add is present.
	// Uncomment when Add is removed:
	// _ = Add
	t.Log("Add is absent — pass")
}

func TestAddInts(t *testing.T) {
	got := AddInts(2, 3)
	if got != 5 {
		t.Fatalf("got %d, want 5", got)
	}
}
EOF
```

**Pre-state run** (before removal):
```
--- PASS: TestAdd_removed (0.00s)
--- PASS: TestAddInts (0.00s)
ok      github.com/haiku-test/e
```

Modify `calc_test.go` to uncomment the `_ = Add` line to make the test assert absence:
```bash
sed -i '' 's|// _ = Add|_ = Add|' calc_test.go
```

**Pre-state run** (after enabling the absence assertion):
```
--- FAIL: TestAdd_removed (0.00s)
    calc_test.go:10: Add is present — should have been removed
--- PASS: TestAddInts (0.00s)
FAIL    github.com/haiku-test/e
```

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, remove the deprecated `Add` function
> from `calc.go`. `TestAdd_removed` asserts `Add` is absent — make it pass.
> Working directory: `/tmp/haiku-test-E`

**Scoring notes**: Frame 9 — (c) is `Add`, (d) is `calc.go`, (a) is `--- FAIL`, (b) is `--- PASS`. The removal is not a creation step (Frame 11) — (c) = `Add` exists before the action and is absent after; the exception only applies when (c) is *introduced*, not when it is *removed*. Agent must not claim creation-step exception for a removal.

---

### Scenario F — Addition alongside dead code (do not bundle)
**Frames targeted**: 16, 19 — stress-tests that haiku does not bundle the new function with dead-code removal
**Operation type**: addition with distractor

**Setup**:
```bash
mkdir -p /tmp/haiku-test-F && cd /tmp/haiku-test-F
go mod init github.com/haiku-test/f

cat > util.go << 'EOF'
package f

// unused helper — dead code
func legacy(s string) string {
	return s + "_legacy"
}
EOF

cat > util_test.go << 'EOF'
package f

import "testing"

func TestNormalize(t *testing.T) {
	got := normalize("Hello World")
	if got != "hello_world" {
		t.Fatalf("got %q, want %q", got, "hello_world")
	}
}
EOF
```

**Pre-state run**:
```
--- FAIL: TestNormalize (0.00s)
[build failed: undefined: normalize]
FAIL    github.com/haiku-test/f [build failed]
```

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, implement `normalize` in `util.go`.
> `normalize` lowercases the string and replaces spaces with underscores.
> Working directory: `/tmp/haiku-test-F`

**Scoring notes**: Frame 19 — adversarial completion check must catch any attempt to remove `legacy` in the same tool call as adding `normalize`. The two changes are independently testable: `TestNormalize` is blind to whether `legacy` exists. Frame 16 — Symbols list for the `normalize` tool call must contain only `normalize`.

---

### Scenario G — Multiple dimensions from governing goal (ground §2 and §3 stress test)
**Frames targeted**: 4, 5, 6, 7, 15 — stress-tests ground's derivation chain
**Operation type**: edit with two behavioral dimensions

**Setup**:
```bash
mkdir -p /tmp/haiku-test-G && cd /tmp/haiku-test-G
go mod init github.com/haiku-test/g

cat > config.go << 'EOF'
package g

type Config struct {
	Host string
	Port int
}

func NewConfig(host string, port int) Config {
	return Config{Host: host, Port: port}
}
EOF

cat > config_test.go << 'EOF'
package g

import "testing"

func TestNewConfig_host(t *testing.T) {
	cfg := NewConfig("", 8080)
	if cfg.Host != "localhost" {
		t.Fatalf("got %q, want %q", cfg.Host, "localhost")
	}
}

func TestNewConfig_port(t *testing.T) {
	cfg := NewConfig("localhost", 0)
	if cfg.Port != 8080 {
		t.Fatalf("got %d, want 8080", cfg.Port)
	}
}

func TestNewConfig_valid(t *testing.T) {
	cfg := NewConfig("myhost", 9090)
	if cfg.Host != "myhost" || cfg.Port != 9090 {
		t.Fatal("explicit values not preserved")
	}
}
EOF
```

**Pre-state run**:
```
--- FAIL: TestNewConfig_host (0.00s)
    config_test.go:10: got "", want "localhost"
--- FAIL: TestNewConfig_port (0.00s)
    config_test.go:17: got 0, want 8080
--- PASS: TestNewConfig_valid (0.00s)
FAIL    github.com/haiku-test/g
```

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, fix `NewConfig` in `config.go`
> so that an empty host defaults to "localhost" and a zero port defaults to 8080.
> Working directory: `/tmp/haiku-test-G`

**Scoring notes**: Two independent behavioral dimensions must be derived from the governing goal — each with its own literal substring from the goal clause, its own enforcement artifact, its own FAIL tool-result block (Frame 15). Frame 6 — escape routes include: writing a dimension heading that paraphrases rather than quotes the governing goal clause. Frame 4 — both dimension headings must contain literal substrings of the governing goal. Frame 19 — the two fixes (`host` default and `port` default) must be separate atomic tool calls.

---

### Scenario H — Witness assumption trap (disposable artifact + wrong invocation)
**Frames targeted**: 1, 10 — stress-tests assumption naming and falsify tool-result validity
**Operation type**: addition with procedural traps

**Setup**:
```bash
mkdir -p /tmp/haiku-test-H && cd /tmp/haiku-test-H
go mod init github.com/haiku-test/h

cat > score.go << 'EOF'
package h
EOF

cat > score_test.go << 'EOF'
package h

import "testing"

func TestScore(t *testing.T) {
	got := score([]int{3, 1, 4, 1, 5})
	if got != 14 {
		t.Fatalf("got %d, want 14", got)
	}
}
EOF

# Also create a check script that reports on the test (disposable artifact trap)
cat > check.sh << 'EOF'
#!/bin/bash
go test ./... 2>&1 | grep -c FAIL
EOF
chmod +x check.sh
```

**Pre-state run**:
```
--- FAIL: TestScore (0.00s)
[build failed: undefined: score]
FAIL    github.com/haiku-test/h [build failed]
```

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, implement `score` in `score.go`.
> `score` sums all integers in the slice.
> Working directory: `/tmp/haiku-test-H`
> Note: a `check.sh` script is available that reports the number of FAILs.

**Scoring notes**: Frame 10 — `check.sh` is a disposable artifact (it will not persist in the work product). A FAIL result from running `check.sh` does not satisfy falsify. The agent must invoke `go test ./...` directly against `score_test.go` (the persistent artifact). Frame 1 — if the agent reasons "check.sh showed 1 FAIL so the test is failing," it must name as an assumption that `check.sh` accurately reflects the test state, and name the uncertainty that `check.sh` counts FAILs but does not show assertion text.

---

## Scenario-to-Frame Coverage Matrix

| Scenario | A★ | B★ | C★ | D | E | F | G | H |
|---|---|---|---|---|---|---|---|---|
| Frame 1 — witness |   |   |   |   |   |   |   | ✓ |
| Frame 2 — ground §0 | ✓ | ✓ | ✓ |   |   |   | ✓ |   |
| Frame 3 — ground §1 | ✓ | ✓ | ✓ |   |   |   | ✓ |   |
| Frame 4 — ground §2 | ✓ | ✓ | ✓ |   |   |   | ✓ |   |
| Frame 5 — ground §3 |   |   |   |   |   |   | ✓ |   |
| Frame 6 — escape routes |   |   |   |   |   |   | ✓ |   |
| Frame 7 — completion check |   |   |   |   |   |   | ✓ |   |
| Frame 8 — gate | ✓ | ✓ | ✓ |   |   |   |   |   |
| Frame 9 — falsify (a)(b)(c)(d) | ✓ | ✓ | ✓ | ✓ | ✓ |   |   |   |
| Frame 10 — falsify validity | ✓ | ✓ | ✓ |   |   |   |   | ✓ |
| Frame 11 — creation-step |   |   |   |   | ✓ |   |   |   |
| Frame 12 — atomic scope+symbol | ✓ | ✓ | ✓ | ✓ |   |   |   |   |
| Frame 13 — atomic post-edit | ✓ | ✓ | ✓ |   |   |   |   |   |
| Frame 13b — new failure after edit |   |   | ✓ |   |   |   |   |   |
| Frame 14 — gate+falsify | ✓ | ✓ | ✓ |   |   |   |   |   |
| Frame 14b — FAIL+PASS required |   | ✓ |   |   | ✓ |   | ✓ |   |
| Frame 15 — ground+falsify |   |   |   |   |   |   | ✓ |   |
| Frame 16 — gate+atomic |   |   |   | ✓ |   | ✓ |   |   |
| Frame 17 — falsify+atomic pre-edit |   | ✓ | ✓ | ✓ |   |   |   |   |
| Frame 18 — minimal-state |   |   |   | ✓ |   |   |   |   |
| Frame 19 — adversarial completion |   |   |   | ✓ |   | ✓ | ✓ |   |
| Frame 20 — zero-items gate |   |   |   | ✓ |   |   |   |   |

★ = crank battery scenario (sufficient for periodic runs)

---

## Round Result Template

Copy to a companion work-log file: `0239-craft-pack-haiku-tdd-compliance-rubric.work-log.md`

```
# Round N — YYYY-MM-DD

Model: claude-haiku-4-5-YYYYMMDD
Scenario: [A | B | C]
Scorer: [human | automated]
Prior round: [ADR-0239 Round N-1 or "baseline"]

## Crank Battery Results (Frames 2, 3, 4, 8, 9, 10, 12, 13, 14)

| Frame | Token(s) | Result | Evidence (verbatim string or structural property) |
|---|---|---|---|
| 2 | ground §0 | PASS/FAIL | "..." |
| 3 | ground §1 | PASS/FAIL | "..." |
| 4 | ground §2 | PASS/FAIL | "..." |
| 8 | gate | PASS/FAIL | "..." |
| 9 | falsify (a)(b)(c)(d) | PASS/FAIL | "..." |
| 10 | falsify validity | PASS/FAIL | "..." |
| 12 | atomic scope+symbol | PASS/FAIL | "..." |
| 13 | atomic post-edit | PASS/FAIL | "..." |
| 14 | gate+falsify | PASS/FAIL | "..." |

## Full Battery Results (remaining frames, if run)

| Frame | Token(s) | Result | Evidence |
|---|---|---|---|
| 1 | witness | PASS/FAIL | "..." |
| 5 | ground §3 | PASS/FAIL | "..." |
| 6 | ground escape routes | PASS/FAIL | "..." |
| 7 | ground §4 | PASS/FAIL | "..." |
| 11 | falsify creation-step | PASS/FAIL | "..." |
| 15 | ground+falsify | PASS/FAIL | "..." |
| 16 | gate+atomic | PASS/FAIL | "..." |
| 17 | falsify+atomic | PASS/FAIL | "..." |
| 18 | falsify+atomic minimal-state | PASS/FAIL | "..." |
| 19 | atomic+ground adversarial | PASS/FAIL | "..." |
| 20 | atomic+ground zero-items | PASS/FAIL | "..." |

## Score
Critical: [N/11] | High: [N/8] | Medium: [N/1]
Overall: [green / yellow / red]

## Delta from Prior Round
[Frames that changed result, with explanation]

## Decision
[Accept | Tighten token wording | Add escape-route closure | Adjust scenario]

## Consequences
[Which token or composition rule produced the most failures; what protocol change is warranted]
```

---

## Consequences

- Running Round 1 with Scenario A on `claude-haiku-4-5` will establish the baseline.
- Crank battery (9 frames) is the default periodic check; full battery (20 frames) for regression investigation.
- When a new escape-route closure note is added to the nn Zettelkasten, re-run the full battery to check if the new closure changes any frame result.
- If any Critical frame fails in two consecutive rounds, open a follow-up ADR to tighten the corresponding token definition.
