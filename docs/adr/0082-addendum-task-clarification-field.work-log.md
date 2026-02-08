# 0082 – Addendum: Task clarification field — Work Log

## Loop 1: Rename "Static Prompt" display to "Task" in TUI2

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — TUI2 display labels and stage headers. Rename "Static Prompt" / "STATIC" to "Task" / "TASK" in bartui2 view layer.
- **active_constraint**: TUI2 `stageDisplayName("static")` returns `"Static"` and test data uses `Label: "Static Prompt"`, causing the UI to display confusing "STATIC" stage header and "Static Prompt" category labels instead of user-meaningful "TASK" / "Task".
- **validation_targets**:
  - `go test ./internal/bartui2/ -run "TestInitialView|TestStageProgressionView|TestGetCategoryForToken|TestSnapshotBasicLayout|TestSnapshotWithCompletions|TestTokenTreeWithCategoryLabels"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/bartui2/ -run "TestSnapshotWithCompletions"` — `program_test.go:329: expected TASK stage header in view` | inline
    helper:diff-snapshot=1 file changed (program_test.go only; program.go unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/bartui2/ -run "TestInitialView|TestStageProgressionView|TestGetCategoryForToken|TestSnapshotBasicLayout|TestSnapshotWithCompletions|TestTokenTreeWithCategoryLabels"` — all 4 matched tests PASS | inline
    helper:diff-snapshot=2 files changed, 23 insertions(+), 23 deletions(-)
  - removal | 2026-02-07T (git restore program.go) | exit 1 | `git restore internal/bartui2/program.go && go test ./internal/bartui2/ -run "TestSnapshotWithCompletions"` — `program_test.go:329: expected TASK stage header in view` returns | inline
    helper:diff-snapshot=0 files changed (program.go reverted)
- **rollback_plan**: `git restore internal/bartui2/program.go` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=2 files changed, 23 insertions(+), 23 deletions(-). Changed `stageDisplayName("static")` from `"Static"` to `"Task"` (program.go:94) and updated comment (program.go:71). Updated all test data `Label: "Static Prompt"` → `Label: "Task"` and assertions `"STATIC"` → `"TASK"`, `"Static Prompt"` → `"Task"` across program_test.go (~20 occurrences). Depth-first rung: TUI2 display labels (smallest user-facing slice).
- **loops_remaining_forecast**: ~5-8 loops remaining for full Phase 0 rename. Remaining: internal `stageOrder` key rename ("static" → "task"), `isStaticPrompt()` → `isTask()`, grammar.go functions, tokens/overrides.go, skip token rename, help text updates, completion_test.go. Confidence: medium (scope well-defined but cross-file rename may surface hidden dependencies).
- **residual_constraints**:
  - The internal `stageOrder` key `"static"` remains unchanged — renaming it affects multiple packages (`barcli`, `bartui2`) and token resolution logic. Severity: medium (internal-only, no user confusion). Mitigation: defer to Loop 2+. Monitoring: `grep -r '"static"' internal/` to track remaining occurrences. Owning ADR: 0082 Phase 0.
- **next_work**:
  - Behaviour: Rename `stageOrder` key from `"static"` to `"task"` and update all internal references. Validation: `go test ./internal/bartui2/... ./internal/barcli/...`. Future-shaping: centralise the key name as a constant.
  - Behaviour: Rename `isStaticPrompt()` → `isTask()` in build.go. Validation: `go test ./internal/barcli/...`.

## Loop 2: Rename "Static Prompt" production labels in barcli and bartui

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — Production data labels in CLI completion, TUI token categories, and TUI1 fixture. Rename "Static Prompt" / "What (static prompt)" to "Task" / "What (task)" in barcli and bartui production code and golden files.
- **active_constraint**: `completion.go` hardcodes `"What (static prompt)"` as the CLI completion category, `tui_tokens.go` hardcodes `Label: "Static Prompt"` and `axisDisplayLabel("static")` returns `"Static Prompt"`, causing users to see confusing "static prompt" terminology in CLI completions and TUI token category views.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestCompleteStaticStage"`
  - `go test ./internal/bartui/ -run "TestPaletteCategoryStatusIncludesLabel"`
  - `go test ./internal/barcli/ -run "TestRunTUIFixtureOutputsSnapshot"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestCompleteStaticStage"` — `completion_test.go:245: expected category 'What (task)' for todo, got "What (static prompt)"` | inline
    helper:diff-snapshot=2 files changed (completion_test.go, bartui/program_test.go; production code unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... && go test ./internal/bartui/... && go test ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=5 files changed, 10 insertions(+), 10 deletions(-)
  - removal | 2026-02-07T (git restore completion.go tui_tokens.go) | exit 1 | `git restore internal/barcli/completion.go internal/barcli/tui_tokens.go && go test ./internal/barcli/ -run "TestCompleteStaticStage"` — `completion_test.go:245: expected category 'What (task)' for todo, got "What (static prompt)"` returns | inline
    helper:diff-snapshot=0 files changed (production code reverted)
- **rollback_plan**: `git restore internal/barcli/completion.go internal/barcli/tui_tokens.go cmd/bar/testdata/tui_smoke.json` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=5 files changed, 10 insertions(+), 10 deletions(-). Changed `buildStaticSuggestions` category from `"What (static prompt)"` to `"What (task)"` (completion.go:567). Changed `Label: "Static Prompt"` to `Label: "Task"` in `buildStaticCategory` (tui_tokens.go:197). Changed `axisDisplayLabel("static")` from `"Static Prompt"` to `"Task"` (tui_tokens.go:278). Updated golden fixture (tui_smoke.json) to reflect new label widths. Updated test assertions in completion_test.go and bartui/program_test.go. Depth-first rung: production label sources (barcli + bartui).
- **loops_remaining_forecast**: ~4-6 loops remaining for full Phase 0 rename. Remaining: `isStaticPrompt()` → `isTask()` in build.go, `StaticPromptDescription()` → `TaskDescription()` in grammar.go, `GetAllStaticPrompts()` → `GetAllTasks()`, `IsStaticPrompt`/`SetStatic` in tokens/overrides.go, `"STATIC PROMPTS"` help header in app.go, help text strings, `TokenCategoryKindStatic` constant, internal `stageOrder`/`axisOrder` key rename, grammar JSON exporter in Python. Confidence: medium (function renames are mechanical; grammar JSON requires Python changes per user guidance).
- **residual_constraints**:
  - The `prompt-grammar.json` uses `"static"` as the grammar key — renaming requires updating the Python exporter, not just Go code. Severity: medium (internal key, no user confusion since display labels are now updated). Mitigation: defer to a later loop that coordinates Go + Python changes. Monitoring: `grep -r '"static"' internal/barcli/embed/`. Owning ADR: 0082 Phase 0.
  - Help text in `app.go` still says "static prompts", "STATIC PROMPTS" header. Severity: medium (user-facing in `bar help tokens`). Mitigation: next loop. Monitoring: `grep -i "static prompt" internal/barcli/app.go`.
- **next_work**:
  - Behaviour: Rename `isStaticPrompt()` → `isTask()` and `StaticPromptDescription()` → `TaskDescription()` in build.go/grammar.go. Validation: `go test ./internal/barcli/...`. Future-shaping: align function names with "task" terminology.
  - Behaviour: Update `"STATIC PROMPTS"` header and help text strings in app.go. Validation: `go test ./internal/barcli/ -run "TestRenderTokensHelp|TestRunHelpTokens"`.
