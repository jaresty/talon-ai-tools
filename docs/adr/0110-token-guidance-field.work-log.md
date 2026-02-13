# ADR-0110 Work Log: Token Guidance Field — Separate Selection Hints from Execution Instructions

ADRs 0109 and 0110 share implementation surface. Loops 1–3 executed jointly with ADR-0109.
Evidence records are shared; this file records ADR-0110-specific framing and residuals.
VCS_REVERT: `git stash -- <file>` then `git stash pop` to restore.

---

## Loop 1 — 2026-02-13 — Grammar schema + Go accessors (joint with ADR-0109)

helper_version: helper:v20251223.1

focus: ADR-0110 D1+D3 (joint with ADR-0109 D1+D2) — Add guidance field to grammar schema;
  expose AxisGuidance() and TaskGuidance() on Grammar. Populate guidance for 7 audit tokens
  identified in ADR-0110 D2: task:fix, channel:code, channel:html, channel:shellscript,
  channel:gherkin, channel:codetour, form:facilitate.

active_constraint: Grammar.AxisGuidance() and Grammar.TaskGuidance() do not exist. Guidance
  data for the 7 audit tokens is not in the grammar JSON. The description trimming in D2
  (removing mixed-content sentences from axisConfig.py descriptions) cannot be safely
  performed until the guidance field is populated and verified — trimming first would lose
  the selection-oriented content. Falsifiable: TestAxisGuidanceAccessorReturnsNonEmpty exits 1
  (build failure) before implementation.

validation_targets:
  - go test ./internal/barcli/ -run TestAxisGuidanceAccessorReturnsNonEmpty
  - go test ./internal/barcli/ -run TestAxisLabelAccessorReturnsNonEmpty  (shared)

rollback_plan: git stash -- internal/barcli/grammar.go; re-run TestAxisGuidanceAccessorReturnsNonEmpty
  to confirm build failure; git stash pop to restore.

evidence:
  - red | 2026-02-13T02:49:00Z | exit 1 (build failed) |
      go test ./internal/barcli/ -run TestAxisGuidanceAccessorReturnsNonEmpty
      app_help_cli_test.go:50:25: grammar.TaskGuidance undefined
      app_help_cli_test.go:54:25: grammar.AxisGuidance undefined
      helper:diff-snapshot=0 (tests added, no implementation yet) | inline

  - green | 2026-02-13T02:57:00Z | exit 0 |
      go test ./internal/barcli/ -run "TestAxisLabelAccessorReturnsNonEmpty|TestAxisGuidanceAccessorReturnsNonEmpty"
      helper:diff-snapshot=grammar.go +76, grammar JSON +180×3, axisConfig.py +188 (includes
        AXIS_KEY_TO_GUIDANCE with 7 audit tokens), staticPromptConfig.py +35 (includes
        _STATIC_PROMPT_GUIDANCE with task:fix), axisCatalog.py +12, promptGrammar.py +39 | inline

  - removal | 2026-02-13T03:00:04Z | exit 1 (build failed) |
      git stash -- internal/barcli/grammar.go &&
      go test ./internal/barcli/ -run TestAxisGuidanceAccessorReturnsNonEmpty
      grammar.AxisGuidance undefined; grammar.TaskGuidance undefined — build failed | inline
      git stash pop (restored at 2026-02-13T03:00:12Z)

delta_summary:
  helper:diff-snapshot: grammar.go +76, grammar JSON ×3 +180 each, axisConfig.py +188,
    staticPromptConfig.py +35, axisCatalog.py +12, promptGrammar.py +39.
  ADR-0110-specific changes: AXIS_KEY_TO_GUIDANCE in axisConfig.py (channel: code, codetour,
  gherkin, html, shellscript; form: facilitate), _STATIC_PROMPT_GUIDANCE in staticPromptConfig.py
  (task: fix). Go: Grammar.Axes.Guidance, Grammar.Static.Guidance fields; AxisGuidance(),
  TaskGuidance() methods.

loops_remaining_forecast: 3 loops remaining (help tokens display, help llm Notes column,
  description trimming). Confidence: high for display loops; medium for trimming (requires
  per-token judgement call on which sentences to remove).

residual_constraints:
  - Description trimming (ADR-0110 D2): mixed-content sentences still present in axisConfig.py
    descriptions for the 7 audit tokens. Cannot trim until guidance field is verified (done
    this loop). Severity M. Monitoring: inspect channel:code description — "Not appropriate for
    narrative tasks..." sentence still present; must be removed in a future loop.
    Planned: dedicated loop after display work is complete.
  - help tokens ↳ guidance display (ADR-0110 D4): app.go not yet updated.
    Severity M. Monitoring: manual bar help tokens channel output.
  - help llm Notes column (ADR-0110 D4): help_llm.go not yet updated.
    Severity M. Monitoring: TestHelpLLMTokenCatalogHasLabelColumn red until Loop 3.

