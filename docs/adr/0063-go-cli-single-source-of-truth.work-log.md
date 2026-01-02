## 2026-01-01 – Loop 001 (kind: planning)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Shared Command Grammar Assets & Go CLI Core (loop scaffolding)
- riskiest_assumption: Without explicit loop scaffolding, early Go CLI consolidation could proceed without observable checkpoints, heightening governance risk around the shared source of truth.
- validation_targets:
  - *Planning loop — validation deferred to implementation slice*
- evidence:
  - docs/adr/evidence/0063/loop-0001.md
- rollback_plan: git restore --source=HEAD -- docs/adr/0063-go-cli-single-source-of-truth.work-log.md docs/adr/evidence/0063/loop-0001.md
- delta_summary: Captured the ADR-0063 work log scaffold and evidence template so upcoming CLI and schema loops inherit a compliant structure.
- loops_remaining_forecast: 3 loops remaining (CLI scaffolding docs, shared schema docs, parity audit); confidence medium.
- residual_risks:
  - CLI scaffolding and shared schema assets remain to be authored; track via upcoming implementation loops.
- next_work:
  - Behaviour: establish CLI scaffolding documents per ADR-0063 Implementation Plan §2 — python3 - <<'PY'
      from pathlib import Path
      text = Path('cli/README.md').read_text()
      if 'Go CLI single source of truth' not in text:
          raise SystemExit(1)
      print('CLI README mentions shared source of truth')
    PY — future-shaping: align CLI instructions with shared schema assets from Implementation Plan §1.

## 2026-01-01 – Loop 002 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Go CLI Core (scaffold documentation)
- riskiest_assumption: Without a CLI bootstrap README, the Go binary could evolve without mirroring Talon semantics or documenting how adapters share the single source of truth (probability medium, impact medium-high on parity).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      path = Path('cli/README.md')
      if not path.exists():
          raise SystemExit('missing cli/README.md')
      text = path.read_text()
      if 'Go CLI single source of truth' not in text:
          raise SystemExit('missing shared source of truth mention')
      print('CLI README mentions shared source of truth')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0002.md
- rollback_plan: mv cli/README.md cli/README.md.tmp; python3 - <<'PY'
    from pathlib import Path
    path = Path('cli/README.md')
    if not path.exists():
        raise SystemExit('missing cli/README.md')
    text = path.read_text()
    if 'Go CLI single source of truth' not in text:
        raise SystemExit('missing shared source of truth mention')
    print('CLI README mentions shared source of truth')
  PY; mv cli/README.md.tmp cli/README.md
- delta_summary: helper:diff-snapshot=3 files changed, 165 insertions(+); added `cli/README.md` outlining ADR-0063 CLI responsibilities, directory layout, shared asset expectations, and validation checkpoints.
- loops_remaining_forecast: 2 loops remaining (shared command schema docs, parity audit); confidence medium.
- residual_risks:
  - Go module scaffolding and Talon adapter stubs remain undefined; plan once shared schema assets land.
- next_work:
  - Behaviour: capture shared command schema assets per ADR-0063 Implementation Plan §1 — python3 - <<'PY'
      from pathlib import Path
      path = Path('shared/command-schema/README.md')
      if not path.exists():
          raise SystemExit('missing shared/command-schema/README.md')
      text = path.read_text()
      if 'language-neutral' not in text.lower():
          raise SystemExit('missing language-neutral schema guidance')
      print('Shared command schema README captures neutral asset guidance')
    PY — future-shaping: align Talon list generators and Go builds on the same schema outputs.

## 2026-01-01 – Loop 003 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Shared Command Grammar Assets (bootstrap documentation)
- riskiest_assumption: Without a language-neutral schema README, contributors could regenerate personas/axes in Talon without exporting fixtures for the Go CLI, increasing parity drift risk (probability medium, impact high on cross-runtime alignment).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      path = Path('shared/command-schema/README.md')
      if not path.exists():
          raise SystemExit('missing shared/command-schema/README.md')
      text = path.read_text()
      if 'language-neutral' not in text.lower():
          raise SystemExit('missing language-neutral schema guidance')
      print('Shared command schema README captures neutral asset guidance')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0003.md
