# 055 – Portable prompt grammar CLI
# 0065 — Portable prompt grammar CLI

## Status
Proposed

## Context
- Python modules such as `lib/talonSettings.py` compose prompts by combining a static prompt key, contract axes (completeness, scope, method, form, channel, directional), and optional persona hints (voice, tone, audience, intent).
- Teams who rely on those shorthand tokens need access to the same behaviour when Talon is unavailable, particularly for shell automation and cross-platform collaboration.
- Prior Go-based experiments diverged because they reimplemented the grammar instead of consuming a single source of truth.
- Talon-only state such as GUI presets or runtime history cannot be assumed in a portable tool, so the solution must rely solely on static configuration.

## Decision
- The Python implementation remains the single source of truth. A lightweight exporter (`python -m prompts.export`) serialises static prompts, contract-axis metadata, persona vocabularies, persona presets (voice + audience + tone bundles), and hierarchy rules into `build/prompt-grammar.json`, including schema versioning and checksums.
- The Go CLI is named `bar` and launches with a single command surface: `bar build <tokens…> [--prompt TEXT|--input FILE] [--output FILE] [--json]`. Tokens may be provided in shorthand order (static prompt → contract axes → persona hints or presets → directional lens) or via explicit `key=value` overrides. Parsing is left-to-right: all tokens before the first `=` are treated as shorthand; once a `key=value` token appears, every subsequent token must be `key=value`. Shorthand semantics match Talon: static and completeness accept at most one token, form/channel/directional/persona axes accept at most one token each, scope accepts up to two tokens, and method accepts up to three tokens. Overrides encountered later may update any axis (last wins); attempts to supply multiple shorthand tokens for a single-valued axis, multiple presets, or to exceed the scope/method cardinality raise a `conflict` error.
- The static prompt defaults to `static=infer` when no shorthand or explicit `static=` token is supplied, matching Talon behaviour. The resolved static prompt always appears in the JSON output even when defaulted.
- Prompt content is optional. When no prompt body is supplied via `--prompt`, `--input`, or stdin, `bar build` still renders the Task/Constraints block and emits a `Subject:` line containing the fixed placeholder `(none provided)` (not localised in v1). When stdin is piped, the CLI consumes it automatically; no delimiter is required.
- Persona usage is stateless and deterministic. Exactly one preset token (e.g., `persona=facilitator`) may appear in the shorthand region (before any `=` tokens); the preset expands immediately to voice/audience/tone. Intent tokens may appear in shorthand (`coach`) or as `intent=` overrides and follow the same last-wins rule. Providing more than one preset or placing a preset after a `key=value` token raises `preset_conflict`; repeating other single-valued persona axes in the shorthand portion (voice, audience, tone, intent) raises `conflict`.
- Once override mode begins (after the first `key=value` token), any further shorthand token results in a `format` error (`error.type = "format"`), prompting users to place overrides last.
- Error responses are structured. When `--json` is set, failed invocations return JSON in the form `{ "error": { "type": "unknown_token" | "conflict" | "missing_static" | "preset_conflict" | "format" | "io" | …, "message": "…", "unrecognized": [ … ], "recognized": { … } } }`. Without `--json`, errors return human-readable text conveying the same information. Any additional error types that emerge will follow the same schema and consolidate around the documented contract.
- `--json` emits a machine-readable payload containing `schema_version`, `subject`, `task`, `constraints`, `axes`, and `persona` fields so downstream tooling has a stable contract. The `subject` field carries the raw prompt body (empty string when no body is supplied). The `constraints` array contains only meaningful entries (no header line). Optional fields are omitted rather than populated with empty strings; arrays (such as `axes.channel`) are emitted only when non-empty. The empty-subject placeholder is only present in the plain-text output.
- Discovery and linting helpers are deferred to future ADRs to keep v1 focused on prompt construction.
- CI regenerates the artifact, verifies cleanliness, and exercises shared fixtures covering at least: (1) a static-only recipe using defaults, (2) one recipe per contract axis (completeness-only, scope-only, method-only, form/channel-only, directional-only), (3) a mixed shorthand + `key=value` recipe, (4) a persona preset recipe, and (5) an error case verifying structured error output.

