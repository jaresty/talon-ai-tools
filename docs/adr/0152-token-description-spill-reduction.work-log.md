# ADR-0152 Work Log — Token Description Spill Reduction

---

## Loop-2 — 2026-03-03T01:20:00Z

```yaml
helper_version: helper:v20260227.1
focus: >
  ADR-0152 T-3 — load-bearing test of the "may not be attributed" cluster:
  afford, polar, trans, canon. Documentation loop; no executable artefacts change.

active_constraint: >
  The "may not be attributed to X without Y" clauses in afford, polar, trans,
  canon cannot be trimmed until their load-bearing status is determined.
  Blocker evidence: no behavioral tests exist to distinguish definitional
  clauses from prescriptive spill for these tokens.

validation_targets:
  - T-3 (documentation-only): per-token written analysis recorded in work-log;
    no executable validation; decision governs whether T-5 scope includes these
    tokens.

evidence:
  - red | 2026-03-03T01:20:00Z | documentation-only |
    No per-token decision recorded; trimming any of the four without analysis
    risks removing definitional content. | inline

delta_summary: >
  helper:diff-snapshot=0 files changed (documentation-only loop).
  Blocker: no executable artefacts change; per-token analysis follows.

  Per-token analysis:
  - afford: "Outcomes may not be attributed solely to preferences or incentives
    without modeling how affordances influenced selection." — This IS the
    negative-space definition of affordance theory. Affordance analysis is
    distinguished from preference/incentive analysis by exactly this exclusion.
    Removing it would allow shallow "preferences shaped behavior" conclusions
    to pass as afford analysis. Decision: KEEP.
  - canon: "Explanations may not treat multiple representations of the same
    knowledge as independent causal or justificatory elements without specifying
    their dependency relationship." — Canonicalization is defined by what it
    prohibits: treating duplicate representations as independent. Without this
    clause, canon is just "use one authoritative source" which doesn't guard
    against the failure mode (multiple references to the same concept without
    declared dependency). Decision: KEEP.
  - polar: "Outcomes may not be attributed solely to positive objectives without
    modeling active avoidance pressures." — Polar dynamics requires BOTH
    attractors and repellers. Without this clause, polar becomes indistinguishable
    from single-attractor goal-maximization. The clause is the structural
    definition of polarity. Decision: KEEP.
  - trans: "Outcomes may not be attributed to communication without specifying
    how the signal survived, degraded, or was corrected during transmission." —
    Shannon information theory's core claim: "communication occurred" is not
    complete without modeling the channel and noise. Without this, trans can
    be used for casual message-passing analysis that lacks information-theoretic
    rigor. Decision: KEEP.

  Structural test that separates definitional "may not" from spill "may not":
  Spill (verify, balance): the "may not" clause expresses a POLICY (who is
  the authority, what procedure to follow) external to the concept's meaning.
  Definitional (afford, canon, polar, trans): the "may not" clause expresses
  what the concept EXCLUDES or PROHIBITS — the negative space that defines the
  concept's boundary. Removing it would allow misapplication by conflation
  with adjacent concepts.

loops_remaining_forecast: >
  2 loops remaining.
  Loop-3: T-4+T-5 — infrastructure decision + migrate contextualise/socratic
  task-pairing to use_when; condense quiz/facilitate/cocreate/taxonomy
  channel-conditional language.
  presenterm stays blocked (no notes field; decision: no new infrastructure).

residual_constraints:
  - T-4/T-5 | Cross-axis coupling migration | severity: Medium |
    contextualise and socratic embed task-pairing conditionals in descriptions;
    quiz/facilitate/cocreate/taxonomy have channel-conditional descriptions.
    use_when already partially covers some cases (quiz). Next loop. ADR: 0152.
  - presenterm | Technical spec | severity: Low |
    Stays blocked: T-4 decision (next loop) will confirm no new notes field,
    leaving presenterm out of scope. ADR: 0152.

next_work:
  - Behaviour T-4+T-5: Add task-pairing guidance to contextualise and socratic
    use_when; remove "With X:" conditionals from their descriptions. Condense
    quiz/facilitate/cocreate/taxonomy channel-conditional language. Run
    bar-grammar-update. Specifying validation: absence assertions for
    "With pull:" in contextualise and "With sort/plan:" in socratic.
```

---

## Loop-1 — 2026-03-03T01:00:00Z