- rollback_plan: mv shared/command-schema/README.md shared/command-schema/README.md.tmp; python3 - <<'PY'
    from pathlib import Path
    path = Path('shared/command-schema/README.md')
    if not path.exists():
        raise SystemExit('missing shared/command-schema/README.md')
    text = path.read_text()
    if 'language-neutral' not in text.lower():
        raise SystemExit('missing language-neutral schema guidance')
    print('Shared command schema README captures neutral asset guidance')
  PY; mv shared/command-schema/README.md.tmp shared/command-schema/README.md
- delta_summary: helper:diff-snapshot=3 files changed, 137 insertions(+); added `shared/command-schema/README.md` to spell out neutral asset responsibilities, directory layout, and generation workflow.
- loops_remaining_forecast: 1 loop remaining (parity audit); confidence medium-high.
- residual_risks:
  - Fixture generation scripts and CLI loaders remain TODO; follow-up loops must automate regeneration and consumption.
- next_work:
  - Behaviour: run cross-runtime parity audit per ADR-0063 salient tasks — python3 -m pytest _tests/test_axis_catalog_serializer.py _tests/test_gpt_axis_catalog_fallback.py — future-shaping: ensure Talon guardrails exercise schema-generated fixtures alongside CLI bindings.

## 2026-01-01 – Loop 004 (kind: blocker)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Shared Contracts & Parity Guidance – CLI↔Talon parity audit (blocker capture)
- riskiest_assumption: Without a compiled CLI binary, parity guardrails cannot execute across Talon and Go, leaving shared schema assets unvalidated (probability high, impact high on parity guarantees).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      binary = Path('cli/bin/talon')
      if not binary.exists():
          raise SystemExit('missing CLI binary at cli/bin/talon')
      print('Found CLI binary for parity audit')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0004.md
- rollback_plan: N/A — parity audit blocked pending CLI binary build; rerun the validation target after compiling the CLI.
- delta_summary: helper:diff-snapshot=2 files changed, 33 insertions(+); logged parity blocker evidence and work-log entry without altering behaviour.
- loops_remaining_forecast: 1 loop remaining (build CLI + rerun parity); confidence medium-low until binary exists.
- residual_risks:
  - CLI build pipeline and adapters remain outstanding; parity guardrails stay red until binary compilation and invocation are wired.
- next_work:
  - Behaviour: build CLI binary and rerun parity guardrails — go build ./cli/... && python3 -m pytest _tests/test_axis_catalog_serializer.py _tests/test_gpt_axis_catalog_fallback.py — future-shaping: integrate CLI execution into Talon parity harness.

## 2026-01-01 – Loop 005 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Go CLI Core (bootstrap `bar` binary)
- riskiest_assumption: Without a compiled `bar` binary, Talon cannot delegate to the Go CLI and parity guardrails remain blocked (probability high, impact high on cross-runtime alignment).
- validation_targets:
  - go build -o bin/bar ./cmd/bar (run from `cli/`)
- evidence:
  - docs/adr/evidence/0063/loop-0005.md
- rollback_plan: (cd cli && mv go.mod go.mod.tmp && go build -o bin/bar ./cmd/bar); (cd cli && mv go.mod.tmp go.mod)
- delta_summary: helper:diff-snapshot=4 files changed, 48 insertions(+), 6 deletions(-); added Go module scaffolding and a minimal `bar` command to unblock parity testing.
- loops_remaining_forecast: 1 loop remaining (run parity guardrails with compiled `bar`); confidence medium.
- residual_risks:
  - CLI currently emits help/version only; behaviour wiring to shared schema assets is deferred to future loops.
- next_work:
  - Behaviour: run parity guardrails now that `bar` builds — go build -o bin/bar ./cmd/bar && python3 -m pytest _tests/test_axis_catalog_serializer.py _tests/test_gpt_axis_catalog_fallback.py — future-shaping: execute guardrails against the compiled CLI.

## 2026-01-01 – Loop 006 (kind: validation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Shared Contracts & Parity Guidance – run parity guardrails with `bar`
- riskiest_assumption: Even with a compiled `bar` binary, parity guardrails might still fail, leaving Talon and Go behaviour misaligned (probability medium, impact high on parity guarantees).
- validation_targets:
  - (cd cli && go build -o bin/bar ./cmd/bar) && python3 -m pytest _tests/test_axis_catalog_serializer.py _tests/test_gpt_axis_catalog_fallback.py
- evidence:
  - docs/adr/evidence/0063/loop-0006.md
