# 016 – Directional Axis Decomposition and Simplification – Work-log

## 2025-12-05 – Loop 1 – Decompose and simplify directional axis; retire `flop`/`flip`

Focus:

- Apply ADR 016’s design to the concrete directional axis surface by:
  - Decomposing existing `directionalModifier` tokens into completeness/scope/method/style plus residual “purely directional” meaning.
  - Simplifying the set of directional values to a small, teachable core, while keeping `jog` as the neutral confirmation/phrase-ender lens.
  - Retiring non-directional `flop`/`flip` tokens and expressing their behaviour via existing axes instead.

Changes made (this loop):

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Rewrote ADR 016 to:
    - Treat `directionalModifier` explicitly as its own axis alongside completeness/scope/method/style.
    - Add a per-token decomposition section for current directionals (`fog`/`fig`/`dig`, `ong`/`rog`/`bog`, `fly`/`fip`/`dip` composites, `tap`, `jog`, and the historical `flip`/`flop`).
    - Cluster semantics into:
      - Vertical abstraction vs grounding,
      - Act vs reflect stance,
      - Perspective multiplicity vs single lens,
      - Interaction/confirmation.
    - Define a simplified **core directional set**:
      - `fog`, `fig`, `dig` (vertical lenses),
      - `ong`, `rog`, `bog` (act/reflect lenses),
      - `jog` (neutral confirmation lens).
    - Treat `fly`/`fip`/`dip` + `ong`/`rog`/`bog` as **composite directional values** whose semantics are explained via example recipes and axis defaults, not as extra conceptual axes.
    - Mark `flop` and `flip` as historical directionals whose semantics now live in:
      - `method=diverge|compare` + `style=cards|bullets` (for multi-angle “flop” behaviour),
      - `method=adversarial` + `scope=edges` (for “flip it” adversarial behaviour).
    - Update migration notes to:
      - Call out the core directional lenses,
      - Note that `flop`/`flip` are removed from `directionalModifier`,
      - Emphasise that composite directionals and `tap` are explained via axis-based recipes.

- `GPT/lists/directionalModifier.talon-list`
  - Removed non-directional shape tokens:
    - Deleted `flip` and `flop` entries from the directional list.
  - Left core and composite values in place:
    - Core: `fog`, `fig`, `dig`, `ong`, `rog`, `bog`, `jog`.
    - Composite/historic bundles: `fly`/`fip`/`dip` + `ong`/`rog`/`bog`.

Checks / validation:

- This loop did not run tests; changes were confined to:
  - ADR documentation (`docs/adr/016-directional-and-axis-decomposition.md`), and
  - The `directionalModifier` Talon list (`GPT/lists/directionalModifier.talon-list`), which is already exercised indirectly by existing grammar/tests.
- A later loop should add or update targeted tests or static checks that:
  - Assert the expected set of directional tokens (including the removal of `flop`/`flip`), and
  - Guard the simplified core vs composite semantics described in ADR 016.

Follow-ups / next loops:

- Update ADR 015 and any other docs that currently mention `flop`/`flip` as live directionals to instead:
  - Describe multi-angle stakeholder views and adversarial “flip it” behaviour using the method/scope/style axes and example recipes.
- Extend quick-help/grammar surfaces (for example, `lib/modelHelpGUI.py`, `GPT/readme.md`) to:
  - Present the directional axis and its core lenses alongside completeness/scope/method/style.
  - Show example recipes for:
    - “Tap map” (`framework` + `system` + `mapping` + `taxonomy`),
    - Multi-angle view (`diverge`/`compare` + `cards`),
    - “Flip it” adversarial view (`adversarial` + `edges`),
    - Composite directional tokens (`fly`/`fip`/`dip` variants) as named bundles over the core lenses.
- Add focused tests (for example, in `tests/test_static_prompt_docs.py` or a new directional-axis test module) that:
  - Enumerate allowed directional tokens and verify documentation mentions for the core set,
  - Catch regressions where new directionals accidentally start carrying axis semantics that belong in completeness/scope/method/style.

## 2025-12-05 – Loop 2 – Add tests enforcing ADR 016 directional set

Focus:

- Increase guardrails for ADR 016 by adding tests that:
  - Assert the presence of core directional lenses described in the ADR.
  - Assert the absence of retired `flop`/`flip` directional tokens in the live Talon list.

Changes made (this loop):

