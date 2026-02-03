# ADR 0096: Automatic Update Mechanism for Bar CLI

## Status

Proposed

## Context

The `bar` CLI tool is distributed as a standalone Go binary via GitHub releases. Users currently must manually check for updates, download new versions, verify checksums, and replace their installed binary. This creates friction for:

- **Version drift**: Users remain on stale versions with bugs or missing features
- **Security patches**: Critical fixes require manual intervention to propagate
- **Feature adoption**: New capabilities don't reach users organically
- **Support burden**: Issues filed against outdated versions waste maintainer time

The proposal introduces an automatic update mechanism that:
- Checks GitHub releases API for newer versions
- Downloads platform-appropriate binaries
- Verifies SHA256 checksums against published artifacts
- Performs atomic in-place replacement with rollback on failure

### Prior Work

- **ADR 0065**: Portable prompt grammar CLI (established GitHub release workflow)
- **ADR 0066**: Embed portable grammar CLI (established binary distribution pattern)

## Decision

Implement a self-update subsystem with the following structural components:

### Component Architecture

**Release Discovery Layer**
- Query GitHub Releases API (`/repos/:owner/:repo/releases/latest`)
- Compare semver tags against embedded build version
- Cache negative results (TTL: 24h) to limit API calls
- Respect rate limits; degrade gracefully on 403/429

**Artifact Retrieval Layer**
- Download binary for detected platform/architecture pair
- Stream to temporary file with progress indication (optional, stderr)
- Fetch corresponding `checksums.txt` from same release

**Verification Layer**
- Compute SHA256 of downloaded binary
- Parse `checksums.txt` for expected hash
- Abort if mismatch; surface error with diagnostic context

**Installation Layer**
- Detect running binary path via `os.Executable()`
- Rename current binary to `.bar.backup.<timestamp>`
- Atomically move new binary into place
- Set executable permissions (`chmod +x`)
- On failure: restore `.backup` and remove partial artifacts

**Rollback Mechanism**
- Preserve previous binary for N days (default: 7)
- Provide `bar update rollback` to revert manually
- Cleanup stale backups on successful update

### Invocation Modes

1. **Manual trigger**: `bar update` — user-initiated check + install
2. **Automatic check**: Background goroutine on `bar` launch (opt-in via config)
3. **Notification only**: Check + notify on stderr; require manual `bar update` to proceed

### Configuration Surface

```toml
# ~/.config/bar/config.toml or BAR_UPDATE_* env vars
[update]
enabled = true              # master toggle
auto_install = false        # if true, install without prompt; else notify only
check_interval = "24h"      # frequency for background checks
backup_retention = "168h"   # 7 days
github_token = ""           # optional; increases rate limit to 5000/hr
```

### Security & Trust Boundaries

- **TLS verification**: Enforce certificate validation for GitHub API/CDN
- **Checksum authority**: Trust only checksums published in same release as binary
- **No code execution during update**: Downloaded binary not executed until user runs `bar` again
- **Backup preservation**: Users can always revert to known-good state

## Consequences

### Benefits

- **Reduced version fragmentation**: Users converge on recent releases faster
- **Security patch velocity**: Critical fixes propagate without manual intervention
- **Lower support burden**: Maintainers can assume users are on N or N-1 versions
- **User convenience**: Zero-friction updates for casual users

### Weaknesses & Attack Vectors

**Compromised GitHub Account**
If an attacker gains access to the `bar` repository's release workflow, they can publish malicious binaries with matching checksums.

**Mitigation**: Consider Sigstore/cosign signature verification in future iteration (adds dependency complexity).

**Checksum File Manipulation**
Attacker who compromises CDN but not repository could serve altered `checksums.txt`.

**Mitigation**: Parse checksums from GitHub API response body (JSON), not separate artifact fetch. Fallback: Require checksums to be GPG-signed.

**Partial Write Failures**
If `os.Rename()` fails mid-operation (filesystem corruption, permissions), binary may be unusable.

