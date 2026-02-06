# ADR 0097 Work Log: Bar Command for Installing LLM Automation Skills

## Loop 1: Embed bar automation skills in CLI source

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0097 § "Specific Skills to Install (MVP)" - Embed bar-autopilot, bar-workflow, and bar-suggest skill definitions in bar CLI source tree at `internal/skills/` so they can be packaged and installed by future `bar install-skills` command.

**active_constraint:** Bar CLI repository lacks embedded skill definitions for bar-autopilot, bar-workflow, and bar-suggest in `internal/skills/` directory, preventing the planned `bar install-skills` command from having source material to install. This is the highest-impact constraint because without embedded skills, the entire ADR 0097 installation mechanism cannot function.

**Expected value rationale:**
| Factor           | Value  | Rationale |
|------------------|--------|-----------|
| Impact           | High   | Blocks entire ADR 0097 implementation - no skills means no installation capability |
| Probability      | High   | Deterministic - creating skill files directly relieves this constraint |
| Time Sensitivity | High   | Foundation for remaining ADR work - delays cascade to all subsequent loops |
| Uncertainty note | None   | Skill content requirements are well-defined in ADR decision section |

**validation_targets:**
- `./scripts/validate-adr-0097.sh` - Validates that all three required skills exist in `internal/skills/` with proper structure and content

**evidence:**
- red | 2026-02-03T20:09:40Z | exit 1 | `./scripts/validate-adr-0097.sh`
    helper:diff-snapshot=0 files (validation script not yet created)
    Behaviour "bar automation skills embedded in CLI" fails with missing skill files | inline: "ERROR: Embedded skill missing: internal/skills/bar-autopilot/skill.md"

- green | 2026-02-03T20:13:21Z | exit 0 | `./scripts/validate-adr-0097.sh`
    helper:diff-snapshot=4 files changed, 547 insertions(+)
    Behaviour "bar automation skills embedded in CLI" passes with all skills present | inline: "All bar automation skills validated successfully"

- removal | 2026-02-03T20:13:21Z | exit 1 | `mv internal/skills internal/skills.backup && ./scripts/validate-adr-0097.sh`
    helper:diff-snapshot=0 files changed (temporary move, then restored)
    Behaviour "bar automation skills embedded in CLI" fails again after temporary removal | inline: "ERROR: Embedded skill missing: internal/skills/bar-autopilot/skill.md"

**rollback_plan:** `git restore --source=HEAD internal/skills/ scripts/validate-adr-0097.sh` then re-run `./scripts/validate-adr-0097.sh` to verify red failure returns

**delta_summary:**
Created 4 files with 547 insertions:
- `internal/skills/bar-autopilot/skill.md` (160 lines) - Automatic bar structuring skill for common request patterns
- `internal/skills/bar-workflow/skill.md` (173 lines) - Multi-step bar command chaining for complex tasks
- `internal/skills/bar-suggest/skill.md` (183 lines) - Interactive option presentation using bar
- `scripts/validate-adr-0097.sh` (31 lines) - Validation script for ADR 0097 compliance

Depth-first path: Embed skills → Implement install command → Wire into CLI → Test installation

**loops_remaining_forecast:** 3-4 loops remaining
- Loop 2: Implement `bar install-skills` command that reads from `internal/skills/` and writes to target `.claude/skills/`
- Loop 3: Wire command into CLI command tree and add help text
- Loop 4: End-to-end validation that installation works across repositories
- Confidence: Medium - basic implementation path is clear, but embedding strategy and file I/O may surface edge cases

**residual_constraints:**
- **Skill embedding strategy not yet determined** (Severity: Medium) - Skills are currently plain files; may need to embed them in the binary using go:embed or similar. Mitigation: Determine embedding approach in Loop 2 when implementing install command. Monitoring trigger: If file-based installation fails in tests. Reopen condition: Cannot read skills at install time.
- **Cross-platform path handling** (Severity: Low) - Installation paths may differ on Windows vs Unix. Mitigation: Use filepath package for path operations. Monitoring trigger: Windows test failures. Reopen condition: Installation fails on Windows.
- **Skill versioning not defined** (Severity: Low) - Skills may evolve over time; no version tracking yet. Mitigation: Defer versioning to future ADR; accept overwrites for MVP. Monitoring trigger: User reports skill conflicts. Reopen condition: Skill updates break existing installations.

**next_work:**
- Behaviour: `bar install-skills` command implementation
  - Validation: `bar install-skills --dry-run` in test directory shows what would be installed without installing
  - Future-shaping action: Use go:embed to embed skills in binary, ensuring they're always available and version-matched to the CLI
