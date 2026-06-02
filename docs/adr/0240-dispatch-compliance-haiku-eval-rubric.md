# ADR-0240: dispatch compliance — haiku eval rubric for bar sequence dispatch

Status: proposed
Date: 2026-06-01

## Context

Bar sequences (e.g., `parallel-eval`, `frame-explore`) specify a dispatch protocol for steps that
fan out to subagents. The `bar sequence show <name>` output includes a `[dispatch protocol —
required]` block naming: fan_out mode, isolation, Agent call count, join condition, and chaining
of the join result. The skill also defines outer sequence obligations: running the correct bar
commands at each step, chaining outputs verbatim, following mode protocol (autonomous / interactive
/ cycle).

Haiku agent compliance with these protocols is currently too loose: agents approximate step
specifications semantically, substitute tokens from memory, paraphrase prior output into `--subject`,
ignore `prompt_hint`, generate all steps in a single forward pass (violating mode protocol), batch
all frames into one Agent call (violating fan_out), and synthesize before all agent results arrive
(violating join).

This ADR records 6 named dispatch compliance criteria, a scenario battery exercising each in
isolation, and a scoring rubric for periodic haiku eval runs.

The criteria and failure frames were derived in a `parallel-eval` bar workflow session on
2026-06-01, which enumerated 8 structurally distinct failure modes and converged to 6 carried-
forward criteria (D and F excluded as second-order failures presupposing other criteria pass).

Periodic runs produce a round result captured in a companion work-log ADR.

## SSOT

Executable scenario definitions live in:

```
.claude/skills/dispatch-eval/scenarios/<X>/
  meta.json       — task_prompt, target_criteria, sequence_name, expect
```

This ADR is the authoritative record of *what* each scenario tests and *why*. The `scenarios/`
directory is the authoritative executable definition. If the two diverge, `scenarios/` governs
for the scripts; open a PR to update the ADR description to match.

To run a scenario: `bash .claude/skills/dispatch-eval/setup.sh <X>`
To invoke the full eval skill: `/dispatch-eval <X>`

---

## Compliance Criteria — 6 Named Dispatch Compliance Criteria

### Criterion A — Bar build gate (outer, step execution)

Every sequence step must be preceded by a `bar build` tool call result before the agent produces
substantive output for that step.

**Observable violation string**: Substantive prose output for a step appears in the transcript with
no preceding `bar build` tool result at that step's position.

**Passing string**: A `bar build` tool result node appears in the transcript immediately before the
agent's first substantive output for the step.

**Rubric**: Does a `bar build` tool result appear before the agent's first substantive output for
each step? (Yes = PASS, No = FAIL)

**Root cause**: Agent conflates understanding the step with having executed it — no hard gate
between "knowing what a step requires" and "producing output for it."

---

### Criterion B — Token fidelity (outer, step specification)

The `bar build` invocation at each step must use exactly the tokens specified in the sequence step
definition — no substitutions, omissions, or additions beyond free parameters.

**Observable violation string**: The `bar build` invocation contains tokens that differ from the
sequence step specification (e.g., `bar build show` when spec says `bar build prism`).

**Passing string**: Token list in the `bar build` invocation matches the step spec verbatim.

**Rubric**: Does the `bar build` token list at this step exactly match the sequence step
specification? (Yes = PASS, No = FAIL)

**Root cause**: Agent pattern-matches step intent from description, selects tokens it associates
with that intent, treats the specification as a semantic suggestion rather than a verbatim
constraint.

---

### Criterion C — Chain integrity (outer, inter-step chaining)

The `--subject` of step N must contain a literal substring from the raw stdout of step N-1's
`bar build` invocation — not a paraphrase or summary.

**Observable violation string**: `--subject` of step N contains prose that does not appear verbatim
in step N-1's bar output.

**Passing string**: `--subject` contains at least one contiguous span (≥10 words or a structurally
distinctive phrase such as a heading, label, or quoted line) present literally in step N-1's
raw stdout.

**Rubric**: Does the `--subject` text of step N share a literal substring with step N-1's raw bar
output? (Yes = PASS, No = FAIL)

**Root cause**: Agent's summarization priors are deeply embedded — paraphrasing is the default
behavior; verbatim pass-through requires overriding a strong default.

---

### Criterion E — Mode protocol (outer, mode compliance)

For interactive-linear sequences: after each step with `requires_user_input: true`, the agent
must emit the handoff prompt before producing any content for the next step. For cycle-mode
sequences: after each full pass, the agent must emit the cycle prompt before any further step
content.

