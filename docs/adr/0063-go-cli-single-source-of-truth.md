# ADR-0063 – Consolidate Go CLI with Talon Command Surface

Status: Superseded — Single-user workflow keeps Talon as the sole command surface
Date: 2025-12-31
Owners: Talon AI tools maintainers

---

## Superseding Decision (2026-01-06)

As the sole operator of this repository, I am deferring the Go CLI migration and keeping Talon as the primary executor. This simplifies maintenance and reduces operational overhead while preserving existing workflows.

- Keep Talon as the canonical command surface; defer building and packaging a separate Go binary.
- When CLI-style scripting is needed, expose a lightweight Python entry point that reuses the Talon modules instead of introducing a new stack.
- Rely on occasional manual smoke checks rather than parity SLO automation; document a simple manual fallback to the existing Talon handler.

These adjustments reflect the absence of multi-operator churn, the limited value of latency SLOs for a solo workflow, and the high cost of maintaining binary distribution mechanics. The original proposal remains below for historical context.

## Context

- Talon currently hosts the authoritative persona, intent, suggestion, and prompt grammar definitions used across GUIs, docs, and guardrails.
- Operators want a Go-based CLI that can be run interactively (TUI) or noninteractively (pipes) without duplicating the Talon command surface.
- The voice grammar today embeds source/destination stacks, provider orchestration, request gating, and guardrail messaging directly in Talon modules; the CLI will mirror core semantics while Talon adapters bridge Talon-only IO (selection, canvases, stack commands).
- Keeping Talon and the new CLI inside this repository preserves a single history, issue tracker, and shared `_tests/` harness (`python3 -m pytest`).
- Publishing a standalone binary and delegating Talon commands to it would let other environments reuse the tooling without importing Talon runtime modules.

---

## Problem

Maintaining two independent implementations of personas, prompt grammar, and guardrail commands would accelerate Concordance churn and risk behavioural drift. Today, Talon scripts (`GPT/gpt.py`, `lib/providerCommands.py`, Talon list generators) embed the command grammar directly. A separate Go CLI would need the same assets, validation rules, and tests. Without a shared source of truth:

- **Visibility**: personas, intents, and axis definitions would diverge between Python/Talon modules and Go packages, confusing downstream docs and guardrails.
- **Scope**: every grammar change would require coordinated edits across Talon, CLI, docs, and snapshot tests.
- **Volatility**: mismatch between Talon behaviour and CLI output would invalidate current `_tests` guardrails, multiplying regression risk.

---

## Hidden Domains and Concordance Analysis

### 1. Command Grammar & Persona Catalog Domain

- **Members (sample)**: `GPT/gpt.py::{_prompt_grammar,_suggest_prompt_text}`, `lib/personaCatalog.py`, `lib/axisCatalog.py`, Talon list generators under `GPT/lists/`, docs in `docs/readme-axis-cheatsheet.md`.
- **Visibility**: grammar helpers and persona catalogs remain embedded in Talon/Python modules; no reusable schema exists for other runtimes.
- **Scope**: modifying personas, intents, or axis metadata touches Talon lists, docs, tests, and help surfaces simultaneously.
- **Volatility**: churn surfaces across persona lists, docs, and guardrails whenever prompt recipes evolve.
- **Hidden tune**: *Prompt Grammar Source of Truth* — export neutral schemas and fixtures consumed by both Talon and the CLI.

### 2. Execution Surface Domain

- **Members (sample)**: Talon command scripts (`GPT/gpt.talon`, `GPT/gpt.py`), `lib/providerCommands.py`, potential Go `cli/internal/runner`, future TUI components.
- **Visibility**: Talon wraps command execution tightly with its runtime; there is no shared façade for external processes.
- **Scope**: implementing the same command set in Go risks duplicating provider orchestration, suggestion flows, and guardrails.
- **Volatility**: provider command surfaces change as models, destinations, and guardrails grow.
- **Hidden tune**: *Command Execution Adapter* — a single Go binary exposed via CLI/TUI and callable from Talon.

### 3. Testing & Release Domain