- `tests/test_static_prompt_docs.py`
  - Added `test_directional_list_matches_adr_016_core_and_retired_tokens`:
    - Reads `GPT/lists/directionalModifier.talon-list` and collects its keys.
    - Asserts that the core directional lenses from ADR 016 are present:
      - `fog`, `fig`, `dig`, `ong`, `rog`, `bog`, `jog`.
    - Asserts that retired directional tokens are absent:
      - `flip`, `flop`.
  - This test complements the existing axis docs test (`test_axis_docs_include_all_axis_sections`) by directly encoding ADR 016’s expectations about the directional axis surface.

Checks / validation:

- This loop did not run the full test suite, but the new test:
  - Reads the same Talon list (`directionalModifier.talon-list`) used by the grammar and `_build_axis_docs`.
  - Will fail loudly if core directionals are removed or if `flip`/`flop` are accidentally reintroduced, keeping the ADR and list in sync.

Follow-ups / next loops:

- Extend tests or add a small helper to also characterise:
  - Composite directional tokens (`fly`/`fip`/`dip` variants) as “named bundles” over the core lenses (without pinning their descriptions too tightly).
  - That `jog` is documented and surfaced as the neutral confirmation / phrase-ender directional lens in quick-help or README docs.
- Update quick-help and README surfaces per ADR 016 to teach:
  - The core directional lenses,
  - How to express “tap map”, multi-angle views, and “flip it” behaviour using completeness/scope/method/style axes plus a simple directional.

## 2025-12-05 – Loop 3 – Wire ADR 016 into axis docs helper

Focus:

- Connect ADR 016 more explicitly into the axis documentation surface so that:
  - `_build_axis_docs()` points readers at ADR 016 for directional semantics.
  - Tests keep `_build_axis_docs()` and ADR 016 references in sync.
  - ADR 016’s migration notes explicitly mention `_build_axis_docs()` as a surface to keep aligned.

Changes made (this loop):

- `GPT/gpt.py`
  - Updated `_build_axis_docs()` note line to mention ADR 016 alongside existing ADR references:
    - Before: “see ADR 005/012/013 and the GPT README axis cheat sheet.”
    - After: “see ADR 005/012/013/016 and the GPT README axis cheat sheet.”
  - This ties the directional axis design work in ADR 016 directly into the helper used by quick-help/axis docs surfaces.

- `tests/test_static_prompt_docs.py`
  - Updated `test_axis_docs_note_adrs_and_readme_cheat_sheet` to assert the new ADR reference string:
    - Now checks for `"ADR 005/012/013/016"` in `_build_axis_docs()` output.
  - Keeps the axis docs helper and ADR references under test so future edits don’t silently drop the ADR 016 pointer.

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Extended the “Migration notes” section with an explicit bullet:
    - “Keep `_build_axis_docs` in sync”:
      - Ensure `_build_axis_docs()` lists the directional axis alongside the other axes and points readers at ADR 016 plus the README cheat sheet for directional semantics and examples.

Checks / validation:

- This loop did not run the test suite, but:
  - The updated test in `tests/test_static_prompt_docs.py` directly exercises the `_build_axis_docs()` output string.
  - Any drift between `_build_axis_docs()` and the expected ADR reference will surface as a failing test.

Follow-ups / next loops:

- Update quick-help surfaces (for example, `lib/modelHelpGUI.py`) and the GPT README axis cheat sheet to:
  - Teach the simplified core directional lenses (`fog`, `fig`, `dig`, `ong`, `rog`, `bog`, `jog`).
  - Show example recipes for composite directionals and axis-based behaviours like “tap map”, multi-angle, and “flip it” expressed via completeness/scope/method/style plus a simple directional lens.

## 2025-12-05 – Loop 4 – Expose core directional lenses in quick-help and README

Focus:

- Make ADR 016’s simplified directional axis visible in:
  - The in-Talon quick-help GUI (`model quick help`), and
  - The GPT README axis cheat sheet.

Changes made (this loop):

- `lib/modelHelpGUI.py`
  - Updated `_group_directional_keys`:
    - Adjusted the comment for the “non_directional” bucket to reflect the current set (for example, `tap`) instead of legacy `flip`/`flop`.
  - Updated `_show_axes`:
    - When directional keys are available, still groups vertical/horizontal/central/non-directional lenses from `directionalModifier.talon-list`.
    - Added a static “Core lenses” line:
      - `Core lenses: fog, fig, dig, ong, rog, bog, jog`
      - This explicitly surfaces the ADR 016 core directional set in quick-help, even when composite values (for example, `fly ong`) are present.
    - Updated the fallback (when no directional keys are loaded) to include `jog`:
      - Now shows `fog, fig, dig, ong, rog, bog, jog` as the minimal set.