next_work:
  Behaviour: bar help tokens shows ↳ guidance for audit tokens |
    Validation: go test ./internal/barcli/ -run TestPlainOutputTokensHelp (backwards compat);
    manual inspection of bar help tokens channel output for ↳ lines.

---

## Loop 2 — 2026-02-13 — bar help tokens guidance display (joint with ADR-0109 Loop 2)

helper_version: helper:v20251223.1

focus: ADR-0110 D4 (partial), ADR-0109 D3+D4 — app.go renderTokensHelp shows
  ↳ guidance line for tokens with guidance defined.

active_constraint: renderTokensHelp does not emit guidance. The ↳ pattern is absent from
  bar help tokens output. Jointly addressed with ADR-0109 D3 (tab-separated plain output)
  in the same app.go edit.

validation_targets:
  - go test ./internal/barcli/ -run TestPlainOutputWithLabelTabSeparated  (shared, ADR-0109)
  - go test ./internal/barcli/ -run TestPlainOutputTokensHelp  (backwards compat)

rollback_plan: git stash -- internal/barcli/app.go; re-run targets; git stash pop.

evidence:
  - red | 2026-02-13T02:57:30Z | exit 1 |
      go test ./internal/barcli/ -run TestPlainOutputWithLabelTabSeparated
      (shared with ADR-0109 Loop 2; guidance display validated via manual CLI inspection) | inline

  - green | 2026-02-13T02:58:30Z | exit 0 |
      go test ./internal/barcli/ -run "TestPlainOutputWithLabelTabSeparated|TestPlainOutputTokensHelp"
      helper:diff-snapshot=app.go +47 | inline

  - removal | 2026-02-13T03:00:31Z | exit 1 |
      git stash -- internal/barcli/app.go &&
      go test ./internal/barcli/ -run TestPlainOutputWithLabelTabSeparated
      app_help_cli_test.go:88 fails | inline
      git stash pop (2026-02-13T03:00:40Z)

delta_summary:
  helper:diff-snapshot: app.go +47.
  ADR-0110-specific: axis token loop now calls AxisGuidance(); task loop calls TaskGuidance().
  Both emit `      ↳ <guidance>\n` when non-empty. channel:code and task:fix both show
  guidance in `bar help tokens channel` and `bar help tokens task` respectively.

loops_remaining_forecast: 2 loops remaining (help llm Notes column, description trimming).

residual_constraints:
  - help llm Notes column (ADR-0110 D4): TestHelpLLMTokenCatalogHasLabelColumn red until Loop 3.
    Severity M.
  - Description trimming (ADR-0110 D2): still deferred. Severity M.
    Monitoring: channel:code description still contains "Not appropriate for narrative tasks..."
    Planned loop: after Loop 3.

next_work:
  Behaviour: bar help llm Token Catalog has Notes column |
    Validation: TestHelpLLMTokenCatalogHasLabelColumn

---

## Loop 3 — 2026-02-13 — bar help llm Token Catalog Notes column (joint with ADR-0109 Loop 3)

helper_version: helper:v20251223.1

focus: ADR-0110 D4, ADR-0109 D5 — help_llm.go Token Catalog tables expanded to
  4 columns: Token | Label | Description | Notes.

active_constraint: renderTokenCatalog emits two-column tables; Notes column absent.
  TestHelpLLMTokenCatalogHasLabelColumn fails on `| Notes |` header and task:fix guidance.
  Specifying validation written after implementation (non-compliant); removal-first evidence
  establishes contract retroactively.

validation_targets:
  - go test ./internal/barcli/ -run TestHelpLLMTokenCatalogHasLabelColumn

rollback_plan: git stash -- internal/barcli/help_llm.go; re-run; git stash pop.

evidence:
  - red (removal-first) | 2026-02-13T03:00:50Z | exit 1 |
      git stash -- internal/barcli/help_llm.go &&
      go test ./internal/barcli/ -run TestHelpLLMTokenCatalogHasLabelColumn
      app_help_cli_test.go:125: Token Catalog tables must include a Notes column
      app_help_cli_test.go:135: Token Catalog must include task:fix guidance in Notes column | inline

  - green | 2026-02-13T03:00:59Z | exit 0 |
      git stash pop &&
      go test ./internal/barcli/ -run TestHelpLLMTokenCatalogHasLabelColumn
      helper:diff-snapshot=help_llm.go +16 | inline

  Non-compliant ordering note: same as ADR-0109 Loop 3.

