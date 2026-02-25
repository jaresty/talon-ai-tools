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

---

## Loop 2 — 2026-02-25

```yaml
helper_version: helper:v20251223.1
focus: ADR-0146 Change 1 — add max/grow tension to AXIS_KEY_TO_GUIDANCE; remove hardcoded block
active_constraint: >
  Neither completeness:max nor method:grow had any AXIS_KEY_TO_GUIDANCE entry;
  the tension note existed only as hardcoded Go prose in renderTokenSelectionHeuristics.
  The new specifying test (TestHelpLLMMaxGrowGuidanceInSSoT) failed red on all three
  assertions: no max guidance, no grow guidance, hardcoded block present.
  Expected value: Impact=High (prevents SSOT drift on key compatibility rule),
  Probability=High (deterministic), Time Sensitivity=Low.
validation_targets:
  - go test ./internal/barcli/... -run TestHelpLLMMaxGrowGuidanceInSSoT -count=1
evidence:
  - red  | 2026-02-25T00:05:00Z | exit 1 | go test ./internal/barcli/... -run TestHelpLLMMaxGrowGuidanceInSSoT
      helper:diff-snapshot=0 files changed
      3 failures: max guidance empty, grow guidance empty, hardcoded block present | inline
  - green | 2026-02-25T00:07:00Z | exit 0 | go test ./internal/barcli/... -run TestHelpLLMMaxGrowGuidanceInSSoT
      helper:diff-snapshot=7 files changed, 48 insertions(+), 7 deletions(-)
      TestHelpLLMMaxGrowGuidanceInSSoT PASS; full suite ok | inline
  - removal | 2026-02-25T00:08:00Z | exit 1 | git stash impl && go test ... && git stash pop
      helper:diff-snapshot=0 files changed (impl reverted; test remains)
      All 3 assertions fail again after revert | inline
rollback_plan: git restore --source=HEAD lib/axisConfig.py internal/barcli/help_llm.go; make bar-grammar-update
delta_summary: >
  helper:diff-snapshot=7 files changed, 48 insertions(+), 7 deletions(-)
  Added completeness:max and method:grow guidance entries to AXIS_KEY_TO_GUIDANCE in
  axisConfig.py. Removed 2-line hardcoded "Completeness × Method compatibility" block
  from help_llm.go; added cross-reference pointer sentence. Ran make bar-grammar-update
  to propagate guidance into prompt-grammar.json and TUI fixture.
  Depth-first rung: Change 1 lands green.
loops_remaining_forecast: "4 loops (Change 2, then Phase 2 loops 4–6). Confidence: high."
residual_constraints:
  - Change 2 (channel × audience): code/shellscript guidance still missing audience
    incompatibility note in AXIS_KEY_TO_GUIDANCE. Hardcoded bullet still in help_llm.go:917.
    Severity: Medium. Mitigation: Loop 3.
  - Phase 2 (routing concept): AXIS_KEY_TO_ROUTING_CONCEPT not yet in axisConfig.py.
    Severity: Medium. Mitigation: Loops 4–6.
next_work:
  - Behaviour: Change 2 — add channel × audience incompatibility to AXIS_KEY_TO_GUIDANCE
    for code and shellscript; remove hardcoded bullet from help_llm.go
    Validation: go test ./internal/barcli/... -run TestHelpLLMChannelAudienceGuidanceInSSoT
```

---

## Loop 3 — 2026-02-25

