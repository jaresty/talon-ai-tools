# 2025-12-13 – Loop entry (kind: behaviour)
- Focus: ADR 050 (stance-like static prompts) – establish stance homes before removing static prompts.
- Changes:
  - Added new intent/purpose tokens for JTBD/value/pain/DoD/facilitation/discovery/team mapping in `GPT/lists/modelPurpose.talon-list`.
  - Hydrated the new purpose tokens with descriptions in `lib/personaConfig.py`.
  - Updated purpose list guardrail test to expect the expanded stance set in `_tests/test_voice_audience_tone_purpose_lists.py`.
  - Removed meta/transform static prompts (`LLM`, `shuffled`) from `lib/staticPromptConfig.py` and `GPT/lists/staticPrompt.talon-list` to reduce static prompt scope to task-oriented entries.
- Loop 2 (2025-12-13, kind: behaviour):
  - Removed stance-like static prompts (`value`, `jobs`, `done`, `facilitate`, `pain`, `question`, `team`) from `lib/staticPromptConfig.py` and `GPT/lists/staticPrompt.talon-list`.
  - Kept filter/profile guardrail by redirecting the filter-style modelPrompt test to use `relevant` instead of `pain` in `_tests/test_talon_settings_model_prompt.py`.
  - Guardrail tests run: `python3 -m pytest _tests/test_static_prompt_axis_tokens.py _tests/test_static_prompt_completeness_hints.py _tests/test_talon_settings_model_prompt.py` (pass).
- Tests: `python3 -m pytest _tests/test_voice_audience_tone_purpose_lists.py` (pass).
- Removal test: Reverting would drop new purpose tokens and break the updated guardrail test; stance homes for migrating static prompts would be missing again.
- Follow-ups:
  - Migrate static prompts (jobs/value/pain/team/question/facilitate/done/fix/shuffled/LLM/ticket) off `staticPrompt`, mapping to these stance tokens and structural axes; update dependent tests/patterns.
  - Revisit form/channel tone-like tokens (`announce`, `plain`, `tight`, `headline`) and consider tone/method re-homing.

# 2025-12-13 – Loop 3 (kind: behaviour)
- Focus: ADR 050 – provide tone-axis homes for form-style tone tokens.
- Changes:
  - Added tone tokens (`plainly`, `tightly`, `headline first`) to `GPT/lists/modelTone.talon-list`.
  - Hydrated the new tones in `lib/personaConfig.py`.
  - Updated tone guardrail expectations in `_tests/test_voice_audience_tone_purpose_lists.py`.
- Tests: `python3 -m pytest _tests/test_voice_audience_tone_purpose_lists.py` (pass).
- Removal test: Reverting would drop the new tone tokens and break the guardrail test; stance homes for former form-style tones would be missing.
- Follow-ups:
  - Continue re-homing remaining stance-like entries (e.g., ticket, announce/plain/tight/headline form/channel tokens) and regenerate axisConfig after final moves.

# 2025-12-13 – Loop 4 (kind: behaviour)
- Focus: ADR 050 – remove remaining stance/destination static prompt and align patterns with axes.
- Changes:
  - Removed `ticket` static prompt from `lib/staticPromptConfig.py` and `GPT/lists/staticPrompt.talon-list`; patterns now express Jira ticket via form/channel axes.
  - Updated patterns to avoid removed static prompts and preserve form/channel: Liberating facilitation now uses static prompt `describe`; Jira ticket pattern carries form `story` + channel `jira`; sketch diagram uses form `code` + channel `diagram`; pain/facilitation patterns moved off static prompts.
  - Adjusted suggestion/pattern/action tests to match the new recipes and axis expectations (story/jira, diagram form/channel, liberating static prompt change).
- Tests: `python3 -m pytest _tests/test_model_suggestion_gui.py _tests/test_model_pattern_gui.py _tests/test_gpt_actions.py _tests/test_talon_settings_model_prompt.py` (pass).
- Removal test: Reverting would reintroduce removed static prompts into lists/config and break updated pattern/suggestion guardrails.
- Follow-ups:
  - Remove tone-like form/channel tokens (`plain`, `tight`, `headline`, `announce`) from axisConfig and rehome as tone/method/destination; regenerate `lib/axisConfig.py` and run full drift/pytest.

# 2025-12-13 – Loop 5 (kind: behaviour)
- Focus: ADR 050 – remove channel-style announce and rehome to tone; keep channel axis focused on destinations.
- Changes:
  - Removed `announce` from channel axis/list: `GPT/lists/channelModifier.talon-list`, `lib/axisConfig.py`.
  - Cleaned up references in `lib/helpHub.py`, `lib/talonSettings.py`, and `GPT/readme.md`.
- Tests: `python3 -m pytest _tests/test_voice_audience_tone_purpose_lists.py _tests/test_model_pattern_gui.py::ModelPatternGUITests::test_slack_and_jira_patterns_are_configured` (pass).
- Removal test: Reverting would restore announce into channel list/config and break updated docs/help expectations.
- Follow-ups:
  - Consider moving tone-like form tokens (`plain`, `tight`, `headline`) off the form axis and regenerating `lib/axisConfig.py`; run full drift/pytest after final axis edits.

# 2025-12-13 – Loop 6 (kind: behaviour)
- Focus: ADR 050 – move tone-like form tokens off form axis and keep axis SSOTs clean.
- Changes:
  - Removed `headline`, `plain`, `tight` from form list (`GPT/lists/formModifier.talon-list`) and from the form axis in `lib/axisConfig.py` (tone already lives in persona).
  - Cleaned channel tone references in `GPT/readme.md` to match the tightened channel list.
  - Tests: `python3 -m pytest _tests/test_voice_audience_tone_purpose_lists.py _tests/test_model_pattern_gui.py::ModelPatternGUITests::test_pattern_with_form_token_sets_form_axis _tests/test_model_pattern_gui.py::ModelPatternGUITests::test_slack_and_jira_patterns_are_configured` (pass).
- Removal test: Reverting would reintroduce tone-like tokens into form/channel axes and break updated docs/tests alignment.
- Follow-ups:
  - Regenerate `lib/axisConfig.py` via `scripts/tools/generate_axis_config.py` to keep generated SSOT in sync, then run full drift/pytest.

# 2025-12-13 – Loop 7 (kind: behaviour)
- Focus: ADR 050 – finish moving stance-like hints off contract axes and align helpers/docs.
- Changes:
  - Dropped `plain` form hints from static prompt profiles (ops/context/com b/tune/melody/constraints/effects) and patterns; tightened pattern recipes/tests to treat tone as persona-only.
  - Restored `axis_docs_index`/`axis_key_to_value_map` helpers after regenerating `lib/axisConfig.py`; updated axis docs/readme lists (including `form=visual`) and removed the retired `ticket` static prompt profile.
  - Adjusted history and talon settings filtering to the new axis vocab and made history notifications resilient to stale suppression flags.
- Tests: `python3 -m pytest` (pass).
- Removal test: Reverting would reintroduce form-plain drift into static prompts/patterns, break axis docs/readme alignment, and drop history notification guards.
