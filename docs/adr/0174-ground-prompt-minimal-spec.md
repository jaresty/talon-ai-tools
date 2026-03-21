# ADR-0174: Ground Prompt Minimal Spec (Stress-Test Experiment)

**Status:** Experimental
**Date:** 2026-03-21
**Relates to:** ADR-0172, ADR-0173

---

## Context

The ground method prompt (`lib/groundPrompt.py`) has grown to ~26,800 chars across four sections. ADR-0173 found that most of this length is load-bearing redundancy — each repeated phrase appears at a different violation hook. However, the fundamental question of whether the prompt is **overspecified** remains open.

A prompt is overspecified when rules patch anticipated violations rather than observed ones. The current prompt cannot distinguish these because it has no attached violation log. The accumulated patch rules may be overfitting to specific LLM failure modes observed during development, making the protocol fragile and domain-specific rather than general.

The hypothesis: a three-rule abstract core is sufficient for correct ground behavior, and the remaining ~26,000 chars are elaboration that either (a) patches violations that would not reappear without them, or (b) never catches violations in practice.

The experiment is designed to test this hypothesis empirically by running representative tasks against the minimal spec and logging every violation.

---

## Decision

Add `GROUND_PARTS_MINIMAL` to `lib/groundPrompt.py` as a parallel, switchable spec alongside the existing `GROUND_PARTS`. Extend `build_ground_prompt(minimal: bool = False)` to select between them.

**Minimal spec content:**

- **Rule 1:** Every claim about system state or artifact completeness is valid only if a tool-executed event in this conversation produced it.
- **Rule 2:** Each artifact derives from the prior rung — form changes, intent does not; a skipped rung voids all artifacts below it; each artifact addresses only the gap declared by the prior rung — nothing beyond it.
- **Rule 3:** Every thread ends when tool output names the declared gap; stop there.
- **Reconciliation gate:** At every upward rung transition — whether the scheduled formal-notation → executable-validation gate or any upward return triggered by new information — reconcile all artifacts at that rung against I before redescending. Documentation is a reconciliation artifact, not a thread.
- Seven rung names in order (from `RUNG_SEQUENCE`).
- Sentinel format strings (from `SENTINEL_TEMPLATES`).

Nothing else. No named violation modes, no edge-case qualifications, no patch rules.

**Note on documentation:** ADRs and design documents are representations of I, not deliverable threads. They are updated at reconciliation gates, not declared in the manifest.

**Switching mechanism:** `build_ground_prompt(minimal=True)` returns the minimal spec. The default (`minimal=False`) returns the full spec unchanged. The switch is at build time: edit `axisConfig.py` to call `build_ground_prompt(minimal=True)`, then run `make axis-regenerate-apply`.

---

## Consequences

**Experiment protocol:**

1. Switch to minimal: in `lib/axisConfig.py`, change the `build_ground_prompt()` call to `build_ground_prompt(minimal=True)`, then run `make axis-regenerate-apply`.
2. Run a representative task set (ideally the same tasks used in ADR-0113 evaluation loops).
3. Log every violation: which rule would have caught it, and which section of the full spec it lives in.
4. Restore: `git restore lib/axisConfig.py && make axis-regenerate-apply`.

**What counts as a violation:** Any point where the model skips a rung, produces an artifact without a required sentinel, modifies a prior artifact without upward correction, or conflates infrastructure events with behavioral observations.

**Decision rule for adding back a rule:** A rule is added back to `GROUND_PARTS_MINIMAL` only if a specific observed violation in the experiment would have been prevented by it. Rules that catch zero violations across the task set are candidates for permanent removal from the full spec.

**If the experiment succeeds** (few violations, manageable): retire `GROUND_PARTS` and make `GROUND_PARTS_MINIMAL` the production spec. Increment to a new ADR.

**If the experiment fails** (violations are frequent and severe): the full spec is justified. Document which rules caught which violations. Consider whether those rules can be stated more abstractly.

**Test coverage:** `_tests/test_ground_prompt_minimal.py` validates structure; `_tests/test_adr_0174.py` validates this document.
