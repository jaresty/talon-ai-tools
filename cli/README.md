# Bar CLI Bootstrap (ADR-0063)

ADR-0063 commits the Go CLI single source of truth for the Talon command surface, delivered as the `bar` binary. This README captures the initial scaffold and checkpoints the CLI must satisfy before feature work lands.

## Behaviour Outcomes

- **Mirror Talon semantics**: the Bar CLI must emit the same personas, intents, axes, guardrails, and drop-reason messaging that Talon exposes today.
- **Serve multiple entrypoints**: support non-interactive CLI flows, an interactive TUI, and adapters that Talon can shell out to.
- **Delegate Talon-specific IO**: adapters inside Talon translate selection, canvases, and stack destinations into the CLI’s neutral inputs/outputs.

## Directory Layout (initial)

```
cli/
  README.md                # loop scaffolding and onboarding notes
  cmd/                     # future Go entrypoints (e.g., bar, bar-daemon)
  internal/                # shared Go packages for request orchestration, schema loading
  shared/                  # generated assets and neutral schemas vendored for Go builds
```

- `cmd/` and `internal/` mirror Talon modules such as `lib/providerCommands.py` and `lib/requestLifecycle.py` while remaining Go-native.
- `shared/` depends on language-neutral assets that originate from `shared/command-schema/` (Loop 003) so Go builds and Talon list generators consume identical inputs.

## Shared Assets & Validation

- Generated fixtures (personas, intents, guardrails) are canonically produced under `shared/command-schema/` and checked into `cli/shared/` for Go builds.
- Integration guardrails must exercise `python3 -m pytest` suites that spawn the `bar` binary to keep Talon and Go behaviour aligned.
- CLI unit tests (Go) should live alongside the Go packages; Python guardrails remain in `_tests/`.

## Feature Flag

- `user.bar_cli_enabled` controls delegation to the `bar` binary. The default value `0` keeps the legacy in-process provider path.
- Toggle it via Talon settings (for example `settings.set("user.bar_cli_enabled", 1)`) or the `settings.talon` config file once the adapter path lands.
- Feature-flagged rollout lets CI and contributors compare legacy vs. CLI behaviour before flipping defaults.

## Implementation Slices

1. Establish shared command schema assets (Loop 003) with generation scripts that hydrate Talon lists and Go bindings.
2. Scaffold Go entrypoints (`cmd/bar`, future daemon entrypoints) that load the shared schema and dispatch to adapters.
3. Implement adapters that translate CLI responses back into Talon canvases, selections, and history flows.
4. Extend CI to build and sign CLI binaries alongside existing docs and guardrail artefacts.

## Validation Checklist

- [ ] `python3 -m pytest _tests/test_make_axis_regenerate.py` can spawn the CLI once guardrails land.
- [ ] Future Go unit tests cover persona/intent loading, provider routing, and guardrail messaging.
- [ ] Talon adapters expose feature flags to fall back to legacy Python execution until CLI parity is confirmed.

## Next Steps

- Capture shared schema asset requirements in Loop 003 and wire the generation script outputs into `cli/shared/`.
- Draft Go module scaffolding (`go.mod`, `cmd/bar/main.go`) once shared assets exist and tests can pin expected behaviour.
