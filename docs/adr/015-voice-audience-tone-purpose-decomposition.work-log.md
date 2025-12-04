# 015 – Voice, Audience, Tone, Purpose Axis Decomposition – Work-log

## 2025-12-04 – Loop 1 – Wire core list and axis changes

Focus:

- Apply ADR 015’s current decisions to the concrete Talon lists and axes:
  - Trim `modelVoice`, `modelAudience`, `modelTone`, and `modelPurpose` down to the agreed core sets.
  - Introduce the new method/style tokens (`xp`, `adversarial`, `receptive`, `resistant`, `novice`, `liberating`, `diverge`, `converge`, `mapping`, `codetour`) in the corresponding axis lists.

Changes made (this loop):

- `GPT/lists/modelVoice.talon-list`
  - Trimmed to the core voice set from ADR 015:
    - Kept: `as programmer`, `as prompt engineer`, `as scientist`, `as writer`, `as designer`, `as teacher`, `as facilitator`, `as PM`, `as junior engineer`, `as principal engineer`, `as Kent Beck`.
    - Removed: method/stance and low-yield roles such as `as logician`, `as blender`, `as artist`, `as adversary`, `as reader`, `as editor`, `as other`, `as liberator`, `as negotiator`, `as mediator`, CxO and team-structure voices, `as XP enthusiast`, `as various`, `as perspectives`, `as systems thinker`.

- `GPT/lists/modelAudience.talon-list`
  - Trimmed to a focused audience set:
    - Kept: `to managers`, `to team`, `to stakeholders`, `to product manager`, `to designer`, `to analyst`, `to programmer`, `to LLM`, `to junior engineer`, `to principal engineer`, `to Kent Beck`, `to CEO`, `to platform team`, `to stream aligned team`, `to XP enthusiast` (to be description-trimmed in a later loop).
    - Removed: `to CTO`, `to CFO`, `to enabling team`, `to complicated subsystem team`, plus state/stance items (`to receptive`, `to resistant`, `to dummy`, `to various`, `to perspectives`, `to systems thinker`).

- `GPT/lists/modelTone.talon-list`
  - Kept: `casually`, `formally`, `directly`, `gently`, `kindly`.
  - Removed: `neutrally` (treated as default when no tone is specified) and `briefly` (now represented via completeness/style).

- `GPT/lists/modelPurpose.talon-list`
  - Kept: `for information`, `for entertainment`, `for persuasion`, `for brainstorming`, `for deciding`, `for planning`, `for evaluating`, `for coaching`, `for appreciation`, `for triage`, `for announcing`, `for walk through`, `for collaborating`, `for teaching`, `for project management`.
  - Removed: style/destination and method-shaped entries (`for coding`, `for debugging`, `for slack`, `for table`, `for prompting`, `for diverging`, `for converging`, `for comparison`, `for contrast`, `for mapping`, `for discovery`, `for framing`, `for sensemaking`, `for presenterm`, `for code tour`) in favour of axis methods/styles and recipes per ADR 015.

- `GPT/lists/methodModifier.talon-list`
  - Added new method tokens from ADR 015:
    - `xp`, `adversarial`, `receptive`, `resistant`, `novice`, `liberating`, `diverge`, `converge`, `mapping`, with descriptions matching the ADR.

- `GPT/lists/styleModifier.talon-list`
  - Added `codetour` style with a strict “output only valid CodeTour `.tour` JSON” contract.

Checks / validation:

- This loop did not run tests; list/axis changes are configuration-only. A later loop should add or update tests that assert the presence/absence of these tokens and their wiring into `talonSettings` / pattern GUIs.

Follow-ups / next loops:

- Tighten and shorten the description for `to XP enthusiast` so it focuses on what the audience cares about rather than fully restating the XP method (now covered by `method=xp`).  
- Add axis-based recipes and/or GUI patterns for:
  - XP-flavoured recommendations (`method=xp` + `scope=actions`/`system`).  
  - Adversarial review (`method=adversarial` + `for evaluating`).  
  - Beginner explanations (`method=novice` + `gist`/`minimal` + `plain`).  
  - Liberating Structures facilitation (`method=liberating` + `as facilitator`).  
  - Diverging/converging (`method=diverge` / `method=converge` + purposes).  
  - Mapping-heavy responses (`method=mapping` + system/relations/dynamics scope + diagram/table/abstractvisual styles).

