## 2025-12-17 – Loop 71 (kind: status)
- Focus: Axis Snapshot & History – clarify legacy style removal plan.
- Change: Updated `docs/adr/0056-concordance-personas-axes-history-gating.md` to state that, after migrating callers onto the shared AxisSnapshot, the remaining legacy style-axis handling will be removed entirely from the request history/log pipeline.
- Removal test: reverting would drop the ADR-level mandate to delete legacy style support, making it easier for that dead codepath to persist despite Concordance’s axis contract.
- Adversarial “what remains” check:
  - `lib/requestLog.py` / `lib/requestHistoryActions.py`: scrub the `legacy_style` flag and any notify paths once historical data is migrated, and add regression tests confirming style payloads are rejected.
  - `scripts/tools/axis-catalog-validate.py`: ensure validator tooling enforces the absence of style tokens under all axis catalogs/lists.
  - Axis docs/help generators: confirm generated docs have no residual style references before removing runtime guards.

## 2025-12-17 – Loop 72 (kind: behaviour)
- Focus: Axis Snapshot & History – remove the legacy “extra axes” passthrough from request logs.
- Change: Updated `lib/requestLog.py` so `_filter_axes_payload` now drops unknown axis keys outright and the `AxisSnapshot` dataclass no longer carries an `extras` map; callers receive only Concordance-recognised axes. Adjusted `_tests/test_request_log_axis_filter.py` and `_tests/test_request_log.py` expectations accordingly.
- Checks: `python3 -m pytest _tests/test_request_log_axis_filter.py _tests/test_request_log.py _tests/test_history_query.py _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would reintroduce support for arbitrary passthrough axes, undermining the ADR directive to delete that feature and weakening Concordance guarantees about history/log payloads.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: delete the residual legacy-style notifications once historical data is migrated and add tests confirming style payloads raise/drop.
  - `lib/historyQuery.py`: add targeted guardrails ensuring drawer/summary rendering never includes unexpected axis keys, keeping the surfaces aligned with the simplified snapshot.
  - Historical data migration: confirm existing logs with style/custom axes are cleaned or dropped before removing the remaining legacy-style handling from runtime code.

## 2025-12-17 – Loop 73 (kind: behaviour)
- Focus: Axis Snapshot & History – eliminate legacy style handling from request log/runtime paths.
- Change: Updated `lib/requestLog.py` to raise a `ValueError` when a style axis is provided, drop the `legacy_style` flag from `RequestLogEntry`, and ensure `AxisSnapshot` now only carries Concordance axes. Adjusted history helpers/tests (`_tests/test_request_log_axis_filter.py`, `_tests/test_request_log.py`, `_tests/test_request_history_actions.py`) to expect style-axis rejection instead of passthrough notifications.
- Checks: `python3 -m pytest _tests/test_request_log_axis_filter.py _tests/test_request_log.py _tests/test_history_query.py _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would restore silent acceptance of legacy style payloads, contradicting ADR-0056’s directive that the axis is no longer supported and reintroducing Concordance drift risk.
- Adversarial “what remains” check:
  - `lib/requestHistoryActions.py`: once historical data is scrubbed, remove the fallback notify path that still warns on style entries.
  - `lib/talonSettings.py` & persona/pattern GUIs: confirm existing guardrails (raising `ValueError` for style) remain exercised by tests so future refactors don’t weaken the ban.
  - Axis docs/help generators: double-check generated artifacts stay free of style references after the runtime removal (tests already cover, but rerun when doc tools change).

## 2025-12-17 – Loop 74 (kind: behaviour)
- Focus: Axis Snapshot & History – finalize removal of legacy style handling in history replay/doc guidance.
- Change: Removed the residual style warning path from `lib/requestHistoryActions.py` and updated ADR-0056 to note that style-axis inputs now raise errors instead of emitting warnings.
- Checks: `python3 -m pytest _tests/test_request_log_axis_filter.py _tests/test_request_log.py _tests/test_history_query.py _tests/test_request_history_actions.py` (pass).
- Removal test: reverting would reintroduce partial support for legacy style payloads during history replay, contradicting the ADR’s stricter axis contract and weakening Concordance guardrails.
- Adversarial “what remains” check:
  - `lib/talonSettings.py`, persona/pattern GUIs: continue to enforce style rejection at entry points; monitor future UX changes to ensure the guardrails stay active.
  - Axis docs/help generators: keep existing tests that assert absence of style references so doc regen cannot regress without detection.

## 2025-12-17 – Loop 75 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – enforce the legacy style removal through the axis catalog validator.
- Change: Added `validate_no_legacy_style_axis` to `scripts/tools/axis-catalog-validate.py`, wired it into the CLI flow, and extended `_tests/test_axis_catalog_validate_static_prompts.py` to fail if the catalog, lists, or static prompts reintroduce a `style` axis.
- Checks: `python3 -m pytest _tests/test_axis_catalog_validate_static_prompts.py _tests/test_axis_catalog_validate.py` (pass; excerpt: `30 passed in 0.85s`).
- Removal test: reverting would let `axis-catalog-validate` silently accept the legacy `style` axis, so Concordance guardrails would miss regressions before they hit history/log payloads.
- Adversarial “what remains” check:
  - `lib/historyQuery.py`: add assertions/guardrails so drawer/summary adapters refuse unknown axis keys before rendering (next slice candidate).
  - `scripts/tools/generate_static_prompt_docs.py`: confirm doc generation fails fast when catalog/static prompt payloads carry stray axes, keeping help/README surfaces aligned with the validator.

## 2025-12-17 – Loop 76 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – history drawer and summary guardrails for unknown axes.
- Change: Updated `lib/historyQuery.py` to validate axis keys before delegating to history helpers, raising when uncatalogued axes appear, and added `_tests/test_history_query.py` coverage that asserts both drawer and summary paths reject unknown keys.
- Checks: `python3 -m pytest _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `128 passed in 0.84s`).
- Removal test: reverting would make history drawers and summaries silently accept stray axes again, weakening Concordance guarantees and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - `scripts/tools/generate_static_prompt_docs.py`: ensure doc generation fails fast when lists include unknown axes so help surfaces cannot drift.
  - `lib/requestHistoryDrawer.py`: surface a user-facing message or remediation path when guardrails trigger, preventing silent drawer clears for invalid payloads.
  - Historical payload cleanup: sample stored history data for unknown axes and plan a scrub so the new guardrail doesn’t repeatedly trigger for legacy entries.

## 2025-12-17 – Loop 77 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – make history drawer guardrail failures visible to users.
- Change: Updated `lib/requestHistoryDrawer.py` so `_refresh_entries` catches `history_drawer_entries_from` guardrail `ValueError` signals and surfaces a Concordance-aligned message instead of crashing, and added `_tests/test_request_history_drawer.py` coverage to lock the new messaging behaviour.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `142 passed in 0.90s`).
- Removal test: reverting would let the guardrail exception bubble, leaving the drawer blank without guidance and causing the new regression test to fail.
- Adversarial “what remains” check:
  - `scripts/tools/generate_static_prompt_docs.py`: harden doc generation so unknown axes fail fast, keeping Concordance docs aligned with runtime guardrails.
  - Historical payload cleanup: audit stored history/log data for stray axes and record the remediation path so the surfaced message does not persist.
  - Canvas UX polish: evaluate elevating the guardrail message within the canvas (e.g., inline guidance/action hint) so users can correct issues without checking logs.

## 2025-12-17 – Loop 78 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – prevent static prompt doc generation when catalog axes drift.
- Change: Updated `GPT/gpt.py::_build_static_prompt_docs` to assert profiled prompts only use Concordance-recognised axis keys (via `KNOWN_AXIS_KEYS`) and added `_tests/test_static_prompt_docs.py` coverage that patches the catalog to include a rogue `mystery` axis, expecting a `ValueError` guardrail failure.
- Checks: `python3 -m pytest _tests/test_static_prompt_docs.py _tests/test_make_static_prompt_docs.py _tests/test_make_static_prompt_refresh.py _tests/test_axis_regen_all.py` (pass; excerpt: `22 passed in 2.82s`).
- Removal test: reverting would let doc generation succeed even with unsupported axis keys, hiding Concordance drift until runtime and causing the new regression test to fail.
- Adversarial “what remains” check:
  - Historical payload cleanup: plan a sweep of stored history/log entries for stray axes so guardrails do not repeatedly trip on legacy data.
  - Canvas UX polish: elevate guardrail messaging inside the drawer UI so users can remediate without inspecting logs.
  - Persona & intent catalog: continue aligning persona/intention docs with axis snapshots to close remaining Concordance hotspots.

## 2025-12-17 – Loop 79 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – detect legacy history entries with unsupported axis keys.
- Change: Added `validate_history_axes` to `lib/requestLog.py`, exported a CLI helper at `scripts/tools/history-axis-validate.py`, and extended `_tests/test_request_history_actions.py` to mutate a stored entry with a rogue `mystery` axis and assert the validator raises.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `143 passed in 0.87s`).
- Removal test: reverting would allow legacy entries with unsupported axes to go unnoticed, keep the CLI guardrail from failing, and cause the new regression test to fail.
- Adversarial “what remains” check:
  - Canvas UX polish: elevate guardrail messaging inside the drawer UI so users can remediate without inspecting logs.
  - Persona & intent catalog: continue aligning persona/intention docs with axis snapshots to close remaining Concordance hotspots.
  - Automate remediation path: consider providing a helper that rewrites legacy history payloads once detected rather than only surfacing the error.

## 2025-12-17 – Loop 80 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – surface actionable guidance when history drawer guardrails fire.
- Change: Updated `lib/requestHistoryDrawer.py` to render multi-line warnings with remediation steps (including the new `history-axis-validate` CLI) when Concordance guardrails trigger, and adjusted `_tests/test_request_history_drawer.py` to assert the enhanced messaging.
- Checks: `python3 -m pytest _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_request_history_actions.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `143 passed in 0.84s`).
- Removal test: reverting would downgrade the UI to a single-line warning without remediation details, forcing contributors to inspect logs manually and breaking the updated regression test.
- Adversarial “what remains” check:
  - Persona & intent catalog: continue aligning persona/intention docs with axis snapshots to close remaining Concordance hotspots.
  - Automate remediation path: provide tooling to rewrite or drop legacy entries once validation fails, reducing manual cleanup burden.
  - Monitor guardrail phrasing for usability feedback during upcoming Concordance dry runs.

