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

## 2026-02-02 — loop 005
- helper_version: helper:v20251223.1
- focus: ADR 0096 Update Check Integration — Wire bar update check command to UpdateChecker with GitHub API client and version comparison
- active_constraint: Bar update check command not connected to updater package; users cannot check for updates (falsifiable via `go run ./cmd/bar update check` returning "not yet implemented" error instead of performing actual version check against GitHub)
- expected_value:
  | Factor           | Value | Rationale |
  | Impact           | High  | Enables end-to-end update checking flow; delivers user-facing feature |
  | Probability      | High  | All components exist (UpdateChecker, HTTPGitHubClient, CompareVersions); integration is straightforward |
  | Time Sensitivity | High  | Completes MVP for update checking; unblocks user testing |
  | Uncertainty note | N/A   | Integration path clear; need to determine current version from binary |
- validation_targets:
  - go test ./cmd/bar -run TestUpdateCheckIntegration
- evidence: docs/adr/evidence/0096-bar-cli-automatic-updates/loop-005.md
- rollback_plan: `git stash` to save changes, verify test failures return, then `git stash pop` to restore
- delta_summary: helper:diff-snapshot=7 files changed, 209 insertions(+), 28 deletions(-) — wired bar update check to updater package: added runUpdateCheck function in app.go to create UpdateChecker with HTTPGitHubClient, added SetVersion/SetUpdateClient helpers for version injection and test mocking, created main.go barVersion variable set via ldflags, moved MockGitHubClient/MockRelease from release_test.go to mock.go for cross-package testing, created update_integration_test.go with 3 test scenarios (newer version, already latest, current newer)
- loops_remaining_forecast: 4-8 loops remaining (Binary Installation, Rollback, Configuration, Integration tests, Documentation) — high confidence on update check completion
- residual_constraints:
  - Version string not embedded in bar binary (severity: medium; mitigation: add build-time version via ldflags in loop 006; monitoring: go run ./cmd/bar --version; owning ADR: 0096)
  - GitHub API rate limiting not handled (severity: low; mitigation: defer to future loop with exponential backoff; monitoring: test with mock rate-limit responses; owning ADR: 0096)
  - Binary replacement and rollback logic not implemented (severity: high; mitigation: implement in loop 006-007; monitoring: integration tests with temp binaries; owning ADR: 0096)
  - Configuration file parsing not implemented (severity: medium; mitigation: defer to loop 008; monitoring: config validation tests; owning ADR: 0096)
  - No end-to-end integration tests (severity: medium; mitigation: add in loop 009; monitoring: CI test coverage; owning ADR: 0096)
  - Documentation incomplete (severity: low; mitigation: update README and help text in loop 010; monitoring: documentation coverage checklist; owning ADR: 0096)
- next_work:
  - Behaviour: Embed version string in bar binary at build time (validation: `go run -ldflags "-X main.version=dev" ./cmd/bar --version`)
  - Behaviour: Implement binary installation with atomic replacement (validation: `go test ./internal/updater -run TestBinaryInstallation`)
  - Behaviour: Add rollback mechanism for failed updates (validation: `go test ./internal/updater -run TestRollback`)

## 2026-02-02 — loop 006
- helper_version: helper:v20251223.1
- focus: ADR 0096 Binary Installation Layer — Implement atomic binary replacement with backup and verification
- active_constraint: No mechanism to install downloaded binaries; bar update install cannot replace running executable with new version (falsifiable via `go test ./internal/updater -run TestBinaryInstallation` failing with "undefined" error for BinaryInstaller type)
- expected_value:
  | Factor           | Value | Rationale |
  | Impact           | High  | Enables complete update flow from check to installation; critical for ADR completion |
  | Probability      | High  | Standard filesystem operations (rename, copy, chmod); atomic replacement via os.Rename well-understood |
  | Time Sensitivity | High  | Blocks rollback mechanism and end-to-end update testing |
  | Uncertainty note | N/A   | File permissions and cross-device rename are deterministic; tests use temp directories |
- validation_targets:
  - go test ./internal/updater -run TestBinaryInstallation