```yaml
helper_version: helper:v20260227.1
focus: >
  ADR-0152 Phase 1 — T-1 (trim verify) and T-2 (trim balance).
  Remove policy/ethics language from verify; remove methodology prescription
  sentences 2–4 from balance. Sync grammar files.

active_constraint: >
  Five test assertions fail because policy language is present in verify and
  methodology prescription is present in balance. Demonstrated by:
  python3 -m pytest _tests/test_token_description_spill.py exits 1 with 5 failures.
  Outranks T-3 (cluster testing) and T-4/T-5 (cross-axis migration) because
  confidence is high and no behavioral testing is required for these two tokens.

validation_targets:
  - T-1+T-2: >
      python3 -m pytest _tests/test_token_description_spill.py exits 0 (7 passed).
      Asserts: verify has no "transfer authority", "human oversight",
      "trust beyond the model"; verify retains "falsification pressure" +
      "causal chain integrity". balance has no "restoring or destabilizing
      dynamics", "No configuration may be treated as stable"; balance retains
      "balancing forces".

evidence:
  - red | 2026-03-03T01:00:00Z | exit=1 |
      python3 -m pytest _tests/test_token_description_spill.py
      (test file present, spill phrases still in axisConfig.py —
      5 failed, 2 passed) | inline
  - green | 2026-03-03T01:05:00Z | exit=0 |
      python3 -m pytest _tests/test_token_description_spill.py
      (7 passed after trimming verify and balance in AXIS_KEY_TO_VALUE) | inline
  - removal | 2026-03-03T01:06:00Z | exit=1 |
      git stash && python3 -m pytest _tests/test_token_description_spill.py
      (5 failed again; git stash pop restored trims) | inline

rollback_plan: >
  git restore lib/axisConfig.py build/prompt-grammar.json
  internal/barcli/embed/prompt-grammar.json cmd/bar/testdata/grammar.json
  cmd/bar/testdata/tui_smoke.json web/static/prompt-grammar.json
  && rm _tests/test_token_description_spill.py
  Re-run validation to confirm 5 tests fail.

delta_summary: >
  helper:diff-snapshot=6 files changed
  - lib/axisConfig.py: verify trimmed to 1 sentence (falsification core only);
    balance trimmed to 2 sentences (definition + opposing pressures core);
    removed: authority-transfer/human-oversight policy (verify) and
    transient-state/perturbation methodology (balance)
  - build/prompt-grammar.json, internal/barcli/embed/prompt-grammar.json,
    cmd/bar/testdata/grammar.json, web/static/prompt-grammar.json: grammar
    files regenerated via make bar-grammar-update reflecting the trimmed descriptions
  - _tests/test_token_description_spill.py: 7 specifying assertions (5 absence
    checks + 2 core-retention checks)

loops_remaining_forecast: >
  3 loops remaining (confidence: high).
  Loop-2: T-3 — load-bearing test of the "may not" cluster (afford, polar,
  trans, canon); analysis/documentation loop.
  Loop-3: T-4 — infrastructure decision (CROSS_AXIS_COMPOSITION vs. use_when
  for cross-axis coupling migration).
  Loop-4: T-5 — migrate conditional coupling out of contextualise, socratic,
  taxonomy, quiz, facilitate, cocreate descriptions.

residual_constraints:
  - T-3 | "may not be attributed" cluster | severity: Medium |
    afford, polar, trans, canon all have "may not be attributed to X without Y"
    clauses. These are formal-discipline tokens where the negative constraint
    may be load-bearing. Testing required before trimming. Monitoring: no test
    coverage exists for behavioral output quality yet. Owning ADR: 0152.
  - T-4/T-5 | Cross-axis coupling in form descriptions | severity: Medium |
    contextualise, socratic, taxonomy, quiz, facilitate, cocreate embed
    "With X:" and "Adapts to channel:" conditional guidance in descriptions.
    Correct home TBD (T-4). Owning ADR: 0152.
  - presenterm | Technical spec in description | severity: Low |
    Blocked on T-4 infrastructure decision. Owning ADR: 0152.

next_work:
  - Behaviour T-3: Documentation loop — analyze afford, polar, trans, canon
    "may not" clauses to determine if load-bearing. Compare each clause against
    the semantic core; record per-token keep/trim decision. No executable
    validation required if all four are determined to be definitional.
```