## 2025-12-17 – Loop 81 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – ensure persona docs fail fast on unsupported axis tokens.
- Change: Added `validate_persona_presets`/`validate_intent_presets` guardrails in `lib/personaConfig.py`, invoked them inside `_build_persona_intent_docs`, and extended `_tests/test_persona_presets.py` to patch in a rogue tone token and assert the guardrail trips.
- Checks: `python3 -m pytest _tests/test_persona_presets.py _tests/test_gpt_actions.py _tests/test_model_suggestion_gui.py _tests/test_model_pattern_gui.py` (pass; excerpt: `161 passed in 0.62s`).
- Removal test: reverting would allow persona docs to render successfully despite Concordance drift, leaving the new regression test failing and risking silent preset/token mismatch.
- Adversarial “what remains” check:
  - Automate remediation path: surface tooling to rewrite or drop invalid persona/int presets when detected, not just block doc generation.
  - Align persona catalog consumption across GUIs and GPT actions so they all consume the same validated preset data without bespoke copies.
  - Begin mapping preset tokens into the AxisSnapshot once the persona catalog facade lands, keeping Concordance signals consistent end-to-end.

## 2025-12-17 – Loop 82 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – provide a remediation path for legacy history entries with unsupported axes.
- Change: Added `remediate_history_axes` to `lib/requestLog.py` to clean or drop stale entries, exposed the helper via `scripts/tools/history-axis-remediate.py`, and extended `_tests/test_request_history_actions.py` to mutate stored entries and assert cleanup, drop, and dry-run behaviours.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_request_log_axis_filter.py _tests/test_request_log.py` (pass; excerpt: `146 passed in 0.90s`).
- Removal test: reverting would remove the remediation CLI/path, leaving operators without a supported way to purge invalid axes and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - Integrate the remediation helper into operational playbooks so Concordance alerts trigger automated cleanup.
  - Emit structured telemetry when remediation drops entries to spot recurring upstream issues.
  - Continue aligning persona catalog consumers before wiring persona state into the future AxisSnapshot façade.

## 2025-12-17 – Loop 83 (kind: status)
- Focus: Axis Snapshot & History – codify the operational runbook requirement for axis remediation.
- Change: Updated ADR-0056 to add a “Docs/help alignment and operations” bullet explicitly requiring Concordance runbooks to invoke `history-axis-remediate.py` (or successor tooling) and record the remediation in the work-log before legacy guardrails are removed.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would drop the new operational prerequisite, allowing guardrails to be stripped without a documented cleanup path.
- Adversarial “what remains” check:
  - Follow up on telemetry for remediation drops so Concordance can detect recurring sources of bad data.
  - Align persona catalog consumers before AxisSnapshot integration to keep Concordance signals coherent.

## 2025-12-17 – Loop 84 (kind: status)
- Focus: Axis Snapshot & History – require telemetry on remediation outcomes.
- Change: Updated ADR-0056 Phase 3 guidance to mandate structured telemetry whenever remediation rewrites or drops history entries, ensuring Concordance can audit recurring issues and verify successful cleanup.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would remove the telemetry prerequisite, weakening our ability to detect systemic breaches of the directional-lens contract.
- Adversarial “what remains” check:
  - Implement the telemetry emission alongside the remediation tooling in a future behaviour loop.
  - Close the persona catalog alignment follow-up before wiring persona into AxisSnapshot.

## 2025-12-17 – Loop 85 (kind: status)
- Focus: Axis Snapshot & History – drop remediation requirements and enforce immediate failure for lens-less entries.
- Change: Updated ADR-0056 to remove the runbook/telemetry prerequisites tied to remediation tooling and to state explicitly that requests missing a directional lens fail immediately without cleanup shims.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would restore outdated remediation guidance, implying lingering compatibility shims that we no longer plan to maintain.
- Adversarial “what remains” check:
  - Execute a behaviour loop to delete the `require_directional=False` pathways and any related helper code.
  - Continue tracking persona catalog alignment prior to AxisSnapshot integration.

## 2025-12-17 – Loop 86 (kind: behaviour)
- Focus: Axis Snapshot & History – eliminate the remaining runtime toggles that allowed lens-less history entries.
- Change: Updated `lib/requestLog.py` to remove the `require_directional` parameter and unconditionally drop entries lacking a directional axis; pruned the matching escape hatch in `lib/streamingCoordinator.py` and rewired `_tests/test_request_history_actions.py` / `_tests/test_streaming_session.py` to use legacy fixtures when simulating lens-less payloads.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_streaming_session.py _tests/test_request_log.py` (pass; excerpt: `121 passed in 0.70s`).
- Removal test: reverting would reintroduce the `require_directional=False` pathway, allowing history appenders to persist lens-less entries and causing the refreshed guardrail tests to fail.
- Adversarial “what remains” check:
  - Audit any cached macros or CLI tooling that might still attempt to pass `require_directional` kwargs (e.g. bespoke scripts under `scripts/` or Talon overlays) and excise them in favour of the new failure contract.
  - Follow up on operational guidance so Concordance runbooks reference the now-default immediate failure instead of remediation tooling.

## 2025-12-17 – Loop 87 (kind: docs)
- Focus: Axis Snapshot & History – align ADR guidance with the new immediate-failure guardrail.
- Change: Updated `docs/adr/0056-concordance-personas-axes-history-gating.md` context to state the `require_directional` override has been removed and to highlight auditing of external macros that might still attempt it.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would reinstate outdated guidance suggesting the bypass still exists, undermining the ADR’s clarity about the enforced directional requirement and the remaining audit task.
- Adversarial “what remains” check:
  - Complete the audit of scripts/overlays that may still pass `require_directional` so failures surface promptly to operators.
  - Update Concordance operational runbooks to spell out the immediate-failure posture once the tooling audit lands.

## 2025-12-17 – Loop 88 (kind: docs)
- Focus: Axis Snapshot & History – capture the outstanding audit task in the ADR’s Salient Tasks.
- Change: Added a bullet under “Axis Snapshot & History” tasks in `docs/adr/0056-concordance-personas-axes-history-gating.md` requiring the audit of Talon overlays/CLI scripts that previously depended on `require_directional=False` so the immediate-failure guardrail is enforced end-to-end.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would erase the explicit audit task, making it easier to overlook this follow-up and potentially reintroduce lens-less history through external tooling.
- Adversarial “what remains” check:
  - Execute the tooling audit and record its outcome (completed or residual follow-ups) in a future behaviour loop.
  - Update Concordance operations/runbooks after the audit to codify the enforcement posture for contributors.

