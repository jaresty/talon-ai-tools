# ADR-0238: Dispatch Step Type for Bar Sequences

**Status**: Proposed
**Date**: 2026-05-29

---

## Context

Bar sequences support two step types implicitly: prompt steps (run a `bar build` command,
produce a response) and interactive steps (pause for user input via `requires_user_input:
true`). Both assume one agent produces one response per step.

The `parallel-eval` sequence requires a third behavior — autonomous fan-out to multiple
isolated subagents — but encodes it entirely in free-form `prompt_hint` prose:

> "spawn one isolated subagent per frame using the Agent tool, passing only the subject
> and that frame's description as the subagent's full context — no shared history,
> no cross-frame information"

This prose encoding has three failure modes:

1. **Non-machine-readable**: `bar sequence show` cannot render fan-out/join/isolation
   fields distinctly — the token column shows `method:prism`, not dispatch semantics.
2. **Non-validatable**: `validate_sequences` cannot enforce dispatch-specific invariants
   (no token field, required `fan_out`+`join`) because dispatch steps look like prompt steps.
3. **Non-reusable**: new sequences requiring fan-out must duplicate the same prose pattern
   with no consistency guarantee.

The `SequenceStep` struct in `internal/barcli/sequence.go` currently carries: `Token`,
`Role`, `PromptHint`, `RequiresUserInput`. The renderer (`sequence.go` line 156) always
renders `step.Token` in the token column — dispatch steps would show an empty or misleading
column.

`validate_sequences` in `lib/sequenceConfig.py` runs at test time (called from
`_tests/test_sequence_config.py`) and checks that every step token is a member of
`known_tokens`. Dispatch steps have no bar token and would fail this check.

---

## Decision

Add `type` as an optional field on sequence steps with two valid values:
- `"prompt"` — default; existing behavior; requires a `token` field
- `"dispatch"` — new; autonomous agent fan-out; no `token` field

Absence of `type` is equivalent to `type: "prompt"`. All existing sequences are
unaffected without modification.

### 1. Schema — `lib/sequenceConfig.py`

A `dispatch` step carries these fields in place of `token`:

```python
{
    "type": "dispatch",
    "role": "<role name>",
    "fan_out": "enumerate",   # replicate | enumerate  (partition deferred)
    "join": "all",             # all | first | merge
    "isolation": True,         # strip shared context from each agent
    "prompt_hint": "...",      # governs what the prior step must produce
}
```

`validate_sequences` is updated to:
- Skip the `known_tokens` membership check when `type == "dispatch"`
- Require `fan_out` and `join` when `type == "dispatch"`
- Reject a `token` field on dispatch steps (prevents conflation with prompt steps)

`fan_out: "enumerate"` carries a runtime contract: the preceding step's output must be
a list of named frames. This cannot be enforced statically — it is a sequence-authoring
precondition, not a schema constraint.

### 2. Export pipeline — `lib/promptGrammar.py` → `internal/barcli/sequence.go`

The `SequenceStep` struct gains four new optional fields:

```go
type SequenceStep struct {
    Token             string `json:"token"`
    Role              string `json:"role"`
    PromptHint        string `json:"prompt_hint,omitempty"`
    RequiresUserInput bool   `json:"requires_user_input,omitempty"`
    // new fields:
    Type      string `json:"type,omitempty"`       // "prompt" | "dispatch"
    FanOut    string `json:"fan_out,omitempty"`     // "replicate" | "enumerate"
    Join      string `json:"join,omitempty"`        // "all" | "first" | "merge"
    Isolation bool   `json:"isolation,omitempty"`
}
```

`lib/promptGrammar.py` already passes `SEQUENCES` through unchanged (lines 525–545).
The new fields are present in the Python dicts and will appear in `prompt-grammar.json`
automatically once the Go struct is updated to receive them.

### 3. Renderer — `internal/barcli/sequence.go`

`bar sequence show` renders dispatch steps distinctly in the token column (line 156):

```
  Step N  dispatch [enumerate→all, isolated]   <role>
          <prompt_hint>
```

