# 047 Multi-Provider Selection and Voice Switching Commands – Work Log

## 2025-12-12
- Status update: ADR 047 accepted. Behaviour, docs, and guardrails implemented in this repo.

## 2025-12-12
- Slice (kind: behaviour): establish provider registry + canvas-backed commands for OpenAI/Gemini and thread provider selection into request plumbing.
- Changes:
  - Added `lib/providerRegistry.py` (defaults: openai/gemini with spoken aliases including "gemeni"), settings overrides, and cycling/status helpers.
  - Added `lib/providerStatusLog.py` (formerly `providerCanvas.py`) and `lib/providerCommands.py` to render provider list/status/switch errors via log output and new Talon grammar in `GPT/gpt.talon`.
  - Wired provider-aware defaults through settings (`model_provider_current/default/extra`), request building (`lib/modelHelpers.py` now reads provider model/token/endpoint), and state (`GPTState.current_provider_id`).
  - Updated settings example for provider overrides.
- Validation: `python3 -m pytest _tests/test_provider_registry.py _tests/test_provider_commands.py` (7 passed).
- Removal test: reverting this slice removes provider commands/canvas, loses alias resolution for gemini, and reverts request routing to single OpenAI endpoint only.

## 2025-12-12
- Slice (kind: behaviour): expose provider capabilities in status/list canvas output and keep status entries feature-aware.
- Changes:
  - Added normalized feature flags to `ProviderConfig` and threaded them into status entries; canvas now shows streaming/vision/images readiness.
  - Updated provider command tests to assert capability rows appear in canvas output.
- Validation: `python3 -m pytest _tests/test_provider_registry.py _tests/test_provider_commands.py` (7 passed).
- Removal test: reverting would hide capability indicators in provider list/status and drop the guard that features propagate through registry outputs.

## 2025-12-12
- Slice (kind: guardrail/tests): surface missing API key as a provider canvas error and guard it with tests.
- Changes:
  - `lib/modelHelpers.py` now renders a provider error canvas when a provider key is missing (before raising `MissingAPIKeyError`), keeping feedback in-canvas per ADR 047.
  - Added `_tests/test_provider_error_canvas.py` to assert missing key triggers the canvas with the expected env var hint.
- Validation: `python3 -m pytest _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (8 passed).
- Removal test: reverting would revert to silent MissingAPIKeyError without canvas guidance and drop the guardrail test.

## 2025-12-12
- Slice (kind: behaviour/tests): bind provider selection to the prepared request so mid-run switches use the original provider; add guard.
- Changes:
  - `lib/modelHelpers.py` stores `request_provider` on build, uses bound provider for model selection, endpoint, and token resolution (streaming + sync), and shows canvas errors for missing keys.
  - `lib/modelState.py` tracks/reset `request_provider`.
  - Added `_tests/test_provider_binding.py` to assert that changing provider settings after `build_request` does not change the provider used for the in-flight send.
- Validation: `python3 -m pytest _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (9 passed).
- Removal test: reverting would allow provider switches mid-run, potentially mixing endpoints/keys, and would drop the binding guard test.

## 2025-12-12
- Slice (kind: guardrail/tests): block unsupported capabilities (vision) before send and surface via provider canvas.
- Changes:
  - Added `_ensure_request_supported` and `UnsupportedProviderCapability` in `lib/modelHelpers.py`; vision requests now error early with a canvas hint when the provider lacks `vision` capability.
  - Added `_tests/test_provider_capability_guard.py` to assert image-containing requests are rejected for non-vision providers.
- Validation: `python3 -m pytest _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (10 passed).
- Removal test: reverting would allow non-vision providers to attempt image requests and would remove the guardrail test.

## 2025-12-12
- Slice (kind: behaviour/tests): add reachability hints to provider list/status canvases with optional probes.
- Changes:
  - `lib/providerRegistry.py` now supports endpoint probing (configurable via `user.model_provider_probe`) and surfaces `reachable/reachability_error` in status entries.
  - `lib/providerCommands.py` renders reachability in canvases; settings example updated with probe flag.
  - Added `user.model_provider_probe` setting in `lib/talonSettings.py` and example in `talon-ai-settings.talon.example`.
  - Tests extended (`_tests/test_provider_commands.py`) to assert reachability lines and error handling.
- Validation: `python3 -m pytest _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (11 passed).
- Removal test: reverting would remove reachability hints/probes from provider canvases and drop the probe guard test.