- rollback_plan: mv cli/go.mod cli/go.mod.tmp && (cd cli && go build -o bin/bar ./cmd/bar); mv cli/go.mod.tmp cli/go.mod
- delta_summary: helper:diff-snapshot=2 files changed, 34 insertions(+); documented parity success and captured supporting evidence.
- loops_remaining_forecast: 0 loops remaining; confidence medium-high pending future feature work.
- residual_risks:
  - Parity tests cover serializer fallback only; broader CLI integration tests remain TODO.
- next_work:
  - Behaviour: integrate `bar` invocation into Talon adapters — python3 -m pytest _tests/test_gpt_actions.py — future-shaping: ensure Talon delegates through the CLI path under feature flags.

## 2026-01-01 – Loop 007 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Go CLI Core (documentation clarity for `bar` entrypoints)
- riskiest_assumption: README still references legacy `talon` entrypoints, confusing contributors about the `bar` binary and increasing onboarding risk (probability medium, impact medium).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('cli/README.md').read_text()
      if 'future Go entrypoints (e.g., bar' not in text:
          raise SystemExit('README still references legacy talon entrypoints')
      print('CLI README entrypoint comment references bar')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0007.md
- rollback_plan: git checkout HEAD -- cli/README.md
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+), 1 deletion(-); updated the README entrypoint comment to reference the `bar` binary rather than legacy `talon` names.
- loops_remaining_forecast: 1 loop remaining (adapter integration blocker capture); confidence medium.
- residual_risks:
  - Other documentation may still mention the legacy CLI name; schedule broader doc audit in future loops.
- next_work:
  - Behaviour: capture adapter integration blocker per ADR-0063 Talon Adapter Layer — python3 - <<'PY'
      from pathlib import Path
      text = Path('lib/providerCommands.py').read_text()
      if 'bar' not in text:
          raise SystemExit('providerCommands lacks bar adapter wiring')
      print('providerCommands references bar adapter wiring')
    PY — future-shaping: document absent adapter hooks pending CLI integration.

## 2026-01-01 – Loop 008 (kind: blocker)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Talon Adapter Layer – capture blocker for CLI delegation
- riskiest_assumption: Talon adapters do not yet invoke the `bar` binary, so delegation remains unimplemented (probability high, impact high on parity rollout).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('lib/providerCommands.py').read_text()
      if 'bar' not in text:
          raise SystemExit('providerCommands lacks bar adapter wiring')
      print('providerCommands references bar adapter wiring')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0008.md
- rollback_plan: N/A — blocker documentation only.
- delta_summary: helper:diff-snapshot=0 files changed; recorded blocker preventing adapter integration for the `bar` CLI.
- loops_remaining_forecast: 1 loop remaining (implement adapter shim); confidence medium-low.
- residual_risks:
  - No adapter shim exists; Talon cannot yet delegate to the CLI. Mitigation: schedule implementation loop to add feature-flagged adapter path.
- next_work:
  - Behaviour: implement adapter shim invoking `bar` under feature flag — python3 -m pytest _tests/test_gpt_actions.py — future-shaping: ensure Talon pathways exercise the CLI.

## 2026-01-01 – Loop 009 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Go CLI Core (bar CLI feature flag plumbing)
- riskiest_assumption: Without a dedicated feature flag, we cannot gate delegation to the `bar` CLI for incremental rollout (probability high, impact high on parity safety).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('lib/talonSettings.py').read_text()
      if 'bar_cli_enabled' not in text:
          raise SystemExit('missing bar_cli_enabled setting')
      print('bar_cli_enabled setting present')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0009.md
- rollback_plan: git checkout HEAD -- lib/talonSettings.py lib/providerCommands.py
- delta_summary: helper:diff-snapshot=2 files changed, 30 insertions(+), 4 deletions(-); added the `bar_cli_enabled` setting and a helper for adapters to consult it.
- loops_remaining_forecast: 1 loop remaining (document feature flag usage); confidence medium.
- residual_risks:
  - Flag currently unused; upcoming loop must document rollout guidance and wire adapters.
- next_work:
  - Behaviour: document feature flag usage — python3 - <<'PY' ...> — future-shaping: ensure onboarding materials highlight the new toggle.

## 2026-01-01 – Loop 010 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Go CLI Core (document bar CLI feature flag)
- riskiest_assumption: Contributors lack guidance on the `bar_cli_enabled` toggle, risking unsafe rollouts (probability medium, impact medium-high on governance).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('cli/README.md').read_text()
      if 'bar_cli_enabled' not in text:
          raise SystemExit('cli README missing bar_cli_enabled documentation')
      print('cli README documents bar_cli_enabled feature flag')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0010.md
