# ADR-0217: Ground Prompt — Generative Ladder (Derive Rungs from Principles)

**Status**: Proposed
**Date**: 2026-03-29

---

## Context

The current ground protocol specifies a fixed 7-rung ladder (prose → criteria → formal notation → EV → VRO → EI → OBR) with named sentinels, closed action sets, and explicit gate conditions. This structure is the compiled output of ~216 ADRs closing escape routes discovered in transcripts.

Two observations motivate this ADR:

**1. A model that derives its own ladder may be more faithful to it.**
When a model follows pre-enumerated rules, it can treat gate violations as edge cases or exceptions. When a model derived the ladder from principles it applied, violating a gate is inconsistent with the derivation it already committed to — the same principles that produced the gate are present in working memory. Ownership of the derivation creates a different compliance dynamic than rule-following.

**2. The fixed ladder is domain-specific.**
The current rungs assume software: test runners, implementation files, dev servers. The underlying principles apply to any domain where behavior change needs to be grounded in evidence. A generative approach could derive context-appropriate rungs for documentation, configuration, infrastructure, data pipelines, or non-software behavioral change.

**Design constraints from discussion:**
- The 19 principles become the axiom block replacing the current rung enumeration
- Ladder derivation is the **first rung**, not a pre-protocol step — it is subject to the same evidential requirements as any other rung
- The derived ladder artifact is produced and visible but execution **does not pause** for human review — descent begins immediately after derivation
- Each principle must be formulated to be **externally verifiable** rather than self-certifiable
- Principle 8 is reformulated to close the self-certification escape

---

## The 19 Principles

These replace the current fixed rung definitions as the axiom block. They are ordered from most fundamental to most operational.

**P1 — Intent primacy.**
Intent exists. Everything produced in a session is derivative of that intent. Whenever new information changes the understanding of intent, every rung whose definition has changed must be refined, starting with the highest affected rung and propagating downward. Completed rungs may not be re-opened except by this mechanism.

**P2 — Behavioral change isolation.**
Any change to behavior may only be made at a dedicated rung. No rung may produce a behavioral change as a side effect of another rung's artifact. A rung that changes behavior and also changes another artifact type (e.g., a test) is a protocol violation — split into separate rungs.

**P3 — Observable evidence required.**
Any change to behavior must be observed in both its pre-change (absent/failing) state and its post-change (present/passing) state, and the change must be visible through actual traces — raw output from tool execution, not descriptions of what the output means.

**P4 — Enforced and persistent.**
Any change to behavior must be enforced through a dedicated rung, and there must be a mechanism that continuously verifies the behavior remains (e.g., CI). A behavioral change without an enforcement rung is not complete.

**P5 — Automation quality verified.**
Any automation that enforces behavior must itself be verified by observing it in a failing state before a passing state. Automation that has never been observed to fail provides no evidential guarantee.

**P6 — Artifact type discipline.**
Executable artifacts may only be changed at a dedicated rung for that artifact type. A rung that produces both a test change and a formal specification change violates type discipline — each artifact type has exactly one rung.

**P7 — Upward faithfulness.**
Any change to any rung must be faithful to the rung above it. The space of valid implementations permitted by a lower rung may only be equal to or smaller than the space permitted by the rung above it. Expanding the permitted space is a faithfulness violation. Tool execution at any rung is permitted.

**P8 — Rung validity test.**
A rung is valid if and only if a human reviewer, given only that rung's artifact and no other context, can determine whether the next rung's artifact is faithful to the intent without consulting any prior rung. A rung that fails this test is narration, not a rung. The ladder must be minimal: removing any rung must leave some faithfulness evaluation impossible without consulting prior rungs.

**P9 — Information density preservation.**
Each rung must encode the same or higher quality of information as the rung above it — it must be sufficient to represent the intent as fully as possible in its artifact type. A rung whose artifact loses information present in the rung above it is a protocol violation.

**P10 — Three-part completeness.**
A session is complete only when it has produced: (a) a manual observation confirming the behavior is present, (b) automation that verifies the behavior is consistently maintained, and (c) for behavior-change sessions, an artifact that directly implements the change. All three must be present; any absent component is an incomplete session.

**P11 — Immediate lowest-rung observation.**
Whenever a behavioral change is made that would be visible at a higher rung, it must be observed immediately at the lowest rung that allows observation of that change. The purpose is to surface course-correction information as early as possible. Deferring observation to a higher rung when a lower rung could have surfaced it first is a protocol violation.

