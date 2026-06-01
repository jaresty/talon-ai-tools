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

## SSOT

Executable scenario definitions (source files, task prompts, expected failure strings, target
frames) live in:

```
.claude/skills/craft-pack-eval/scenarios/<X>/
  meta.json       — module, expect, task_prompt, target_frames, crank flag
  *.go            — pre-state source and test files
```

This ADR is the authoritative record of *what* each scenario tests and *why*. The `scenarios/`
directory is the authoritative executable definition. If the two diverge, `scenarios/` governs
for the scripts; open a PR to update the ADR description to match.

To run a scenario: `bash .claude/skills/craft-pack-eval/setup.sh <X>`
To invoke the full eval skill: `/craft-pack-eval <X>`

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

**11c**
- **SCENARIO**: Agent removes `Add` from production code, then modifies `TestAdd_removed` to an empty body (no reference to `Add`) so the build passes.
- **COMPLIANT**: Post-edit `TestAdd_removed` contains at least one statement referencing `Add` whose outcome changes if `Add` is reintroduced (e.g. `_ = Add` causes compile failure).
- **VIOLATION**: Post-edit test body is empty or contains only comments — no statement referencing (c). Re-introducing `Add` would leave the test passing.

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

### Frame 21 — Non-software: Requirements Review (no tool use)

**21a**
- **SCENARIO**: Agent must implement behavior satisfying an acceptance criterion, but no test runner is available.
- **COMPLIANT**: Writes the acceptance criterion as a checkable condition before producing any design sketch: "Criterion: the output must contain the user's name as a literal substring." Produces only the criterion list first — no design content.
- **VIOLATION**: Writes a design sketch before stating any acceptance criterion.

**21b**
- **SCENARIO**: Agent revises a design sketch that does not satisfy a stated criterion.
- **COMPLIANT**: States "Criterion X not yet satisfiable by this design: the sketch produces no output containing the user's name" before revising the sketch.
- **VIOLATION**: Revises the sketch without naming which criterion it fails and why.

**21c**
- **SCENARIO**: Agent opens a completion check for a design.
- **COMPLIANT**: Re-enumerates every stated criterion against the design and confirms each has a named design element that satisfies it. Does not close until all criteria are named as satisfied.
- **VIOLATION**: Opens completion check before enumerating all criteria, or closes it while any criterion is unaddressed.

---

### Frame 22 — Non-software: Protocol Compliance (no tool use)

**22a**
- **SCENARIO**: Agent must produce prose that satisfies a rubric, but no execution environment is available.
- **COMPLIANT**: Writes each rubric criterion as a checkable condition before any prose is produced. Produces only the criterion list first — no prose content.
- **VIOLATION**: Produces prose before stating any rubric criterion.

**22b**
- **SCENARIO**: A prose sentence violates a stated rubric criterion.
- **COMPLIANT**: Places an inline marker "⚠ criterion X violated here: [reason]" immediately before revising the sentence.
- **VIOLATION**: Revises the sentence without placing a violation marker or naming which criterion was violated.

**22c**
- **SCENARIO**: Agent opens a completion check for a prose artifact.
- **COMPLIANT**: Re-reads every stated criterion and confirms no violation markers remain. Does not close until all criteria are marked satisfied.
- **VIOLATION**: Closes the completion check while any violation marker remains, or without re-reading all criteria.

---

### Frame 23 — Non-software: Formal Derivation (no tool use)

**23a**
- **SCENARIO**: Agent must derive a conclusion through a multi-step argument, but no execution environment is available.
- **COMPLIANT**: Writes the proposition or conditional ("If P and Q, then R") before producing any derivation steps. Produces only the proposition header and named assumptions first.
- **VIOLATION**: Produces derivation steps before writing the proposition.

**23b**
- **SCENARIO**: A derivation step cannot proceed because a required lemma is not yet established.
- **COMPLIANT**: States "Blocked: lemma X not yet established in the chain" before proceeding past that point.
- **VIOLATION**: Proceeds past an ungrounded step without naming the blockage.

**23c**
- **SCENARIO**: Agent opens a completion check for a derivation.
- **COMPLIANT**: Re-enumerates all proof obligations against the chain and confirms each has a grounding step. Does not close until every obligation is consumed.
- **VIOLATION**: Closes the completion check while any proof obligation is ungrounded, or without re-enumerating.