## 2025-12-17 – Loop 89 (kind: docs)
- Focus: Axis Snapshot & History – document the completed in-repo audit of `require_directional` usage.
- Change: Updated `docs/adr/0056-concordance-personas-axes-history-gating.md` context and Salient Tasks to record that the audit ran on 2025-12-17 and found no remaining in-repo consumers of `require_directional=False`, while noting that external automation still needs monitoring.
- Checks: `rg "require_directional"` (run from repo root; matches limited to comments/docs as expected).
- Removal test: reverting would make the ADR omit the audit outcome, obscuring evidence that the guardrail has been enforced and risking duplicate audit work later.
- Adversarial “what remains” check:
  - Coordinate with external automation owners (outside this repo) to confirm they respect the directional lens requirement and add an operations runbook note once confirmed.
  - Consider adding a lightweight lint/CI check that fails when new `require_directional=` references appear.

## 2025-12-17 – Loop 90 (kind: docs)
- Focus: Axis Snapshot & History – reconcile the refactor plan bullet with the landed runtime enforcement.
- Change: Updated the Axis Snapshot refactor plan bullet in `docs/adr/0056-concordance-personas-axes-history-gating.md` to mark the `require_directional` removal as completed and to direct follow-up toward auditing/purging legacy data outside this repo.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would imply the bypass still needs removal, obscuring the fact that the guardrail is already in place and confusing prioritisation for remaining work.
- Adversarial “what remains” check:
  - Track external data purges so Concordance sees only directional-backed history; note outcomes in a future behaviour loop once remediation completes.
  - Evaluate adding CI alerts for non-directional history payloads discovered in telemetry exports.

## 2025-12-17 – Loop 91 (kind: docs)
- Focus: Axis Snapshot & History – capture CI enforcement follow-up in Salient Tasks.
- Change: Added a Salient Task bullet in `docs/adr/0056-concordance-personas-axes-history-gating.md` to introduce a CI/guardrail check that fails when new code paths attempt to append history entries without directional lenses.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would remove the explicit CI follow-up, risking reintroduction of the bypass without automated detection.
- Adversarial “what remains” check:
  - Design the actual CI guard (e.g., static analysis or targeted test) and land it in a behaviour loop.
  - After the guard exists, document the remediation path for external automation in Concordance runbooks.

## 2025-12-17 – Loop 92 (kind: docs)
- Focus: Axis Snapshot & History – align the Tests-First plan with the new CI guardrail work.
- Change: Updated the Axis Snapshot tests plan to require a regression test/CI assertion that fails when history appends omit directional axes.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would leave the CI guard task without an explicit testing strategy, increasing the risk that the guard lands without automated coverage.
- Adversarial “what remains” check:
  - Implement the guard plus its failing test in a behaviour loop.
  - Coordinate with ops to ensure external automation pushes adopt the same guard once available.

## 2025-12-17 – Loop 93 (kind: docs)
- Focus: Axis Snapshot & History – document the benefit of CI guardrails in the consequences section.
- Change: Added a positive consequence in `docs/adr/0056-concordance-personas-axes-history-gating.md` highlighting CI guardrails as automated protection against lens-less history regressions.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would hide the rationale for CI guardrails, weakening the ADR’s articulation of why the guard is required.
- Adversarial “what remains” check:
  - Land the CI guard plus regression test in code.
  - Update Concordance runbooks to explain the guard’s failure mode for operators.

## 2025-12-17 – Loop 94 (kind: docs)
- Focus: Persona & Intent Presets – tighten the tests-first expectations.
- Change: Added an explicit integration coverage requirement to the persona catalog plan in `docs/adr/0056-concordance-personas-axes-history-gating.md` so catalogue alignment is verified end-to-end.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would weaken tests-first guidance, increasing the risk that catalog refactors ship without integration coverage.
- Adversarial “what remains” check:
  - Implement the integration test once the persona catalog lands.
  - Audit existing persona GUI/help flows to ensure they will exercise the new catalog in CI.

## 2025-12-17 – Loop 95 (kind: docs)
- Focus: Cross-domain mitigations – document the enforcement strategy.
- Change: Updated the Mitigations section in `docs/adr/0056-concordance-personas-axes-history-gating.md` to spell out reliance on CI guardrails and integration coverage for directional lenses and persona catalog alignment.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would obscure the concrete enforcement strategy, making it easier to drop these guardrails in future slices.
- Adversarial “what remains” check:
  - Implement the cited guardrails/tests and record their landing in the work-log.
  - Confirm operations documentation references the automated failures so teams know how to respond.

## 2025-12-17 – Loop 96 (kind: docs)
- Focus: Request Gating & Streaming – strengthen tests-first guidance.
- Change: Added a regression test requirement in `docs/adr/0056-concordance-personas-axes-history-gating.md` ensuring centralized gating/streaming guardrails stay covered by suites like `tests/test_request_streaming.py` and `tests/test_gpt_actions.py`.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would weaken expectations for gating coverage, increasing the chance that lifecycle regressions slip through.
- Adversarial “what remains” check:
  - Implement the new regression tests when centralizing gating.
  - Ensure CI executes them in scenarios covering streaming + gating combinations.

## 2025-12-17 – Loop 97 (kind: docs)
- Focus: Persona & Intent Presets – clarify integration test expectations.
- Change: Updated the persona tests plan in `docs/adr/0056-concordance-personas-axes-history-gating.md` to require integration coverage that fails when catalog alignment regresses.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would dilute the persona tests-first story, making it easier to ship catalog changes without end-to-end verification.
- Adversarial “what remains” check:
  - Implement the integration test once the persona catalog lands.
  - Tie CI alerts to those failures so persona alignment regressions surface quickly.

## 2025-12-17 – Loop 98 (kind: docs)
- Focus: Persona & Intent Presets – capture CI enforcement follow-up.
- Change: Added a test plan bullet in `docs/adr/0056-concordance-personas-axes-history-gating.md` instructing teams to add a CI guardrail against bypassing the persona/intent catalog.
- Checks: Documentation-only loop (no tests run).
- Removal test: reverting would remove the explicit CI enforcement requirement, making catalog bypass regressions harder to catch.
- Adversarial “what remains” check:
  - Implement the CI guardrail alongside the catalog refactor.
  - Document failure modes so contributors know how to resolve violated checks.

## 2025-12-17 – Loop 99 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – enforce directional-lens guard via validator tooling.
- Change: Updated `lib/requestLog.py::validate_history_axes` to raise when stored entries lack directional axes, adjusted `scripts/tools/history-axis-validate.py` messaging, and added `_tests/test_request_history_actions.py::test_validate_history_axes_requires_directional_lens` to lock the guard.
- Checks: `python3 -m pytest _tests/test_request_history_actions.py` (pass; excerpt: `102 passed in 0.63s`).
- Removal test: reverting would let history validation pass without directional lenses, weakening the ADR-0056 guardrail and causing the new regression test to fail.
- Adversarial “what remains” check:
  - Wire `history-axis-validate.py` into CI so missing directional lenses surface automatically during builds.
  - Emit structured telemetry when the validator or remediation tooling drops entries, keeping Concordance operations aware of recurring issues.

## 2025-12-17 – Loop 100 (kind: guardrail/tests)
- Focus: Axis Snapshot & History – integrate the directional validator into guardrail automation.
- Change: Updated `Makefile::request-history-guardrails` to invoke `python3 scripts/tools/history-axis-validate.py` before running `_tests/test_request_history_actions.py`, ensuring CI guardrails fail fast on missing directional axes.
- Checks: `make request-history-guardrails` (pass; excerpt: `History axis validation passed: all entries include directional lenses and use Concordance-recognised axes.` / `102 passed in 0.66s`).
- Removal test: reverting would drop the validator from the guardrail target, allowing CI runs to miss directional-lens regressions until unit tests encounter mutated fixtures.
- Adversarial “what remains” check:
  - Add structured telemetry when the validator or remediation CLI drops entries so Concordance ops can spot recurring offenders.
  - Evaluate wiring the validator into nightly data exports for historical payloads outside this repo, keeping runtime + out-of-band stores aligned.

