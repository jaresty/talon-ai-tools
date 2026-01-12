# ADR-0075 – CLI Coordination Layer Refactor
Status: Accepted
Date: 2026-01-11
Owners: Bubble Tea / CLI working group

## Context
- The churn × complexity concordance scan (scope `cmd/bar/, internal/barcli/`) flagged `internal/barcli/app.go`, `internal/barcli/build.go`, `internal/barcli/tui.go`, and `internal/barcli/grammar.go` as the highest-scoring coordination hotspots (scores 1.6k–2.1k) with repeated edits to `parseArgs`, `Run`, `runTUI`, and `applyOverrideToken`.
- These helpers sit at the boundary between CLI flag parsing, preset/token hydration, and the Bubble Tea TUI launch described in ADR 0072. Each palette or preset change forces churn across the same monolith files.
- Snapshot fixtures and expect suites added for ADR 0072 now depend on consistent CLI summaries. Without a clearer CLI abstraction, future omnibox/tokens work will keep touching the same surfaces.
- Previous ADRs (0063 Go CLI single source of truth, 0065 portable prompt grammar CLI) catalogued CLI generation and grammar output but did not split runtime coordination or argument validation.

## Problem
- CLI coordination is spread across large files (`app.go`, `build.go`, `tui.go`) with duplicated token/preset logic. Every Bubble Tea or token change requires edits across these functions, driving churn and increasing the risk of regressions.
- `parseArgs` mixes flag parsing, environment bootstrap, preset resolution, and grammar wiring, obscuring the contract needed by ADR 0072’s palette/TUI orchestration.
- Token override handling (`applyOverrideToken` et al.) sits inside CLI command pipelines instead of a reusable library, making it difficult to align with the TUI workflow.
- Lack of a dedicated CLI/TUI coordination module makes it harder to align expect tests and palette changes; summary strip/destination updates added in ADR 0072 still rely on bespoke CLI string building scattered across files.

## Decision
- Introduce a dedicated CLI coordination layer that encapsulates argument parsing, preset/token resolution, and TUI launch wiring.
- Extract `parseArgs` and `Run` responsibilities into a new package (e.g., `internal/barcli/cli`) that returns a typed configuration consumed by both `build` and `tui` entry points.
- Factor token override helpers (currently in `build.go`) into a shared library aligned with ADR 0072 token semantics so the TUI and CLI reuse the same transformations.
- Wrap TUI launch (`runTUI`) with an injected interface supplied by the coordination layer, clarifying what state the Bubble Tea app requires (subject, tokens, env, presets) and minimizing direct CLI dependency on the TUI package.
- Regenerate grammar embed assets once the coordination layer is in place; future grammar or preset rewrites should funnel through the extracted package, reducing churn in `grammar.go`.

## Tests-First Principle
> Guard the CLI coordination refactor with existing expect/TUI harnesses and CLI unit tests before moving code. Characterize `parseArgs`, `Run`, `applyOverrideToken`, and `runTUI` behaviour with snapshot/expect coverage, then refactor in slices that keep the harness green.

## Refactor Plan
1. **Characterize & Extract CLI configuration**
   - Add focused tests around `parseArgs` covering presets, overrides, and env flags.
   - Introduce a `Config` struct (tokens, subject, preset, env) returned by a new package; update `Run` to consume it without changing behaviour.
2. **Factor token override utilities**
   - Move `applyOverrideToken` and related helpers into `internal/barcli/tokens` (or similar) with unit coverage, ensuring both CLI and TUI use the same canonical helpers.
3. **Decouple TUI launch wiring**
   - Wrap `runTUI` with an interface provided by the coordination package; ensure expect cases (`token-command-history`, `sticky-summary`, etc.) stay green.
4. **Grammar/TUI alignment**
   - Once the config layer is stable, review `grammar.go` initialization; regenerate embed assets or expose the grammar to the new package to reduce duplication.
5. **Documentation & ADR 0072 linkage**
   - Update ADR 0072 follow-ups to reference the new coordination layer, making it explicit how palette workflows target CLI behaviour.

## Consequences
- The CLI and TUI will share typed contracts, reducing churn when ADR 0072 adds new palette features or summary fields.
- Hotspot churn in `app.go`, `build.go`, and `tui.go` should drop as logic moves into cohesive packages with focused tests.
- Short-term refactor slices add overhead (new package, migration), but expect harnesses accelerate verification.
- Downstream docs and snapshots need a light refresh once the coordination layer exposes clearer public APIs.

## Salient Tasks
1. Characterize current CLI parsing and build tests for `parseArgs`/`Run` before extraction.
2. Extract token override helpers into a shared package and update CLI/TUI callers.
3. Introduce the CLI coordination package and migrate `Run`/`runTUI` to use it.
4. Regenerate grammar embed output and ensure expect/TUI harnesses remain green.
5. Update ADR 0072 work log to reference the new coordination layer for future palette loops.
