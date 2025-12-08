# 028 – Help Hub and Discoverability – Work Log

## 2025-12-08 – Slice: Help Hub shell (canvas + command)

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Introduce a minimal Help Hub surface and command that routes to existing help/pattern/suggestions/history/HTML docs actions, closing overlapping overlays per the ADR; keep execution non-disruptive and add a cheat-sheet copy action.

### Summary of this loop

- Added a new Help Hub canvas module (`lib/helpHub.py`) with open/close/toggle actions:
  - Provides buttons for Quick help, Patterns, Prompt pattern menu (using the last static prompt when available), Suggestions, History drawer, HTML docs, Copy cheat sheet, and Close.
  - Opens via `model help hub` (`GPT/help-hub.talon`) and closes overlapping overlays (quick help/pattern/prompt-pattern/suggestions) on open.
  - Includes an Escape-to-close/key handler, mouse click handling for buttons, and a small fallback cheat-sheet copier.
- Added a work log for ADR 028 noting this slice.

### Behaviour impact

- New command `model help hub` opens a simple canvas with navigation buttons to existing help/pattern/suggestion/history/docs surfaces and a cheat-sheet copy action. No model execution occurs from the hub.
- Opening the hub closes other overlay canvases to avoid stacking; hub can be closed via the UI or `model help hub` again.

### Follow-ups and remaining work

- Add search/filter UI, ADR links, voice-trigger hints, normalization notes, onboarding overlay, and a richer cheat sheet as specified in ADR 028.
- Wire minimal cross-link buttons into quick help/confirmation per ADR 028 (Help Hub, Suggestions, History).
- Integrate hub surface with the request/UI controller (ADR 027) for modal coordination and add tests covering hub navigation/handlers.

## 2025-12-08 – Slice: Confirmation cross-link to Help Hub

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Add a discoverability hook from the confirmation GUI to the Help Hub, per ADR 028 cross-link guidance.

### Summary of this loop

- Added “Open Help Hub” and “History” buttons to the confirmation GUI advanced actions, calling `help_hub_open` and `request_history_drawer_toggle`.
- Added a test to assert the Help Hub button triggers the action.

### Behaviour impact

- When the advanced panel is expanded in the confirmation GUI, users can jump directly to the Help Hub or open the request history drawer.

### Follow-ups

- Continue wiring cross-links from quick help/pattern surfaces to Help Hub; add search/filter and hints per ADR 028; integrate modal coordination with the request UI controller.

## 2025-12-08 – Slice: ADR links + richer cheat sheet in Help Hub

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Add the ADR links “Learn why” copy action and enrich the cheat sheet, advancing ADR 028’s content requirements.

### Summary of this loop

- Expanded Help Hub content in `lib/helpHub.py`:
  - Enriched the cheat sheet with core commands and axis token examples.
  - Added an “ADR links” button that copies key ADR paths to the clipboard with a notification.
- Added a test (`_tests/test_help_hub.py`) to assert ADR links are copied.

### Behaviour impact

- Help Hub now offers a richer cheat sheet and a one-click way to copy ADR references, improving in-Talon discoverability.

### Follow-ups

- Still need search/filter, voice-hint/normalization notes, onboarding overlay, additional cross-links from quick help/patterns, and controller integration per ADR 028.

## 2025-12-08 – Slice: Help Hub search/filter skeleton and ADR links action

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Add a basic filterable search in Help Hub and a “Learn why” ADR links copy action, per ADR 028.

### Summary of this loop

- Added Help Hub filter state with key-capture (characters/backspace/Escape) and a voice command `model help filter <phrase>`.
- Built a simple search index from hub buttons, static prompts (list file), axis tokens, patterns, and prompt presets; matches (label contains query) render in the hub and are clickable.
- Added a helper to copy ADR links and included an “ADR links” button; expanded the cheat sheet with core commands and axis examples.
- Tests cover search-triggered quick help and ADR link copying.

### Behaviour impact

- Users can set a filter (voice or typing while hub is focused) to find entries (quick help, prompts, axes, patterns, presets) and click to open the relevant surface; still non-executing for model runs.
- ADR links copy to clipboard from the hub.

### Follow-ups

- Improve search grouping/labels and axis-focused quick help opens; add voice-hint/normalization notes, onboarding overlay, additional cross-links, and controller integration as specified in ADR 028.

## 2025-12-08 – Slice: Grouped buttons and cheat-sheet hints

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Polish Help Hub layout and hints to make navigation clearer.

### Summary of this loop

- Grouped Hub buttons into Navigation vs Docs & Copy sections and added cheat-sheet hints about confirmation entry (`More actions… → Open Help Hub`) and the filter voice command.

### Behaviour impact

- Hub layout is more scannable; cheat sheet calls out how to reach Hub from confirmation and how to filter by voice.

### Follow-ups

- Still pending: voice-hint/normalization notes in Hub, onboarding overlay, quick help/pattern cross-links, and controller integration.