- evidence: docs/adr/evidence/0096-bar-cli-automatic-updates/loop-006.md
- rollback_plan: `git stash` to save changes, verify test failures return, then `git stash pop` to restore
- delta_summary: helper:diff-snapshot=3 files changed, 294 insertions(+) — created install.go (BinaryInstaller with Install method for atomic replacement via os.Rename, CreateBackup method for timestamped backups, copyFile helper for safe file operations with permission preservation) and install_test.go (TestBinaryInstallation with 2 scenarios validating installation and permission preservation, TestBinaryInstallationBackupCreation validating backup creation and content)
- loops_remaining_forecast: 3-7 loops remaining (Rollback mechanism, Wire install command, Configuration, Integration tests, Documentation) — high confidence on installation layer completion
- residual_constraints:
  - Rollback mechanism not implemented (severity: high; mitigation: implement in loop 007 with backup restoration; monitoring: go test for rollback scenarios; owning ADR: 0096)
  - Bar update install command not wired to installation logic (severity: medium; mitigation: implement in loop 007; monitoring: manual test of bar update install; owning ADR: 0096)
  - Version string not embedded in bar binary (severity: medium; mitigation: add build-time version via ldflags in loop 008; monitoring: go run ./cmd/bar --version; owning ADR: 0096)
  - GitHub API rate limiting not handled (severity: low; mitigation: defer to future loop; monitoring: test with mock rate-limit responses; owning ADR: 0096)
  - Configuration file parsing not implemented (severity: medium; mitigation: defer to loop 009; monitoring: config validation tests; owning ADR: 0096)
  - No end-to-end integration tests (severity: medium; mitigation: add in loop 010; monitoring: CI test coverage; owning ADR: 0096)
  - Documentation incomplete (severity: low; mitigation: update README and help text in loop 011; monitoring: documentation coverage checklist; owning ADR: 0096)
- next_work:
  - Behaviour: Implement rollback mechanism with backup restoration (validation: `go test ./internal/updater -run TestRollback`)
  - Behaviour: Wire bar update install command to binary installation logic (validation: `go run ./cmd/bar update install` attempting installation)
  - Behaviour: Add --version flag to display embedded version (validation: `go run -ldflags "-X main.barVersion=1.0.0" ./cmd/bar --version`)

## 2026-02-02 — loop 007
- helper_version: helper:v20251223.1
- focus: ADR 0096 Update Install Integration — Wire bar update install command to download, verify, and install binaries from GitHub releases
- active_constraint: Bar update install command not connected to installation logic; users cannot install updates (falsifiable via `go test ./cmd/bar -run TestUpdateInstallIntegration` failing with "undefined" error for installation orchestration)
- expected_value:
  | Factor           | Value | Rationale |
  | Impact           | High  | Completes end-to-end update installation flow; delivers user-facing feature |
  | Probability      | High  | All components exist (HTTPGitHubClient, ArtifactDownloader, ChecksumVerifier, BinaryInstaller); orchestration is straightforward |
  | Time Sensitivity | High  | Enables complete update workflow testing; unblocks MVP validation |
  | Uncertainty note | N/A   | Integration path clear; need to determine target binary path and asset selection |
- validation_targets:
  - go test ./cmd/bar -run TestUpdateInstallIntegration