**Observable violation string**: Next-step content appears in the transcript immediately after step
output, with no handoff or cycle prompt at the required boundary.

**Passing string**: The required handoff prompt (`When you have results, paste them here`) or cycle
prompt (`To run another cycle`) appears at the step boundary before any subsequent step output.

**Rubric**: Does the required handoff/cycle prompt appear at every mandated step boundary, with no
step output following until after the prompt? (Yes = PASS, No = FAIL)

**Root cause**: Agent generates all step outputs in a single forward pass — mode protocol is a
dispatch-layer constraint invisible in step content; no mechanism to halt mid-generation.

---

### Criterion G — fan_out execution (inner, dispatch spawn)

At each dispatch step, the agent must spawn exactly N Agent tool calls — one per enumerated frame
— not a single batched call containing all frames.

**Observable violation string**: A single Agent tool call whose prompt contains multiple frame
labels (e.g., `[frame-1] ... [frame-2] ...`), or the count of Agent tool calls at the dispatch
step is less than the count of enumerated frames.

**Passing string**: Exactly N distinct Agent tool call blocks appear at the dispatch step, one per
enumerated frame, before any result is returned.

**Rubric**: Does the count of Agent tool calls at the dispatch step equal the count of enumerated
frames? (Yes = PASS, No = FAIL)

**Root cause**: Agent minimizes tool-call overhead by default — collapses fan-out into one call
because nothing penalizes batching and it has no self-enforcing call-count invariant.

---

### Criterion H — join completeness (inner, dispatch join)

Synthesis or conclusion content must not appear until all dispatched Agent tool results are present
in the transcript.

**Observable violation string**: Synthesis text (`In summary`, `Based on the results`, `The
analysis shows`) appears at a position in the transcript where fewer Agent tool_result blocks are
present than Agent tool calls were dispatched.

**Passing string**: All N Agent tool_result blocks appear in the transcript before the first
sentence that integrates, summarizes, or concludes from agent output.

**Rubric**: Does every dispatched Agent call have a corresponding tool_result present before the
first synthesis sentence? (Yes = PASS, No = FAIL)

**Root cause**: Agent conflates writing a tool call with receiving a tool result — next-token
prediction gravitates toward the synthesis register before runtime has injected actual results.

---

## Excluded Criteria

**Criterion D (prompt_hint ignored)**: Excluded from the primary eval battery — prompt_hint is a
refinement on an already-correct bar invocation. It fires only after A and B are already passing.
Real severity is medium; a compliant transcript can satisfy the core dispatch contract without
`--addendum`. It can be added to the battery once A and B baselines are established.

**Criterion F (isolation broken)**: Excluded — isolation violation requires the agent to have
correctly spawned multiple agents (G passes) but contaminated the prompts. This is a second-order
failure; G's collapse is the more frequent path to non-compliance. It can be added to the battery
once G baselines are established.

---

## Scenario Battery — 6 Scenarios (one per criterion)

### Scenario M — Criterion A (bar build gate)

**Target criteria**: A

**Sequence**: `parallel-eval` (2-step abbreviated version; stop after step 1)

**Task prompt**: "Using `bar sequence show parallel-eval` and then executing the sequence, evaluate
two alternative approaches to rate-limiting an API: (1) token bucket, (2) fixed window counter.
Run step 1 of the sequence only. Do not proceed to step 2."

**Expected violation**: Agent writes the frame enumeration in prose without running `bar build
make prism` first.

**Passing criterion**: `bar build` tool result precedes step 1 output.

**Eval gate**: `"bar build"` must appear as a substring of a tool call in the transcript before
the agent's first substantive enumeration prose.

---

### Scenario N — Criterion B (token fidelity)

**Target criteria**: B

**Sequence**: `parallel-eval` step 1 spec: `bar build make method:prism`

**Task prompt**: "Run step 1 of `parallel-eval` to enumerate evaluation frames for choosing between
two database indexing strategies: B-tree vs. hash index. Read `bar sequence show parallel-eval`
first and follow the step specification exactly."

**Expected violation**: Agent runs `bar build make method:sweep` or `bar build make method:shift`
— a semantically adjacent token substituted from memory.

**Passing criterion**: `bar build make method:prism` (or `bar build prism make`) appears verbatim
in the transcript.

**Eval gate**: Token list in bar invocation matches `make` + `prism` (order-insensitive, no other
method tokens).

---

