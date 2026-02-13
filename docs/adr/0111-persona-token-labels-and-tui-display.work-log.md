# ADR-0111 Work Log: Persona Token Labels and Label-First TUI Display

VCS_REVERT: `git stash -- <file>` then `git stash pop` to restore.

---

## Loop 1 — 2026-02-13 — Persona axis labels schema + Go accessor (ADR-0111 D1+D2)

helper_version: helper:v20251223.1

focus: ADR-0111 D1+D2 — Add PERSONA_KEY_TO_LABEL to personaConfig.py (~38 tokens across
  voice/audience/tone/intent); update promptGrammar.py to emit persona.labels in JSON;
  add Labels field to rawPersona and PersonaSection in grammar.go; expose PersonaLabel()
  accessor method.

active_constraint: grammar.PersonaLabel() does not exist. Persona axis tokens have no label
  field in the grammar schema. TestPersonaLabelAccessorReturnsNonEmpty fails to build
  (PersonaLabel undefined). Falsifiable: exit 1 (build failed) before implementation.

validation_targets:
  - go test ./internal/barcli/ -run TestPersonaLabelAccessorReturnsNonEmpty

rollback_plan: git stash -- lib/personaConfig.py lib/promptGrammar.py
  internal/barcli/grammar.go internal/barcli/embed/prompt-grammar.json
  build/prompt-grammar.json cmd/bar/testdata/grammar.json;
  re-run target to confirm build failure; git stash pop.

evidence:
  - red | 2026-02-13T07:17:53Z | exit 1 (build failed) |
      go test ./internal/barcli/ -run TestPersonaLabelAccessorReturnsNonEmpty
      app_help_cli_test.go:310:20: grammar.PersonaLabel undefined
      helper:diff-snapshot=0 (test written, no implementation yet) | inline

  - green | 2026-02-13T07:19:16Z | exit 0 |
      go test ./internal/barcli/ -run TestPersonaLabelAccessorReturnsNonEmpty
      helper:diff-snapshot=personaConfig.py +58 (PERSONA_KEY_TO_LABEL + accessor),
        promptGrammar.py +10 (import + labels block in section),
        grammar.go +26 (Labels field in PersonaSection + rawPersona, loader line,
          PersonaLabel() method +23 lines), grammar JSON ×3 regenerated | inline

  - removal | 2026-02-13T07:19:28Z | exit 1 (build failed) |
      git stash -- lib/personaConfig.py lib/promptGrammar.py internal/barcli/grammar.go
        internal/barcli/embed/prompt-grammar.json build/prompt-grammar.json
        cmd/bar/testdata/grammar.json &&
      go test ./internal/barcli/ -run TestPersonaLabelAccessorReturnsNonEmpty
      Build fails: PersonaLabel undefined (all ADR-0109/0110 accessors also absent,
      confirming grammar.go is causal) | inline
      git stash pop (2026-02-13T07:19:37Z)

delta_summary:
  helper:diff-snapshot: personaConfig.py +58, promptGrammar.py +10, grammar.go +26,
    grammar JSON ×3 regenerated.
  PERSONA_KEY_TO_LABEL authored for all 38 tokens across voice (11), audience (15),
  tone (5), intent (7). Grammar.PersonaLabel() looks up persona.labels[axis][token]
  with exact + lowercase fallback. D1 and D2 complete.

loops_remaining_forecast: 2 loops remaining (--plain wiring, tui2 display). Confidence: high.

residual_constraints:
  - --plain persona labels (ADR-0111 D3): app.go persona/intent rendering still emits
    bare slugs. Severity M. Monitoring: run bar help tokens --plain; verify no tab after
    persona:design. Planned: Loop 2.
  - tui2 label display (ADR-0111 D4): buildPersonaOptions, buildAxisOptions,
    buildStaticCategory still use displayLabel(value, description). Severity M.
    Monitoring: tui_tokens_test if exists; else manual tui2 inspection. Planned: Loop 3.

next_work:
  Behaviour: --plain emits tab-separated labels for persona presets, persona axes,
    intent tokens |
    Validation: go test ./internal/barcli/ -run TestPlainOutputPersonaLabels

---

## Loop 2 — 2026-02-13 — --plain labels for persona presets/axes/intent (ADR-0111 D3)

helper_version: helper:v20251223.1

focus: ADR-0111 D3 — Update app.go renderTokensHelp --plain rendering for persona presets,
  persona axes (voice/audience/tone), and intent tokens to emit category:slug<TAB>label.

active_constraint: --plain rendering for persona/intent tokens emits bare slugs.
  TestPlainOutputPersonaLabels fails (not yet written) because the test defines correct
  tab-separated format; without app.go changes the tab will be absent.
  Falsifiable: exit 1 after specifying test is written.

