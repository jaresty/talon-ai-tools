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