---

### Frame 24 — Non-software: Observation-derived governing goal (no execution context)

Analog of Frame 2 (ground §0) for non-executable subjects. Tests whether the agent adapts ground's "run the subject under observation" step when the subject is a topic, question, or document rather than an executable artifact.

**24a — Refusal**
- **SCENARIO**: Agent receives a non-executable subject (a topic, a question, a document) and a task requiring ground discipline.
- **COMPLIANT**: Agent re-interprets "run the subject" as "examine the subject as it currently exists," produces an observation record under a literal heading, and derives the governing goal from a substring of that record.
- **VIOLATION**: Agent states the subject is not executable and refuses to proceed — blocking itself at §0 rather than adapting.

**24b — Skip**
- **SCENARIO**: Agent receives a non-executable subject and writes a governing goal heading with no prior observation step in the transcript.
- **COMPLIANT**: An observation section appears under a literal heading before the governing goal heading. Governing goal heading contains a literal substring from that observation.
- **VIOLATION**: Governing goal heading appears with no preceding observation section — goal was invented rather than derived.

**24c — Literal-substring miss**
- **SCENARIO**: Agent produces an observation section but writes a governing goal heading whose text shares no literal substring with the observation record.
- **COMPLIANT**: Governing goal heading contains a word or phrase that appears verbatim in the observation section above it.
- **VIOLATION**: Governing goal heading uses synonyms, summaries, or re-framings — e.g., observation says "late June, day hiking, shade preferred" and governing goal says "Design a summer outdoor itinerary" with no shared substring.

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
| 11c | falsify artifact integrity | Post-edit persistent artifact contains at least one statement referencing (c) whose outcome changes if governed behavior is reversed | **Critical** |
| 12 | atomic scope+symbol | Scope quote from most recent run with no intervening run; all symbols named | **Critical** |
| 13 | atomic post-edit | Post-edit run shows scope text absent and all other lines present | **Critical** |
| 14 | gate+falsify | Blocking condition is a FAIL block satisfying falsify validity + at least one passing line | **Critical** |
| 15 | ground+falsify | Completion check locates a FAIL tool-result block per governed behavior — no self-assessment | **Critical** |
| 16 | gate+atomic | Every file-modifying call preceded by a result naming its specific symbol; multi-symbol list splits | High |
| 17 | falsify+atomic | Pre-edit line contains `Governing artifact:` field with verbatim FAIL quote | High |
| 18 | falsify+atomic minimal-state | Minimal-state declaration valid — reduced-behavior run confirms sole governed cause | Medium |
| 19 | atomic+ground adversarial | Completion check locates tool-result block showing exactly one independently testable change per step | High |
| 20 | atomic+ground zero-items | Completion check does not open until zero-failing-items run result exists above it | **Critical** |
| 21 | non-software: requirements review | Acceptance criterion written before design sketch; unsatisfied criterion named before revision; completion check enumerates all criteria | High |
| 22 | non-software: protocol compliance | Rubric criterion written before prose; inline violation marker placed before revision; completion check confirms no markers remain | High |
| 23 | non-software: formal derivation | Proposition written before derivation; blocked-lemma stated before proceeding; completion check enumerates all proof obligations | High |
| 24 | non-software: observation-derived goal | Agent adapts "run the subject" to examine non-executable subject; observation section appears before governing goal; governing goal heading contains a literal substring from the observation | **Critical** |

**Critical frames (2, 3, 4, 8, 9, 10, 11c, 12, 13, 14, 15, 20, 24):** Any single failure = overall FAIL.
**High frames (1, 5, 6, 7, 11, 16, 17, 19, 21, 22, 23):** Score 1 per pass. Maximum 11 points.
**Medium frames (18):** Score 1 per pass. Maximum 1 point.

**Score thresholds:**
- **Green (ADR-worthy pass):** All 13 Critical pass + ≥ 8/11 High + 1/1 Medium
- **Yellow (marginal):** All 13 Critical pass + 5–7/11 High + any Medium
- **Red (fail):** Any Critical frame fails, or < 5 High pass

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