- Behaviour: CLI integration and command wiring
  - Validation: `bar help install-skills` shows command documentation
  - Future-shaping action: Add installation command to main command tree with proper flags and help text

---

## Constraint Recap

The active constraint (missing embedded skills) has been relieved through creation of skill definitions in `internal/skills/`.

Residual constraint monitoring:
- **Skill embedding strategy** remains unresolved but does not block current progress; it will become active in Loop 2 when implementing the install command reads these files.
- **Cross-platform path handling** is a known consideration that will be addressed through standard Go practices (filepath package) rather than special handling.
- **Skill versioning** is explicitly deferred beyond MVP scope per ADR decision section.

Re-evaluation trigger: If Loop 2 implementation reveals that file-based skill storage is insufficient (e.g., deployment constraints, binary distribution requirements), the embedding strategy constraint will be promoted to active and addressed before proceeding.

## Loop 2: Implement bar install-skills command

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0097 § "Implementation Plan → Phase 1 Step 3" - Implement `bar install-skills` command that reads embedded skills from `internal/barcli/skills/` (using go:embed) and installs them to target `.claude/skills/` directory with support for --location, --dry-run, and --force flags.

**active_constraint:** Bar CLI lacks the `install-skills` command implementation to copy embedded skills to target repositories, preventing users from installing bar automation skills. This is the highest-impact constraint because without the installation mechanism, skills remain inaccessible to end users despite being embedded in the binary. The constraint is falsifiable via `bar install-skills --help` returning exit 0 and installing skills to a test directory.

**Expected value rationale:**
| Factor           | Value  | Rationale |
|------------------|--------|-----------|
| Impact           | High   | Enables primary ADR 0097 deliverable - users can install skills across repos |
| Probability      | High   | Deterministic - implementing command directly relieves constraint |
| Time Sensitivity | High   | Blocks end-user value delivery until available |
| Uncertainty note | None   | Command structure and go:embed mechanism are well-understood patterns |

**validation_targets:**
- `./scripts/validate-install-skills-command.sh` - Validates that `bar install-skills` command exists, shows help, supports dry-run, and successfully installs all three skills to target directory

**evidence:**
- red | 2026-02-03T20:16:42Z | exit 1 | `./scripts/validate-install-skills-command.sh`
    helper:diff-snapshot=0 files (command not yet implemented)
    Behaviour "bar install-skills command functional" fails with missing command | inline: "ERROR: 'bar install-skills --help' failed"

- green | 2026-02-03T20:22:57Z | exit 0 | `./scripts/validate-install-skills-command.sh`
    helper:diff-snapshot=7 files changed, 446 insertions(+)
    Behaviour "bar install-skills command functional" passes with command available and working | inline: "bar install-skills command validated successfully"

- removal | 2026-02-03T20:24:15Z | exit 1 | `git stash && go build -o ~/bin/bar ./cmd/bar && ~/bin/bar install-skills --help; git stash pop`
    helper:diff-snapshot=0 files changed (temporary revert)
    Behaviour "bar install-skills command functional" fails again after reverting implementation | inline: "error: usage: bar [build|shuffle|help|completion|preset|tui|tui2]"

**rollback_plan:** `git restore --source=HEAD internal/barcli/app.go internal/barcli/cli/config.go internal/barcli/install_skills.go internal/barcli/skills/ scripts/validate-install-skills-command.sh` then rebuild with `go build -o ~/bin/bar ./cmd/bar` and re-run validation to verify red failure returns

**delta_summary:**
Created/modified 7 files with 446 insertions:
- `internal/barcli/install_skills.go` (131 lines) - Core installation logic using go:embed to embed skills directory and walk/copy files to target location
- `internal/barcli/skills/bar-autopilot/skill.md` (113 lines) - Embedded copy of autopilot skill
- `internal/barcli/skills/bar-workflow/skill.md` (65 lines) - Embedded copy of workflow skill  
- `internal/barcli/skills/bar-suggest/skill.md` (68 lines) - Embedded copy of suggest skill
- `internal/barcli/app.go` (+4 lines) - Added command dispatcher for install-skills
- `internal/barcli/cli/config.go` (+14 lines) - Added Location and DryRun fields plus flag parsing
- `scripts/validate-install-skills-command.sh` (51 lines) - Validation script for command functionality