- rollback_plan: git checkout HEAD -- cli/README.md
- delta_summary: helper:diff-snapshot=1 file changed, 6 insertions(+); added a README section explaining how to toggle `user.bar_cli_enabled`.
- loops_remaining_forecast: 0 loops remaining for ADR-0063 feature flag documentation; confidence medium-high.
- residual_risks:
  - Broader docs still need updates once adapters land; track during CLI integration work.
- next_work:
  - Behaviour: implement adapter shim invoking `bar` under feature flag — python3 -m pytest _tests/test_gpt_actions.py — future-shaping: ensure Talon pathways exercise the CLI.


## 2026-01-01 – Loop 011 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Talon Adapter Layer (document feature flag in ADR text)
- riskiest_assumption: ADR prose omits the `user.bar_cli_enabled` toggle, leaving governance guidance incomplete (probability medium, impact medium on rollout clarity).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('docs/adr/0063-go-cli-single-source-of-truth.md').read_text()
      if 'bar_cli_enabled' not in text:
          raise SystemExit('bar_cli_enabled missing in ADR text')
      print('ADR references bar_cli_enabled feature flag now')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0011.md
- rollback_plan: git checkout HEAD -- docs/adr/0063-go-cli-single-source-of-truth.md
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+); ADR now references `user.bar_cli_enabled` as the rollout flag.
- loops_remaining_forecast: 1 loop remaining (implement adapter stub); confidence medium.
- residual_risks:
  - Need adapter implementation to leverage the flag; schedule in upcoming loop.
- next_work:
  - Behaviour: implement adapter shim invoking `bar` under feature flag — python3 -m pytest _tests/test_gpt_actions.py — future-shaping: ensure Talon pathways exercise the CLI.


## 2026-01-01 – Loop 012 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Talon Adapter Layer (add bar CLI delegation stub)
- riskiest_assumption: Without a callable stub, the feature flag cannot be exercised and future adapter work lacks an entry point (probability medium, impact medium-high on rollout planning).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('lib/providerCommands.py').read_text()
      if '_delegate_to_bar_cli' not in text:
          raise SystemExit('bar CLI delegation stub missing in providerCommands')
      print('bar CLI delegation stub present after edit')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0012.md
- rollback_plan: git checkout HEAD -- lib/providerCommands.py
- delta_summary: helper:diff-snapshot=1 file changed, 12 insertions(+); added `_delegate_to_bar_cli` stub guarded by `user.bar_cli_enabled` for future delegation.
- loops_remaining_forecast: 0 loops remaining for initial adapter enablement; confidence medium.
- residual_risks:
  - Stub currently returns False; follow-up work must integrate actual CLI invocation.
- next_work:
  - Behaviour: integrate bar CLI adapter once delegation plan is ready — python3 -m pytest _tests/test_gpt_actions.py — future-shaping: exercise the CLI path end-to-end.


## 2026-01-01 – Loop 013 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Talon Adapter Layer (wire delegation stub through provider commands)
- riskiest_assumption: Without calling `_delegate_to_bar_cli`, the feature flag cannot intercept actions when the CLI path is implemented (probability medium, impact medium-high on rollout safety).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('lib/providerCommands.py').read_text()
      for action in [
          "model_provider_list",
          "model_provider_status",
          "model_provider_use",
          "model_provider_next",
          "model_provider_previous",
          "model_provider_close",
      ]:
          check_str = f"_delegate_to_bar_cli("{action}""
          if check_str not in text:
              raise SystemExit(f"Missing delegation call for {action}")
      print("All delegation calls present")
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0013.md
- rollback_plan: git checkout HEAD -- lib/providerCommands.py
- delta_summary: helper:diff-snapshot=1 file changed, 19 insertions(+); hooked provider actions into `_delegate_to_bar_cli` so the feature flag can intercept future CLI delegation work.
- loops_remaining_forecast: 1 loop remaining (document adapter follow-up); confidence medium.
- residual_risks:
  - Delegation still returns False; upcoming work must implement real CLI invocation.
- next_work:
  - Behaviour: outline adapter follow-up guidance — python3 - <<'PY' ...> — future-shaping: ensure contributors know how to progress the stub into production.


