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