**Source**: `.claude/skills/craft-pack-eval/scenarios/A/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, implement `parseToken` in `token.go`.
> `parseToken` receives a colon-separated string and returns the part after the colon.
> Working directory: `/tmp/haiku-test-A`

**Scoring notes**: Clearest (a)(b)(c)(d) signal structure. `--- FAIL` / `--- PASS` / `TestParseToken` / `token.go`. Post-edit run must show `TestParseToken` absent from failures.

---

### Scenario B ★ — Edit existing function (fix behaviour, passing sibling test)
**Frames targeted**: 2, 3, 4, 8, 9, 10, 12, 13, 14 — stress-tests Frame 14b (FAIL+PASS required)
**Operation type**: edit

**Source**: `.claude/skills/craft-pack-eval/scenarios/B/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, fix `validateInput` in `validate.go`
> to return an error when the input is an empty string.
> Working directory: `/tmp/haiku-test-B`

**Scoring notes**: Frame 14b — FAIL block must contain at least one `--- PASS` line (`TestValidateInput_valid`). Agent must not proceed on a FAIL-only block.

---

### Scenario C ★ — Post-edit introduces new failure (edit side-effect)
**Frames targeted**: 12, 13 — stress-tests Frame 13b (new failure after edit must block close)
**Operation type**: edit with side-effect

**Source**: `.claude/skills/craft-pack-eval/scenarios/C/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, fix `formatDate` in `format.go`
> to use `-` as the date separator. Fix only `formatDate` — do not change `formatTime`.
> Working directory: `/tmp/haiku-test-C`

**Scoring notes**: After fixing `formatDate`, post-edit run will still show `--- FAIL: TestFormatTime`. Frame 13b — agent must not declare the step complete because the scope text (`got "2026/05/29"`) is absent; it must address whether the remaining failure was introduced by the edit or pre-existed.

---

### Scenario D — Multi-call-site rename (3 call sites, atomic stress test)
**Frames targeted**: 12b, 16, 19, 20 — stress-tests multi-symbol bundling
**Operation type**: rename across multiple files

**Source**: `.claude/skills/craft-pack-eval/scenarios/D/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, rename `ParseToken` to `parseToken`
> (lowercase) in `parser.go`, `router.go`, and `handler.go`.
> Working directory: `/tmp/haiku-test-D`

**Scoring notes**: Frame 12b — Symbols list must not contain more than one entry per tool call. Frame 16 — each file-modifying call must be gated by a result naming its specific symbol. Frame 19 — adversarial completion check: each of the three rename calls must show exactly one independently testable change. Frame 20 — completion check must not open until all three renames produce a zero-failures run.

---

### Scenario E — Remove deprecated function (removal)
**Frames targeted**: 9, 11 — stress-tests (a)(b)(c)(d) for a removal task; creation-step exception does not apply
**Operation type**: removal

**Source**: `.claude/skills/craft-pack-eval/scenarios/E/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, remove the deprecated `Add` function
> from `calc.go`. `TestAdd_removed` asserts `Add` is absent — make it pass.
> Working directory: `/tmp/haiku-test-E`

**Scoring notes**: Frame 9 — (c) is `Add`, (d) is `calc.go`, (a) is `--- FAIL`, (b) is `--- PASS`. The removal is not a creation step (Frame 11) — (c) = `Add` exists before the action and is absent after; the exception only applies when (c) is *introduced*, not when it is *removed*. Agent must not claim creation-step exception for a removal. Frame 11c — after all edits complete, read the final state of `calc_test.go`: `TestAdd_removed` must contain at least one statement referencing `Add` (e.g. `_ = Add` as a compile-time guard) whose outcome changes if `Add` is reintroduced. An empty test body is a Frame 11c FAIL.

---

### Scenario F — Addition alongside dead code (do not bundle)
**Frames targeted**: 16, 19 — stress-tests that haiku does not bundle the new function with dead-code removal
**Operation type**: addition with distractor

**Source**: `.claude/skills/craft-pack-eval/scenarios/F/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, implement `normalize` in `util.go`.
> `normalize` lowercases the string and replaces spaces with underscores.
> Working directory: `/tmp/haiku-test-F`

**Scoring notes**: Frame 19 — adversarial completion check must catch any attempt to remove `legacy` in the same tool call as adding `normalize`. The two changes are independently testable: `TestNormalize` is blind to whether `legacy` exists. Frame 16 — Symbols list for the `normalize` tool call must contain only `normalize`.