- **Members (sample)**: `_tests/`, `tests/`, `scripts/tools/`, future Go unit tests, release automation (`Makefile`, GitHub Actions).
- **Visibility**: Talon-focused tests run via `python3 -m pytest`; Go binaries would introduce new testing pathways and release steps.
- **Scope**: separate repositories would require duplicated fixtures, mocks, and release orchestration.
- **Volatility**: releases and guardrail updates already exercise complex CI flows.
- **Hidden tune**: *Unified Toolchain Harness* — extend the current test+release pipeline to cover the Go CLI without splitting repos.

---

## Decision (Original Proposal)

We establish the Go CLI as the canonical command surface while keeping Talon-first workflows equally privileged. This decision is anchored to four non-negotiable outcomes:

1. Language-neutral grammar, persona, and guardrail assets live in a single source that both Talon and the CLI consume without forked definitions.
2. Talon adapters delegate to the CLI only when the CLI satisfies the latency, availability, and telemetry thresholds published under **Parity Expectations**; they expose immediate downgrade paths whenever startup health probes fail or the binary is missing.
3. Validation, release, and telemetry flows treat Talon-bound and non-Talon operators as first-class consumers of the same command semantics.
4. Delegation detects missing network or provider access and reverts to the legacy executor with clear operator feedback; offline bundles cover binary/schema parity only and never imply successful runs without upstream model connectivity.

These outcomes allow non-Talon environments to reuse the command surface without sacrificing the responsiveness or reliability Talon users expect today.

---

## Verification Principle

> Every migration slice must demonstrate Talon↔CLI parity before the slice lands. The canonical validation command is `python3 -m pytest _tests/test_cli_talon_parity.py`, which exercises Talon adapters invoking the CLI alongside CLI-only entry points on the same machine. A failing parity command blocks the slice until red evidence is resolved and rerun green.

---

## Implementation Guardrails

- **Shared command assets**: Maintain a single, language-neutral schema for personas, intents, axes, and prompt grammar. Talon, the CLI, docs, and guardrails must generate their artefacts from that schema rather than bespoke definitions.
- **CLI foundation**: Develop the Go CLI within this repository so interactive (TUI) and noninteractive flows remain aligned with Talon behaviour. The CLI owns command parsing and execution while exposing clean APIs for adapters.
- **Hermetic verification**: Parity tests and health probes rely on recorded fixtures and mocks; no automated test contacts live providers, LLMs, or ChatGPT endpoints.
- **Adapter commitments**: Talon adapters delegate through the CLI only when parity is demonstrated. They run a startup health probe (`cli --health`), enforce the latency and availability SLOs defined under **Parity Expectations**, and revert to the legacy executor after `FAILURE_THRESHOLD=3` consecutive probe or invocation failures while emitting operator-facing alerts.
- **Shared contracts**: Provider metadata, request gating, session persistence, attachment handling, and telemetry formats stay canonical across runtime boundaries. Any change to these contracts ships once and must be consumable by both surfaces.
- **Delivery posture**: Releases, artefacts, and telemetry rollups continue to originate from this repository. Each release publishes signed binaries plus a checksum manifest that Talon verifies on startup before delegation, eliminating additional tooling burden for Talon users.

---

## Shared Contracts

Single, auditable definitions govern the following domains, and any change must be consumable by Talon and the CLI simultaneously:

- Persona, intent, suggestion, and prompt grammar semantics (tokens, caps, canonical forms).
- Provider registry metadata, capability flags, and request-gating rules.
- Session, attachment, telemetry, and history payload schemas, including versioning and retention expectations.
- Error taxonomy, exit-code mappings, and configuration precedence.

## Parity Expectations

- Published SLOs hold: delegated commands complete within `p50 ≤ 400 ms` and `p95 ≤ 1200 ms` on the reference workstation, and the rolling 24 h success rate stays above `99%`. Adapters compute these metrics locally, log them for the operator, and disable delegation automatically whenever a threshold is breached.
- Network connectivity to the configured provider endpoints (e.g., ChatGPT) is mandatory; adapters surface connectivity failures immediately, record them in local telemetry, and disable delegation until connectivity returns.
- The CLI enforces the same semantics, limits, and guardrails that Talon enforces today; deviations are treated as regressions.
- Talon adapters translate ergonomic voice inputs and UI affordances into CLI commands without regressing latency, reliability, or accessibility.
- Non-Talon operators receive the identical command surface, artefacts, and telemetry emitted for Talon workflows, enabling downstream tooling to trust a single canonical format.
- Feature flags, health checks, and telemetry instrumentation provide early warning and automatic fallback whenever parity is at risk.
- Schema stewards (Talon AI tools maintainers) approve contract changes before either runtime consumes them, ensuring assets remain in lockstep.