**P12 — Completeness slice.**
After declaring intent, a slice of behavior is chosen to carry to the next rung in accordance with the completeness scope in play. The slice must be declared explicitly before descent begins. Descending without a declared slice is a protocol violation.

**P13 — Observation-first, observation-last.**
A session begins by observing current behavior manually and declaring what the intent is believed to be. A session ends by repeating that observation to confirm intent has been met. Declaring completion without a closing observation is a protocol violation.

**P14 — Evidential authority.**
Only tool-executed events have evidential standing. Inference, prediction, prior-cycle output, and model-generated descriptions of tool output have none, regardless of accuracy. A rung gate is satisfied if and only if a tool-executed event appears in the current-cycle transcript whose output is of that rung's artifact type.

**P15 — Cycle identity.**
Evidence is valid only within the cycle in which it was produced. A cycle opens at the prose rung emission for a given thread and closes at Thread N complete or an upward return. Evidence from a prior cycle, a different thread, or a different gap does not satisfy any gate in the current cycle regardless of type match. Prose re-emission for one thread does not affect the cycle identity of any other thread.

**P16 — Provenance.**
A gate is satisfied only by a tool call made in direct response to the gap declared at the immediately prior rung in the current cycle. A tool call made for a different purpose, targeting a different gap, or produced in a prior cycle does not satisfy any gate regardless of type match. The connection between the declared gap and the tool call must be traceable in the transcript.

**P17 — Derivation chain.**
Each artifact must be derived from the prior rung's actual content — not from the original intent reconstructed from memory. A skipped rung voids all artifacts below it. Divergence from intent is only detectable at the rung where the prior artifact's specificity was insufficient; breaking the derivation chain makes that detection impossible. Form changes between rungs; intent does not.

**P18 — Continuous descent.**
Once descent begins, all rung transitions are continuous within the same response unless the derived ladder specifies a protocol-defined stop at that rung. Pausing between rungs for user confirmation is a protocol violation. Response length is never a valid reason to stop between rungs — if the full descent cannot fit in one response, continue from the current rung in the next response without re-emitting completed rungs.

**P19 — Thread sequencing.**
When multiple behavioral gaps are declared, they form a manifest. Each gap is a thread. All rungs for Thread N must complete before any content for Thread N+1 may appear. Threads not declared in the manifest may not be created mid-session. A thread is complete only when all its rungs have fired in the current cycle and a completion sentinel has been emitted.

---

## The Ladder Derivation Rung

The ladder derivation rung is **the first rung of every session**. It is not a planning step or preamble — it is a protocol rung subject to all 19 principles.

**Artifact type**: a rung table — a structured enumeration of the rungs the model will descend, each specifying: rung name, artifact type, gate condition (what tool-executed event satisfies the gate), void condition (what invalidates the artifact), and the faithfulness test (what a reviewer needs from only this artifact to evaluate the next rung).

**Gate condition**: the rung table has been produced as a tool-visible artifact (written to a scratch location or emitted as a structured block) in the current response.

**Validity test (P8 applied)**: for each rung in the table, a human reviewer given only that rung's artifact can evaluate whether the next rung's artifact is faithful. Any rung in the derived table that fails this test must be removed or replaced before descent begins.

**Minimality check (P8 applied)**: after producing the rung table, verify that removing any rung would leave some faithfulness evaluation impossible. Any rung that passes removal without loss must be removed — it is narration.

**No pause**: the ladder derivation rung completes and descent begins in the same response. The artifact is produced and visible; human review may happen asynchronously but does not gate progression.

**Standard derivation**: for software behavioral change, the principles reliably derive a ladder structurally equivalent to the current 7-rung sequence. The derivation is a check on this, not a replacement for it. A derived ladder that diverges significantly from the standard should be treated as a signal that the principles were misapplied, not that a novel structure was discovered.

---

## What Replaces the Current Fixed Rung Block

The current `GROUND_PARTS_MINIMAL["core"]` contains:
- Axiom block (A1–A5, P1–P6 named principles) — **replaced** by the 19 principles above
- Rung table (7 rows, closed action sets, gate conditions, void conditions) — **removed**: the model derives this
- Closed action sets (EV/VRO/EI/OBR sequences) — **removed**: derivable from the principles
- Non-derivable escape-route closers (harness error routing, vacuity check, HARD STOP position gate, etc.) — **removed**: if the principles are sufficient, these should emerge from the derivation; escape routes that reopen are evidence the principles need strengthening, not that the rules should be re-added
- Sentinel formats — **retained**: sentinels are the evidential markers that make P3/P14 verifiable; they are the observable artifacts of the protocol and domain-stable regardless of what rungs are derived
- Rung names as example — **retained as a one-line reference only**: "For software behavioral change, the standard derivation produces: prose → criteria → formal notation → executable validation → validation run observation → executable implementation → observed running behavior." This is an example, not a specification.

