# 048 – Grammar Control Plane Simplification (Stance/Contract Split)

- Status: Accepted  
- Date: 2025-12-15  
- Context: Current grammar exposes Persona (voice/audience/tone), Intent (purpose), Contract (completeness/scope/method/style/directional), static prompts, and destinations/sources all in one utterance. Directional lenses are mnemonic and opaque; style mixes container and channel; persona and purpose lists carry low-signal items. Users must remember 6–7 families, optional defaults, and composite directionals, leading to slow recall, mis-parses, and noisy confirmations.

---

## Summary (for users)

- Two verbs:  
  - `model set …` → stance and defaults (Who/Why and optional Contract defaults).  
  - `model run …` → per-call contract (prompt + axes + directional + destination/source).
- Simpler lenses and style: keep the seven core directionals with short glosses (no renames); style split into Form vs Channel with single-value enforcement and legacy style tokens removed.
- Presets and stance defaults reduce repetition; “again” keeps tweaks small.

---

## Decision

1) **Separate stance from per-call contract (required)**
   - Keep existing `persona <preset>` grammar (or explicit voice/audience/tone) and the already-implemented `persona status` / `persona reset`; no grammar change.  
   - Keep existing `intent <preset>` grammar; split the preset list into task vs relational buckets (see #2). No new `relation` alias; use `intent` for both buckets.  
   - Stance + defaults persist for the session; “run” is always per-call. Existing default setters for completeness/scope/method/style remain.

2) **Tighten persona/intent surface (required)**
   - Collapse persona into a small preset set (5–7 high-signal roles); keep raw axes accessible but de-emphasised.  
   - Trim/alias low-yield voice/audience entries (platform/stream-aligned/XP-enthusiast) into presets instead of raw axes.  
   - Split purpose into task intents (decide/teach/evaluate/plan/brainstorm/inform/announce/walkthrough/triage) vs relational intents (persuade/appreciate/coach/collaborate/entertain). Keep a single `intent <preset>` grammar, surface both buckets in help, and allow combining task+relational via presets or sequential commands—not by widening the capture.

3) **Simplify directionals (no renames, required)**
   - Keep the seven core lenses as-is: `fog`, `fig`, `dig`, `ong`, `rog`, `bog`, `jog`. Provide short glosses in docs/help, but do not rename tokens.  
   - Hide composite `fly/fip/dip` values from primary help (advanced shorthand only); keep them as aliases.  
   - Require exactly one directional lens per `run`; allow `jog` as the neutral confirmation lens.

4) **Split style into Form vs Channel (concept + migration)**
   - Form: bullets, table, code, adr, story, checklist, plain, tight, faq, headline, diagram, recipe, bug, spike, log.  
   - Channel bias: slack, jira, presenterm, announce, sync, remote, html.  
   - Grammar shape stays: … `[method]? [method]? [method]? [form]? [channel]? {directional}`; slot order remains stable while the axis name shifts from “style” to “form/channel”.  
   - Enforce Form = 1 and Channel = 1 (replace prior style multiplicity).  
   - Convert existing style tokens to this split now: `slack`, `jira`, `presenterm`, `announce`, `remote`, `sync`, `html` become Channel values (announce also sets Form=headline by default). Remove legacy style tokens rather than keeping alias coverage; update lists/grammar/help/tests to reflect the new Form/Channel vocab.

5) **Presets as first-class control (optional/extend)**
   - `model preset save <name>` from last run; `preset run <name>`; `preset list`.  
   - A preset = prompt + persona + intent/relation + contract axes + directional + destination (extends current persona/intent presets).  
   - Encourage JTBD (summaries, critiques, plans, explanations) to rely on presets instead of long ad-hoc utterances.

6) **Execution grammar shape (required for consistency)**
   - `model run [<prompt>] [<completeness>] [<scope>] [<scope>] [<method>] [<method>] [<method>] [<form>] [<channel>] <directional> [to <destination>] [from <source>] [using <additionalSource>]`.  
   - Minimal path: `model run <prompt> <directional>` (source/destination default). Form/Channel are optional but, when present, must appear at most once each and fall back to defaults/last-run values when omitted.  
   - `model again [<prompt>] [<completeness>] [<scope>] [<scope>] [<method>] [<method>] [<method>] [<form>] [<channel>] [<directional?>]` (directional optional; reuse last).  
   - Apply the same explicit-cardinality `<prompt/axes form>` (scope×2, method×3, form×1, channel×1, directional×1) to other consumers (run-again-with-source, suggest, pattern menus, replay/history).  
   - Axis caps: completeness single; scope up to 2; method up to 3; form exactly 1; channel exactly 1; directional exactly 1.

7) **Discoverability and feedback**
   - `model help who|why|how|form` focuses help panes on persona, intent, contract, style/destination.  
   - Parse-back after capture: “Persona: … | Intent: … | Contract: … | Dest: …”.  
   - Primary help shows only core directionals and Form/Channel split; remove legacy style tokens rather than maintaining alias appendices.

---

## Consequences

### Benefits

- Lower recall burden: fewer visible directionals; style clarified; persona/purpose trimmed.  
- Faster common paths: minimal `run` form; stance defaults reduce repetition; presets cover JTBDs.  
- Clear state separation: stance/defaults vs per-call contract reduces accidental over-specification.  