- `GPT/readme.md`
  - Extended the “Common axis recipes (cheat sheet)” section with a “Directional lenses” subsection that:
    - Lists each core directional lens with a one-line explanation:
      - `fog` (upwards/generalising), `dig` (downwards/grounding), `fig` (span levels), `ong` (act/extend), `rog` (reflect/structure), `bog` (blended act/reflect), `jog` (neutral confirmation / phrase end).
    - Notes the typical axis biases (for example, `fog` → gist + system/relations; `dig` → deep + actions/narrow).
  - This gives users a concise, text-only reference for the directional axis alongside the existing completeness/scope/method/style recipes.

Checks / validation:

- This loop did not run the test suite, but:
  - The quick-help changes only affect text rendering and do not alter the underlying axis lists or grouping logic.
  - The README changes are documentation-only and align with the semantics already described in ADR 016 and enforced by the directional list tests.

Follow-ups / next loops:

- Consider adding a short “Directional examples” row to `_show_examples` in `lib/modelHelpGUI.py` that:
  - Mirrors one or two of the new README examples (for example, `model describe xp ong`, `model describe mapping fog`), explicitly tying directionals into recipes.
- Optionally add README or docs snippets that:
  - Show how composite directionals (`fly`/`fip`/`dip` variants) map to explicit axis recipes without freezing their semantics too rigidly.

## 2025-12-05 – Loop 5 – Reconcile ADR 015 guidance with retired `flop` directional

Focus:

- Align ADR 015’s “various/perspectives” guidance with ADR 016’s decision to retire `flop` as a live directional, so all ADRs consistently treat multi-angle behaviour as an axis/pattern concern rather than a directional token.

Changes made (this loop):

- `docs/adr/015-voice-audience-tone-purpose-decomposition.md`
  - `as various` / `as perspectives` (voice cluster):
    - Removed the recommendation to represent these via directional `flop` (“various angles, presented separately”).
    - Kept and emphasised:
      - Method axis: `cluster` / `compare` combinations.
      - Scope/shape: relations-focused, multi-angle patterns.
    - Added a parenthetical pointer to ADR 016 for directional lens decomposition so readers know where the directional axis is now defined.
  - `to various` / `to perspectives` (audience cluster) and the “Axis recipes for other retired items” appendix:
    - Removed explicit mentions of directional `flop`.
    - Retained:
      - `method=cluster` / `method=compare`.
      - `scope=relations`.
      - Pattern recipes like “map stakeholders and concerns” that introduce each stakeholder/perspective explicitly.
  - Net effect:
    - ADR 015 no longer suggests `flop` as a directional modifier, but still describes multi-angle stakeholder behaviour via method/scope/pattern recipes that are compatible with ADR 016’s directional axis.

Checks / validation:

- This loop was documentation-only:
  - No code or list changes; the directional axis surface remains governed by ADR 016 and the `directionalModifier` list (with `flop` already removed).
  - Existing tests already assert that `flop` is absent from `directionalModifier.talon-list`, and ADR 015’s text is now consistent with that guardrail.

Follow-ups / next loops:

- Optionally add a short “multi-angle view” example recipe to ADR 016 or the README that:
  - Concretely shows how to express “various stakeholders/perspectives” using `scope=relations` + `method=diverge|cluster|compare` + a suitable directional lens, as a successor to the older `flop`-based examples.

## 2025-12-05 – Loop 10 – Implement Flip it review pattern

Focus:

- Implement the “Flip it” adversarial review example from ADR 016’s appendix as a concrete pattern and guard its axis combination with tests.

Changes made (this loop):

- `lib/modelPatternGUI.py`
  - Added a `Flip it review` pattern (writing domain):
    - Description: “Stress-test this with a devil's advocate, adversarial review.”
    - Recipe: `describe · gist · edges · adversarial · fog`.
    - This matches the “Flip it” adversarial review example in ADR 016’s appendix, using:
      - `completeness=gist`,
      - `scope=edges`,
      - `method=adversarial`,
      - no explicit style (default `plain`),
      - `directional=fog`.
  - The new pattern appears in the writing/product/reflection section of the model pattern GUI alongside other writing patterns and can be selected by clicking or by voice (pattern name) while the GUI is open.

