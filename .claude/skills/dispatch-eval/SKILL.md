# dispatch-eval skill

Evaluate haiku agent compliance with bar sequence dispatch protocols (ADR-0240).

## Usage

```bash
# Setup a scenario (creates /tmp/dispatch-test-<X>)
bash .claude/skills/dispatch-eval/setup.sh <M|N|O|P|Q|R>

# Run haiku agent against a scenario
BAR_CMD=/tmp/bar-new bash .claude/skills/dispatch-eval/run-agent.sh <M|N|O|P|Q|R>

# Run all scenarios
for s in M N O P Q R; do
  bash .claude/skills/dispatch-eval/setup.sh $s
  BAR_CMD=/tmp/bar-new bash .claude/skills/dispatch-eval/run-agent.sh $s
done
```

## Scenarios

| Scenario | Criterion | Tests |
|----------|-----------|-------|
| M | A | bar build gate — step must be preceded by bar build tool result |
| N | B | token fidelity — bar build token list matches step spec verbatim |
| O | C | chain integrity — --subject contains literal substring from prior step output |
| P | E | mode protocol — handoff/cycle prompt emitted at required boundary |
| Q | G | fan_out execution — one Agent call per frame, not batched |
| R | H | join completeness — all tool_results present before synthesis |

## Scoring

All scenarios require manual scoring — review the transcript against the rubric line in ADR-0240.

**Score thresholds (per ADR-0240):**
- Green: All 4 Critical (A/B/C/G) PASS + both High (E/H) PASS
- Yellow: All 4 Critical PASS + at least 1 High PASS
- Red: Any Critical FAIL

## Eval gate (automated check)

`run-agent.sh` prints the eval gate string at the end of each run. The gate is a necessary but
not sufficient condition for PASS — it catches the most obvious violations. Full scoring requires
reading the transcript.

## Infrastructure notes

- Transcripts saved to `/tmp/dispatch-test-<X>/transcript.jsonl`
- Agent allowed tools: Bash, Read, Edit, Write, Agent (Agent tool needed for fan_out scenarios Q/R)
- `BAR_CMD` env var overrides the bar binary (use `/tmp/bar-new` for dev builds)
- No Go module setup needed — all scenarios are prose/dispatch tasks, not software tasks