validation_targets:
  - go test ./internal/barcli/ -run TestPlainOutputPersonaLabels

rollback_plan: git stash -- internal/barcli/app.go;
  re-run target to confirm failure; git stash pop.

evidence:
  - red | 2026-02-13T07:20:27Z | exit 1 |
      go test ./internal/barcli/ -run TestPlainOutputPersonaLabels
      5 failures: persona:design, voice:as-kent-beck, audience:to-ceo, tone:casually,
      intent:announce all missing tab-separated label in --plain output.
      helper:diff-snapshot=0 (test written, no app.go changes yet) | inline

  - green | 2026-02-13T07:32:13Z | exit 0 |
      go test ./internal/barcli/ -run TestPlainOutputPersonaLabels
      helper:diff-snapshot=app.go +18 (3 plain rendering blocks updated: persona presets,
        persona axes, intent tokens — each now emits <TAB><label> when PersonaLabel
        or preset.Label is non-empty) | inline

  - removal | 2026-02-13T07:32:23Z | exit 1 |
      git stash -- internal/barcli/app.go &&
      go test ./internal/barcli/ -run TestPlainOutputPersonaLabels
      All 5 failures re-appear | inline
      git stash pop (2026-02-13T07:32:31Z)

delta_summary:
  helper:diff-snapshot: app.go +18. Three --plain rendering blocks updated.
  Persona presets now emit persona:<slug><TAB><preset.Label>. Persona axes emit
  <axis>:<slug><TAB><PersonaLabel()>. Intent tokens emit intent:<slug><TAB><PersonaLabel("intent",token)>.
  All fall back to bare slug when no label. D3 complete.

loops_remaining_forecast: 1 loop remaining (tui2 label display). Confidence: high.

residual_constraints:
  - tui2 label display (ADR-0111 D4): buildPersonaOptions, buildAxisOptions,
    buildStaticCategory still use displayLabel(value, description). Severity M.
    Planned: Loop 3.

next_work:
  Behaviour: tui2 TokenOption.Label uses short labels for axis/task/persona tokens |
    Validation: go test ./internal/barcli/ -run TestTUITokenCategoriesUseShortLabels

---

## Loop 3 — 2026-02-13 — tui2 uses labels for all token types (ADR-0111 D4)

helper_version: helper:v20251223.1

focus: ADR-0111 D4 — Update tui_tokens.go buildStaticCategory, buildAxisOptions, and
  buildPersonaOptions to prefer grammar.TaskLabel/AxisLabel/PersonaLabel over the full
  long description for the TokenOption.Label field. Update tui_smoke.json snapshot
  to match new short-label display.

active_constraint: buildAxisOptions, buildStaticCategory, buildPersonaOptions all use
  displayLabel(value, description) which returns the full prompt-injection text.
  TestTUITokenCategoriesUseShortLabels (written this loop) fails because token Labels
  contain multi-sentence descriptions rather than the 3-8 word short labels.
  Falsifiable: exit 1 confirmed after test written, before tui_tokens.go edited.

validation_targets:
  - go test ./internal/barcli/ -run TestTUITokenCategoriesUseShortLabels
  - go test ./internal/barcli/ -run TestRunTUIFixtureOutputsSnapshot

rollback_plan: git stash -- internal/barcli/tui_tokens.go cmd/bar/testdata/tui_smoke.json;
  re-run TestTUITokenCategoriesUseShortLabels (specifying test stays in place);
  git stash pop.

evidence:
  - red | 2026-02-13T07:33:09Z | exit 1 |
      go test ./internal/barcli/ -run TestTUITokenCategoriesUseShortLabels
      3 failures: scope:act, task:make, voice:as-kent-beck all have full descriptions
      as Label (e.g. "The response focuses on..."), not short labels.
      helper:diff-snapshot=0 (test written, no tui_tokens.go changes yet) | inline

  - green | 2026-02-13T07:35:23Z | exit 0 |
      go test ./internal/barcli/...
      All tests pass including TestTUITokenCategoriesUseShortLabels and
      TestRunTUIFixtureOutputsSnapshot (after snapshot update).
      helper:diff-snapshot=tui_tokens.go +18 (3 option builders updated with
        shortLabel := grammar.TaskLabel/AxisLabel/PersonaLabel; fallback to
        displayLabel when empty), tui_test.go +53 (specifying test added),
        tui_smoke.json expected_view updated (lines 10, 13, 15 now show short labels) | inline

  - removal | 2026-02-13T07:35:58Z | exit 1 |
      git stash -- internal/barcli/tui_tokens.go cmd/bar/testdata/tui_smoke.json &&
      go test ./internal/barcli/ -run TestTUITokenCategoriesUseShortLabels
      All 3 failures re-appear: "The response focuses on...", "The response creates...",
      "The response channels..." — confirming tui_tokens.go and snapshot are causal | inline
      git stash pop (2026-02-13T07:36:08Z)

