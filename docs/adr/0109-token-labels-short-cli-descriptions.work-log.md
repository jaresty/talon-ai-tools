# ADR-0109 Work Log: Token Labels — Short CLI-Facing Descriptions

ADRs 0109 and 0110 share implementation surface (same schema fields, same Python/Go changes).
Loops 1–3 are executed jointly with ADR-0110. Loop 4 is shared documentation.
VCS_REVERT: `git stash -- <file>` then `git stash pop` to restore.

---

## Loop 1 — 2026-02-13 — Grammar schema + Go accessors (joint with ADR-0110)

helper_version: helper:v20251223.1

focus: ADR-0109 D1+D2, ADR-0110 D1+D3 — Add labels/guidance to grammar schema; expose
  AxisLabel(), TaskLabel(), AxisGuidance(), TaskGuidance() on Grammar.

active_constraint: Grammar.AxisLabel() and Grammar.TaskLabel() do not exist. No label data
  exists in the embedded grammar JSON. Therefore --plain cannot emit tab-separated labels
  (ADR-0109 D3) and bar help llm cannot show a Label column (ADR-0109 D5). This bottleneck
  outranks all downstream output changes because they cannot be specified until accessors exist.
  Falsifiable: `go test ./internal/barcli/ -run TestAxisLabelAccessorReturnsNonEmpty` exits 1
  (build failure) before implementation.

validation_targets:
  - go test ./internal/barcli/ -run TestAxisLabelAccessorReturnsNonEmpty
  - go test ./internal/barcli/ -run TestAxisGuidanceAccessorReturnsNonEmpty

rollback_plan: git stash -- internal/barcli/grammar.go; re-run validation targets to confirm
  red (build failure, methods undefined); git stash pop to restore.

evidence:
  - red | 2026-02-13T02:49:00Z | exit 1 (build failed) |
      go test ./internal/barcli/ -run TestAxisLabelAccessorReturnsNonEmpty
      app_help_cli_test.go:26:20: grammar.AxisLabel undefined (type *Grammar has no field or method AxisLabel)
      app_help_cli_test.go:31:23: grammar.TaskLabel undefined (type *Grammar has no field or method TaskLabel)
      helper:diff-snapshot=0 (tests added, no implementation yet) | inline

  - green | 2026-02-13T02:57:00Z | exit 0 |
      go test ./internal/barcli/ -run "TestAxisLabelAccessorReturnsNonEmpty|TestAxisGuidanceAccessorReturnsNonEmpty"
      helper:diff-snapshot=grammar.go +76, grammar JSON +180×3, axisConfig.py +188,
        staticPromptConfig.py +35, axisCatalog.py +12, promptGrammar.py +39 | inline

  - removal | 2026-02-13T03:00:04Z | exit 1 (build failed) |
      git stash -- internal/barcli/grammar.go &&
      go test ./internal/barcli/ -run "TestAxisLabelAccessorReturnsNonEmpty|TestAxisGuidanceAccessorReturnsNonEmpty"
      grammar.AxisLabel undefined; grammar.TaskLabel undefined; grammar.AxisGuidance undefined;
      grammar.TaskGuidance undefined — 10+ errors, build failed | inline
      git stash pop (restored at 2026-02-13T03:00:12Z)

delta_summary:
  helper:diff-snapshot: grammar.go +76, app_help_cli_test.go +93 (loop 1 portion),
    grammar JSON ×3 +180 each, axisConfig.py +188, staticPromptConfig.py +35,
    axisCatalog.py +12, promptGrammar.py +39.
  Rationale: Added AXIS_KEY_TO_LABEL (~90 tokens across 6 axes), AXIS_KEY_TO_GUIDANCE
  (7 audit tokens), _STATIC_PROMPT_LABELS (11 tasks), _STATIC_PROMPT_GUIDANCE (task:fix).
  Python pass-through in axisCatalog/promptGrammar. Go: AxisSection.Labels/Guidance,
  StaticSection.Labels/Guidance fields; rawAxisSection/rawStatic JSON tags; loader
  population; four accessor methods.

loops_remaining_forecast: 3 loops remaining (--plain output, bar help llm catalog,
  skill docs). Confidence: high.