## 2025-12-12
- Slice (kind: behaviour/tests): gate image generation by provider capability and align endpoints with active provider.
- Changes:
  - `Images/ai-images.py` now checks provider `images` feature before sending, shows provider canvas, and raises `UnsupportedProviderCapability`; computes image endpoint from provider chat endpoint.
  - Added importable `Images/ai_images.py` for tests; `_tests/test_provider_images_guard.py` covers endpoint derivation and capability guard.
  - Settings unchanged; uses active provider selection.
- Validation: `python3 -m pytest _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (13 passed).
- Removal test: reverting would allow image requests on providers without image support and drop the guardrail test.

## 2025-12-12
- Slice (kind: docs): surface provider settings/commands in user docs.
- Changes:
  - Documented provider settings (`current/default/extra/probe`) in `GPT/readme.md` config table.
  - Added provider voice commands + probe note to `readme.md`.
- Validation: doc-only; provider test suite re-run: `python3 -m pytest _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (13 passed).
- Removal test: reverting would hide provider settings/commands from docs while behaviour remains.

## 2025-12-12
- Slice (kind: behaviour/tests): add provider canvas close grammar and guard.
- Changes:
  - Added `{user.model} provider close` grammar in `GPT/gpt.talon`.
  - Extended `_tests/test_provider_commands.py` to assert close hides the provider canvas (and reran provider suite).
- Validation: `python3 -m pytest _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (14 passed).
- Removal test: reverting would remove the close grammar and test coverage for closing the provider canvas.

## 2025-12-12
- Slice (kind: behaviour/tests): include streaming toggle in provider status canvas.
- Changes:
  - Provider status now renders `streaming (current): on/off` based on `user.model_streaming`.
  - Updated `_tests/test_provider_commands.py` to assert streaming status appears.
- Validation: `python3 -m pytest _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (14 passed).
- Removal test: reverting would hide streaming state from provider status and drop the guard test.

## 2025-12-12
- Slice (kind: guardrail/tests): verify provider commands accept spoken aliases.
- Changes:
  - Added `_tests/test_provider_commands.py::test_switch_accepts_spoken_alias` to ensure "gemeni" spoken alias resolves to `gemini` via the provider command path.
- Validation: `python3 -m pytest _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (15 passed).
- Removal test: reverting would drop alias coverage for the command path even though registry resolve supports it.

## 2025-12-12
- Slice (kind: behaviour/tests): expose provider controls in Help Hub.
- Changes:
  - Added a “Providers” button to Help Hub (`lib/helpHub.py`) to open the provider list canvas; updated tests to assert it triggers `model_provider_list`.
- Validation: `python3 -m pytest _tests/test_help_hub.py _tests/test_provider_commands.py _tests/test_provider_registry.py _tests/test_provider_error_canvas.py _tests/test_provider_binding.py _tests/test_provider_capability_guard.py _tests/test_provider_images_guard.py` (29 passed).
- Removal test: reverting removes Help Hub discoverability for provider switching and the corresponding test.

## 2025-12-12
- Slice (kind: docs/guardrail): add provider commands to Help Hub cheat sheet.
- Changes:
  - Cheat sheet text (`lib/helpHub.py`) now includes `model provider list/use/status` to surface provider switching in clipboard copy.
- Validation: `python3 -m pytest _tests/test_help_hub.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (15+ tests) — doc change only; suites remain green.
- Removal test: reverting would drop provider commands from cheat sheet while behaviour remains.

## 2025-12-12
- Slice (kind: guardrail/tests): warn when streaming is disabled for the active provider.
- Changes:
  - `lib/modelHelpers.py` now shows a provider canvas warning and falls back to sync when the provider disables streaming.
  - Added `_tests/test_provider_streaming_warning.py` to assert the warning fires and the request still completes.
