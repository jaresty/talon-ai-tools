---
name: craft-pack-eval
description: Set up a tmp scenario from ADR-0239, run a haiku agent through it using the craft pack (bar build make witness ground gate falsify atomic), score the transcript against the 20-frame battery, and output a filled round-result block for the work-log.
when_to_use: "Is the user asking to run a craft pack compliance evaluation or periodic crank check on a haiku agent? (yes/no)"
requires:
  - bash
  - go (1.21+)
  - bar CLI (bar build, bar help token)
  - claude CLI with --output-format stream-json support
args:
  - name: scenario
    description: "Letter A–H identifying the scenario from ADR-0239"
    required: true
  - name: round
    description: "Round number for the work-log entry (default: 1)"
    required: false
---

# craft-pack-eval

Runs one round of the ADR-0239 craft pack compliance evaluation against a haiku agent.

## When to invoke

Invoke with `/craft-pack-eval <scenario>` when:
- Running a periodic crank battery check (scenarios A, B, C — Critical frames only)
- Running a full battery investigation (scenarios D–H — specific excluded frames)
- Establishing a baseline for a new haiku model version

## Phases

### Phase 1 — Setup

Run the setup companion script for the named scenario:

```bash
bash .claude/skills/craft-pack-eval/setup.sh <scenario>
```

This creates `/tmp/haiku-test-<scenario>/`, initialises the Go module, writes the source
and test files from ADR-0239, and runs `go test ./...` to confirm the pre-state failure.

**Gate (falsifiable):**
- (a) absence signal: `setup.sh` exits non-zero, OR `go test` output does not contain
  the scenario's `EXPECT` string (defined in `setup.sh` per scenario)
- (b) presence signal: `setup.sh` exits 0 AND `go test` output contains `EXPECT`
- Gate is satisfied when: `grep -q "$EXPECT" <(cd /tmp/haiku-test-<X> && go test ./... 2>&1)`
  exits 0

Do not proceed to Phase 2 until this grep exits 0.

### Phase 2 — Haiku agent run

Run the agent companion script:

```bash
bash .claude/skills/craft-pack-eval/run-agent.sh <scenario>
```

This:
1. Runs `bar build make witness ground gate falsify atomic` to capture the system prompt
2. Loads the scenario task prompt from `setup.sh`
3. Invokes the haiku agent:
   ```bash
   claude -p "<task-prompt>" \
     --system-prompt "<craft-pack-system-prompt>" \
     --model claude-haiku-4-5 \
     --allowedTools "Bash,Read,Edit,Write" \
     --output-format stream-json --verbose \
     > /tmp/haiku-test-<scenario>/transcript.jsonl
   ```
4. Saves the stream-json transcript to `/tmp/haiku-test-<scenario>/transcript.jsonl`

**Gate (falsifiable):**
- (a) absence signal: `transcript.jsonl` does not exist, OR
  `grep '"type":"tool_result"' transcript.jsonl` exits non-zero
- (b) presence signal: file exists AND contains `"type":"tool_result"`
- Gate is satisfied when:
  `grep -q '"type":"tool_result"' /tmp/haiku-test-<scenario>/transcript.jsonl`
  exits 0

Do not proceed to Phase 3 until this grep exits 0.

### Phase 3 — Scoring

Read `/tmp/haiku-test-<scenario>/transcript.jsonl`. Extract the assistant text turns:

```bash
cat /tmp/haiku-test-<scenario>/transcript.jsonl \
  | jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text' \
  > /tmp/haiku-test-<scenario>/assistant-text.md
```

For each frame in the scenario's target frame list (from the coverage matrix in ADR-0239):

1. State the pass criterion for the frame (from ADR-0239 Scoring Rubric)
2. Search `assistant-text.md` (and tool-result blocks in `transcript.jsonl`) for the
   required string or structural property
3. Quote the verbatim evidence if found, or write `absent` if not
4. State PASS or FAIL

**Scoring rules:**
- Critical frame failure → overall FAIL regardless of other scores
- Evidence must be a verbatim quote from `transcript.jsonl` or `assistant-text.md`
- "I would have..." or prose narration does not count as a tool-result block
- A required tool-result block is absent if no `"type":"tool_result"` line in
  `transcript.jsonl` contains the required string

### Phase 4 — Output

Emit the filled round-result block using the template from ADR-0239 §Round Result Template.

Every `PASS/FAIL` cell must be filled. Every evidence cell must contain either a verbatim
quoted string or `absent`. A block containing any unfilled `PASS/FAIL` placeholder is not
complete — the Phase 4 gate is satisfied when `grep -q 'PASS/FAIL' <output>` exits non-zero
(i.e. the placeholder is gone).

---

## Companion scripts

### `setup.sh`

- Accepts scenario letter A–H as `$1`
- Creates `/tmp/haiku-test-$1/`
- Writes exact source/test files from ADR-0239 for that scenario
- Sets `EXPECT` to the exact string the pre-state `go test` output must contain
- Runs `go test ./...` and greps for `EXPECT`; exits non-zero if not found
- Prints the pre-state run output

See: `.claude/skills/craft-pack-eval/setup.sh`

### `run-agent.sh`

- Accepts scenario letter A–H as `$1`
- Loads the task prompt string for that scenario (defined inline per scenario)
- Captures `bar build make witness ground gate falsify atomic` output as system prompt
- Invokes `claude -p` with `--output-format stream-json --verbose`
- Saves to `/tmp/haiku-test-$1/transcript.jsonl`
- Greps for `"type":"tool_result"` and exits non-zero if absent

See: `.claude/skills/craft-pack-eval/run-agent.sh`

---

## Worked example

```
/craft-pack-eval A
```

**Phase 1**: `setup.sh A` runs → `/tmp/haiku-test-A/` created with empty `token.go` and
`token_test.go` containing `TestParseToken`. EXPECT=`build failed`. Pre-state run confirms:
`FAIL: github.com/haiku-test/a [build failed]`. Grep exits 0. Gate satisfied.

**Phase 2**: `run-agent.sh A` runs → haiku receives craft-pack system prompt + task "implement
parseToken in token.go". Transcript saved to `/tmp/haiku-test-A/transcript.jsonl`. Grep for
`"type":"tool_result"` exits 0. Gate satisfied.

**Phase 3**: Extract assistant text. Check Frame 2: search for a governing goal heading whose
text contains a literal substring of `build failed`. Found: `## Governing Goal: eliminate
'build failed' in go test ./...` — PASS. Check Frame 9: search for explicit (a)(b)(c)(d)
declarations. Found: `(a) --- FAIL (b) --- PASS (c) TestParseToken (d) token.go` — PASS.
Continue for Frames 3, 4, 8, 10, 12, 13, 14.

**Phase 4**: Emit filled round-result block. All 9 crank frames filled. Score: Critical 9/9.
Overall: green (if High frames also pass).

---

## Write to disk

Write this file to:
```
.claude/skills/craft-pack-eval/SKILL.md
```

Companion scripts:
```
.claude/skills/craft-pack-eval/setup.sh
.claude/skills/craft-pack-eval/run-agent.sh
```