## Adapter Responsibilities

Talon adapters must:

- Accept voice grammar inputs, selections, and destination intents, mapping them to CLI-friendly payloads while preserving Talon accessibility affordances.
- Capture CLI stdout/stderr/exit codes, converting outcomes into Talon guardrail notifications and locally persisted Concordance telemetry that reports against the published SLOs without relying on centralized services.
- Manage temporary resources inside a user-scoped cache directory, scrubbing attachments, session files, and clipboard artefacts after each invocation; credentials never leave Talon’s secure store.
- Detect CLI absence, version drift, or performance regressions; after `FAILURE_THRESHOLD=3` consecutive issues the adapter emits a Talon notification, disables delegation, and replays the legacy executor automatically.

---

## Operational Mitigations

- **Configuration & credentials**: map existing Talon settings/env vars into CLI config precedence, validate credential presence early, and warn when migration is needed.
- **Session lifecycle**: document JSON/TOML schema, version markers, locking strategy, and reconnection rules; enforce cleanup on abnormal exits.
- **Performance & latency**: run daemon mode by default for Talon delegation; the CLI exposes `--health` and `--warm-cache` commands that adapters use at startup to satisfy latency budgets and benchmark cold vs. warm invocations before flipping defaults.
- **Version compatibility**: embed semantic version + capability list in CLI handshake; adapters negotiate and refuse unsupported features with explicit fallbacks.
- **Testing strategy**: add golden transcript tests for CLI stdout/stderr, attachment fixtures, and session persistence across restarts; run both CLI and legacy paths in CI during migration.
- **Distribution & updates**: define signature verification, notarization (macOS), auto-update prompts inside Talon, and manual override instructions for offline setups.
- **Offline readiness**: publish a bundled update path (CLI binary + schema assets + checksums) that Talon can verify and install locally when the machine lacks network access, while clearly signalling that upstream provider connectivity remains required for command execution.
- **Deferred hardening** *(future ADRs)*: advanced threat assessments, privacy redaction policies, third-party plugin support.

---

## Consequences

- **Positive**: eliminates duplicate command grammar definitions, enables automation-friendly CLI usage, and keeps Concordance guardrails aligned across Talon and non-Talon surfaces.
- **Risks**: Talon dependency on an external binary introduces latency, error-handling, packaging, and IO surface complexity; mapping Talon-exclusive interactions (selection, canvases, provider canvases) to CLI outputs may degrade UX if underspecified; Go runtime requirements must be managed for contributors.
- **Mitigations**: maintain a fallback adapter during rollout, add telemetry to detect CLI/Talon mismatches, flesh out the IO parity matrix before delegating commands, validate session/config migration and credential configuration up front, negotiate CLI version/capabilities at startup, and use CI to enforce schema/fixture synchronization across shared guardrails.

---

## Salient Tasks

- Stand up shared schema assets with generation scripts for Talon and CLI consumers, and document maintainer sign-off for contract changes.
- Land `_tests/test_cli_talon_parity.py` plus recorded fixtures that exercise Talon adapters and CLI-only entry points without contacting live providers; keep the command green in CI.
- Implement adapter health probes, latency/availability telemetry, and automatic fallback after `FAILURE_THRESHOLD=3` consecutive issues.
- Extend CI releases to produce signed binaries and checksum manifests consumed by Talon’s startup verifier; fail builds when the manifest is missing.
- Make daemon mode the default delegation path, wiring Talon startup to call `cli --health` and `cli --warm-cache` before enabling delegation.
- Publish the offline update bundle (binary + schema + checksums) and document the operator workflow for installing it without network access.
- Update onboarding material for Talon operators and CLI-first users to explain delegation, fallback signals, and manual recovery.

