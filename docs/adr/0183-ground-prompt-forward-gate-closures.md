# ADR-0183: Ground Prompt Forward-Gate Closures

## Status

Accepted

## Context

A compliance audit of two independent ground protocol transcripts identified a shared structural failure mode: the protocol enforces what may not be *completed* without prior conditions, but does not enforce what the *only valid next token* is at critical sequencing points. This produces a stable attractor — "narrative compliance" — in which a model emits all sentinel text in grammatically valid order while the underlying tool-call chain is absent or structurally wrong.

The specific violations observed across both transcripts:

1. **Multi-criteria emission**: After ✅ Manifest declared, the model wrote criteria for all threads simultaneously. The prompt says "the first criteria rung after ✅ Manifest declared emits exactly one criterion for Thread 1 — emitting criteria for multiple threads is a protocol violation." This was removed in ADR-0182 as a P3 corollary. The removal is sound in principle, but P3's formulation ("one criterion per thread per cycle") is a counting constraint, not a sequencing constraint. A model can satisfy "one criterion per thread" by emitting them all at once in sequence and treating each as belonging to a distinct thread-cycle. The forward gate — "after Manifest declared, the only valid next token is the Thread 1 criteria rung label" — is absent.

2. **OBR dev-server-without-query**: The model started a dev server (valid tool call) then emitted planning narration ("Let me wait... Let me try a different approach...") without issuing a query tool call against the running process. The prompt names "start the dev server and emit the HTML response body (e.g., via curl or browser)" as the OBR pattern for web UIs, but does not state that after a process-start tool call, the only valid next action is a query tool call. The model treated process-start as sufficient.

3. **HARD STOP at harness error**: The prompt prohibits HARD STOP at the EV rung ("a harness error at EV requires fixing the harness, not an upward return") but frames this as a prohibition, not a sequencing constraint. A model that emits HARD STOP after a harness error has violated a prohibition it could ignore; a model that is told "the only valid next token after a harness-error exec_observed is a harness-repair tool call" has no gap to emit HARD STOP through.

4. **Formal notation copy-pasted across cycles**: When multi-criteria emission produces identical criteria across cycles, identical formal notation follows derivationally. This is a downstream consequence of violation 1. However, a secondary gap exists: A3 prohibits *reliance* on prior-cycle artifacts, not *identity* with them. A model can re-derive an identical artifact without relying on the prior cycle, satisfying A3 textually while violating its intent.

5. **impl_gate never emitted**: The prompt says "🟢 Implementation gate cleared licenses the first edit — the next required action after 🟢 is a tool call that creates or modifies an implementation file." This states what comes *after* impl_gate, not that impl_gate must come *first*. A model entering the EI rung can emit a file-write tool call before impl_gate and satisfy the rule ("impl_gate licenses the edit" — the edit follows impl_gate if impl_gate is emitted later in the same response).

6. **Final report emitted without Manifest exhausted**: The prompt says "After emitting ✅ Manifest exhausted, produce a final report." A model that labels its summary "Implementation Summary" rather than "final report" satisfies the heading check while bypassing the Manifest exhausted gate. The gate condition is currently defined by heading rather than content type.

### Relationship to ADR-0182

ADR-0182 removed several enforcement paragraphs as P3 corollaries, including "the first criteria rung after ✅ Manifest declared emits exactly one criterion for Thread 1." That removal was sound — the paragraph restated P3 — but it removed a sequencing constraint alongside the restatement. The multi-criteria violation (1) is a consequence of that removal not being compensated by a forward gate at the Manifest declared → criteria transition. ADR-0183 restores the sequencing constraint in forward-gate form, which is distinct from the P3 restatement that was removed.

## Decision

Add six forward-gate sentences to `GROUND_PARTS_MINIMAL["core"]` in `lib/groundPrompt.py`. Each sentence names the only valid next token (or token class) at a critical sequencing point. None of these sentences are corollaries of P1–P3; each closes a gap that the named principles do not cover.

### L7 — Forward gate at Manifest declared → criteria

**Insertion point:** criteria paragraph, after "one criterion per thread per cycle."

> After ✅ Manifest declared, the only valid next token is the criteria rung label for Thread 1 — no criteria for other threads, no planning narration, no other content. No criterion for Thread N+1 may appear until ✅ Thread N complete has been emitted for Thread N's current cycle.

**Closes:** violation 1 (multi-criteria emission) as root cause; violations 4, 5, 6 as downstream consequences of never entering a valid single-thread cycle.

### L8 — Forward gate at OBR process-start → query

**Insertion point:** OBR paragraph, after "for a web UI, start the dev server and emit the HTML response body."