- evidence: docs/adr/evidence/0096-bar-cli-automatic-updates/loop-007.md
- rollback_plan: `git stash` to save changes, verify test failures return, then `git stash pop` to restore
- delta_summary: helper:diff-snapshot=4 files changed, 177 insertions(+), 2 deletions(-) — wired bar update install to installation logic: added runUpdateInstall function in app.go orchestrating UpdateChecker for version check, HTTPGitHubClient.GetAssetDownloadURL for asset URL resolution (hardcoded darwin-amd64 for now), ArtifactDownloader for binary download to temp directory, BinaryInstaller for atomic installation with backup; added path/filepath import; created update_install_test.go validating command attempts installation and fails gracefully without real release
- loops_remaining_forecast: 2-6 loops remaining (Rollback mechanism, Version flag, Configuration, Integration tests, Documentation) — high confidence on install integration completion
- residual_constraints:
  - Rollback mechanism not implemented (severity: high; mitigation: implement in loop 008 with backup restoration; monitoring: go test for rollback scenarios; owning ADR: 0096)
  - Version string not embedded in bar binary (severity: medium; mitigation: add build-time version via ldflags in loop 009; monitoring: go run ./cmd/bar --version; owning ADR: 0096)
  - Asset selection logic hardcoded (severity: medium; mitigation: add platform detection in loop 009; monitoring: test on multiple platforms; owning ADR: 0096)
  - GitHub API rate limiting not handled (severity: low; mitigation: defer to future loop; monitoring: test with mock rate-limit responses; owning ADR: 0096)
  - Configuration file parsing not implemented (severity: medium; mitigation: defer to loop 010; monitoring: config validation tests; owning ADR: 0096)
  - No end-to-end integration tests (severity: medium; mitigation: add in loop 011; monitoring: CI test coverage; owning ADR: 0096)
  - Documentation incomplete (severity: low; mitigation: update README and help text in loop 012; monitoring: documentation coverage checklist; owning ADR: 0096)
- next_work:
  - Behaviour: Implement rollback mechanism with backup restoration (validation: `go test ./internal/updater -run TestRollback`)
  - Behaviour: Add --version flag to display embedded version (validation: `go run -ldflags "-X main.barVersion=1.0.0" ./cmd/bar --version`)
  - Behaviour: Add platform detection for asset selection (validation: `go test ./internal/updater -run TestPlatformDetection`)

## 2026-02-02 — loop 008
- helper_version: helper:v20251223.1
- focus: ADR 0096 Rollback Mechanism — Implement backup restoration to revert failed or unwanted updates
- active_constraint: No mechanism to restore previous binary versions; users cannot recover from failed updates (falsifiable via `go test ./internal/updater -run TestRollback` failing with "undefined" error for rollback functionality)
- expected_value:
  | Factor           | Value | Rationale |
  | Impact           | High  | Critical safety feature; prevents user lockout from failed updates |
  | Probability      | High  | Backup files already created by BinaryInstaller; restoration is file copy + rename |
  | Time Sensitivity | High  | Required before production deployment; safety-critical feature |
  | Uncertainty note | N/A   | File operations deterministic; backup format already established |
- validation_targets:
  - go test ./internal/updater -run TestRollback
- evidence: docs/adr/evidence/0096-bar-cli-automatic-updates/loop-008.md
- rollback_plan: `git stash` to save changes, verify test failures return, then `git stash pop` to restore
- delta_summary: helper:diff-snapshot=2 files changed, 86 insertions(+), 1 deletion(-) — implemented rollback mechanism: added Rollback method to BinaryInstaller in install.go (finds most recent backup, copies to temp, atomic rename to replace current binary, preserves permissions); added ListBackups method returning sorted backup list (most recent first); added sort and strings imports; created rollback_test.go with TestRollback (2 scenarios: successful rollback, permission preservation), TestRollbackNoBackupsAvailable (validates error when no backups), TestListBackups (validates sorting)
- loops_remaining_forecast: 1-5 loops remaining (Wire rollback command, Version flag, Platform detection, Integration tests, Documentation) — high confidence on rollback mechanism completion
- residual_constraints:
  - Bar update rollback command not wired to rollback logic (severity: medium; mitigation: implement in loop 009; monitoring: manual test of bar update rollback; owning ADR: 0096)
  - Version string not embedded in bar binary (severity: medium; mitigation: add build-time version via ldflags in loop 010; monitoring: go run ./cmd/bar --version; owning ADR: 0096)
  - Asset selection logic hardcoded (severity: medium; mitigation: add platform detection in loop 010; monitoring: test on multiple platforms; owning ADR: 0096)
  - Multiple backups not managed (severity: low; mitigation: add backup pruning in future loop; monitoring: disk usage in backup directory; owning ADR: 0096)
  - GitHub API rate limiting not handled (severity: low; mitigation: defer to future loop; monitoring: test with mock rate-limit responses; owning ADR: 0096)
  - Configuration file parsing not implemented (severity: medium; mitigation: defer to loop 011; monitoring: config validation tests; owning ADR: 0096)
  - No end-to-end integration tests (severity: medium; mitigation: add in loop 012; monitoring: CI test coverage; owning ADR: 0096)
  - Documentation incomplete (severity: low; mitigation: update README and help text in loop 013; monitoring: documentation coverage checklist; owning ADR: 0096)