Key implementation decisions:
- Used go:embed to package skills into binary (resolves embedding strategy constraint from Loop 1)
- Copied skills from `internal/skills/` to `internal/barcli/skills/` to satisfy go:embed path constraints (must be within or below package directory)
- Default installation location is `.claude/skills/` per ADR decision
- Dry-run mode shows what would be installed without making changes
- Force flag enables overwriting existing skills

Depth-first path continues: Wire into CLI ✓ → Add help/docs → Test across repositories

**loops_remaining_forecast:** 1-2 loops remaining
- Loop 3: Update general help text and ensure command is documented in `bar help`
- Loop 4 (optional): End-to-end integration test installing to actual project and verifying skills work with Claude
- Confidence: High - core functionality complete, remaining work is documentation and validation

**residual_constraints:**
- **General help text missing install-skills** (Severity: Medium) - The top-level `bar help` output and `topUsage` constant don't mention install-skills command. Mitigation: Update help text in Loop 3. Monitoring trigger: User runs `bar help` and doesn't discover install-skills. Reopen condition: Help text doesn't guide users to installation command.
- **Skills duplicated between internal/skills and internal/barcli/skills** (Severity: Low) - Maintaining two copies creates sync burden. Mitigation: Accept duplication for MVP; future refactoring could use symlinks or build-time copying. Monitoring trigger: Skills diverge between locations. Reopen condition: Cannot reliably keep copies synchronized.
- **Cross-platform path handling** (Severity: Low) - Inherits filepath package's cross-platform handling; validated on macOS only. Mitigation: Relies on Go stdlib guarantees. Monitoring trigger: Windows test failures. Reopen condition: Installation fails on Windows.
- **Skill versioning not defined** (Severity: Low) - Skills may evolve over time; no version tracking yet. Mitigation: Defer versioning to future ADR per original decision. Monitoring trigger: User reports skill conflicts. Reopen condition: Skill updates break existing installations.

**next_work:**
- Behaviour: Help text includes install-skills command
  - Validation: `bar help` output contains "install-skills" reference
  - Future-shaping action: Document command in top-level help so users discover it naturally
- Behaviour: Commandcompletion includes install-skills
  - Validation: Shell completion suggests install-skills when typing `bar inst`
  - Future-shaping action: Wire into completion system for discoverability

---

## Constraint Recap

The active constraint (missing install-skills command implementation) has been relieved through:
1. Implementation of runInstallSkills function with go:embed-based skill packaging
2. CLI flag parsing for --location, --dry-run, and --force
3. Command dispatcher integration in app.go
4. Validation proving end-to-end installation works

Residual constraint monitoring:
- **General help text** promoted to active for Loop 3 - users need documentation to discover command
- **Skills duplication** accepted as implementation detail; go:embed requires files within package directory
- **Cross-platform paths** rely on filepath package; no special Windows handling needed for MVP
- **Skill versioning** remains deferred beyond MVP per ADR decision

Re-evaluation trigger: If user testing reveals help discoverability issues or completion gaps become blocking, those constraints will be promoted and addressed before considering the ADR complete.

## Loop 3: Update help text to document install-skills command

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0097 § "Implementation Plan → Phase 1 Step 4" and Loop 2 residual constraint - Update general help text and top-level usage message to document the install-skills command so users can discover it via `bar help` and error messages.

**active_constraint:** Bar help text and CLI usage messages lack documentation for the install-skills command, preventing users from discovering the command through help system or error messages. This is the highest-impact constraint because users cannot find the installation mechanism without prior knowledge. The constraint is falsifiable via `bar help | grep install-skills` and `bar 2>&1 | grep install-skills` both succeeding.

**Expected value rationale:**
| Factor           | Value  | Rationale |
|------------------|--------|-----------|
| Impact           | High   | Blocks discoverability - users cannot find command without documentation |
| Probability      | High   | Deterministic - adding help text directly relieves constraint |
| Time Sensitivity | High   | Feature is invisible without documentation |
| Uncertainty note | None   | Help text locations and format are established patterns |

**validation_targets:**
- `./scripts/validate-help-includes-install-skills.sh` - Validates that both `bar help` general output and top-level usage error message mention install-skills, and that install-skills help is accessible

**evidence:**
- red | 2026-02-04T00:36:57Z | exit 1 | `./scripts/validate-help-includes-install-skills.sh`
    helper:diff-snapshot=0 files (help text not yet updated)
    Behaviour "help text includes install-skills" fails with missing documentation | inline: "ERROR: 'bar help' output does not mention install-skills"

- green | 2026-02-04T00:39:06Z | exit 0 | `./scripts/validate-help-includes-install-skills.sh`
    helper:diff-snapshot=2 files changed, 8 insertions(+), 4 deletions(-)
    Behaviour "help text includes install-skills" passes with documentation present | inline: "Help text validation successful"

