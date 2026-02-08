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
