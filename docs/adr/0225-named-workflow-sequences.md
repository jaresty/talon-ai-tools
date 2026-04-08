# ADR-0225: Named Workflow Sequences — Discoverable Token Cycles

**Status**: Proposed
**Date**: 2026-04-08

---

## Context

The bar grammar encodes pairwise contrast between tokens via `distinctions[]`:
"these two tokens differ in this way." This is useful for choosing between alternatives,
but it does not encode *direction* or *iteration* semantics.

Several natural multi-step patterns emerge repeatedly in practice:

- **experiment-cycle**: `form:prep` → run experiment → `form:vet` — frame hypothesis
  before running, review evidence after
- **debug-cycle**: `task:probe` → `task:fix` → `task:check` — surface assumptions,
  repair root cause, verify the fix
- **scenario-to-plan**: `method:sim` → `method:plan` — simulate a scenario, then derive
  the action plan it implies
- **extract-and-package**: `method:pull` → `method:contextualise` — extract a relevant
  subset, package it for a downstream LLM or reader

In each case, the individual tokens already carry their own prompt instructions correctly.
What is missing is the *sequence relationship*: token B is the natural next step after
token A, and the two together form a named, repeatable workflow.

Without sequence encoding:
- Users must rediscover `prep → vet` from prose each session
- `bar-autopilot` cannot detect mid-sequence position and suggest the next step
- `bar lookup` results do not reveal sequence membership, missing a discoverability path
- TUI2 has no affordance to hint "you just selected prep — vet is the follow-up step"

The gap is not about token semantics (the definitions are correct) but about workflow
topology — the directed graph of how tokens relate across time.

---

## Decision

### Grammar: top-level `sequences` block

Add a top-level `sequences` key to `prompt-grammar.json`. The value is an object whose
keys are sequence identifiers (slug strings) and whose values are sequence descriptors.

```json
"sequences": {
  "experiment-cycle": {
    "description": "Frame a hypothesis before running an experiment, then review evidence afterward.",
    "steps": [
      {
        "token": "form:prep",
        "role": "pre-experiment framing",
        "prompt_hint": "Use this step to state the hypothesis and success criteria before running the experiment."
      },
      {
        "token": "form:vet",
        "role": "post-experiment review",
        "prompt_hint": "Use this step to evaluate the evidence against the original hypothesis."
      }
    ]
  },
  "debug-cycle": {
    "description": "Surface root causes, fix them, then verify the fix holds.",
    "steps": [
      {
        "token": "task:probe",
        "role": "root cause investigation",
        "prompt_hint": "Use this step to surface hidden assumptions and possible causes before writing any fix."
      },
      {
        "token": "task:fix",
        "role": "repair",
        "prompt_hint": "Use this step to implement the targeted fix once the root cause is confirmed."
      },
      {
        "token": "task:check",
        "role": "verification",
        "prompt_hint": "Use this step to verify the fix holds and no regressions were introduced."
      }
    ]
  },
  "scenario-to-plan": {
    "description": "Simulate a scenario, then derive the action plan it implies.",
    "steps": [
      {
        "token": "method:sim",
        "role": "scenario simulation",
        "prompt_hint": "Use this step to simulate the scenario and observe what it implies."
      },
      {
        "token": "method:plan",
        "role": "action planning",
        "prompt_hint": "Use this step to convert the simulation's implications into a concrete action plan."
      }
    ]
  },
  "extract-and-package": {
    "description": "Extract a relevant subset, then package it for downstream use.",
    "steps": [
      {
        "token": "method:pull",
        "role": "extraction",
        "prompt_hint": "Use this step to identify and extract only the relevant material from the subject."
      },
      {
        "token": "method:contextualise",
        "role": "packaging",
        "prompt_hint": "Use this step to wrap the extracted material with enough context for a downstream reader or LLM."
      }
    ]
  }
}
```

**Schema per sequence:**
- `description` (string, required) — one sentence naming the workflow and its purpose
- `steps` (array, required, length ≥ 2) — ordered list of steps