### Risks and mitigations

- **Risk:** Users relying on composite directionals or long-tail styles may feel items “missing”.  
  - **Mitigation:** keep composite directional aliases; surface an advanced/compat section in help; map composites to core recipes.  
- **Risk:** Removing legacy style tokens during the Form/Channel split can break memorised utterances.  
  - **Mitigation:** convert all style entries to Form/Channel now, update help/cheatsheets/tests, and provide a short migration notice in help.  
- **Risk:** Added verbs (`set`, `preset`) introduce new commands to learn.  
  - **Mitigation:** minimal `run` path stays; help panes and parse-back narrate active stance/defaults.  
- **Risk:** Preset management adds state.  
  - **Mitigation:** small guardrail tests; clear status/list; “preset save” derives from last run only.

---

## Implementation sketch

1) **Grammar/captures**
   - Keep `intent` as the sole setter for task/relational presets; no `relation` alias.  
   - Update `model run` capture to require one directional and accept exactly one Form and one Channel; apply the same Form/Channel caps to `again`, replay/history, suggest, and pattern consumers.  
   - Adjust `again` to allow optional directional reuse.

2) **Token surfacing**
   - Core directional names + aliases; hide composites from default help.  
   - Style lists refactored into Form/Channel buckets with no legacy style aliases retained.  
   - Persona/purpose lists trimmed; keep aliases for retired items mapped to presets or canonical tokens.

3) **Presets**
   - Store presets (prompt + persona + intent/relation + contract + directional + dest).  
   - Commands: `preset save/run/list`; small canvas or spoken feedback on apply.

4) **UI/help/feedback**
   - Help panes for `who/why/how/form`; parse-back summaries after capture; axis docs updated to reflect Form/Channel and core directionals.  
   - Quick help shows minimal surface; compatibility appendix lists aliases.

5) **Tests/guardrails**
   - Grammar capture tests for new verbs and required directional.  
   - Alias resolution tests (composite directionals; Form/Channel enforced without legacy style aliases).  
   - Preset save/run coverage and stance/default persistence.  
   - Parse-back text assertions to prevent regressions in user feedback.  
   - Post-migration guardrails to assert single-value Form/Channel across captures, replay/history, and UI surfacing.

---

## Outstanding follow-ups (tracked for implementation)
- Highest-risk hybrid to cut: `modelPrompt` is now migrated to `[form] [channel] <directional>` with style removed; `run/again` (and rerun helpers) were already migrated. Remaining capture cutovers: `suggest/replay/history` and any other style-bearing entrypoints. Finish migrating them to the single-cardinality shape, drop legacy style tokens/aliases, and block spoken style+form coexistence.
- Add an explicit guardrail/check to fail when `styleModifier` is spoken after the migration (for example, a capture regression that expects `model run ... style` to be rejected) so hybrid reintroduction is caught early.
- Require the axis registry/readme drift checks to fail if any style token remains in the SSOT or Talon lists after migration, and add a negative voice/capture test that surfaces a migration message when a legacy style token is spoken.
- Remove style from state/hydration and recaps: retire `last_style`/style defaults, plumb form/channel through rerun/helpers/system prompt/history/parse-back, and ensure resets/defaults cover form/channel singletons.
- Update help/cheatsheets/parse-back with migration messaging and explicit cardinalities once grammar/state are switched; surface the Form/Channel defaults fallback and directional requirement.
- Strengthen guardrails/tests: axis registry drift should exclude style and include form/channel; add capture/recap/rerun tests enforcing single form/channel and exactly one directional lens across run/again/suggest/replay/history.
- Remove any remaining `+` multiplicity notation in help/captures; repeat tokens explicitly per cardinality (scope×2, method×3, form×1, channel×1, directional×1).
- Suggested execution order (risk-first): (1) finish the hybrid capture cutover (`modelPrompt` plus suggest/replay/history/apply/please); (2) switch state/hydration/resets/recap to form/channel-only; (3) align UI/help/cheatsheets/parse-back; (4) land guardrail/tests for caps and alias removal; (5) clean multiplicity notation.
- Acceptance for the hybrid-cutover slice: (a) `styleModifier` no longer accepted in any capture, with explicit coverage for `modelPrompt` and `suggest/replay/history/apply/please` (run/again already migrated); (b) state/rerun/recap/help/cheatsheet surfaces show form/channel only; (c) drift/readme/list guardrails fail if style tokens remain; (d) negative voice/capture test asserts migration messaging when a legacy style token is spoken; (e) caps tests enforce form=1/channel=1/directional=1 with scope×2, method×3.
- Risk-first pre-cutover checks: before switching the remaining captures, run the capture/grammar suites that exercise `modelPrompt` and rerun flows (for example `python3 -m pytest _tests/test_gpt_actions.py -k run_again` and `python3 -m pytest _tests/test_talon_settings_model_prompt.py`) to surface regressions early; repeat them immediately after the cutover to confirm the new grammar shape.
- No further ADR text changes planned; future loops must land implementation/guardrail/doc deltas tied to these follow-ups (status-only loops remain frozen).

---

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
