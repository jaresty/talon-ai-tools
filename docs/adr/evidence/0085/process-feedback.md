# ADR-0085: Process Feedback
**Date:** 2026-02-25
**Cycles covered:** 16–19 (seeds 456–615); first meta-analysis since program start (cycles 1–15 deferred Phase 2b/2c entirely)
**Meta-analysis method:** `bar build probe full domains gap`

---

## Process Health Score: 3 / 5

Meaningful gaps found. Three issues had already caused observable drift: Phase 2b/2c deferred for 9 cycles, release lag on R37 undetected, and skim note inconsistency persisted across multiple cycles without being caught.

---

## Gaps Identified

### G1 — Phase 2b/2c deferred for 9 cycles (cadence failure)
**Score impact: visible drift**

The ADR implies meta-evaluation happens alongside rapid evaluation. In practice, phases 2b/2c were deferred from the program start through cycle 19 — 9 full cycles. During that time:
- The R37 narrow guidance was applied in cycle 16 and never verified against the installed binary
- The skim Composition Rules note has been incomplete since at least cycle 11 (when R36 was applied) — 8 cycles of misalignment between the skim note and Choosing Directional went undetected
- The "Grammar-enforced restrictions" section has been empty since bar help llm existed; no cycle detected it

**Root cause:** No explicit cadence constraint. The ADR says "after evaluating prompts" (implying always) but provides no enforcement or reminder mechanism.

**Recommendation:** The ADR now specifies 3–5 cycles as the maximum deferral. In practice: run Phase 2b/2c whenever a new fix is applied AND at least every 5 cycles regardless.

---

### G2 — Release pipeline verification absent (release lag)
**Score impact: R37 guidance invisible to users for unknown number of cycles**

After applying R37 (cycle 16) via `make bar-grammar-update`, no step verified that the guidance was visible in `bar help llm` output from the installed binary. The dev grammar JSON was updated; the installed binary was not.

**The implicit assumption:** "Running `make bar-grammar-update` propagates guidance to users." This is false — dev-repo changes require a Homebrew/Nix release to reach the installed binary.

**Discovery method:** This gap was only found during the meta-analysis because we ran `bar help llm | grep narrow` and got no output for the guidance.

**Recommendation:** Added as step 11a in the Refinement Cycle: after every `make bar-grammar-update`, run `bar help llm | grep -A3 "<token-name>"` for each modified token and confirm the guidance appears. If absent, file a release request and note it in `catalog-feedback.md` Release Lag Tracking table.

---

### G3 — Fix closure tracking is implicit, not structured
**Score impact: open recommendations accumulate; unclear which are implemented**

Cycle evaluations contain recommendations as free-form YAML in the Recommendations section. There is no single place to see: "Which recommendations are open? Which are applied? Which are verified against the installed binary?"

For example:
- R37 note: marked "Applied" in cycle-16 evaluations — but the meaning of "applied" was ambiguous (dev repo only, not installed binary)
- R40: marked "deferred to R41-grammar-hardening" across three cycles — the deferral is documented but there's no explicit owner or trigger condition
- The skim note fix (G3-catalog-feedback) was identified in cycle 11 and still not fixed in cycle 19

**Recommendation:** `process-feedback.md` should include a cumulative open recommendations table at each meta-analysis. This table tracks status across both rapid and meta-evaluation cycles.

---

### G4 — Score-3 "sparse" findings are systematically undercounted
**Score impact: may miss accumulating pattern signals**

Every cycle has 10–15 score-3 results labeled "sparse" — meaning the combination is valid but lacks enough constraint tokens to be interesting. These are not analyzed for patterns. But some "sparse" score-3s may be masking systematic gaps:
- Repeated score-3 for tasks with no scope token (seeds 517, 567, etc.) could indicate that bare tasks without scope tokens are reliably score-3, which is useful to document
- Score-3 for unusual form-as-channel combinations (score-3 seeds 498, 519, 529) go without cross-cycle analysis

**Implicit assumption:** Score-3 sparse = noise. But some sparse patterns recur across 3+ cycles and have not been catalogued.

**Recommendation:** Add a "Recurring score-3 sparse patterns" section to the aggregated work log entries. Three data points at score-3 across different cycles = the same threshold used for score-2 action (R37 was 3 data points). Apply consistently.

---

### G5 — Seed selection for meta-analysis was not explicitly sampled, just recalled from memory
**Score impact: potential confirmation bias**

The 10 seeds selected for this meta-analysis were chosen based on memory of cycle findings — the most notable score-2s and a few representative score-4s. This is subject to:
- Availability bias: seeds that produced clear findings are over-represented
- Recency bias: cycles 17–19 are better remembered than cycle 16
- Category bias: R40 seeds (shellscript) are over-represented (3 of 4 score-2 seeds)

**Recommendation:** For future meta-analyses, select seeds by a defined rule: N random score-4 seeds, all score-2 seeds from the covered cycles, and N score-3 seeds chosen by maximum recurrence count rather than subjective memory.

---

### G6 — Process Health Check (step 9) overlaps Phase 2d but is not explicitly connected
**Score impact: duplicated work without integration**

The Refinement Cycle step 9 says: "Run `probe gap` on the aggregated findings to surface implicit assumptions in the evaluation cycle itself." Phase 2d now adds a similar per-meta-analysis process evaluation. These overlap.

