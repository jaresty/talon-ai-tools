# Work Log — ADR-0108: Channel-Adaptive Interactive Forms

**Helper version:** `helper:v20251223.1`
**Evidence root:** `docs/adr/evidence/0108/`
**VCS revert:** `git restore --source=HEAD`
**Validation target:** `make bar-grammar-update && go test ./... 2>&1`

---

## Loop 1 — 2026-02-11

**focus:** ADR-0108 D1 (channel-adaptive rewrites for cocreate/quiz/facilitate) + D2 (remove interactive-form conflict section from help_llm.go) + ADR-0107 residuals restored after removal-evidence revert

**active_constraint:** `cocreate`, `quiz`, `facilitate` descriptions define the behavior as inherently interactive, causing 2/5 failures when paired with output-exclusive channels. The Interactive-form conflicts section in § Incompatibilities documents these as prohibited rather than channel-adaptive.

**context cited:** ADR-0108 § Decision 1 and § Decision 2; ADR-0107 work-log Loop 2 (axisConfig.py changes reverted by removal evidence, required restoration in this loop); cycle 5 evidence seeds 0082, 0085.

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | High | Eliminates a category of 2/5 failures and opens valid new combinations |
| Probability | High | Direct description rewrite, no structural schema change |
| Time Sensitivity | Medium | Immediate quality improvement to catalog |

**validation_targets:**
- `go test ./internal/barcli/ -run "TestLLMHelpADR0108Decisions" -v`
- `go test ./... 2>&1`

**evidence:**
- red | 2026-02-11T00:20:00Z | exit 1 | `go test ./internal/barcli/ -run "TestLLMHelpADR0108Decisions" -v`
  - helper:diff-snapshot=test file added (ADR-0108 test); axisConfig.py and help_llm.go at pre-ADR-0108 state
  - D1: missing 'output-exclusive channel' in catalog; D2: 'Interactive-form conflicts' still present | inline
- green | 2026-02-11T00:25:00Z | exit 0 | `make bar-grammar-update && go test ./... 2>&1`
  - helper:diff-snapshot=6 files changed, 171 insertions(+), 33 deletions(-)
  - All packages pass including TestLLMHelpADR0108Decisions | inline
- removal | 2026-02-11T00:26:00Z | exit 1 | `git restore --source=HEAD lib/axisConfig.py internal/barcli/help_llm.go && make bar-grammar-update && go test ./internal/barcli/ -run "TestLLMHelpADR0108Decisions" -v`
  - helper:diff-snapshot=0 files changed (revert only)
  - D1 fails: 'output-exclusive channel' missing from catalog | inline

**rollback_plan:** `git restore --source=HEAD lib/axisConfig.py internal/barcli/help_llm.go internal/barcli/embed/prompt-grammar.json build/prompt-grammar.json cmd/bar/testdata/grammar.json` then verify TestLLMHelpADR0108Decisions fails red.

**delta_summary:** Rewrote `cocreate`, `quiz`, `facilitate` descriptions as channel-adaptive — each now describes the default interactive mode (no channel) and the static-artifact mode (with output-exclusive channel). Removed Interactive-form conflicts section from `renderCompositionRules`. Also restored ADR-0107 changes (help_llm.go adr task-affinity rule + prose-form extended channel list; axisConfig.py scaffold, bug descriptions) which were wiped by the removal-evidence revert. Full suite clean.

**loops_remaining_forecast:** 0. All ADR-0108 behaviours implemented and green. ADR-0108 completion bar met.

**residual_constraints:**
- severity: Low | No prefix enforcement test exists — the descriptions for cocreate/quiz/facilitate no longer start with "The response" (they start with verb phrases: "Structures…", "Organizes…"). The existing test suite does not enforce this convention, so no breakage. Future ADR may want to establish a description convention test if uniformity matters.

**next_work:** None. ADR-0108 complete.
