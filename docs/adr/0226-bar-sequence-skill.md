# ADR-0226: Sequence-Aware bar-workflow and Interactive Sequence Modes

**Status:** Proposed
**Date:** 2026-04-08
**Supersedes:** ADR-0226 (initial draft — withdrawn, single-skill approach)
**Related:** ADR-0225 (Named Workflow Sequences), ADR-0085 (Shuffle-Driven Refinement)

---

## Context

ADR-0225 introduced named workflow sequences — directed multi-step token patterns where step
N's output makes step N+1 more effective than running cold. The grammar encodes four initial
sequences (`experiment-cycle`, `debug-cycle`, `scenario-to-plan`, `extract-and-package`).

The existing `bar-workflow` skill chains `bar build` commands sequentially but has two
structural constraints that make it insufficient for named sequences:

1. **No sequence awareness**: it doesn't know `bar sequence list` exists and composes all
   chains ad hoc
2. **No pause protocol**: it plans the full chain upfront and runs all steps autonomously
   without user input — unsuitable when steps depend on real-world results (experiment
   outcomes, test results, gathered feedback) that the LLM cannot synthesize

Three distinct execution modes emerge from named sequences:

| Mode | Steps | User input between steps | Repetition |
|---|---|---|---|
| Autonomous chain | All run without pause | None | No |
| Interactive linear | Pause after each step | User provides real-world results | No |
| Interactive cycle | Pause after each pass | User provides results + decides whether to repeat | Yes (N times) |

`experiment-cycle` (`prep→vet`) illustrates the cycle mode: the user frames a hypothesis
(`prep`), runs an experiment (outside the LLM), provides results, reviews them (`vet`), then
may run another experiment — repeating `prep→vet` until the question is resolved.

No current skill handles interactive or cyclic modes. This ADR decides how to extend the
system to support all three.

---

## Decision

### 1. Skill boundary: extend bar-workflow, not a new skill

A dedicated `bar-sequence` skill is not introduced. Instead, `bar-workflow` is extended to
be sequence-aware and to support all three execution modes.

**Rationale:** bar-workflow already owns the concept of "run bar commands in a deliberate
sequence." Adding sequence discovery and pause/resume to it keeps the skill surface minimal.
Users already know when to invoke bar-workflow; they don't need to choose between two
overlapping skills.

The extension adds to bar-workflow:
- A discovery step: check `bar sequence list` before composing an ad hoc chain
- A mode declaration: after selecting a sequence (or deciding to compose ad hoc), declare
  the execution mode explicitly before running any commands
- A pause/resume protocol for interactive and cyclic modes

### 2. Grammar schema evolution

The sequence schema in `lib/sequenceConfig.py` must encode execution mode per sequence.
Each sequence gets a top-level `mode` field:

```python
SEQUENCES = {
    "experiment-cycle": {
        "description": "...",
        "mode": "cycle",          # NEW: "autonomous" | "linear" | "cycle"
        "steps": [...],
    },
    "debug-cycle": {
        "mode": "linear",
        ...
    },
    "scenario-to-plan": {
        "mode": "autonomous",
        ...
    },
    "extract-and-package": {
        "mode": "autonomous",
        ...
    },
}
```

Each step may also declare `requires_user_input: true` to signal that the LLM must pause
and collect real-world results before the next step. This is implicit in `linear` and `cycle`
modes but explicit encoding prevents ambiguity as sequences grow.

`bar sequence show <name>` output must include the mode field so bar-workflow can read it
without parsing Python.

### 3. Autonomous mode (bar-workflow extension)

Bar-workflow's existing protocol applies unchanged, with one addition at the start:

1. Run `bar sequence list` to discover named sequences
2. If request matches a named sequence, run `bar sequence show <name>` to get steps and mode
3. Confirm the sequence with the user if the match was implicit (not explicitly requested)
4. Run all steps autonomously, using previous step's output as `--subject` for the next,
   and the step's `prompt_hint` as `--addendum`
5. Synthesize as bar-workflow does today

If no named sequence fits, bar-workflow enters ad hoc mode — but before composing the chain,
it applies a mode inference check (see §7).

### 4. Interactive linear mode

After each step, bar-workflow pauses and emits a handoff prompt:

```
✅ Step 1 complete (pre-experiment framing).

Now perform the experiment or action this framing was designed to support.
When you have results to review, paste them here and I will run step 2 (post-experiment review).
```