- Validation: `python3 -m pytest _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (16 passed).
- Removal test: reverting would silently fall back to sync without warning and drop the guardrail test.

## 2025-12-12
- Slice (kind: docs): add provider switching quick reference to GPT README.
- Changes:
  - Added a “Provider switching (ADR 047)” quick reference section in `GPT/readme.md` covering list/use/status/next/previous commands and settings.
- Validation: doc-only; provider test suite re-run: `python3 -m pytest _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (16 passed).
- Removal test: reverting would hide provider quick reference from GPT docs while behaviour remains.

## 2025-12-12
- Slice (kind: docs): clarify provider env vars and quickstart note.
- Changes:
  - `readme.md` notes bundled providers and the `GEMINI_API_KEY` env var.
  - `GPT/readme.md` config table now lists provider env vars (OpenAI/Gemini) as part of configuration.
- Validation: doc-only; provider suites rerun: `python3 -m pytest _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (16 passed).
- Removal test: reverting would hide env-var requirements from docs while behaviour remains unchanged.

## 2025-12-12
- Slice (kind: docs/cleanup): align image module name with provider work.
- Changes:
  - Normalized the image module path to `Images/ai_images.py` (dashless) to match provider-aware imports; tests remain green.
- Validation: `python3 -m pytest _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (16 passed).
- Removal test: reverting would reintroduce the dashed module name and break test imports.

## 2025-12-12
- Slice (kind: guardrail/tests): provider command errors for ambiguous names render in canvas.
- Changes:
  - Added `_tests/test_provider_commands.py::test_ambiguous_provider_shows_error` to ensure ambiguous spoken names surface a canvas error instead of silently picking a provider.
- Validation: `python3 -m pytest _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (17 passed).
- Removal test: reverting would drop the guard against ambiguous provider selection in the command path.

## 2025-12-12
- Slice (kind: docs): hint provider env vars in settings example.
- Changes:
  - `talon-ai-settings.talon.example` now reminds users to set `OPENAI_API_KEY` / `GEMINI_API_KEY` when switching providers.
- Validation: doc-only; provider suites re-run: `python3 -m pytest _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (17 passed).
- Removal test: reverting would drop the env-var reminder from the settings example while behaviour stays the same.

## 2025-12-12
- Slice (kind: guardrail/tests): ensure Help Hub search triggers provider list.
- Changes:
  - Added `_tests/test_help_hub.py::test_help_hub_search_can_trigger_provider_list` to confirm filtered Help Hub clicks still invoke the provider list command.
- Validation: `python3 -m pytest _tests/test_help_hub.py _tests/test_provider_commands.py _tests/test_provider_registry.py _tests/test_provider_streaming_warning.py` (27 passed across invoked suites).
- Removal test: reverting would drop coverage that Help Hub search preserves provider list discoverability.

## 2025-12-12
- Slice (kind: guardrail/tests): log provider id in request history for replay surfaces.
- Changes:
  - `RequestLogEntry` now carries `provider_id`, populated via `append_entry_from_request`; model helpers pass the active provider id when logging requests.
  - Added `_tests/test_request_history.py::test_append_entry_from_request_captures_provider` to guard provider persistence in history entries.
- Validation: `python3 -m pytest _tests/test_request_history.py _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (21 passed).
- Removal test: reverting would drop provider tracking in history and its guardrail test.

## 2025-12-12
- Slice (kind: guardrail/tests): surface provider id in history summaries for drawers.
- Changes:
  - History summaries now append `provider=<id>` when available; added `_tests/test_request_history_actions.py::test_history_summary_lines_include_provider`.
  - `RequestLogEntry` provider_id already captured; summaries now render it for list/drawer surfaces.
- Validation: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history.py _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (36 passed).
- Removal test: reverting would hide provider info in history list/drawer and drop the guardrail test.

## 2025-12-12
- Slice (kind: guardrail/tests): include provider in history drawer rows.
- Changes:
  - `history_drawer_entries_from` appends provider id when present; drawer rows now show `provider=<id>`.
  - Updated `_tests/test_request_history_drawer.py` to assert provider rendering in drawer entries.
- Validation: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history.py _tests/test_request_history_drawer.py _tests/test_history_query.py` (26 passed); provider suites remain green from prior runs.
- Removal test: reverting would drop provider visibility from history drawer entries and remove the guardrail.

