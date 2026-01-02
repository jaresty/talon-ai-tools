# ADR-0063 – Consolidate Go CLI with Talon Command Surface

Status: Proposed — Go CLI and Talon command sets share a single repo
Date: 2025-12-31
Owners: Talon AI tools maintainers

---

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

## Decision

We will build the Go CLI inside this repository and treat it as the authoritative command implementation. Talon modules will shell out to the binary (or call its APIs) so the CLI owns:

1. Shared persona, intent, suggestion, and prompt schemas delivered as language-neutral assets.
2. Command execution logic exposed through both TUI and noninteractive CLI entry points.
3. Shared guardrail contracts (provider registry, request gating, drop-reason messaging) defined once and consumed by both runtimes, with a slimmed CLI IO surface.
4. Talon-only IO (selection, stack destinations, canvases) handled in adapter layers that translate to the CLI’s neutral inputs/outputs.
5. Integration tests that run from this repo’s existing harness to keep Talon and CLI behaviour aligned.
6. Release artifacts (signed binaries, checksums) generated from the same CI workflows, keeping docs and guardrails in sync.

Talon code will gradually migrate to delegating through adapters rather than maintaining parallel logic.

---

## Tests-First Principle

> Each migration slice will extend or add tests before wiring new adapters. Existing `_tests/` guardrails stay canonical; Go packages add Go-native unit tests, while end-to-end command snapshots run via `python3 -m pytest` helpers that spawn the CLI. No behaviour lands without cross-runtime coverage.

---

## Implementation Plan (Prior Art Aligned)

### 1. Shared Command Grammar Assets

- **Original Draft**: expose personas, intents, axes, and prompt grammar as reusable data for both Talon and the CLI.
- **Similar Existing Behavior**: `GPT/gpt.py`, `lib/personaCatalog.py`, and Talon list generators already materialize canonical lists for docs/tests.
- **Revised Recommendation**:
  - Create a `shared/command-schema/` (name TBD) containing JSON/YAML fixtures or compiled assets that describe personas, intents, grammar tokens, and prompt templates.
  - Generate Talon lists, docs, and CLI bindings from those assets (potentially via existing list generation scripts).
  - Add tests asserting the schema round-trips into both Talon and CLI helpers without drift.

### 2. Go CLI Core

- **Original Draft**: new Go codebase supporting interactive TUI and scriptable CLI flows.
- **Similar Existing Behavior**: Talon command handlers (`lib/providerCommands.py`, `GPT/gpt.py`) execute prompts, suggestions, personas, and guardrails.
- **Revised Recommendation**:
  - House Go code under `cli/` with modules for command parsing, prompt execution, session history, and TUI rendering.
  - Introduce adapters that load the shared schema assets at runtime.
  - Provide Go unit tests using the shared fixtures plus integration tests that emit the same transcripts guarded by `_tests` fixtures.

### 3. Shared IO & Guardrail Contracts

- **Original Draft**: keep Talon-specific IO (selection, clipboard, canvases) and guardrail messaging local while CLI focuses on prompts.
- **Similar Existing Behavior**: `lib/modelSource.py`, `lib/modelDestination.py`, `lib/providerCommands.py`, and `GPT/gpt.py` encode source stacks, destination routing, provider registry flows, request gating, and drop-reason telemetry.
- **Revised Recommendation**:
- Extract neutral definitions for provider metadata, request gating rules, and drop-reason messages so both Talon and the CLI load identical guardrails.
- Define a limited CLI IO contract (stdin/stdout, files, optional clipboard bridges) and document how Talon adapters translate richer voice commands (sources, stack destinations, canvases) into those primitives.
- Standardise session persistence (named sessions, state files/IPC) so daemon, TUI, and batch modes share provider/stance/recipe context; document file formats, versioning, locking, and reconnection/fallback behaviour when sessions are missing or incompatible.
- Extend Concordance guardrails and history persistence helpers to operate on the shared schema, ensuring the CLI can raise the same errors, handle attachments, and write identical telemetry artifacts even when Talon handles the UI-specific work.


### 4. Talon Adapter Layer

- **Original Draft**: Talon shells out to the CLI instead of duplicating logic.
- **Similar Existing Behavior**: current Talon actions call Python helpers that in turn orchestrate providers.
- **Revised Recommendation**:
  - Add a configurable shim (`lib/providerCommands.py` or new module) that invokes the CLI binary (or its daemon mode) and marshals responses back into Talon surfaces.
  - Retain a feature flag to fall back to the legacy path until parity is proven through guardrails.
  - Update `_tests/` to cover both code paths during the transition.