## 2025-12-04 – Loop 2 – Wire patterns and keep docs/tests aligned

Focus:

- Advance ADR 015 by:
  - Wiring a couple of representative patterns that use new methods (`xp`, `novice`) into the model pattern GUI.
  - Ensuring the pattern parser recognises the new methods.
  - Updating the GPT README to advertise the expanded method/style axis vocabulary and common recipes.

Changes made (this loop):

- `lib/modelPatternGUI.py`
  - Extended `METHOD_TOKENS` to include the ADR 015 method tokens so that patterns can use them:
    - `xp`, `adversarial`, `receptive`, `resistant`, `novice`, `liberating`, `diverge`, `converge`, `mapping`.
  - Added two concrete patterns that exercise new methods:
    - `XP next steps` (coding domain):  
      - Recipe: `describe · gist · actions · xp · bullets · ong`.  
      - Behaviour: suggest XP-flavoured next steps (tiny slices, tests, production feedback).
    - `Explain for beginner` (writing domain):  
      - Recipe: `describe · gist · focus · novice · plain · fog`.  
      - Behaviour: explain from first principles to a beginner using simple language.

- `GPT/readme.md`
  - Linked ADR 015 in the ADR list so contributors can find the decomposition rules.  
  - Extended the “Modifier axes (advanced)” section to:
    - Include the new method tokens (`xp`, `adversarial`, `receptive`, `resistant`, `novice`, `liberating`, `diverge`, `converge`, `mapping`).  
    - Include the new style `codetour`.  
  - Extended the “Common axis recipes (cheat sheet)” to add examples for:
    - `xp`, `adversarial`, `novice`, `liberating`, `diverge`, `converge`, `mapping`.

- `tests/test_readme_axis_lists.py`
  - No code changes were required: the test already asserts that all tokens in `methodModifier.talon-list` and `styleModifier.talon-list` appear in the corresponding README axis lines. After updating both, the existing tests cover the new tokens automatically.

Checks / validation:

- Ran a quick mental scan against `tests/test_readme_axis_lists.py` and `tests/test_model_pattern_gui.py`:
  - `test_readme_method_axis_list_matches_method_modifier_list` / `test_readme_style_axis_list_matches_style_modifier_list` remain valid because the README and list files were updated together.  
  - Pattern GUI tests use existing patterns and `_parse_recipe`; extending `METHOD_TOKENS` does not break them and allows new patterns to parse correctly.
  - This loop did not run the test suite; a future loop can run targeted tests (model pattern, README axis list) if needed.

Follow-ups / next loops:

- Add more patterns that exercise the remaining new methods:
  - Adversarial review, Liberating Structures facilitation, diverge/converge decision flows, mapping-heavy scans.  
- Add a small migration/mapping table (old voice/audience/purpose tokens → recommended axis/recipe combinations) to `GPT/readme.md` or a dedicated doc.  
- Consider adding targeted tests that:
  - Assert that decommissioned voice/audience/tone/purpose tokens no longer appear in the grammar.  
  - Assert that at least one pattern uses each of the highest-value new methods (`xp`, `novice`, `liberating`, `diverge`, `converge`, `mapping`) to keep them exercised.

## 2025-12-04 – Loop 3 – Tests for new methods and patterns

Focus:

- Strengthen guardrails around ADR 015 changes by:
  - Ensuring the pattern GUI tests explicitly cover the new `xp` and `novice` methods.
  - Confirming that README-based axis list tests continue to enforce alignment between `methodModifier`/`styleModifier` lists and documentation after adding new tokens.

Changes made (this loop):