## Rationale
- Exporting static data keeps Python authoritative while allowing other runtimes to consume the grammar without duplication.
- A single `build` command and the defined parsing rules remove ambiguity between shorthand tokens and overrides, ensuring deterministic precedence and clearer errors.
- Treating prompt content as optional supports workflows where the contract is prepared before the body and avoids blocking on stdin when no data is present; the fixed placeholder keeps downstream detection simple while the JSON `subject` field preserves raw input for automation.
- Clear preset semantics (one preset, last-wins overrides, explicit error types) produce predictable behaviour for end users and automation alike.
- Deferring ancillary helpers keeps the initial release small and reduces implementation risk while leaving room for future expansion via new ADRs.
- Explicit CI coverage expectations give contributors a concrete bar for maintaining parity between Python and Go implementations.

## JSON Output Schema
The `--json` flag produces:
```json
{
  "schema_version": "1.0",
  "subject": "",
  "task": "Task:\n  …",
  "constraints": ["Completeness: …", "Scope: …"],
  "axes": {
    "static": "todo",
    "completeness": "full",
    "scope": ["focus"],
    "method": ["steps"],
    "form": ["checklist"],
    "directional": "fog"
  },
  "persona": {
    "preset": "facilitator",
    "voice": "as-facilitator",
    "audience": "to-team",
    "tone": "kindly",
    "intent": "coach"
  }
}
```
Fields such as `axes.channel` and `persona.intent` are omitted when unset. The `subject` string contains the raw prompt body or `""` when none was provided. Schema evolution will bump `schema_version` (semantic versioning) while preserving backward compatibility guarantees.

## Examples
- `bar build todo gist focus steps fog persona=facilitator intent=coach`
- `bar build todo gist focus steps fog persona=facilitator intent=coach tone=kindly`
- `bar build static=describe completeness=full scope=system method=mapping form=table directional=rog voice=as-teacher audience=to-junior-engineer tone=gently intent=teach --prompt "Outline the onboarding module"`
- `cat incident-notes.md | bar build static=fix completeness=skim scope=narrow method=steps form=plain directional=fog tone=kindly intent=persuade`
- `bar build todo scope=focus method=steps persona=facilitator static=todo`
- `bar build todo persona=facilitator persona=coach` *(raises preset_conflict)*
- `bar build todo gist fog tone=kindly scope=focus intent=coach` *(raises format because shorthand appears after overrides)*
- `bar build todo gist --json`

Each example yields a Task/Constraints block. Examples without body input include the placeholder `Subject:
  (none provided)` in the plain-text form while the JSON `subject` field returns `""`.

## Consequences
- Users without Talon gain access to the established grammar through a portable binary while continuing to reason about the same tokens.
- Contributors regenerate the JSON artifact whenever grammar rules change, adding a modest but explicit development step.
- Persona usage stays deliberate and per-invocation; users who want persistent stances must layer their own scripts.
- Structured errors and JSON output make the CLI predictable in automation, while deferring helper flags keeps the scope manageable for the first release.
- Future enhancements (e.g., listing tokens, validation-only checks, recipe helpers) require new ADRs to maintain clarity around scope.

## Alternatives Considered
- Persisting persona defaults in a CLI config — rejected to avoid hidden state and UX drift.
- Rebuilding the grammar directly in Go — rejected due to duplication risk and long-term maintenance costs.
- Shipping only the Python exporter and expecting users to script around it — rejected because many collaborators prefer ready-to-run binaries and minimal setup.
- Forcing exclusive `key=value` syntax — rejected because shorthand tokens remain core to the grammar’s ergonomics; instead the parser handles shorthand first and applies `key=value` overrides afterward for clarity where needed.
- Requiring stdin content for every invocation — rejected to support prompt-shell workflows and prevent hangs when no input is present.