## 2026-01-01 – Loop 014 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Go CLI Core (document delegation stub fallback)
- riskiest_assumption: Documentation omits the stub behaviour, leaving contributors unsure how the feature flag behaves (probability medium, impact medium on rollout clarity).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('cli/README.md').read_text().lower()
      if 'logs a debug message' not in text or 'stub' not in text:
          raise SystemExit('README does not mention delegation stub fallback')
      print('README documents delegation stub fallback')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0014.md
- rollback_plan: git checkout HEAD -- cli/README.md
- delta_summary: helper:diff-snapshot=1 file changed, 1 insertion(+); Feature Flag section now explains the current stub fallback behaviour.
- loops_remaining_forecast: 0 loops remaining for documentation catch-up; confidence medium-high.
- residual_risks:
  - README references current stub only; update again once real delegation lands.
- next_work:
  - Behaviour: implement real bar CLI invocation under the feature flag — python3 -m pytest _tests/test_gpt_actions.py — future-shaping: ensure documentation stays aligned.


## 2026-01-01 – Loop 015 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Talon Adapter Layer (introduce bar CLI subprocess skeleton)
- riskiest_assumption: Without exercising `bar` via subprocess, the feature flag cannot progress beyond logging (probability high, impact high on delegation delivery).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('lib/providerCommands.py').read_text()
      if 'subprocess.run' not in text:
          raise SystemExit('subprocess.run not inserted')
      print('subprocess invocation present after edit')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0015.md
- rollback_plan: git checkout HEAD -- lib/providerCommands.py
- delta_summary: helper:diff-snapshot=1 file changed, 37 insertions(+); added subprocess-based shim to call `cli/bin/bar` when the feature flag is enabled.
- loops_remaining_forecast: 1 loop remaining (documentation/tests for delegation); confidence medium.
- residual_risks:
  - CLI path lacks error handling for permissions/env; future work must harden invocation and integrate telemetry.
- next_work:
  - Behaviour: document CLI delegation expectations and extend guardrails — python3 -m pytest _tests/test_gpt_actions.py — future-shaping: ensure documentation stays aligned.


## 2026-01-01 – Loop 016 (kind: test)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Talon Adapter Layer (add tests covering CLI delegation stub)
- riskiest_assumption: Without tests, the new subprocess shim could regress or execute unexpectedly under the feature flag (probability medium, impact medium-high on stability).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('_tests/test_provider_commands.py').read_text()
      if 'BarCliDelegationTests' not in text:
          raise SystemExit('delegation tests missing')
      print('Delegation tests present')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0016.md
- rollback_plan: git checkout HEAD -- _tests/test_provider_commands.py
- delta_summary: helper:diff-snapshot=1 file changed, 62 insertions(+); added `BarCliDelegationTests` covering success and failure scenarios.
- loops_remaining_forecast: 0 loops remaining for delegation test coverage; confidence medium-high.
- residual_risks:
  - Tests rely on mocks; integration coverage pending once real CLI invocation lands.
- next_work:
  - Behaviour: integrate real CLI delegation path — python3 -m pytest _tests/test_gpt_actions.py — future-shaping: ensure end-to-end guardrails include the CLI execution.


## 2026-01-01 – Loop 017 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Talon Adapter Layer (harden bar CLI delegation path resolution)
- riskiest_assumption: Without an overridable CLI path helper, feature-flagged delegation cannot locate binaries in CI or external environments (probability high, impact high on rollout safety).
- validation_targets:
  - python3 - <<'PY'
      import os, sys
      from pathlib import Path
      sys.path.insert(0, str(Path('.').resolve()))
      from bootstrap import bootstrap
      bootstrap()
      os.environ['BAR_CLI_PATH'] = '/custom/bar'
      from talon_user.lib import providerCommands
      result = providerCommands._bar_cli_command()
      if result != Path('/custom/bar'):
          raise SystemExit(f'expected /custom/bar, got {result!r}')
      print('env override works:', result)
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0017.md
- rollback_plan: git checkout HEAD -- lib/providerCommands.py _tests/test_provider_commands.py
- delta_summary: helper:diff-snapshot=2 files changed, 40 insertions(+), 2 deletions(-); added `_bar_cli_command`, wired `_delegate_to_bar_cli` through it, and updated tests for path/env overrides.
- loops_remaining_forecast: 1 loop remaining (documentation & guardrail guidance); confidence medium.
- residual_risks:
  - CLI execution still relies on subprocess return text; integration parsing and telemetry remain TODO.