**Distinction:**
- Step 9 (Process Health Check): runs on `recommendations.yaml` before human review — validates that specific recommendations are well-formed and assumption-free
- Phase 2d (Process Self-Evaluation): evaluates the meta-analysis methodology itself — sampling strategy, cadence, release pipeline

They are complementary, not redundant. Step 9 is a pre-review gate for each recommendations batch. Phase 2d is a meta-analysis-level retrospective on the process as a whole.

**Recommendation:** Keep both. Clarify in the ADR that Phase 2d runs during meta-analysis cycles and step 9 runs during every cycle before review.

---

## Open Recommendations Tracking

*(Cumulative — update at each meta-analysis)*

| ID | Description | Status | Blocker |
|----|-------------|--------|---------|
| R37 | narrow+compound dir guidance note | Dev applied (cycle 16); not in installed binary | Needs bar release |
| R40 | shellscript cross-axis incompatibilities | ✅ Done (2026-02-26) — CROSS_AXIS_COMPOSITION cautionary data + Choosing Channel section + universal Reference Key rule | ADR-0147 complete |
| R41 | Cross-axis grammar hardening schema | Superseded by ADR-0147 | ADR-0147 implementation |
| F2 | Release narrow guidance (bar release) | Open — dev correct, installed binary outdated | Bar release required |
| F3 | Fix skim Composition Rules note | Open — dev already correct (full list), installed binary outdated | Bar release required |
| F4 | Add "Choosing Channel" section to help_llm.go | ✅ Done (2026-02-26) — ADR-0147 Phase 3b; renderCrossAxisComposition renders natural+cautionary per channel token | Deployed via help_llm.go |
| F5 | Fill "Grammar-enforced restrictions" section | ✅ Done (2026-02-25) | Deployed via help_llm.go fix |
| spike-task-tension | spike+gherkin, spike+sim — 2 data points | Watching | 3rd data point needed |

---

## ADR-0147 Phase 4 Validation (2026-02-26)

**Validation method:** Build score-2 seed combinations against updated dev grammar; verify universal rule present in prompt output; assess analytically whether first-principles guidance is sufficient.

### Seeds re-run

| Seed | Tokens | Pre-ADR-0147 issue | Post-ADR-0147 assessment |
|------|--------|-------------------|--------------------------|
| 531 | `probe minimal shellscript executive_brief` | LLM had no guidance for probe+shellscript | Universal rule: "what would it mean to produce probe task's output through shellscript?" → diagnostic shell script. Cautionary (probe→shellscript) now in bar help llm. Audience mismatch (to-CEO) still a runtime concern; cautionary in bar help llm. |
| 560 | `sim full shellscript fip-rog teach_junior_dev` | LLM had no guidance for sim+shellscript | Universal rule present. Cautionary (sim→shellscript: inherently narrative) now in bar help llm; LLM may still produce thin output for sim at runtime — structurally the weakest combination. |
| 615 | `probe max robust commit peer_engineer` | commit+max had no guidance | Cautionary (max→commit: no room for depth) now in bar help llm. Universal rule: "probe task output through commit format" = commit-formatted investigation notes. Commit form brevity constraint documented. |
| 588 | Not found in documented cycles | — | Not evaluated — may be from an undocumented cycle. |

### Reframe combinations (positive cases now handled by universal rule)

| Combination | Original reframe entry (removed) | Universal rule derivation | Assessment |
|-------------|----------------------------------|--------------------------|-----------|
| `shellscript+diff` | "shell script that diffs or compares" | Channel wins; task=diff becomes lens: produce a shell script that diffs the subject | ✓ derivable; score-4 expected for code subjects |
| `shellscript+sort` | "shell script that filters or orders" | Channel wins; task=sort becomes lens: produce a shell script that sorts the items | ✓ derivable; score-4 expected |
| `adr+pull` | "ADR capturing what was extracted" | Channel wins; task=pull becomes lens: express extraction in ADR format | ✓ derivable; score-4 expected |
| `gherkin+sim` | none (cautionary in bar help llm) | Channel wins; task=sim becomes lens: Gherkin scenarios expressing the scenario outcomes | ✓ structurally valid; quality depends on subject |

**Overall assessment:** Universal Reference Key rule (Phase 3a) provides first-principles guidance for previously-undocumented positive combinations. Cautionary entries in bar help llm (Phase 3b) provide pre-selection warnings for structurally-broken combinations. The two-tier approach (execution-time universal rule + pre-selection cautionary) meets the ADR-0147 design intent.

---

## Recommendations for Process

| Priority | Gap | Recommendation |
|----------|-----|----------------|
| High | G2 release pipeline | Step 11a: verify guidance in installed binary after every `make bar-grammar-update` |
| High | G3 fix closure | Add open recommendations tracking table to process-feedback.md; update at each meta-analysis |
| Medium | G1 cadence | Phase 2b/2c every 3–5 cycles; already added to ADR |
| Medium | G5 seed selection | Select meta-analysis seeds by rule (N random score-4, all score-2, N max-recurrence score-3) |
| Low | G4 score-3 sparse | Track recurring sparse patterns; treat 3+ occurrences same as score-2 threshold |
| Low | G6 step 9 / Phase 2d overlap | Clarify distinction in ADR; both are kept |