**Schema per step:**
- `token` (string, required) — `axis:slug` reference to an existing grammar token
- `role` (string, required) — short label for this step's function in the sequence
- `prompt_hint` (string, optional) — one sentence of usage guidance for this step
  specifically in this sequence context (distinct from the token's own definition)

**Why top-level, not alongside tokens**: Sequences are multi-token and potentially
multi-axis. Embedding them at the token level would require duplication (which token
owns the sequence?) or a single-owner convention that is arbitrary. A top-level
`sequences` block is unambiguous and composable — a token can belong to multiple
sequences without any structural conflict.

**Why `axis:slug` references rather than inline token data**: Sequences are a
topology layer on top of existing token semantics. The token's definition, heuristics,
and distinctions remain the authoritative source; the sequence only adds role and
prompt_hint within the sequence context. Duplicating token data would create a drift
risk.

---

### Python SSOT: `lib/sequenceConfig.py`

Define sequences in a new Python file `lib/sequenceConfig.py`. The grammar export
pipeline (`lib/promptGrammar.py`) reads this file and serializes the `sequences` block
into `prompt-grammar.json` alongside the existing axes, tasks, and persona sections.

```python
# lib/sequenceConfig.py

SEQUENCES = {
    "experiment-cycle": {
        "description": "Frame a hypothesis before running an experiment, then review evidence afterward.",
        "steps": [
            {
                "token": "form:prep",
                "role": "pre-experiment framing",
                "prompt_hint": "Use this step to state the hypothesis and success criteria before running the experiment.",
            },
            {
                "token": "form:vet",
                "role": "post-experiment review",
                "prompt_hint": "Use this step to evaluate the evidence against the original hypothesis.",
            },
        ],
    },
    # ... (debug-cycle, scenario-to-plan, extract-and-package)
}
```

Validation at export time: each `token` reference is resolved against the grammar;
export fails with a named error if any `axis:slug` is not found. This prevents
sequences from silently referencing stale or misspelled token keys.

---

### Go grammar layer: `Grammar.Sequences`

Extend `grammar.go`:

```go
type SequenceStep struct {
    Token      string `json:"token"`
    Role       string `json:"role"`
    PromptHint string `json:"prompt_hint,omitempty"`
}

type Sequence struct {
    Description string         `json:"description"`
    Steps       []SequenceStep `json:"steps"`
}

// In Grammar struct:
Sequences map[string]Sequence `json:"sequences"`
```

Add accessors:

```go
// SequencesForToken returns the name and step index for every sequence
// that contains the given "axis:slug" token reference.
func (g *Grammar) SequencesForToken(axisSlug string) []SequenceMembership

type SequenceMembership struct {
    Name      string   // sequence key
    StepIndex int      // 0-based position in Steps
    NextStep  *SequenceStep // nil if last step
}
```

`SequencesForToken` is the shared lookup used by both the CLI and TUI2.

---

### CLI: `bar sequence` subcommand

```
bar sequence list
bar sequence show <name>
```

**`bar sequence list`** — one sequence per line:

```
experiment-cycle    Frame a hypothesis before running an experiment, then review evidence afterward.
debug-cycle         Surface root causes, fix them, then verify the fix holds.
scenario-to-plan    Simulate a scenario, then derive the action plan it implies.
extract-and-package Extract a relevant subset, then package it for downstream use.
```

**`bar sequence show experiment-cycle`**:

```
experiment-cycle — Frame a hypothesis before running an experiment, then review evidence afterward.

  Step 1  form:prep   pre-experiment framing
          Use this step to state the hypothesis and success criteria before running the experiment.

  Step 2  form:vet    post-experiment review
          Use this step to evaluate the evidence against the original hypothesis.
```

Both commands support `--json` for machine-readable output.

**`bar lookup` integration**: Results that are sequence members include a `sequences`
field in `--json` output listing sequence names and step indices. Human-readable output
adds a dim suffix:

```
form:prep — Frame response as pre-experiment setup    [part of: experiment-cycle step 1/2]
```

---

### TUI2: sequence hint in token detail panel

When a user selects a token that belongs to one or more sequences, the token detail
panel shows a dim hint line below the token definition:

```
part of experiment-cycle (step 1/2) — next: form:vet (post-experiment review)
```

This hint is:
- Only shown on *selected* tokens (not on hover / cursor focus) — same pattern as
  `routing_concept` subtitle
- Suppressed if the token is the last step in all its sequences (nothing to suggest)
- If the token belongs to multiple sequences, show one hint per sequence

Implementation: populate a `Sequences []SequenceMembership` field on `TokenOption`
in `tui_tokens.go`, sourced from `Grammar.SequencesForToken`. Render in the detail
panel in `program.go`.

---

### Harness: sequence membership in HarnessToken

Add `sequences []SequenceMembership` to `HarnessToken` in `harness.go`, populated
from `Grammar.SequencesForToken`. This lets LLM-driven harness sessions detect
mid-sequence position and reason about the natural next step.

---

### Sequence discovery via shuffle (extending ADR-0085)

The initial sequence set is seeded from known usage patterns. The ongoing discovery
process runs as an extension of the ADR-0085 shuffle-driven refinement loop.

**The signal is directed quality uplift, not co-occurrence.**

Co-occurrence (tokens appearing together in the same shuffle) indicates *compatibility*
— that is already captured by `cross_axis_composition` natural pairings. A sequence
candidate requires a stronger and directional claim: step A's *output* makes step B
*more effective* than running B cold. The order encodes a dependency, not just
affinity. `probe → fix` is a sequence because probe's output (identified root cause,
surfaced assumptions) is the right input for fix. `fix → probe` is not a sequence
even though both tokens are fully compatible.