> When the OBR artifact is a server process or web UI, two tool calls are required in sequence: (1) a process-start tool call, then (2) a query tool call (curl, HTTP request, or browser fetch) against the running process. The 🔴 Execution observed: sentinel may not be emitted until both tool calls have completed. Starting the process without querying it does not satisfy this gate.

**Closes:** violation 2 (OBR dev-server-without-query).

### L9 — Forward gate at EV harness error

**Insertion point:** VRO/HARD STOP paragraph, after "HARD STOP may not be emitted at the executable validation rung."

> When 🔴 Execution observed: at the executable validation rung shows a harness error (import failure, syntax error, missing file), the only valid next token is a tool call that repairs the harness — not a gap statement, not HARD STOP, not a rung label. HARD STOP may not appear in the same response as a harness-error exec_observed at the EV rung.

**Closes:** violation 3 (HARD STOP at harness error).

### L10 — Formal notation cycle-identity check

**Insertion point:** formal notation paragraph, after "before writing the test, re-read the formal notation."

> Before emitting the formal notation artifact, confirm via tool call that the criteria artifact for this cycle was produced in this cycle's transcript. If the criteria artifact is identical to a prior cycle's criteria artifact, the criterion has not changed — return to the prose rung and re-emit with an updated gap before descending again.

**Closes:** violation 4 (formal notation copy-paste) as secondary defense when criteria legitimately repeat across cycles.

### L11 — impl_gate as entry token of the EI rung

**Insertion point:** impl_gate paragraph, replacing the existing "licenses the first edit" formulation.

> 🟢 Implementation gate cleared is the first token of the executable implementation rung — no tool call, no prose, and no file modification may appear before it in the current response. Emitting a file-write tool call before 🟢 Implementation gate cleared is a protocol violation regardless of whether impl_gate is emitted later in the same response.

**Closes:** violation 5 (impl_gate never emitted) independently of L7.

### L12 — Final report gate by content type

**Insertion point:** final report paragraph, extending the "After emitting ✅ Manifest exhausted" sentence.

> Any prose that summarizes implemented behavior, lists acceptance criteria met, describes files created or modified, or names gaps as resolved is a final report regardless of its heading. Such prose may not appear until ✅ Manifest exhausted exists in the transcript for this invocation. If no ✅ Manifest exhausted exists, stop: emit ✅ Manifest exhausted if all threads are complete, or open the next gap cycle if they are not.

**Closes:** violation 6 (final report without Manifest exhausted) independently of L7.

### Propagation structure

L7 is the highest-leverage intervention: it closes violation 1 at root and collapses violations 4, 5, 6 as downstream consequences. L8 and L9 are independent root-cause closures for violations 2 and 3. L10, L11, and L12 provide defense-in-depth for violations 4, 5, and 6 when L7's root closure is bypassed (e.g., after an upward return that correctly resets to a single criterion).

## Consequences

**Positive:**
- Multi-criteria emission is closed at the Manifest declared → criteria transition, the earliest point where a forward gate can fire
- OBR process-start is no longer sufficient; a query tool call is required before exec_observed
- HARD STOP at harness error is prevented by sequencing constraint, not prohibition
- Final report gate is content-type-based, closing the heading-substitution escape route
- All six interventions are minimal additions to existing paragraphs; no existing rule is removed

**Negative:**
- L7 adds a sequencing constraint that was previously expressed as a prohibition and then removed in ADR-0182 as a P3 corollary; this reintroduces a sentence adjacent to P3 that is not redundant with it (forward gate vs. counting constraint) but may appear redundant on casual reading — the work log must document the distinction
- L8's two-step sequence requirement assumes process-start and query are distinct tool calls; for CLIs where the artifact is directly invocable, step 1 and step 2 collapse into one tool call — this is not a violation but the rule should be read as "query the process; if process-start and query are one operation, one tool call satisfies both steps"
- Baseline character count increases by approximately 500–600 characters; test baselines must be updated

## Implementation Notes

- Edit `GROUND_PARTS_MINIMAL["core"]` in `lib/groundPrompt.py` (SSOT)
- Write tests for each of L7–L12 before editing the prompt (red-first)
- Run `make axis-regenerate-apply` and `cp build/prompt-grammar.json web/static/prompt-grammar.json` after editing
- Update char-count baselines in `test_ground_prompt_minimal.py`, `test_ground_prompt_redundancy_audit.py`, `test_ground_prompt_rung_table.py`, and `test_ground_rewrite_thread1.py`
- Run ADR-0113 loop (minimum 5 tasks) to validate compliance after implementation

## Work Log

*(to be populated during implementation)*