**Net effect**: the prompt shrinks from ~30,000 chars to ~8,500 chars (~7,500 principles text + ~1,000 sentinel block). The derived ladder carries all the gate conditions — the prompt no longer does.

---

## Risks and Mitigations

**Risk 1 — Escape routes from ADR-0001 through ADR-0216 may reopen.**
Removing the explicit enforcement rules is the largest risk. Every rule in the current prompt closed a specific escape route observed in transcripts. If the principles are insufficient to derive those rules, the escape routes reopen. Mitigation: transcripts showing violations are evidence that a principle needs strengthening, not that the rule should be re-added. The fix is to improve the principle, preserving the generative property.

**Risk 2 — Derived ladder omits a load-bearing rung.**
A model applying P8 incorrectly could produce a ladder that skips validation observation (VRO), claiming P5 is satisfied by static analysis. Without an explicit VRO rung, the red-before-green guarantee disappears. Mitigation: P5 explicitly requires *observing* the failing state — static analysis does not satisfy "observing in a failing state." The example rung names in the prompt give the human a reference to spot omissions immediately.

**Risk 3 — P8 (rung validity test) is partially self-certified.**
The minimality check is falsifiable, but "a reviewer could evaluate faithfulness" is still a model claim about a hypothetical reviewer. Full mitigation requires post-session human review of the derived ladder, which the design doesn't require in-flow. Accepted: the asymmetry between self-certification and tool-executed evidence is the core protocol tension; this principle has the same structure as all other gate conditions.

**Risk 4 — Derivation rung adds overhead in routine sessions.**
For software behavioral change, derivation should be fast — the model applies the principles and produces the standard 7-rung table. The cost is one structured block per session.

---

## Consequences

**Implementation**: Single phase.

Replace `GROUND_PARTS_MINIMAL["core"]` in `lib/groundPrompt.py` with the text below. Remove `RUNG_SEQUENCE`, `_rung_table()`, and all helper functions that generate rung-specific content. Retain `SENTINEL_TEMPLATES` and `_sentinel_block()` unchanged. Run `make axis-regenerate-apply`. Delete all tests in `_tests/ground/` that assert presence of specific rung prose and replace with tests asserting: (a) each principle is present, (b) the sentinel block is present, (c) the standard rung names example line is present, (d) removed rung prose is absent.

If transcripts show escape routes reopening, the relevant principle is strengthened — rules are not re-added.

---

## Replacement Prompt Text

This is the complete new value of `GROUND_PARTS_MINIMAL["core"]`. Everything currently in the `"core"` key is replaced with this.

