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

## 2026-02-02 — loop 003
- helper_version: helper:v20251223.1
- focus: ADR 0096 Artifact Retrieval and Verification Layer — Implement artifact download with SHA256 checksum verification
- active_constraint: No mechanism to download and verify release artifacts; `bar update install` cannot retrieve binaries from GitHub releases or validate integrity (falsifiable via `go test ./internal/updater -run TestArtifactDownload` and `go test ./internal/updater -run TestChecksumVerification` failing with "undefined" error)
- expected_value:
  | Factor           | Value | Rationale |
  | Impact           | High  | Blocks entire update installation flow; severity=critical |
  | Probability      | High  | Standard Go libraries (net/http, crypto/sha256) provide deterministic implementation path |
  | Time Sensitivity | High  | Blocks downstream work (binary replacement, rollback, integration tests) |
  | Uncertainty note | N/A   | Implementation complexity is well-understood; no unknowns |
- validation_targets:
  - go test ./internal/updater -run TestArtifactDownload
  - go test ./internal/updater -run TestChecksumVerification
- evidence: docs/adr/evidence/0096-bar-cli-automatic-updates/loop-003.md
- rollback_plan: `git stash` to save changes, verify test failures return, then `git stash pop` to restore
- delta_summary: helper:diff-snapshot=3 files changed, 301 insertions(+) — created download.go (ArtifactDownloader.Download for HTTP artifact retrieval, ChecksumVerifier.VerifySHA256/ComputeSHA256 for SHA256 validation) and download_test.go (TestArtifactDownload with httptest mock server, TestChecksumVerification with known hashes, TestComputeSHA256 with temp files)
- loops_remaining_forecast: 6-10 loops remaining (Binary Installation, Rollback, Real GitHub API Integration, Configuration, Integration tests, Documentation) — high confidence on artifact layer completion
- residual_constraints:
  - Real GitHub API client not implemented (severity: high; mitigation: implement HTTP client in loop 004 with retry/timeout handling; monitoring: go test with mock server; owning ADR: 0096)
  - GitHub API rate limiting not handled (severity: medium; mitigation: implement in loop 004 with exponential backoff; monitoring: test with rate-limit scenarios; owning ADR: 0096)
  - Binary replacement and rollback logic not implemented (severity: high; mitigation: implement in loop 005-006; monitoring: integration tests with temp binaries; owning ADR: 0096)
  - Configuration file parsing not implemented (severity: medium; mitigation: implement in loop 007; monitoring: config validation tests; owning ADR: 0096)
  - No end-to-end integration tests (severity: medium; mitigation: add in loop 008-009; monitoring: CI test coverage; owning ADR: 0096)
  - Documentation incomplete (severity: low; mitigation: update README and help text in loop 010; monitoring: documentation coverage checklist; owning ADR: 0096)
- next_work:
  - Behaviour: Implement real GitHub API client with HTTP transport (validation: `go test ./internal/updater -run TestGitHubAPIClient`)
  - Behaviour: Add retry logic and rate limit handling for GitHub API (validation: `go test ./internal/updater -run TestRateLimitHandling`)
  - Behaviour: Implement binary installation with atomic replacement (validation: `go test ./internal/updater -run TestBinaryInstallation`)

## 2026-02-02 — loop 004
- helper_version: helper:v20251223.1
- focus: ADR 0096 Real GitHub API Integration — Implement HTTP client for GitHub Releases API with asset URL resolution
- active_constraint: No real GitHub API client exists; UpdateChecker cannot query actual releases from GitHub (falsifiable via `go test ./internal/updater -run TestGitHubAPIClient` failing with "undefined" error for HTTPGitHubClient type)
- expected_value:
  | Factor           | Value | Rationale |
  | Impact           | High  | Blocks end-to-end update functionality; mock client insufficient for production |
  | Probability      | High  | GitHub API is well-documented; standard REST endpoints with JSON responses |
  | Time Sensitivity | High  | Required for integration with bar update check command; blocks user-facing feature |
  | Uncertainty note | N/A   | GitHub API contract is stable; implementation path is deterministic |
- validation_targets:
  - go test ./internal/updater -run TestGitHubAPIClient
- evidence: docs/adr/evidence/0096-bar-cli-automatic-updates/loop-004.md
- rollback_plan: `git stash` to save changes, verify test failures return, then `git stash pop` to restore
- delta_summary: helper:diff-snapshot=3 files changed, 331 insertions(+) — created github.go (HTTPGitHubClient implementing GitHubClient interface with GetLatestRelease for GitHub Releases API /repos/:owner/:repo/releases/latest endpoint, GetAssetDownloadURL for asset resolution, githubRelease/githubAsset JSON structs for API parsing) and github_test.go (TestGitHubAPIClient with 3 scenarios using httptest mock server, TestGitHubAPIClientAssetURLResolution and TestGitHubAPIClientAssetNotFound for asset URL lookup)
- loops_remaining_forecast: 5-9 loops remaining (Bar update check integration, Binary Installation, Rollback, Configuration, Integration tests, Documentation) — high confidence on API client completion
- residual_constraints:
  - GitHub API rate limiting not handled (severity: medium; mitigation: implement in loop 005 with exponential backoff and 429 response handling; monitoring: test with mock rate-limit responses; owning ADR: 0096)
  - Binary replacement and rollback logic not implemented (severity: high; mitigation: implement in loop 005-006; monitoring: integration tests with temp binaries; owning ADR: 0096)
  - Bar update check command not wired to updater package (severity: medium; mitigation: implement in loop 005 after API client lands; monitoring: go test for update check integration; owning ADR: 0096)
  - Configuration file parsing not implemented (severity: medium; mitigation: defer to loop 007; monitoring: config validation tests; owning ADR: 0096)
  - No end-to-end integration tests (severity: medium; mitigation: add in loop 008-009; monitoring: CI test coverage; owning ADR: 0096)
  - Documentation incomplete (severity: low; mitigation: update README and help text in loop 010; monitoring: documentation coverage checklist; owning ADR: 0096)
- next_work:
  - Behaviour: Wire bar update check command to GitHub API client (validation: `go run ./cmd/bar update check` with version comparison)
  - Behaviour: Add retry logic and rate limit handling for GitHub API (validation: `go test ./internal/updater -run TestRateLimitHandling`)
  - Behaviour: Implement binary installation with atomic replacement (validation: `go test ./internal/updater -run TestBinaryInstallation`)