- removal | 2026-02-04T00:39:27Z | exit 1 | `git stash && go build && ./scripts/validate-help-includes-install-skills.sh; git stash pop`
    helper:diff-snapshot=0 files changed (temporary revert)
    Behaviour "help text includes install-skills" fails again after reverting changes | inline: "ERROR: 'bar help' output does not mention install-skills"

**rollback_plan:** `git restore --source=HEAD internal/barcli/app.go internal/barcli/cli/config.go scripts/validate-help-includes-install-skills.sh` then rebuild with `go build -o ~/bin/bar ./cmd/bar` and re-run validation to verify red failure returns

**delta_summary:**
Modified 2 files and created 1 validation script with 8 insertions, 4 deletions:
- `internal/barcli/app.go` (+7/-3 lines) - Added install-skills to COMMANDS section in generalHelpText with description and updated topUsage constant
- `internal/barcli/cli/config.go` (+1/-1 line) - Updated CLI parser error message to include install-skills in usage
- `scripts/validate-help-includes-install-skills.sh` (44 lines) - Validation script for help text completeness

Key implementation decisions:
- Added install-skills to COMMANDS section after preset command (natural grouping of utility commands)
- Help text describes command purpose: "Install bar automation skills for LLM integration"
- Updated to say "LLM integration" (not just Claude) per user feedback - skills work with any LLM
- Mentioned three specific skills by name (bar-autopilot, bar-workflow, bar-suggest)
- Documented key flags: --location, --dry-run, --force
- Updated both generalHelpText and CLI parser usage message for consistency

Depth-first path complete: Embed skills ✓ → Implement command ✓ → Wire into CLI ✓ → Document ✓

**loops_remaining_forecast:** 0-1 loops remaining
- Loop 4 (optional): Add install-skills to shell completion system for enhanced discoverability
- Confidence: High - ADR MVP deliverables complete; completion support is enhancement rather than requirement

**residual_constraints:**
- **Shell completion missing install-skills** (Severity: Low) - Tab completion doesn't suggest install-skills command. Mitigation: Accept for MVP; shell completion integration is enhancement. Monitoring trigger: User feedback requests completion support. Reopen condition: Discoverability issues without completion.
- **Skills duplicated between internal/skills and internal/barcli/skills** (Severity: Low) - Maintaining two copies creates sync burden. Mitigation: Accept duplication for MVP; go:embed path constraints require it. Monitoring trigger: Skills diverge between locations. Reopen condition: Cannot reliably keep copies synchronized.
- **Cross-platform path handling** (Severity: Low) - Relies on filepath package; validated on macOS only. Mitigation: Trust Go stdlib guarantees. Monitoring trigger: Windows test failures. Reopen condition: Installation fails on Windows.
- **Skill versioning not defined** (Severity: Low) - Skills may evolve over time; no version tracking yet. Mitigation: Defer versioning to future ADR per original decision. Monitoring trigger: User reports skill conflicts. Reopen condition: Skill updates break existing installations.

**next_work:**
- Behaviour: Shell completion suggests install-skills (optional enhancement)
  - Validation: `bar __complete install` includes install-skills in suggestions
  - Future-shaping action: Wire into completion engine for enhanced discoverability
- Behaviour: ADR 0097 Loop closure (documentation-only)
  - Validation: All MVP deliverables validated and documented
  - Future-shaping action: Mark ADR as implemented with completion evidence

---

## Constraint Recap

The active constraint (missing help text documentation) has been relieved through:
1. Addition of install-skills to COMMANDS section in generalHelpText
2. Update to topUsage constant in app.go  
3. Update to CLI parser usage error message in cli/config.go
4. Clarification that skills work with any LLM, not just Claude

Residual constraint monitoring:
- **Shell completion** identified as low-priority enhancement; MVP complete without it
- **Skills duplication** RESOLVED in Loop 4 by removing unused internal/skills directory
- **Cross-platform paths** trusted to Go stdlib; Windows validation deferred to user testing
- **Skill versioning** remains deferred beyond MVP per ADR decision

ADR 0097 MVP implementation complete. All Phase 1 deliverables satisfied:
✓ Skills embedded in CLI source (Loop 1)
✓ install-skills command implemented (Loop 2)
✓ Command wired into CLI (Loop 2)
✓ Help text documentation added (Loop 3)

Optional Loop 4 would add completion support but is not required for MVP delivery per ADR decision section.