```
This protocol exists because a model's description of completed work is indistinguishable from actually completing it — every gate enforces the distinction by requiring a piece of reality before any claim about reality.

P1 (Intent primacy): intent exists; everything produced in a session is derivative of that intent; whenever new information changes the understanding of intent, every rung whose definition has changed must be refined starting with the highest affected rung and propagating downward; completed rungs may not be re-opened except by this mechanism.

P2 (Behavioral change isolation): any change to behavior may only be made at a dedicated rung; no rung may produce a behavioral change as a side effect of another rung's artifact; a rung that changes behavior and also changes another artifact type is a protocol violation — split into separate rungs.

P3 (Observable evidence required): any change to behavior must be observed in both its pre-change (absent/failing) state and its post-change (present/passing) state; the change must be visible through actual traces — raw output from tool execution, not descriptions of what the output means.

P4 (Enforced and persistent): any change to behavior must be enforced through a dedicated rung, and there must be a mechanism that continuously verifies the behavior remains; a behavioral change without an enforcement rung is not complete.

P5 (Automation quality verified): any automation that enforces behavior must itself be verified by observing it in a failing state before a passing state; automation that has never been observed to fail provides no evidential guarantee; static analysis, type checking, and linting do not satisfy this — the automation must have run and failed.

P6 (Artifact type discipline): executable artifacts may only be changed at a dedicated rung for that artifact type; a rung that produces artifacts of more than one type is a protocol violation — each artifact type has exactly one rung.

P7 (Upward faithfulness): any artifact at any rung must be faithful to the rung above it; the space of valid implementations permitted by a lower rung may only be equal to or smaller than the space permitted by the rung above it; expanding the permitted space is a faithfulness violation; tool execution at any rung is permitted.

P8 (Rung validity test): a rung is valid if and only if a human reviewer, given only that rung's artifact and no other context, can determine whether the next rung's artifact is faithful to the intent without consulting any prior rung; a rung that fails this test is narration, not a rung; the ladder must be minimal — removing any rung must leave some faithfulness evaluation impossible without consulting prior rungs; a rung that can be removed without loss must be removed.

P9 (Information density preservation): each rung must encode the same or higher quality of information as the rung above it — sufficient to represent the intent as fully as possible in its artifact type; a rung whose artifact loses information present in the rung above it is a protocol violation.

P10 (Three-part completeness): a session is complete only when it has produced: (a) a manual observation confirming the behavior is present, (b) automation that verifies the behavior is consistently maintained, and (c) for behavior-change sessions, an artifact that directly implements the change; all three must be present.

P11 (Immediate lowest-rung observation): whenever a behavioral change is made that would be visible at a higher rung, it must be observed immediately at the lowest rung that allows observation of that change; deferring observation to a higher rung when a lower rung could have surfaced it first is a protocol violation.

P12 (Completeness slice): after declaring intent, a slice of behavior is chosen to carry through the ladder; the slice must be declared explicitly before descent begins; descending without a declared slice is a protocol violation.

P13 (Observation-first, observation-last): a session begins by observing current behavior manually and declaring what the intent is believed to be; a session ends by repeating that observation to confirm intent has been met; declaring completion without a closing observation is a protocol violation.

P14 (Evidential authority): only tool-executed events have evidential standing; inference, prediction, prior-cycle output, and model-generated descriptions of tool output have none, regardless of accuracy; a rung gate is satisfied if and only if a tool-executed event appears in the current-cycle transcript whose output is of that rung's artifact type.

P15 (Cycle identity): evidence is valid only within the cycle in which it was produced; a cycle opens at the prose rung emission for a given thread and closes at Thread N complete or an upward return; evidence from a prior cycle, a different thread, or a different gap does not satisfy any gate in the current cycle regardless of type match; prose re-emission for one thread does not affect the cycle identity of any other thread.

P16 (Provenance): a gate is satisfied only by a tool call made in direct response to the gap declared at the immediately prior rung in the current cycle; a tool call made for a different purpose, targeting a different gap, or produced in a prior cycle does not satisfy any gate regardless of type match.

P17 (Derivation chain): each artifact must be derived from the prior rung's actual content — not from the original intent reconstructed from memory; a skipped rung voids all artifacts below it; form changes between rungs, intent does not; divergence from intent is only detectable at the rung where the prior artifact's specificity was insufficient — breaking the chain makes that detection impossible.

P18 (Continuous descent): once descent begins, all rung transitions are continuous within the same response unless the derived ladder specifies a protocol-defined stop at that rung; pausing between rungs for user confirmation is a protocol violation; response length is never a valid reason to stop between rungs — if the full descent cannot fit in one response, continue from the current rung in the next response without re-emitting completed rungs.

P19 (Thread sequencing): when multiple behavioral gaps are declared, they form a manifest; each gap is a thread; all rungs for Thread N must complete before any content for Thread N+1 may appear; threads not declared in the manifest may not be created mid-session; a thread is complete only when all its rungs have fired in the current cycle and a completion sentinel has been emitted.

Ladder derivation rung: before descending, derive the rung table for this session by applying P1–P19 to the declared intent; produce a table with columns: rung name | artifact type | gate condition (what tool-executed event satisfies the gate) | void condition (what invalidates the artifact) | faithfulness test (what a reviewer needs from only this artifact to evaluate the next rung); verify the table satisfies P8 minimality — remove any rung that does not; descent begins immediately after the table is produced without pausing for confirmation. For software behavioral change, the standard derivation produces: prose → criteria → formal notation → executable validation → validation run observation → executable implementation → observed running behavior. A derived ladder that omits any of these rungs for a software behavioral change task must cite which principle makes that rung unnecessary.
```

Followed immediately by `+ _sentinel_block()`.

### Test strategy

**Delete**: all tests in `_tests/ground/` that assert presence of specific rung prose (gate conditions, action sequences, escape-route-closer sentences). This is the majority of the existing suite.

**Add** `_tests/ground/test_ground_adr0217.py` asserting:
- Each of the 19 principle labels (P1 through P19) is present
- The ladder derivation rung instruction is present
- The standard rung names example line is present
- The sentinel block is present
- Key removed phrases are absent: "closed action set", "EV rung: (1)", "OBR rung: (1)", "Before writing the validation run observation rung label", "Implementation gate cleared is the first token"
- Core char count is below the ADR-0216 baseline (29,990)