```yaml
helper_version: helper:v20251223.1
focus: ADR-0146 Change 2 — add channel × audience incompatibility to AXIS_KEY_TO_GUIDANCE for code/shellscript; remove hardcoded bullet
active_constraint: >
  channel:code and channel:shellscript had no audience incompatibility note in
  AXIS_KEY_TO_GUIDANCE. The hardcoded bullet in help_llm.go:917 was the only
  location. codetour already documents "Avoid with manager, PM, executive, CEO..."
  so no change needed there. The new specifying test
  (TestHelpLLMChannelAudienceGuidanceInSSoT) failed red on both guidance checks
  and the hardcoded-block check.
  Expected value: Impact=High (rule silently lost if channel tokens are added without
  matching help_llm.go edit), Probability=High, Time Sensitivity=Low.
validation_targets:
  - go test ./internal/barcli/... -run TestHelpLLMChannelAudienceGuidanceInSSoT -count=1
evidence:
  - red  | 2026-02-25T00:10:00Z | exit 1 | go test ./internal/barcli/... -run TestHelpLLMChannelAudienceGuidanceInSSoT
      helper:diff-snapshot=0 files changed
      channel:code/shellscript missing "non-technical" in guidance; hardcoded bullet present | inline
  - green | 2026-02-25T00:12:00Z | exit 0 | go test ./internal/barcli/... -run TestHelpLLMChannelAudienceGuidanceInSSoT
      helper:diff-snapshot=7 files changed (inc. grammar regeneration)
      TestHelpLLMChannelAudienceGuidanceInSSoT PASS; full suite ok | inline
  - removal | 2026-02-25T00:13:00Z | exit 1 | git stash impl && go test ... && git stash pop
      channel:shellscript missing, hardcoded bullet present | inline
rollback_plan: git restore --source=HEAD lib/axisConfig.py internal/barcli/help_llm.go; make bar-grammar-update
delta_summary: >
  helper:diff-snapshot=7 files changed
  Added audience incompatibility note to channel:code and channel:shellscript in
  AXIS_KEY_TO_GUIDANCE. Confirmed codetour guidance already covers non-technical
  audiences — no change needed. Removed hardcoded "Channel × audience compatibility"
  bullet from Choosing Persona heuristic in help_llm.go.
  Phase 1 complete: all three SSOT violations resolved.
  Depth-first rung: Change 2 lands green. Phase 1 done.
loops_remaining_forecast: "3 loops (Phase 2: AXIS_KEY_TO_ROUTING_CONCEPT data, grammar structs, dynamic rendering). Confidence: medium."
residual_constraints:
  - Phase 2 step 1: AXIS_KEY_TO_ROUTING_CONCEPT not yet in axisConfig.py.
    Concept phrases for scope (11 tokens) and form (~11 tokens) need enumeration.
    Severity: Medium (scope/form routing still hardcoded). Mitigation: Loop 4.
  - Phase 2 step 2: RoutingConcept field not yet in grammar structs.
    Severity: Low (blocked by step 1). Mitigation: Loop 5.
  - Phase 2 step 3: Choosing Scope/Form still renders ~30 hardcoded bullets.
    Severity: Low (blocked by steps 1-2). Mitigation: Loop 6.
next_work:
  - Behaviour: Phase 2 step 1 — add AXIS_KEY_TO_ROUTING_CONCEPT for scope and form
    Validation: .venv/bin/python -m pytest _tests/test_routing_concept.py -v
```

---

## Loop 4 — 2026-02-25

```yaml
helper_version: helper:v20251223.1
focus: ADR-0146 Phase 2 step 1 — add AXIS_KEY_TO_ROUTING_CONCEPT dict and accessor to axisConfig.py
active_constraint: >
  AXIS_KEY_TO_ROUTING_CONCEPT did not exist. There was no per-token routing concept
  metadata for scope or form axes. The specifying test (test_routing_concept.py) failed
  red at import time (ImportError). No grammar wiring needed in this loop — that is
  Loop 5's job.
  Expected value: Impact=High (unblocks Loops 5-6; establishes the phrase table that
  must be reviewed in one pass per ADR risk mitigation), Probability=High, Time Sensitivity=Low.
validation_targets:
  - .venv/bin/python -m pytest _tests/test_routing_concept.py -v
evidence:
  - red  | 2026-02-25T00:20:00Z | exit 1 | .venv/bin/python -m pytest _tests/test_routing_concept.py
      helper:diff-snapshot=0 files changed
      ImportError: cannot import name 'AXIS_KEY_TO_ROUTING_CONCEPT' | inline
  - green | 2026-02-25T00:22:00Z | exit 0 | .venv/bin/python -m pytest _tests/test_routing_concept.py
      helper:diff-snapshot=lib/axisConfig.py modified (+38 lines), _tests/test_routing_concept.py created
      7 tests pass; make bar-grammar-update + go test also pass | inline
  - removal | 2026-02-25T00:23:00Z | exit 1 | git stash lib/axisConfig.py && pytest && git stash pop
      ImportError re-appears after stash | inline
rollback_plan: git restore --source=HEAD lib/axisConfig.py; remove _tests/test_routing_concept.py
delta_summary: >
  helper:diff-snapshot=2 files changed
  Added AXIS_KEY_TO_ROUTING_CONCEPT dict covering scope (13 tokens, 12 concept groups)
  and form (8 tokens, 6 concept groups) with exact phrases matching current hardcoded
  Choosing Scope/Form bullets. Added axis_key_to_routing_concept_map accessor.
  Created _tests/test_routing_concept.py with 7 specifying tests (RC1-RC7).
  Grammar update + Go test suite remain green.
  Depth-first rung: Phase 2 step 1 lands green.
loops_remaining_forecast: "2 loops (Loop 5: grammar struct + export wiring; Loop 6: dynamic rendering). Confidence: high."
residual_constraints:
  - Grammar export not yet wired: prompt-grammar.json has no routing_concept field.
    Severity: Medium (Loops 5-6 blocked). Mitigation: Loop 5.
  - Go grammar structs have no RoutingConcept field yet. Severity: Low (blocked by export).
    Mitigation: Loop 5.
  - Choosing Scope/Form still renders hardcoded bullets. Severity: Low (blocked by Loop 5).
    Mitigation: Loop 6.
next_work:
  - Behaviour: Phase 2 step 2 — wire routing_concept into grammar export; add RoutingConcept
    field to Go grammar structs
    Validation: go test ./internal/barcli/... -run TestHelpLLMRoutingConceptInGrammar
```