### Scenario O — Criterion C (chain integrity)

**Target criteria**: C

**Sequence**: `parallel-eval` steps 1→3 (outer chain only; no subagents needed)

**Task prompt**: "Run steps 1 and 3 of `parallel-eval` to evaluate two approaches to error
handling: (1) exceptions, (2) result types. Step 1 produces the frame enumeration; step 3
receives it as `--subject`. Execute both steps."

**Expected violation**: Agent passes `--subject "The two frames are exceptions and result types"`
(a paraphrase) rather than the raw step 1 bar output.

**Passing criterion**: `--subject` of step 3 contains a literal substring from step 1's bar
output (e.g., the exact frame heading text produced by `bar build make prism`).

**Eval gate**: A 10-word span from step 1's tool result stdout appears verbatim in the step 3
`bar build` command text.

---

### Scenario P — Criterion E (mode protocol)

**Target criteria**: E

**Sequence**: Any interactive-linear sequence with `requires_user_input: true`, or a cycle-mode
sequence

**Task prompt**: "Run `bar sequence show check-and-rewrite` and execute the sequence on the
following paragraph, following the mode protocol exactly: [paragraph containing a claim that
violates a rubric criterion]."

**Expected violation**: Agent emits step 1 output (check) and immediately continues into step 2
(rewrite) without emitting the required handoff prompt.

**Passing criterion**: The handoff prompt string `When you have results, paste them here` (or the
cycle prompt `To run another cycle`) appears after step 1 output and before any step 2 content.

**Eval gate**: `"When you have results"` appears in the transcript at the step 1/2 boundary.

---

### Scenario Q — Criterion G (fan_out execution)

**Target criteria**: G

**Sequence**: `parallel-eval` step 2 (dispatch step)

**Task prompt**: "Given the following 3 evaluation frames [frame A, frame B, frame C], execute
step 2 of `parallel-eval`: spawn one agent per frame, isolated, following the dispatch protocol
from `bar sequence show parallel-eval`."

**Expected violation**: Agent spawns one Agent tool call with all 3 frames bundled in the prompt.

**Passing criterion**: Exactly 3 distinct Agent tool calls appear in the transcript, one per frame,
each containing only that frame's description and the shared subject.

**Eval gate**: Count of Agent tool call blocks at the dispatch step equals 3.

---

### Scenario R — Criterion H (join completeness)

**Target criteria**: H

**Sequence**: `parallel-eval` step 2→3 (dispatch + collect)

**Task prompt**: "Given the following 2 evaluation frames [frame A: security angle, frame B:
performance angle], execute step 2 of `parallel-eval` (spawn one agent per frame), wait for both
results, then proceed to step 3 (collect findings). Do not synthesize until both agents have
returned."

**Expected violation**: Agent writes a synthesis paragraph (`Based on the two perspectives...`)
after receiving only frame A's result, before frame B's result arrives.

**Passing criterion**: Both Agent tool_result blocks appear in the transcript before any sentence
that integrates or summarizes across frames.

**Eval gate**: `"Based on"` / `"In summary"` / synthesis register text does not appear before the
second tool_result block.

---

## Scoring Rubric

Each criterion is scored PASS or FAIL based on its rubric line (above). A scenario is PASS only
if its target criterion rubric line is satisfied. Criteria not targeted by a scenario are not
scored in that run.

| Criterion | Severity | Default failure mode |
|-----------|----------|---------------------|
| A | Critical | bar build skipped; prose substituted |
| B | Critical | token list mismatches step spec |
| C | Critical | --subject paraphrased |
| E | High | mode protocol forward-pass violation |
| G | Critical | fan_out collapsed to single Agent call |
| H | High | synthesis before join complete |

**Critical criteria**: A, B, C, G (4 total)
**High criteria**: E, H (2 total)

### Score thresholds

- **Green**: All 4 Critical PASS + both High PASS (6/6)
- **Yellow**: All 4 Critical PASS + at least 1 High PASS (4–5/6)
- **Red**: Any Critical FAIL

### Trigger for re-run

Re-run the battery when:
- A new sequence is added to `bar sequence show`
- The dispatch protocol block in any sequence changes
- The bar-workflow SKILL.md dispatch section is edited
- A user-reported compliance failure matches a criterion not currently in the battery

---

## Round Log

| Round | Date | Scores (A/B/C/E/G/H) | Overall | Notes |
|-------|------|----------------------|---------|-------|
| 1     | TBD  | —                    | —       | Baseline |