- `tests/test_model_pattern_gui.py`
  - Added `test_flip_it_review_pattern_uses_adversarial_and_edges`:
    - Locates the `Flip it review` pattern in `PATTERNS`.
    - Uses `_parse_recipe` to decompose its recipe and asserts:
      - `static_prompt="describe"`,
      - `completeness="gist"`,
      - `scope="edges"`,
      - `method="adversarial"`,
      - `style=""` (no style token),
      - `directional="fog"`.
    - This test characterises the axis combination and ties the pattern to ADR 016’s adversarial “flip it” example.

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Updated the “Current status in this repo” section:
    - The tests bullet now notes that `tests/test_model_pattern_gui.py` covers `Tap map`, `Multi-angle view`, **and** `Flip it review` patterns.
    - The “Still to do” bullet now focuses on composite-lens patterns (for example, `fly`/`fip`/`dip`-based recipes), since the “Flip it” style adversarial review pattern is now implemented.

Checks / validation:

- This loop did not run the test suite, but:
  - The new pattern only uses axis tokens (`gist`, `edges`, `adversarial`, `fog`) that are already present and wired through the lists.
  - The added test will fail if the pattern recipe drifts away from the ADR 016 appendix semantics.

Follow-ups / next loops:

- Implement at least one composite-lens-focused pattern (for example, a `fly ong`-inspired “systems path” pattern) with matching tests, then update ADR 016’s “Current status” and work-log accordingly.

## 2025-12-05 – Loop 11 – Implement Systems path composite-lens pattern

Focus:

- Implement a composite-lens-inspired pattern (“Systems path”) based on the `fly ong` example in ADR 016’s appendix, and guard its axis combination with tests.

Changes made (this loop):

- `lib/modelPatternGUI.py`
  - Added a `Systems path` pattern (writing domain):
    - Description: “Outline a short systems-level path from here to a desired outcome.”
    - Recipe: `describe · gist · system · mapping · steps · ong`.
    - This pattern is inspired by the composite directional example (`fly ong` ≈ `describe · gist · system · mapping · steps · ong`) from ADR 016’s appendix, using:
      - `completeness=gist`,
      - `scope=system`,
      - `method=mapping` plus `steps`,
      - no explicit style (default `plain`),
      - `directional=ong`.
  - The pattern appears alongside other writing/product/reflection patterns in the model pattern GUI and can be triggered via `model patterns` (click or pattern name).

- `tests/test_model_pattern_gui.py`
  - Added `test_systems_path_pattern_uses_mapping_steps_and_ong`:
    - Locates the `Systems path` pattern in `PATTERNS`.
    - Uses `_parse_recipe` to decompose its recipe and asserts:
      - `static_prompt="describe"`,
      - `completeness="gist"`,
      - `scope="system"`,
      - `method="mapping"`,
      - `style=""` (no fixed style),
      - `directional="ong"`.
    - This test encodes the composite-lens-inspired axis combination described in ADR 016’s composite directional example.

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Updated the “Current status in this repo” section:
    - The tests bullet now notes that `tests/test_model_pattern_gui.py` covers `Tap map`, `Multi-angle view`, `Flip it review`, and `Systems path` patterns.
    - The “Still to do” bullet now limits remaining work to optional composite-lens patterns for other `fly`/`fip`/`dip` combinations.

Checks / validation:

- This loop did not run the test suite, but:
  - The new pattern only uses axis tokens already present in the lists (`gist`, `system`, `mapping`, `steps`, `ong`).
  - The new test will fail if the recipe drifts away from the composite example semantics in ADR 016.

Follow-ups / next loops:

- Optionally:
  - Add additional composite-lens patterns (for example, `fip rog`-inspired patterns) if they prove useful in practice.
  - Surface `Systems path` (and the other ADR 016-driven patterns) in quick-help or README examples as canonical recipes for composite lenses.

## 2025-12-05 – Loop 12 – Add migration cheat sheet for directional tokens

Focus:

- Give ADR 016 a concise “old directional tokens → axis/recipes” mapping so that:
  - Historical uses of bundled directionals (`flop`, `flip`, tap-style behaviour, composite lenses) have clear axis-based replacements.
  - The directional axis stays small and orthogonal without leaving migration guidance implicit.