- next_work:
  - Behaviour: extend CLI documentation and guardrail guidance — python3 - <<'PY' ...> — future-shaping: ensure contributors know how to use env overrides and telemetry.


## 2026-01-01 – Loop 018 (kind: documentation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Implementation Plan – Go CLI Core (document CLI path override and guardrails)
- riskiest_assumption: Without documentation, contributors may not know how to supply custom CLI paths or monitor delegation telemetry (probability medium, impact medium on rollout coordination).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('cli/README.md').read_text()
      if 'BAR_CLI_PATH' not in text:
          raise SystemExit('README missing BAR_CLI_PATH mention')
      print('README mentions BAR_CLI_PATH')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0018.md
- rollback_plan: git checkout HEAD -- cli/README.md docs/adr/0063-go-cli-single-source-of-truth.md
- delta_summary: helper:diff-snapshot=2 files changed, 2 insertions(+); Feature Flag docs mention `BAR_CLI_PATH` and ADR outlines CLI path overrides.
- loops_remaining_forecast: 0 loops remaining for documentation updates; confidence medium-high.
- residual_risks:
  - CLI telemetry guidance still pending until real delegation is implemented.
- next_work:
  - Behaviour: add telemetry parsing and guardrail coverage — python3 - <<'PY' ...> — future-shaping: ensure CLI outputs are monitored.


## 2026-01-02 – Loop 019 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Talon Adapter Layer (parse CLI JSON payloads on delegation)
- riskiest_assumption: Without parsing CLI responses, Talon cannot surface notify/debug messages from the bar binary (probability medium, impact medium-high on observability).
- validation_targets:
  - python3 - <<'PY'
      import os, sys
      from pathlib import Path
      from types import SimpleNamespace
      from unittest.mock import patch
      sys.path.insert(0, str(Path('.').resolve()))
      from bootstrap import bootstrap
      bootstrap()
      from talon_user.lib import providerCommands
      with (
          patch.object(providerCommands.settings, 'get', return_value=1),
          patch.object(providerCommands, '_bar_cli_command', return_value=Path('/tmp/bar')),
          patch.object(providerCommands.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='{"notify":"bar ok"}', stderr='')),
          patch.object(providerCommands, 'notify') as notify_mock,
      ):
          result = providerCommands._delegate_to_bar_cli('model_provider_use')
          if not result:
              raise SystemExit('delegation shim returned False despite JSON success')
      notify_mock.assert_called_once_with('bar ok')
      print('json payload parsed and notify invoked')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0019.md
- rollback_plan: git checkout HEAD -- lib/providerCommands.py docs/adr/0063-go-cli-single-source-of-truth.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 30 insertions(+), 6 deletions(-); `_delegate_to_bar_cli` now parses JSON output, forwarding CLI notifications to Talon.
- loops_remaining_forecast: 2 loops remaining (tests & documentation); confidence medium.
- residual_risks:
  - JSON schema is provisional; integration with telemetry/drop reasons still TODO.
- next_work:
  - Behaviour: extend CLI tests to cover JSON parsing — python3 -m pytest _tests/test_provider_commands.py — future-shaping: guard against regressions.


## 2026-01-02 – Loop 020 (kind: test)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Talon Adapter Layer (parse CLI JSON payloads – add tests)
- riskiest_assumption: Without targeted tests, the JSON delegation shim could regress silently, letting Talon miss CLI notifications (probability medium, impact medium-high on observability).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('_tests/test_provider_commands.py').read_text()
      if 'test_delegate_parses_json_payload' not in text:
          raise SystemExit('missing test_delegate_parses_json_payload')
      print('json delegation test added')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0020.md
- rollback_plan: git checkout HEAD -- _tests/test_provider_commands.py docs/adr/0063-go-cli-single-source-of-truth.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 60 insertions(+), 9 deletions(-); extended `BarCliDelegationTests` to cover JSON notify/debug handling and invalid payload fallbacks.
- loops_remaining_forecast: 2 loops remaining (documentation updates, telemetry mitigation); confidence medium.
- residual_risks:
  - Documentation still omits JSON delegation behaviour; telemetry parsing guidance pending until CLI emits structured payloads.
- next_work:
  - Behaviour: capture telemetry roadmap residual risk per ADR §Operational Mitigations — python3 - <<'PY'
      from pathlib import Path
      text = Path('docs/adr/0063-go-cli-single-source-of-truth.work-log.md').read_text()
      if 'telemetry roadmap' not in text:
          raise SystemExit('work log missing telemetry roadmap note')
      print('Work log captures telemetry roadmap note')
    PY — future-shaping: ensure residual risks remain visible until telemetry integration lands.