## 2025-12-12
- Slice (kind: guardrail/tests): propagate provider id into history recalls.
- Changes:
  - History entry replay now sets `GPTState.current_provider_id` when showing a history entry, keeping recaps aligned with the original provider.
  - Added `_tests/test_request_history_actions.py::test_show_entry_sets_provider` to guard the provider handoff when opening history entries.
- Validation: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history.py _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (44 passed).
- Removal test: reverting would drop provider handoff on history recall and remove the guardrail test.

## 2025-12-12
- Slice (kind: guardrail/tests): block clipboard image use on providers without vision.
- Changes:
  - `get_clipboard_image` now checks provider vision capability and raises `ClipboardImageUnsupportedProvider` with a provider canvas error when unsupported.
  - Added `_tests/test_clipboard_image_guard.py` to assert non-vision providers are blocked before clipboard access.
- Validation: `python3 -m pytest _tests/test_clipboard_image_guard.py _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (18 passed).
- Removal test: reverting would allow clipboard images to flow to non-vision providers and drop the guardrail test.

## 2025-12-12
- Slice (kind: guardrail/tests): ensure historyQuery surfaces provider tags.
- Changes:
  - History drawer labels now include `[provider]`; historyQuery façade tests assert provider tags flow through summaries and drawer entries.
- Validation: `python3 -m pytest _tests/test_request_history_actions.py _tests/test_request_history.py _tests/test_request_history_drawer.py _tests/test_history_query.py _tests/test_provider_streaming_warning.py _tests/test_provider_images_guard.py _tests/test_provider_capability_guard.py _tests/test_provider_binding.py _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (44 passed).
- Removal test: reverting would hide provider ids from historyQuery/drawer labels and drop the guardrails.

## 2025-12-13
- Slice (kind: status): adversarial completion check before keeping ADR in Accepted.
- Objective: verify no remaining in-repo gaps for provider switching, and note plausible edge cases.
- Evidence reviewed this loop:
  - Re-ran provider command suite: `python3 -m pytest _tests/test_provider_commands.py` (7 passed).
  - Re-read registry/command surfaces for risk review: `lib/providerRegistry.py`, `lib/providerCommands.py`.
- Adversarial checks and dispositions:
  - **New provider shapes**: Adding a non-OpenAI-compatible vendor (different request/response schema) would need a translation layer; out-of-scope for this ADR, would require a new ADR/task if requested.
  - **Auth mismatch per-provider**: Today we rely on env var hints per provider; missing or rotated tokens already surface via provider canvas + tests. No further in-repo change needed now.
  - **Alias collisions**: Registry enforces unique ids/aliases; ambiguous spoken names already error in canvas (`test_ambiguous_provider_shows_error`). No additional gap found.
  - **Reachability false positives**: Probes are optional (`user.model_provider_probe`); misconfigured endpoints show errors in canvas/status. Acceptable for this ADR; deeper SLA/error-budget tracking would be a new scope.
- Removal test: removing this entry would drop the recorded adversarial completion check; no behaviour/tests change, but ADR audit trail would be weaker.

## 2025-12-13
- Slice (kind: behaviour/tests): allow provider tokens to be configured via Talon settings (no env vars required).
- Changes:
  - Added per-provider token settings (`user.model_provider_token_openai`, `user.model_provider_token_gemini`) in `lib/talonSettings.py` and documented in `talon-ai-settings.talon.example`, `readme.md`, and `GPT/readme.md`. Legacy dict setting still supported.
  - Provider availability now checks tokens from these settings in addition to env vars (`lib/providerRegistry.py`), surfaces the source and hint in canvases (`lib/providerCommands.py`), and token errors point to the settings path (`lib/modelHelpers.py`).
  - Tests updated/added to assert settings-backed tokens count as available and are used by `get_token` (`_tests/test_provider_registry.py`).
- Validation: `python3 -m pytest _tests/test_provider_registry.py _tests/test_provider_commands.py _tests/test_provider_error_canvas.py` (13 passed).
- Removal test: reverting would drop settings-based tokens, regress provider status availability when env vars are absent, and remove documentation of the supported path.