The `jsonStep` struct used by `sequence show --json` (lines 116–133) also gains the four
new fields so machine consumers can read them.

No ⏸ marker is shown for dispatch steps — they are always autonomous.

### 4. SKILL.md — `internal/barcli/skills/bar-workflow/SKILL.md`

A new `§ Dispatch mode` section is added parallel to `§ Autonomous mode`,
`§ Interactive linear mode`, and `§ Interactive cycle mode`. It applies when `bar sequence
show` renders `dispatch` in a step's token column.

The protocol:
1. Do not run `bar build` for this step. The rule "run one `bar build` command" does not
   apply to dispatch steps.
2. Read `fan_out`: `replicate` sends the full prior output to each agent; `enumerate`
   treats the prior output as a list and sends one item per agent.
3. Read `isolation`: when `true`, each agent receives only the subject for its frame and
   the step's `prompt_hint` — no shared conversation history.
4. Spawn one agent per frame using the Agent tool.
5. Read `join`: `all` waits for all agents (fail if any fail); `first` takes the first
   successful result and emits a soft cancellation signal to others (the Agent tool has
   no hard cancel — agents may complete anyway); `merge` collects all results into an
   array for the next step's `--subject`.
6. Proceed to the next step using the collected results as subject.

### 5. `parallel-eval` migration — `lib/sequenceConfig.py`

The `prism` step is split into two: `prism` produces the frame list; a new `dispatch`
step executes the fan-out.

**Before:**
```python
{
    "token": "method:prism",
    "role": "frame enumeration",
    "prompt_hint": "Enumerate the named evaluation frames ... spawn one isolated subagent
        per frame using the Agent tool, passing only the subject and that frame's
        description as the subagent's full context — no shared history ...",
},
```

**After:**
```python
{
    "token": "method:prism",
    "role": "frame enumeration",
    "prompt_hint": "Enumerate the named evaluation frames as a governing artifact. Each
        frame must differ structurally. Do not apply any frame yet — enumeration is the
        only output of this step.",
},
{
    "type": "dispatch",
    "role": "parallel frame evaluation",
    "fan_out": "enumerate",
    "join": "all",
    "isolation": True,
    "prompt_hint": "Each agent receives only the subject and its assigned frame
        description. Return findings in a labeled block.",
},
```

The `show` (independent results collection) and `converge` steps that follow are
unchanged. `parallel-eval` step count increases from 3 to 4.

**Migration ordering constraint**: apply only after both the Go struct update and the
SKILL.md dispatch block are deployed. Structured `dispatch` fields without an execution
protocol are inert but misleading.

---

## Deferred Decisions

- **`fan_out: "partition"`**: splitting input by chunk or key requires a `partition_by`
  sub-field whose semantics are non-trivial. Deferred to a follow-on ADR.
- **Hard agent cancellation for `join: "first"`**: the Agent tool provides no hard cancel.
  Soft signaling is acknowledged but not specified here.
- **Dispatch steps as sequence entry points**: a sequence whose first step is `dispatch`
  is schema-valid under this ADR but untested. No structural barrier exists.

---

## Consequences

**Positive:**
- Dispatch semantics are machine-readable: `bar sequence show` renders fan-out/join/isolation;
  SKILL.md branches on them structurally rather than inferring from prose.
- `parallel-eval` becomes structurally consistent with other sequences.
- New sequences requiring fan-out reuse the `dispatch` step type without prose duplication.
- `validate_sequences` enforces dispatch-specific invariants at test time.

**Negative / risks:**
- The Go struct and Python schema must be updated together; a partial update leaves
  `bar sequence show` unable to render the new fields (they will be silently absent from
  the JSON).
- `enumerate` fan-out creates a runtime contract between adjacent steps that cannot be
  statically validated — a poorly-authored sequence can pass tests but fail at execution.
- `join: first` soft cancellation means agents may complete work that is discarded;
  no structural remedy until hard cancellation is available in the Agent tool.
- `parallel-eval` step count increases from 3 to 4; any test asserting step count will
  need updating.