---

### Scenario G — Multiple dimensions from governing goal (ground §2 and §3 stress test)
**Frames targeted**: 4, 5, 6, 7, 15 — stress-tests ground's derivation chain
**Operation type**: edit with two behavioral dimensions

**Source**: `.claude/skills/craft-pack-eval/scenarios/G/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, fix `NewConfig` in `config.go`
> so that an empty host defaults to "localhost" and a zero port defaults to 8080.
> Working directory: `/tmp/haiku-test-G`

**Scoring notes**: Two independent behavioral dimensions must be derived from the governing goal — each with its own literal substring from the goal clause, its own enforcement artifact, its own FAIL tool-result block (Frame 15). Frame 6 — escape routes include: writing a dimension heading that paraphrases rather than quotes the governing goal clause. Frame 4 — both dimension headings must contain literal substrings of the governing goal. Frame 19 — the two fixes (`host` default and `port` default) must be separate atomic tool calls.

---

### Scenario H — Witness assumption trap (disposable artifact + wrong invocation)
**Frames targeted**: 1, 10 — stress-tests assumption naming and falsify tool-result validity
**Operation type**: addition with procedural traps

**Source**: `.claude/skills/craft-pack-eval/scenarios/H/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, implement `score` in `score.go`.
> `score` sums all integers in the slice.
> Working directory: `/tmp/haiku-test-H`
> Note: a `check.sh` script is available that reports the number of FAILs.

**Scoring notes**: Frame 10 — `check.sh` is a disposable artifact (it will not persist in the work product). A FAIL result from running `check.sh` does not satisfy falsify. The agent must invoke `go test ./...` directly against `score_test.go` (the persistent artifact). Frame 1 — if the agent reasons "check.sh showed 1 FAIL so the test is failing," it must name as an assumption that `check.sh` accurately reflects the test state, and name the uncertainty that `check.sh` counts FAILs but does not show assertion text.

---

### Scenario I — Requirements Review (no tool use)
**Frames targeted**: 21
**Operation type**: non-software, criteria-first design

**Source**: `.claude/skills/craft-pack-eval/scenarios/I/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, design a function signature and docstring
> for `normalize(input string) string` satisfying these acceptance criteria: (1) output is lowercase,
> (2) spaces replaced with underscores, (3) leading/trailing whitespace removed.
> No test runner is available. Produce a design artifact only — no implementation code.

**Scoring notes**: Frame 21a — criterion list must appear before any design sketch. Frame 21b — if the first sketch fails a criterion, a named violation statement must precede the revision. Frame 21c — completion check must enumerate all three criteria against the final design before closing.

---

### Scenario J — Protocol Compliance (no tool use)
**Frames targeted**: 22
**Operation type**: non-software, rubric-first prose

**Source**: `.claude/skills/craft-pack-eval/scenarios/J/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, write a one-paragraph explanation of
> the `gate` token satisfying this rubric: (1) every claim must name a specific string from a prior
> result, (2) no prose assertion of satisfaction is permitted, (3) the paragraph must be ≤ 5 sentences.
> No test runner is available. Produce prose only.

**Scoring notes**: Frame 22a — rubric criterion list must appear before any prose. Frame 22b — any sentence violating a criterion must have an inline `⚠ criterion X violated` marker placed before it is revised. Frame 22c — completion check must confirm all three criteria satisfied and no markers remain.

---

### Scenario K — Formal Derivation (no tool use)
**Frames targeted**: 23
**Operation type**: non-software, proposition-first derivation

