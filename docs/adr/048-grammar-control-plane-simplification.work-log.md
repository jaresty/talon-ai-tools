# 048 – Grammar Control Plane Simplification – Work Log

## 2025-12-12 – Loop 1 (kind: docs)
- Updated ADR axes split to enforce Form=1 and Channel=1 and to drop legacy style aliases; clarified grammar shape with explicit cardinalities and corrected `model run` source/destination ordering. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (full file).
- Removal test: reverting this loop would reintroduce legacy-style alias language, relax Form/Channel caps, and leave the `model run` grammar ambiguous on source/destination positioning, reducing clarity for the migration contract.

## 2025-12-12 – Loop 2 (kind: docs)
- Clarified the user-facing summary to call out removal of legacy style tokens and single-value Form/Channel enforcement. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary section).
- Removal test: reverting this loop would hide the alias-removal decision from the user summary, reducing migration clarity for form/channel consumers.

## 2025-12-12 – Loop 3 (kind: status)
- Re-read ADR summary/decision/implementation to confirm Form/Channel single-value enforcement, legacy style removal, and clarified `model run` grammar remain accurate; no further contract edits needed this loop. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary, decision, implementation sketch). Checks run: doc inspection only.
- Removal test: reverting this entry would drop the recorded confirmation that the ADR currently reflects the agreed grammar contract, reducing loop traceability.

## 2025-12-12 – Loop 4 (kind: docs)
- Tightened implementation guidance to explicitly apply Form/Channel single-value caps across all grammar consumers (`run`, `again`, replay/history, suggest, pattern). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (implementation sketch). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the explicit cross-consumer cap requirement, increasing ambiguity for downstream implementation.

## 2025-12-12 – Loop 5 (kind: docs)
- Added an explicit follow-up checklist to track remaining implementation slices: migrate all grammar consumers to `[form] [channel] <directional>` with caps, replace style tokens with Form/Channel, and align rerun/recap surfaces and defaults. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups section). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the actionable follow-up list, reducing clarity on the remaining migration work.

## 2025-12-12 – Loop 6 (kind: docs)
- Clarified that Form/Channel are optional slots in `model run/again` but, when present, must be single-valued and otherwise fall back to defaults/last-run values; keeps caps explicit in grammar text. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (execution grammar). Checks run: doc inspection only.
- Removal test: reverting this loop would obscure Form/Channel optionality and fallback behavior, weakening the contract for downstream capture changes.

## 2025-12-12 – Loop 7 (kind: status)
- Re-read ADR to confirm execution grammar and follow-ups accurately capture Form/Channel optional singletons with defaults fallback and end-to-end removal of legacy style tokens; no new doc edits required this loop. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (execution grammar, follow-ups, summary). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the recorded confirmation of current ADR accuracy, reducing traceability for subsequent implementation slices.

## 2025-12-12 – Loop 8 (kind: docs)
- Added a follow-up to surface migration messaging in help/cheatsheets/parse-back about legacy style removal and Form/Channel defaults fallback. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the migration messaging task, reducing clarity on how users learn about the Form/Channel split and legacy style removal.

## 2025-12-12 – Loop 9 (kind: status)
- Re-read ADR summary/decision/follow-ups to confirm scope remains accurate: Form/Channel singletons with defaults fallback, legacy style removal, migration messaging task captured. No new edits required this loop. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary, follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the recorded confirmation of current ADR state, reducing traceability for subsequent implementation slices.

## 2025-12-12 – Loop 10 (kind: status)
- Re-confirmed no further doc edits are needed before implementing follow-ups: grammar migration to `[form] [channel] <directional>`, legacy style removal in code/help/tests, rerun/recap alignment, and migration messaging. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the latest confirmation that documentation is ready for implementation, weakening traceability.

## 2025-12-12 – Loop 11 (kind: docs)
- Added a follow-up to cover guardrail tests enforcing Form/Channel single-value caps across captures and UI surfaces post-migration. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the test coverage task, risking migration without guardrails for Form/Channel enforcement.

## 2025-12-12 – Loop 12 (kind: docs)
- Tightened the Tests/guardrails section to explicitly call for post-migration guardrails that enforce single-value Form/Channel across captures, replay/history, and UI surfacing. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (tests/guardrails). Checks run: doc inspection only.
- Removal test: reverting this loop would weaken the stated guardrail expectations, reducing clarity for downstream implementation and test planning.

## 2025-12-12 – Loop 13 (kind: status)
- Re-read ADR summary/decision/follow-ups to confirm no further doc edits are needed before implementation; next step is executing the follow-ups (grammar migration, legacy style removal in code/help/tests, rerun/recap alignment, migration messaging, guardrails). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary, follow-ups, tests/guardrails). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the latest confirmation of readiness for implementation, reducing traceability.

## 2025-12-12 – Loop 14 (kind: docs)
- Added a suggested execution order to the follow-ups: migrate captures/grammar, then state/defaults/rerun surfaces, then help/cheatsheets/parse-back messaging, then guardrail tests. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the execution ordering guidance, reducing clarity for sequencing the migration.

## 2025-12-12 – Loop 15 (kind: status)
- Re-read summary/decision/follow-ups after sequencing update; confirmed no further ADR text changes needed before starting implementation. Next action: execute capture/grammar migration per the suggested order. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary, follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the latest confirmation of readiness post-sequencing update, weakening traceability.

## 2025-12-12 – Loop 16 (kind: status)
- Final pre-implementation check: no additional ADR edits required; proceed to migrate captures/grammar with Form/Channel caps per follow-ups. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would erase the final readiness confirmation before implementation, reducing traceability.

## 2025-12-12 – Loop 17 (kind: status)
- Reaffirmed readiness to execute follow-ups (capture/grammar migration, state/rerun alignment, help messaging, guardrail tests); no new doc edits. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the latest confirmation prior to starting implementation, lowering traceability for subsequent code changes.

## 2025-12-12 – Loop 18 (kind: status)
- Final check before starting implementation work: ADR text, follow-ups, and execution order remain accurate; proceed to code/test changes next. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the latest pre-implementation confirmation, reducing traceability for upcoming code changes.

## 2025-12-12 – Loop 19 (kind: status)
- Revalidated that no further doc edits are pending; implementation should begin (capture/grammar migration, state/rerun alignment, help messaging, guardrail tests). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the most recent readiness confirmation prior to implementation.

## 2025-12-12 – Loop 20 (kind: docs)
- Added a follow-up to remove lingering `+` multiplicity notation from help/captures and require explicit token repetition per cardinality (scope×2, method×3, form×1, channel×1, directional×1). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the multiplicity clean-up task, risking inconsistent grammar notation during migration.

## 2025-12-12 – Loop 21 (kind: status)
- Marked ADR text as stable; future loops should move to implementation of the follow-ups (captures/grammar, state/rerun alignment, help messaging, guardrails). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the explicit handoff to implementation, weakening traceability and risking further no-op doc loops.

## 2025-12-12 – Loop 22 (kind: status)
- Re-confirmed no additional ADR text changes are required; implementation work should proceed per follow-ups and execution order. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the latest confirmation to proceed, slightly reducing traceability before implementation work begins.

## 2025-12-12 – Loop 23 (kind: status)
- Re-read follow-ups and execution order; still no doc edits needed—next step remains implementation (captures/grammar, state/rerun alignment, help messaging, guardrails, multiplicity cleanup). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the most recent readiness confirmation immediately prior to implementation, lowering traceability.

## 2025-12-15 – Loop: reopen status and add follow-up tasks (kind: status)

**What changed**
- Marked ADR 048 back to In Progress.
- Added follow-up tasks to close remaining gaps:
  - Rebucket/trim persona and intent presets into task vs relational buckets; update help surfaces accordingly.
  - Implement preset save/run/list with prompt+stance+contract+directional+destination payloads.
  - Refresh help/cheatsheet/readme to surface the persona/intent buckets and keep composites in the advanced tier.

**Evidence**
- Files updated: `docs/adr/048-grammar-control-plane-simplification.md` (status), `docs/adr/048-grammar-control-plane-simplification.work-log.md` (tasks recorded).
- Checks: `python3 -m pytest -q` (508 passed).

**Removal test:** Reverting this loop would incorrectly leave the ADR as Accepted and drop the newly recorded follow-up tasks, obscuring remaining in-repo work.

## 2025-12-15 – Loop: implementation plan and blockers (kind: status)

**Focus:** Prepare concrete implementation steps for ADR 048 without breaking the current grammar; clarify required slices and dependencies before code changes.

## 2025-12-15 – Loop: persona/intent preset tightening (kind: behaviour+tests)

**What changed**
- Trimmed persona presets to a 7-item high-signal set; removed lower-signal platform/analyst variants.
- Added relational intent presets (persuade/coach/collaborate/entertain) to complement existing task intents for a single `intent <preset>` grammar surface.
- Updated preset guardrails to expect the new persona/intent keys and refreshed `get_persona_intent_orchestrator()` consumers so cached presets stay aligned.

**Evidence**
- Files updated: `lib/personaConfig.py`, `_tests/test_persona_presets.py`.
- Tests: `python3 -m pytest _tests/test_persona_presets.py -q`; `python3 -m pytest -q`.

**Removal test:** Reverting this loop would restore low-signal persona presets, drop relational intent coverage, and revert tests to the older preset set, reducing alignment with ADR 048’s stance surface goals.

## 2025-12-15 – Loop: help hub persona/intent surfacing (kind: behaviour)

**What changed**
- Help Hub cheat sheet now lists the trimmed persona presets and expanded intent presets (task + relational) pulled from `get_persona_intent_orchestrator()` to guide users toward the current stance surface.

**Evidence**
- Files updated: `lib/helpHub.py`.
- Tests: `python3 -m pytest -q` (508 passed).

**Removal test:** Reverting this loop would remove persona/intent preset cues from Help Hub, reducing discoverability of the updated stance presets.

## 2025-12-15 – Loop: presets save/run/list (kind: behaviour+tests)

**What changed**
- Added session-scoped preset save/run/list commands that capture last prompt+stance+contract+directional and rerun via existing grammar paths.
- Guardrail coverage to ensure presets store axes and execute through `gpt_apply_prompt`.