## 2025-12-08 – Slice: Normalisation/voice hints in Help Hub

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Surface caps/voice hints inside Help Hub per ADR 028 (normalization visibility, hidden voice triggers).

### Summary of this loop

- Added static info lines in Help Hub for axis caps (scope≤2, method≤3, style≤3, directional required) and voice hints (`model patterns`, `model quick help`, `model suggest`, `history drawer`, `model help hub`/`model help filter …`).
- No behaviour change to actions; purely UI guidance in the Hub.

### Behaviour impact

- Hub now surfaces normalization caps and key voice entrypoints inline, improving discoverability without extra commands.

### Follow-ups

- Remaining: onboarding overlay, controller integration, additional cross-links, and optional dynamic voice-hint/normalization diagnostics.

## 2025-12-08 – Slice: Onboarding overlay command

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Add the onboarding entrypoint and inline tips to the Help Hub.

### Summary of this loop

- Added `help_hub_onboarding` action + `model onboarding` command to open Help Hub with an onboarding overlay (three starter steps: run a pattern, open quick help, try `model again gist fog`).
- Overlay renders inside the Hub; state clears on close.
- Added a test to assert onboarding flag/state.

### Behaviour impact

- Users can say `model onboarding` to open Help Hub with guided starter steps.

### Follow-ups

- Still need controller integration, more cross-links from quick help/pattern surfaces, and any dynamic diagnostics per ADR 028.

## 2025-12-08 – Slice: Close Help Hub on model runs

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Align hub modal coordination with model runs to avoid overlay collisions.

### Summary of this loop

- `gpt_apply_prompt` now closes the Help Hub (best-effort) alongside other overlays before running a model prompt, keeping only one surface visible.

### Behaviour impact

- Running a model command auto-closes the Hub if it’s open, preventing stacked overlays during requests.

### Follow-ups

- Still to do: deeper controller integration, cross-links from quick help/pattern surfaces, and dynamic diagnostics per ADR 028.

## 2025-12-08 – Slice: Pattern GUIs voice cross-link to Help Hub

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Add a cross-link from pattern/prompt-pattern GUIs to the Help Hub via voice triggers, per ADR 028.

### Summary of this loop

- Added `help hub` voice triggers to `gpt-patterns-gui.talon` and `gpt-prompt-patterns-gui.talon`, opening the Help Hub from either GUI while they are active.

### Behaviour impact

- When a pattern or prompt-pattern window is open, saying “help hub” opens the Hub, improving discoverability without extra clicks.

### Follow-ups

- Remaining: controller integration and any additional cross-links/diagnostics per ADR 028.

## 2025-12-08 – Slice: Quick help voice cross-link to Help Hub

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Add a quick-help entrypoint to open the Help Hub by voice.

### Summary of this loop

- Added `{user.model} quick help hub` Talon command to open the Help Hub directly from the quick-help grammar.

### Behaviour impact

- Users can now say “model quick help hub” to jump from grammar help to the Help Hub.

### Follow-ups

- Controller integration and any remaining diagnostics are still outstanding per ADR 028.

## 2025-12-08 – Slice: Controller closes Help Hub on requests

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Integrate the request UI controller so Help Hub closes when requests start (per ADR 028/027 modal guidance).

### Summary of this loop

- Extended `RequestUIController` with an optional `hide_help_hub` callback and invoked it whenever leaving idle; added a test to assert it fires.
- `gpt_apply_prompt` already best-effort closes Hub; this controller hook keeps it consistent across request events.

### Behaviour impact

- Any request state transition out of idle now triggers the hub-close callback (when wired), preventing overlay clashes managed by the controller.

### Follow-ups

- If desired, wire the controller’s `hide_help_hub` to `help_hub_close` in the runtime wiring; remaining diagnostics/cross-links still pending per ADR 028.

## 2025-12-08 – Slice: Wire controller to close Help Hub

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Connect the controller’s `hide_help_hub` hook to the runtime wiring so requests consistently close the Hub.

### Summary of this loop

- Updated default request UI wiring (`lib/requestUI.py`) to pass `hide_help_hub` (calls `help_hub_close`) into `RequestUIController`, so controller-driven state changes close the Hub.
- Full test suite passes.

### Behaviour impact

- Whenever the request controller transitions out of idle, Help Hub is closed via the wired callback, matching ADR 027 modal coordination.

### Follow-ups

- Remaining diagnostics/cross-links per ADR 028; otherwise Hub/runtime coordination is in place.

## 2025-12-08 – Slice: Suggestions GUI voice cross-link to Help Hub

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Add a Help Hub entrypoint from the suggestions GUI.

### Summary of this loop

- Added a `help hub` voice trigger to `gpt-suggestions-gui.talon` so users can open Help Hub while the suggestions window is active.

### Behaviour impact

- Suggestions picker now offers an in-context voice path to Help Hub, reducing recall friction.

### Follow-ups

- Remaining diagnostics/cross-links per ADR 028.

## 2025-12-08 – Slice: Pattern GUI close hotspot opens Help Hub

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Provide another cross-link path to Help Hub from pattern UIs.