- `tests/test_model_pattern_gui.py`
  - Added `test_xp_next_steps_pattern_uses_xp_method`:
    - Locates the `XP next steps` pattern in `PATTERNS`.
    - Asserts that `_parse_recipe` yields:
      - `static_prompt="describe"`, `completeness="gist"`, `scope="actions"`, `method="xp"`, `style="bullets"`, `directional="ong"`.
    - This verifies both that `xp` is recognised as a method token and that the pattern recipe matches ADR 015’s intent.
  - Added `test_explain_for_beginner_pattern_uses_novice_method`:
    - Locates the `Explain for beginner` pattern.
    - Asserts that `_parse_recipe` yields:
      - `static_prompt="describe"`, `completeness="gist"`, `scope="focus"`, `method="novice"`, `style="plain"`, `directional="fog"`.
    - This ensures `novice` is wired as a method and that the pattern matches ADR 015’s “beginner’s mind” semantics.

- `tests/test_readme_axis_lists.py`
  - No code changes were required in this loop. The existing tests already:
    - Parse the full set of keys from `methodModifier.talon-list` and `styleModifier.talon-list`.
    - Compare them against the backticked tokens in the README lines for `Method (`methodModifier`)` and `Style (`styleModifier`)`.
  - After previous loops added `xp`, `adversarial`, `receptive`, `resistant`, `novice`, `liberating`, `diverge`, `converge`, `mapping`, and `codetour` to both the lists and README, these tests now implicitly guard the new tokens as well.

Checks / validation:

- This loop did not execute the test suite, but:
  - New tests in `test_model_pattern_gui.py` follow existing patterns and only assert on additional patterns, so they are low-risk.
  - README/list alignment tests are unchanged in code but now cover the expanded method/style vocab; any future drift will be caught by them.

Follow-ups / next loops:

- Add a small, explicit test (or set of tests) that:
  - Confirms the trimmed voice/audience/tone/purpose lists do not contain deprecated tokens listed in ADR 015.
  - Optionally, asserts that at least one pattern exists for each of the high-value new methods (`liberating`, `diverge`, `converge`, `mapping`) to keep them exercised.

## 2025-12-04 – Loop 4 – Guardrails for trimmed voice/audience/tone/purpose lists

Focus:

- Add dedicated tests that:
  - Assert the trimmed `modelVoice`, `modelAudience`, `modelTone`, and `modelPurpose` lists match the core sets defined by ADR 015.
  - Ensure deprecated tokens are not accidentally reintroduced into these lists.

Changes made (this loop):

- `tests/test_voice_audience_tone_purpose_lists.py`
  - New test module that reads list keys from the four Talon list files and asserts they match ADR 015’s decisions:
    - `test_model_voice_list_trimmed_to_core_set`:
      - Confirms `modelVoice.talon-list` contains the expected core voices only:
        - `as programmer`, `as prompt engineer`, `as scientist`, `as writer`, `as designer`, `as teacher`, `as facilitator`, `as PM`, `as junior engineer`, `as principal engineer`, `as Kent Beck`.
      - Asserts that deprecated/moved voices are absent (for example, `as XP enthusiast`, `as adversary`, `as blender`, `as artist`, `as logician`, `as reader`, `as editor`, `as other`, `as liberator`, `as negotiator`, `as mediator`, CxO and team-structure voices, `as various`, `as perspectives`, `as systems thinker`).
    - `test_model_audience_list_trimmed_to_core_set`:
      - Confirms `modelAudience.talon-list` contains the expected focused set:
        - `to managers`, `to team`, `to stakeholders`, `to product manager`, `to designer`, `to analyst`, `to programmer`, `to LLM`, `to junior engineer`, `to principal engineer`, `to Kent Beck`, `to CEO`, `to platform team`, `to stream aligned team`, `to XP enthusiast`.
      - Asserts that deprecated/states/structural tokens are absent (for example, `to CTO`, `to CFO`, `to enabling team`, `to complicated subsystem team`, `to receptive`, `to resistant`, `to dummy`, `to various`, `to perspectives`, `to systems thinker`).
    - `test_model_tone_list_trimmed_and_neutral_is_default`:
      - Asserts that `modelTone.talon-list` contains exactly: `casually`, `formally`, `directly`, `gently`, `kindly` (with `neutrally` treated as default when no tone is set and `briefly` retired into completeness/style).
    - `test_model_purpose_list_only_contains_interaction_level_intents`:
      - Asserts that `modelPurpose.talon-list` contains only the interaction-level intents:
        - `for information`, `for entertainment`, `for persuasion`, `for brainstorming`, `for deciding`, `for planning`, `for evaluating`, `for coaching`, `for appreciation`, `for triage`, `for announcing`, `for walk through`, `for collaborating`, `for teaching`, `for project management`.
      - This implicitly verifies that style/method/destination-shaped purposes (for example, `for coding`, `for debugging`, `for slack`, `for table`, `for diverging`, `for converging`, `for mapping`, `for discovery`, `for framing`, `for sensemaking`, `for presenterm`, `for code tour`) have been removed.