The LLM then waits. When the user provides results, those results become the `--subject` for
the next step. The LLM does not advance until user input arrives.

Key constraint: the LLM must not synthesize or predict the user's results. The handoff
prompt must be explicit that it is waiting for real-world input, not continuing autonomously.

### 5. Interactive cycle mode

Cycle mode extends linear mode with an iteration decision after each full pass:

```
✅ Cycle 1 complete (prep → vet).

To run another experiment cycle:
  - Provide your next experiment's setup and I will run prep again
  - Or say "done" to close the cycle and I will summarize all iterations

What would you like to do?
```

The LLM accumulates cycle summaries across passes. When the user ends the cycle ("done" or
equivalent), the LLM synthesizes across all iterations — what changed, what converged, what
remains unresolved.

Cycle termination is always user-driven. The LLM must not decide the cycle is complete.

**Iteration tracking:** bar-workflow maintains a visible cycle count in each handoff prompt
(`Cycle 1`, `Cycle 2`, etc.) so the user can see how many passes have run.

### 6. Scope boundary: ad hoc chains remain bar-workflow's domain

When no named sequence fits, bar-workflow composes an ad hoc chain as it does today. The
sequence discovery step is additive — it does not prevent ad hoc composition.

The check is: does a named sequence describe the user's workflow? If yes, use it and declare
the mode. If no, enter ad hoc mode and apply §7.

### 7. Mode inference for ad hoc chains

When composing an ad hoc chain (no named sequence matched), bar-workflow infers whether the
chain is autonomous, interactive, or cyclic before executing any steps. Two signals:

**From the request:** if the user's description implies real-world action between steps
("I'm going to run experiments and review each one", "after each test I want to…"), the
chain is interactive. If it implies repetition until a goal is met, it is cyclic.

**From the planned steps:** if any step's intended input cannot exist until the user takes an
action outside the conversation (runs code, conducts an interview, collects data, deploys
something), that step boundary is interactive. The LLM should recognize this when planning
the chain and declare the mode before executing.

When the mode is ambiguous, bar-workflow prompts the user:

```
I've planned a 2-step chain: [step 1 purpose] → [step 2 purpose].

Step 2 will need [description of what's needed]. Will you be providing that between steps,
or should I proceed autonomously using what I have?
```

This keeps mode selection transparent and user-confirmed rather than silently assumed.
Ad hoc interactive and cyclic chains follow the same pause/resume and iteration protocols
as their named-sequence equivalents (§4 and §5).

---

## Consequences

**Positive:**
- Named sequences become exercisable without a new skill surface
- Interactive and cyclic sequences have an explicit, documented protocol — no ambiguity about
  when the LLM pauses vs. continues
- Cycle mode formalizes the prep→vet→prep→vet pattern, making iterative experiments a
  first-class workflow
- The grammar schema gains `mode` — a durable field that constrains skill behavior across
  bar-workflow versions
- Mode inference (§7) extends interactive and cyclic support to ad hoc chains, not just
  named sequences — the capability is general, not gated on the sequence library

**Negative / risks:**
- Bar-workflow becomes more complex: it must handle three modes, sequence discovery, and
  cycle state tracking. The skill definition will grow substantially.
- Pause protocol depends on the user providing well-formed results. If the user provides
  thin input between steps, the next step's quality degrades. No automatic recovery — the
  LLM can note the gap but must proceed.
- Cycle termination is user-driven, which means the LLM cannot end a cycle that has clearly
  converged. A future extension could add a convergence signal, but this ADR does not
  address it.
- Implicit sequence matching (LLM infers the sequence from the user's description) requires
  user confirmation to prevent misapplication. This adds a turn before any work begins.

**Grammar changes required (before implementation):**
- Add `mode` field to each sequence in `lib/sequenceConfig.py`
- Add `requires_user_input` per-step flag (optional, defaults false)
- Expose `mode` in `bar sequence show` output (Go: `runSequenceShow` in `sequence.go`)

**Skill changes required:**
- Update `bar-workflow` skill definition to add discovery step, mode declaration, and
  pause/resume protocol for interactive and cyclic modes
- No new skill file

**Out of scope:**
- Cross-conversation state persistence (cycle state is lost if the conversation ends)
- User-defined sequences (ADR-0169)
- Convergence detection for cycle termination