- next_work:
  - Behaviour: Wire bar update rollback command to restoration logic (validation: `go run ./cmd/bar update rollback` restoring backup)
  - Behaviour: Add --version flag to display embedded version (validation: `go run -ldflags "-X main.barVersion=1.0.0" ./cmd/bar --version`)
  - Behaviour: Add platform detection for asset selection (validation: `go test ./internal/updater -run TestPlatformDetection`)

## 2026-02-02 — loop 009
- helper_version: helper:v20251223.1
- focus: ADR 0096 Rollback Command Wiring — Wire bar update rollback command to BinaryInstaller.Rollback
- active_constraint: Rollback command returns "not yet implemented" instead of invoking BinaryInstaller.Rollback; users cannot trigger rollback via CLI (falsifiable via `go test ./cmd/bar -run TestUpdateRollbackIntegration` failing with "not yet implemented" in output)
- expected_value:
  | Factor           | Value | Rationale |
  | Impact           | High  | Completes rollback safety feature; enables user recovery from failed updates |
  | Probability      | High  | Rollback mechanism already implemented; wiring is deterministic integration |
  | Time Sensitivity | High  | Safety-critical feature required before production deployment |
  | Uncertainty note | N/A   | Integration path clear; backup directory and binary path determination straightforward |
- validation_targets:
  - go test ./cmd/bar -run TestUpdateRollbackIntegration
- evidence: docs/adr/evidence/0096-bar-cli-automatic-updates/loop-009.md
- rollback_plan: `git stash` to save changes, verify test failures return, then `git stash pop` to restore
- delta_summary: helper:diff-snapshot=2 files changed, 58 insertions(+), 2 deletions(-) — wired bar update rollback command to BinaryInstaller.Rollback: added runUpdateRollback function in app.go (gets current binary path, creates BinaryInstaller with backup directory, lists available backups, performs rollback via installer.Rollback, prints success message); updated rollback verb case to call runUpdateRollback instead of returning "not yet implemented"; created update_rollback_test.go validating command attempts rollback and no longer shows "not yet implemented"
- loops_remaining_forecast: 1-4 loops remaining (Version flag, Platform detection, Integration tests, Documentation) — high confidence on rollback command completion
- residual_constraints:
  - Version string not embedded in bar binary (severity: medium; mitigation: add build-time version via ldflags in loop 010; monitoring: go run ./cmd/bar --version; owning ADR: 0096)
  - Asset selection logic hardcoded (severity: medium; mitigation: add platform detection in loop 010; monitoring: test on multiple platforms; owning ADR: 0096)
  - Multiple backups not managed (severity: low; mitigation: add backup pruning in future loop; monitoring: disk usage in backup directory; owning ADR: 0096)
  - Backup directory location hardcoded (severity: medium; mitigation: add configuration support in future loop; monitoring: user feedback on backup location; owning ADR: 0096)
  - GitHub API rate limiting not handled (severity: low; mitigation: defer to future loop; monitoring: test with mock rate-limit responses; owning ADR: 0096)
  - Configuration file parsing not implemented (severity: medium; mitigation: defer to loop 011; monitoring: config validation tests; owning ADR: 0096)
  - No end-to-end integration tests (severity: medium; mitigation: add in loop 012; monitoring: CI test coverage; owning ADR: 0096)
  - Documentation incomplete (severity: low; mitigation: update README and help text in loop 013; monitoring: documentation coverage checklist; owning ADR: 0096)
- next_work:
  - Behaviour: Add --version flag to display embedded version (validation: `go run -ldflags "-X main.barVersion=1.0.0" ./cmd/bar --version`)
  - Behaviour: Add platform detection for asset selection (validation: `go test ./internal/updater -run TestPlatformDetection`)
  - Behaviour: Add end-to-end integration tests (validation: `go test ./cmd/bar -run TestUpdateE2E`)
