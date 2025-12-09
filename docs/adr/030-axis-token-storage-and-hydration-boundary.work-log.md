# 030 – Axis token storage and hydration boundary – Work Log

## 2025-12-09 – Slice: token-first axis state with hydrated system prompt

**ADR focus**: 030 – Axis token storage and hydration boundary  
**Loop goal**: Store completeness/scope/method/style as canonical tokens only, hydrating to long descriptions solely when building the model-facing system prompt.

### Summary of this loop

- Added `lib/axisMappings.py` to centralise axis list parsing, value→key and key→value maps, and hydration helpers while keeping defaults token-based.
- Normalised `modelPrompt` axis resolution to tokens (spoken > profile > defaults), stored tokens in `GPTState.system_prompt`/`last_*`, and dropped dependence on reverse-mapping heuristics for UI recap.
- Updated `GPTSystemPrompt.format_as_array()` to hydrate tokens to full axis descriptions for the system prompt, with defaults now read as tokens even when settings contain hydrated text.

### Behaviour impact

- Axis state and recaps stay concise, deterministic tokens; the system prompt continues to send full instruction text to the model via a single hydration boundary.
- Default axis settings persist as tokens, so changes to Talon list descriptions no longer leak hydrated strings into stored state.

### Follow-ups

- Hydrated constraints recap

**ADR focus**: 030 – Axis token storage and hydration boundary  
**Loop goal**: Keep user-facing constraint lines readable by hydrating axis tokens while leaving stored state token-only.

### Summary of this loop

- Hydrate constraint lines in `modelPrompt` using axis list descriptions while preserving token storage in `GPTState` for recap/rerun.
- Added `axis_hydrate_tokens` plumbing and a test covering hydrated constraint output.

### Behaviour impact

- Confirmation/constraint text shows human-friendly descriptions again even though state remains tokenised.

### Follow-ups

- Consider hydrating other UI recaps (for example, suggestion picker) if needed.

## 2025-12-09 – Status snapshot

- State, recap/rerun, and system prompt now follow the token-first + boundary hydration design across code/tests/docs.
- Remaining follow-ups are optional UX polish (e.g., hydrating suggestion picker); no known in-repo blockers for ADR 030.

## 2025-12-09 – Slice: hydrate suggestion picker axes

**ADR focus**: 030 – Axis token storage and hydration boundary  
**Loop goal**: Keep suggestion UI user-friendly by hydrating axis tokens when listing recipes while leaving stored state token-only.

### Summary of this loop

- `modelSuggestionGUI` now hydrates axis tokens for each suggested recipe row (Details: C/S/M/St/D) so users see descriptive text without changing stored token recipes.

### Behaviour impact

- Suggestion picker remains token-backed for execution but shows readable axis descriptions, aligning with the boundary hydration model.

### Follow-ups

- None pending for ADR 030; future UX hydration can follow the same pattern if new surfaces appear.

## 2025-12-09 – Slice: hydrate response recap axes

**ADR focus**: 030 – Axis token storage and hydration boundary  
**Loop goal**: Improve readability of the response recap while keeping stored state token-only.

### Summary of this loop

- Response canvas now hydrates axis tokens (C/S/M/St) for the recap details line so users see descriptive axis text without changing stored tokens.

### Behaviour impact

- Response recap stays token-backed for grammar/speakability but surfaces hydrated descriptions for clarity.

### Follow-ups

- None remaining; ADR 030 is fully applied in this repo.

## 2025-12-09 – Status confirmation

- Reviewed ADR 030 surfaces after hydration slices (constraints, suggestions, response recap) and token-only state remains intact.
- README axis lists are in sync; tests were last run with a green suite.
- No further in-repo work remains for ADR 030; future tweaks would be optional UX polish outside the ADR scope.

- Consider hydrating constraint recap text for readability and add coverage for rerun flows that mix spoken, profile, and default axis tokens.