residual_constraints:
  - --plain tab-separated output (ADR-0109 D3): renderTokensHelp not yet updated.
    Severity M. Monitoring: TestPlainOutputWithLabelTabSeparated red until Loop 2.
  - bar help llm Label column (ADR-0109 D5): help_llm.go not yet updated.
    Severity M. Monitoring: TestHelpLLMTokenCatalogHasLabelColumn red until Loop 3.
  - bar-manual skill docs (ADR-0109 D7): documentation-only, no test exists.
    Severity L. Monitoring: manual review in Loop 4.

next_work:
  Behaviour: --plain emits category:slug<TAB>label | Validation: TestPlainOutputWithLabelTabSeparated
  Behaviour: bar help tokens shows label + guidance inline | Validation: go test ./internal/barcli/ -run TestPlainOutputTokensHelp (backwards compat)

---

## Loop 2 — 2026-02-13 — --plain tab-separated output + bar help tokens display

helper_version: helper:v20251223.1

focus: ADR-0109 D3+D4, ADR-0110 D4 (partial) — Update renderTokensHelp in app.go:
  --plain emits category:slug<TAB>label; non-plain shows [label] + ↳ guidance.

active_constraint: renderTokensHelp emits bare category:slug in --plain mode and shows no
  label or guidance in full mode. Therefore TestPlainOutputWithLabelTabSeparated exits 1.
  Falsifiable: test fails with app.go at HEAD (before this loop's changes).

validation_targets:
  - go test ./internal/barcli/ -run TestPlainOutputWithLabelTabSeparated
  - go test ./internal/barcli/ -run TestPlainOutputTokensHelp  (backwards compat)

rollback_plan: git stash -- internal/barcli/app.go; re-run TestPlainOutputWithLabelTabSeparated
  to confirm red; git stash pop to restore.

evidence:
  - red | 2026-02-13T02:57:30Z | exit 1 |
      go test ./internal/barcli/ -run TestPlainOutputWithLabelTabSeparated
      app_help_cli_test.go:88: --plain output must include scope:act with tab-separated label
      helper:diff-snapshot=0 (app.go unchanged from HEAD at this point) | inline

  - green | 2026-02-13T02:58:30Z | exit 0 |
      go test ./internal/barcli/ -run "TestPlainOutputWithLabelTabSeparated|TestPlainOutputTokensHelp"
      helper:diff-snapshot=app.go +47 | inline

  - removal | 2026-02-13T03:00:31Z | exit 1 |
      git stash -- internal/barcli/app.go &&
      go test ./internal/barcli/ -run TestPlainOutputWithLabelTabSeparated
      app_help_cli_test.go:88: --plain output must include scope:act with tab-separated label | inline
      git stash pop (restored at 2026-02-13T03:00:40Z, exit 0)

delta_summary:
  helper:diff-snapshot: app.go +47 lines.
  Rationale: task and axis plain branches now call AxisLabel()/TaskLabel() and emit
  category:slug<TAB>label when non-empty. Non-plain branches emit • token [Label]\n
  description\n  ↳ guidance pattern. Backwards compat preserved: grep '^scope:' and
  cut -f1 still work; TestPlainOutputTokensHelp passes unchanged.

loops_remaining_forecast: 2 loops remaining (bar help llm catalog, skill docs). Confidence: high.

residual_constraints:
  - bar help llm Label + Notes columns (ADR-0109 D5, ADR-0110 D4): help_llm.go not yet updated.
    Severity M. Monitoring: TestHelpLLMTokenCatalogHasLabelColumn red until Loop 3.
  - bar-manual skill docs (ADR-0109 D7): documentation-only. Severity L.

next_work:
  Behaviour: bar help llm Token Catalog has Label + Notes columns |
    Validation: TestHelpLLMTokenCatalogHasLabelColumn

---

## Loop 3 — 2026-02-13 — bar help llm Token Catalog Label + Notes columns

helper_version: helper:v20251223.1

focus: ADR-0109 D5, ADR-0110 D4 — Update help_llm.go renderTokenCatalog: expand
  two-column tables to four columns (Token | Label | Description | Notes).

active_constraint: renderTokenCatalog emits two-column tables with no Label or Notes column.
  TestHelpLLMTokenCatalogHasLabelColumn fails. Specifying validation written after
  implementation (non-compliant order); removal evidence retroactively establishes contract.
  Falsifiable: git stash -- internal/barcli/help_llm.go causes test to fail at all four assertions.

validation_targets:
  - go test ./internal/barcli/ -run TestHelpLLMTokenCatalogHasLabelColumn

rollback_plan: git stash -- internal/barcli/help_llm.go; re-run validation target to confirm
  red; git stash pop to restore.

evidence:
  - red (removal-first) | 2026-02-13T03:00:50Z | exit 1 |
      git stash -- internal/barcli/help_llm.go &&
      go test ./internal/barcli/ -run TestHelpLLMTokenCatalogHasLabelColumn
      app_help_cli_test.go:122: Token Catalog tables must include a Label column
      app_help_cli_test.go:125: Token Catalog tables must include a Notes column
      app_help_cli_test.go:130: Token Catalog must include scope:act label 'Tasks and intended actions'
      app_help_cli_test.go:135: Token Catalog must include task:fix guidance in Notes column | inline

  - green | 2026-02-13T03:00:59Z | exit 0 |
      git stash pop &&
      go test ./internal/barcli/ -run TestHelpLLMTokenCatalogHasLabelColumn
      helper:diff-snapshot=help_llm.go +16 | inline

  Non-compliant ordering note: specifying validation (TestHelpLLMTokenCatalogHasLabelColumn)
  was written after implementation rather than before. The removal-first evidence above
  demonstrates the validation fully specifies the behaviour and the implementation satisfies it.
  Future loops for this ADR must write the specifying validation before implementation.

delta_summary:
  helper:diff-snapshot: help_llm.go +16, app_help_cli_test.go +36 (loop 3 portion).
  Rationale: Task table header changed from `| Token | Description |` to
  `| Token | Label | Description | Notes |`. Axis table headers same. Row format
  calls AxisLabel()/TaskLabel() and AxisGuidance()/TaskGuidance() for the two new cells.

loops_remaining_forecast: 1 loop remaining (skill docs, documentation-only). Confidence: high.

residual_constraints:
  - bar-manual skill docs (ADR-0109 D7): no automated test exists for skill file content.
    Severity L. Blocker: validation commands exercise compiled CLI paths; grep/string checks
    do not qualify per helper. Mitigation: manual review + next loop is documentation-only.

next_work:
  Behaviour: bar-manual skill --plain docs updated | Blocker: no CLI test for skill content.

---

## Loop 4 — 2026-02-13 — bar-manual skill --plain documentation (documentation-only)

helper_version: helper:v20251223.1

focus: ADR-0109 D7 — Update --plain comment in bar-manual/skill.md (×3 copies) to reflect
  tab-separated format and add cut -f1 example.

active_constraint: bar-manual skill still documents --plain as `category:slug one per line`,
  omitting the tab-separated label format. No automated test exists for skill file content;
  validation commands exercise the compiled CLI path — grep/string checks do not qualify
  per helper compliance rules. This is the repository-controlled bottleneck for this loop.

validation_targets: (none — documentation-only loop; blocker evidence below)

rollback_plan: git restore --source=HEAD .claude/skills/bar-manual/skill.md
  .opencode/skills/bar-manual/skill.md internal/barcli/skills/bar-manual/skill.md

evidence:
  - blocker | 2026-02-13T03:01:00Z | no automated test exists |
      No Go test or make target exercises skill file content. The helper prohibits
      grep/string checks as validation. This loop is documentation-only per contract.
      helper:diff-snapshot: .claude, .opencode, internal/barcli skill copies each +1 line
      (cut -f1 example added) and comment updated from "one per line" to tab-format. | inline

delta_summary:
  helper:diff-snapshot: ×3 skill files, each +1 line (cut -f1 example), comment updated.
  Rationale: Reflects ADR-0109 D3 behaviour now live in compiled CLI. No executable
  artefacts changed in this loop.

loops_remaining_forecast: 0 loops remaining. All ADR-0109 behaviours have landed green
  or have documented blocker evidence (skill docs, editorial label quality).

residual_constraints:
  - Editorial label quality: labels authored from description review; cannot be
    machine-validated. Severity L. Mitigation: labels reviewed against full descriptions
    during authoring; revisit when grammar tokens are added or renamed.
    Monitoring: re-audit AXIS_KEY_TO_LABEL on any token rename or addition.
  - ADR-0110 description trimming (D2): guidance is now populated but the mixed-content
    sentences have not yet been removed from the corresponding descriptions in axisConfig.py.
    Severity M. Monitoring: tracked in ADR-0110 work-log as residual for a future loop.
    Owning ADR: 0110.

next_work: (none — ADR-0109 complete pending editorial quality review)