### 5. Release & Distribution

- **Original Draft**: publish binaries while keeping repo as single source.
- **Similar Existing Behavior**: GitHub Actions and `Makefile` scripts already build docs, guardrails, and Python packages.
- **Revised Recommendation**:
  - Extend CI to build, sign, and attach Go binaries (macOS, Linux, Windows) to releases.
- Include checksum/manifest files consumed by Talon installers and external tooling.
- Document installation and Talon delegation flows in the repo README/docs, including version negotiation and auto-update guidance for Talon adapters.


---

## Shared Contracts and Parity Guidance

### Shared Contracts Requiring Parity

- Persona, intent, suggestion, and prompt grammar schemas (axis tokens, caps, canonicalisation rules).
- Provider registry metadata, capability flags, and default model selection rules.
- Request gating states, drop-reason identifiers/messages, and Concordance guardrails.
- Suggestion JSON schema, prompt recap metadata, and history snapshot headers.
- Telemetry/export formats consumed by docs, guardrail tests, and history tooling.
- CLI stdout JSON contract (fields such as `notify`, `debug`, `status`, `error`, `severity`, `alert`, `breadcrumbs`) consumed by Talon adapters.
- Session state schema (provider selection, persona/intent stance, recipe snapshots, last responses) with versioning and concurrency hints.
- Attachment payload formats (text/image/audio/other binary descriptors) including size/streaming limits and capability requirements.
- Error taxonomy, exit-code mapping, and structured stderr logs recognised by Talon guardrails.
- Configuration migration rules (Talon settings → CLI config/env) to keep defaults in sync.

### CLI↔Talon Parity Matrix

| Area | CLI responsibility | Talon adapter responsibility | Notes |
| --- | --- | --- | --- |
| Prompt grammar & axis tokens | Parse persona/intent + axis arguments; enforce caps and canonical tokens | Surface voice grammar, validate spoken aliases before invoking CLI | CLI emits same recipe snapshots used by guardrails |
| Suggest command (`model run suggest`) | Produce suggestion JSON using shared schema; expose stdin/stdout toggles | Map current selection/context into CLI inputs; render suggestion GUI from CLI output | GUI rendering stays Talon-side |
| Attachments (images, files) | Accept structured attachment descriptors (inline base64 or file paths), enforce provider capability checks, include in API requests | Convert Talon clipboard/images into temp files or descriptors; clean up and render responses | Same schema applies to standalone CLI users |
| Provider management | Load shared registry, switch providers/models, report status JSON | Convert voice commands to CLI subcommands; display provider canvas using CLI data | CLI exposes machine-readable status |
| Persona/intent presets | Normalize preset keys, apply to system prompt state, return summaries | Handle spoken aliases and GUI notifications | Notifications remain Talon responsibility |
| Source selection | Support neutral sources (stdin, file, clipboard snapshot flag) | Translate Talon sources/stacks into temp files/stdin payloads; restore clipboard/selection after run | Stack semantics stay Talon-side |
| Destination handling | Emit response text/meta to stdout/files | Route CLI output into Talon destinations (paste, browser, history canvas) | Talon decides UI insertion |
| History persistence | Generate canonical snapshot payloads (recipe, axes, persona headers) | Call CLI in file mode or consume payload to write Talon history files | Edition ensures guardrail parity |
| Debug/telemetry | Expose structured logs, request/response dumps, and drop reasons | Surface in Talon debug canvases and notifications | Shared format simplifies tests |
| Error handling & exit codes | Emit standard exit codes + JSON error payloads mapped to guardrail drop reasons | Interpret exit codes, trigger fallbacks, surface errors to user | Enables resilient delegation |
| Configuration defaults | Respect shared config schema; surface CLI config path/env overrides | Migrate existing Talon settings, manage precedence, prompt when conflicts arise | Keeps behaviour consistent |
| UI surfaces (canvases, pattern debug) | Provide data APIs only | Render canvases/notifications, manage focus and dismissal | Keeps CLI headless |

### Adapter Responsibility Outline