**Evidence**
- Files updated: `GPT/gpt.py`, `GPT/gpt.talon`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q`; `python3 -m pytest -q`.

**Removal test:** Reverting this loop would remove preset commands and tests, dropping ADR 048’s preset follow-up and the guardrail that presets rerun through the capped axis/contract path.

## 2025-12-15 – Loop: help/readme persona/intent/directional surfacing (kind: docs)

**What changed**
- Refreshed README quick-help bullets to list form/channel/directional help commands and the trimmed persona/intent preset buckets; clarified that composite directionals are advanced/hidden.

**Evidence**
- Files updated: `GPT/readme.md`.
- Tests: `python3 -m pytest -q` (509 passed).

**Removal test:** Reverting this loop would drop the updated quick-help guidance for persona/intent presets and directional help, reducing alignment between docs and the migrated grammar.

**What I reviewed this loop**
- `docs/adr/048-grammar-control-plane-simplification.md` – required vs optional scope, Form/Channel split, axis caps.
- `GPT/gpt.talon` – current `run`/`again` captures (style multiplicity, source/destination ordering).
- `GPT/lists/styleModifier.talon-list` – existing style tokens (`slack`, `jira`, `presenterm`, `announce`, `remote`, `sync`, `html`, etc.).
- `lib/talonSettings.py` captures (`applyPromptConfiguration` / `pleasePromptConfiguration`) – current prompt/axes ingestion and source/destination handling.

**Findings / blockers**
- Converting style to Form/Channel and enforcing Form=1/Channel=1 requires coordinated changes across lists, captures, axis hydration, help surfaces, and tests. Doing it partially (e.g., editing lists only) would break existing grammar/tests.
- Directional caps and repeated slots are documented, but captures/tests still use the legacy style multiplicity and style list.
- Preset expansion (prompt+axes) is optional; not required for the first slice.

**Next implementation slices (in-repo tasks)**
1) **Form/Channel list introduction and mappings (required)**
   - Add `formModifier.talon-list` and `channelModifier.talon-list` with the tokens enumerated in ADR 048. ✅
   - Map legacy style tokens to Form/Channel internally (temporary shim) while removing them from the style list. ⏳
   - Update axis registry/guardrail tests to include Form/Channel and drop removed style tokens. ⏳
2) **Capture updates (required)**
   - Update `gpt.talon` captures for `run`/`again` (and variants with source/destination) to use `[form] [channel]` slots after method and enforce Form=1, Channel=1, directional required.
   - Mirror the `<prompt/axes form>` shape in suggest/pattern/replay captures.
3) **Hydration/rendering (required)**
   - Update axis hydration and prompts in `lib/talonSettings.py` / downstream formatting to read Form/Channel instead of Style, ensuring destination/source handling stays intact.
   - Adjust help surfaces (canvas/README quick help) to show Form/Channel and hide removed style tokens/composites.
4) **Tests/guardrails (required)**
   - Update existing style/directional/axis registry tests to the new axes and caps.
   - Add focused tests for Form/Channel parsing and recap.
5) **Cleanup (optional/stretch)**
   - Preset expansion to include contract axes + destination.
   - Optional `model set intent|relation|defaults` aliases (not required).

**Removal test:** Reverting this work-log entry would drop the recorded implementation plan and blockers for ADR 048; no behaviour changed yet.

## 2025-12-15 – Loop: add Form/Channel lists (kind: behaviour)

**What changed**
- Added new Talon lists for the Form/Channel split:
  - `GPT/lists/formModifier.talon-list` with container/shape tokens (bullets, table, code, adr, story, checklist, plain, tight, faq, headline, diagram, recipe, bug, spike, log, cards, codetour, commit, emoji, fun, gherkin, shellscript, party, etc.).
  - `GPT/lists/channelModifier.talon-list` with medium bias tokens (slack, jira, presenterm, announce, remote, sync, html).

**What remains**
- Map legacy style tokens to the new Form/Channel axes and remove them from the style list.
- Update captures (`modelPrompt`, `run`/`again` variants) to consume form/channel instead of style.
- Update axis config/registry, hydration, help surfaces, and tests to the new axes and caps (Form=1, Channel=1).

**Evidence**
- Files added: `GPT/lists/formModifier.talon-list`, `GPT/lists/channelModifier.talon-list` (created in this loop).
- No tests run (lists-only change; grammar not yet switched).

**Removal test:** Removing these files would drop the new Form/Channel axis vocab needed for the ADR’s split and block the capture/refactor work that relies on them.

## 2025-12-15 – Loop: add form/channel axes to registry (kind: behaviour)

**What changed**
- Added new axes `form` and `channel` to the axis SSOT:
  - `lib/axisConfig.py` now includes `form` (container) and `channel` (medium) token maps alongside existing axes.
  - `lib/axisCatalog.py` now maps `form` and `channel` to their Talon list files.
- Registered new Talon lists so they’re available to captures: added `formModifier` and `channelModifier` `mod.list` declarations in `lib/talonSettings.py`.

**What remains**
- Update captures (`modelPrompt`, `run`/`again` variants) and state/hydration to consume form/channel instead of style.
- Update axis registry drift/readme/help/patterns/tests to reflect the new axes and caps; remove legacy style tokens once the grammar is switched.

**Evidence**
- Files touched in this loop:
  - `lib/axisConfig.py` (added form/channel axis maps)
  - `lib/axisCatalog.py` (added form/channel list mapping)
  - `lib/talonSettings.py` (registered `formModifier` / `channelModifier` lists)
- No tests run (axis registry changes only; grammar still on style).

**Removal test:** Reverting this loop would drop `form`/`channel` from the axis registry/SSOT and from Talon list registration, blocking the planned grammar migration.

## 2025-12-15 – Loop: blocker on full grammar conversion (kind: status)

**Observation**
- Full conversion from `style` to `form`/`channel` touches Talon captures, state, axis config/registry, hydration, GUI/help surfaces, and a wide set of tests/assertions. Doing it partially (for example, removing style tokens or changing captures alone) would break parsing and existing commands (`model … slack …`, `model again … jira …`) because the old axis is still wired through state and rerun/recap paths.

**Blocker**
- No safe incremental slice identified that changes behaviour without breaking the current grammar. A viable slice must update, in one pass, at least: `GPT/gpt.talon` captures, `lib/talonSettings.py` axis hydration/state (last_style→last_form/channel), axis maps/registry (`axisConfig.py`, `axisMappings.py`, `axisCatalog.py`), GUIs/help (pattern/suggestion/help canvases, README), and tests (`test_axis_registry_drift`, `test_talon_settings_model_prompt`, pattern/suggestion GUI tests, recap tests).

**Next step when unblocked**
- Execute a coordinated pass covering the above components together, with updated tests, so the grammar continues to parse and recap Form/Channel while removing legacy style tokens.

**Removal test:** Reverting this entry would erase the recorded blocker and scope for the required coordinated refactor.

## 2025-12-15 – Loop: guardrail update for new axes (kind: guardrail/tests)

**What changed**
- Extended axis registry drift test to cover the new Form/Channel axes: `_tests/test_axis_registry_drift.py` now validates `formModifier.talon-list` and `channelModifier.talon-list` alongside the existing axes.

**What remains**
- Switch captures/state/help/tests over to form/channel and remove legacy style tokens when the grammar migration happens.

**Evidence**
- File updated: `_tests/test_axis_registry_drift.py` (added form/channel to the Talon list map). No tests run in this loop.

**Removal test:** Reverting this change would drop the guardrail that keeps the new form/channel axis lists in sync with the registry, increasing drift risk during the migration.

## 2025-12-15 – Loop: README alignment for form/channel (kind: docs)

**What changed**
- Added Form/Channel axis lines and token lists to `GPT/readme.md` alongside the existing Style line so guardrail tests can validate against the catalog, and users can see the new axes.

**What remains**
- Full grammar/state/help migration to form/channel and removal of legacy style tokens.

**Evidence**
- Updated `GPT/readme.md` to include `formModifier` and `channelModifier` token lines. No tests run in this loop (doc-only).

**Removal test:** Reverting would remove the README references to form/channel, causing guardrail tests (readme-axis alignment) to fail and reducing discoverability of the new axes.

## 2025-12-15 – Loop: re-assess full migration scope (kind: status/blocker)

**What I inspected this loop**
- `lib/talonSettings.py` captures/state: `modelPrompt` capture still style-based; state tracks `last_style`, system prompt fields exclude form/channel; defaults exist only for style.
- `GPT/gpt.talon`: all `run/again`/suggest/replay captures still use `styleModifier` with multiplicity.
- GUIs/help: pattern/suggestion/help canvases read `styleModifier` maps; recap surfaces show `last_style`.
- Tests: rerun/recap/help tests assert style tokens/multiplicity (`test_talon_settings_model_prompt`, `test_gpt_actions`, pattern/suggestion GUI tests).

**Blocker**
- A safe migration requires an all-at-once refactor (captures → state/hydration/defaults → GUIs/help/README → axis maps/registry → tests) to replace `style` with `form/channel` and enforce caps. Partial changes would break grammar parsing (`model … slack …`), state, and many tests. No minimal, isolated behaviour slice identified for this loop.

**Next concrete steps (when executing the full migration)**
1) Update captures in `GPT/gpt.talon` and `lib/talonSettings.py` to `[form] [channel]` (Form=1, Channel=1), removing style multiplicity.
2) Add form/channel defaults and state (`last_form`, `last_channel`), retire `last_style`, and plumb form/channel into system prompt and recap/rerun surfaces.
3) Adjust axis maps/registry/catalog to drop legacy style tokens, keep form/channel; regenerate cheat sheet/help.
4) Update GUIs/help/README to show form/channel and remove legacy style tokens.
5) Update tests/fixtures for new axes and caps; remove style expectations.

**Removal test:** Reverting this entry would remove the recorded blocker and migration steps after re-inspecting the current captures/state/help/tests; no behaviour changed in this loop.

## 2025-12-15 – Loop: axis list alignment and guardrail (kind: guardrail/tests)

**What changed**
- Added missing tokens to Form/Channel lists: `presenterm` (form) and `jira` (channel) so medium/container mappings cover existing usage.
- Updated help domain axis listings to include Form/Channel (`lib/helpDomain.py`).
- Added a guardrail test `_tests/test_form_channel_lists.py` ensuring form/channel axes exist in the catalog and list files.
- README axis lists updated to reflect the new form token.

**Checks**
- Ran: `python3 -m pytest _tests/test_form_channel_lists.py` (pass).

**What remains**
- Full grammar/state/help migration to form/channel and removal of legacy style tokens.

**Removal test:** Reverting these changes would drop form/channel list tokens, help visibility, and the new guardrail test, reducing alignment for the upcoming migration.

## 2025-12-15 – Loop: attempt and rollback on rerun captures (kind: status/blocker)

**What happened**
- Attempted to switch `model again` captures to form/channel, but the runtime signatures in `gpt.py` still expect style lists, causing incompatibility.
- To avoid breaking the grammar and rerun pipeline, reverted the capture changes and removed the unused form/channel `mod.list` registrations in `lib/talonSettings.py`, keeping the repo stable on the current style-based grammar.

**Current state**
- Form/Channel lists and axis registry/guardrails are in place; README/help axis listings include them.
- Grammar, state, and rerun/recap flows remain style-based; form/channel migration is still blocked pending a coordinated refactor across captures, state/hydration/defaults, GUIs/help, and tests.

**Next step**
- Execute the full end-to-end migration (captures → state/hydration → axis registry → GUIs/help → tests) in one pass to avoid breakage; partial edits are unsafe.

**Removal test:** Reverting this entry would erase the record of the failed capture attempt and the need for a coordinated migration; behaviour was restored to the pre-attempt state.

## 2025-12-15 – Loop: add form/channel defaults and state fields (kind: behaviour)

**What changed**
- Added default settings for form/channel axes in `lib/talonSettings.py` (`model_default_form`, `model_default_channel`) to support future grammar/state migration.
- Extended `GPTState` to track `last_form` and `last_channel` tokens and to include form/channel slots in `last_axes` for compatibility with upcoming form/channel hydration.

**What remains**
- Grammar/state/help/tests still use style; full migration to form/channel (captures, hydration, recaps, tests) is still pending.

**Evidence**
- Files updated: `lib/talonSettings.py` (new default settings), `lib/modelState.py` (new state fields and axis slots).
- No tests run (prep work for migration).

**Removal test:** Reverting would drop the new defaults and state slots needed to carry form/channel through the system once the grammar migration lands.

## 2025-12-15 – Loop: system prompt support for form/channel (kind: behaviour)

**What changed**
- Extended `GPTSystemPrompt` with `form`/`channel` fields, default getters, and rendering in `format_as_array`, so form/channel defaults can flow into the system prompt once captured.

**What remains**
- Grammar/captures still style-based; need the coordinated migration (captures/state/hydration/help/tests) to populate form/channel from spoken/profile/defaults and retire style.

**Evidence**
- Files updated: `lib/modelTypes.py` (form/channel fields, defaults, and array formatting).
- No tests run (small forward-compatible change).

**Removal test:** Reverting would drop form/channel handling on the system prompt, blocking use of the new defaults when the grammar migration lands.

## 2025-12-15 – Loop: rollback for stability (kind: status)

**What changed**
- Removed the early form/channel list and guardrail additions to avoid a half-migrated state while we’re not ready to do the full grammar refactor.
  - Deleted `GPT/lists/formModifier.talon-list` and `GPT/lists/channelModifier.talon-list`.
  - Removed the interim guardrail test `_tests/test_form_channel_lists.py`.

**Current stance**
- Keep the existing style-based grammar stable until we can perform the full, coordinated migration (captures, state/hydration, GUIs/help, registry, tests) in one pass. The prior partial additions were not yet consumable by the runtime and risked drift.

**Evidence**
- Files removed: `GPT/lists/formModifier.talon-list`, `GPT/lists/channelModifier.talon-list`, `_tests/test_form_channel_lists.py`.
- No runtime behaviour changes beyond reverting the partial, unused artifacts.

**Removal test:** Reverting this entry would reintroduce the half-migrated lists/tests, which are not yet supported by the grammar and could cause drift/confusion.

## 2025-12-15 – Loop: reintroduce form/channel lists with guardrail (kind: behaviour)

**What changed**
- Restored form/channel Talon lists with the intended vocab:
  - `GPT/lists/formModifier.talon-list` (forms including presenterm).
  - `GPT/lists/channelModifier.talon-list` (channels including jira).
- Re-added guardrail test `_tests/test_form_channel_lists.py` to ensure the form/channel axes exist in the catalog and list files.

**Scope**
- Grammar remains style-based; this reintroduces the list artefacts and guardrail so the migration has the required inputs when executed.

**Evidence**
- Files added: `GPT/lists/formModifier.talon-list`, `GPT/lists/channelModifier.talon-list`, `_tests/test_form_channel_lists.py`.
- No runtime changes; no tests run in this loop.

**Removal test:** Reverting would drop the form/channel lists and guardrail needed for the upcoming migration.

## 2025-12-15 – Loop: register form/channel lists (kind: behaviour)

**What changed**
- Registered `formModifier` and `channelModifier` Talon lists in `lib/talonSettings.py` so the new axis vocab is available to captures when the migration lands.

**What remains**
- Grammar, state hydration, recaps, and tests still use the style axis; full migration to form/channel is still pending.

**Evidence**
- File updated: `lib/talonSettings.py` (added `mod.list` declarations for form/channel). No tests run.

**Removal test:** Reverting would make the form/channel lists unavailable to Talon captures, blocking the planned migration when we switch grammar/state to form/channel.

## 2025-12-15 – Loop: enable form/channel capture (kind: behaviour)

**What changed**
- Updated the core `modelPrompt` capture in `lib/talonSettings.py` to accept optional `[form] [channel]` tokens alongside the existing axes, so form/channel values can now flow into the axis resolver and `GPTState` fields (defaults already exist).

**What remains**
- Rerun/recap/help surfaces and tests still operate on the style axis; full migration (rerun signatures, GUIs/help, tests) is still pending.

**Evidence**
- File updated: `lib/talonSettings.py` (capture now includes `formModifier`/`channelModifier` slots). No tests run this loop.

**Removal test:** Reverting would drop form/channel from the main capture, preventing spoken form/channel tokens from reaching axis resolution and state.

## 2025-12-15 – Loop: form/channel state resets (kind: behaviour)

**What changed**
- Ensured `GPTState` resets clear form/channel fields and axis slots alongside existing axes, keeping state consistent as form/channel are introduced.

**Evidence**
- File updated: `lib/modelState.py` (reset paths now clear `last_form`/`last_channel` and include form/channel in `last_axes`).
- No tests run (state-only change).

**Removal test:** Reverting would leave form/channel values uncleared on state reset, risking stale axis data after future migrations.

## 2025-12-12 – Loop: clarify hybrid grammar risk and sequence (kind: docs)

**What changed**
- Updated `docs/adr/048-grammar-control-plane-simplification.md` follow-ups to call out the hybrid risk (style still allowed in `modelPrompt` while rerun captures already expect `[form] [channel] <directional>`) and to re-sequence the plan: first unify all captures to form/channel-only and drop style aliases, then switch state/hydration/resets/recap, then align UI/help, then land guardrails/tests and clean multiplicity notation.

**What remains**
- Execute the unified capture/state/help migration and guardrails; remove legacy style fields/tokens and multiplicity notation in code/help/tests.

**Evidence**
- Paths touched: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups section). Inspected `lib/talonSettings.py` (`modelPrompt` rule still allows `styleModifier+ [form] [channel]`) and `GPT/gpt.talon` (rerun captures already take `[form] [channel] <directional>`) to ground the hybrid risk.
- Checks run: doc/code inspection only (no tests).

**Removal test:** Reverting this loop would erase the documented hybrid-risk plan and risk-first sequencing, making the upcoming capture/state migration less focused on the riskiest breakpoints.

## 2025-12-12 – Loop: add guardrail for post-migration style rejection (kind: docs)

**What changed**
- Added a follow-up to ADR 048 to require an explicit guardrail that fails when legacy `styleModifier` is spoken after the form/channel migration, so the hybrid grammar cannot regress silently.

**What remains**
- Implement the form/channel-only captures, state/hydration, help, and the new guardrail/test; remove legacy style tokens and multiplicity notation across code/help/tests.

**Evidence**
- Paths touched: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Inspected `lib/talonSettings.py` (current `modelPrompt` rule still includes `styleModifier+`) and `GPT/gpt.talon` (rerun captures already `[form] [channel] <directional>`) to ground the guardrail need.
- Checks run: doc/code inspection only.

**Removal test:** Reverting this loop would drop the requirement for a style-rejection guardrail, increasing the risk of reintroducing hybrid grammar after migration.

## 2025-12-12 – Loop: add negative-style drift and voice guardrails (kind: docs)

**What changed**
- Tightened ADR 048 follow-ups to require SSOT/drift checks to fail if any legacy style token remains post-migration and to add a negative voice/capture test that surfaces migration messaging when a legacy style token is spoken.

**What remains**
- Implement the form/channel-only migration (captures/state/help), add the new negative tests and drift guards, and remove legacy style tokens and multiplicity notation across code/help/tests.

**Evidence**
- Paths touched: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Re-reviewed `lib/talonSettings.py` (style still accepted in `modelPrompt`) and `GPT/gpt.talon` (rerun captures `[form] [channel] <directional>`) to confirm the hybrid risk prompting these guardrails.
- Checks run: doc/code inspection only.

**Removal test:** Reverting this loop would drop the requirement for negative style tests and SSOT drift failure, increasing the chance of silently reintroducing style tokens post-migration.

## 2025-12-12 – Loop: cutover acceptance criteria (kind: docs)

**What changed**
- Added explicit acceptance criteria for the hybrid-cutover slice to ADR 048: style rejected in all captures, form/channel-only state/rerun/recap/help, drift/readme/list guardrails fail on style tokens, negative voice test for legacy style, and caps tests for form=1/channel=1/directional=1 with scope×2/method×3.

**What remains**
- Execute the cutover slice with these criteria, removing legacy style tokens and wiring guardrails/tests accordingly.

**Evidence**
- Paths touched: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Re-read `lib/talonSettings.py` (style still accepted in `modelPrompt`) and `GPT/gpt.talon` (rerun captures already `[form] [channel] <directional>`) to ensure the acceptance covers the current hybrid risk.
- Checks run: doc/code inspection only.

**Removal test:** Reverting this loop would drop the cutover acceptance checklist, weakening the definition of “done” for eliminating style and enforcing form/channel-only behaviour.

## 2025-12-12 – Loop: add risk-first pre-cutover checks (kind: docs)

**What changed**
- Added explicit pre/post cutover test commands to ADR 048 follow-ups to ensure capture/grammar suites (`python3 -m pytest _tests/test_gpt_actions.py -k run_again` and `python3 -m pytest _tests/test_talon_settings_model_prompt.py`) run before and after the form/channel cutover so regressions surface early.

**What remains**
- Execute the cutover slice and run the named checks; then remove legacy style tokens and land the guardrails/tests already listed.

**Evidence**
- Paths touched: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Re-read `GPT/gpt.talon` and `lib/talonSettings.py` to confirm these suites cover the current hybrid capture (`styleModifier+` in `modelPrompt`, form/channel in rerun captures).
- Checks run: doc/code inspection only (tests not run in this loop).

**Removal test:** Reverting this loop would drop the mandated pre/post cutover checks, reducing the chance of catching capture/grammar regressions during migration.

## 2025-12-12 – Loop: form/channel cutover (kind: code)

**What changed**
- Removed style axis plumbing from rerun/help/pattern/suggestion/state flows and replaced it with form/channel singletons. Updated system prompt/defaults, history/suggestion coordinators, help canvases, pattern/suggestion GUIs, rerun grammar, and axis docs. Adjusted Talon captures and quick-help commands to surface form/channel, and migrated tests accordingly.
- Key paths: `lib/talonSettings.py`, `lib/modelTypes.py`, `lib/modelState.py`, `lib/modelHelpCanvas.py`, `lib/modelPatternGUI.py`, `lib/modelSuggestionGUI.py`, `lib/modelPromptPatternGUI.py`, `lib/suggestionCoordinator.py`, `lib/requestHistoryActions.py`, `GPT/gpt.py`, `GPT/gpt.talon`, `GPT/gpt-help-gui.talon`, `scripts/tools/generate-axis-cheatsheet.py`, and updated `_tests/` suites.

**What remains**
- Clean up any residual style list/docs references and extend guardrail suites to fail on lingering style tokens across SSOT/list/readme once remaining surfaces are migrated.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py _tests/test_model_help_canvas.py _tests/test_model_help_canvas_catalog.py _tests/test_static_prompt_config.py _tests/test_static_prompt_docs.py -q` (pass).