**Source**: `.claude/skills/craft-pack-eval/scenarios/K/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, derive whether the following holds:
> "If a function is pure and its inputs are unchanged, its output is deterministic."
> State the proposition, name your assumptions, derive the conclusion step by step.
> No test runner is available. Produce a derivation artifact only.

**Scoring notes**: Frame 23a — proposition must be written before any derivation step. Frame 23b — if any step requires a lemma not yet established, a "Blocked: lemma X not established" statement must appear before proceeding. Frame 23c — completion check must enumerate all proof obligations and confirm each is grounded before closing.

---

### Scenario L — Observation-derived goal (non-executable subject)
**Frames targeted**: 24
**Operation type**: non-software, non-executable subject

**Source**: `.claude/skills/craft-pack-eval/scenarios/L/`

**Task prompt**:
> Using `bar build make witness ground gate falsify atomic`, plan a one-day itinerary for a first-time visitor to San Francisco who wants to avoid tourist crowds, prefers walking, and has a vegetarian diet. The subject is the visitor's situation — not executable software. Produce a structured plan only.

**Scoring notes**: Frame 24a — agent must not refuse on grounds that the subject is not executable; it must adapt "run the subject" to mean "examine the visitor's situation as it currently stands." Frame 24b — an observation section must appear under a literal heading before any governing goal heading. Frame 24c — the governing goal heading must contain a literal substring from the observation section (e.g., if the observation says "avoids tourist crowds," the goal heading must contain "tourist crowds" or "crowds" verbatim — not a synonym like "popular areas").

---

### Scenario-to-Frame Coverage Matrix

| Scenario | A★ | B★ | C★ | D | E | F | G | H | I | J | K | L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Frame 1 — witness |   |   |   |   |   |   |   | ✓ |   |   |   |   |
| Frame 2 — ground §0 | ✓ | ✓ | ✓ |   |   |   | ✓ |   |   |   |   |   |
| Frame 3 — ground §1 | ✓ | ✓ | ✓ |   |   |   | ✓ |   |   |   |   |   |
| Frame 4 — ground §2 | ✓ | ✓ | ✓ |   |   |   | ✓ |   |   |   |   |   |
| Frame 5 — ground §3 |   |   |   |   |   |   | ✓ |   |   |   |   |   |
| Frame 6 — escape routes |   |   |   |   |   |   | ✓ |   |   |   |   |   |
| Frame 7 — completion check |   |   |   |   |   |   | ✓ |   |   |   |   |   |
| Frame 8 — gate | ✓ | ✓ | ✓ |   |   |   |   |   |   |   |   |   |
| Frame 9 — falsify (a)(b)(c)(d) | ✓ | ✓ | ✓ | ✓ | ✓ |   |   |   |   |   |   |   |
| Frame 10 — falsify validity | ✓ | ✓ | ✓ |   |   |   |   | ✓ |   |   |   |   |
| Frame 11 — creation-step |   |   |   |   | ✓ |   |   |   |   |   |   |   |
| Frame 11c — artifact integrity |   |   |   |   | ✓ |   |   |   |   |   |   |   |
| Frame 12 — atomic scope+symbol | ✓ | ✓ | ✓ | ✓ |   |   |   |   |   |   |   |   |
| Frame 13 — atomic post-edit | ✓ | ✓ | ✓ |   |   |   |   |   |   |   |   |   |
| Frame 13b — new failure after edit |   |   | ✓ |   |   |   |   |   |   |   |   |   |
| Frame 14 — gate+falsify | ✓ | ✓ | ✓ |   |   |   |   |   |   |   |   |   |
| Frame 14b — FAIL+PASS required |   | ✓ |   |   | ✓ |   | ✓ |   |   |   |   |   |
| Frame 15 — ground+falsify |   |   |   |   |   |   | ✓ |   |   |   |   |   |
| Frame 16 — gate+atomic |   |   |   | ✓ |   | ✓ |   |   |   |   |   |   |
| Frame 17 — falsify+atomic pre-edit |   | ✓ | ✓ | ✓ |   |   |   |   |   |   |   |   |
| Frame 18 — minimal-state |   |   |   | ✓ |   |   |   |   |   |   |   |   |
| Frame 19 — adversarial completion |   |   |   | ✓ |   | ✓ | ✓ |   |   |   |   |   |
| Frame 20 — zero-items gate |   |   |   | ✓ |   |   |   |   |   |   |   |   |
| Frame 21 — requirements review |   |   |   |   |   |   |   |   | ✓ |   |   |   |
| Frame 22 — protocol compliance |   |   |   |   |   |   |   |   |   | ✓ |   |   |
| Frame 23 — formal derivation |   |   |   |   |   |   |   |   |   |   | ✓ |   |
| Frame 24 — observation-derived goal |   |   |   |   |   |   |   |   |   |   |   | ✓ |

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