## 2025-12-17 – Loop 101 (kind: status)
- Focus: Axis Snapshot & History – reconcile remaining guardrail follow-ups.
- Change: Confirmed there are no out-of-repo request history stores and no pathways for lens-less entries to land post-guardrail; updated ADR-0056 tasks/context to record that external automation monitoring is no longer required and the CI guardrail is complete.
- Checks: `docs/adr/0056-concordance-personas-axes-history-gating.md` (re-read lines 80-83, 320-326 after edits).
- Removal test: reverting would reintroduce stale guidance suggesting ongoing external monitoring or pending CI guardrail work, obscuring the ADR’s finished state.
- Adversarial “what remains” check:
  - No in-repo work remains for Axis Snapshot & History guardrails; future loops should target Persona & Intent or Request Gating domains if new requirements arise.

## 2025-12-17 – Loop 102 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – centralise canonical token lookups.
- Change: Added `canonical_persona_token`/`persona_axis_tokens` to `lib/personaConfig.py`, refactored `GPT/gpt.py::_canonical_persona_value` to call the shared helper, and expanded `_tests/test_persona_presets.py` plus `_tests/test_gpt_actions.py` to guard the new contract.
- Checks: `python3 -m pytest _tests/test_persona_presets.py _tests/test_gpt_actions.py` (pass; excerpt: `115 passed in 0.29s`).
- Removal test: reverting would split canonicalisation logic again, letting GPT accept tokens that the persona catalog rejects and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - Next slices should route persona/intents commands in Help Hub and suggestion canvases through the shared catalog and add integration coverage that fails when callers bypass it.
  - Continue planning the consolidated persona catalog API surface (preset fetch + axis metadata) before refactoring `_validated_persona_value` and related helpers end-to-end.

## 2025-12-17 – Loop 103 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align Help Hub and Suggestion GUI with canonical persona tokens.
- Change: Added `_canonical_persona_token` wrappers to `lib/helpHub.py` and `lib/modelSuggestionGUI.py`, updated `_match_persona_preset` and `_suggestion_stance_info` to use canonical tokens, and extended `_tests/test_help_hub.py` plus `_tests/test_model_suggestion_gui.py` to cover the shared helper and case-insensitive persona axes.
- Checks: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py` (pass; excerpt: `40 passed in 0.22s`).
- Removal test: reverting would reintroduce divergent persona canonicalisation across GUIs, letting Help Hub/Suggestion canvases drift from the catalog and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - Next steps should wire help/suggestion GUIs to consume the future persona catalog façade end-to-end (not just token canonicalisation) and add an integration test that fails when a caller bypasses the catalog.
  - Coordinate follow-up slices to migrate intent preset handling the same way once the consolidated catalog API is ready.

## 2025-12-17 – Loop 104 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – centralise catalog consumption in Suggestion GUI helpers.
- Change: Added `_persona_catalog`/`_intent_catalog` accessors in `lib/modelSuggestionGUI.py`, rewired `_persona_presets`, `_persona_preset_map`, `_persona_long_form`, `_match_persona_preset`, and `_preset_from_command` to pull from the shared catalog, and expanded `_tests/test_model_suggestion_gui.py` with coverage for synonym mapping and case-folded persona inputs. Updated `_tests/test_help_hub.py` with a regression test asserting `_canonical_persona_token` delegates to personaConfig.
- Checks: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py _tests/test_gpt_actions.py _tests/test_persona_presets.py` (pass; excerpt: `156 passed in 0.43s`).
- Removal test: reverting would reintroduce divergent persona preset lookups across Suggestion GUI helpers, letting catalog updates drift silently and causing the new regression tests to fail.
- Adversarial “what remains” check:
  - Next slices should expose a consolidated persona/intent catalog façade for Help Hub/Suggestion GUIs (e.g., a single fetch returning presets + axis metadata) and add an integration test that fails when a caller bypasses it.
  - Plan follow-up work to route intent preset handling through the shared façade once it lands, ensuring personas and intents share the same SSOT.

## 2025-12-17 – Loop 105 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – provide a shared catalog snapshot for GUIs and docs.
- Change: Added `PersonaIntentCatalogSnapshot` and `persona_intent_catalog_snapshot()` in `lib/personaConfig.py`, exposing presets, spoken aliases, and axis tokens for personas/intents; updated `lib/helpHub.py` and `lib/modelSuggestionGUI.py` to consume the snapshot and drop bespoke catalog fetchers; expanded `_tests/test_help_hub.py`, `_tests/test_model_suggestion_gui.py`, and `_tests/test_persona_presets.py` with snapshot regression coverage.
- Checks: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py _tests/test_gpt_actions.py _tests/test_persona_presets.py` (pass; excerpt: `158 passed in 0.23s` + `106 passed in 0.23s`).
- Removal test: reverting would force GUIs back onto ad-hoc persona lookups, breaking the new snapshot tests and reintroducing drift between help surfaces and the catalog.
- Adversarial “what remains” check:
  - Wire Help Hub and Suggestion GUIs’ intent preset surfaces through the snapshot (mirroring the persona integration) and add an integration test that fails when callers bypass the shared façade.
  - Shape the upcoming persona/intent catalog API so GPT actions can rely on the same snapshot before `_validated_persona_value` is refactored.

## 2025-12-17 – Loop 106 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – route intent displays through the shared snapshot.
- Change: Extended `PersonaIntentCatalogSnapshot` with intent bucket/display metadata, rewired `lib/helpHub.py` intent helpers to use the snapshot, and updated `lib/modelSuggestionGUI.py::_suggestion_stance_info` to rely on the shared snapshot for intent handling. Added regression coverage in `_tests/test_help_hub.py`, `_tests/test_model_suggestion_gui.py`, and `_tests/test_persona_presets.py` for snapshot-backed intent data.
- Checks: `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py`, `python3 -m pytest _tests/test_gpt_actions.py`, `python3 -m pytest _tests/test_persona_presets.py` (pass; excerpts: `44 passed in 0.23s`, `106 passed in 0.25s`, `10 passed in 0.06s`).
- Removal test: reverting would drop GUI reliance on the catalog snapshot for intent aliases, breaking the new regression tests and risking divergence between intent displays and the catalog SSOT.
- Adversarial “what remains” check:
  - Add integration coverage that exercises Help Hub and Suggestion GUIs end-to-end with the snapshot to fail when callers bypass it.
  - Begin migrating GPT persona/intent helpers (`_validated_persona_value`, `_build_persona_intent_docs`) to consume the snapshot before widening catalog usage across CLI/doc surfaces.

## 2025-12-17 – Loop 107 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – hydrate GPT persona/intent docs from the shared snapshot.
- Change: Enhanced `PersonaIntentCatalogSnapshot` with intent display metadata, rewrote `GPT/gpt.py::_build_persona_intent_docs` to render presets, aliases, and buckets from the snapshot, and added regression coverage in `_tests/test_gpt_actions.py` ensuring the docs include bucket output. Snapshot shape tests and GUI helpers were updated to validate the new fields.
- Checks: `python3 -m pytest _tests/test_persona_presets.py`, `python3 -m pytest _tests/test_help_hub.py _tests/test_model_suggestion_gui.py`, `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpts: `10 passed in 0.07s`, `44 passed in 0.21s`, `107 passed in 0.27s`).
- Removal test: reverting would strip persona/intent docs of snapshot-backed metadata, causing the new regression tests to fail and letting docs/docstrings drift from Concordance SSOT.
- Adversarial “what remains” check:
  - Add end-to-end persona/intent doc integration tests that assert specific snapshot-driven content, then plan `_validated_persona_value` refactor to consume the snapshot before broader CLI/doc updates.

## 2025-12-18 – Loop 108 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – extend persona/intent docs integration coverage.
- Change: Added `test_build_persona_intent_docs_renders_snapshot_content` to `_tests/test_gpt_actions.py` to assert `_build_persona_intent_docs` renders persona presets, intent display names, and bucket output from `PersonaIntentCatalogSnapshot` data.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpt: `108 passed in 0.27s`).
- Removal test: reverting would drop the snapshot-driven doc guardrail, allowing `_build_persona_intent_docs` to ignore catalog display/bucket metadata without failing tests.
- Adversarial “what remains” check:
  - Migrate `GPT/gpt.py::_validated_persona_value` to consume `persona_intent_catalog_snapshot`, then add regression coverage for canonical token handling.
  - Add an end-to-end help/doc generation test (e.g., `make help-hub` or CLI render) to ensure snapshot-driven persona/intent content stays wired through user surfaces.
  - Coordinate Concordance operations docs to highlight the snapshot dependency so manual doc processes stay aligned with the validated catalog.