## 2025-12-13
- Slice (kind: behaviour/tests): allow switching provider and model together via voice.
- Changes:
  - Added optional `model` capture to provider use/switch grammar (`GPT/gpt.talon`) and action signature (`lib/providerCommands.py`), persisting the requested model per provider (OpenAI -> `user.openai_model`; Gemini -> `user.model_provider_model_gemini`; custom providers get an in-session override in the registry).
  - Added Gemini model setting (`user.model_provider_model_gemini`) and hooked it into provider defaults (`lib/talonSettings.py`, `lib/providerRegistry.py`, `lib/modelHelpers.py`).
  - Docs mention the combined command and new setting (`readme.md`, `GPT/readme.md`, `talon-ai-settings.talon.example`).
  - Tests cover the new command path (`_tests/test_provider_commands.py::test_switch_with_model_sets_preference`).
- Validation: `python3 -m pytest _tests/test_provider_commands.py _tests/test_provider_registry.py` (13 passed).
- Removal test: reverting would drop the provider+model voice ergonomics and Gemini model setting, and command/tests would regress to provider-only switching.

## 2025-12-13
- Slice (kind: status): adversarial completion check after provider+model ergonomics.
- Evidence this loop:
  - Tests: `python3 -m pytest _tests/test_provider_commands.py _tests/test_provider_registry.py _tests/test_provider_binding.py _tests/test_provider_capability_guard.py _tests/test_provider_images_guard.py` (17 passed).
  - Re-read code paths: `lib/providerCommands.py` (provider+model persistence), `lib/modelHelpers.py` (model selection), `lib/providerRegistry.py` (defaults/overrides).
- Adversarial observations:
  - **Custom provider model persistence**: we mutate `user.model_provider_extra` to store a model. Risk: user-supplied structure could be non-list/dict; we guard by rebuilding dict/list but could overwrite user comments/ordering in settings files. Accept for now; larger UX would need an explicit per-provider model setting.
  - **Legacy `user.model_provider_tokens` fallback**: still supported; if both legacy dict and new string settings set, dict can override unintendedly. Mitigation: prefer string settings in docs; no change required now.
  - **Non-OpenAI request shapes**: ADR scopes OpenAI-compatible schemas; true non-OpenAI schemas would need a new adapter/ADR. Documented in prior adversarial entry; no in-repo action.
  - **Model mismatch vs capabilities**: capability guards (vision/images) already enforce provider support; streaming guard still warns. No gap observed.
- Conclusion: Current feature set matches ADR 047 in-repo scope; no additional in-repo tasks identified.
- Removal test: removing this entry would drop the adversarial check record; behaviour/tests unchanged but audit trail weaker.

## 2025-12-13
- Slice (kind: status): adversarial check after removing persistence expectations on custom provider models (Talon voice-first constraints).
- Evidence this loop:
  - Tests: `python3 -m pytest _tests/test_provider_commands.py _tests/test_provider_registry.py _tests/test_provider_error_canvas.py` (14 passed).
  - Re-read: `lib/providerCommands.py`, `lib/providerRegistry.py`, `lib/modelHelpers.py`.
- Adversarial observations (Talon-focused):
  - **Custom provider model persistence**: now session-only overrides; Talon settings cannot reliably store nested dict mutations via voice. Risk: users wanting persistent custom models must edit `model_provider_extra` manually in settings; acceptable given Talon constraints and voice ergonomics.
  - **Voice + canvas UX**: provider switches and errors already surface via commands/canvas; no reliance on non-voice interactivity. Listing/status/close are covered.
  - **Token configuration**: per-provider string settings cover Talon’s limitations on structured settings; legacy dict kept for compatibility. Minimal risk of users being unable to set tokens via voice; they can set strings directly.
  - **Non-OpenAI schema**: still out-of-scope; requires new adapter/ADR if ever needed.
- Conclusion: Within Talon’s constraints (voice-first, limited structured settings), feature is complete for ADR 047 scope.
- Removal test: dropping this entry would remove the Talon-focused adversarial audit; behaviour/tests unchanged.