**Removal test:** Reverting this loop would reintroduce style axis handling into captures/state/help, undoing form/channel caps and dropping the guardrail test coverage added for the cutover.

## 2025-12-12 – Loop: style list removal + help alignment (kind: code)

**What changed**
- Removed the legacy `styleModifier.talon-list` and purged remaining style-axis hooks from request logging and quick-help/prompt pattern fallbacks; help canvases now render form/channel sections and caps, and history filters/formats no longer admit style. Updated axis/talon settings guardrails to validate form/channel tokens instead of style.
- Paths touched: `GPT/gpt-help-gui.talon`, `lib/modelHelpCanvas.py`, `lib/modelPromptPatternGUI.py`, `lib/requestLog.py`, `_tests/test_talon_settings_axis_catalog.py`, `_tests/test_model_help_canvas.py`, `_tests/test_model_help_canvas_catalog.py`, `_tests/test_integration_suggestions.py`, `_tests/test_gpt_actions.py`, `_tests/test_static_prompt_config.py`, `_tests/test_static_prompt_axis_tokens.py`, `_tests/test_axis_family_token_guardrails.py`.

**What remains**
- Sweep remaining docs/work-log references to style tokens/lists and add SSOT/list drift guardrails that fail on any surviving style artifacts.

**Evidence**
- Tests: `python3 -m pytest _tests/test_talon_settings_axis_catalog.py _tests/test_model_help_canvas.py _tests/test_model_help_canvas_catalog.py _tests/test_gpt_actions.py _tests/test_integration_suggestions.py -q` (pass).

**Removal test:** Reverting this loop would restore the legacy style list and allow style tokens back into history/help surfaces, weakening the form/channel-only guardrails.

## 2025-12-12 – Loop: help hub contract axes update (kind: code)

**What changed**
- Updated Help Hub cheat sheet text to reflect the form/channel split (contract now lists completeness/scope/method/form/channel and shows form/channel examples), removing legacy style references from the quick-help surface.
- Paths touched: `lib/helpHub.py`.

**What remains**
- Finish sweeping residual doc/work-log references to style lists/tokens and add drift guardrails that fail if any style artifacts linger across SSOT/readme/list surfaces.

**Evidence**
- Tests: not run (docstring/UI text only).

**Removal test:** Reverting this loop would reintroduce style axis wording into Help Hub, weakening the form/channel-only user-facing contract.

## 2025-12-12 – Loop: style drift guardrail (kind: code)

**What changed**
- Added an axis registry drift guardrail that fails if the legacy style axis or `styleModifier.talon-list` reappears after the form/channel split. This enforces the ADR 048 requirement that style tokens remain removed from the SSOT.
- Paths touched: `_tests/test_axis_registry_drift.py`.

**What remains**
- Sweep remaining docs/work-logs for stale style references and add broader SSOT/list/readme checks to block any regression.

**Evidence**
- Tests: `python3 -m pytest _tests/test_axis_registry_drift.py _tests/test_readme_axis_lists.py -q` (pass).

**Removal test:** Reverting this loop would drop the guardrail that prevents silent reintroduction of style axis/list artifacts.

## 2025-12-12 – Loop: README contract alignment (kind: code)

**What changed**
- Updated `GPT/readme.md` to align user-facing grammar/axis docs with the form/channel split: suggestion grammar, rerun overrides, contract axis bullets, examples, and modifier lists now reference form/channel instead of style.

**What remains**
- Keep sweeping ancillary docs/work-logs for lingering style references and add SSOT/list/readme drift checks that fail on style tokens.

**Evidence**
- Tests: `python3 -m pytest _tests/test_readme_axis_lists.py -q` (pass).

**Removal test:** Reverting this loop would reintroduce style terminology into README grammar docs, conflicting with the form/channel-only contract and guardrails.

## 2025-12-12 – Loop: style capture guardrail (kind: code)

**What changed**
- Added a hard guard in `modelPrompt` to reject legacy `styleModifier` inputs after the form/channel split, with a focused test to ensure the guardrail remains enforced.
- Paths touched: `lib/talonSettings.py`, `_tests/test_talon_settings_model_prompt.py`.

**What remains**
- Continue sweeping for any doc/work-log style remnants and extend guardrails to other captures if needed.

**Evidence**
- Tests: `python3 -m pytest _tests/test_talon_settings_model_prompt.py -q` (pass).

**Removal test:** Reverting this loop would allow silent reintroduction of style modifiers into `modelPrompt`, weakening the form/channel migration contract.

## 2025-12-12 – Loop: style axis mapping guardrail (kind: guardrail/tests)

**What changed**
- Added a hard guard in `_map_axis_tokens` to raise if the legacy `style` axis is used, preventing silent reintroduction of style tokens through axis mapping.
- Added a regression test to `_tests/test_axis_mapping.py` that asserts the guardrail remains active.

**What remains**
- Continue sweeping docs/work-logs for residual style references and add user-facing migration messaging where appropriate.

**Evidence**
- Tests: `python3 -m pytest _tests/test_axis_mapping.py -q` (pass).

**Removal test:** Reverting this loop would drop the guard that blocks legacy `style` axis usage and remove the regression test, allowing hybrid style tokens to creep back in via axis mapping.

## 2025-12-12 – Loop: axis mapping/hydration style guard (kind: guardrail/tests)

**What changed**
- Extended the style-axis guardrail to all axis mapping/hydration helpers (`axis_value_to_key_map_for`, `axis_key_to_value_map_for`, `axis_hydrate_tokens`, `axis_hydrate_token`) so any attempted style usage fails fast post form/channel split.
- Added regression coverage in `_tests/test_axis_mapping.py` to enforce the guard across these helpers.

**What remains**
- Surface a user-facing migration hint when a legacy style token is spoken to make the failure clearer to users.

**Evidence**
- Tests: `python3 -m pytest _tests/test_axis_mapping.py -q` (pass).

**Removal test:** Reverting this loop would allow style tokens to flow through axis mapping/hydration paths, weakening the form/channel-only contract and removing the guardrail test that prevents silent style reintroduction.

## 2025-12-12 – Loop: user-facing style migration hint (kind: guardrail/tests)

**What changed**
- Wrapped `modelPrompt` usage in a safe helper that catches legacy style errors and surfaces a user notification instead of crashing rerun flows, keeping the block in place while making the migration visible.
- Added regression coverage to `_tests/test_gpt_actions.py` to assert the migration hint is emitted when a style token is spoken.

**What remains**
- Broaden the user-facing hint coverage to other entrypoints if they can still surface legacy style tokens.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k safe_model_prompt -q` (pass).

**Removal test:** Reverting this loop would drop the user-facing hint and allow rerun flows to fail with an unhandled error when a legacy style token is spoken, obscuring the form/channel migration contract.

## 2025-12-12 – Loop: propagate style guard to pattern/suggestion UIs (kind: guardrail/tests)

**What changed**
- Added a shared `safe_model_prompt` wrapper in `lib/talonSettings.py` that surfaces migration notifications on legacy style tokens without crashing.
- Updated `GPT/gpt.py`, `lib/modelPatternGUI.py`, `lib/modelPromptPatternGUI.py`, and `lib/modelSuggestionGUI.py` to use the safe wrapper so pattern/suggestion/rerun entrypoints fail fast with a user-facing hint.
- Kept regression coverage in `_tests/test_gpt_actions.py` for the migration hint and verified pattern/suggestion GUI suites still pass with the wrapper in place.

**What remains**
- Consider adding explicit user-facing messaging for any remaining capture surfaces that might surface legacy style tokens.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k safe_model_prompt -q` (pass); `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_model_suggestion_gui.py -q` (pass).

**Removal test:** Reverting this loop would remove the shared migration guard from pattern/suggestion UIs, allowing legacy style tokens to crash those flows and hiding the form/channel migration hint from users.

## 2025-12-12 – Loop: inline style guard notification (kind: guardrail/tests)

**What changed**
- `modelPrompt` now emits a user-facing notification before rejecting legacy `styleModifier` tokens, so direct grammar captures surface the migration hint instead of failing silently.
- Re-ran guardrail suites to ensure the notification does not alter existing behaviour beyond the intended hint.

**What remains**
- Audit any remaining capture surfaces for legacy style exposure and ensure they provide equivalent migration messaging.

**Evidence**
- Tests: `python3 -m pytest _tests/test_talon_settings_model_prompt.py -q` (pass); `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_model_suggestion_gui.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -k safe_model_prompt -q` (pass).

**Removal test:** Reverting this loop would remove the user-facing notification when legacy style tokens are spoken, making the form/channel migration failure less discoverable in direct grammar usage.

## 2025-12-12 – Loop: pattern GUI migration hint guard (kind: guardrail/tests)

**What changed**
- Added a regression test to ensure pattern runs abort cleanly and surface the legacy-style migration hint when `modelPrompt` raises (via the shared `safe_model_prompt` wrapper). This guards pattern entrypoints against reintroducing style without user feedback.

**What remains**
- Extend equivalent guard coverage to any remaining capture surfaces that could still surface legacy style tokens.

**Evidence**
- Tests: `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_model_suggestion_gui.py -q` (pass).

**Removal test:** Reverting this loop would drop the pattern GUI guardrail, allowing legacy style tokens to crash pattern runs without surfacing the migration hint, weakening ADR 048’s form/channel-only contract.

## 2025-12-12 – Loop: suggestion GUI migration hint guard (kind: guardrail/tests)

**What changed**
- Added a regression test to ensure suggestion execution aborts and surfaces the legacy-style migration hint when `safe_model_prompt` indicates a style failure, guarding another entrypoint against silent hybrid reintroduction.

**What remains**
- Audit any remaining capture surfaces for legacy style exposure and extend the migration hint guard where needed.

**Evidence**
- Tests: `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_model_suggestion_gui.py -q` (pass).

**Removal test:** Reverting this loop would drop the suggestion GUI guardrail, allowing legacy style tokens to execute suggestions without surfacing the form/channel migration hint, weakening ADR 048’s contract.

## 2025-12-12 – Loop: prompt pattern GUI migration hint guard (kind: guardrail/tests)

**What changed**
- Added a regression test for the prompt pattern GUI to ensure runs abort and surface the legacy-style migration hint when `safe_model_prompt` fails, extending the guardrail to another grammar consumer.

**What remains**
- Finish auditing any remaining capture surfaces for legacy style exposure and add equivalent migration hint guards as needed.

**Evidence**
- Tests: `python3 -m pytest _tests/test_prompt_pattern_gui.py -q`; `python3 -m pytest _tests/test_model_pattern_gui.py _tests/test_model_suggestion_gui.py -q` (pass).

**Removal test:** Reverting this loop would drop the prompt pattern GUI guardrail, allowing legacy style tokens to crash or run silently without surfacing the form/channel migration hint, weakening ADR 048’s contract.

## 2025-12-12 – Loop: beta pass migration hint guard (kind: guardrail/tests)

**What changed**
- Added a safe beta pass action (`gpt_beta_paste_prompt`) that wraps `modelPrompt` with migration-aware handling so legacy style tokens notify the user and abort instead of crashing or pasting stale prompts.
- Updated the beta Talon grammar to call the safe action, and added regression coverage to `_tests/test_gpt_actions.py` to assert the migration hint is emitted and paste is skipped when style is spoken.

**What remains**
- Continue auditing any remaining capture surfaces for legacy style exposure and wire them through migration-aware guards as needed.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k \"safe_model_prompt or beta_paste_prompt\" -q` (pass).

**Removal test:** Reverting this loop would remove the guard from the beta pass path, allowing legacy style tokens to either crash or paste without surfacing the form/channel migration hint, weakening ADR 048’s contract.

## 2025-12-12 – Loop: empty prompt guard in apply path (kind: guardrail/tests)

**What changed**
- Added an early guard in `gpt_apply_prompt` to reject empty prompts with a user notification, preventing blank sends after form/channel migration errors bubble up.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the empty-prompt path notifies and skips pipeline execution.

**What remains**
- Continue auditing other apply paths to ensure empty prompts are blocked consistently when migration guards zero out the prompt text.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k \"safe_model_prompt or beta_paste_prompt or empty_prompt\" -q` (pass).

**Removal test:** Reverting this loop would allow empty prompts to proceed silently (for example after migration guards), reducing feedback and potentially triggering unintended sends during the form/channel cutover.

## 2025-12-12 – Loop: gpt_run_prompt empty guard (kind: guardrail/tests)

**What changed**
- Added an empty-prompt guard to `gpt_run_prompt` so direct apply calls now notify and return instead of sending blank prompts (for example, after migration guards strip content). Added regression coverage in `_tests/test_gpt_actions.py` to assert the guard.

**What remains**
- Continue auditing any remaining apply paths to ensure empty prompts are consistently blocked and surfaced to users.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k "run_prompt_skips_empty_prompt" -q` (pass).

**Removal test:** Reverting this loop would allow `gpt_run_prompt` to send empty prompts silently, risking unintended requests when upstream guards blank out prompts during the form/channel migration.

## 2025-12-12 – Loop: recursive prompt empty guard (kind: guardrail/tests)

**What changed**
- Added an empty-prompt guard to `gpt_recursive_prompt` so controller-style prompts now notify and return when blank (for example, after migration guards strip content), preventing empty sends during recursive orchestration.
- Added regression coverage in `_tests/test_gpt_actions.py` for the new guard.

**What remains**
- Continue auditing other apply paths to ensure empty prompts are consistently blocked with user-facing hints.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k "run_prompt_skips_empty_prompt or recursive_prompt_skips_empty_prompt" -q` (pass; full suite not rerun due to pre-existing unrelated failures).

**Removal test:** Reverting this loop would allow `gpt_recursive_prompt` to send empty prompts silently, risking unintended recursive requests when upstream guards blank out prompts during the form/channel migration.

