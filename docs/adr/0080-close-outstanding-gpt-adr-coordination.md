
# 080 – Coordination plan to close outstanding GPT surface ADRs

Status: In Progress
Date: 2026-01-12
Updated: 2026-02-11
Owners: GPT Surface Coordination Pod

## Context
- ADR-0057 (paste destinations & response canvas alignment) remains in "Proposed" status because the streaming reminder toast, `model pass response` grammar coverage, and help-surface copy have not shipped.
- ADR-0073 (CLI discoverability and surface parity) has no implementation yet: the CLI still displays legacy usage text and lacks shared `--no-input` / `--plain` handling, concise help entry points, and automation-focused validation.
- ADR-035 (Talon busy tag to block GPT runs) still needs a grammar-level guard; only the Python `_reject_if_request_in_flight` helper prevents overlapping runs, leaving noisy drop notifications and repeated recognitions.
- ADR-054 (source-agnostic GPT presets) landed its runtime changes but still requires doc/help surface regeneration to advertise the new `model run … preset …` command path.
- Each ADR was scoped independently, but the remaining work clusters around a common theme: polishing GPT request ergonomics across voice, canvas, and CLI surfaces.

## Problem
- Without a shared plan, the residual tasks keep aging in "Proposed" status, and downstream teams lack clarity on sequencing, owners, or validation targets.
- The outstanding items affect user trust (duplicate run notifications), discoverability (CLI help), and parity between documented and live behaviours (preset commands, canvas reminders).
- We need a coordinated push that schedules the remaining work, defines acceptance evidence, and codifies dependencies so each ADR can be closed with confidence.

## Decision
- Establish a single coordination effort that stages the remaining work into four focused workstreams, each aligned to an open ADR but tracked under this coordination document.
- Assign workstream leads and explicit validation targets, with weekly check-ins during the execution window.
- Treat ADR closure criteria as non-negotiable exit gates: each workstream reports back with evidence (code diffs, tests, guardrail regen) that demonstrates the ADR's decision has been fully delivered.
- Bundle cross-cutting doc/help updates into a shared documentation refresh sprint to avoid repeated guardrail regeneration.

## Workstreams

### 1. ADR-0057: Canvas reminder & grammar parity

**Completed (as of 2026-02):**
- Pill dual-action affordance with "Show response" button implemented (`lib/pillCanvas.py`).
- Shared `prepare_destination_surface` helper in `lib/modelDestination.py` for focus re-check before paste.
- `paste response` command wired in `GPT/gpt-confirmation-gui.talon`.
- Tests covering destination promotion and pill/canvas toggling.

**Remaining:**
- Implement delayed streaming reminder toast referencing `model show response` (Request UI controller + notification helpers).
- Add `model pass response` (and related variants) to Talon grammar, delegating to existing paste destination logic.
- Refresh help surfaces (Help Hub, quickstart) to mention the toast, pill affordance, and explicit follow-up commands.
- Validation: `python3 -m pytest` suites covering request UI, grammar guardrails, plus regenerated documentation snapshots.

### 2. ADR-0073: CLI discoverability upgrade

**Completed:** ADR documented only.

**Remaining (all items outstanding):**
- Introduce concise top-level help output and short usage hints when running `bar` with no subcommand.
- Implement global `--no-input` and `--plain` flags, propagating through build, preset, and TUI entry points.
- Implement `--command` flag for `bar tui` (documented in ADR but not yet in Config struct).
- Update Go tests to cover help output, flag validation, and automation pathways; refresh README/help text accordingly.
- Validation: `go test ./cmd/bar ./internal/barcli`, regenerated CLI docs, and updated quickstart snippets.

### 3. ADR-035: Grammar-level busy gating

**Completed:** ADR documented only.

**Remaining (all items outstanding):**
- Define `tag: gpt_busy`, toggle it when the request lifecycle enters/leaves active states, and scope run grammars to `not gpt_busy`.
- Keep non-run commands (help, canvas controls) available by isolating their contexts from the new tag.
- Add startup/reload tag cleanup to prevent stranded tags on Talon reload.
- Add telemetry/log hooks to confirm reduced duplicate-run notifications.
- Validation: Talon grammar smoke checks, updated unit tests ensuring busy tag toggles, and a short usability capture demonstrating silent suppression of duplicate commands.

### 4. ADR-054: Documentation close-out

**Completed (as of 2026-01):**
- `model run [source] [destination] preset <name>` grammar and `gpt_run_preset_with_source` action implemented.
- Source-agnostic preset execution with cleared source cache on preset runs.
- Legacy `model preset run` alias removed.
- 81 regression tests added covering preset behavior.

**Remaining:**
- Regenerate Help Hub, quickstart, and guardrail artefacts to reference `model run [source] [destination] preset <name>`.
- Audit README/CLI docs for any remaining legacy `model preset run` references.
- Validation: guardrail regeneration (`make axis-guardrails-ci`), doc diff review, and confirmation from support docs owners.

## Execution Timeline

The original 5-week window (starting 2026-01-12) has elapsed. Revised schedule:

- **Now – Week 1**: Complete Workstream 1 remaining items (toast + `model pass response` grammar) and Workstream 4 docs regeneration.
- **Weeks 2–3**: Implement Workstreams 2 and 3 (CLI flags, busy tag).
- **Week 4**: Integration, validation evidence collection, doc refresh.
- **Week 5 (close-out)**: Review outcomes, archive work logs, update ADR statuses to "Accepted".

## Dependencies & Risks
- Guardrail regeneration is shared across Workstreams 1 and 4; coordinate to avoid conflicting snapshots.
- Implementing the busy tag requires careful Talon reload handling to prevent stranded tags; include QA time for reload/resume scenarios.
- CLI help restructuring may ripple through existing documentation; involve docs maintainers early to manage tone/format changes.
- Delaying doc refresh (Workstream 4) blocks final acceptance of ADR-054; sequence runtime updates ahead of documentation work to keep momentum.

## Validation & Reporting
- Each workstream maintains a work log entry referencing this ADR (080) with validation commands, artifacts, and rollback plans.
- Weekly coordination notes capture progress, blockers, and updated timelines; publish summaries in the GPT surface channel.
- On completion, update ADR-0057, ADR-0073, ADR-035, and ADR-054 statuses to "Accepted", linking to the relevant work logs and validation evidence.
- Archive this coordination ADR as "Accepted" once all dependent ADRs are closed and evidence is recorded.
