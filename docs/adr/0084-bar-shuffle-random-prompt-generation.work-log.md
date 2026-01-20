# ADR 0084 Work Log: Bar Shuffle Random Prompt Generation

## Overview

This work-log tracks implementation progress for `bar shuffle` command per ADR 0084.

**Evidence root:** `docs/adr/evidence/0084/`
**VCS revert:** `git restore --source=HEAD`
**Helper version:** `helper:v20251223.1`

---

## Loop 1: Implement shuffle.go with complete functionality

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0084 - Create shuffle.go with core random token selection logic

**active_constraint:** No shuffle.go file exists; cannot build or test shuffle functionality until the file is created with basic structure.

**validation_targets:**
- `go build ./cmd/bar && ./bar shuffle` exits 0 and produces valid prompt
- `./bar shuffle --seed 42` produces reproducible output
- `./bar shuffle --json | jq -e '.task and .axes'` validates JSON format

**evidence:**
- red | 2026-01-20T00:00:00Z | exit 1 | `go build ./cmd/bar && ./bar shuffle`
  - helper:diff-snapshot=0 files changed
  - shuffle subcommand does not exist | inline
- green | 2026-01-20T01:00:00Z | exit 0 | `go build ./cmd/bar && ./bar shuffle`
  - helper:diff-snapshot=3 files changed
  - shuffle command produces valid prompt with TASK, CONSTRAINTS, PERSONA sections | inline
- green | 2026-01-20T01:01:00Z | exit 0 | `./bar shuffle --seed 42` (reproducibility)
  - Two consecutive runs with same seed produce identical output | inline
- green | 2026-01-20T01:02:00Z | exit 0 | `./bar shuffle --json | jq -e '.task and .axes'`
  - JSON output matches build command schema | inline

**rollback_plan:** `git restore --source=HEAD internal/barcli/shuffle.go internal/barcli/app.go internal/barcli/cli/config.go`

**delta_summary:** Created shuffle.go with ShuffleOptions struct and Shuffle function. Added shuffle-specific CLI flags (--seed, --include, --exclude, --fill) to config.go. Wired shuffle command in app.go with help text. Tokens are sorted for reproducibility with --seed.

**files_changed:**
- `internal/barcli/shuffle.go` (new) - Shuffle function, ShuffleOptions, getStageTokens helper
- `internal/barcli/app.go` - Added runShuffle function, updated topUsage and generalHelpText
- `internal/barcli/cli/config.go` - Added Seed, Include, Exclude, Fill fields and parsing

**loops_remaining_forecast:** 0 (implementation complete)

**residual_constraints:**
- None - all ADR 0084 requirements implemented

**next_work:**
- None - ready for commit