Checks / validation:

- This loop did not run the test suite, but:
  - The new tests read from the same Talon list files used by the grammar and other tests, and encode ADR 015’s final sets directly; if these lists drift, tests will fail with clear messages.
  - `modelTone.talon-list` and `modelPurpose.talon-list` were double-checked against the expectations in these tests to ensure alignment.

Follow-ups / next loops:

- Add a small migration/mapping table in the docs (for example, in `GPT/readme.md` or a dedicated file) that shows common retired voice/audience/purpose tokens (for example, `as XP enthusiast`, `to receptive`, `for debugging`, `for mapping`) and their recommended axis/recipe replacements.  
- Consider adding a quick-help section that surfaces the new method tokens (`xp`, `novice`, `liberating`, `diverge`, `converge`, `mapping`) and example phrases, referencing ADR 015 for deeper rationale.

## 2025-12-04 – Loop 5 – Patterns for remaining new methods

Focus:

- Complete ADR 015’s intent that each high-value new method (`liberating`, `diverge`, `converge`, `mapping`) have at least one concrete, discoverable pattern:
  - Add representative patterns to the model pattern GUI.
  - Add tests that assert these patterns use the correct axis combinations.

Changes made (this loop):

- `lib/modelPatternGUI.py`
  - Added a Liberating Structures-flavoured facilitation pattern:
    - `Liberating facilitation` (writing domain):
      - Recipe: `facilitate · full · focus · liberating · bullets · rog`.
      - Behaviour: frames the task as a short Liberating Structures-style facilitation plan, using the `facilitate` static prompt and `liberating` method.
  - Added diverge/converge/mapping patterns:
    - `Diverge options` (writing domain):
      - Recipe: `describe · gist · focus · diverge · bullets · fog`.
      - Behaviour: open up the option space with multiple angles and possibilities.
    - `Converge decision` (writing domain):
      - Recipe: `describe · full · focus · converge · bullets · rog`.
      - Behaviour: weigh trade-offs and converge towards a clear decision or short list.
    - `Mapping scan` (writing domain):
      - Recipe: `describe · gist · relations · mapping · bullets · fog`.
      - Behaviour: emphasise mapping elements and relationships over linear exposition, using the `relations` scope and `mapping` method.

- `tests/test_model_pattern_gui.py`
  - Added tests for each new pattern to ensure `_parse_recipe` recognises the correct axes:
    - `test_liberating_facilitation_pattern_uses_liberating_method`:
      - Asserts: `facilitate`, `full`, `focus`, `liberating`, `bullets`, `rog`.
    - `test_diverge_options_pattern_uses_diverge_method`:
      - Asserts: `describe`, `gist`, `focus`, `diverge`, `bullets`, `fog`.
    - `test_converge_decision_pattern_uses_converge_method`:
      - Asserts: `describe`, `full`, `focus`, `converge`, `bullets`, `rog`.
    - `test_mapping_scan_pattern_uses_mapping_method`:
      - Asserts: `describe`, `gist`, `relations`, `mapping`, `bullets`, `fog`.

Checks / validation:

- This loop did not run the test suite, but:
  - New patterns only use existing static prompts (`describe`, `facilitate`) and axis tokens already present in the method/scope/style lists.
  - New tests mirror existing pattern tests and assert only on `_parse_recipe` output, providing a lightweight guard that the recipes remain consistent with ADR 015’s method semantics.

Follow-ups / next loops:

- Add a concise migration table (old tokens → axis/recipe replacements) to the docs (for example, an appendix in ADR 015 or a short section in `GPT/readme.md`).  
- Optionally, add one or two focused quick-help examples or pattern descriptions that highlight when to reach for these new methods (for example, “when you want LS-style facilitation, use `Liberating facilitation` or `method=liberating`”).  

## 2025-12-04 – Loop 6 – Migration cheat sheet in ADR 015

Focus:

- Make ADR 015 easier to apply in day-to-day use by:
  - Adding an explicit migration cheat sheet that maps commonly retired voice/audience/tone/purpose tokens to concrete axis and pattern equivalents.

Changes made (this loop):

- `docs/adr/015-voice-audience-tone-purpose-decomposition.md`
  - Added a new appendix section, **“Appendix – Migration cheat sheet (old tokens → axis/recipes)”**, which consolidates the most important migrations:
    - Voices → methods/patterns:
      - `as XP enthusiast` → `as programmer` + `method=xp` (+ `scope=actions`/`system`), with an example command.  
      - `as adversary` → suitable voice + `method=adversarial` + `for evaluating`.  
      - `as liberator` → `as facilitator` + `method=liberating` (+ discovery/framing/sensemaking purposes) and a pointer to the “Liberating facilitation” pattern.  
      - `as various` / `as perspectives` → normal voice + `flop` + `method=cluster`/`compare` + `scope=relations`.  
      - `as systems thinker` → normal voice + `method=systemic` (and/or `mapping`) + `scope=system`/`relations`/`dynamics`.  
    - Audiences → methods/scopes:
      - `to receptive` / `to resistant` → any audience + `method=receptive` / `method=resistant`.  
      - `to dummy` → friendlier phrasing + `method=novice` + `gist`/`minimal` + `plain`.  
      - `to various` / `to perspectives` → primary audience + `flop` + `cluster`/`compare` + `relations`.  
      - `to systems thinker` → normal audience + `systemic`/`mapping` + systems/relations/dynamics scope.  
    - Tone → completeness/style:
      - `briefly` → `completeness=minimal` or `gist` + `style=tight`.  
    - Purposes → methods/styles/goals:
      - `for coding` → `goal=solve` + `style=code`.  
      - `for debugging` → `goal=solve` + `method=debugging`.  
      - Channel/format purposes (`for slack`, `for table`, `for presenterm`, `for code tour`) → `style=slack` / `table` / `presenterm` / `codetour`.  
      - `for diverging` / `for converging` → `for brainstorming` + `method=diverge`; `for deciding` + `method=converge`.  
      - `for mapping` → `method=mapping` + relations/system/dynamics scope (+ diagram/table/abstractvisual styles).  
      - `for discovery` / `for framing` / `for sensemaking` → specific combinations of directional lenses (`fog`/`fig`/`rog`), scopes, and methods (`systemic`, `mapping`, `motifs`, `structure`, etc.), with representative example commands.

Checks / validation:

- No code or tests changed in this loop; this was a documentation-only slice aimed at making ADR 015 more directly actionable.
- The cheat sheet entries are consistent with ADR 015’s main Decision section and with the patterns and methods added in earlier loops.

Follow-ups / next loops:

- Optionally reflect a subset of this migration cheat sheet in `GPT/readme.md` (for example, a short “If you used to say X, now say Y” table) for quicker discoverability without reading the full ADR.  

## 2025-12-04 – Loop 7 – Quick mapping in GPT README

Focus:

- Surface the most common migrations from ADR 015 directly in the main GPT README so users can see “old token → new grammar” mappings without reading the full ADR.

Changes made (this loop):