### Summary of this loop

- Updated pattern and prompt-pattern canvases so clicking their close hotspot also opens Help Hub (best-effort), offering an in-surface path to broader help.

### Behaviour impact

- When closing a pattern/prompt-pattern window via the header close hotspot, Help Hub opens, improving discoverability without requiring a separate command.

### Follow-ups

- Remaining diagnostics/cross-links per ADR 028.

## 2025-12-08 – Slice: Quick help voice cross-links to patterns/suggestions/docs

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Provide quick-help voice routes to other help surfaces (patterns, suggestions, HTML docs).

### Summary of this loop

- Added `model quick help patterns`, `model quick help suggestions`, and `model quick help docs` commands to open the pattern picker, suggestion GUI, and HTML help from the quick-help grammar.

### Behaviour impact

- From quick help, users can jump to patterns, suggestions, or full docs via voice without recalling separate commands.

### Follow-ups

- Remaining diagnostics/cross-links per ADR 028; current cross-links cover Hub, patterns, prompt patterns, suggestions, and docs.

## 2025-12-08 – Slice: Help Hub search grouping/labels

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Make search results clearer by labelling hub, prompt, axis, pattern, and preset entries.

### Summary of this loop

- Prefixed search entries by type (Hub, Prompt, Axis, Pattern, Preset) to disambiguate results.
- Kept non-executing behaviour; search remains click-to-open relevant surfaces.

### Behaviour impact

- Filtered results now show their type in the label, improving scanability and reducing accidental clicks.

### Follow-ups

- Remaining diagnostics/cross-links per ADR 028; search grouping is minimal but clearer.

## 2025-12-08 – Slice: Fallback and status

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Add a minimal fallback when the Hub cannot open and mark ADR status updated.

### Summary of this loop

- Help Hub now best-effort copies the cheat sheet and notifies when the canvas cannot open, providing a fallback instead of silently failing.
- ADR 028 status set to Accepted; core features implemented across Hub, cross-links, search/filter, hints, onboarding, controller wiring, and fallbacks.

### Behaviour impact

- If Hub fails to open (canvas unavailable), users get a notification and copied cheat sheet for quick reference.

### Follow-ups

- None beyond incremental polish; ADR considered implemented for this repo.

## Current status (2025-12-08)

- Help Hub implemented with search/filter, cross-links (quick help, patterns, prompt patterns, suggestions, history, docs), normalization/voice hints, ADR links, onboarding overlay, controller-driven closure, and fallback cheat-sheet copy when the canvas cannot open.
- Voice entrypoints in quick help/pattern/prompt-pattern/suggestions GUIs, confirmation advanced actions, and the base command (`model help hub`) are wired.
- Controller wiring closes Hub on request start; model runs also close Hub before execution.
- No remaining in-repo tasks for ADR 028; further changes would be optional polish.

## 2025-12-09 – Status confirmation

- Reviewed ADR 028 scope against current code and work log. All scoped features are present; no new in-repo tasks identified. Treat future tweaks as optional polish outside ADR scope.

## 2025-12-09 – Slice: Quick help cross-link to history

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Add a quick-help voice path to request history, rounding out cross-links.

### Summary of this loop

- Added `model quick help history` to open the request history drawer from the quick-help grammar (`GPT/gpt-help-gui.talon`).

### Behaviour impact

- Users can jump from quick help to request history via voice without recalling separate commands.

### Follow-ups

- ADR remains Accepted; this is incremental polish.

## 2025-12-09 – Slice: README help surfacing

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Surface the consolidated help entrypoints in the README to reinforce discoverability.

### Summary of this loop

- Added an “In-Talon help surfaces” section to `readme.md` listing `model help hub`, quick help variants, patterns, suggestions, and history commands.

### Behaviour impact

- New users see a concise help directory in the README pointing to the Hub and related surfaces.

### Follow-ups

- ADR remains Accepted; further changes would be optional polish.

## 2025-12-09 – Slice: Last recipe recap in Help Hub

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Surface the last recipe in Help Hub to aid recall.

### Summary of this loop

- Help Hub now shows the last recipe (and directional lens if available) inline, so users can see what they last ran without opening other surfaces.

### Behaviour impact

- Hub provides a quick recap of the last model recipe, improving recall without extra commands.

### Follow-ups

- ADR remains Accepted; further changes would be optional polish.

## 2025-12-09 – Slice: Help Hub render fix (opacity/indent)

**ADR focus**: 028 – Help hub and discoverability consolidation  
**Loop goal**: Fix Talon runtime load/render issues and make the Hub background fully opaque.

### Summary of this loop

- Corrected indentation in `helpHub.py` draw block (fixing Talon import errors) and set the Hub background to fully opaque dark gray to avoid translucent overlays.

### Behaviour impact

- Hub should now load on Talon without syntax errors and render with an opaque background instead of translucent red.

### Follow-ups

- If translucency persists on some runtimes, consider adding an explicit backdrop/shadow; otherwise ADR remains Accepted.