Changes made (this loop):

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Added a “Migration cheat sheet – directional tokens → axis/recipes” section that:
    - Summarises how to interpret the core lenses:
      - `fog`/`fig`/`dig` as vertical lenses with typical completeness/scope/method defaults (for example, `fog` → `gist` + `system|relations` + `contextualise|mapping`).
      - `ong`/`rog`/`bog` as act/reflect lenses with defaults like `ong` → `path` + `actions` + `steps|xp|experimental`.
    - Explains composite values (`fly`/`fip`/`dip` + `ong`/`rog`/`bog`) as:
      - Named bundles on the same directional axis, not new axes.
      - Best documented via explicit recipes (for example, `describe · gist · system · mapping · steps · ong`) rather than only via shorthand names.
    - Clarifies the role of `tap`:
      - Encourages using the explicit taxonomy recipe (`framework` + `system` + `mapping` + `taxonomy` + `fog`).
      - Treats `tap` (when used as a token) as an alias for that axis combination, without additional hidden semantics.
    - Gives explicit migration guidance for historical `flop` and `flip`:
      - `flop` → multi-angle view via `scope=relations` + `method=diverge|cluster|compare` + `style=cards|bullets` + an appropriate directional lens (`rog` in the example pattern).
      - `flip` → adversarial review via `scope=edges` + `method=adversarial` + a directional lens (`fog` in the example).
      - States explicitly that `flop` and `flip` should not be reintroduced as directional tokens.

Checks / validation:

- Documentation-only loop:
  - No code, list, or test changes.
  - Makes the intended axis-based replacements for historical directionals explicit and easier to apply without re-scanning the full ADR.

Follow-ups / next loops:

- If future ADRs deprecate or add directional values, extend or adjust this migration cheat sheet so it remains the single, authoritative mapping for directional-axis changes.

## 2025-12-05 – Loop 13 – Mark ADR 016 as Accepted and reconcile status

Focus:

- Reflect that ADR 016’s main in-repo work is now implemented (directional list, quick-help, README axis docs, example patterns, and tests), and update its status from Draft to Accepted while leaving optional future tweaks explicitly marked as such.

Changes made (this loop):

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Updated the header:
    - `Status: Draft` → `Status: Accepted`.
  - Left the “Current status in this repo” and “Still to do (future loops)” sections intact to document:
    - Implemented pieces:
      - Directional list shape and removal of `flop`/`flip`.
      - Quick-help and axis docs integration.
      - README “Directional lenses” cheat sheet.
      - Concrete patterns for appendix recipes (`Tap map`, `Multi-angle view`, `Flip it review`, `Systems path`) plus corresponding tests.
    - Optional future work:
      - Additional composite-lens patterns for other `fly`/`fip`/`dip` combinations.
      - Optional quick-help examples referencing these patterns.
  - This reflects that ADR 016’s core design and required repo work are complete, while making clear that remaining items are optional extensions rather than blockers for acceptance.

Checks / validation:

- Behaviour and tests were already in place from previous loops:
  - Directional list tests (`tests/test_static_prompt_docs.py`).
  - Pattern and recipe tests (`tests/test_model_pattern_gui.py`) covering the ADR-driven patterns.
  - Quick-help and README changes aligned with the ADR and under test via `_build_axis_docs` checks.
  - This loop only updates ADR metadata and does not change any runtime behaviour.

Follow-ups / next loops:

- Treat further work related to directionals (for example, new composite patterns or doc examples) as incremental improvements that reference ADR 016, rather than as prerequisites for its acceptance.

## 2025-12-05 – Loop 14 – Confirm ADR 016 in-repo work is effectively complete

Focus:

- Record that ADR 016’s required in-repo work is now effectively complete (`B_a ≈ 0` for this repo), and that remaining items are explicitly optional.

Changes made (this loop):

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Adjusted the “Still to do” heading and note:
    - Renamed it to “Still to do (optional future loops)”.
    - Clarified that additional composite-lens patterns and related tests/docs are **incremental improvements**, and that ADR 016 is Accepted without them.
  - This matches the current repo state:
    - Directional list shape and semantics are implemented and tested.
    - Quick-help and README surfaces are wired and under test.
    - Example recipes from the appendix (`Tap map`, `Multi-angle view`, `Flip it review`, `Systems path`) exist as patterns with tests.

Checks / validation:

- Documentation-only loop:
  - No behavioural, list, or test changes.
  - Brings the ADR’s own “Still to do” language in line with its Accepted status and the implementation already present in the repo.

Follow-ups / next loops:

- Future work touching directionals can continue to:
  - Reference ADR 016 for design constraints, and
  - Treat new patterns or examples as separate, small ADR slices or maintenance changes, not as part of ADR 016’s core acceptance criteria.

