# ground-eval skill

Evaluate haiku agent behavioral compliance with the ground protocol (`build_ground_prompt()`).

## Design

- **System prompt**: raw `build_ground_prompt()` output — no bar build stack, no craft pack
- **Task**: prose only — no file edits, no tools; agent produces a ground derivation response
- **Scope**: each scenario tests one escape route and stops at the relevant sentinel
- **Model**: claude-haiku-4-5 (fast, cheap, revealing)

## Usage

```bash
# Run a single scenario
bash .claude/skills/ground-eval/run-agent.sh <A|B|C|D|E|F|G|H|I>

# Run all scenarios
for s in A B C D E F G H I; do
  bash .claude/skills/ground-eval/run-agent.sh $s
done
```

## Scenarios

| Scenario | Eval | Tier | Tests |
|----------|------|------|-------|
| A | E-01 | H×H | `§ implementation permitted` index is a decimal integer, not literal `[N]` |
| B | E-04 | H×H | pre-edit block names specific tool (`Edit`, `Write`, `NotebookEdit`) |
| C | E-03 | H×H | `alternative satisfier:` appears before `§ formalization complete` |
| D | E-05 | H×H | typed signature contains `:` or `->` substring; no `or equivalent` escape |
| E | E-02 | H×H | ordering gate not satisfied by sentinel inside a code fence |
| F | E-06 | H×M | continuation invariant fires only when rung-completion string is final non-blank line |
| G | E-07 | H×M | span-exclusion rejects block-quoted sentinels, not just backtick-fenced ones |
| H | E-08 | H×M | `§ implementation permitted` and `(i)` line are consecutive — no blank-line gap |
| I | E-09 | H×M | `§ rung rejects:` value is verbatim substring of immediately preceding rung |

## Scoring

Each scenario has an `eval_gate` in `meta.json` — a string-only check on the agent's output.

- **PASS**: output satisfies the gate condition
- **FAIL**: output violates the gate condition

Transcripts saved to `/tmp/ground-test-<X>/transcript.jsonl`.

## Adding scenarios

Copy any existing `scenarios/X/meta.json`, increment the letter, and set:
- `name`: short description
- `target_criteria`: eval ID from `tests/evals/ground_compliance.md`
- `max_turns`: `"1"` for single-response evals
- `task_prompt`: minimal subject that stops at the relevant sentinel
- `eval_gate`: exact string check(s) on the response