**Mitigation**: Pre-flight checks (writability test, disk space), atomic rename on POSIX, fallback to copy+delete on Windows.

**Rollback Window Expiry**
If backup cleanup runs before user notices broken update, rollback is impossible.

**Mitigation**: Extend retention to 30 days; add `bar doctor` command to validate installation integrity.

**Rate Limit Exhaustion (Unauthenticated)**
GitHub's unauthenticated API limit is 60 requests/hour. Frequent CLI invocations (e.g., in CI loops) could trigger rate limiting.

**Mitigation**: 24-hour negative cache, exponential backoff on 429, document `GITHUB_TOKEN` workaround.

**Network Partitions / Offline Use**
Users in air-gapped or restrictive network environments cannot update.

**Mitigation**: Fail gracefully; log warning but do not block CLI usage. Provide `--skip-update-check` flag.

**Supply Chain: Dependency Introduction**
Go stdlib covers HTTP/JSON/crypto needs, but future enhancements (signature verification) may require external dependencies.

**Mitigation**: Gate behind build tags; ship minimal binary by default.

### Edge Cases & Failure Modes

- **Binary in use during update**: Windows locks executable files. **Mitigation**: Detect lock, defer update to next run.
- **Simultaneous updates**: Multiple CLI instances triggered concurrently. **Mitigation**: File-based lock (`.bar.update.lock`).
- **Version downgrade**: User manually installs older version, then auto-update re-upgrades. **Mitigation**: Honor user intent; skip updates if current version > latest release (allow pre-release testing).
- **Cross-architecture mistakes**: User manually moved binary across machines (e.g., copied `linux_amd64` to `linux_arm64` VM). **Mitigation**: Embed `GOOS/GOARCH` in build metadata; warn on mismatch.

### Unstated Assumptions

- GitHub Releases API remains stable and accessible
- Users have write permissions to binary installation directory (not `/usr/local/bin` without sudo)
- Semver tags are strictly enforced in release workflow
- Checksums are generated and uploaded reliably by CI/CD

### Residual Risks

- **No runtime integrity checks**: Once installed, binary is trusted until next update
- **Metadata tampering**: Release notes or version tags in API could mislead users (cosmetic only)
- **Homograph attacks**: If repository name contains Unicode lookalikes, API endpoint could be spoofed. **Mitigation**: Hard-code repository coordinates in binary

### Trade-offs

- **Increased binary complexity**: Update logic adds ~500-1000 LOC, testing surface, potential bugs
- **User autonomy**: Auto-install mode reduces user control (mitigated by default: notify-only)
- **Dependency on GitHub**: CLI becomes tightly coupled to GitHub infrastructure availability
- **Backup disk usage**: `.backup` files consume storage (mitigated by retention policy)

## Alternatives Considered

**Package Manager Delegation**
Rely on Homebrew, apt, yum, etc. for updates.

**Rejected**: Not all users install via package managers; custom install paths break assumptions.

**Notify-Only (No Auto-Install)**
Only notify users of new versions, require manual download.

**Rejected**: Doesn't reduce friction enough to justify implementation cost.

**Self-Extracting Updater**
Embed updater as separate binary inside `bar`.

**Rejected**: Complicates build; doesn't solve Windows executable lock problem.

**Container-Based Distribution**
Distribute via Docker images; updates are `docker pull`.

**Rejected**: Overhead for CLI users who want native binaries.

## Implementation Notes

- Add `cmd/bar/update.go` subcommand with check/install/rollback verbs
- Extract update logic into `internal/updater` package for testability
- Add integration tests that mock GitHub API responses
- Document update behavior in `bar help update` and README
- Add telemetry (opt-in) to track update success/failure rates

## Follow-Up

- Consider Sigstore integration for cryptographic signatures (ADR pending)
- Evaluate auto-update for plugins/extensions if ecosystem emerges
- Monitor update failure rates; add retry logic if >5% failure rate observed