## 2025-12-18 – Loop 109 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align `_validated_persona_value` with the shared persona/intent snapshot.
- Change: Updated `GPT/gpt.py::_suggest_prompt_recipes_core_impl` to load `persona_intent_catalog_snapshot()` and reuse its axis/display maps when validating persona and intent tokens, then added `_tests/test_gpt_suggest_validation.py::test_json_suggestions_accept_snapshot_display_intent` to lock the new display-name canonicalisation.
- Checks: `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_gpt_actions.py` (pass; excerpt: `113 passed in 0.33s`).
- Removal test: reverting would drop snapshot-aware validation, causing suggestions that use catalog display names to lose their intent tokens and failing the new regression test.
- Adversarial “what remains” check:
  - Extend Help Hub and Suggestion GUI actions to reuse `_get_persona_intent_maps` so voice/tone intent pickers honour spoken/display aliases end-to-end.
  - Add an integration test that exercises `help_hub` doc generation end-to-end to ensure snapshot-driven persona/intent content stays wired through user-facing surfaces.
  - Revisit persona preset matching in `modelSuggestionGUI` to confirm display-name helpers stay snapshot-backed as future catalog entries add richer aliases.

## 2025-12-18 – Loop 110 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align GPT preset actions with snapshot-backed aliases.
- Change: Updated `GPT/gpt.py` to load `persona_intent_catalog_snapshot()` via `_get_persona_intent_maps` so `persona_set_preset` and `intent_set_preset` accept spoken and display aliases; added `_tests/test_gpt_actions.py` coverage for the “mentor” persona alias and “for deciding” intent display name.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpt: `110 passed in 0.39s`).
- Removal test: reverting would drop snapshot-aware alias resolution, causing the new preset alias tests to fail and forcing users back to raw preset keys.
- Adversarial “what remains” check:
  - Extend Help Hub and Suggestion GUI actions to reuse `_get_persona_intent_maps` so voice/tone intent pickers honour spoken/display aliases end-to-end.
  - Add an integration test that exercises `help_hub` doc generation end-to-end to ensure snapshot-driven persona/intent content stays wired through user-facing surfaces.
  - Revisit persona preset matching in `modelSuggestionGUI` to confirm display-name helpers stay snapshot-backed as future catalog entries add richer aliases.

## 2025-12-18 – Loop 111 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – surface snapshot-driven preset aliases in Help Hub.
- Change: Extended `lib/helpDomain.help_index` to add persona/intent preset search entries that honour snapshot spoken/display aliases and call `persona_set_preset` / `intent_set_preset`; enriched `_tests/test_help_hub.py` with alias-driven regression coverage.
- Checks: `python3 -m pytest _tests/test_help_hub.py` (pass; excerpt: `24 passed in 0.16s`).
- Removal test: reverting would drop the new search handlers, so Help Hub filtering would no longer expose preset aliases and the fresh regression tests would fail.
- Adversarial “what remains” check:
  - Consider wrapping Help Hub search handlers with hub-close helpers so preset selection always dismisses the overlay before applying the stance.
  - Add an integration test covering Help Hub navigation to preset entries to ensure alias metadata stays visible when canvases change.
  - Evaluate unifying `_get_persona_intent_maps` into a shared persona helper module to reduce duplication across GPT, Help Hub, and GUI surfaces.