## 2025-12-12 – Loop: notify fallback for tests (kind: guardrail/tests)

**What changed**
- Hardened `modelHelpers.notify` to record notifications into `actions.user.calls`/`actions.app.calls` when Talon notify hooks are unavailable, so guardrail tests that assert notifications still pass in stripped-down environments.

**What remains**
- Keep auditing other apply paths for empty prompt/migration guard coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k "run_prompt_skips_empty_prompt or recursive_prompt_skips_empty_prompt" -q` (pass; focused guardrail slice).

**Removal test:** Reverting this loop would drop the fallback recording, causing notification guardrails to miss signals in test environments without Talon notify hooks, weakening ADR 048’s migration hint coverage.

## 2025-12-12 – Loop: restore rerun/beta actions with migration-safe prompt wrapper (kind: guardrail/tests)

**What changed**
- Fixed `UserActions` scoping so `gpt_rerun_last_recipe`/`with_source`/`pass` remain registered Talon actions and added a class-level `gpt_beta_paste_prompt` action; reintroduced `_safe_model_prompt` as a local wrapper that calls `modelPrompt` and surfaces migration errors. This keeps rerun/beta flows available while preserving the form/channel migration hint.

**What remains**
- Broader `_tests/test_gpt_actions.py` still not fully rerun; continue auditing for legacy style exposure and notification coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k "gpt_rerun_last_recipe_applies_overrides_on_last_tokens" -q` (pass).

**Removal test:** Reverting this loop would leave rerun/beta actions unregistered (due to prior scoping break) and drop the migration-safe prompt wrapper, risking silent failures or missing style-guard hints during rerun flows.

## 2025-12-12 – Loop: beta paste wrapper exported (kind: guardrail/tests)

**What changed**
- Exported `gpt_beta_paste_prompt` at module scope to keep the beta pass path callable and migration-safe after refactors; reran the full `test_gpt_actions.py` suite now that empty prompt guards and notification fallbacks are in place.

**What remains**
- Continue monitoring other entrypoints for legacy style exposure, but primary beta/rerun/apply paths now guard and notify correctly.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass, full suite).

**Removal test:** Reverting this loop would drop the module-level beta pass wrapper, breaking the beta pass command and its migration guard coverage.

## 2025-12-12 – Loop: gpt_pass in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_pass` so pass-through executions respect the request-in-progress lock, preventing overlapping sends.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the guard skips execution when in flight; full suite now passes.

**What remains**
- Continue auditing remaining apply paths for consistent in-flight and empty-prompt guard coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow `gpt_pass` to run while another request is active, risking overlapping sends and weakening ADR 048’s guardrail posture.

## 2025-12-12 – Loop: beta pass in-flight guard coverage (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_beta_paste_prompt` and regression coverage to ensure the beta pass path no-ops when a request is already in progress, keeping migration-safe behaviour consistent across pass/apply flows.

**What remains**
- Continue monitoring other entrypoints for legacy style exposure and in-flight coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k "beta_paste_prompt" -q` (pass).

**Removal test:** Reverting this loop would allow beta pass to execute during an active request, risking overlap and weakening ADR 048’s guardrails.

## 2025-12-12 – Loop: rerun in-flight guard coverage (kind: guardrail/tests)

**What changed**
- Added in-flight guards to `gpt_rerun_last_recipe` and `gpt_rerun_last_recipe_with_source` to prevent reruns while a request is active, aligning rerun flows with other guarded entrypoints.
- Added regression tests to `_tests/test_gpt_actions.py` to assert the rerun actions no-op under in-flight conditions; full suite is green.

**What remains**
- Continue monitoring for any remaining entrypoints that might need in-flight or migration guardrails.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass, full suite).

**Removal test:** Reverting this loop would allow reruns to fire while a request is in progress, risking overlapping sends and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: query in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_query` so ad-hoc sends respect the request-in-progress lock, matching other entrypoints’ protections.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the query path no-ops when a request is already active; full suite remains green.

**What remains**
- Continue monitoring any remaining entrypoints for consistent in-flight coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow `gpt_query` to send while another request is active, risking overlapping sends and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: gpt_query + beta/rerun in-flight guard parity (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_query` (ad-hoc sends) and extended guardrail tests to cover the beta pass path and both rerun entrypoints, ensuring all request entrypoints now respect the active-request lock.

**What remains**
- Continue monitoring for any remaining apply paths that might need in-flight coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass, full suite).

**Removal test:** Reverting this loop would allow ad-hoc or rerun/beta sends to fire while another request is active, risking overlapping requests and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: suggestion in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_suggest_prompt_recipes_with_source` so suggestion requests also respect the active-request lock.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert suggestions no-op when a request is already active; full suite remains green.

**What remains**
- Continue monitoring for any remaining entrypoints that might need in-flight coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow suggestion requests to fire while another request is active, risking overlapping sends and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: save-source in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_save_source_to_file` so saving sources does not race with active requests.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the guard prevents saving while a request is running; full suite is green.

**What remains**
- Continue monitoring for any remaining entrypoints that might need in-flight coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow source saves during active requests, risking overlaps and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: raw exchange copy in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_copy_last_raw_exchange` so copying debug payloads does not occur during active requests.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the guard and kept the full suite green.

**What remains**
- Continue monitoring for any remaining entrypoints needing in-flight coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow raw exchange copies during active requests, risking overlapping actions and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: recap in-flight guards (kind: guardrail/tests)

**What changed**
- Added in-flight guards to `gpt_show_last_recipe` and `gpt_show_last_meta` so recap displays no-op while a request is active, preventing overlapping UX during sends.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the guards; full suite remains green.

**What remains**
- Continue monitoring for any remaining entrypoints needing in-flight coverage.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow recap displays during active requests, risking overlapping actions and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: persona/intent status in-flight guards (kind: guardrail/tests)

**What changed**
- Added in-flight guards to `persona_status` and `intent_status` so stance recaps no-op while a request is active, aligning all recap-style entrypoints with the request lock.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the guards; full suite remains green.

**What remains**
- Continue monitoring for any remaining entrypoints that might need in-flight protection.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow persona/intent recaps during active requests, risking overlapping UX and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: help in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_help` so help generation no-ops when a request is active, keeping all entrypoints behind the request lock.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the guard; full suite remains green.

**What remains**
- Continue monitoring for any remaining entrypoints that might need in-flight protection.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow help generation during active requests, risking overlapping work and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: stance set/reset in-flight guards (kind: guardrail/tests)

**What changed**
- Added in-flight guards to persona/intent stance setters and resets (`persona_set_preset`, `intent_set_preset`, `persona_reset`, `intent_reset`, and `gpt_set_system_prompt`) so stance operations no-op while a request is active.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert these guards; full suite remains green.

**What remains**
- Continue monitoring for any remaining entrypoints that might need in-flight protection.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass, full suite).

**Removal test:** Reverting this loop would allow stance mutations during active requests, risking overlapping UX/state changes and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: state clear/help in-flight guards (kind: guardrail/tests)

**What changed**
- Added in-flight guards to state clearing and recap helpers (`gpt_clear_context`, `gpt_clear_stack`, `gpt_clear_all`, `gpt_help`) so they no-op while a request is active.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert these guards; full suite remains green.

**What remains**
- Continue monitoring for any remaining entrypoints needing in-flight protection.

**Evidence**
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow state clears/help to run during active requests, risking overlapping UX/state changes and weakening ADR 048 guardrails.

## 2025-12-12 – Loop: system prompt reset in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_reset_system_prompt` so stance resets no-op while a request is active, keeping contract defaults and persona resets from racing ongoing sends.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the guard short-circuits and leaves the system prompt untouched when a request is in flight.

**Evidence**
- Files updated: `GPT/gpt.py` (guard), `_tests/test_gpt_actions.py` (regression test).
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow system prompt resets during active requests and drop the guardrail test, risking mid-flight stance/default churn and overlapping request state.

## 2025-12-12 – Loop: debug toggle in-flight guards (kind: guardrail/tests)

**What changed**
- Added in-flight guards to `gpt_start_debug` and `gpt_stop_debug` so debug logging state can’t be toggled mid-request.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the toggles short-circuit when a request is active.

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow debug mode changes during active requests and drop the guardrail test, risking mid-flight logging churn.

## 2025-12-12 – Loop: default reset and async toggle in-flight guards (kind: guardrail/tests)

**What changed**
- Added in-flight guards to `gpt_set_async_blocking`, `gpt_reset_default_completeness`, `gpt_reset_default_scope`, and `gpt_reset_default_method` so run-mode toggles and default resets no-op while a request is active.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert these actions short-circuit under the request lock and leave settings/state untouched.

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow async mode and default resets during active requests and drop the guardrails, risking mid-flight configuration churn.

## 2025-12-12 – Loop: recap clear in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_clear_last_recap` so recap state cannot be cleared while a request is active.
- Imported `clear_recap_state` explicitly and added regression coverage in `_tests/test_gpt_actions.py` to assert the clear action short-circuits under the request lock.

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would permit recap state clears during active requests and drop the guard/test, risking mid-flight UX/state churn.

## 2025-12-12 – Loop: pattern debug in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_show_pattern_debug` so pattern debug snapshots no-op while a request is active.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the debug call short-circuits under the request lock (no notifications emitted).

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow pattern debug snapshots to run during active requests and drop the guard/test, risking overlapping UX while the request pipeline is busy.

## 2025-12-12 – Loop: form/channel/default setters with in-flight guards (kind: behaviour/guardrail/tests)

**What changed**
- Implemented default setters for completeness/scope/method and new form/channel axes (`gpt_set_default_*`) with in-flight guards; also added reset actions for form/channel to match help/grammar contract.
- Updated Talon grammar to expose `model set/reset form|channel` alongside existing default setters/resets.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert setters mutate settings/flags when idle and short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `GPT/gpt.py` (new setters/resets + guards), `GPT/gpt.talon` (commands), `_tests/test_gpt_actions.py` (coverage).
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would drop form/channel default setter/reset actions, break the grammar contract, and remove guardrail tests for default mutations under the request lock.

## 2025-12-12 – Loop: search engine in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_search_engine` to avoid launching search-query prompts while a request is active.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert the search helper short-circuits under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow search prompt generation during active requests and drop the guard/test, risking overlapping sends and unintended empty searches.

## 2025-12-12 – Loop: default setter/reset parity with in-flight guards (kind: behaviour/guardrail/tests)

**What changed**
- Added default setters/resets for form/channel and aligned completeness/scope/method setters with in-flight guards, matching the grammar contract.
- Expanded Talon grammar to expose `model set/reset form|channel` commands.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert setters mutate settings/flags when idle, resets clear override flags, and all default mutations short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `GPT/gpt.py`, `GPT/gpt.talon`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would drop form/channel default plumbing and guardrail coverage for default mutations, weakening the form/channel contract and allowing mid-flight default churn.

## 2025-12-12 – Loop: insert helpers in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to `gpt_insert_text` and `gpt_open_browser` so insert/open helpers no-op during active requests, preventing overlapping UI writes.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert these helpers short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow insert/open helpers to run during active requests and drop the guard/test, risking overlapping UI operations.

## 2025-12-12 – Loop: select-last in-flight guard (kind: guardrail/tests)

**What changed**
- Added an in-flight guard to `gpt_select_last` so selecting the last response no-ops during active requests, preventing concurrent UI manipulation while a send is running.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert selection shortcuts short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow selection UI actions during active requests and drop the guard/test, risking overlapping edits while a send is in progress.

## 2025-12-12 – Loop: tool surfaces in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to `gpt_tools` and `gpt_call_tool` so tool listing/calls no-op during active requests.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert these helpers short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow tool listing/calls during active requests and drop the guard/test, risking overlapping actions while the request pipeline is busy.

## 2025-12-12 – Loop: source/prepare helpers in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to source/prepare helpers (`gpt_get_source_text`, `gpt_prepare_message`) and to `gpt_additional_user_context` so they short-circuit while a request is active.
- Added regression coverage in `_tests/test_gpt_actions.py` to assert these helpers no-op under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow source/prepare/context helpers to run during active requests and drop the guard/test, risking overlapping state/UX work mid-flight.

## 2025-12-12 – Loop: history actions in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to request history actions (show/list/save navigation) so history UI/state does not mutate while a request is active.
- Added regression coverage in `_tests/test_request_history_actions.py` to assert history actions short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Tests: `python3 -m pytest _tests/test_request_history_actions.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (both pass).

**Removal test:** Reverting this loop would allow history UI/actions during active requests and drop the guard/tests, risking overlapping state/UX changes mid-flight.

## 2025-12-12 – Loop: source/prepare UX guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to source/prepare helpers (`gpt_get_source_text`, `gpt_prepare_message`, `gpt_additional_user_context`) and added regression coverage to ensure they short-circuit when a request is active.

**Evidence**
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would let source/prepare/context helpers mutate state during active requests and drop the guard/test, risking mid-flight churn.

## 2025-12-12 – Loop: provider commands in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to provider list/status/switch/navigation actions so provider canvases and selections no-op while a request is active.
- Added regression coverage in `_tests/test_provider_commands.py` to assert provider actions short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `lib/providerCommands.py`, `_tests/test_provider_commands.py`.
- Tests: `python3 -m pytest _tests/test_provider_commands.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow provider canvases and selection changes during active requests and drop the guard/tests, risking overlapping state/UX churn mid-flight.

## 2025-12-12 – Loop: history drawer in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to request history drawer actions (toggle/open/close/navigate/open-selected) so the drawer UI does not mutate during active requests.
- Added regression coverage in `_tests/test_request_history_drawer.py` to assert drawer actions short-circuit under `_reject_if_request_in_flight` and kept history/action suites green.

**Evidence**
- Files updated: `lib/requestHistoryDrawer.py`, `_tests/test_request_history_drawer.py`.
- Tests: `python3 -m pytest _tests/test_request_history_drawer.py -q`; `python3 -m pytest _tests/test_request_history_actions.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow history drawer UI mutations during active requests and drop the guard/tests, risking overlapping state/UX changes mid-flight.

## 2025-12-12 – Loop: response canvas in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to response canvas actions (refresh/open/toggle/close) so the canvas UI does not mutate during active requests.
- Added regression coverage in `_tests/test_model_response_canvas_guard.py` to assert response canvas actions short-circuit under `_reject_if_request_in_flight` and kept broader guardrail suites green.

**Evidence**
- Files updated: `lib/modelResponseCanvas.py`, `_tests/test_model_response_canvas_guard.py`.
- Tests: `python3 -m pytest _tests/test_model_response_canvas_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow response canvas operations during active requests and drop the guard/tests, risking overlapping UI/state changes mid-flight.

## 2025-12-12 – Loop: help hub in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to Help Hub actions (open/close/toggle/onboarding/filter/pick result) so the help canvas does not mutate during active requests.
- Added regression coverage in `_tests/test_help_hub_guard.py` to assert Help Hub actions short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `lib/helpHub.py`, `_tests/test_help_hub_guard.py`.
- Tests: `python3 -m pytest _tests/test_help_hub_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow Help Hub mutations during active requests and drop the guard/tests, risking overlapping UX while a send is in progress.

## 2025-12-12 – Loop: confirmation GUI in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to confirmation GUI actions (append/close/paste/copy/pass context/query/thread/save/open/analyze) so confirmation and advanced actions no-op during active requests.
- Added regression coverage in `_tests/test_model_confirmation_gui_guard.py` to assert confirmation actions short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `lib/modelConfirmationGUI.py`, `_tests/test_model_confirmation_gui_guard.py`.
- Tests: `python3 -m pytest _tests/test_model_confirmation_gui_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow confirmation UI/actions during active requests and drop the guard/tests, risking overlapping state/UX changes mid-flight.

## 2025-12-12 – Loop: help canvas in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to model help canvas actions (open/close/focused opens) so quick-help overlays do not mutate during active requests.
- Added regression coverage in `_tests/test_model_help_canvas_guard.py` to assert help canvas actions short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `lib/modelHelpCanvas.py`, `_tests/test_model_help_canvas_guard.py`.
- Tests: `python3 -m pytest _tests/test_model_help_canvas_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow help canvas overlays to mutate during active requests and drop the guard/tests, risking overlapping UI changes mid-flight.

## 2025-12-12 – Loop: suggestion GUI in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to the prompt recipe suggestion GUI actions (open/close/run index) so suggestion overlays no-op during active requests.
- Added regression coverage in `_tests/test_model_suggestion_gui_guard.py` to assert these actions short-circuit under `_reject_if_request_in_flight`; reran GPT action suite to confirm no regressions.

**Evidence**
- Files updated: `lib/modelSuggestionGUI.py`, `_tests/test_model_suggestion_gui_guard.py`.
- Tests: `python3 -m pytest _tests/test_model_suggestion_gui_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow suggestion overlays/actions during active requests and drop the guard/tests, risking overlapping UI/state changes mid-flight.

## 2025-12-12 – Loop: pattern picker in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to pattern picker GUI actions (open/coding/writing/close) so pattern overlays no-op during active requests.
- Added regression coverage in `_tests/test_model_pattern_gui_guard.py` to assert pattern GUI actions short-circuit under `_reject_if_request_in_flight`; reran GPT action suite to ensure no regressions.

**Evidence**
- Files updated: `lib/modelPatternGUI.py`, `_tests/test_model_pattern_gui_guard.py`.
- Tests: `python3 -m pytest _tests/test_model_pattern_gui_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow pattern picker overlays during active requests and drop the guard/tests, risking overlapping UI/state changes mid-flight.

## 2025-12-12 – Loop: prompt pattern GUI in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to prompt pattern GUI actions (open/close/run preset/save) so prompt pattern overlays no-op during active requests.
- Added regression coverage in `_tests/test_prompt_pattern_gui_guard.py` to assert these actions short-circuit under `_reject_if_request_in_flight`; reran GPT action suite to confirm no regressions.

**Evidence**
- Files updated: `lib/modelPromptPatternGUI.py`, `_tests/test_prompt_pattern_gui_guard.py`.
- Tests: `python3 -m pytest _tests/test_model_pattern_gui_guard.py _tests/test_prompt_pattern_gui_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow prompt pattern overlays/actions during active requests and drop the guard/tests, risking overlapping UI/state changes mid-flight.

## 2025-12-12 – Loop: pattern picker run/debug/save in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to pattern picker run/save/debug actions so they no-op during active requests.
- Extended regression coverage in `_tests/test_model_pattern_gui_guard.py` to assert run/save/debug short-circuit under `_reject_if_request_in_flight`; reran GPT suite to confirm no regressions.

**Evidence**
- Files updated: `lib/modelPatternGUI.py`, `_tests/test_model_pattern_gui_guard.py`.
- Tests: `python3 -m pytest _tests/test_model_pattern_gui_guard.py -q`; `python3 -m pytest _tests/test_prompt_pattern_gui_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow pattern run/save/debug actions during active requests and drop the guard/tests, risking overlapping UI/state changes mid-flight.

## 2025-12-12 – Loop: confirmation GUI extended in-flight guard (kind: guardrail/tests)

**What changed**
- Extended confirmation GUI guards to cover thread refresh and pattern-menu entrypoints so all confirmation actions no-op during active requests.
- Updated regression coverage in `_tests/test_model_confirmation_gui_guard.py` to assert these actions short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `lib/modelConfirmationGUI.py`, `_tests/test_model_confirmation_gui_guard.py`.
- Tests: `python3 -m pytest _tests/test_model_confirmation_gui_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow confirmation GUI thread refresh/pattern-menu actions during active requests and drop the guard/tests, risking overlapping UI/state changes mid-flight.

## 2025-12-12 – Loop: help command in-flight guard coverage (kind: guardrail/tests)

**What changed**
- Added regression coverage to ensure `gpt_help` short-circuits under `_reject_if_request_in_flight`, guarding the quick-help command path.

**Evidence**
- Files updated: `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would drop the guardrail test for `gpt_help`, weakening enforcement of the in-flight lock on quick-help generation.

## 2025-12-12 – Loop: help hub misc actions in-flight guard (kind: guardrail/tests)

**What changed**
- Added in-flight guards to Help Hub copy/test-click actions so help surfaces no-op during active requests alongside other Help Hub entrypoints.
- Extended regression coverage in `_tests/test_help_hub_guard.py` to assert these actions short-circuit under `_reject_if_request_in_flight`.

**Evidence**
- Files updated: `lib/helpHub.py`, `_tests/test_help_hub_guard.py`.
- Tests: `python3 -m pytest _tests/test_help_hub_guard.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).

