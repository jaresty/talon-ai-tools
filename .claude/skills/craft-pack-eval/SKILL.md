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

## Execution — run these steps in order

When this skill is invoked, execute all four phases sequentially using tool calls. Do not
describe what you would do — run the Bash tool calls directly.

### Phase 1 — Setup

Run:
```bash
bash .claude/skills/craft-pack-eval/setup.sh <scenario>
```

Read the output. Confirm it ends with `PASS: pre-state output contains expected string`.
If it exits non-zero or prints `FAIL:`, stop and report the error — do not proceed.

### Phase 2 — Haiku agent run

Run:
```bash
bash .claude/skills/craft-pack-eval/run-agent.sh <scenario>
```

This will take 1–3 minutes. Read the output. Confirm it ends with
`PASS: transcript contains N tool_result block(s)`.
If it exits non-zero or prints `FAIL:`, stop and report the error — do not proceed.

### Phase 3 — Scoring

Extract assistant text from the transcript:
```bash
cat /tmp/haiku-test-<scenario>/transcript.jsonl \
  | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    try:
        obj = json.loads(line)
        if obj.get('type') == 'assistant':
            for block in obj.get('message', {}).get('content', []):
                if block.get('type') == 'text':
                    print(block['text'])
    except: pass
" > /tmp/haiku-test-<scenario>/assistant-text.md
cat /tmp/haiku-test-<scenario>/assistant-text.md
```

Then read `assistant-text.md` and `transcript.jsonl`. For each frame in the scenario's
target frame list (coverage matrix in ADR-0239), apply the pass criterion:

1. Quote the specific string or structural property being checked
2. Search the transcript for it — use Bash grep if needed:
   ```bash
   grep -n "<string>" /tmp/haiku-test-<scenario>/assistant-text.md
   ```
3. State PASS or FAIL with verbatim evidence quoted from the transcript, or `absent`

**Scoring rules:**
- Critical frame failure → overall FAIL regardless of other scores
- Evidence must be a verbatim quote — not paraphrase, not inference
- Prose narration ("I would now run...") does not count as a tool-result block
- A tool-result block is absent if no line in `transcript.jsonl` matching
  `"type":"tool_result"` contains the required string

### Phase 4 — Output

Emit the filled round-result block (template from ADR-0239 §Round Result Template).
Every cell must contain `PASS` or `FAIL` plus a quoted evidence string or `absent`.
No `PASS/FAIL` placeholder may remain in the output.

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