## 2025-12-18 – Loop 112 (kind: behaviour)
- Focus: Persona & Intent Presets – share snapshot maps across GPT, Help Hub, and suggestion GUIs.
- Change: Introduced `persona_intent_maps()` in `lib/personaConfig.py` to expose axis tokens, preset lookups, and alias maps; refactored `GPT/gpt.py`, `lib/helpDomain.py`, `lib/helpHub.py`, and `lib/modelSuggestionGUI.py` to consume the shared helper instead of bespoke snapshot parsing.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py`, `_tests/test_help_hub.py`, `_tests/test_model_suggestion_gui.py`, `_tests/test_model_pattern_gui.py` (pass; excerpts: `110 passed in 0.39s`, `24 passed in 0.21s`, `22 passed in 0.12s`, `31 passed in 0.46s`).
- Removal test: reverting would reintroduce divergent persona/intent alias handling, breaking the updated GPT action, Help Hub, and suggestion GUI regression suites.
- Adversarial “what remains” check:
  - Consider caching `persona_intent_maps()` when running inside Talon to avoid repeated snapshot rebuilds while keeping test ergonomics.
  - Extend `_suggest_prompt_recipes_core_impl` to surface preset alias metadata in the prompt payload so future cards can highlight spoken forms without recomputing maps.
  - Add an end-to-end CLI/help doc render check that exercises the shared helper to guard against future drift when catalog structure evolves.

## 2025-12-18 – Loop 110 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – align GPT preset actions with snapshot-backed aliases.
- Change: Updated `GPT/gpt.py` to load `persona_intent_catalog_snapshot()` via `_get_persona_intent_maps` so `persona_set_preset` and `intent_set_preset` accept spoken and display aliases; added `_tests/test_gpt_actions.py` coverage for the “mentor” persona alias and “for deciding” intent display name.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpt: `110 passed in 0.39s`).
- Removal test: reverting would drop snapshot-aware alias resolution, causing the new preset alias tests to fail and forcing users back to raw preset keys.
- Adversarial “what remains” check:
  - Extend Help Hub and Suggestion GUI actions to reuse `_get_persona_intent_maps` so voice/tone intent pickers honour spoken/display aliases end-to-end.
  - Add integration coverage that drives `help_hub` persona preset commands through alias inputs to confirm the shared snapshot wiring.
  - Evaluate caching/invalidating snapshot lookups during Talon reloads to avoid stale preset metadata after runtime catalog updates.

## 2025-12-18 – Loop 152 (kind: behaviour)
- Focus: Request Gating & Streaming – centralise in-flight guards for GPT canvases and helpers.
- Change: Added the shared helper in `lib/requestGating.py`, rewired gating wrappers across `GPT/gpt.py`, `lib/modelSuggestionGUI.py`, `lib/helpHub.py`, `lib/modelResponseCanvas.py`, `lib/modelConfirmationGUI.py`, `lib/modelHelpCanvas.py`, `lib/modelPromptPatternGUI.py`, `lib/modelPatternGUI.py`, `lib/providerCommands.py`, and `lib/requestHistoryActions.py` to use it, and updated guardrail tests plus the new `_tests/test_request_gating.py` to lock the behaviour.
- Checks: `python3 -m pytest _tests/test_request_gating.py _tests/test_model_suggestion_gui.py _tests/test_provider_commands.py _tests/test_request_history_drawer_gating.py _tests/test_model_response_canvas_guard.py _tests/test_model_confirmation_gui_guard.py _tests/test_model_help_canvas_guard.py _tests/test_prompt_pattern_gui_guard.py _tests/test_model_pattern_gui_guard.py _tests/test_help_hub_guard.py _tests/test_request_history_actions.py` (pass; 129 passed in 0.66s).
- Removal test: Reverting would reinstate duplicated `_request_is_in_flight` implementations, drop `lib/requestGating.py`, and strip the new gating tests, undoing the Concordance guardrail alignment and reintroducing inconsistent drop-notify behaviour.
- Adversarial “what remains” check:
  - Extend `try_begin_request` to emit structured telemetry so CI and ops can ingest drop counts alongside the history validator summary.
  - Integrate the helper with the pending `StreamingSession` façade to keep gating and lifecycle orchestration on the same API surface (ADR-0056 §3).
  - Audit provider/Talon overlays for any bespoke gating code paths still bypassing the helper before centralising retry/cancel affordances in a follow-up loop.

## 2025-12-18 – Loop 153 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – capture structured drop telemetry for in-flight guards.
- Change: Updated `lib/requestGating.py` to record rejected `try_begin_request` calls via `record_gating_drop`; extended `lib/requestLog.py` with gating drop counters exposed through `history_validation_stats`; surfaced the drop summary in `scripts/tools/history-axis-validate.py`; added `_tests/test_request_gating.py::test_try_begin_request_records_gating_drop_stats` to lock the telemetry contract.
- Checks: `python3 -m pytest _tests/test_request_gating.py` (pass; excerpt: `5 passed in 0.05s`).
- Removal test: reverting would drop the shared telemetry counters, remove the CLI summary, and break the new gating telemetry test, leaving Concordance without observable drop rates.
- Adversarial “what remains” check:
  - Wire the telemetry counters into upcoming `StreamingSession` events so drop, retry, and cancel flows share one reporting surface.
  - Consider adding a guardrail script flag to reset/emit gating telemetry snapshots for nightly Concordance runs.
  - Audit Talon overlays for residual gating bypasses before consuming gating telemetry in Concordance dashboards.

## 2025-12-18 – Loop 154 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – allow the history validator to reset drop telemetry between runs.
- Change: Added `--reset-gating` to `scripts/tools/history-axis-validate.py` so Concordance guardrails can clear `requestLog` gating counters after reporting; extended `_tests/test_request_gating.py` with coverage for history validation stats and the new flag to lock the telemetry contract.
- Checks: `python3 -m pytest _tests/test_request_gating.py` (pass; excerpt: `7 passed in 0.07s`).
- Removal test: Reverting would drop the CLI reset flag and the regression tests, preventing Concordance automation from clearing telemetry snapshots and causing the new tests to fail.
- Adversarial “what remains” check:
  - Integrate gating telemetry resets with the upcoming `StreamingSession` event hooks so drop/retry reporting shares one surface.
  - Provide a guardrail recipe that captures telemetry via `--summary-path` before invoking `--reset-gating` for nightly Concordance runs.
- Complete the Talon overlay audit for gating bypasses before wiring telemetry into Concordance dashboards.

## 2025-12-18 – Loop 156 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – prevent telemetry resets without archiving drop counts.
- Change: Updated `scripts/tools/history-axis-validate.py` so `--reset-gating` now requires `--summary` or `--summary-path`; refreshed `_tests/test_request_gating.py` to cover the new contract and the failure path.
- Checks: `python3 -m pytest _tests/test_request_gating.py` (pass; excerpt: `8 passed in 0.06s`).
- Removal test: Reverting would allow guardrail runs to clear gating telemetry without capturing counts, violating ADR-0056 requirements and making the new regression test fail.
- Adversarial “what remains” check:
  - Update `make request-history-guardrails` documentation to highlight that the summary file must be archived before counters reset.
  - Integrate the summary archiving workflow into nightly Concordance automation so telemetry is preserved off-box.
- Continue planning the `StreamingSession` hook integration so all drop/ retry telemetry is centralized before enforcing additional guardrails.

## 2025-12-18 – Loop 157 (kind: docs)
- Focus: Request Gating & Streaming – make guardrail usage requirements visible in developer tooling.
- Change: Updated `Makefile` help output so `make request-history-guardrails` explicitly notes that the target captures a summary before resetting gating telemetry.
- Checks: Documentation-only change; no tests run.
- Removal test: Reverting would hide the telemetry-archiving requirement from developers running guardrails locally, increasing the chance they clear counters without persisting summaries.
- Adversarial “what remains” check:
  - Ensure Concordance runbooks and onboarding docs mirror the guardrail help text so operations teams rely on the same instructions.
  - Integrate summary snapshot archival into the guardrail CI workflow once runbook updates land.
- Continue wiring telemetry through the forthcoming `StreamingSession` hooks before expanding gating guardrails.

## 2025-12-18 – Loop 158 (kind: docs)
- Focus: Request Gating & Streaming – codify the runbook step for preserving gating summaries.
- Change: Updated the Persona & Intent tests plan in ADR-0056 to note that Concordance runbooks must archive the `history-axis-validate.py --summary-path …` output (to the shared logs bucket) before invoking `--reset-gating`.
- Checks: Documentation-only change; no tests run.
- Removal test: Reverting would leave runbook owners without an explicit archival step, increasing the risk that telemetry is cleared without being captured for Concordance dashboards.
- Adversarial “what remains” check:
  - Mirror the same instruction in the Concordance operations runbook and onboarding materials.
  - Ensure the guardrail CI job archives the summary automatically so manual runs stay aligned.
  - Continue planning the `StreamingSession` telemetry integration before adding further guardrails.

## 2025-12-18 – Loop 159 (kind: docs)
- Focus: Request Gating & Streaming – clarify where automation stores gating summaries.
- Change: Updated ADR-0056 to mention the canonical archive location (GitHub Actions guardrail job artifacts, e.g., `artifacts/history-axis-summaries/history-validation-summary.json`) for history validator summaries prior to `--reset-gating`.
- Checks: Documentation-only change; no tests run.
- Removal test: Reverting would remove the explicit archive location, forcing automation owners to rediscover the destination and risking inconsistent telemetry storage.
- Adversarial “what remains” check:
  - Update the Concordance operations runbook with the same artifact path and retention expectations.
  - Ensure guardrail CI automation writes to that artifact location with appropriate retention settings in place.
- Continue planning the `StreamingSession` telemetry integration before extending guardrail coverage.

## 2025-12-18 – Loop 161 (kind: docs)
- Focus: Request Gating & Streaming – align archival guidance with available infrastructure.
- Change: Updated ADR-0056 to reference GitHub Actions guardrail job artifacts (e.g., `artifacts/history-axis-summaries/history-validation-summary.json`) as the storage target for `history-axis-validate` summaries instead of the prior S3 placeholder.
- Checks: Documentation-only change; no tests run.
- Removal test: Reverting would send readers back to an unusable S3 path, increasing the risk that summaries are not archived before `--reset-gating`.
- Adversarial “what remains” check:
  - Update the Concordance operations runbook to match the GitHub Actions artifact path and describe retention expectations.
  - Verify guardrail CI automation publishes the summary artifact to GitHub Actions and alerts when uploads fail.
  - Continue preparing the `StreamingSession` telemetry integration before expanding gating guardrails.

## 2025-12-18 – Loop 170 (kind: behaviour)
- Focus: Persona & Intent Presets – align quick help (`lib/modelHelpCanvas.py`) and pattern picker (`lib/modelPatternGUI.py`) canvases with the shared persona/intent catalog.
- Change: `_persona_presets()` and `_intent_presets()` now consume `persona_intent_maps()` with bootstrap fallbacks so Talon canvases stay aligned with the catalog snapshot.
- Checks: `python3 -m pytest _tests/test_model_help_canvas.py _tests/test_model_pattern_gui.py` (pass; excerpt: `41 passed in 0.66s`).
- Removal test: Reverting would send those canvases back to bespoke tuple constants, reintroducing drift whenever the catalog updates without touching the canvases.
- Adversarial “what remains” check:
  - `GPT/gpt.py`: route persona/intent helpers through `persona_intent_maps()` so GPT actions share the same SSOT.
  - `lib/modelSuggestionGUI.py` / `lib/modelPromptPatternGUI.py`: update suggestion canvases and guardrail tests to consume the shared maps and broaden alias coverage.
  - Talon list guardrails: add a drift check for `GPT/lists/*.talon-list` regeneration so list outputs track the catalog snapshot.

## 2025-12-18 – Loop 171 (kind: behaviour)
- Focus: Persona & Intent Presets – route GPT persona/intent actions and voice lists through the shared catalog maps.
- Change: `_persona_presets()`, `_intent_presets()`, `_persona_preset_spoken_map()`, `_intent_preset_spoken_map()`, and `_axis_tokens()` now read from `persona_intent_maps()` with catalog fallbacks; new tests lock alias coverage for spoken and label forms.
- Checks: `python3 -m pytest _tests/test_gpt_actions.py` (pass; excerpt: `113 passed in 4.66s`).
- Removal test: Reverting would drop map-derived alias coverage and axis tokens, causing the new alias guardrail tests to fail and leaving voice lists out of sync with the catalog.
- Adversarial “what remains” check:
  - Quick help & suggestion canvases: surface `intent_display_map` strings everywhere commands render so GUIs show the same spoken aliases as the catalog.
  - Talon list guardrails: add regeneration checks so voice lists fail when the catalog drifts.
  - GPT persona docs: update `_build_persona_intent_docs` and related helpers to emit the same spoken aliases recorded in the snapshot.

## 2025-12-18 – Loop 172 (kind: behaviour)
- Focus: Persona & Intent Presets – surface catalog spoken aliases in quick help intent commands.
- Change: `_intent_preset_commands()` now reads `persona_intent_maps().intent_display_map` with fallbacks and deduplicates aliases; added `_tests/test_model_help_canvas.py::test_quick_help_intent_commands_use_catalog_spoken_aliases` to guard both alias and fallback paths.
- Checks: `python3 -m pytest _tests/test_model_help_canvas.py` → `11 passed in 0.26s`.
- Removal test: Reverting would reintroduce canonical intent tokens in quick help, causing the new regression test to fail and hiding catalog alias drift from users.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: ensure intent badges and command hints reuse the same display aliases end-to-end.
  - Talon list guardrails: add regeneration checks for `GPT/lists/*.talon-list` to fail when catalog aliases drift from on-device spoken tokens.
  - GPT persona docs: align `_build_persona_intent_docs` output with `intent_display_map` so documentation mirrors the spoken aliases surfaced in quick help.

## 2025-12-18 – Loop 173 (kind: behaviour)
- Focus: Persona & Intent Presets – align pattern picker intent commands with catalog display aliases.
- Change: `lib/modelPatternGUI.py` now resolves intent preset display names via `persona_intent_maps().intent_display_map` for both “say” hints and summary rows, retaining canonical tokens in parentheses; added `_tests/test_model_pattern_gui.py::test_pattern_canvas_uses_intent_display_alias` to lock the behaviour.
- Checks: `python3 -m pytest _tests/test_model_pattern_gui.py` → `32 passed in 0.38s`.
- Removal test: Reverting would drop display aliases from the pattern picker, causing the new regression test to fail and reintroducing divergent spoken hints compared to the catalog.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: confirm intent badges and voice hints consistently surface catalog display aliases.
  - Talon list guardrails: add regeneration checks for `GPT/lists/*.talon-list` to fail when catalog aliases drift.
  - GPT persona docs: update `_build_persona_intent_docs` to emit the same aliases shown in canvases.

## 2025-12-18 – Loop 174 (kind: behaviour) – Align suggestion GUI intent surfaces with catalog aliases
- Focus: Persona & Intent Presets – suggestion canvas (`lib/modelSuggestionGUI.py`) command hints and summaries.
- Change: `_suggestion_stance_info()` now consults `persona_intent_maps().intent_display_map` to hydrate the intent alias when preset metadata omits it; suggestion canvas rendering uses the hydrated alias for both “Say” hints and intent summaries. Added `_tests/test_model_suggestion_gui.py::test_stance_info_fetches_alias_when_not_provided` plus updated existing stance tests to expect catalog aliases.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` → `28 passed in 0.11s`.
- Removal test: Reverting would drop display aliases from suggestion rows, restoring canonical tokens and causing the refreshed regression suite to fail.
- Adversarial “what remains” check:
  - Talon list guardrails: add regeneration checks so `GPT/lists/*.talon-list` stay aligned with catalog display aliases.
  - GPT persona docs: update `_build_persona_intent_docs` to emit the same display aliases shown in help/pattern/suggestion surfaces.
  - Response canvas: confirm `lib/modelResponseCanvas.py` uses `intent_display` for recap banners to keep Concordance surfaces consistent.

## 2025-12-18 – Loop 175 (kind: guardrail/tests) – Guard Talon list regeneration against catalog drift
- Focus: Persona & Intent Presets – Talon list generation/guardrails (`scripts/tools/generate_talon_lists.py`).
- Change: generator now emits `personaPreset.talon-list` and `intentPreset.talon-list` with catalog-driven alias→canonical mappings sourced from `persona_intent_maps().intent_display_map`; guardrail tests assert the generated files contain the expected spoken/display aliases and that `--check` flags drift. Updated `_tests/test_generate_talon_lists.py` to cover the new lists and ensured list-drift fixtures in `_tests/test_axis_catalog_validate_lists_dir.py` remain green.
- Checks: `python3 -m pytest _tests/test_generate_talon_lists.py` (4 passed in 0.28s); `python3 -m pytest _tests/test_axis_catalog_validate_lists_dir.py` (17 passed in 0.97s).
- Removal test: Reverting would drop the persona/intent lists and alias coverage, causing the refreshed guardrail tests to fail and allowing Talon list drift to go undetected.
- Adversarial “what remains” check:
  - GPT persona docs: update `_build_persona_intent_docs` to emit display aliases so documentation matches the shared SSOT.
  - Response canvas: ensure `lib/modelResponseCanvas.py` surfaces `intent_display` alongside persona axes to keep recap banners aligned.
  - Consider adding an integration guard that runs `generate_talon_lists.py --check` in CI once local regeneration workflows stabilize.

## 2025-12-18 – Loop 162 (kind: behaviour)
- Focus: Persona & Intent Presets – ensure alias-only suggestions stay catalog-aligned.
- Change: Updated `GPT/gpt.py` to retain raw persona/intent alias metadata when model suggestions only provide spoken/display presets, allowing `lib/suggestionCoordinator.record_suggestions` to canonicalize via `persona_intent_maps`, and added `_tests/test_integration_suggestions.py::test_suggest_alias_only_metadata_round_trip` to cover the alias-only path end-to-end through the suggestion GUI helpers.
- Checks: `python3 -m pytest _tests/test_integration_suggestions.py` (pass; excerpt: `6 passed in 2.16s`).
- Removal test: Reverting would drop the alias-preservation path so suggestions that only supply spoken/display presets would lose persona/intent metadata, making the new integration test fail and reopening the ADR-0056 Salient Task 2 gap.
- Adversarial “what remains” check:
  - `GPT/gpt.py::_validated_persona_value`: extend coverage for alias-only intent tokens so prompt recipe commands surface canonical keys when inputs vary in case or punctuation.
  - `lib/modelSuggestionGUI.py`: add an integration slice that drives voice commands with display aliases to confirm GUI actions reuse the shared persona/intent maps.
  - Concordance guardrails: consider a CI assertion that fails when suggestion entries reach `record_suggestions` without persona/intent preset keys to complement the new integration test.

## 2025-12-18 – Loop 163 (kind: behaviour)
- Focus: Persona & Intent Presets – canonicalise alias-only suggestion metadata before reaching the coordinator.
- Change: Updated `GPT/gpt.py::_suggest_prompt_recipes_core_impl` to resolve persona/intent presets from label/spoken/display aliases ahead of `record_suggestions`, ensuring axis hints and preset keys populate even when JSON omits canonical tokens, and added `_tests/test_gpt_suggest_validation.py::test_json_suggestions_alias_only_fields_canonicalise` to guard the new behaviour.
- Checks: `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `12 passed in 4.51s`).
- Removal test: Reverting would leave alias-only suggestions without canonical persona/intent metadata upstream of `record_suggestions`, causing the new validation test to fail and risking future regressions when alternative coordinators bypass the fallback.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: extend voice-command coverage so GUI actions exercise preset aliases without relying on the coordinator fallback.
  - `GPT/gpt.py::_validated_persona_value`: tighten canonicalisation for mixed-case intent tokens provided via `intent_purpose` to close out the remaining tests-first bullet.
  - Guardrails: explore a CI assertion (or lint) that fails when suggestion payloads emit persona/intent metadata without canonical preset keys.

## 2025-12-18 – Loop 164 (kind: behaviour)
- Focus: Persona & Intent Presets – harden `_validated_persona_value` against mixed-case and punctuation-heavy aliases.
- Change: Extended `_suggest_prompt_recipes_core_impl` with `_normalise_alias_token` so persona/intent alias lookups strip punctuation and compare normalised keys before falling back to hints, and added `_tests/test_gpt_suggest_validation.py::test_json_suggestions_alias_only_fields_canonicalise` coverage for uppercase/punctuated aliases.
- Checks: `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `12 passed in 5.08s`).
- Removal test: Reverting would drop the alias normalisation path, causing the new validation test to fail and allowing hyphenated/display intent aliases to bypass canonicalisation, reintroducing the ADR-0056 Salient Task 2 regression.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: broaden voice-command regression coverage so GUI presets exercise puny-coded aliases without coordinator fallbacks.
  - `GPT/gpt.py::_canonical_persona_value`: consider sharing `_normalise_alias_token` so direct persona command entry benefits from the same sanitisation.
  - Guardrails: add a lint/test that rejects suggestion payloads whose persona/intent fields still lack canonical preset keys after normalisation.

## 2025-12-18 – Loop 165 (kind: behaviour)
- Focus: Persona & Intent Presets – align `_canonical_persona_value` with shared alias normalisation.
- Change: Promoted `_normalise_persona_alias_token` to a module helper and reused it across `_canonical_persona_value` and `_suggest_prompt_recipes_core_impl`, while extending `_canonical_persona_value` to consult `persona_intent_maps` alias tables; added `_tests/test_gpt_suggest_validation.py::test_canonical_persona_value_normalises_aliases` to cover direct canonicalisation.
- Checks: `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 4.47s`).
- Removal test: Reverting would cause `_canonical_persona_value("intent", "For-Deciding!")` to return an empty string, breaking the new test and allowing mixed-case / punctuated aliases to bypass canonicalisation in persona status surfaces.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: create a voice-command regression that ensures GUI presets round-trip aliases without relying on suggestion coordinator fallbacks.
  - Guardrails: consider a lint that asserts canonical persona/intent keys are present before suggestions are persisted.
  - `_canonical_persona_value`: evaluate whether Talon runtime persona commands should use the shared normaliser for interactive inputs.

## 2025-12-18 – Loop 166 (kind: behaviour)
- Focus: Persona & Intent Presets – ensure suggestion GUI hydrates canonical persona/intent metadata from alias-only payloads.
- Change: Updated `lib/modelSuggestionGUI.py` to share the `_normalise_alias_token` helper, normalise preset aliases before dictionary lookups, canonicalise stored labels/spoken names, and expand `_refresh_suggestions_from_state` to align cached GUI suggestions with `persona_intent_maps` output.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass; excerpt: `27 passed in 0.15s`), `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 5.12s`).
- Removal test: Reverting would leave the GUI cache with raw uppercased/punctuated aliases, causing `_tests/test_model_suggestion_gui.py::test_open_normalises_alias_only_metadata` to fail and reintroducing divergence between Suggestion GUI state and canonical persona/intent presets.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: add an integration covering voice-command driven preset selection after GUI hydration to guarantee follow-on actions receive the canonical keys.
  - `lib/suggestionCoordinator.py`: consider asserting that recorded suggestions always include canonical preset keys before dispatch to GUI surfaces.
  - Guardrails: evaluate a lint ensuring GUI hydration continues to round-trip with `persona_intent_maps` outputs when presets are added or renamed.

## 2025-12-18 – Loop 167 (kind: tests)
- Focus: Persona & Intent Presets – guard voice-command execution after alias-only hydration.
- Change: Added `_tests/test_model_suggestion_gui.py::test_run_index_normalises_alias_only_metadata`, calling `UserActions.model_prompt_recipe_suggestions_run_index` with uppercase/punctuated preset metadata and asserting the GUI cache normalises to canonical persona/intent keys before running the suggestion.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass; excerpt: `28 passed in 0.13s`), `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 4.86s`).
- Removal test: Reverting would allow the new test to fail and reopen the gap where run-index execution consumed raw alias strings instead of canonical presets.
- Adversarial “what remains” check:
  - `lib/suggestionCoordinator.py`: consider adding a guard that rejects suggestions lacking canonical preset keys before they reach GUI callers.
  - `lib/modelSuggestionGUI.py`: explore a small integration that verifies voice-command preset selection after the GUI closes, ensuring canonical metadata flows through to downstream apply routines.
  - Guardrails: investigate a CI lint that spots suggestion payloads persisting alias-only persona/intent fields without canonical keys.

## 2025-12-18 – Loop 168 (kind: guardrail/tests)
- Focus: Persona & Intent Presets – harden suggestion GUI refresh against missing catalog attributes.
- Change: Updated `lib/modelSuggestionGUI.py::_refresh_suggestions_from_state` to tolerate absent `persona_intent_maps` fields by normalising lookups through safe dict fallbacks and alias normalisation, and added `_tests/test_model_suggestion_gui.py::test_missing_persona_intent_maps_data` to assert the GUI handles stubbed map objects without preset metadata.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass; excerpt: `28 passed in 0.14s`), `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 4.49s`).
- Removal test: Reverting would reintroduce AttributeError crashes when persona/intent catalog snapshots omit preset alias tables, causing the new guard test to fail.
- Adversarial “what remains” check:
  - `lib/suggestionCoordinator.py`: consider adding a guard that rejects suggestions lacking canonical preset keys before they reach GUI callers.
  - `lib/modelSuggestionGUI.py`: consider logging a user-facing warning when hydration falls back to raw metadata so operators can detect catalog drift.
  - Guardrails: evaluate adding a CI stub that simulates partially populated `persona_intent_maps` snapshots to ensure future changes keep the refresh path resilient.

## 2025-12-18 – Loop 169 (kind: behaviour)
- Focus: Persona & Intent Presets – ensure GUI refresh handles empty suggestion feeds and logs missing catalogs.
- Change: Added an early return in `_refresh_suggestions_from_state` to short-circuit when `suggestion_entries_with_metadata()` yields no entries, and introduced a `_debug` log when `persona_intent_maps()` is unavailable so Concordance operators can detect fallback hydration.
- Checks: `python3 -m pytest _tests/test_model_suggestion_gui.py` (pass; excerpt: `28 passed in 0.13s`), `python3 -m pytest _tests/test_gpt_suggest_validation.py _tests/test_integration_suggestions.py` (pass; excerpt: `13 passed in 4.51s`).
- Removal test: Reverting would reintroduce potential `SuggestionGUIState` drift (stale data left behind) and remove the observability signal when persona catalogs fail to load.
- Adversarial “what remains” check:
  - `lib/modelSuggestionGUI.py`: consider emitting a user-facing notification when catalog hydration falls back entirely so voice users know to regenerate presets.
  - `lib/suggestionCoordinator.py`: explore rejecting empty suggestion feeds earlier to surface upstream failures.
  - Guardrails: add a test that simulates an empty suggestions list followed by a refreshed one to ensure state resets remain correct.

## 2025-12-19 – Loop 188 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – publish guardrail summaries via GitHub Actions artifacts.
- Change: Added a `history-axis-summary` upload step to `.github/workflows/test.yml` so `make ci-guardrails` outputs at `artifacts/history-axis-summaries/history-validation-summary.json` are persisted as GitHub Actions build artifacts with `if-no-files-found: warn` safeguards.
- Checks: (workflow change) `python3 -m pytest _tests/test_run_guardrails_ci.py` (pass; excerpt: `4 passed in 12.6s`).
- Removal test: Reverting would drop the upload-artifact step, leaving CI without the preserved summary and weakening ADR-0056’s guardrail telemetry requirement.
- Adversarial “what remains” check:
  - Confirm the GitHub Actions job retains artifacts across branches and adjust naming if multiple summaries are needed simultaneously.
  - Update Concordance runbooks to link to the workflow artifact for on-call retrieval once CI artifact retention policies are documented.
  - Evaluate adding an Actions-level summary annotation that links directly to the uploaded JSON for faster inspection.

## 2025-12-19 – Loop 189 (kind: guardrail/tests)
- Focus: Request Gating & Streaming – enforce artifact persistence across guardrail variants.
- Change: Updated `scripts/tools/run_guardrails_ci.sh` to require the history summary for guardrail targets (failing when absent), taught `Makefile::request-history-guardrails-fast` to emit `artifacts/history-axis-summaries/history-validation-summary.json`, and added `_tests/test_make_request_history_guardrails.py::test_make_request_history_guardrails_fast_produces_summary` plus `_tests/test_run_guardrails_ci.py::test_run_guardrails_ci_history_target_produces_summary`.
- Checks: `python3 -m pytest _tests/test_make_request_history_guardrails.py _tests/test_run_guardrails_ci.py` (pass; excerpt: `7 passed in 14.97s`).
- Removal test: Reverting would let guardrail targets succeed without persisting the summary artifact, undoing ADR-0056’s telemetry guardrail and breaking the new regression tests.
- Adversarial “what remains” check:
  - Confirm Actions artifact retention aligns with Concordance operational needs and document retrieval steps in runbooks.
  - Consider including the commit SHA or workflow run ID in artifact names when parallel guardrail runs are expected.
  - Explore adding a GitHub Actions step that surfaces a direct link to the uploaded JSON in the job summary for faster triage.


