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
- With the current stub (Loop 012), enabling the flag logs a debug message and gracefully falls back to the legacy path; upcoming loops will replace the stub with real CLI delegation.
- Override the binary location with the `BAR_CLI_PATH` environment variable (useful in CI or virtualenvs); otherwise the helper resolves to `<repo>/cli/bin/bar`.

## CLI JSON Payloads

When the adapters call `bar`, the binary responds with structured JSON on stdout. Current fields parsed by `_delegate_to_bar_cli` include:

- `notify`: short message surfaced to Talon users (mirrors `notify()` calls); documentation refers to this as the **JSON notify payload**.
- `debug`/`status`: additional diagnostics logged to the Talon debug console.
- `error`: Talon now surfaces CLI error payloads via `notify()` and logs the `drop_reason` hint when provided; follow-up telemetry work will map errors to guardrail drop reasons.

Emit plain JSON objects (single line) so Talon can parse responses deterministically; non-JSON stdout falls back to legacy logging only. When returning a **CLI error payload**, include both `error` and optional `drop_reason` keys so Talon can mirror CLI diagnostics without re-running the legacy path. Talon wraps decoded responses in the `BarCliPayload` dataclass (see `lib/providerCommands.py`), which exposes convenience attributes (`notice`, `error`, `debug`, `drop_reason`, `alert`, `severity`) and the `has_payload` flag used across adapters and tests.

Severity values (for example `"severity": "warning"`) are prefixed to notices and alerts (`[WARNING] message`) and logged for debugging. Use lowercase severity strings; the adapter normalises them to uppercase when surfacing notifications.

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
