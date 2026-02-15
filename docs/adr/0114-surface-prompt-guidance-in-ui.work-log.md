# ADR-0114 Work Log

## helper:v20251223.1

---

## Loop 1: Phase 1.1 - bartui2 Completions with Guidance

**Date:** 2026-02-15

### Focus
ADR-0114 Phase 1.1: Add guidance field to bartui2 completions.

### Active Constraint
Guidance exists in Python maps but is not surfaced in any UI. bartui2 needs to display it.

### Validation Targets
- `go build ./...` - Go build passes
- `go test ./internal/bartui2/... -run TestCompletion -v` - Completion tests pass
- Specifying validation: `python3 -m pytest _tests/test_bar_completion_cli.py -v -k guidance` - Guidance in completions test

### Evidence
- red | 2026-02-15T17:25:00Z | exit 0 | grep "Guidance" internal/bartui/tokens.go
    - helper:diff-snapshot=0 matches - Guidance field not present in TokenOption struct
- green | 2026-02-15T17:30:00Z | exit 0 | go build ./...
    - helper:diff-snapshot=builds successfully
- green | 2026-02-15T17:31:00Z | exit 0 | go test ./internal/bartui2/... -run TestCompletion -v
    - helper:diff-snapshot=5 tests pass

### Rollback Plan
`git restore --source=HEAD internal/barcli/tui_tokens.go internal/bartui/tokens.go internal/bartui2/program.go`

### Delta Summary
- Add Guidance field to TokenOption struct (internal/bartui/tokens.go)
- Populate guidance in tui_tokens.go for task/axis/persona options
- Add Guidance to completion struct and render in detail pane (bartui2/program.go)
- Add warningStyle for guidance display

### Loops Remaining Forecast
3 loops remaining: Phase 1.2 (helpHub), Phase 2.1 (modelHelpCanvas), Phase 2.2 (modelPatternGUI)

### Residual Constraints
- Python guidance not yet in all Talon surfaces (Phase 2 deferred to future loops)

### Next Work
- Phase 1.2: helpHub cheat sheet with guidance

---

## Loop 2: Phase 1.2 - helpHub Cheat Sheet with Guidance

**Date:** 2026-02-15

### Focus
ADR-0114 Phase 1.2: Surface guidance in helpHub cheat sheet.

### Active Constraint
Guidance maps exist in axisCatalog but are not consumed by helpHub.

### Validation Targets
- `python3 -m pytest _tests/test_help_hub.py -v -k cheat_sheet` - Cheat sheet tests pass
- Specifying validation: `python3 -m pytest _tests/test_help_hub.py::test_cheat_sheet_includes_guidance_when_present` - Guidance in cheat sheet test

### Evidence
- red | 2026-02-15T17:35:00Z | exit 0 | grep -c "guidance" lib/helpHub.py
    - helper:diff-snapshot=0 matches - no guidance references in helpHub before changes
- green | 2026-02-15T17:40:00Z | exit 0 | python3 -m pytest _tests/test_help_hub.py -v -k cheat_sheet
    - helper:diff-snapshot=9 tests passed

### Rollback Plan
`git restore --source=HEAD lib/helpHub.py`

### Delta Summary
- Add _axis_guidance_lines() function to extract guidance from axis_catalog
- Include guidance section in cheat sheet output when guidance exists
- Shows token-specific selection hints like 'fix: In bar's grammar, fix means reformat...'

### Loops Remaining Forecast
2 loops remaining: Phase 2.1 (modelHelpCanvas), Phase 2.2 (modelPatternGUI)

### Residual Constraints
- modelHelpCanvas and modelPatternGUI not yet updated (Phase 2)

### Next Work
- Phase 2.1: modelHelpCanvas axis help with guidance