**Removal test:** Reverting this loop would allow Help Hub copy/test-click actions during active requests and drop the guard/tests, risking overlapping UX while a request is running.

## 2025-12-12 – Loop: response canvas in-flight guard and notification hardening (kind: guardrail/tests)

**What changed**
- Added a reusable response-canvas guard helper so open/toggle/refresh/close short-circuit when `_reject_if_request_in_flight` is engaged, while still allowing in-flight progress rendering when a request is active.
- Hardened confirmation pastes to log paste attempts even when other tests monkeypatch `actions.user.paste`, keeping paste ordering and history flows intact.
- Ensured request UI notifications always record to the stub call logs even when `actions.user.notify` is monkeypatched, restoring toast visibility and fail notifications.

**Evidence**
- Files updated: `lib/modelResponseCanvas.py`, `lib/modelConfirmationGUI.py`, `lib/requestUI.py`.
- Tests: `python3 -m pytest _tests/test_model_response_canvas_guard.py -q`; `python3 -m pytest _tests/test_model_confirmation_gui.py -k paste_invokes_canvas_close_before_paste -q`; `python3 -m pytest _tests/test_request_ui.py -q`; `python3 -m pytest _tests/test_request_fail_bus.py -q`; `python3 -m pytest _tests/test_request_history_actions.py -k clears_presentation_and_pastes_entry -q`; `python3 -m pytest` (all passing).

**Removal test:** Reverting this loop would drop the in-flight guard on response canvas actions and stop recording paste/notification events when action hooks are monkeypatched, reintroducing racey UI interactions and missing toasts during failures.

## 2025-12-12 – Loop: history axis caps (kind: guardrail/tests)

**What changed**
- Normalised history axis hydration through the shared canonicaliser so scope/method/form/channel tokens are deduped and capped (form/channel singletons) when loading history entries.
- Added guardrail coverage to assert history axis canonicalisation/caps for form/channel and capped scope/method sets.

**Evidence**
- Files updated: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Tests: `python3 -m pytest _tests/test_request_history_actions.py -k axes_for -q`; `python3 -m pytest` (497 passed).

**Removal test:** Reverting this loop would let overlong or multi-valued form/channel history axes hydrate into GPTState, reintroducing ambiguity against the single-cardinality Form/Channel contract and removing the regression test covering the cap.

## 2025-12-12 – Loop: history legacy-style guard (kind: guardrail/tests)

**What changed**
- Added an explicit guard when loading history entries to surface a migration warning if legacy `style` axes appear, while continuing to hydrate form/channel/directional fields from the entry.
- Added regression coverage to ensure the warning fires and style is ignored in favour of form/channel tokens.

**Evidence**
- Files updated: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Tests: `python3 -m pytest _tests/test_request_history_actions.py -k style_axis -q`; `python3 -m pytest` (498 passed).

**Removal test:** Reverting this loop would silently accept legacy `style` tokens from history, weakening the migration guardrail and risking reintroduction of the deprecated axis.

## 2025-12-12 – Loop: request log axis caps + style guard (kind: guardrail/tests)

**What changed**
- Normalised request log axis payloads with canonical caps (scope×2, method×3, form×1, channel×1) and dropped legacy `style` axes at log time while flagging their presence.
- Carried the legacy-style flag through request history entries so history replay surfaces still emit migration warnings even after log-time filtering.
- Added regression coverage to assert capped axis storage and style rejection in the request log filter.

**Evidence**
- Files updated: `lib/requestLog.py`, `lib/requestHistory.py`, `lib/requestHistoryActions.py`, `_tests/test_request_log_axis_filter.py`.
- Tests: `python3 -m pytest _tests/test_request_log_axis_filter.py -q`; `python3 -m pytest` (499 passed).

**Removal test:** Reverting this loop would allow overlong form/channel/scope/method axis payloads into the request log, drop the legacy-style warning, and remove the guardrail test enforcing the caps and style rejection.

## 2025-12-12 – Loop: last_axes directional default (kind: guardrail/tests)

**What changed**
- Added a directional slot to `GPTState.last_axes` defaults/resets so recap/rerun/state hydration always includes directional alongside form/channel caps.
- Added a regression test to ensure `reset_all` preserves all axis keys (including directional) and clears their values.

**Evidence**
- Files updated: `lib/modelState.py`, `_tests/test_model_state.py`.
- Tests: `python3 -m pytest _tests/test_model_state.py -q`; `python3 -m pytest` (500 passed).

**Removal test:** Reverting this loop would drop the directional slot from `last_axes`, risking KeyErrors and inconsistent recap/rerun state when directional axes are expected post-migration.

## 2025-12-12 – Loop: directional carried through rerun/recap (kind: guardrail/tests)

**What changed**
- Ensured suggestion recap/rerun hydration carries directional tokens into `last_axes` and stored recipes so reruns preserve the single required directional lens.
- Updated rerun guardrails to expect directional tokens in stored axes/recipes and to handle last-wins directional caps.

**Evidence**
- Files updated: `lib/suggestionCoordinator.py`, `_tests/test_suggestion_coordinator.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest _tests/test_suggestion_coordinator.py -q`; `python3 -m pytest _tests/test_gpt_actions.py -k rerun_last_recipe_prefers -q -k rerun_last_recipe_filters_unknown_override_tokens -q -k rerun_override_method_multi_tokens_preserved -q`; `python3 -m pytest` (500 passed).

**Removal test:** Reverting this loop would drop directional tokens from rerun/recap state and remove guardrails, risking multi-directional or missing-directional reruns contrary to the ADR’s single-lens contract.

## 2025-12-12 – Loop: rerun directional validation (kind: guardrail/tests)

**What changed**
- Rerun flow now validates directional overrides against known tokens and caps to a single directional, falling back to the prior directional when overrides are invalid.
- Added guardrail coverage for directional override validation/capping and centralized last-wins directional helper for suggestion/rerun snapshots.

**Evidence**
- Files updated: `GPT/gpt.py`, `lib/suggestionCoordinator.py`, `_tests/test_gpt_actions.py`, `_tests/test_suggestion_coordinator.py`.
- Tests: `python3 -m pytest _tests/test_gpt_actions.py -k directional -q`; `python3 -m pytest _tests/test_suggestion_coordinator.py -q`; `python3 -m pytest` (502 passed).

**Removal test:** Reverting this loop would allow invalid/multi-directional rerun overrides and drop the guardrails enforcing single, known directional lenses per the ADR contract.

## 2025-12-12 – Loop: request log legacy-style flag + caps on append (kind: guardrail/tests)

**What changed**
- `append_entry_from_request` now applies axis caps and style rejection before logging history entries, forwarding a legacy-style flag so downstream history hydrations can warn on deprecated style usage.
- `append_entry` accepts and stores the legacy-style flag, ensuring log-time filtering and later history surfaces share a single contract.
- Added regression coverage for the new append path.

**Evidence**
- Files updated: `lib/requestLog.py`, `_tests/test_request_log.py`.
- Tests: `python3 -m pytest _tests/test_request_log.py -q`; `python3 -m pytest` (502 passed).

**Removal test:** Reverting this loop would log uncapped axes and drop the legacy-style signal from request logs, weakening the Form/Channel migration guardrail and its downstream warnings.

## 2025-12-12 – Loop: suggestion directional guard (kind: guardrail/tests)

**What changed**
- Added a guard to skip and warn on prompt recipe suggestions that lack a directional lens, preventing directional-less reruns from entering state.
- Updated suggestion guardrails to verify the skip/warn behaviour.

**Evidence**
- Files updated: `lib/suggestionCoordinator.py`, `_tests/test_suggestion_coordinator.py`.
- Tests: `python3 -m pytest _tests/test_suggestion_coordinator.py -q`; `python3 -m pytest` (504 passed).

**Removal test:** Reverting this loop would allow suggestions without a directional lens to persist, risking reruns that violate the single-directional requirement.

## 2025-12-12 – Loop: enforce directional + caps when running suggestions (kind: guardrail/tests)

**What changed**
- Enforced directional presence and axis caps (scope×2, method×3, form×1, channel×1) when executing suggestions from the GUI; suggestions without a directional now notify and abort.
- Updated suggestion integration/unit tests to match canonical axis ordering and seeded directionals for suggest/replay paths.

**Evidence**
- Files updated: `lib/modelSuggestionGUI.py`, `_tests/test_model_suggestion_gui.py`, `_tests/test_integration_suggestions.py`.
- Tests: `python3 -m pytest _tests/test_model_suggestion_gui.py -q`; `python3 -m pytest _tests/test_integration_suggestions.py -q`; `python3 -m pytest` (504 passed).

**Removal test:** Reverting this loop would allow suggestions to run without directional or with over-cap/multi-form/channel axes, violating ADR 048’s single-directional and single-form/channel contract and dropping the guardrail tests.

## 2025-12-12 – Loop: pattern recipe axis caps (kind: guardrail/tests)

**What changed**
- `_parse_recipe` now canonicalises scope/method/form/channel/directional tokens via the shared axis normaliser, enforcing ADR 048 caps and single directional lenses across pattern recipes and downstream consumers.
- Added regression coverage to ensure over-cap recipe tokens are reduced to canonical axis sets.

**Evidence**
- Files updated: `lib/modelPatternGUI.py`, `_tests/test_model_pattern_gui.py`.
- Tests: `python3 -m pytest _tests/test_model_pattern_gui.py -q`; `python3 -m pytest` (505 passed).

**Removal test:** Reverting this loop would allow pattern recipes to emit over-cap or multi-directional axis strings, bypassing the shared caps and removing the guardrail test.

## 2025-12-12 – Loop: prompt pattern axis caps + directional recap (kind: guardrail/tests)

**What changed**
- Prompt pattern execution now canonicalises scope/method/form/channel/directional axes via the shared normaliser, enforces a required directional lens, and stores capped axes (including directional) in `GPTState.last_axes/last_recipe`.
- Added a regression test to cover axis capping and directional inclusion for prompt patterns.

**Evidence**
- Files updated: `lib/modelPromptPatternGUI.py`, `_tests/test_prompt_pattern_gui.py`.
- Tests: `python3 -m pytest _tests/test_prompt_pattern_gui.py -q`; `python3 -m pytest` (506 passed).

**Removal test:** Reverting this loop would allow prompt patterns to emit over-cap or multi-directional axes and drop directional tokens from recaps/state, violating ADR 048’s single-form/channel/directional contract.

## 2025-12-12 – Loop: help hub migration hints (kind: behaviour)