**Discovery protocol:**

1. **Nominate candidates** — During any shuffle evaluation cycle (ADR-0085 Phase 2),
   flag token pairs where a natural "what next?" question arises after reading the
   output. The nomination criterion is intuitive: does this output feel like setup for
   a follow-up step?

2. **Chain test** — For each candidate pair (A → B):
   - Run token A against a subject; record the output.
   - Run token B twice: once cold (original subject only), once chained (A's output
     as subject, or appended as addendum).
   - Score both B runs on the ADR-0085 rubric (1–5).
   - A candidate is confirmed if the chained run scores ≥ 1 point higher than the
     cold run, across at least 2 independent subjects.

3. **Document ordering rationale** — Before promoting, write one sentence explaining
   why A must precede B (not just that they are compatible). If the ordering rationale
   cannot be stated clearly, the pair is not a sequence — it is a natural pairing and
   belongs in `cross_axis_composition` instead.

4. **Promote** — Add the confirmed sequence to `lib/sequenceConfig.py` with role and
   prompt_hint for each step. Re-export grammar.

**Retrospective seed review:**

Existing shuffle seeds in `docs/adr/evidence/0085/` are a candidate pool that has
never been evaluated for sequence signals. Before generating new seeds for discovery,
run the nomination pass (step 1) against high-scoring historical seeds. Sequences that
were already being used implicitly may surface without any new generation.

---

### bar-autopilot integration

When `bar-autopilot` detects that the user has just run a bar command containing a
sequence-member token, it may suggest the next step in the sequence as the natural
continuation. This requires `bar-autopilot` to call `bar sequence show <name>` (or
`bar lookup --json`) to retrieve the sequence definition and identify the next step.

Implementation of the autopilot integration is deferred — the CLI and grammar layer
are the precondition. The integration is a skill-level change, not a grammar change.

---

## Consequences

**Changes:**
- New `lib/sequenceConfig.py` (Python SSOT for sequence data)
- Grammar export extended: `sequences` block in `prompt-grammar.json`
- `grammar.go`: `Sequence`, `SequenceStep`, `SequenceMembership` types; `Sequences`
  field; `SequencesForToken` accessor
- `tui_tokens.go`: populate `Sequences` on `TokenOption` via `SequencesForToken`
- `program.go`: render sequence hint in token detail panel for selected tokens
- `harness.go`: populate `sequences` on `HarnessToken`
- `app.go`: `bar sequence list` and `bar sequence show` subcommands
- `lookup.go`: extend `LookupResult` with `Sequences []SequenceMembership`; extend
  human-readable and JSON output
- `bar help llm` or `generalHelpText`: document `bar sequence` subcommand

**Unchanged:**
- Token definitions, heuristics, distinctions — sequences are additive metadata
- `bar build`, `bar shuffle`, all existing subcommands
- Grammar schema version (minor addition; backwards-compatible)

**Enables:**
- `bar-autopilot` sequence detection (deferred; no code change required here)
- `bar-dictionary` skill: can include sequence membership in token lookup responses
- User-defined sequences in a future extension of ADR-0169 user-defined token sets

## What is not decided here

- Whether users can define their own sequences (deferred to ADR-0169 extension)
- Whether sequences can be cross-axis (current examples include cross-axis steps; the
  schema allows it, but no validation enforces axis diversity)
- Whether `bar sequence show` should render the full token definition for each step or
  only role + prompt_hint (current decision: role + prompt_hint only, with a pointer
  to `bar lookup <token>` for full detail)
- The exact set of initial sequences beyond the four listed above
- Whether TUI2 should show a sequence hint on *hover* rather than only on selection
