# 2025-12-14 – Loop 1 (kind: behaviour)
- Focus: ADR 051 – enforce “Why-only” intent axis and re-home how/what tokens into method/static prompt axes.
- Changes:
  - Removed non-Why purpose tokens from intent SSOT and Talon list (`lib/personaConfig.py`, `GPT/lists/modelPurpose.talon-list`); dropped the `collaborate` intent preset/bucket entry to keep presets aligned with the trimmed purpose axis.
  - Added method-axis homes for process/interaction tokens (`walkthrough`, `cocreate`, `facilitate`, `probe`) in `GPT/lists/methodModifier.talon-list` with descriptions in `lib/axisConfig.py`; updated README method token list (`GPT/readme.md`).
  - Added static prompt homes for deliverable-shaped tokens (`jobs`, `value`, `pain`, `done`, `team`) in `GPT/lists/staticPrompt.talon-list` with axis profiles in `lib/staticPromptConfig.py`.
  - Added a guardrail to block reintroduction of how/artifact tokens on the purpose axis (`_tests/test_axis_family_token_guardrails.py`) and updated purpose/preset expectation tests (`_tests/test_voice_audience_tone_purpose_lists.py`, `_tests/test_persona_presets.py`); adjusted help fallback text to the new preset set (`lib/helpHub.py`).
- Tests: `python3 -m pytest` (all passing after README sync), `python3 -m pytest _tests/test_readme_axis_lists.py`.
- Removal test: Reverting would restore how/what tokens onto the intent axis, drop method/static prompt homes and guardrails, and re-break README/test alignment for the method axis.