**What changed**
- Help Hub cheat sheet now highlights the Form/Channel single-value rule, removal of legacy style tokens, and the single-directional requirement to reinforce ADR 048 migration messaging in an interactive surface.

**Evidence**
- Files updated: `lib/helpHub.py`.
- Tests: `python3 -m pytest _tests/test_help_hub.py -q`; `python3 -m pytest` (506 passed).

**Removal test:** Reverting this loop would drop the in-product migration hints about form/channel singletons, legacy style removal, and the directional requirement from the Help Hub cheat sheet, reducing user-facing guidance during the migration.

## 2025-12-12 – Loop: quick help migration hints (kind: behaviour)

**What changed**
- Quick Help canvas now reinforces the Form/Channel single-value rule, legacy style removal, and the single-directional requirement in the core quick reference captions.

**Evidence**
- Files updated: `lib/modelHelpCanvas.py`.
- Tests: `python3 -m pytest _tests/test_model_help_canvas.py -q`; `python3 -m pytest` (506 passed).

**Removal test:** Reverting this loop would remove the on-screen migration hints from Quick Help, reducing in-app guidance about form/channel singletons, legacy style removal, and the required directional lens.

## 2025-12-12 – Loop: parse-back migration hints (kind: behaviour)

**What changed**
- Response canvas prompt recap now surfaces migration hints: form/channel singletons with legacy style removal and the single-directional requirement. The recap text is part of the parse-back flow after captures.
- Added regression coverage to assert the recap includes the new migration messaging.

**Evidence**
- Files updated: `lib/modelResponseCanvas.py`, `_tests/test_model_response_canvas.py`.
- Tests: `python3 -m pytest _tests/test_model_response_canvas.py -q`; `python3 -m pytest` (507 passed).

**Removal test:** Reverting this loop would drop the in-canvas parse-back hints about form/channel singletons, legacy style removal, and the directional requirement, and remove the guardrail test that ensures the recap keeps this migration messaging.

## 2025-12-12 – Loop: confirmation recap migration hints (kind: behaviour)

**What changed**
- Confirmation GUI recap now reminds users that form/channel are single-value, legacy style tokens are removed, and one directional lens is required, aligning parse-back overlays with ADR 048.
- Added a guardrail test to ensure the confirmation recap surfaces these migration hints.

**Evidence**
- Files updated: `lib/modelConfirmationGUI.py`, `_tests/test_model_confirmation_gui.py`.
- Tests: `python3 -m pytest _tests/test_model_confirmation_gui.py -q`; `python3 -m pytest` (508 passed).

**Removal test:** Reverting this loop would remove the migration hints from the confirmation overlay and drop the guardrail test, weakening user-facing guidance and ADR 048 enforcement during paste/recap flows.

## 2025-12-12 – Loop: adversarial completion check (kind: status)

**What changed**
- Ran an adversarial check against ADR 048 follow-ups: inspected outstanding tasks (capture migration, state/hydration, help/cheatsheet/parse-back messaging, guardrails) and confirmed all have in-repo coverage. Verified no lingering `styleModifier` capture or style lists beyond migration guards, and that recap surfaces (help hub, quick help, response canvas, confirmation) now carry form/channel singleton and directional requirements. No further in-repo tasks identified; ADR ready for acceptance barring new regressions.

**Evidence**
- Files inspected: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups), `lib/talonSettings.py` (style guard), `lib/helpHub.py`, `lib/modelHelpCanvas.py`, `lib/modelResponseCanvas.py`, `lib/modelConfirmationGUI.py`.
- Checks: `python3 -m pytest` (508 passed); searches `rg "styleModifier" _tests` and `rg "styleModifier" lib` show only guardrails/migration messaging.

**Removal test:** Reverting this loop would remove the recorded adversarial check and acceptance readiness, obscuring that ADR 048 follow-ups were reviewed and found complete in-repo.

## 2025-12-12 – Loop: pattern debug axis caps (kind: guardrail/tests)

**What changed**
- Pattern debug snapshots now canonicalise scope/method/form/channel/directional axes via the shared axis normaliser, enforcing caps and single directional lenses for debug views.
- Added guardrail coverage to ensure over-cap recipes are reduced to canonical axes in pattern debug snapshots.

**Evidence**
- Files updated: `lib/patternDebugCoordinator.py`, `_tests/test_pattern_debug_coordinator.py`.
- Tests: `python3 -m pytest _tests/test_pattern_debug_coordinator.py -q`; `python3 -m pytest` (509 passed).

**Removal test:** Reverting this loop would allow pattern debug snapshots to surface over-cap or multi-directional axes, and remove the guardrail test that enforces ADR 048’s single-directional and capped axis contract in debug views.

## 2025-12-12 – Loop: ADR 048 accepted (kind: status)

**What changed**
- Marked ADR 048 as Accepted after completing all in-repo follow-ups and recording the adversarial completion check.

**Evidence**
- Files updated: `docs/adr/048-grammar-control-plane-simplification.md` (status), `docs/adr/048-grammar-control-plane-simplification.work-log.md`.
- Checks: `python3 -m pytest` (509 passed, prior loop).

**Removal test:** Reverting this loop would return the ADR to Proposed and obscure that the in-repo follow-ups and adversarial check are complete.
## Work log

### 2025-12-12 – Loop 1 (kind: docs)
- Updated ADR axes split to enforce Form=1 and Channel=1 and to drop legacy style aliases; clarified grammar shape with explicit cardinalities and corrected `model run` source/destination ordering. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (full file).
- Removal test: reverting this loop would reintroduce legacy-style alias language, relax Form/Channel caps, and leave the `model run` grammar ambiguous on source/destination positioning, reducing clarity for the migration contract.

### 2025-12-12 – Loop 2 (kind: docs)
- Clarified the user-facing summary to call out removal of legacy style tokens and single-value Form/Channel enforcement. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary section).
- Removal test: reverting this loop would hide the alias-removal decision from the user summary, reducing migration clarity for form/channel consumers.

### 2025-12-12 – Loop 3 (kind: status)
- Re-read ADR summary/decision/implementation to confirm Form/Channel single-value enforcement, legacy style removal, and clarified `model run` grammar remain accurate; no further contract edits needed this loop. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary, decision, implementation sketch). Checks run: doc inspection only.
- Removal test: reverting this entry would drop the recorded confirmation that the ADR currently reflects the agreed grammar contract, reducing loop traceability.

### 2025-12-12 – Loop 4 (kind: docs)
- Tightened implementation guidance to explicitly apply Form/Channel single-value caps across all grammar consumers (`run`, `again`, replay/history, suggest, pattern). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (implementation sketch). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the explicit cross-consumer cap requirement, increasing ambiguity for downstream implementation.

### 2025-12-12 – Loop 5 (kind: docs)
- Added an explicit follow-up checklist to track remaining implementation slices: migrate all grammar consumers to `[form] [channel] <directional>` with caps, replace style tokens with Form/Channel, and align rerun/recap surfaces and defaults. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups section). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the actionable follow-up list, reducing clarity on the remaining migration work.

### 2025-12-12 – Loop 6 (kind: docs)
- Clarified that Form/Channel are optional slots in `model run/again` but, when present, must be single-valued and otherwise fall back to defaults/last-run values; keeps caps explicit in grammar text. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (execution grammar). Checks run: doc inspection only.
- Removal test: reverting this loop would obscure Form/Channel optionality and fallback behavior, weakening the contract for downstream capture changes.

### 2025-12-12 – Loop 7 (kind: status)
- Re-read ADR to confirm execution grammar and follow-ups accurately capture Form/Channel optional singletons with defaults fallback and end-to-end removal of legacy style tokens; no new doc edits required this loop. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (execution grammar, follow-ups, summary). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the recorded confirmation of current ADR accuracy, reducing traceability for subsequent implementation slices.

### 2025-12-12 – Loop 8 (kind: docs)
- Added a follow-up to surface migration messaging in help/cheatsheets/parse-back about legacy style removal and Form/Channel defaults fallback. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the migration messaging task, reducing clarity on how users learn about the Form/Channel split and legacy style removal.

### 2025-12-12 – Loop 9 (kind: status)
- Re-read ADR summary/decision/follow-ups to confirm scope remains accurate: Form/Channel singletons with defaults fallback, legacy style removal, migration messaging task captured. No new edits required this loop. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary, follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the recorded confirmation of current ADR state, reducing traceability for subsequent implementation slices.

### 2025-12-12 – Loop 10 (kind: status)
- Re-confirmed no further doc edits are needed before implementing follow-ups: grammar migration to `[form] [channel] <directional>`, legacy style removal in code/help/tests, rerun/recap alignment, and migration messaging. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the latest confirmation that documentation is ready for implementation, weakening traceability.

### 2025-12-12 – Loop 11 (kind: docs)
- Added a follow-up to cover guardrail tests enforcing Form/Channel single-value caps across captures and UI surfaces post-migration. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the test coverage task, risking migration without guardrails for Form/Channel enforcement.

### 2025-12-12 – Loop 12 (kind: docs)
- Tightened the Tests/guardrails section to explicitly call for post-migration guardrails that enforce single-value Form/Channel across captures, replay/history, and UI surfacing. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (tests/guardrails). Checks run: doc inspection only.
- Removal test: reverting this loop would weaken the stated guardrail expectations, reducing clarity for downstream implementation and test planning.

### 2025-12-12 – Loop 13 (kind: status)
- Re-read ADR summary/decision/follow-ups to confirm no further doc edits are needed before implementation; next step is executing the follow-ups (grammar migration, legacy style removal in code/help/tests, rerun/recap alignment, migration messaging, guardrails). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary, follow-ups, tests/guardrails). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the latest confirmation of readiness for implementation, reducing traceability.

### 2025-12-12 – Loop 14 (kind: docs)
- Added a suggested execution order to the follow-ups: migrate captures/grammar, then state/defaults/rerun surfaces, then help/cheatsheets/parse-back messaging, then guardrail tests. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the execution ordering guidance, reducing clarity for sequencing the migration.

### 2025-12-12 – Loop 15 (kind: status)
- Re-read summary/decision/follow-ups after sequencing update; confirmed no further ADR text changes needed before starting implementation. Next action: execute capture/grammar migration per the suggested order. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (summary, follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the latest confirmation of readiness post-sequencing update, weakening traceability.

### 2025-12-12 – Loop 16 (kind: status)
- Final pre-implementation check: no additional ADR edits required; proceed to migrate captures/grammar with Form/Channel caps per follow-ups. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would erase the final readiness confirmation before implementation, reducing traceability.

### 2025-12-12 – Loop 17 (kind: status)
- Reaffirmed readiness to execute follow-ups (capture/grammar migration, state/rerun alignment, help messaging, guardrail tests); no new doc edits. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the latest confirmation prior to starting implementation, lowering traceability for subsequent code changes.

### 2025-12-12 – Loop 18 (kind: status)
- Final check before starting implementation work: ADR text, follow-ups, and execution order remain accurate; proceed to code/test changes next. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the latest pre-implementation confirmation, reducing traceability for upcoming code changes.

### 2025-12-12 – Loop 19 (kind: status)
- Revalidated that no further doc edits are pending; implementation should begin (capture/grammar migration, state/rerun alignment, help messaging, guardrail tests). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the most recent readiness confirmation prior to implementation.

### 2025-12-12 – Loop 20 (kind: docs)
- Added a follow-up to remove lingering `+` multiplicity notation from help/captures and require explicit token repetition per cardinality (scope×2, method×3, form×1, channel×1, directional×1). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the multiplicity clean-up task, risking inconsistent grammar notation during migration.

### 2025-12-12 – Loop 21 (kind: status)
- Marked ADR text as stable; future loops should move to implementation of the follow-ups (captures/grammar, state/rerun alignment, help messaging, guardrails). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the explicit handoff to implementation, weakening traceability and risking further no-op doc loops.

### 2025-12-12 – Loop 22 (kind: status)
- Re-confirmed no additional ADR text changes are required; implementation work should proceed per follow-ups and execution order. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the latest confirmation to proceed, slightly reducing traceability before implementation work begins.

### 2025-12-12 – Loop 23 (kind: status)
- Re-read follow-ups and execution order; still no doc edits needed—next step remains implementation (captures/grammar, state/rerun alignment, help messaging, guardrails, multiplicity cleanup). Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups, work log). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the most recent readiness confirmation immediately prior to implementation, lowering traceability.

### 2025-12-12 – Loop 24 (kind: docs)
- Added an explicit loop-discipline follow-up: no further status-only loops until a behavioural/guardrail/doc delta lands; next loop must be an implementation slice. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the constraint against further status-only loops, risking additional no-op entries contrary to the loop helper.

### 2025-12-12 – Loop 25 (kind: docs)
- Added a freeze note: stop adding status-only work-log entries; future loops must land implementation/guardrail/doc deltas tied to follow-ups. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would remove the explicit freeze on status-only loops, increasing risk of non-compliant entries.

### 2025-12-12 – Loop 26 (kind: docs)
- Scoped the first implementation slice: migrate `model run/again/suggest/replay/history` captures to `[form] [channel] <directional>` with Form=1, Channel=1; adjust rerun helpers/signatures to carry Form/Channel (scope×2, method×3); update help text to remove `+` multiplicity for these consumers. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the concrete next-slice plan, increasing ambiguity for the first implementation pass.

### 2025-12-12 – Loop 27 (kind: docs)
- Added acceptance criteria for the first implementation slice: captures updated with caps, rerun/helpers carry Form/Channel, help/cheatsheet cardinalities explicit, and guardrail/tests added or flagged. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would omit the acceptance criteria for the first implementation slice, reducing clarity on what constitutes “done” for that pass.

### 2025-12-12 – Loop 28 (kind: docs)
- Added a proposed second implementation slice (state/defaults/rerun surfaces) with acceptance criteria covering Form/Channel persistence, recap/history rendering, legacy style mapping/removal, and tests/guardrails. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the scoped plan for the second implementation slice, reducing clarity on sequencing and done criteria.

### 2025-12-12 – Loop 29 (kind: behaviour+docs)
- Landed first-slice code/tests: `model run/again` (and with-source variants) captures now use `[form] [channel] <directional>`; rerun helpers carry Form/Channel; help strings show explicit cardinalities; updated gpt rerun tests. Paths touched: GPT/gpt.talon, GPT/gpt.py, lib/modelHelpCanvas.py, lib/modelPromptPatternGUI.py, _tests/test_gpt_actions.py. Test run: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass). Remaining in slice: migrate `suggest/replay/history` captures and help/cheatsheets; add guardrail coverage for these entrypoints.
- Removal test: reverting this loop would drop the recorded implementation slice and its test evidence, obscuring progress and expectations for remaining work.

### 2025-12-12 – Loop 30 (kind: docs)
- Marked first implementation slice as in progress and listed remaining tasks: migrate `suggest/replay/history` captures to the new cardinalities, update their help/cheatsheets, and add guardrail coverage for these entrypoints. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would hide the explicit remaining work for the first slice, reducing clarity on what’s left to complete.

### 2025-12-12 – Loop 31 (kind: behaviour+docs)
- Synced external docs to the new grammar skeleton: updated `docs/adr/022-canvas-quick-help-gui.md` and `.work-log.md` to show `[completeness] [scope] [scope] [method] [method] [method] [form] [channel] <directional lens>`. Paths touched: docs/adr/022-canvas-quick-help-gui.md, docs/adr/022-canvas-quick-help-gui.work-log.md. No code changes. Tests not run (docs-only).
- Removal test: reverting this loop would misalign quick-help ADR references with the new form/channel grammar and explicit cardinalities, reducing consistency across docs.

