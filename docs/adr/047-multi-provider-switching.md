# 047 – Multi-Provider Selection and Voice Switching Commands

- Status: Accepted  
- Date: 2025-12-12  
- Context: Current LLM orchestration assumes a single OpenAI-compatible endpoint configured via `user.model_endpoint` / `user.openai_model`, with occasional Azure/llamafile swaps done by editing settings. Voice flows (`model run`, `model write`, `model suggest`, etc.) do not expose a first-class concept of "provider" or a way to switch providers mid-session.

---

## Summary (for users)

- A **provider** is a named bundle of endpoint URL, auth, defaults, and compatible models (for example `openai`, `azure-gpt4o`, `local-llamafile`).
- New commands keep switching hands-free:
  - `model provider list` – show available providers with status (current, unavailable).
  - `model provider use <name>` / `model provider switch <name>` – make `<name>` the active provider for future requests.
  - `model provider next` / `model provider previous` – cycle through the registry in voice-friendly order.
  - `model provider status` – speak/show the current provider, default model, and streaming toggle.
- Changing provider is **immediate for new prompt sessions**; in-flight requests continue with their original provider unless explicitly cancelled and retried.

---

## Decision

1. **Introduce a provider registry and SSOT**
   - Define a typed registry (for example `lib/providerRegistry.py`) that owns provider IDs, **spoken aliases**, display names, endpoint URLs, auth hints (env var names), default model IDs, and feature flags (streaming, vision, images). Spoken aliases must be short, unambiguous, and voice-friendly (for example `open ai`, `azure g p t four o`, `llama local`, `gemini`).
   - Allow local overrides via `talon-ai-settings.talon` (for example `user.model_provider_default`, per-provider model overrides, or an additional `user.model_provider_extra` list) so users can add or replace providers without patching code. Each provider override can define: endpoint URL (optional if using the OpenAI default), API key/env var name, default model, and capability flags. Secrets remain in env vars; settings only reference the env var name.
   - Registry resolves the *current provider* to a concrete HTTP client config consumed by `PromptSession` and downstream request builders.

2. **Voice commands for selection and inspection**
   - Add commands under `model provider …` to list, switch by name, cycle, and report status. Name matching accepts provider ID or any spoken alias; ambiguous matches fail fast with a concise spoken error and a canvas hint.
   - Switching updates the in-memory provider choice and persists to settings (for example `user.model_provider_current`) so restarts keep the selection.
   - Status/list surfaces include availability hints (missing key, unreachable endpoint last check, unsupported capabilities for the current recipe).

3. **Provider-aware prompt sessions**
   - `PromptSession.prepare_prompt` reads the active provider and injects provider-specific model ID, endpoint, headers, and request shape. Contract/axis logic remains unchanged.
   - In-flight sessions keep their bound provider; switching affects *new* sessions only, unless the user cancels and retries.
   - Errors from provider mismatch (missing key, feature not supported) surface early with actionable speech/overlay tips.

4. **Testing and guardrails**
   - Unit tests cover registry resolution (including spoken alias matching), voice command parsing, cycling order, persistence to settings, and that prompt sessions honor the active provider without leaking previous config.
   - Smoke test scripts stub multiple providers to assert switching does not mutate cached headers/body shapes across requests.

---

## Consequences

### Benefits

- Voice-first workflow for swapping cost/quality/offline providers without editing files or restarting Talon.
- Clear separation between **provider** (transport + auth) and **contract axes** (what to ask), reducing accidental drift in request shapes.
- Extensible path to add image/vision/streaming capability flags per provider without touching core prompt logic.

### Risks and mitigations

- **Risk: inconsistent model IDs across providers** – Mitigate with per-provider default model config and command feedback that echoes the chosen model.
- **Risk: user switches mid-run causing confusion** – Mitigate by binding provider to each session at creation and narrating that switches affect new runs only.
- **Risk: registry rot or missing secrets** – Mitigate with availability/status commands, stub providers in tests, and graceful fallbacks to the last known-good provider.

---

## Implementation sketch

1) **Registry + settings** – Add `ProviderConfig` dataclass, registry list/dict (seeded with `openai` and `gemini` out of the box), and helpers to merge user overrides from `talon-ai-settings.talon`. Persist current provider in `user.model_provider_current` with a sane default (`openai`).

2) **Command layer** – New Talon commands (`model provider list/use <name>/next/previous/status`) wired to registry helpers, emitting spoken feedback plus **canvas-based** list/status output (instead of transient notifications). Errors for unknown or unavailable providers render in the canvas with the interpreted alias and nearest matches.

3) **Session plumbing** – Thread provider config through `GPTState` / `PromptSession` creation so request builders use the active provider's endpoint/model/auth/flags. Ensure cancelling+retrying re-reads the latest provider.

4) **Tests** – Cover registry resolution (IDs + spoken aliases), persistence, cycling order, provider-bound sessions, and a regression test that switching providers between requests does not leak headers or URL from the prior provider.