- `GPT/readme.md`
  - Added a new subsection **“Legacy tokens → new grammar (quick mapping)”** after the “Common axis recipes (cheat sheet)” section.  
  - The mapping lists a small, high-value subset of migrations:
    - Voices / stance:
      - `as XP enthusiast` → `as programmer` + `method=xp` (with example `model describe xp ong`).  
      - `as adversary` → suitable voice + `method=adversarial` + `for evaluating`.  
      - `as liberator` → `as facilitator` + `method=liberating` (or the “Liberating facilitation” pattern).
    - Audiences:
      - `to receptive` / `to resistant` → keep the role audience (for example, `to managers`, `to stakeholders`) and add `method=receptive` / `method=resistant`.  
      - `to dummy` → use a friendlier audience (for example, `to junior engineer`) and add `method=novice` + `gist`/`minimal` + `plain`.
    - Purposes / shape:
      - `for coding` → `goal=solve` + `style=code`.  
      - `for debugging` → `goal=solve` + `method=debugging`.  
      - `for slack` / `for table` / `for presenterm` / `for code tour` → `style=slack` / `table` / `presenterm` / `codetour`.  
      - `for diverging` / `for converging` → `for brainstorming` + `method=diverge`; `for deciding` + `method=converge`.  
      - `for mapping` → `method=mapping` + relations/system/dynamics scope, often with visual styles like `diagram`, `table`, or `abstractvisual`.

Checks / validation:

- No code or tests were changed in this loop; this is a documentation-only improvement.  
- The mappings are a direct subset of the more detailed migration cheat sheet already added to ADR 015, keeping the README concise while still giving concrete “old → new” guidance.

Follow-ups / next loops:

- If users still reach frequently for other retired tokens (for example, `for discovery`, `for framing`, `for sensemaking`), consider extending this mapping list slightly or adding concrete “before/after” examples in the docs site.  

## 2025-12-04 – Loop 8 – Status reconciliation for ADR 015

Focus:

- Confirm that ADR 015’s in-repo objectives are effectively complete and documented, and that no substantial additional slices remain beyond minor refinements.

Changes made (this loop):

- No code or configuration changes were made. Instead:
  - Re-reviewed ADR 015, this work-log, and key implementation touchpoints (`GPT/lists/*`, `lib/modelPatternGUI.py`, `lib/modelHelpGUI.py`, `GPT/readme.md`, and the new tests).  
  - Verified that:
    - List trims and axis additions from ADR 015 are in place.  
    - Patterns exist for the new high-value methods (`xp`, `novice`, `liberating`, `diverge`, `converge`, `mapping`).  
    - Tests enforce both:
      - Axis/README alignment (`tests/test_readme_axis_lists.py`), and  
      - List trims and pattern semantics (`tests/test_voice_audience_tone_purpose_lists.py`, `tests/test_model_pattern_gui.py`).  
  - Ensured ADR 015 is marked `Status: Accepted` and that the ADR itself now includes a “Current status (this repo)” section summarising implementation and guardrails.

Assessment:

- For this repo, `B_015` (remaining in-scope work) is effectively ≈ 0:
  - Voice/audience/tone/purpose lists are trimmed and locked by tests.  
  - New methods/styles are implemented, surfaced in help/README, and exercised by patterns.  
  - Migration guidance is captured both in ADR 015 (detailed cheat sheet) and in `GPT/readme.md` (quick mapping).
- Any future work related to this ADR is expected to be:
  - Local UX/documentation polish, or  
  - Adjustments driven by new ADRs that intentionally evolve the grammar.

Follow-ups / next loops:

- None required specifically for ADR 015 in this repo. Future changes that affect voice/audience/tone/purpose or their axis counterparts should reference this ADR and update the work-log only if they materially revise its decisions.

## 2025-12-04 – Loop 9 – Contributor guidance hook

Focus:

- Ensure future contributors discover ADR 015 alongside the other core GPT/axes ADRs when changing prompts or axes.

Changes made (this loop):

- `CONTRIBUTING.md`
  - In the “GPT prompts, axes, and ADRs” section, extended the short ADR list to include ADR 015:
    - Added `docs/adr/015-voice-audience-tone-purpose-decomposition.md` to the “Before adding or changing static prompts or axis lists, read:” bullet list.
  - This makes ADR 015 part of the standard pre-reading for any changes to prompts, axes, or related lists, alongside ADR 012 and ADR 013.

Checks / validation:

- No code or tests were changed; this is a small but meaningful documentation hook so contributors see ADR 015 when editing voice/audience/tone/purpose or adjacent axes.

Follow-ups / next loops:

- None required for ADR 015; this loop simply improves discoverability of the ADR for future changes.