delta_summary:
  helper:diff-snapshot: tui_tokens.go +18, tui_test.go +53, tui_smoke.json updated.
  buildStaticCategory: TaskLabel() preferred over displayLabel.
  buildAxisOptions: AxisLabel() preferred over displayLabel.
  buildPersonaOptions: PersonaLabel() preferred over displayLabel.
  All three fall back to displayLabel(value, description) for tokens without labels.
  Description field unchanged — still available for hover/expand views.
  tui_smoke.json snapshot regenerated with new short-label output.
  ADR-0111 D4 and ADR-0109 D4 (deferred tui2 item) complete.

loops_remaining_forecast: 1 loop remaining (bartui2 program.go display format). Confidence: high.

residual_constraints:
  - bartui2 completion display (ADR-0111 D4 tui2 fix): program.go updateCompletions uses
    label-only display; user confirmed format should be "slug — label". Severity H.
    Planned: Loop 4.

next_work:
  Behaviour: bartui2 completion Display uses "slug — label" format when label available |
    Validation: go test ./internal/bartui2/ -run TestCompletionDisplayUsesLabel

---

## Loop 4 — 2026-02-13 — bartui2 completion display uses "slug — label" format (ADR-0111 D4)

helper_version: helper:v20251223.1

focus: ADR-0111 D4 (tui2 fix) — Update bartui2/program.go updateCompletions to display
  completions as "slug — label" (e.g. "act — Tasks and intended actions") when
  TokenOption.Label is set, instead of label-only. Also enable fuzzy matching against
  opt.Label. Update program_test.go assertions to the correct format.

active_constraint: updateCompletions used label-only display (Display := opt.Label), ignoring
  the slug. User confirmed "slug — label" format required. TestCompletionDisplayUsesLabel
  asserts c.Display == "Todo" (wrong); after test update it asserts "todo — Todo" and fails.
  Falsifiable: exit 1 after test update, before program.go edit.

validation_targets:
  - go test ./internal/bartui2/ -run TestCompletionDisplayUsesLabel
  - go test ./internal/bartui2/ -run TestCompletionListScrolling
  - go test ./internal/bartui2/...

rollback_plan: git stash -- internal/bartui2/program.go;
  re-run TestCompletionDisplayUsesLabel (specifying test stays in place);
  confirm exit 1 with got "todo" (pre-impl display); git stash pop.

evidence:
  - red | 2026-02-13T07:48:36Z | exit 1 |
      go test ./internal/bartui2/ -run "TestCompletionDisplayUsesLabel|TestCompletionListScrolling"
      TestCompletionDisplayUsesLabel: got "Todo" (not "todo — Todo")
      TestCompletionListScrolling: expected "option4 — Option 4" not found
      helper:diff-snapshot=0 (tests updated to correct format, no program.go change yet) | inline

  - green | 2026-02-13T07:48:50Z | exit 0 |
      go test ./internal/bartui2/...
      All tests pass.
      helper:diff-snapshot=program.go +3 (slugDisplay := formatCompletionDisplay; display =
        slugDisplay + " — " + opt.Label when label set; label fuzzy match retained),
        program_test.go +2 (assertions updated to "todo — Todo" and
        "option%d — Option %d" format) | inline

  - removal | 2026-02-13T07:49:18Z | exit 1 |
      git stash -- internal/bartui2/program.go &&
      go test ./internal/bartui2/ -run "TestCompletionDisplayUsesLabel|TestCompletionListScrolling"
      TestCompletionDisplayUsesLabel: got "todo" (pre-impl formatCompletionDisplay)
      TestCompletionListScrolling: expected "option4 — Option 4" not found
      confirming program.go is causal | inline
      git stash pop (2026-02-13T07:49:27Z)

delta_summary:
  helper:diff-snapshot: program.go +3, program_test.go +2.
  updateCompletions now computes slugDisplay := formatCompletionDisplay(...) first,
  then display = slugDisplay + " — " + opt.Label when opt.Label is non-empty.
  Fuzzy match against opt.Label retained from Loop 4 initial pass.
  Assertions updated: "todo — Todo", "option%d — Option %d".
  Full suite green.

loops_remaining_forecast: 0 loops remaining. All D1–D4 + tui2 fix implemented.

residual_constraints: none.

next_work: ADR-0111 complete. ADR-0109 D4 (tui2) now also satisfied.
