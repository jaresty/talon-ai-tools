# ADR-0226: bar-sequence Skill for LLM-Driven Sequence Execution

**Status:** Proposed
**Date:** 2026-04-08
**Supersedes:** —
**Related:** ADR-0225 (Named Workflow Sequences), ADR-0085 (Shuffle-Driven Refinement)

---

## Context

ADR-0225 introduced named workflow sequences — directed multi-step token patterns where step
N's output makes step N+1 more effective than running cold. The grammar encodes four initial
sequences (`experiment-cycle`, `debug-cycle`, `scenario-to-plan`, `extract-and-package`), each
with ordered steps, roles, and prompt hints.

The existing `bar-workflow` skill covers a related but distinct need: the LLM composes an ad
hoc sequence of `bar build` commands for progressive refinement of a single complex task. The
LLM chooses the steps; the sequence is ephemeral and task-specific.

Named sequences are structurally different:

| Dimension | bar-workflow | Named sequences (ADR-0225) |
|---|---|---|
| Sequence origin | LLM constructs per-task | Grammar encodes, grammar owns |
| Step count | Variable, chosen per task | Fixed by sequence definition |
| Handoff | Same subject, different angle | Output of step N is input to step N+1 |
| Recurrence | One-off | Reusable workflow pattern |
| Discovery | LLM decides to chain | User or LLM recognizes pattern applies |

No skill currently teaches an LLM to: recognize when a named sequence applies, execute its
steps in order, treat each step's output as the subject for the next, or handle weak output
mid-sequence. This is the gap ADR-0226 closes.

---

## Decision

### 1. Scope boundary with bar-workflow

`bar-sequence` executes **grammar-defined named sequences** from `bar sequence list`. It does
not compose ad hoc chains — that is `bar-workflow`'s domain.

The trigger condition for `bar-sequence`: the user's request matches a named sequence's
description or the LLM identifies that the task structure maps to a known sequence pattern
(e.g., "I want to frame a hypothesis, run an experiment, then review the results" → maps to
`experiment-cycle`).

`bar-workflow` remains the right skill when no named sequence fits and the LLM needs to
compose a custom multi-step prompt chain.

### 2. Sequence recognition

The skill must run `bar sequence list` at the start of each session to discover available
sequences. Recognition is a two-step check:

1. **Explicit**: the user names a sequence (`"run the experiment-cycle sequence"`)
2. **Implicit**: the LLM matches the user's described workflow against sequence descriptions.
   The skill provides a recognition heuristic: does the task involve a before/after structure,
   a hypothesis/validation loop, or a transform/package pattern? If yes, check `bar sequence
   show <name>` for fit before committing.

When in doubt, surface the candidate sequence to the user for confirmation before executing.
Do not silently apply a sequence the user did not request.

### 3. Step chaining and valid handoff

Each step in a sequence produces output that becomes the **subject** of the next step's `bar
build` command. The handoff protocol:

1. Run `bar build <step-tokens> --subject "<previous output>"` for step N+1
2. The previous step's full output (not a summary) is the subject
3. The `prompt_hint` from the sequence step definition (available via `bar sequence show`)
   is passed as `--addendum` to give the step its role context
4. The LLM writes a **complete response** to each step's bar output before advancing

The `NextToken` and `NextRole` fields in `HarnessToken.Sequences` (ADR-0225) are informational
— the skill reads them from `bar sequence show`, not from the harness.

### 4. Recovery from weak output

If a step's output is assessed as weak (the LLM judges it fails to satisfy the step's stated
role), the skill has two permitted responses:

1. **Retry**: re-run the same step with an adjusted `--addendum` that corrects the gap. At
   most one retry per step.
2. **Surface and halt**: inform the user that step N produced weak output, show what was
   produced, and ask whether to continue, retry with guidance, or abort. Do not silently
   advance to the next step with weak input.

Silent advancement with weak output is prohibited — the sequence's quality guarantee depends
on each step producing usable handoff material.

### 5. Drive bar commands directly; surface the sequence plan first

The skill drives `bar build` commands directly — it does not ask the user to run them. This
matches `bar-workflow` and `bar-autopilot` behavior.

However, before executing, the skill must surface the execution plan:

```
Sequence: experiment-cycle (2 steps)
  Step 1: form:prep — pre-experiment framing
  Step 2: form:vet — post-experiment review

Proceeding with step 1...
```

This makes the sequence structure visible and gives the user a natural point to redirect
before any bar commands run.

---

## Skill Structure

```
.claude/skills/bar-sequence/
  skill.md          # skill definition loaded by Claude Code
```

The skill definition covers:

- **Trigger**: when to invoke (recognition heuristics, explicit user request)
- **Discovery**: `bar sequence list` → `bar sequence show <name>` workflow
- **Execution loop**: plan display → step 1 (bar build + full response) → handoff → step N
- **Handoff protocol**: previous output as `--subject`, `prompt_hint` as `--addendum`
- **Recovery rules**: retry-once or surface-and-halt; no silent advancement
- **Boundary**: explicit exclusion of ad hoc chaining (→ bar-workflow)

---

## Consequences

**Positive:**
- Named sequences become exercisable without requiring the user to manually compose chained
  `bar build` commands
- The quality uplift premise of ADR-0225 (A's output makes B more effective) becomes
  testable in real sessions
- Clear boundary with `bar-workflow` prevents overlap confusion

**Negative / risks:**
- Recognition heuristic may misfire — LLM applies a sequence the user didn't intend. Mitigated
  by the surface-and-confirm requirement for implicit matches.
- Sequence library is small (4 sequences at launch). The skill is most useful as the library
  grows via ADR-0085 Phase 2f discovery.
- Handoff fidelity depends on step output quality. If step 1 is weak and the LLM retries
  rather than halting, step 2's subject is still degraded input. The retry-once cap limits
  compounding degradation.

**Out of scope for this ADR:**
- Harness integration (the harness surfaces sequence hints but the skill does not use the
  harness for execution)
- Partial sequence resumption (no state persistence between conversations)
- User-defined sequences (covered by ADR-0169 if implemented)