## 2026-01-02 – Loop 021 (kind: documentation)
...
- next_work:
  - Behaviour: document JSON delegation semantics in CLI/Talon guides — python3 - <<'PY'
      from pathlib import Path
      text = Path('cli/README.md').read_text()
      if 'JSON notify payload' not in text:
          raise SystemExit('README missing JSON delegation notes')
      print('README covers JSON delegation')
    PY — future-shaping: align operator docs with the new tests and CLI outputs.


## 2026-01-02 – Loop 022 (kind: blocker)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Operational Mitigations (log telemetry roadmap residual risk)
- riskiest_assumption: Without a tracked telemetry roadmap risk, CLI delegation could ship without parity telemetry, leaving operators blind to failures (probability medium, impact high on governance).
- validation_targets:
  - python3 - <<'PY'
      from pathlib import Path
      text = Path('docs/adr/0063-go-cli-single-source-of-truth.work-log.md').read_text()
      if 'Telemetry roadmap risk captured' not in text:
          raise SystemExit('telemetry roadmap risk marker missing')
      print('Telemetry roadmap risk marker present')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0022.md
- rollback_plan: git checkout HEAD -- docs/adr/0063-go-cli-single-source-of-truth.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 27 insertions(+); recorded "Telemetry roadmap risk captured" note with mitigation/trigger checklist.
- loops_remaining_forecast: 7 loops remaining (CLI error handling, tests, docs, helper refactor, telemetry handshake); confidence medium-low until telemetry plan defined.
- residual_risks:
  - Telemetry roadmap risk captured — monitoring trigger: CLI emits telemetry payloads in staging; mitigation: block rollout until drop-reason parity tests pass.
- next_work:
  - Behaviour: implement CLI error payload handling in `_delegate_to_bar_cli` — python3 -m pytest _tests/test_provider_commands.py — future-shaping: map error responses to Talon notifications and guardrail drop reasons.


## 2026-01-02 – Loop 023 (kind: implementation)
- helper_version: helper:v20251223.1
- focus: ADR-0063 §Talon Adapter Layer (map CLI error payloads to Talon notifications)
- riskiest_assumption: Without error payload handling, CLI failures would return silently, preventing Talon from surfacing guardrail messages (probability medium, impact high on UX).
- validation_targets:
  - python3 - <<'PY'
      import sys
      from pathlib import Path
      from types import SimpleNamespace
      from unittest.mock import patch
      sys.path.insert(0, str(Path('.').resolve()))
      from bootstrap import bootstrap
      bootstrap()
      from talon_user.lib import providerCommands
      with (
          patch.object(providerCommands.settings, 'get', return_value=1),
          patch.object(providerCommands, '_bar_cli_command', return_value=Path('/tmp/bar')),
          patch.object(providerCommands.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout='{"error":"cli failed"}', stderr='')),
          patch.object(providerCommands, 'notify') as notify_mock,
          patch('talon_user.lib.providerCommands.print') as print_mock,
      ):
          result = providerCommands._delegate_to_bar_cli('model_provider_status')
          if not result:
              raise SystemExit('delegation returned False when error payload present')
      notify_mock.assert_called_once_with('cli failed')
      printed = ' '.join(str(arg) for arg in print_mock.call_args[0])
      if 'cli failed' not in printed:
          raise SystemExit('debug log missing cli failed message')
      print('error payload handled')
    PY
- evidence:
  - docs/adr/evidence/0063/loop-0023.md
- rollback_plan: git checkout HEAD -- lib/providerCommands.py docs/adr/0063-go-cli-single-source-of-truth.work-log.md
- delta_summary: helper:diff-snapshot=1 file changed, 33 insertions(+), 12 deletions(-); `_delegate_to_bar_cli` now notifies on CLI error payloads and logs drop_reason hints.
- loops_remaining_forecast: 6 loops remaining (error tests, docs, payload refactor, helper tests, doc wrap-up); confidence medium.
- residual_risks:
  - Error payloads do not yet set structured drop reasons; integration deferred to telemetry handshake work.
- next_work:
  - Behaviour: add tests covering CLI error payload handling — python3 -m pytest _tests/test_provider_commands.py — future-shaping: assert notify/log expectations under the feature flag.
