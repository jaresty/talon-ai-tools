# ADR 0096: Automatic Update Mechanism for Bar CLI - Work Log

## 2026-02-02 — loop 001
- helper_version: helper:v20251223.1
- focus: ADR 0096 Decision → Implementation Notes — Add `cmd/bar/update.go` subcommand skeleton with check/install/rollback verbs
- active_constraint: No `bar update` subcommand exists; users cannot trigger update checks (falsifiable via `go run ./cmd/bar update --help` returning exit code !=0 with "unknown command" error)
- validation_targets:
  - go test ./cmd/bar -run TestUpdateHelpCommand
- evidence: docs/adr/evidence/0096-bar-cli-automatic-updates/loop-001.md
- rollback_plan: `git restore --source=HEAD -- cmd/bar/update.go cmd/bar/update_test.go cmd/bar/main.go` then rerun `go test ./cmd/bar -run TestUpdateHelpCommand` to verify red failure returns
- delta_summary: helper:diff-snapshot=3 files changed, ~150 insertions(+) — added update.go subcommand skeleton with check/install/rollback verbs, wired into main.go dispatcher, and added test validating help output
- loops_remaining_forecast: 8-12 loops (Release Discovery Layer, Artifact Retrieval Layer, Verification Layer, Installation Layer, Rollback Mechanism, Configuration, Integration tests, Documentation) — medium confidence pending GitHub API integration complexity
- residual_constraints:
  - GitHub Releases API integration not implemented (severity: high; mitigation: implement in loop 002 with mock-based tests; monitoring: go test coverage for updater package; owning ADR: 0096)
  - Checksum verification logic missing (severity: high; mitigation: implement in loop 003-004; monitoring: go test for SHA256 verification; owning ADR: 0096)
  - Binary replacement and rollback logic not implemented (severity: high; mitigation: implement in loop 005-006; monitoring: integration tests with temp binaries; owning ADR: 0096)
  - Configuration file parsing not implemented (severity: medium; mitigation: implement in loop 007; monitoring: config validation tests; owning ADR: 0096)
  - No end-to-end integration tests (severity: medium; mitigation: add in loop 008-009; monitoring: CI test coverage; owning ADR: 0096)
  - Documentation incomplete (severity: low; mitigation: update README and help text in loop 010; monitoring: documentation coverage checklist; owning ADR: 0096)
- next_work:
  - Behaviour: Implement Release Discovery Layer — query GitHub Releases API and compare semver (validation: `go test ./internal/updater -run TestReleaseDiscovery`)
  - Behaviour: Add mock GitHub API responses for testing (validation: `go test ./internal/updater -run TestMockAPI`)
  - Behaviour: Implement version comparison logic with semver parsing (validation: `go test ./internal/updater -run TestVersionCompare`)

## 2026-02-02 — loop 002
- helper_version: helper:v20251223.1
- focus: ADR 0096 Release Discovery Layer — Implement version comparison and GitHub Releases API querying with mock-based tests
- active_constraint: No mechanism to discover available updates; `bar update check` cannot determine if newer versions exist (falsifiable via `go test ./internal/updater -run TestReleaseDiscovery` failing with "undefined" error)
- validation_targets:
  - go test ./internal/updater -run TestVersionCompare
  - go test ./internal/updater -run TestReleaseDiscovery
- evidence: docs/adr/evidence/0096-bar-cli-automatic-updates/loop-002.md
- rollback_plan: `git stash` to save changes, verify test failures return, then `git stash pop` to restore
- delta_summary: helper:diff-snapshot=5 files changed, 365 insertions(+) — created internal/updater package with version comparison (ParseVersion, CompareVersions), release discovery (Release, UpdateChecker, GitHubClient interface), and comprehensive mock-based tests (TestVersionCompare, TestParseVersion, TestReleaseDiscovery)
- loops_remaining_forecast: 7-11 loops remaining (Artifact Retrieval, Verification, Installation, Rollback, Configuration, Integration tests, Documentation)
- residual_constraints:
  - GitHub API rate limiting not handled (severity: medium; mitigation: implement in loop 003; monitoring: test with rate-limit scenarios; owning ADR: 0096)
  - Checksum verification logic missing (severity: high; mitigation: implement in loop 003-004; monitoring: go test for SHA256 verification; owning ADR: 0096)
  - Binary replacement and rollback logic not implemented (severity: high; mitigation: implement in loop 005-006; monitoring: integration tests with temp binaries; owning ADR: 0096)
  - Configuration file parsing not implemented (severity: medium; mitigation: implement in loop 007; monitoring: config validation tests; owning ADR: 0096)
  - No end-to-end integration tests (severity: medium; mitigation: add in loop 008-009; monitoring: CI test coverage; owning ADR: 0096)
  - Documentation incomplete (severity: low; mitigation: update README and help text in loop 010; monitoring: documentation coverage checklist; owning ADR: 0096)
- next_work:
  - Behaviour: Implement Artifact Retrieval Layer — download release artifacts with progress tracking (validation: `go test ./internal/updater -run TestArtifactDownload`)
  - Behaviour: Add checksum verification for downloaded artifacts (validation: `go test ./internal/updater -run TestChecksumVerification`)
  - Behaviour: Handle GitHub API rate limiting gracefully (validation: `go test ./internal/updater -run TestRateLimitHandling`)
