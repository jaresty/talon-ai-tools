# Shared Command Schema Assets (ADR-0063)

ADR-0063 establishes `shared/command-schema/` as the language-neutral source of truth for personas, intents, axis metadata, prompt grammar tokens, guardrail contracts, and provider capabilities. These assets flow into both the Talon runtime and the Go CLI so changes land once and propagate everywhere.

## Responsibilities

- **Schema definition**: capture canonical JSON/YAML for personas, intents, axis tokens, prompt templates, provider metadata, request gating states, drop-reason messaging, and telemetry envelopes.
- **Generation pipeline**: scripts under `scripts/tools/` ingest Python/Talon data sources and emit language-neutral artefacts stored alongside this README; Talon list generators and the Go CLI treat these files as inputs, not code.
- **Backward compatibility**: embed schema versions, capability flags, and migration notes so Talon adapters and the CLI can negotiate upgrades during handshake flows.
- **Validation**: extend `_tests/` guardrails to read the shared assets, assert parity with Talon modules, and spawn the Go CLI to ensure behaviour matches across runtimes.

## Directory Layout

```
shared/command-schema/
  README.md                  # governance, layout, and generation guidance
  fixtures/                  # generated JSON/YAML assets committed to the repo
  generators/                # future scripts/modules that produce fixtures
  schema/                    # JSON Schema / OpenAPI definitions for validation
```

- `fixtures/` stores checked-in outputs consumed by Talon list generators, docs builders, and Go builds.
- `generators/` will house Python tooling that assembles neutral assets from existing catalog helpers (personas, axis catalog, guardrails).
- `schema/` captures machine-readable definitions so both runtimes validate the fixtures consistently.

## Generation Workflow (planned)

1. Regenerate fixtures via `python3 scripts/tools/generate-command-schema.py` (to be implemented) when personas, intents, axis metadata, or guardrail rules change.
2. Run `python3 -m pytest _tests/test_axis_catalog_serializer.py _tests/test_gpt_axis_catalog_fallback.py` (and future Go parity tests) to ensure Talon and CLI consumers load the assets without drift.
3. Commit regenerated fixtures together with the `shared/command-schema` README updates and guardrail snapshots.

## Next Steps

- Author generation tooling that reads existing Talon catalogs and writes fixtures under `shared/command-schema/fixtures/`.
- Wire Talon list generators and docs to ingest the fixtures instead of Python modules directly.
- Update Go CLI loaders to consume the same assets during startup and stamp schema version telemetry for parity checks.