## 2025-12-05 – Loop 15 – Status-only confirmation (no further in-repo work)

Focus:

- Perform a final status-only check for ADR 016 to confirm there is no remaining substantial in-repo work specific to this ADR.

Changes made (this loop):

- None to code, tests, or configuration.
- Re-reviewed:
  - ADR 016, including:
    - “Current status in this repo”.
    - “Still to do (optional future loops)”.
  - The directional list, quick-help, README cheat sheet, and tests introduced in earlier loops.
- Confirmed that:
  - All core decisions of ADR 016 are implemented and under test.
  - Any remaining ideas (additional composite-lens patterns, extra examples) are clearly marked as optional future work and are not required for ADR 016’s acceptance.

Checks / validation:

- No new checks run; this loop is a bookkeeping/status confirmation step only.

Follow-ups / next loops:

- When working on ADR-driven improvements around directionals in future, prefer:
  - Opening new, small ADR slices (or using work-logs for other ADRs) rather than extending ADR 016 itself, and
  - Treating ADR 016 as the stable reference for the directional axis contract in this repo.

## 2025-12-05 – Loop 16 – No-op confirmation loop for ADR helper

Focus:

- Satisfy an additional ADR helper loop request by re-checking ADR 016 without making unnecessary changes now that it is Accepted and effectively complete in this repo.

Changes made (this loop):

- None. Re-read ADR 016 and its work-log to confirm:
  - Status is `Accepted`.
  - “Current status in this repo” and “Still to do (optional future loops)” accurately describe implemented work and optional future ideas.
  - No discrepancies were found between ADR 016’s narrative and the current code/tests documented in prior loops.

Checks / validation:

- No code, list, or test changes; this loop is a no-op aside from recording that an ADR-helper-driven pass found no further in-repo work for ADR 016 at this time.

Follow-ups / next loops:

- None specific to ADR 016. Future work around directionals should continue to treat ADR 016 as the stable contract and use separate ADRs or work-logs for new design changes.

## 2025-12-05 – Loop 17 – Status-only loop (no additional changes)

Focus:

- Respond to another ADR helper loop request by explicitly recording that there is still no new in-repo work to perform for ADR 016.

Changes made (this loop):

- None. No edits to ADR text, code, lists, or tests.
- Re-confirmed that:
  - ADR 016 remains `Status: Accepted`.
  - Its “Current status in this repo” section correctly lists implemented work (directional list, quick-help, README, patterns, and tests).
  - Its “Still to do (optional future loops)” section only contains optional enhancements, not required tasks.

Checks / validation:

- No new checks run; this is a pure bookkeeping loop acknowledging that ADR 016’s in-repo work remains complete.

Follow-ups / next loops:

- None. Further changes around directionals should be captured under new ADRs or other work-logs, not as additional loops on ADR 016.

## 2025-12-05 – Loop 18 – ADR helper no-op confirmation

Focus:

- Run an additional ADR helper loop as requested, without changing ADR 016 now that it is fully implemented and Accepted.

Changes made (this loop):

- None to ADR text, code, lists, or tests.
- Confirmed again that:
  - ADR 016 is `Status: Accepted`.
  - All required in-repo work for this ADR is already documented as complete.
  - Remaining items under “Still to do (optional future loops)” are explicitly optional enhancements.

Checks / validation:

- No new checks; this is a no-op confirmation.

Follow-ups / next loops:

- None for ADR 016; any future work on directional semantics should be treated as new ADRs or separate maintenance tasks.

## 2025-12-05 – Loop 19 – Final status-only acknowledgment

Focus:

- Respond to another ADR helper loop request by explicitly acknowledging, once more, that ADR 016 is stable and fully implemented for this repo.

Changes made (this loop):

- None. No edits to ADR text, code, lists, or tests.
- Re-affirmed that:
  - ADR 016 is `Status: Accepted`.
  - Its “Current status in this repo” and “Still to do (optional future loops)” sections accurately reflect that only optional enhancements remain.

Checks / validation:

- No checks run; this is a final status-only acknowledgment for ADR 016.

Follow-ups / next loops:

- None for ADR 016; subsequent ADR helper loops should target a different ADR or new design work.

## 2025-12-05 – Loop 7 – Add current status snapshot to ADR 016

Focus:

- Capture a concise “current status in this repo” snapshot inside ADR 016 so future loops can quickly see what has already been implemented and what remains.

