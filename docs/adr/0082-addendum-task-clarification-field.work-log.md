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

## Loop 3: Rename "STATIC PROMPTS" header and help text in app.go

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — User-facing help text in `bar help` and `bar help tokens` output. Rename "Static prompt" / "static prompts" / "STATIC PROMPTS" to "Task" / "tasks" / "TASKS" in app.go help strings.
- **active_constraint**: `app.go` hardcodes `writeHeader("STATIC PROMPTS")` in `renderTokensHelp` and 5 occurrences of "static prompt(s)" in `generalHelpText`, causing `bar help` and `bar help tokens static` to display confusing "static prompt" terminology instead of user-meaningful "task" terminology.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestRenderTokensHelpFiltersStaticSection|TestRunHelpTokensFiltersSections"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestRenderTokensHelpFiltersStaticSection|TestRunHelpTokensFiltersSections"` — `app_test.go:97: expected tasks heading in filtered output, got: STATIC PROMPTS` and `app_test.go:152: expected tasks heading in CLI output, got: STATIC PROMPTS` | inline
    helper:diff-snapshot=1 file changed (app_test.go only; app.go unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... && go test ./internal/bartui/... && go test ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=2 files changed, 13 insertions(+), 13 deletions(-)
  - removal | 2026-02-07T (git restore app.go) | exit 1 | `git restore internal/barcli/app.go && go test ./internal/barcli/ -run "TestRenderTokensHelpFiltersStaticSection"` — `app_test.go:97: expected tasks heading in filtered output, got: STATIC PROMPTS` returns | inline
    helper:diff-snapshot=0 files changed (app.go reverted)
- **rollback_plan**: `git restore internal/barcli/app.go` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=2 files changed, 13 insertions(+), 13 deletions(-). Changed `writeHeader("STATIC PROMPTS")` → `writeHeader("TASKS")` (app.go:960). Updated 5 help text strings: "1. Static prompt" → "1. Task", "show static prompts" → "show tasks", "Show only static prompts" → "Show only tasks", "List available static prompts" → "List available tasks", "List only static prompts" → "List only tasks". Updated test assertions from "STATIC PROMPTS" → "TASKS" and test messages from "static prompt" → "task" (app_test.go:34,40,96-97,151-152). Depth-first rung: help output text (user-facing CLI documentation).
- **loops_remaining_forecast**: ~3-5 loops remaining for full Phase 0 rename. Remaining: `isStaticPrompt()` → `isTask()` in build.go, `StaticPromptDescription()` → `TaskDescription()` and `GetAllStaticPrompts()` → `GetAllTasks()` in grammar.go, `IsStaticPrompt`/`SetStatic` in tokens/overrides.go, build error messages ("static prompt (task) is required"), `help_llm.go` references, `TokenCategoryKindStatic` constant, grammar JSON exporter in Python. Confidence: medium.
- **residual_constraints**:
  - Build error messages in `build.go` still say "static prompt (task) is required" and reference "static prompts". Severity: medium (user-facing error when task token is missing). Mitigation: next loop alongside function renames. Monitoring: `grep -i "static prompt" internal/barcli/build.go`.
  - `help_llm.go` contains multiple "static prompt" references in LLM-facing help text. Severity: low-medium (LLM-facing, not direct CLI user). Mitigation: defer to later loop. Monitoring: `grep -i "static prompt" internal/barcli/help_llm.go`.
  - The `prompt-grammar.json` uses `"static"` as the grammar key — renaming requires updating the Python exporter. Severity: medium (internal). Mitigation: defer. Owning ADR: 0082 Phase 0.
- **next_work**:
  - Behaviour: Rename `isStaticPrompt()` → `isTask()`, `StaticPromptDescription()` → `TaskDescription()`, `GetAllStaticPrompts()` → `GetAllTasks()` in build.go/grammar.go, and update build error messages. Validation: `go test ./internal/barcli/...`. Future-shaping: align function names with "task" terminology.
  - Behaviour: Rename `IsStaticPrompt`/`SetStatic` in tokens/overrides.go. Validation: `go test ./internal/barcli/...`.

## Loop 4: Rename functions and error messages from "static prompt" to "task"

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — Function names (`isStaticPrompt`, `StaticPromptDescription`, `GetAllStaticPrompts`, `IsStaticPrompt`) and error messages ("static prompt (task) is required", "multiple static prompt tokens provided", "Available static prompts") in build.go, grammar.go, tokens/overrides.go, and all call sites. Rename to "task" terminology.
- **active_constraint**: `build.go` error messages say "static prompt (task) is required" and "multiple static prompt tokens provided"; `grammar.go` exports `StaticPromptDescription()` and `GetAllStaticPrompts()`; `tokens/overrides.go` uses `IsStaticPrompt` struct field — all using confusing "static prompt" terminology instead of "task" in function names and user-facing error output.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestLoadEmbeddedGrammar|TestBuildUnrecognizedToken"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestLoadEmbeddedGrammar|TestBuildUnrecognizedToken/missing_task|TestBuildUnrecognizedToken/duplicate_task"` — `grammar_loader_test.go:19:39: grammar.TaskDescription undefined (type *Grammar has no field or method TaskDescription)` | inline
    helper:diff-snapshot=2 files changed (grammar_loader_test.go, build_error_test.go only; production code unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... && go test ./internal/bartui/... && go test ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=9 files changed, 51 insertions(+), 27 deletions(-)
  - removal | 2026-02-07T (git restore 7 production files) | exit 1 | `git restore internal/barcli/build.go internal/barcli/grammar.go internal/barcli/completion.go internal/barcli/app.go internal/barcli/help_llm.go internal/barcli/tui_tokens.go internal/barcli/tokens/overrides.go && go test ./internal/barcli/ -run "TestLoadEmbeddedGrammar"` — `grammar_loader_test.go:19:39: grammar.TaskDescription undefined` returns | inline
    helper:diff-snapshot=0 files changed (production code reverted)
- **rollback_plan**: `git restore internal/barcli/build.go internal/barcli/grammar.go internal/barcli/completion.go internal/barcli/app.go internal/barcli/help_llm.go internal/barcli/tui_tokens.go internal/barcli/tokens/overrides.go` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=9 files changed, 51 insertions(+), 27 deletions(-). Renamed `isStaticPrompt()` → `isTask()` (build.go: definition + 2 call sites), `StaticPromptDescription()` → `TaskDescription()` (grammar.go definition + 5 call sites in build.go, completion.go, app.go, help_llm.go, tui_tokens.go), `GetAllStaticPrompts()` → `GetAllTasks()` (grammar.go definition + 2 call sites in build.go), `IsStaticPrompt` → `IsTask` (tokens/overrides.go struct field + usage). Updated error messages: "multiple static prompt tokens provided" → "multiple task tokens provided", "static prompt (task) is required" → "task is required", "The static prompt defines" → "The task defines", "Available static prompts" → "Available tasks", "all static prompts with detailed descriptions" → "all tasks with detailed descriptions". Updated comments. Added 2 new test cases in build_error_test.go (missing task, duplicate task) with `unexpectInMessage: "static prompt"` assertions. Depth-first rung: function names + error messages (internal API + user-facing errors).
- **loops_remaining_forecast**: ~2-4 loops remaining for full Phase 0 rename. Remaining: `help_llm.go` "static prompt" references (~6 occurrences), `TokenCategoryKindStatic` constant, `SetStatic`/`SetStaticPromptUsed` in build.go, internal `stageOrder`/`axisOrder` key rename ("static" → "task"), skill.md files, grammar JSON exporter in Python. Confidence: medium.
- **residual_constraints**:
  - `help_llm.go` contains ~6 "static prompt" references in LLM-facing help text (e.g., "Static prompts are REQUIRED", "Static Prompts (required)" heading, "Missing static token" example). Severity: medium (LLM-facing, affects automated usage guidance). Mitigation: next loop. Monitoring: `grep -i "static prompt" internal/barcli/help_llm.go`.
  - Skill files (`bar-workflow/skill.md`, `bar-autopilot/skill.md`, `bar-suggest/skill.md`) contain "static prompt" references. Severity: low-medium (LLM-facing skill instructions). Mitigation: defer to later loop after help_llm.go. Monitoring: `grep -ri "static prompt" internal/barcli/skills/`.
  - The `prompt-grammar.json` uses `"static"` as the grammar key — renaming requires updating the Python exporter. Severity: medium (internal). Mitigation: defer. Owning ADR: 0082 Phase 0.
- **next_work**:
  - Behaviour: Update `help_llm.go` "static prompt" references to "task" terminology (~6 occurrences). Validation: `go test ./internal/barcli/ -run "TestRenderTokenCatalog|TestRenderLLMHelp"`. Future-shaping: consistent "task" language in LLM-facing documentation.
  - Behaviour: Rename `TokenCategoryKindStatic` constant and `SetStatic` in build.go. Validation: `go test ./internal/barcli/...`.

## Loop 5: Rename "static prompt" references to "task" in LLM help output

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — LLM-facing help text in `help_llm.go`. Rename "Static prompts" / "static prompt" to "Tasks" / "task" in all `renderLLMHelp` sub-functions that produce `bar help llm` output.
- **active_constraint**: `help_llm.go` hardcodes 5 "static prompt" references in output strings — axis capacity heading ("Static prompts: 1 token"), automated usage guidance ("Static prompts are REQUIRED"), error example ("static prompt (task) is required"), token catalog heading ("Static Prompts (required)"), and metadata count ("Static prompts: N") — causing LLM-facing documentation to use confusing "static prompt" terminology instead of "task".
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestLLMHelpUsesTaskTerminology"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestLLMHelpUsesTaskTerminology"` — `help_llm_test.go:21: line 35 contains 'static prompt': - **Static prompts**: 1 token (required)` (5 lines flagged + 2 missing assertions) | inline
    helper:diff-snapshot=1 file changed (help_llm_test.go only; help_llm.go unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... && go test ./internal/bartui/... && go test ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=1 file changed, 7 insertions(+), 7 deletions(-)
  - removal | 2026-02-07T (git restore help_llm.go) | exit 1 | `git restore internal/barcli/help_llm.go && go test ./internal/barcli/ -run "TestLLMHelpUsesTaskTerminology"` — `help_llm_test.go:21: line 35 contains 'static prompt'` returns | inline
    helper:diff-snapshot=0 files changed (help_llm.go reverted)
- **rollback_plan**: `git restore internal/barcli/help_llm.go` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=2 files changed (help_llm.go + help_llm_test.go), 7 insertions(+), 7 deletions(-) in help_llm.go. Changed "Static prompts" → "Tasks" in axis capacity (line 93), automated usage guidance (line 103), token catalog heading (line 441), metadata count (line 909). Changed "static prompt (task) is required" → "task is required" in error example (line 308). Updated 2 code comments from "Static prompts" → "Tasks". Created new test file `help_llm_test.go` with `TestLLMHelpUsesTaskTerminology` that asserts no "static prompt" appears in full LLM help output and checks for "Tasks" heading and "task is required" error text. Depth-first rung: LLM-facing help output text.
- **loops_remaining_forecast**: ~1-3 loops remaining for full Phase 0 rename. Remaining: `TokenCategoryKindStatic` constant in bartui/tokens.go, `SetStatic`/`SetStaticPromptUsed` in build.go, skill `.md` files (bar-workflow, bar-autopilot, bar-suggest), internal key rename ("static" → "task" in stageOrder/axisOrder) + Python grammar exporter. Confidence: medium.
- **residual_constraints**:
  - Skill files (`bar-workflow/skill.md`, `bar-autopilot/skill.md`, `bar-suggest/skill.md`) contain "static prompt" references. Severity: low-medium (LLM-facing skill instructions). Mitigation: next loop. Monitoring: `grep -ri "static prompt" internal/barcli/skills/`.
  - The `prompt-grammar.json` uses `"static"` as the grammar key — renaming requires updating the Python exporter. Severity: medium (internal). Mitigation: defer. Owning ADR: 0082 Phase 0.
  - `TokenCategoryKindStatic` constant in bartui/tokens.go is internal but misaligned with "task" terminology. Severity: low (no user impact). Mitigation: next loop. Monitoring: `grep -r "TokenCategoryKindStatic" internal/`.
- **next_work**:
  - Behaviour: Rename `TokenCategoryKindStatic` → `TokenCategoryKindTask` in bartui/tokens.go and all references. Validation: `go test ./internal/bartui/... ./internal/bartui2/... ./internal/barcli/...`. Future-shaping: consistent internal constant naming.
  - Behaviour: Update skill `.md` files to use "task" terminology. Validation: `grep -ri "static prompt" internal/barcli/skills/` returns 0 matches. Future-shaping: consistent LLM-facing documentation.

## Loop 6: Rename TokenCategoryKindStatic and SetStatic to task terminology

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — Internal constant `TokenCategoryKindStatic` in bartui/tokens.go, struct field `SetStatic` in tokens/overrides.go, and all references in barcli/build.go, barcli/tui_tokens.go, bartui/program_test.go.
- **active_constraint**: `bartui/tokens.go` exports `TokenCategoryKindStatic` constant and `tokens/overrides.go` exports `SetStatic` struct field, both using "static" naming that is misaligned with "task" terminology adopted in Loops 1-5. Referenced in 5 files across 3 packages.
- **validation_targets**:
  - `go test ./internal/bartui/ -run "TestPaletteCategoryStatusIncludesLabel"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/bartui/ -run "TestPaletteCategoryStatusIncludesLabel"` — `program_test.go:41:19: undefined: TokenCategoryKindTask` | inline
    helper:diff-snapshot=1 file changed (program_test.go only; production code unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=5 files changed, 7 insertions(+), 7 deletions(-)
  - removal | 2026-02-07T (git restore 4 production files) | exit 1 | `git restore internal/bartui/tokens.go internal/barcli/tui_tokens.go internal/barcli/tokens/overrides.go internal/barcli/build.go && go test ./internal/bartui/ -run "TestPaletteCategoryStatusIncludesLabel"` — `program_test.go:41:19: undefined: TokenCategoryKindTask` returns | inline
    helper:diff-snapshot=0 files changed (production code reverted)
- **rollback_plan**: `git restore internal/bartui/tokens.go internal/barcli/tui_tokens.go internal/barcli/tokens/overrides.go internal/barcli/build.go` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=5 files changed, 7 insertions(+), 7 deletions(-). Renamed `TokenCategoryKindStatic` → `TokenCategoryKindTask` (bartui/tokens.go:9, kept value `"static"` unchanged). Updated 2 references in bartui/program_test.go and 1 in barcli/tui_tokens.go. Renamed `SetStatic` → `SetTask` in tokens/overrides.go (struct field:17 + usage:46) and barcli/build.go (struct init:276). Depth-first rung: internal constant + struct field names.
- **loops_remaining_forecast**: ~1-2 loops remaining for full Phase 0 rename. Remaining: skill `.md` files (bar-workflow, bar-autopilot, bar-suggest) with "static prompt" references, internal key rename ("static" → "task" in stageOrder/axisOrder) + Python grammar exporter. Confidence: medium-high (skill files are text-only; internal key rename is the largest remaining risk).
- **residual_constraints**:
  - Skill files (`bar-workflow/skill.md`, `bar-autopilot/skill.md`, `bar-suggest/skill.md`) contain "static prompt" references. Severity: low-medium (LLM-facing skill instructions). Mitigation: next loop. Monitoring: `grep -ri "static prompt" internal/barcli/skills/`.
  - The `prompt-grammar.json` uses `"static"` as the grammar key — renaming requires updating the Python exporter. Severity: medium (internal). Mitigation: defer. Owning ADR: 0082 Phase 0.
  - Internal `stageOrder`/`axisOrder` key `"static"` remains unchanged — the `TokenCategoryKindTask` value is still `"static"` to maintain internal consistency. Severity: medium (internal-only, no user confusion since display labels all say "task"). Mitigation: defer to coordinated key rename loop. Monitoring: `grep -r '"static"' internal/bartui/tokens.go internal/bartui2/program.go`.
- **next_work**:
  - Behaviour: Update skill `.md` files to replace "static prompt" with "task" terminology. Validation: `grep -ri "static prompt" internal/barcli/skills/` returns 0 matches. Future-shaping: consistent LLM-facing documentation.
  - Behaviour: Internal key rename ("static" → "task" in stageOrder/axisOrder + Python grammar exporter). Validation: `go test ./...`. Future-shaping: complete Phase 0 alignment.

## Loop 7: Rename "static prompt" to "task" in embedded skill files

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — Embedded skill `.md` files (bar-workflow, bar-autopilot, bar-suggest, bar-manual). Replace "static prompt" / "Static Prompts" with "task" / "Tasks" in LLM-facing skill instructions.
- **active_constraint**: Four embedded skill files contain "static prompt" references in step instructions and code comments, causing LLM agents to see outdated terminology that conflicts with the "task" terminology adopted in Loops 1-6. The embedded skills are compiled into the Go binary via `//go:embed skills`, so text changes are testable through `embeddedSkills` filesystem.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestEmbeddedSkillsUseTaskTerminology"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestEmbeddedSkillsUseTaskTerminology"` — `help_llm_test.go:48: skills/bar-autopilot/skill.md:87 contains 'static prompt'` (4 files flagged) | inline
    helper:diff-snapshot=1 file changed (help_llm_test.go only; skill files unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=5 files changed, 27 insertions(+), 4 deletions(-)
  - removal | 2026-02-07T (git restore skills/) | exit 1 | `git restore internal/barcli/skills/ && go test ./internal/barcli/ -run "TestEmbeddedSkillsUseTaskTerminology"` — `help_llm_test.go:48: skills/bar-autopilot/skill.md:87 contains 'static prompt'` returns | inline
    helper:diff-snapshot=0 files changed (skill files reverted)
- **rollback_plan**: `git restore internal/barcli/skills/` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=5 files changed, 27 insertions(+), 4 deletions(-). Updated `bar-workflow/skill.md:75` ("Select static prompts for each step" → "Select task for each step", all "static prompt" → "task", "Static Prompts" → "Tasks"). Updated `bar-autopilot/skill.md:87` ("Select static prompt" → "Select task", all references). Updated `bar-suggest/skill.md:91` ("Select static prompts for options" → "Select task for options", all references). Updated `bar-manual/skill.md:78` ("Static prompts only" → "Tasks only"). Created `TestEmbeddedSkillsUseTaskTerminology` in help_llm_test.go that walks all embedded `.md` files and asserts no "static prompt" appears. Depth-first rung: skill file text (LLM-facing documentation).
- **loops_remaining_forecast**: ~1 loop remaining for Phase 0 Go-side rename. Remaining: internal key rename ("static" → "task" in stageOrder/axisOrder, `TokenCategoryKindTask` value, grammar JSON key) requires coordinated Go + Python changes. Confidence: medium (cross-language coordination adds risk).
- **residual_constraints**:
  - The `prompt-grammar.json` uses `"static"` as the grammar key — renaming requires updating the Python exporter. Severity: medium (internal). Mitigation: defer to coordinated loop. Owning ADR: 0082 Phase 0.
  - Internal `stageOrder`/`axisOrder` key `"static"` and `TokenCategoryKindTask` value `"static"` remain unchanged. Severity: medium (internal-only, no user confusion). Mitigation: defer to final Phase 0 loop. Monitoring: `grep -r '"static"' internal/bartui/tokens.go internal/bartui2/program.go internal/barcli/embed/`.
- **next_work**:
  - Behaviour: Internal key rename ("static" → "task" in stageOrder/axisOrder, `TokenCategoryKindTask` value, all `"static"` key references in barcli/bartui/bartui2 + Python grammar exporter). Validation: `go test ./...`. Future-shaping: complete Phase 0 alignment.

## Loop 8: Rename internal key "static" to "task" across all Go packages

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — Internal key `"static"` used as classification/ordering/display key across barcli, bartui, bartui2 packages. Rename to `"task"` while preserving CLI argument names (`bar help tokens static`, `static=make`) and JSON struct tags (`json:"static"`).
- **active_constraint**: Internal key `"static"` appears in ~15 production code sites (stageOrder, axisOrder, shuffleStageOrder, TokenCategoryKindTask value, TokenCategory Key, addRecognized calls, completion section keys, filter keys, stage display case statements) across 10 files in 3 packages. The key drives user-visible error output ("static: make" in recognized tokens), TUI completion prefixes ("static=todo"), and stage ordering. All sites use the confusing "static" name instead of meaningful "task".
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestBuildUnrecognizedToken/error_shows_recognized|TestRenderTokensHelpFiltersStaticSection"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestBuildUnrecognizedToken/error_shows_recognized|TestRenderTokensHelpFiltersStaticSection"` — `build_error_test.go: expected stderr to contain "task: make" Got: static: make` | inline
    helper:diff-snapshot=2 files changed (build_error_test.go, app_test.go; production code unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=14 files changed, 61 insertions(+), 61 deletions(-)
  - removal | 2026-02-07T (git restore 9 production files) | exit 1 | `git restore internal/bartui/tokens.go internal/bartui/program.go internal/bartui2/program.go internal/barcli/tui_tokens.go internal/barcli/build.go internal/barcli/shuffle.go internal/barcli/completion.go internal/barcli/app.go internal/barcli/tokens/overrides.go && go test ./internal/barcli/ -run "TestBuildUnrecognizedToken/error_shows_recognized"` — `expected stderr to contain "task: make" Got: static: make` returns | inline
    helper:diff-snapshot=0 files changed (production code reverted)
- **rollback_plan**: `git restore internal/bartui/tokens.go internal/bartui/program.go internal/bartui2/program.go internal/barcli/tui_tokens.go internal/barcli/build.go internal/barcli/shuffle.go internal/barcli/completion.go internal/barcli/app.go internal/barcli/tokens/overrides.go` then replay red failure.
- **delta_summary**: helper:diff-snapshot=14 files changed, 61 insertions(+), 61 deletions(-). Changed `TokenCategoryKindTask` value from `"static"` to `"task"` (bartui/tokens.go). Changed `stageOrder` key (bartui2/program.go), `stageDisplayName` case (bartui2/program.go), stage priority key (bartui/program.go), `shuffleStageOrder` + `mustInclude` + `getStageTokens` case (shuffle.go), `TokenCategory.Key` (tui_tokens.go), `axisDisplayLabel` case (tui_tokens.go), `addRecognized` calls (build.go + overrides.go), `axisOrder` (build.go), completion `sectionOrder`/`markRecognizedStage`/`appendSection` keys (completion.go), CLI filter mapping `"static"` → `"task"` (app.go), `shouldShow("task")` (app.go). Updated ~20 test assertions across bartui/program_test.go, bartui2/program_test.go, build_error_test.go, completion_test.go, app_test.go. JSON struct tags (`json:"static"` on Grammar.Static and BuildResult.Static) and CLI argument names (`bar help tokens static`, `static=make`) preserved unchanged. Depth-first rung: internal key rename (final Go-side Phase 0 rung).
- **loops_remaining_forecast**: 0 Go-side loops remaining for Phase 0. The `prompt-grammar.json` key `"static"` and Python exporter remain as the only outstanding item — this requires Python changes outside the Go codebase. All Go code now uses `"task"` internally while correctly reading from the JSON `"static"` section via struct tags. Confidence: high.
- **residual_constraints**:
  - The `prompt-grammar.json` uses `"static"` as the grammar section key and Go struct tags read from it via `json:"static"`. Renaming the JSON key requires updating the Python exporter + Go struct tags simultaneously. Severity: low (no user confusion, purely internal JSON field name). Mitigation: coordinate with Python exporter change. Owning ADR: 0082 Phase 0.
  - CLI arguments `bar help tokens static` and `static=make` override syntax still use "static" as user input. Severity: low (breaking CLI change deferred). Mitigation: future phase if desired. Monitoring: `grep -r 'case "static":' internal/barcli/app.go internal/barcli/tokens/overrides.go`.
- **next_work**:
  - Behaviour: Update Python grammar exporter to rename JSON section from `"static"` to `"task"`, then update Go struct tags `json:"static"` → `json:"task"`. Validation: `go test ./...` + Python exporter tests. Future-shaping: complete alignment of data format with internal terminology.

## Loop 9: Rename JSON grammar keys from "static" to "task" in Python exporter and Go struct tags

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — JSON grammar schema keys (`"static_prompts"`, `"static_prompt"`, `"static"` in slugs/overrides) and corresponding Go struct tags. Rename to `"tasks"`, `"task"` across Python exporter, all three JSON grammar files, and Go deserialization struct tags.
- **active_constraint**: Python exporter (`lib/promptGrammar.py`) generates JSON grammar with `"static_prompts"` as top-level section key, `"static_prompt"` in hierarchy defaults, and `"static"` in slug/override subsections. Go struct tags (`json:"static_prompts"`, `json:"static"`, `json:"static_prompt"`) in grammar.go read these keys. The internal Go code already uses "task" terminology (Loops 1-8) but the data interchange format still uses "static", creating a terminology split between internal code and serialised data.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestEmbeddedGrammarUsesTaskKeys"`
  - `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...`
  - `.venv/bin/python -m pytest _tests/test_prompt_grammar_export.py`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestEmbeddedGrammarUsesTaskKeys"` — `grammar_loader_test.go:35: expected top-level 'tasks' key in grammar JSON (found 'static_prompts'?)` | inline
    helper:diff-snapshot=1 file changed (grammar_loader_test.go only; production code unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...` — all tests PASS + `.venv/bin/python -m pytest _tests/test_prompt_grammar_export.py` — 2 passed | inline
    helper:diff-snapshot=9 files changed, 76 insertions(+), 35 deletions(-)
  - removal | 2026-02-07T (git restore embed/prompt-grammar.json) | exit 1 | `git restore internal/barcli/embed/prompt-grammar.json && go test ./internal/barcli/ -run "TestEmbeddedGrammarUsesTaskKeys"` — `grammar_loader_test.go:35: expected top-level 'tasks' key in grammar JSON (found 'static_prompts'?)` returns | inline
    helper:diff-snapshot=0 files changed (embedded grammar reverted)
- **rollback_plan**: `git restore lib/promptGrammar.py internal/barcli/grammar.go internal/barcli/build.go internal/barcli/tui_tokens.go _tests/test_prompt_grammar_export.py && make bar-grammar-update` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=9 files changed, 76 insertions(+), 35 deletions(-). Python exporter: renamed `"static_prompts"` → `"tasks"` (top-level section key), `"static_prompt"` → `"task"` (hierarchy defaults), `"static"` → `"task"` (slug section, override section keys), `category="override-static"` → `category="override-task"`. Go struct tags: `json:"static_prompts"` → `json:"tasks"` (rawGrammar.Static), `json:"static"` → `json:"task"` (rawSlugSection.Static), `json:"static_prompt"` → `json:"task"` (rawHierarchy.Defaults), struct field `StaticPrompt` → `Task` (DefaultsSection). Updated all three grammar JSON files via `make bar-grammar-update`. Updated Python test assertion `"static_prompts"` → `"tasks"`. Added `TestEmbeddedGrammarUsesTaskKeys` specifying validation (checks embedded JSON has `"tasks"` top-level key, `"task"` in hierarchy defaults, and `"task"` in slugs). Depth-first rung: JSON schema key rename (final Phase 0 data format rung).
- **loops_remaining_forecast**: 0 loops remaining for Phase 0 terminology cleanup. All Go code, Python exporter, JSON schema, tests, help text, skill files, and display labels now use "task" terminology. CLI argument syntax (`static=make`, `bar help tokens static`) remains unchanged as user-facing compatibility surface. Phase 0 is complete. Confidence: high.
- **residual_constraints**:
  - CLI arguments `bar help tokens static` and `static=make` override syntax still use "static" as user input. Severity: low (breaking CLI change, deferred intentionally). Mitigation: future phase if desired; display labels already show "task". Monitoring: `grep -r 'case "static":' internal/barcli/app.go internal/barcli/tokens/overrides.go`.
  - JSON override values still contain `"static=check": "static-check"` patterns — these are slug values for user-facing CLI syntax, not structural keys. Severity: low (cosmetic, consistent with CLI argument preservation). Mitigation: rename only if CLI syntax changes. Monitoring: `grep "static=" build/prompt-grammar.json`.
- **next_work**:
  - Phase 0 complete. Next: ADR 0082 Phase 1 (CLI `bar build` — Subject and Addendum flags). Behaviour: Add `--subject TEXT` flag with mutual exclusivity against stdin. Validation: `go test ./internal/barcli/...` with new test cases. Future-shaping: separate task clarification from subject content.

## Loop 10: Rename CLI argument syntax from `static=` to `task=`

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 0 (Terminology Cleanup) — CLI-facing argument syntax. Rename override key `static=make` → `task=make`, filter command `bar help tokens static` → `bar help tokens task`, completion prefix `static=` → `task=`, EBNF grammar `"static="` → `"task="`, JSON override slugs `"static=check": "static-check"` → `"task=check": "task-check"`, and all user-visible references across Go, Python, JSON, skill files, and documentation.
- **active_constraint**: CLI override syntax `static=make` and filter command `bar help tokens static` use "static" as user-facing argument key — the last user-visible vestige of the old terminology. Override handler (`tokens/overrides.go:42`) has `case "static":`, completion generates `"static="` prefix, EBNF grammar shows `"static="`, JSON slugs use `"static=check"` patterns, and 21 files across Go/Python/JSON/docs contain the old syntax.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestBuildUnrecognizedToken/static=_override_key_rejected|TestBuildUnrecognizedToken/error_shows_recognized_override"`
  - `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...`
  - `.venv/bin/python -m pytest _tests/test_prompt_grammar_export.py`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestBuildUnrecognizedToken/static=_override_key_rejected|TestBuildUnrecognizedToken/error_shows_recognized_override"` — `static=_override_key_rejected: expected non-zero exit, got 0` (static=make still accepted) and `error_shows_recognized_override: expected stderr to contain "task: make" Got: unknown override key task` (task=make rejected) | inline
    helper:diff-snapshot=1 file changed (build_error_test.go only; production code unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...` — all tests PASS + `.venv/bin/python -m pytest _tests/test_prompt_grammar_export.py` — 2 passed | inline
    helper:diff-snapshot=21 files changed, 106 insertions(+), 98 deletions(-)
  - removal | 2026-02-07T (git restore overrides.go) | exit 1 | `git restore internal/barcli/tokens/overrides.go && go test ./internal/barcli/ -run "TestBuildUnrecognizedToken/static=_override_key_rejected"` — `expected non-zero exit, got 0` (static=make accepted again) | inline
    helper:diff-snapshot=0 files changed (overrides.go reverted)
- **rollback_plan**: `git restore internal/barcli/tokens/overrides.go internal/barcli/completion.go internal/barcli/help_llm.go internal/barcli/app.go internal/barcli/build.go internal/barcli/grammar.go internal/bartui/program.go lib/promptGrammar.py lib/modelResponseCanvas.py GPT/gpt.py && make bar-grammar-update` then replay red failure.
- **delta_summary**: helper:diff-snapshot=21 files changed, 106 insertions(+), 98 deletions(-). Override handler `case "static":` → `case "task":` (overrides.go:42). Completion prefix `"static="` → `"task="` (completion.go:725). EBNF grammar `"static="` → `"task="` (help_llm.go:169). Help text `bar help tokens static` → `bar help tokens task` (app.go:171). Filter key `case "static":` → `case "task":` (app.go:915). Error message `bar help tokens static` → `bar help tokens task` (build.go:721). BuildResult JSON tag `json:"static"` → `json:"task"` (build.go:36). Slug format `"static=%s"` → `"task=%s"` (grammar.go:451,455). TUI toast `static=%s` → `task=%s` (bartui/program.go:4887). Comment `"static=inf"` → `"task=inf"` (bartui/program.go:1582). Python exporter `f"static={label}"` → `f"task={label}"` (promptGrammar.py:330). Python debug logs `static=` → `task=` (gpt.py:2486,2497,2630; modelResponseCanvas.py:1569). All 3 JSON grammar files regenerated with `"task=check": "task-check"` override slugs. Skill files and docs updated. Test assertions updated. Added `static=_override_key_rejected_in_favor_of_task=` specifying test. Depth-first rung: user-facing CLI argument syntax (breaking change completing Phase 0).
- **loops_remaining_forecast**: 0 loops remaining for Phase 0. All terminology — internal code, JSON schema, CLI arguments, help text, completion, EBNF grammar, skill files, docs — now uses "task" consistently. Phase 0 is fully complete. Confidence: high.
- **residual_constraints**:
  - ADR documentation files (0065, 0077, 0101, etc.) contain historical `static=` references in examples. Severity: low (historical records, not user-facing). Mitigation: leave as historical context. Monitoring: none required.
  - Stored preset files on user machines may contain `"axes":{"static":"make"}` — the BuildResult JSON tag changed to `json:"task"`, so presets saved with old format will not populate the task field on load. Severity: medium (user presets break silently). Mitigation: consider migration or backward-compatible reading in a follow-up. Monitoring: user reports.
- **next_work**:
  - Phase 0 complete. Next: ADR 0082 Phase 1 (CLI `bar build` — Subject and Addendum flags). Behaviour: Add `--subject TEXT` flag with mutual exclusivity against stdin. Validation: `go test ./internal/barcli/...` with new test cases. Future-shaping: separate task clarification from subject content.

## Loop 11: Add --subject flag with mutual exclusivity (Phase 1a)

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 1a (CLI Implementation) — Add `--subject TEXT` flag as alternative to stdin/`--prompt` for providing subject content inline. Implement mutual exclusivity: `--subject` vs stdin, `--subject` vs `--input`, `--subject` vs `--prompt`.
- **active_constraint**: No way to provide subject content inline via a named flag — users must use `--prompt` (which conflates task clarification with content) or stdin (which requires piping). The CLI lacks a clear, named mechanism for providing subject material that is distinct from task clarification.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestRunBuildWithSubjectFlag|TestRunBuildSubjectAndStdinMutualExclusivity|TestRunBuildSubjectAndInputMutualExclusivity"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestRunBuildWithSubjectFlag"` — `app_build_cli_test.go:200: expected exit 0, got 1 with stderr: error: unknown flag --subject` | inline
    helper:diff-snapshot=1 file changed (app_build_cli_test.go only; production code unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=3 files changed, 72 insertions(+)
  - removal | 2026-02-07T (git restore config.go app.go) | exit 1 | `git restore internal/barcli/cli/config.go internal/barcli/app.go && go test ./internal/barcli/ -run "TestRunBuildWithSubjectFlag"` — `error: unknown flag --subject` returns | inline
    helper:diff-snapshot=0 files changed (production code reverted)
- **rollback_plan**: `git restore internal/barcli/cli/config.go internal/barcli/app.go` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=3 files changed, 72 insertions(+). Added `Subject string` field to `cli.Config` struct (config.go:15). Added `--subject` / `--subject=` flag parsing (config.go:62-68). Added mutual exclusivity validation: `--subject` + `--input` (config.go:285), `--subject` + `--prompt` (config.go:288). Updated `readPrompt()` to check `opts.Subject` first with stdin mutual exclusivity check (app.go:1191-1196). Added 3 specifying tests: `TestRunBuildWithSubjectFlag` (flag provides subject), `TestRunBuildSubjectAndStdinMutualExclusivity` (error when both), `TestRunBuildSubjectAndInputMutualExclusivity` (error when both). Depth-first rung: `--subject` flag (Phase 1a, first new flag).
- **loops_remaining_forecast**: ~3-4 loops for Phase 1. Remaining: 1b (`--addendum` flag + ADDENDUM section rendering), 1c (remove `--prompt` + migration error), 1d (update help text). Confidence: high (each sub-phase is well-scoped).
- **residual_constraints**:
  - `--prompt` flag still works and conflates subject with task clarification. Severity: medium (user confusion, ADR goal unmet). Mitigation: Phase 1c removes it with migration guidance. Monitoring: `grep "opts.Prompt" internal/barcli/app.go`.
  - No `--addendum` flag yet — users cannot provide task clarification separate from subject. Severity: medium (ADR core feature missing). Mitigation: Phase 1b. Monitoring: N/A.
  - Stored preset files may contain `"axes":{"static":"make"}` (from Loop 10). Severity: medium. Mitigation: deferred. Owning ADR: 0082 Phase 0.
- **next_work**:
  - Behaviour: Add `--addendum TEXT` flag, `Addendum` field on `BuildResult`, and `=== ADDENDUM (CLARIFICATION) ===` section in `RenderPlainText()`. Validation: `go test ./internal/barcli/ -run "TestRunBuildWithAddendum|TestBuildAddendumRendering"`. Future-shaping: separate task clarification section in rendered output.

## Loop 12: Add --addendum flag with ADDENDUM section rendering (Phase 1b)

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 1b (CLI Implementation) — Add `--addendum TEXT` flag for task clarification, `Addendum` field on `BuildResult`, `=== ADDENDUM (CLARIFICATION) ===` section in rendered output between TASK and CONSTRAINTS, ADDENDUM description in reference key, and completion support.
- **active_constraint**: No mechanism to provide task clarification separate from subject content — users who want to say "focus on security" must use `--prompt` which conflates instruction with data, or axis tokens which cannot express all clarifications.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestRunBuildWithAddendumFlag|TestRunBuildAddendumOmittedWhenEmpty|TestRunBuildAddendumInJSON"`
- **evidence**:
  - red | 2026-02-07T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestRunBuildWithAddendumFlag"` — `app_build_cli_test.go:251: expected exit 0, got 1 with stderr: error: unknown flag --addendum` | inline
    helper:diff-snapshot=1 file changed (app_build_cli_test.go only; production code unchanged)
  - green | 2026-02-07T (post-implementation) | exit 0 | `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=7 files changed, 75 insertions(+), 5 deletions(-)
  - removal | 2026-02-07T (git restore render.go build.go app.go config.go) | exit 1 | `git restore internal/barcli/render.go internal/barcli/build.go internal/barcli/app.go internal/barcli/cli/config.go && go test ./internal/barcli/ -run "TestRunBuildWithAddendumFlag"` — `error: unknown flag --addendum` returns | inline
    helper:diff-snapshot=0 files changed (production code reverted)
- **rollback_plan**: `git restore internal/barcli/render.go internal/barcli/build.go internal/barcli/app.go internal/barcli/cli/config.go internal/barcli/completion.go cmd/bar/testdata/tui_smoke.json` then replay red failure.
- **delta_summary**: helper:diff-snapshot=7 files changed, 75 insertions(+), 5 deletions(-). Added `Addendum string` to `cli.Config` (config.go:16). Added `--addendum` / `--addendum=` parsing (config.go:70-76). Added `Addendum string` to `BuildResult` with `json:"addendum,omitempty"` (build.go:25). Wired `options.Addendum` → `result.Addendum` (app.go:269). Added `sectionAddendum` constant and conditional rendering in `RenderPlainText()` after TASK, before CONSTRAINTS (render.go:13,63-65). Added ADDENDUM paragraph to `referenceKeyText` (render.go:26-29). Added `--subject` and `--addendum` to `buildFlags` and `flagExpectingValue` in completion.go, plus `--subject=`/`--addendum=` prefix detection. Updated TUI fixture `expected_preview` with new reference key text. Added 3 specifying tests: `TestRunBuildWithAddendumFlag`, `TestRunBuildAddendumOmittedWhenEmpty`, `TestRunBuildAddendumInJSON`. Depth-first rung: `--addendum` flag + rendered output (Phase 1b).
- **loops_remaining_forecast**: ~2 loops for Phase 1. Remaining: 1c (remove `--prompt` flag with migration error), 1d (update help text with `--subject`/`--addendum` examples). Confidence: high.
- **residual_constraints**:
  - `--prompt` flag still works — conflates subject with task clarification. Severity: medium (ADR goal to remove it). Mitigation: Phase 1c. Monitoring: `grep "opts.Prompt" internal/barcli/app.go`.
  - Help text still shows `--prompt` in examples. Severity: medium (user-facing). Mitigation: Phase 1d. Monitoring: `grep "\-\-prompt" internal/barcli/app.go`.
  - Stored preset files may contain old `"axes":{"static":"make"}` format (Loop 10). Severity: medium. Mitigation: deferred. Owning ADR: 0082 Phase 0.
- **next_work**:
  - Behaviour: Remove `--prompt` flag — using it emits error with migration guidance to `--subject`/`--addendum`. Update existing tests that use `--prompt` to use `--subject`. Validation: `go test ./internal/barcli/ -run "TestRunBuildPromptFlagRemoved"`. Future-shaping: clean break from conflated flag.

## Loop 13: Remove --prompt flag with migration guidance (Phase 1c)

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 1c (CLI Implementation) — Remove `--prompt` flag entirely. Using `--prompt` now returns a parse-time error with migration guidance to `--subject` / `--addendum`. All callers migrated from `--prompt` to `--subject`.
- **active_constraint**: `--prompt` flag still accepted — conflates subject content with task clarification; ADR 0082 goal requires clean separation via `--subject`/`--addendum`.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestRunBuildPromptFlagRemoved"`
  - `go test ./internal/barcli/...`
- **evidence**:
  - red | 2026-02-09T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestRunBuildPromptFlagRemoved"` — `app_build_cli_test.go:298: expected non-zero exit when --prompt is used` (exit 0 returned) | inline
    helper:diff-snapshot=1 file changed (app_build_cli_test.go only; production code unchanged)
  - green | 2026-02-09T (post-implementation) | exit 0 | `go test ./internal/barcli/...` — all tests PASS | inline
    helper:diff-snapshot=9 files changed, ~30 insertions(+), ~25 deletions(-)
  - removal | 2026-02-09T (git restore config.go) | exit 1 | `git restore internal/barcli/cli/config.go && go test ./internal/barcli/ -run "TestRunBuildPromptFlagRemoved"` — test fails (--prompt exits 0) returns | inline
    helper:diff-snapshot=0 files changed (config.go reverted)
- **rollback_plan**: `git restore internal/barcli/cli/config.go internal/barcli/app.go internal/barcli/tui.go internal/barcli/tui2.go internal/barcli/completion.go` then replay red failure.
- **delta_summary**: helper:diff-snapshot=9 files changed. Removed `Prompt string` from `cli.Config` struct (config.go). Replaced `--prompt` / `--prompt=` parsing cases with parse-time error: `"--prompt flag has been removed.\n\nUse --subject to provide content for the LLM to act on,\nor --addendum to add clarification to the task."` (config.go). Removed `--prompt`/`--input` and `--subject`/`--prompt` mutual exclusivity checks (now superseded by removal). Removed `opts.Prompt` branch from `readPrompt()` (app.go). Removed `opts.Prompt` from TUI input guards in `tui.go` and `tui2.go`, updating error messages. Removed `--prompt` from `buildFlags`, `flagExpectingValue`, and prefix detection in `completion.go`. Migrated all tests using `--prompt` to use `--subject`: `app_parse_test.go`, `app_build_cli_test.go`, `app_test.go`, `app_preset_cli_test.go`. Updated `TestParseArgsErrors` to test `--prompt removed` error instead of missing-value error. Added specifying test `TestRunBuildPromptFlagRemoved`. Depth-first rung: flag removal + migration error (Phase 1c).
- **loops_remaining_forecast**: ~1-2 loops for Phase 1. Remaining: 1d (update help text in app.go, help_llm.go, build.go to replace `--prompt` examples with `--subject`/`--addendum`). Then Phase 2 (TUI2), Phase 3 (Python reference key), Phase 4 (skills), Phase 5 (Talon alignment). Confidence: high.
- **residual_constraints**:
  - Help text in `app.go`, `help_llm.go`, and `build.go` still reference `--prompt` in examples. Severity: medium (user-facing in `bar help`). Mitigation: Phase 1d. Monitoring: `grep "\-\-prompt" internal/barcli/app.go internal/barcli/help_llm.go internal/barcli/build.go`.
  - Stored preset files may contain old `"axes":{"static":"make"}` format (Loop 10). Severity: medium. Mitigation: deferred. Owning ADR: 0082 Phase 0.
- **next_work**:
  - Behaviour: Update all help text and examples in `app.go` (usage strings, examples), `help_llm.go` (all `--prompt` examples), `build.go` (error message example). Replace `--prompt "..."` with `--subject "..."`. Validation: `go test ./internal/barcli/ -run "TestRenderTokensHelp|TestRunHelpTokens|TestHelpLLM"`. Future-shaping: help text teaches the new `--subject`/`--addendum` split.

## Loop 14: Update help text to use --subject and --addendum (Phase 1d)

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 1d (CLI Implementation) — Update all help text, usage strings, and examples in `app.go`, `help_llm.go`, and `build.go` to replace `--prompt` with `--subject`/`--addendum`.
- **active_constraint**: Help text in `app.go`, `help_llm.go`, and `build.go` still references the removed `--prompt` flag in usage lines, command descriptions, and examples — causing `bar help` to document a flag that no longer exists.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestGeneralHelpUsesSubjectAndAddendumFlags"`
  - `go test ./internal/barcli/...`
- **evidence**:
  - red | 2026-02-09T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestGeneralHelpUsesSubjectAndAddendumFlags"` — `app_test.go:225: expected help text not to mention removed --prompt flag` | inline
    helper:diff-snapshot=1 file changed (app_test.go only; production code unchanged)
  - green | 2026-02-09T (post-implementation) | exit 0 | `go test ./internal/barcli/...` — all tests PASS | inline
    helper:diff-snapshot=4 files changed, ~15 insertions(+), ~14 deletions(-)
  - removal | 2026-02-09T (git restore app.go) | exit 1 | `git restore internal/barcli/app.go && go test ./internal/barcli/ -run "TestGeneralHelpUsesSubjectAndAddendumFlags"` — `expected help text not to mention removed --prompt flag` returns | inline
    helper:diff-snapshot=0 files changed (app.go reverted)
- **rollback_plan**: `git restore internal/barcli/app.go internal/barcli/help_llm.go internal/barcli/build.go` then replay red failure.
- **delta_summary**: helper:diff-snapshot=4 files changed. In `app.go`: updated `generalHelpText` USAGE lines (build/shuffle), build command description, preset use description, and examples (removed `--prompt`, added `--subject`/`--addendum`). In `help_llm.go`: replaced all `--prompt "..."` occurrences with `--subject "..."` (~20 occurrences) across `renderQuickStart`, `renderGrammarArchitecture`, and example structs. In `build.go`: updated error message examples `--prompt "..."` → `--subject "..."` and `<static-token>` → `<task-token>`. Added specifying test `TestGeneralHelpUsesSubjectAndAddendumFlags` in `app_test.go`. Depth-first rung: help text (Phase 1d).
- **loops_remaining_forecast**: Phase 1 complete. Remaining phases: 2 (TUI2 separate subject/addendum fields), 3 (Python `PROMPT_REFERENCE_KEY`), 4 (skills integration), 5 (Talon alignment). Confidence: high for current scope; Phase 2 is moderate complexity.
- **residual_constraints**:
  - TUI2 has no separate subject/addendum input fields — users cannot provide `--addendum` via TUI2 interactively. Severity: medium (feature incomplete). Mitigation: Phase 2. Monitoring: TUI2 model state has no `Addendum` field.
  - `help_llm.go` still references `[static]` in grammar architecture description (line 82). Severity: low (LLM-facing help, internal terminology). Mitigation: deferred to Phase 0 cleanup ADR. Monitoring: `grep -i "static" internal/barcli/help_llm.go`.
  - Stored preset files may contain old `"axes":{"static":"make"}` format (Loop 10). Severity: medium. Mitigation: deferred. Owning ADR: 0082 Phase 0.
- **next_work**:
  - Behaviour: Phase 2 — Add separate subject/addendum input fields to TUI2. Validation: `go test ./internal/bartui2/... -run "TestTUI2SubjectAndAddendumFields"`. Future-shaping: TUI2 surfaces the subject/addendum distinction interactively.

## Loop 15: TUI2 addendum modal and preview wiring (Phase 2a)

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 2 (TUI2 Interface) — Add `addendum` field to TUI2 model, Ctrl+A modal for addendum entry, `--addendum` in rebuilt command line, addendum passed through preview callback. Update `Options.Preview` signature to include addendum.
- **active_constraint**: TUI2 model has no `addendum` field and `Options.Preview` signature is `func(subject, tokens)` — users cannot enter addendum in TUI2 and the preview does not show ADDENDUM section even when addendum is set.
- **validation_targets**:
  - `go test ./internal/bartui2/... -run "TestAddendumPassedToPreviewAndCommand"`
  - `go test ./internal/bartui2/... ./internal/barcli/...`
- **evidence**:
  - red | 2026-02-09T (pre-implementation) | exit 1 | `go test ./internal/bartui2/... -run "TestAddendumPassedToPreviewAndCommand"` — `cannot use preview (func(subject, addendum, tokens)) as func(subject, tokens)` and `m.addendum undefined` | inline
    helper:diff-snapshot=1 file changed (program_test.go only; production code unchanged)
  - green | 2026-02-09T (post-implementation) | exit 0 | `go test ./internal/bartui2/... ./internal/barcli/...` — all tests PASS | inline
    helper:diff-snapshot=4 files changed, ~80 insertions(+), ~10 deletions(-)
  - removal | 2026-02-09T (git restore program.go tui2.go) | exit 1 | `git restore internal/bartui2/program.go internal/barcli/tui2.go && go test ./internal/bartui2/... -run "TestAddendumPassedToPreviewAndCommand"` — `m.addendum undefined` returns | inline
    helper:diff-snapshot=0 files changed (production code reverted)
- **rollback_plan**: `git restore internal/bartui2/program.go internal/barcli/tui2.go` then replay red failure.
- **delta_summary**: helper:diff-snapshot=4 files changed. In `program.go`: changed `Options.Preview` signature from `func(subject, tokens)` to `func(subject, addendum, tokens)`. Added `addendum string`, `addendumInput textarea.Model`, `showAddendumModal bool` fields to model. Initialized `addendumInput` in `newModel()`. Added `case "ctrl+a"` hotkey to open addendum modal. Added `updateAddendumModal()` (mirrors subject modal, saves on Ctrl+S). Added modal routing in `Update()` and view routing in `View()`. Added `renderAddendumModal()`. Updated `rebuildCommandLine()` to append `--addendum "..."` when set. Updated `updatePreview()` to pass `m.addendum`. Updated initial preview call to pass empty addendum. Added `^A: addendum` to hotkey bar. In `tui2.go`: updated preview closure signature and sets `result.Addendum = addendum`. Updated all 10 test preview functions to new 3-param signature. Added specifying test `TestAddendumPassedToPreviewAndCommand`. Depth-first rung: TUI2 addendum modal and preview wiring (Phase 2a).
- **loops_remaining_forecast**: ~3-5 loops remaining. Remaining: Phase 3 (Python `PROMPT_REFERENCE_KEY` update), Phase 4 (skills integration), Phase 5 (Talon alignment). Phase 2 is functionally complete (TUI2 addendum modal operational). Confidence: high.
- **residual_constraints**:
  - TUI2 fixture snapshot (`cmd/bar/testdata/tui_smoke.json`) may need updating if it uses the preview callback — but smoke test doesn't exercise addendum so no immediate breakage. Severity: low. Monitoring: `go test ./internal/barcli/... -run TestRunTUIFixtureOutputsSnapshot`.
  - Python `PROMPT_REFERENCE_KEY` in `lib/metaPromptConfig.py` does not yet mention ADDENDUM. Severity: medium (Python users see inconsistent reference key). Mitigation: Phase 3. Monitoring: `grep -i addendum lib/metaPromptConfig.py`.
  - Bar skills (bar-autopilot, bar-workflow, bar-suggest, bar-manual) may not document `--addendum` usage. Severity: medium. Mitigation: Phase 4.
- **next_work**:
  - Behaviour: Phase 3 — Update Python `PROMPT_REFERENCE_KEY` in `lib/metaPromptConfig.py` to include ADDENDUM section description matching the Go reference key. Validation: `make ci-guardrails` or `python -m pytest _tests/`. Future-shaping: Python users see consistent reference key across CLI and Python paths.

## Loop 16: Python ADDENDUM alignment — heading and reference key (Phase 3)

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 3 (Reference Key Updates) — Rename `# Prompt` heading to `=== ADDENDUM (CLARIFICATION) ===` in `lib/modelSource.py:format_source_messages()` and add ADDENDUM entry to `lib/metaPromptConfig.py:PROMPT_REFERENCE_KEY` between TASK and CONSTRAINTS sections.
- **active_constraint**: Python `format_source_messages()` renders the task-clarification parameter as `# Prompt` (legacy heading) instead of `=== ADDENDUM (CLARIFICATION) ===`, and `PROMPT_REFERENCE_KEY` has no ADDENDUM entry — creating an inconsistency between the Python path and the Go `referenceKeyText` (which already documents ADDENDUM after Loop 12).
- **validation_targets**:
  - `.venv/bin/python -m pytest _tests/test_model_source_addendum.py`
  - `.venv/bin/python -m pytest _tests/`
- **evidence**:
  - red | 2026-02-09T (pre-implementation) | exit 1 | `.venv/bin/python -m pytest _tests/test_model_source_addendum.py` — `AssertionError: '=== ADDENDUM (CLARIFICATION) ===' not found in '# Prompt\n do this ...'` and `AssertionError: 'ADDENDUM' not found in PROMPT_REFERENCE_KEY` | inline
    helper:diff-snapshot=1 file changed (test_model_source_addendum.py only; production code unchanged)
  - green | 2026-02-09T (post-implementation) | exit 0 | `.venv/bin/python -m pytest _tests/` — 1211 passed | inline
    helper:diff-snapshot=3 files changed, 13 insertions(+), 8 deletions(-)
  - removal | 2026-02-09T (git restore lib/modelSource.py lib/metaPromptConfig.py) | exit 1 | `.venv/bin/python -m pytest _tests/test_model_source_addendum.py` — both assertions fail again | inline
    helper:diff-snapshot=0 files changed (production code reverted)
- **rollback_plan**: `git restore lib/modelSource.py lib/metaPromptConfig.py` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=3 files changed, 13 insertions(+), 8 deletions(-). In `lib/modelSource.py`: renamed `format_message("# Prompt\n")` → `format_message("=== ADDENDUM (CLARIFICATION) ===\n")` (line 58). In `lib/metaPromptConfig.py`: inserted 5-line ADDENDUM block between TASK and CONSTRAINTS in `PROMPT_REFERENCE_KEY`: `ADDENDUM (user prompt): Task clarification that modifies HOW to execute the task. • Contains additional instructions... • Not the content to work with... • Only present when the user provides explicit clarification`. Created `_tests/test_model_source_addendum.py` with 2 specifying tests: `test_format_source_messages_uses_addendum_heading` and `test_prompt_reference_key_documents_addendum_section`. Also fixed `_tests/test_bar_help_llm_examples.py` to check `--subject` instead of `--prompt` (pre-existing breakage from Loop 14's flag rename). Depth-first rung: Python ADDENDUM alignment (Phase 3).
- **loops_remaining_forecast**: ~1-2 loops remaining. Remaining: Phase 4 (update bar skills to document `--addendum` usage, verify no skills use `--prompt`). Phase 5 (Talon voice command alignment for addendum input) is lower priority and may be deferred. Confidence: high for Phase 4 scope.
- **residual_constraints**:
  - Bar skills (bar-autopilot, bar-workflow, bar-suggest, bar-manual) do not yet document `--addendum` usage. Severity: medium (LLM agents using skills will not know to use `--addendum` for task clarification). Mitigation: Phase 4. Monitoring: `grep -r "\-\-addendum" internal/barcli/skills/`.
  - Python `format_source_messages()` uses the `prompt` parameter as the primary task instruction (not just clarification) — when no bar grammar tokens are present, the `prompt` IS the task, not an addendum. The heading rename is cosmetically correct but semantically the Python path doesn't have a separate task token concept like Go does. Severity: low (behavioral mismatch noted, cosmetic alignment sufficient for now). Mitigation: deferred; future ADR if Python gains grammar-token-based task selection.
  - Stored preset files may contain old `"axes":{"static":"make"}` format (Loop 10). Severity: medium. Mitigation: deferred. Owning ADR: 0082 Phase 0.
- **next_work**:
  - Behaviour: Phase 4 — Update bar skill files (bar-autopilot, bar-workflow, bar-suggest, bar-manual) to document `--addendum` usage and ensure no skill uses `--prompt`. Validation: `grep -r "\-\-prompt" internal/barcli/skills/` returns 0 matches; `.venv/bin/python -m pytest _tests/` passes. Future-shaping: skill documentation teaches correct `--subject`/`--addendum` split.

## Loop 17: Skills Phase 4 — replace --prompt with --subject and document --addendum

- **helper_version**: `helper:v20251223.1`
- **focus**: ADR 0082 Phase 4 (Skills Integration) — Replace all 20 `--prompt` occurrences in embedded skill files (bar-manual, bar-autopilot, bar-workflow, bar-suggest) with `--subject`, and add `--addendum` documentation to bar-autopilot's Understanding Bar Output section.
- **active_constraint**: All four embedded skill files use the removed `--prompt` flag in examples and teaching narrative (20 occurrences total), and no skill file mentions `--addendum` — LLM agents using these skills will construct broken bar commands and have no guidance on when to use `--addendum` for task clarification.
- **validation_targets**:
  - `go test ./internal/barcli/ -run "TestEmbeddedSkillsUseSubjectFlag"`
  - `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...`
- **evidence**:
  - red | 2026-02-09T (pre-implementation) | exit 1 | `go test ./internal/barcli/ -run "TestEmbeddedSkillsUseSubjectFlag"` — 20 `--prompt` occurrences flagged across 4 files + `no embedded skill file mentions --addendum` | inline
    helper:diff-snapshot=1 file changed (help_llm_test.go only; skill files unchanged)
  - green | 2026-02-09T (post-implementation) | exit 0 | `go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...` — all tests PASS | inline
    helper:diff-snapshot=5 files changed, 46 insertions(+), 20 deletions(-)
  - removal | 2026-02-09T (git restore internal/barcli/skills/) | exit 1 | `go test ./internal/barcli/ -run "TestEmbeddedSkillsUseSubjectFlag"` — 20 `--prompt` occurrences flagged again | inline
    helper:diff-snapshot=0 files changed (skill files reverted)
- **rollback_plan**: `git restore internal/barcli/skills/` then replay red failure with validation target.
- **delta_summary**: helper:diff-snapshot=5 files changed, 46 insertions(+), 20 deletions(-). In all 4 skill `.md` files: replaced all ` --prompt "` and ` --prompt '` with ` --subject "` / ` --subject '` using `replace_all` (20 occurrences). In `bar-autopilot/skill.md`: added `ADDENDUM` to the bar output section list, added "Flag reference" subsection documenting `--subject` and `--addendum` with examples. Added `TestEmbeddedSkillsUseSubjectFlag` specifying test in `help_llm_test.go` that walks all embedded `.md` files, asserts no `--prompt` appears, and asserts at least one file mentions `--addendum`. Depth-first rung: skill file flag alignment (Phase 4).
- **loops_remaining_forecast**: Phase 4 complete. Phase 5 (Python/Talon voice command alignment for addendum input) is lower priority and may be deferred. The core ADR 0082 objectives are now satisfied: `--subject`/`--addendum` CLI flags, TUI2 modal, Python reference key alignment, and skills documentation all complete. Remaining open items are cosmetic/deferred. Confidence: high.
- **residual_constraints**:
  - Phase 5 (Talon voice command alignment): Python voice commands for submitting `prompt` to bar still use the `prompt` variable name internally. Severity: low (internal variable naming, no user-visible impact). Mitigation: defer. Monitoring: `grep -r "prompt" GPT/gpt.py | grep "bar build"`.
  - Stored preset files may contain old `"axes":{"static":"make"}` format (Loop 10). Severity: medium. Mitigation: deferred. Owning ADR: 0082 Phase 0.
  - `bar-workflow`, `bar-suggest`, `bar-manual` skill files updated for `--subject` but do not individually document `--addendum` (only bar-autopilot does). Severity: low (bar-autopilot is the canonical reference; agents using any skill can check bar-autopilot). Mitigation: acceptable for now. Monitoring: review if users report confusion.
- **next_work**:
  - Phase 5 (deferred) — Talon voice command alignment: verify Python voice commands that invoke bar use `--subject` and can pass `--addendum` when appropriate. Validation: manual testing or Python test for voice command format. Future-shaping: end-to-end alignment of voice → bar → LLM pipeline.