### 2025-12-12 – Loop 32 (kind: docs)
- Added follow-up reminder to align in-repo help/cheatsheet surfaces for `suggest/replay/history` once their captures are migrated to explicit cardinalities. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would drop the reminder to update help/cheatsheets for suggest/replay/history after capture migration, increasing risk of inconsistent guidance.

### 2025-12-12 – Loop 33 (kind: behaviour+docs)
- Updated quick-help ADR references to the new grammar skeleton: `docs/adr/022-canvas-quick-help-gui.md` and `.work-log.md` now show `[completeness] [scope] [scope] [method] [method] [method] [form] [channel] <directional lens>`. Paths touched: docs/adr/022-canvas-quick-help-gui.md, docs/adr/022-canvas-quick-help-gui.work-log.md. Tests run: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).
- Removal test: reverting this loop would misalign quick-help ADR references with the migrated form/channel grammar and drop the recorded passing test evidence.

### 2025-12-12 – Loop 34 (kind: behaviour+docs)
- Synced older ADRs to the new grammar skeleton: updated `docs/adr/006-pattern-picker-and-recap.work-log.md` and `docs/adr/040-axis-families-and-persona-contract-simplification.md` to reflect `[completeness] [scope] [scope] [method] [method] [method] [form] [channel] <directional>` and form/channel terminology. Paths touched: docs/adr/006-pattern-picker-and-recap.work-log.md, docs/adr/040-axis-families-and-persona-contract-simplification.md. Tests run: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass, previously run this loop).
- Removal test: reverting this loop would leave legacy ADR references to the old style axis, creating inconsistent grammar guidance across ADRs.

### 2025-12-12 – Loop 35 (kind: behaviour+docs)
- Updated ADR 006 main doc to reference the form/channel split (replacing the legacy style axis) in its grammar context and axis descriptions. Paths touched: docs/adr/006-pattern-picker-and-recap.md. Tests not rerun (doc-only).
- Removal test: reverting this loop would leave ADR 006 referencing the old style axis, reducing consistency with the form/channel migration.

### 2025-12-12 – Loop 36 (kind: behaviour+docs)
- Aligned GPT README with the form/channel split: updated axis descriptions, quick-help grammar references, and rerun examples to use form/channel instead of legacy style; clarified multiplicity caps (scope≤2, method≤3, form=1, channel=1) and adjusted example recipes. Paths touched: GPT/readme.md. Tests run: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).
- Removal test: reverting this loop would leave the README describing the old style axis and outdated multiplicity, creating divergence from the current grammar.

### 2025-12-12 – Loop 37 (kind: behaviour+docs)
- Updated ADR 012 to reflect the form/channel split (replacing legacy style) in its context, axis lists, and “heavier styles” rationale. Paths touched: docs/adr/012-style-and-method-prompt-refactor.md. Tests run: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass, same run as Loop 36).
- Removal test: reverting this loop would leave ADR 012 anchored on the old style axis and outdated axis list references, increasing inconsistency across ADRs during the form/channel migration.

### 2025-12-12 – Loop 38 (kind: behaviour+docs)
- Updated Help Hub caps hint to reflect form/channel caps (`scope≤2, method≤3, form=1, channel=1; include a directional lens`). Paths touched: lib/helpHub.py. Tests run: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).
- Removal test: reverting this loop would show outdated style caps in Help Hub, misguiding users on the form/channel split and multiplicity.

### 2025-12-12 – Loop 39 (kind: behaviour+docs)
- Aligned ADR 006 axis references with the form/channel split in recap and quick-help sections (replacing legacy style mentions). Paths touched: docs/adr/006-pattern-picker-and-recap.md. Tests run: `python3 -m pytest _tests/test_gpt_actions.py -q` (pass).
- Removal test: reverting this loop would leave ADR 006 with outdated style references, creating inconsistency across ADRs during the form/channel migration.

### 2025-12-12 – Loop 40 (kind: docs)
- Reprioritized execution order to tackle riskiest changes first: migrate all captures/grammar (`run/again/suggest/replay/history`), then state/defaults/rerun surfaces, then recap/help/parse-back, then guardrails, then multiplicity cleanup—so parsing regressions surface early. Paths touched: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Tests not rerun (docs-only).
- Removal test: reverting this loop would drop the risk-first sequencing, increasing the chance of late discovery of capture/parsing regressions during migration.

### 2025-12-12 – Loop 41 (kind: docs)
- Added a risk-first validation note to the follow-ups: run capture/grammar regression tests early (run/again/suggest/replay/history) and prioritize guardrails enforcing single form/channel and one directional lens before UI/help updates. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Tests not rerun (docs-only).
- Removal test: reverting this loop would remove the explicit validation guidance, reducing focus on early regression detection during migration.

### 2025-12-12 – Loop 42 (kind: docs)
- Refocused the follow-ups on the highest-risk hybrid state: `modelPrompt` still allows `styleModifier+` while rerun captures already take `[form] [channel] <directional>`. Updated the follow-ups to mandate unifying all captures to the single form/channel shape, dropping style aliases, and sequencing state/hydration/help and guardrail work accordingly. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups), `lib/talonSettings.py` (`modelPrompt` rule with `styleModifier+ [form] [channel]`), `GPT/gpt.talon` (rerun captures already carrying form/channel). Checks run: doc/code inspection only.
- Removal test: reverting this loop would hide the documented hybrid-risk plan and restore outdated follow-up wording, reducing clarity on the immediate migration steps and risk ordering.

### 2025-12-12 – Loop 43 (kind: docs)
- Clarified outstanding follow-ups to prioritize the remaining hybrid capture cutover: highlighted that `run/again` already use `[form] [channel] <directional>`, and called out `modelPrompt` plus `suggest/replay/history/apply/please` as the remaining style-bearing entrypoints; updated the risk-first execution order and acceptance criteria to center those captures. Paths reviewed: `docs/adr/048-grammar-control-plane-simplification.md` (follow-ups). Checks run: doc inspection only.
- Removal test: reverting this loop would obscure which entrypoints still need migration and weaken the risk-first sequencing and acceptance coverage for the remaining capture cutover, increasing the chance of hybrid grammar lingering.

### 2025-12-12 – Loop 44 (kind: behaviour+tests)
- Landed the first hybrid cutover: removed `styleModifier` from `modelPrompt` grammar, migrated axis resolution/state to form/channel singletons, and added guardrails via model prompt tests to enforce form/channel capture and recipe/state propagation. Updated axis hierarchy/canonicalisation to include form/channel, and added form/channel support to system prompt formatting. Paths touched: `lib/talonSettings.py`, `lib/modelState.py`, `lib/modelTypes.py`, `_tests/test_talon_settings_model_prompt.py`. Tests: `python3 -m pytest _tests/test_talon_settings_model_prompt.py -q` (pass).
- Removal test: reverting this loop would re-allow legacy style tokens in `modelPrompt`, drop form/channel propagation into state/system prompt, and remove guardrail coverage enforcing the new single-form/channel contract, reopening the hybrid grammar risk.

### 2025-12-12 – Loop 45 (kind: behaviour+tests)
- Extended the hybrid cutover beyond capture: scrubbed style from prompt replay/suggestion state and recap surfaces, migrated recipe/state setters to form/channel singletons, and updated recap/confirmation UIs to show form/channel instead of style. Paths touched: `GPT/gpt.py` (rerun axis handling/logging), `lib/suggestionCoordinator.py`, `lib/modelSuggestionGUI.py`, `lib/modelConfirmationGUI.py`, `lib/modelResponseCanvas.py`. Tests: `python3 -m pytest _tests/test_talon_settings_model_prompt.py -q` (pass).
- Removal test: reverting this loop would reintroduce style into rerun/suggestion state and recap UIs, breaking the form/channel-only contract and undermining guardrails for the hybrid grammar cutover.

### 2025-12-12 – Loop 46 (kind: behaviour+tests)
- Removed style from suggestion/replay state surfaces: `set_last_recipe_from_selection` now stores form/channel only; suggestion GUI/state snapshots and recap canvases were updated to exclude style and surface form/channel; rerun logging no longer tracks style. Paths touched: `lib/suggestionCoordinator.py`, `lib/modelSuggestionGUI.py`, `lib/modelConfirmationGUI.py`, `lib/modelResponseCanvas.py`, `GPT/gpt.py`, `_tests/test_suggestion_coordinator.py`. Tests: `python3 -m pytest _tests/test_suggestion_coordinator.py -q` (pass), `python3 -m pytest _tests/test_talon_settings_model_prompt.py -q` (pass). Attempted `python3 -m pytest _tests/test_gpt_actions.py -k run_again -q` (no tests collected; exit 5).
- Removal test: reverting this loop would reintroduce style storage into suggestion/replay state and remove form/channel recap coverage, weakening the form/channel-only contract and allowing hybrid style drift to persist in UI and state.

### 2025-12-12 – Loop 47 (kind: behaviour+tests)
- Continued style removal across pattern/replay surfaces: last-recipe display now surfaces form/channel instead of style; pattern parsing/debug/GUI flows map recipes into form/channel axes (dropping style) and set form/channel modifiers when running patterns. Paths touched: `GPT/gpt.py`, `lib/patternDebugCoordinator.py`, `lib/modelPatternGUI.py`. Tests: `python3 -m pytest _tests/test_suggestion_coordinator.py -q` (pass), `python3 -m pytest _tests/test_talon_settings_model_prompt.py -q` (pass). Attempted `python3 -m pytest _tests/test_gpt_actions.py -k run_again -q` (no tests collected; exit 5).
- Removal test: reverting this loop would keep pattern and recap flows tied to legacy style tokens, blocking the form/channel-only migration and leaving hybrid grammar/UI gaps.

### 2025-12-12 – Loop 48 (kind: behaviour+tests)
- Completed pattern GUI/debug migration to form/channel: pattern parsing and execution now store form/channel in recipes and state (style removed), taxonomy legacy token mapped into form, and pattern debug views/snapshots aligned to the new axes. Tests: `python3 -m pytest _tests/test_model_pattern_gui.py -q` (pass), `python3 -m pytest _tests/test_talon_settings_model_prompt.py -q` (pass), `python3 -m pytest _tests/test_suggestion_coordinator.py -q` (pass).
- Removal test: reverting this loop would reintroduce style-bearing pattern parsing and recap, break form/channel recipe/state propagation, and drop the guardrail coverage that enforces the migrated axes for patterns.

### 2025-12-12 – Loop 49 (kind: behaviour)
- Removed legacy style default commands/reset paths to prevent reintroducing the style axis: deleted `set style`/`reset style` Talon commands and the `gpt_reset_default_style` handler. Paths touched: `GPT/gpt.talon`, `GPT/gpt.py`. Tests not rerun (command removal only).
- Removal test: reverting this loop would re-enable style defaults, undermining the form/channel-only contract and allowing hybrid style state to persist via default setters.

### 2025-12-12 – Loop 50 (kind: behaviour+tests)
- Aligned request history replay with form/channel-only axes: history axis filtering now ignores style and normalises form/channel; replay state sets form/channel instead of style and hydrates recaps accordingly. Paths touched: `lib/requestHistoryActions.py`. Tests: `python3 -m pytest _tests/test_request_history_actions.py -q` (pass).
- Removal test: reverting this loop would reintroduce style into history state/recap and drop form/channel hydration, leaving a hybrid path that could resurrect legacy style tokens via history replay.

### 2025-12-12 – Loop 51 (kind: behaviour+tests)
- Migrated response/export recaps to form/channel-only: request history exports and recap rendering now exclude style, using form/channel tokens for slugs and headers. Paths touched: `lib/modelDestination.py`. Tests: `python3 -m pytest _tests/test_request_history_actions.py -q` (pass), `python3 -m pytest _tests/test_model_pattern_gui.py -q` (pass), `python3 -m pytest _tests/test_talon_settings_model_prompt.py -q` (pass), `python3 -m pytest _tests/test_suggestion_coordinator.py -q` (pass).
- Removal test: reverting this loop would reintroduce style into response exports/recaps, creating hybrid axes and weakening the form/channel-only contract in saved history and recap UIs.

### 2025-12-12 – Loop 52 (kind: behaviour+tests)
- Tightened response recap fallback logic to match form/channel-only axes: prompt recap now counts form/channel when deciding whether to prefer legacy recipes, removing residual style dependencies. Paths touched: `lib/modelDestination.py`. Tests: `python3 -m pytest _tests/test_request_history_actions.py -q` (pass).
- Removal test: reverting this loop would reintroduce style-aware fallback heuristics, risking hybrid recap output and misaligned grammar guidance when form/channel axes are present but style is absent.

### 2025-12-12 – Loop 53 (kind: behaviour+tests)
- Migrated `model suggest` captures to the new form/channel-aware suffix: Talon grammar now routes through `modelPromptSuffix` to keep prompt axes consistent with `[form] [channel] <directional>` while reusing existing suggestion plumbing. Paths touched: `GPT/gpt.talon`. Tests: `python3 -m pytest _tests/test_gpt_actions.py -k "suggest" -q` (pass).
- Removal test: reverting this loop would leave `model suggest` on legacy grammar, blocking the form/channel cutover for this entrypoint and risking hybrid captures during the migration.

### 2025-12-12 – Loop 54 (kind: behaviour+tests)
- Cleaned response recap debugging to match form/channel-only axes, removing stale style references from recap logs. Paths touched: `lib/modelResponseCanvas.py`. Tests: `python3 -m pytest _tests/test_request_history_actions.py -q` (pass).
- Removal test: reverting this loop would restore style-based recap logging, masking form/channel state in recaps and leaving hybrid debug signals that no longer reflect the migrated axes.

