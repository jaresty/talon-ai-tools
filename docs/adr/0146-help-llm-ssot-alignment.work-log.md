# Work Log — ADR 0146: Help LLM SSOT Alignment

Helper version: `helper:v20251223.1`

Evidence root: `docs/adr/evidence/0146/`

VCS_REVERT: `git restore --source=HEAD`

---

## Loop 1 — 2026-02-25

```yaml
helper_version: helper:v20251223.1
focus: ADR-0146 Change 3 — remove hardcoded "Choosing intent=" line from renderTokenSelectionHeuristics
active_constraint: >
  The hardcoded fmt.Fprintf line at help_llm.go:921 renders a stale abbreviation
  of PERSONA_KEY_TO_USE_WHEN["intent"] in the Token Selection Heuristics section.
  This creates a SSOT violation: when a new intent token is added, the hardcoded
  line silently omits it while the Token Catalog renders correctly. The new
  specifying test (TestHelpLLMNoHardcodedIntentLine) will fail red until the
  line is removed.
  Expected value: Impact=High (SSOT violation that silently omits tokens),
  Probability=High (deterministic — line present in source), Time Sensitivity=Low.
validation_targets:
  - go test ./internal/barcli/... -run TestHelpLLMNoHardcodedIntentLine -count=1
evidence:
  - red  | 2026-02-25T00:00:00Z | exit 1 | go test ./internal/barcli/... -run TestHelpLLMNoHardcodedIntentLine
      helper:diff-snapshot=0 files changed
      TestHelpLLMNoHardcodedIntentLine: "ADR-0146 Change 3: hardcoded '**Choosing intent=**' line must be removed" | inline
  - green | 2026-02-25T00:01:00Z | exit 0 | go test ./internal/barcli/... -run TestHelpLLMNoHardcodedIntentLine
      helper:diff-snapshot=2 files changed, 17 insertions(+), 1 deletion(-)
      TestHelpLLMNoHardcodedIntentLine PASS; full suite ok | inline
  - removal | 2026-02-25T00:02:00Z | exit 1 | git stash -- help_llm.go && go test ... && git stash pop
      helper:diff-snapshot=0 files changed (impl reverted; test remains)
      TestHelpLLMNoHardcodedIntentLine fails again after revert | inline
rollback_plan: git restore --source=HEAD internal/barcli/help_llm.go; replay red
delta_summary: >
  helper:diff-snapshot=2 files changed, 17 insertions(+), 1 deletion(-)
  Added TestHelpLLMNoHardcodedIntentLine specifying test (+17 lines);
  removed single hardcoded fmt.Fprintf line for "Choosing intent=" (-1 line).
  Intent use_when already rendered in Token Catalog via PERSONA_KEY_TO_USE_WHEN["intent"].
  Depth-first rung: Change 3 lands green.
loops_remaining_forecast: "5 loops (Changes 1, 2, then Phase 2 loops 4–6). Confidence: high."
residual_constraints:
  - Change 1 (max/grow tension): no AXIS_KEY_TO_GUIDANCE entries yet for
    completeness:max or method:grow. Severity: Medium (SSOT violation, but
    guidance renders elsewhere via hardcoded prose). Mitigation: Loop 2.
    Monitoring: TestHelpLLMMaxGrowGuidanceInSSoT (to be added in Loop 2).
  - Change 2 (channel × audience): code/shellscript guidance missing audience
    incompatibility note. Severity: Medium. Mitigation: Loop 3.
  - Phase 2 (routing concept): AXIS_KEY_TO_ROUTING_CONCEPT dict not yet in
    axisConfig.py; scope/form sections remain hardcoded. Severity: Medium.
    Mitigation: Loops 4–6.
next_work:
  - Behaviour: Change 1 — add max/grow cross-axis tension to AXIS_KEY_TO_GUIDANCE
    Validation: go test ./internal/barcli/... -run TestHelpLLMMaxGrowGuidanceInSSoT
```