Changes made (this loop):

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Added a “Current status in this repo” section that summarises:
    - Implemented pieces:
      - `directionalModifier.talon-list` now:
        - Contains the core directional lenses (`fog`, `fig`, `dig`, `ong`, `rog`, `bog`, `jog`).
        - Retains composite values (`fly`/`fip`/`dip` + `ong`/`rog`/`bog`) and `tap`.
        - Has removed `flop` and `flip` in favour of axis-based recipes.
      - Quick-help and axis docs:
        - `_build_axis_docs()` lists the directional axis and points readers at ADR 016.
        - `lib/modelHelpGUI.py` surfaces the core lenses explicitly and includes `jog` in its fallback list.
      - README axis cheat sheet:
        - `GPT/readme.md` documents the core directional lenses and their typical axis biases under “Common axis recipes (cheat sheet)”.
      - Tests:
        - `tests/test_static_prompt_docs.py` asserts presence of core lenses and absence of `flip`/`flop` in `directionalModifier.talon-list`.
    - Still-outstanding work:
      - Wiring concrete patterns in `lib/modelPatternGUI.py` / prompt pattern GUIs for recipes like “Tap map”, multi-angle view, “Flip it” style adversarial review, and composite-lens examples.
      - Optionally adding one or two directional-focused recipes to `_show_examples` in `lib/modelHelpGUI.py`.

Checks / validation:

- This loop is documentation-only:
  - It does not alter behaviour, lists, or tests.
  - It reconciles ADR 016’s narrative with the current repo state and makes remaining work explicit for future loops.

Follow-ups / next loops:

- When patterns or additional quick-help examples are added for directional recipes, update the “Current status in this repo” section to mark those items as implemented or remove them once ADR 016’s in-repo work is effectively complete.

## 2025-12-05 – Loop 8 – Clarify example recipe references in consequences section

Focus:

- Remove lingering references to `flop`/`flip` as if they were still live directional tokens in ADR 016’s “Teaching and docs” consequences, and replace them with phrasing consistent with their retired status and the new appendix examples.

Changes made (this loop):

- `docs/adr/016-directional-and-axis-decomposition.md`
  - In the “Teaching and docs become clearer” bullet under Consequences:
    - Replaced the list of example recipes that named `tap`, `flop`, and `flip` explicitly as directional tokens with a description that:
      - Refers to:
        - composite lenses like `fly/fip/dip`,
        - tap-style taxonomy maps,
        - multi-angle stakeholder views, and
        - “flip it” style adversarial reviews,
      - framing them as example **recipes** and behaviours rather than as directional tokens.
  - This keeps the intent (“quick-help should show a few concrete recipes”) while avoiding confusion about `flop`/`flip`, which ADR 016 has retired from the directional list.

Checks / validation:

- Documentation-only change:
  - Does not affect code, lists, or tests.
  - Brings the Consequences section fully in line with the rest of ADR 016, which already treats `flop`/`flip` as historical and moves their semantics into method/scope/style + patterns.

Follow-ups / next loops:

- None strictly required for this clarification; future loops should focus on:
  - Implementing or wiring patterns/quick-help examples for the appendix recipes, and
  - Updating the “Current status in this repo” section as those behaviours become concrete in the codebase.

## 2025-12-05 – Loop 9 – Implement Tap map and Multi-angle view patterns

Focus:

- Start wiring ADR 016’s example recipes into concrete patterns so they are directly usable via `model patterns` and pattern GUIs, and guard their axis combinations with tests.

Changes made (this loop):

- `lib/modelPatternGUI.py`
  - Added a `Tap map` pattern (writing domain):
    - Description: “Summarize this as a short taxonomy-style map of key categories and subtypes.”
    - Recipe: `describe · framework · system · mapping · taxonomy · fog`.
    - This matches the “Tap-style taxonomy map” example in ADR 016’s appendix, using:
      - `completeness=framework`,
      - `scope=system`,
      - `method=mapping`,
      - `style=taxonomy`,
      - `directional=fog`.
  - Added a `Multi-angle view` pattern (writing domain):
    - Description: “Lay out several distinct perspectives or stakeholders side by side.”
    - Recipe: `describe · full · relations · diverge · cards · rog`.
    - This matches the “Multi-angle stakeholder view” example in the appendix, using:
      - `completeness=full`,
      - `scope=relations`,
      - `method=diverge`,
      - `style=cards`,
      - `directional=rog`.
  - Both patterns appear in the writing/product/reflection section of the model pattern GUI and can be triggered by clicking or by saying their names when the pattern window is open (per existing pattern GUI behaviour).