delta_summary:
  helper:diff-snapshot: help_llm.go +16, app_help_cli_test.go +36 (loop 3 portion).
  ADR-0110-specific: Notes column populated by AxisGuidance()/TaskGuidance() calls.
  task:fix guidance ("fix means reformat — not debug") now visible in bar help llm output.

loops_remaining_forecast: 1 loop remaining (description trimming, ADR-0110 D2).
  This loop is deferred — it requires per-token judgement and has no failing test yet.
  A specifying validation must be written before that loop proceeds.

residual_constraints:
  - Description trimming (ADR-0110 D2): mixed-content sentences still present in 7 audit
    token descriptions. Severity M. Monitoring: inspect `channel:code` description in
    axisConfig.py — "Not appropriate for narrative tasks..." still present as of this loop.
    Mitigation: defer to standalone loop with specifying validation (e.g. a test that
    verifies the description does NOT contain "Not appropriate" after trimming).
    Reopen condition: any token whose description still contains guidance-like sentences
    after this ADR is otherwise complete.

next_work:
  Behaviour: audit token descriptions trimmed of selection guidance (ADR-0110 D2) |
    Specifying validation: new test asserting description does not contain guidance sentence |
    Blocker: no failing test yet; this loop must not proceed as documentation-only.

---

## Loop 4 — 2026-02-13 — Description trimming for 7 audit tokens (ADR-0110 D2)

helper_version: helper:v20251223.1

focus: ADR-0110 D2 — Trim mixed-content sentences from descriptions of 7 audit tokens.
  Selection guidance already moved to guidance field (Loop 1). This loop removes the
  now-redundant guidance sentences from the description field so execution instructions
  are pure behavioral contracts.

active_constraint: TestAuditTokenDescriptionsAreTrimmed (written prior to this loop) fails
  for all 7 audit tokens — guidance phrases still present in axisConfig.py and
  staticPromptConfig.py descriptions. Grammar JSON not yet regenerated after trim.
  Falsifiable: exit 1 confirmed (red evidence) before any edits this loop.

validation_targets:
  - go test ./internal/barcli/ -run TestAuditTokenDescriptionsAreTrimmed

rollback_plan: git stash -- lib/axisConfig.py lib/staticPromptConfig.py
  internal/barcli/embed/prompt-grammar.json build/prompt-grammar.json
  cmd/bar/testdata/grammar.json; re-run target to confirm failure; git stash pop.

evidence:
  - red | 2026-02-13T03:06:12Z | exit 1 |
      go test ./internal/barcli/ -run TestAuditTokenDescriptionsAreTrimmed
      7 failures: channel:code, channel:html, channel:shellscript, channel:gherkin,
      channel:codetour, form:facilitate (axisConfig.py); task:fix (staticPromptConfig.py)
      helper:diff-snapshot=0 (specifying test written; no trimming yet) | inline

  - green | 2026-02-13T07:14:04Z | exit 0 |
      go test ./internal/barcli/ -run TestAuditTokenDescriptionsAreTrimmed
      helper:diff-snapshot=axisConfig.py -6 lines (5 guidance sentences removed across
        channel:code, channel:html, channel:shellscript, channel:gherkin, channel:codetour,
        form:facilitate), staticPromptConfig.py -1 line (task:fix Note sentence removed),
        grammar JSON ×3 regenerated | inline

  - removal | 2026-02-13T07:14:09Z | exit 1 |
      git stash -- lib/axisConfig.py lib/staticPromptConfig.py
        internal/barcli/embed/prompt-grammar.json build/prompt-grammar.json
        cmd/bar/testdata/grammar.json &&
      go test ./internal/barcli/ -run TestAuditTokenDescriptionsAreTrimmed
      All 7 failures re-appear (channel:code "Not appropriate for narrative tasks",
      task:fix "Note: in bar's grammar", etc.) — stash confirmed causal | inline
      git stash pop (2026-02-13T07:14:15Z)

delta_summary:
  helper:diff-snapshot: axisConfig.py -6 (removed trailing guidance sentences from
    channel:code, channel:html, channel:shellscript, channel:gherkin, channel:codetour,
    form:facilitate), staticPromptConfig.py -1 (task:fix Note sentence removed),
    grammar JSON ×3 regenerated (no schema change; description values shorter).
  ADR-0110 D2 is now complete. All 7 audit token descriptions are pure execution
  instructions; selection guidance lives exclusively in the guidance field.

loops_remaining_forecast: 0 loops remaining for ADR-0110. All decisions implemented.
  ADR status updated to Accepted — Implementation complete.

residual_constraints: none.

next_work: ADR-0110 complete. Follow-on work tracked separately:
  - ADR-0109 D4 (tui2 label display) — pending
  - Persona/audience/tone/voice/intent labels in --plain — pending (new ADR required)