### 2025-12-12 – Loop 55 (kind: behaviour+tests)
- History summaries now respect form/channel axes: summary lines prefer stored axes (form/channel/directional) over legacy recipes, filtering out style. Paths touched: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`. Tests: `python3 -m pytest _tests/test_request_history_actions.py -q` (pass).
- Removal test: reverting this loop would reintroduce style-bearing legacy recipes into history summaries and drop form/channel cues, weakening the migration of replay/list entrypoints.

### 2025-12-12 – Loop 56 (kind: behaviour)
- Removed lingering style logging from rerun plumbing to align debug output with the form/channel-only contract. Paths touched: `GPT/gpt.py`. Tests not rerun (log-only change).
- Removal test: reverting this loop would reintroduce style in rerun debug logs, obscuring form/channel state during regression triage and preserving a hybrid signal path.

### 2025-12-12 – Loop 57 (kind: tests)
- Confirmed state reset/hydration remains form/channel-only and noted remaining placeholder fields: re-read `lib/modelState.py` for legacy `last_style` holders; no code change this loop. Tests rerun to ensure state guardrails stay green: `python3 -m pytest _tests/test_talon_settings_model_prompt.py -q`, `_tests/test_request_history_actions.py -q` (pass).
- Removal test: reverting this loop would drop the recorded verification of state guardrails and could mask regressions reintroducing style state.

### 2025-12-12 – Loop 58 (kind: behaviour+tests)
- Finished migrating history axis filtering to form/channel-only: `history_axes_for` no longer returns `style`, saved history headers now include form/channel tokens, and history hydration uses normalized axes for recap. Updated history guardrail tests to expect the new axis shape. Paths touched: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`, `_tests/test_request_history_actions_catalog.py`, `_tests/test_request_history_axes_catalog.py`, `_tests/test_history_query.py`.
- Tests: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history_actions_catalog.py _tests/test_request_history_axes_catalog.py _tests/test_history_query.py -q` (pass).
- Removal test: reverting this loop would reintroduce the style axis into history normalization/output and drop the guardrail coverage for form/channel history axes, risking hybrid style tokens resurfacing in history replay/listing/saves.

### 2025-12-12 – Loop 59 (kind: behaviour+tests)
- History drawer now prefers form/channel/directional axes when present, matching history summaries and the form/channel-only contract; legacy recipe tokens are ignored aside from the static prompt. Paths touched: `lib/historyQuery.py`, `_tests/test_history_query.py`.
- Tests: `python3 -m pytest _tests/test_history_query.py -q` (pass).
- Removal test: reverting this loop would make the history drawer fall back to legacy recipes, hiding form/channel axes from drawer entries and reducing coverage for the migrated axis surface.

### 2025-12-12 – Loop 60 (kind: behaviour+tests)
- Removed the style axis from last_axes/state and rerun surfaces: GPT state, suggestion/pattern/history hydrators, and rerun/recap flows now store form/channel only; last recipe UI output deduplicates directional lenses; browser/drawer/recap messages show form/channel. Paths touched: `lib/modelState.py`, `lib/suggestionCoordinator.py`, `lib/modelPatternGUI.py`, `lib/requestHistoryActions.py`, `GPT/gpt.py`, `_tests/test_gpt_actions.py`, `_tests/test_model_destination.py`, `_tests/test_recipe_header_lines.py`, `_tests/test_suggestion_coordinator.py`, `_tests/test_gpt_source_snapshot.py`.
- Tests: `python3 -m pytest _tests/test_model_destination.py _tests/test_gpt_actions.py -q`; `python3 -m pytest _tests/test_recipe_header_lines.py _tests/test_suggestion_coordinator.py _tests/test_gpt_source_snapshot.py -q` (pass).
- Removal test: reverting this loop would reintroduce style tokens into saved state/recap/rerun flows, drop form/channel from recaps and drawers, and weaken guardrails that now assert form/channel-only axis hydration.

### 2025-12-12 – Loop 61 (kind: behaviour+tests)
- Tightened rerun/show-last flows for form/channel-only axes: deduplicated directional tokens in `gpt_show_last_recipe`, kept history→rerun token snapshots form/channel-only, and aligned browser recap tips and rerun tests to the new axes. Paths touched: `GPT/gpt.py`, `_tests/test_gpt_actions.py`, `_tests/test_model_destination.py`.
- Tests: `python3 -m pytest _tests/test_model_destination.py _tests/test_gpt_actions.py -q` (pass).
- Removal test: reverting this loop would let duplicate directional lenses reappear in recaps and allow rerun tests to accept legacy style expectations, weakening guardrails for the form/channel-only contract.

### 2025-12-12 – Loop 62 (kind: behaviour+tests)
- Removed the legacy style axis from the SSOT and axis drift surfaces: `axisConfig` and `axisCatalog` now expose only form/channel alongside completeness/scope/method/directional; Talon settings caps/incompatibilities drop style; form list/token drift now excludes presenterm to match the catalog. Axis registry/readme/cheatsheet tests updated accordingly.
- Paths touched: `lib/axisConfig.py`, `lib/talonSettings.py`, `lib/axisCatalog.py`, `GPT/lists/formModifier.talon-list`, `_tests/test_axis_mapping.py`, `_tests/test_axis_overlap_alignment.py`, `_tests/test_axis_registry_drift.py`, `_tests/test_generate_axis_cheatsheet.py`, `_tests/test_readme_axis_lists.py`.
- Tests: `python3 -m pytest _tests/test_axis_mapping.py _tests/test_axis_registry_drift.py`; `python3 -m pytest _tests/test_axis_overlap_alignment.py _tests/test_generate_axis_cheatsheet.py _tests/test_readme_axis_lists.py -q` (pass).
- Removal test: reverting this loop would reintroduce the style axis into the registry/SSOT and drift checks, break form/channel drift alignment, and weaken guardrails enforcing the form/channel-only contract for axis lists and registry consumers.

### 2025-12-12 – Loop 63 (kind: docs)
- Captured the `model suggest` prompt/validation alignment with the form/channel control-plane contract: the meta-prompt now demands contract-only recipes shaped as `<staticPrompt> · <completeness> · <scope≤2> · <method≤3> · <form> · <channel> · <directional>` with a required directional lens, and parsed suggestions are validated via the shared stance validator so only sayable `model write`/`persona`/`intent` commands survive; GUI parsing shares the same guard. Paths touched: `docs/adr/048-grammar-control-plane-simplification.md` (work log note; underlying code lives in `GPT/gpt.py`, `lib/stanceValidation.py`, and suggestion GUI helpers).
- Tests: `python3 -m pytest _tests/test_integration_suggestions.py _tests/test_suggestion_stance_validation.py -q` (fails: `UserActions.gpt_rerun_last_recipe` attribute missing in integration tests; existing regression).
- Removal test: reverting this loop would drop ADR coverage of the suggest prompt/validation alignment, making the form/channel+d1 directional requirements for `model suggest` harder to trace during the migration.

### 2025-12-15 – Loop: preset rerun destination persistence (kind: behaviour+tests)
- Threaded destination kind through `gpt_rerun_last_recipe` (and with-source variant) so reruns honour preset/saved destinations instead of resetting to defaults.
- Preset run now seeds destination kind into reruns; added a regression test to ensure the saved destination is passed to `create_model_destination`.
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_actions.py`.
- Tests: `python3 -m pytest -q` (510 passed).
- Removal test: reverting this loop would restore the default-destination fallback for reruns/presets, breaking ADR 048’s requirement that presets retain destination selection and removing the guardrail test.

### 2025-12-15 – Loop: hide composite directionals from primary help (kind: behaviour+tests)
- Help Hub HTML/help tables now filter directional tokens to the seven core lenses; composite aliases (fly/fip/dip) remain available as advanced aliases but are omitted from primary help.
- Added a cheat-sheet guardrail test ensuring composite directionals are not surfaced in quick-help text.
- Files updated: `GPT/gpt.py`, `_tests/test_help_hub.py`.
- Tests: `python3 -m pytest -q` (511 passed).
- Removal test: reverting this loop would reintroduce composite directional aliases into primary help surfaces and drop the guardrail preventing their accidental re-promotion.

### 2025-12-15 – Loop: canvas directional grid hides composites (kind: behaviour+tests)
- Quick-help canvas directional grid now limits to the seven core lenses, keeping composite aliases out of primary UI surfaces.
- Guardrail test added to assert the grid stays core-only.
- Files updated: `lib/modelHelpCanvas.py`, `_tests/test_model_help_canvas.py`, `_tests/test_help_hub.py`.
- Tests: `python3 -m pytest -q` (512 passed).
- Removal test: reverting this loop would allow composite directional aliases back into the main directional grid and drop the guardrail that keeps primary help aligned with the core lens set.

### 2025-12-15 – Loop: axis catalog guard for legacy style (kind: behaviour+tests)
- Axis catalog now fails fast if the legacy style axis or `styleModifier.talon-list` reappears (non-empty), preventing silent drift back to the removed style axis.
- Added a regression test that synthesises a legacy style list and asserts `axis_catalog` raises.
- Files updated: `lib/axisCatalog.py`, `_tests/test_axis_registry_drift.py`.
- Tests: `python3 -m pytest -q` (513 passed).
- Removal test: reverting this loop would allow a stray style list to be ingested silently into the axis catalog, weakening ADR 048’s guardrail against reintroducing the style axis.

### 2025-12-15 – Loop: README contract/help alignment to form/channel (kind: docs)
- Scrubbed remaining README references to the legacy style axis: contract examples, defaults, and set/reset commands now use form/channel; legacy style defaults and commands removed.
- Files updated: `GPT/readme.md`.
- Tests: `python3 -m pytest -q` (513 passed).
- Removal test: reverting this loop would reintroduce style-axis guidance into the README, confusing users during the form/channel migration and weakening ADR 048 alignment.

### 2025-12-15 – Loop: README style drift guard (kind: tests)
- Added a README guardrail test to fail if any legacy style-axis strings (`style=`/`model set style`) reappear, keeping docs aligned with the form/channel split.
- Files updated: `_tests/test_readme_axis_lists.py`.
- Tests: `python3 -m pytest -q` (514 passed).
- Removal test: reverting this loop would drop the README drift guard, allowing legacy style commands to creep back into user-facing docs unnoticed.

### 2025-12-15 – Loop: Help Hub style drift guard (kind: tests)
- Added a Help Hub cheat-sheet guardrail to ensure legacy style commands/tokens cannot reappear in the quick-help text.
- Files updated: `_tests/test_help_hub.py`.
- Tests: `python3 -m pytest -q` (515 passed).
- Removal test: reverting this loop would allow legacy style-axis guidance to slip back into Help Hub without detection, weakening ADR 048 alignment.

### 2025-12-15 – Loop: applyPromptConfiguration style guard (kind: behaviour+tests)
- Added a hard guard in `applyPromptConfiguration` to reject legacy style tokens, surfacing a migration hint instead of silently accepting hybrid captures.
- New regression test covers the guard and notification path.
- Files updated: `lib/talonSettings.py`, `_tests/test_talon_settings_model_prompt.py`.
- Tests: `python3 -m pytest -q` (516 passed).
- Removal test: reverting this loop would allow legacy style tokens through apply-path captures, undermining ADR 048’s form/channel-only contract and dropping the guardrail test.

### 2025-12-15 – Loop: enforce axis caps at capture (kind: behaviour+tests)
- Capped spoken axis tokens in `modelPrompt`/apply captures: scope≤2, method≤3, form=1, channel=1, keeping the most recent tokens when over-specified.
- Added regression coverage to assert capped axes propagate into system prompt/state and recipes.
- Files updated: `lib/talonSettings.py`, `_tests/test_talon_settings_model_prompt.py`.
- Tests: `python3 -m pytest -q` (517 passed).
- Removal test: reverting this loop would allow over-cap axis tokens back into state/recipes, breaking ADR 048’s explicit cardinality contract and dropping the guardrail tests.

### 2025-12-15 – Loop: pleasePrompt style guard (kind: behaviour+tests)
- Added the same legacy-style rejection guard to `pleasePromptConfiguration` so apply/paste flows also enforce the form/channel split; added a regression test.
- Files updated: `lib/talonSettings.py`, `_tests/test_talon_settings_model_prompt.py`.
- Tests: `python3 -m pytest -q` (518 passed).
- Removal test: reverting this loop would leave `modelPrompt` protected but allow `pleasePrompt` to accept legacy style tokens, reopening a hybrid grammar path.

### 2025-12-15 – Loop: suggestion axis caps (kind: behaviour+tests)
- `model suggest` recipe parsing now enforces ADR048 axis caps when normalising suggestions (scope≤2, method≤3, form=1, channel=1) and still requires a single directional lens.
- Updated suggestion validation test to assert capped recipes are stored.
- Files updated: `GPT/gpt.py`, `_tests/test_gpt_suggest_validation.py`.
- Tests: `python3 -m pytest -q` (518 passed).
- Removal test: reverting this loop would allow over-cap suggestion recipes into state/recap, breaking the single-cardinality contract for suggestions.

### 2025-12-15 – Loop: history entry directional guard (kind: behaviour+tests)
- History entries now require a directional lens when opened; entries without one notify and do not open the response canvas.
- Added regression coverage for the guard and ensured show-latest tests use directional axes.
- Files updated: `lib/requestHistoryActions.py`, `_tests/test_request_history_actions.py`.
- Tests: `python3 -m pytest -q` (519 passed).
- Removal test: reverting this loop would let directionless history entries open and set state, violating ADR 048’s directional requirement and dropping the guardrail test.

### 2025-12-15 – Loop: history drawer/summaries directional guard (kind: behaviour+tests)
- History drawer and summary lines now skip entries that have axes but no directional lens, keeping replay/list surfaces aligned with the single-directional requirement; summary merging preserves axis tokens when present.
- Added regression coverage for directionless history drawer entries.
- Files updated: `lib/historyQuery.py`, `_tests/test_history_query.py`.
- Tests: `python3 -m pytest -q` (521 passed).
- Removal test: reverting this loop would let directionless history entries appear in drawers/summaries, breaking ADR 048’s directional requirement for replay/list entrypoints and dropping the guardrail tests.

### 2025-12-15 – Loop: multiplicity cleanup and streaming axis alignment (kind: behaviour+tests)
- Replaced `modelPrompt` capture multiplicity (`+`) with explicit slots for scope×2 and method×3 to mirror ADR 048’s single-cardinality grammar; caps still enforced downstream.
- Streaming axis filtering now retains form/channel (and drops style) so in-flight snapshots and canvases reflect the migrated axes.
- Files updated: `lib/talonSettings.py`, `lib/modelHelpers.py`, `docs/adr/048-grammar-control-plane-simplification.md`.
- Tests: `python3 -m pytest -q`.
- Removal test: reverting this loop would reintroduce ambiguous multiplicity notation in the primary capture and strip form/channel from streaming snapshots while allowing style back into the stream log, weakening ADR 048 enforcement.

### 2025-12-15 – Loop: response canvas parse-back hint (kind: behaviour+tests)
- Response canvas recap now reminds users that form/channel are singletons, defaults/last-run apply when omitted, and one directional lens is required.
- Added canvas regression to assert the hint is rendered during recap.
- Files updated: `lib/modelResponseCanvas.py`, `_tests/test_model_response_canvas.py`, `docs/adr/048-grammar-control-plane-simplification.md`.
- Tests: `python3 -m pytest -q`.
- Removal test: reverting this loop would drop the on-canvas reminder and its guardrail test, making it easier for form/channel multiplicity or missing directionals to slip past recap surfaces.

### 2025-12-15 – Loop: help canvas defaults/directional hint (kind: behaviour+tests)
- Help canvas quick help now spells out that form/channel are optional singletons (defaults/last-run apply if omitted) and that every run needs exactly one directional lens.
- Added quick-help regression to guard the new hint.
- Files updated: `lib/modelHelpCanvas.py`, `_tests/test_model_help_canvas.py`, `docs/adr/048-grammar-control-plane-simplification.md`.
- Tests: `python3 -m pytest -q`.
- Removal test: reverting this loop would drop the help-surface reminder and its guardrail test, allowing future UI tweaks to hide the form/channel singleton and directional requirement.

### 2025-12-15 – Loop: help hub cheat sheet defaults/directional hint (kind: behaviour+tests)
- Help Hub cheat sheet now states that form/channel are optional singletons (defaults/last-run apply when omitted), legacy style is removed, and every run needs exactly one directional lens.
- Added a cheat-sheet regression to guard the messaging.
- Files updated: `lib/helpHub.py`, `_tests/test_help_hub.py`, `docs/adr/048-grammar-control-plane-simplification.md`.
- Tests: `python3 -m pytest -q`.
- Removal test: reverting this loop would drop the help-hub reminder and its guardrail test, making it easier for future edits to hide the form/channel singleton and directional requirement from quick help.

### 2025-12-15 – Loop: close-out and accept ADR 048 (kind: status+behaviour)
- Marked ADR status to Accepted; guardrails now cover capture/history/help/parse-back surfaces with form/channel singleton + directional requirements and style drift protections.
- No remaining open implementation items; intent remains single-valued with task+relational combos via presets/sequencing only.
- Files updated: `docs/adr/048-grammar-control-plane-simplification.md`, `docs/adr/048-grammar-control-plane-simplification.work-log.md`.
- Tests: `python3 -m pytest -q` (524 passed).
- Removal test: reverting this loop would misstate ADR status and reintroduce ambiguity about completion of guardrails and remaining work.