- Accept Talon grammar inputs (spoken phrases, selections, stack identifiers) and translate them into CLI command arguments, stdin payloads, or temporary files.
- Capture CLI stdout/stderr/exit codes, mapping guardrail errors and drop reasons back into Talon notifications and Concordance telemetry, including parsing JSON payload fields (`notify`, `debug`, `status`, `error`). When a **CLI error payload** arrives, Talon suppresses legacy fallbacks, surfaces the error message via `notify()`, and logs any `drop_reason` hint.
- Apply CLI `drop_reason` values directly to Talon via `set_drop_reason()` using the severity-prefixed message so Concordance guardrails, history exports, and streaming telemetry observe the same outcome, normalising codes to the shared `RequestDropReason` literal set and collapsing unknown CLI-specific values to the empty string while retaining the message.
- Maintain the shared payload helper (`_parse_bar_cli_payload`) and its `BarCliPayload` dataclass as the canonical decoder for CLI stdout; future telemetry fields must extend this helper so adapters and tests stay aligned. The helper raises the `decode_failed` flag when stdout cannot be parsed, surfaces `severity` so adapters can format notifications consistently, exposes `breadcrumbs` for debug logging, tolerates multi-line or noisy stdout by isolating the final JSON object, and records the CLI stderr stream alongside successful payloads.
- Orchestrate destination side-effects (paste, browser open, history file write, canvas refresh) based on CLI output formats.
- Maintain compatibility fallbacks: detect CLI absence/version mismatch, negotiate capabilities, fall back to legacy Python execution, and log telemetry for parity audits.
- Provide feature flags (for example `user.bar_cli_enabled`) to opt individual commands or surfaces into the CLI path incrementally while `_tests` guardrails compare both behaviours.
- Surface CLI path overrides (`BAR_CLI_PATH` env) so Talon and CI can point at custom binaries without patching code.
- Manage temp directories, attachment storage, and session files with sandbox-aware paths and cleanup guarantees.

---

## Operational Mitigations

- **Configuration & credentials**: map existing Talon settings/env vars into CLI config precedence, validate credential presence early, and warn when migration is needed.
- **Session lifecycle**: document JSON/TOML schema, version markers, locking strategy, and reconnection rules; enforce cleanup on abnormal exits.
- **Performance & latency**: provide daemon mode with keep-alive IPC, cache provider/grammar data, and benchmark cold vs. warm invocations before flipping defaults.
- **Version compatibility**: embed semantic version + capability list in CLI handshake; adapters negotiate and refuse unsupported features with explicit fallbacks.
- **Testing strategy**: add golden transcript tests for CLI stdout/stderr, attachment fixtures, and session persistence across restarts; run both CLI and legacy paths in CI during migration.
- **Log truncation**: cap CLI stdout/stderr and debug log values at 512 characters with an `...(truncated)` suffix and attach indicator metadata (for example, `(original length 2048 chars)`); guardrail tests cover error, breadcrumb, stdout, stderr, and payload logging so runaway payloads cannot overwhelm Talon consoles.
- **Payload helper parity**: keep `_parse_bar_cli_payload` and the `BarCliPayload` dataclass under unit tests covering success and failure cases (including the `decode_failed` flag); extend the helper before introducing new telemetry fields.
- **Distribution & updates**: define signature verification, notarization (macOS), auto-update prompts inside Talon, and manual override instructions for offline setups.
- **Deferred hardening** *(future ADRs)*: advanced threat assessments, privacy redaction policies, third-party plugin support.

---

## Consequences

- **Positive**: eliminates duplicate command grammar definitions, enables automation-friendly CLI usage, and keeps Concordance guardrails aligned across Talon and non-Talon surfaces.
- **Risks**: Talon dependency on an external binary introduces latency, error-handling, packaging, and IO surface complexity; mapping Talon-exclusive interactions (selection, canvases, provider canvases) to CLI outputs may degrade UX if underspecified; Go runtime requirements must be managed for contributors.
- **Mitigations**: maintain a fallback adapter during rollout, add telemetry to detect CLI/Talon mismatches, flesh out the IO parity matrix before delegating commands, validate session/config migration and credential configuration up front, negotiate CLI version/capabilities at startup, and use CI to enforce schema/fixture synchronization across shared guardrails.

---

## Salient Tasks

- Stand up shared schema assets with generation scripts for Talon and CLI consumers.
- Map provider metadata, request gating, guardrail messaging, session schema, attachment formats, error taxonomy, and configuration defaults into shared contracts; document the CLI↔Talon parity matrix and adapter responsibilities for Talon-only IO.
- Define credential discovery (env vars, config files) and security posture for both runtimes; bake checks into telemetry.
- Scaffold `cli/` Go modules with unit tests that load shared fixtures.
- Add Talon adapters that invoke the CLI, guarded by feature flags and `_tests` parity checks.
- Extend CI to build, sign, and publish cross-platform Go binaries from this repo, including golden transcript/attachment tests and version handshake checks.
- Update docs and onboarding material to point Talon operators and external users at the new CLI distribution, including update/rollback instructions.