---

## Loop 5 — 2026-02-25

```yaml
helper_version: helper:v20251223.1
focus: ADR-0146 Phase 2 step 2 — wire routing_concept into grammar export pipeline; add RoutingConcept to Go structs
active_constraint: >
  grammar.Axes.RoutingConcept field did not exist. The Go struct (AxisSection) had
  no RoutingConcept field; the JSON had no routing_concept key; axisCatalog.py
  and promptGrammar.py did not pass routing concept data through the export pipeline.
  The specifying test (TestHelpLLMRoutingConceptInGrammar) failed red at compile time
  (undefined field). All four touch points needed simultaneous change.
  Expected value: Impact=High (unblocks Loop 6 dynamic rendering), Probability=High, Time Sensitivity=Low.
validation_targets:
  - go test ./internal/barcli/... -run TestHelpLLMRoutingConceptInGrammar -count=1
evidence:
  - red  | 2026-02-25T00:30:00Z | exit 1 | go test ./internal/barcli/... -run TestHelpLLMRoutingConceptInGrammar
      helper:diff-snapshot=0 files changed
      Build failed: grammar.Axes.RoutingConcept undefined | inline
  - green | 2026-02-25T00:35:00Z | exit 0 | go test ./internal/barcli/... -run TestHelpLLMRoutingConceptInGrammar
      helper:diff-snapshot=5 files modified (grammar.go, axisCatalog.py, promptGrammar.py, + grammar JSONs)
      TestHelpLLMRoutingConceptInGrammar PASS; full suite ok; routing_concept in JSON | inline
  - removal | 2026-02-25T00:36:00Z | exit 1 | git stash impl && go test ... && git stash pop
      Build fails again (undefined field) | inline
rollback_plan: git restore --source=HEAD internal/barcli/grammar.go lib/axisCatalog.py lib/promptGrammar.py; make bar-grammar-update
delta_summary: >
  helper:diff-snapshot=9 files changed
  Added RoutingConcept field to AxisSection and rawAxisSection in grammar.go with
  json:"routing_concept" tag. Added axis_routing_concept to axisCatalog.py axis_catalog()
  and serialize_axis_config(). Added routing_concept handling in promptGrammar.py
  (parallel to categories pattern). Ran make bar-grammar-update — routing_concept now
  appears in build/prompt-grammar.json under axes.routing_concept.{form,scope}.
  Depth-first rung: Phase 2 step 2 lands green.
loops_remaining_forecast: "1 loop (Loop 6: dynamic rendering of Choosing Scope/Form). Confidence: high."
residual_constraints:
  - Choosing Scope/Form still renders hardcoded bullets in help_llm.go.
    Severity: Medium (final SSOT violation — the whole point of Phase 2).
    Mitigation: Loop 6.
next_work:
  - Behaviour: Phase 2 step 3 — rewrite Choosing Scope/Form to render dynamically
    from grammar.Axes.RoutingConcept
    Validation: go test ./internal/barcli/... -run TestHelpLLMScopeFormDynamic
```