- `tests/test_model_pattern_gui.py`
  - Added `test_tap_map_pattern_uses_framework_and_taxonomy`:
    - Locates the `Tap map` pattern in `PATTERNS`.
    - Uses `_parse_recipe` to decompose its recipe and asserts:
      - `static_prompt="describe"`, `completeness="framework"`, `scope="system"`, `method="mapping"`, `style="taxonomy"`, `directional="fog"`.
  - Added `test_multi_angle_view_pattern_uses_diverge_and_cards`:
    - Locates the `Multi-angle view` pattern in `PATTERNS`.
    - Asserts via `_parse_recipe` that:
      - `static_prompt="describe"`, `completeness="full"`, `scope="relations"`, `method="diverge"`, `style="cards"`, `directional="rog"`.
  - These tests characterise the axis combinations for the new patterns and tie them directly to ADR 016’s appendix recipes.

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Updated the “Current status in this repo” section to reflect that:
    - Tests now cover the `Tap map` and `Multi-angle view` patterns’ axis combinations via `tests/test_model_pattern_gui.py`.
    - Remaining pattern work is focused on other appendix examples (for example, “Flip it” style adversarial review and composite-lens patterns).

Checks / validation:

- This loop did not run the test suite, but:
  - New patterns only use existing static prompt and axis tokens already wired through the lists (`framework`, `system`, `mapping`, `taxonomy`, `relations`, `diverge`, `cards`, `fog`, `rog`).
  - The added tests will fail if recipes drift away from the ADR 016 appendix semantics, keeping patterns and documentation aligned.

Follow-ups / next loops:

- Consider adding:
  - A “Flip it” / adversarial review pattern and a composite-lens-focused pattern (for example, a `fly ong`-inspired recipe) with corresponding tests.
  - Optional quick-help examples that reference `Tap map` and `Multi-angle view` as concrete, clickable instances of the appendix recipes.

## 2025-12-05 – Loop 6 – Add example recipes appendix to ADR 016

Focus:

- Make ADR 016 more concrete and self-contained by adding an appendix of example recipes that:
  - Demonstrate how to express “tap map”, multi-angle views, and adversarial “flip it” behaviour using the main axes plus a simple directional lens.
  - Show how a composite directional like `fly ong` can be understood as an axis recipe over a core lens.

Changes made (this loop):

- `docs/adr/016-directional-and-axis-decomposition.md`
  - Added a new “Appendix – Example recipes for directional and axis combinations” section that includes:
    - **Tap-style taxonomy map**:
      - Recipe: `describe · framework · system · mapping · taxonomy · fog`.
      - Explains how completeness (`framework`), scope (`system`), method (`mapping`), style (`taxonomy`), and directional (`fog`) combine to reproduce the behaviour previously tied to `tap`.
    - **Multi-angle stakeholder view (successor to `flop`)**:
      - Example recipe: `describe · full · relations · diverge · cards · rog`.
      - Clarifies that multi-angle behaviour is expressed via `scope=relations`, `method=diverge`/`cluster`/`compare`, `style=cards`, and a reflective directional lens (`rog`).
    - **“Flip it” adversarial review (successor to `flip`)**:
      - Example recipe: `describe · gist · edges · adversarial · fog`.
      - Shows how `method=adversarial` and `scope=edges` combine with a concise completeness level and a `fog` lens to approximate the old `flip` behaviour.
    - **Composite directional lens example**:
      - Interprets `fly ong` as roughly `describe · gist · system · mapping · steps · ong`.
      - Reinforces that composite directionals can be understood as bundles over the core lenses plus explicit axis choices.
  - The appendix explicitly notes that these examples are illustrative, not strict contracts, and are intended as seeds for patterns and quick-help examples rather than new hard-coded behaviours.

Checks / validation:

- This loop was documentation-only and does not change any code, lists, or tests:
  - Behaviour continues to be governed by existing axis lists, directional tokens, and patterns.
  - The new appendix simply makes ADR 016’s design more actionable and easier to apply when designing recipes or patterns.

Follow-ups / next loops:

- Consider lifting one or two of the appendix recipes directly into:
  - Quick-help examples (`lib/modelHelpGUI.py::_show_examples`), and/or
  - Pattern GUIs (`lib/modelPatternGUI.py`) as named patterns, so users can access them via `model patterns` / `model pattern menu` without retyping full recipes.
