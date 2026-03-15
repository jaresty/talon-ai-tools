# ADR-0165: Preset Save / Load / Share — SPA Named Presets

**Status**: Proposed
**Date**: 2026-03-15

---

## Context

The backlog item "Cross-surface: Preset save / load / share" describes saving a named token
configuration (all axes + persona) and reloading it across all three surfaces: CLI, TUI2, and SPA.
This ADR covers only the SPA surface. TUI2 preset interaction involves richer interactive workflow
questions (e.g. how saved presets integrate with the stage-based flow, navigation back to previous
stages, etc.) and is deferred to a separate ADR.

An audit of the current codebase reveals that the surfaces are in very different states:

### What already exists

**CLI (`bar preset` subcommand) — fully implemented** (`internal/barcli/state.go`, `app.go:557–694`):
- `bar preset save <name>` — saves the last `bar build` result as a named preset
- `bar preset list` — lists all saved presets with summary (name, saved_at, task, voice, audience, tone)
- `bar preset show <name> [--json]` — shows full preset detail or machine-readable JSON
- `bar preset use <name> --subject "..."` — re-runs build with the preset's tokens + new subject/input
- `bar preset delete <name> --force` — deletes a preset with an explicit confirmation gate
- Storage: `~/.config/bar/presets/<slug>.json`, versioned JSON schema v3, overridable via `BAR_CONFIG_DIR`

**SPA — auto-save and URL sharing implemented, named presets absent** (`web/src/routes/+page.svelte`):
- Auto-saves single slot to `localStorage['bar-prompt-state']` on every state change
- Restores from URL hash (priority) → localStorage on mount
- `serialize()` / `deserialize()` encode `{ selected, subject, addendum, persona }` as `btoa(JSON.stringify(...))`
- Share URL (Cmd+Shift+U) writes current state into the URL hash for copy/share
- **Gap**: no named save/load panel; only a single session-scoped slot

**TUI2 — grammar persona presets handled, user-saved presets absent** (`internal/bartui2/program.go`):
- Handles grammar `persona=<preset>` tokens (bundled voice/audience/tone combinations from grammar)
- Writes `last_build.json` on completion (via `state.go`) but does not read named presets at launch
- Gap deferred — TUI2 preset integration involves richer questions about the interactive stage flow and is out of scope for this ADR

### The cross-surface gap

CLI presets live in `~/.config/bar/presets/*.json`. The SPA has no path to that store and auto-saves only a single transient session slot.

---

## Problem Statement

Given that the CLI preset store exists and is tested, the remaining work in scope here is:

**SPA**: Add a named save/load panel backed by `localStorage` (multiple named slots, not the single
auto-save slot). The existing URL share mechanism already serves as the "share" vector.

The cross-surface sharing question (can a CLI preset be loaded in the SPA or vice versa?) requires
a decision about whether to unify the storage format or accept per-surface silos.

---

## Decisions

### Decision 1: SPA named preset panel

**Options compared:**

| Option | Storage | Share vector | Tradeoffs |
|---|---|---|---|
| A. `localStorage` multi-slot | `localStorage['bar-presets']` as `{[name]: serialized}` map | URL hash (existing `shareLink()`) | No backend required; stays within existing SPA architecture; local-only |
| B. URL-only (no save panel) | None; only share/load via URL | URL hash | Zero new state management; but no persistent named list |
| C. Sync with CLI preset store | Requires a local server or file:// bridge | N/A | Eliminated — SPA runs in browser; no access to `~/.config/bar/` |

**Decision: Option A** — add a named preset panel backed by `localStorage`.
- Save panel: name input + "Save" button, writes `{ name, state: serialize(), saved_at }` into `localStorage['bar-presets']`
- Load panel: list of saved presets with name + saved_at; click to restore via `deserialize()`
- Delete: per-item delete with confirmation (matches CLI `--force` gate ergonomics)
- Share (existing): the URL hash path is already the shareable link; no change needed
- The single-slot auto-save (`bar-prompt-state`) continues unchanged as the session-restore path

### Decision 2: Cross-surface sharing format

**Options compared:**

| Option | Mechanism | Tradeoffs |
|---|---|---|
| A. Independent silos (CLI JSON vs SPA localStorage) | Each surface manages its own store | Simplest; no coupling; sufficient for most use cases |
| B. Unified JSON schema importable by SPA | SPA can import/export a `presetFile` JSON matching CLI schema v3 | Enables CLI → SPA bridge; SPA export could be loaded by `bar preset save`; adds UI for import/export |
| C. Shared file path (not viable) | SPA reads `~/.config/bar/presets/` directly | Eliminated — browser cannot access filesystem |

**Decision: Option B (deferred, not blocking)** — adopt the CLI `presetFile` JSON schema v3 as
the portable interchange format, but do not implement import/export in this ADR. The SPA's
`localStorage` format should be compatible with (or trivially convertible to) schema v3 so that
a future export button can write a CLI-importable file without schema migration.

Specifically: the SPA preset record stored in `localStorage` should include:
```json
{
  "version": 3,
  "name": "<name>",
  "saved_at": "<ISO8601>",
  "source": "spa",
  "tokens": ["<token>", ...],
  "result": { "axes": {...}, "persona": {...} }
}
```
The `tokens` array is the key field — it is what `bar preset use` (and future TUI2 preset loading) needs.

---

## Implementation Plan

### Phase 1: SPA named preset panel

**Files**: `web/src/routes/+page.svelte`, possibly a new `web/src/lib/PresetPanel.svelte`

1. Add `localStorage['bar-presets']` store as `Record<string, SpaPreset>` where `SpaPreset` matches the v3 schema shape
2. Preset panel UI: save button (with name input), list of saved presets (name + date), load and delete per item
3. On save: call `serialize()` + build a `SpaPreset` record; merge into `localStorage['bar-presets']`
4. On load: call `deserialize(preset.tokens)` or restore full state from the stored record
5. The `tokens` array must be populated at save time — derive from `selected` + `persona` state using `renderCommand()` (which already exists in `renderPrompt.ts`)
6. Tests: save → list → load round-trip; delete; empty state message; persistence across reload

### Phase 2 (future): SPA import/export

- Export: serialize current preset panel entry as CLI-compatible `presetFile` JSON for download
- Import: accept a `presetFile` JSON file and add it to the SPA preset panel list

---

## Consequences

**Positive**:
- SPA gains multi-slot named presets without requiring a backend or server
- The CLI preset store (already complete) acts as the canonical reference format for future cross-surface interchange
- URL share (already implemented) remains the "share with others" path; named presets serve "my saved configurations"

**Neutral**:
- SPA and CLI maintain separate storage; a user must explicitly export/import to bridge them (deferred to Phase 2)

**Negative / risks**:
- Schema version drift: if CLI schema advances past v3 before SPA export is implemented, migration will be needed; mitigated by adopting v3 shape in SPA localStorage now

---

## Scope

This ADR covers:
- SPA named preset panel in `localStorage` (Phase 1)
- SPA interchange schema alignment with CLI v3 (Phase 1)

Out of scope:
- TUI2 preset integration — deferred; requires separate design for interactive stage-flow workflow
- SPA import/export of CLI-format JSON (Phase 2, deferred)
- Talon `{user.model} preset` — already exists separately and is Talon-only; not addressed here
- `bar preset` CLI subcommand — already complete; no changes needed

---

## Related

- `internal/barcli/state.go` — `presetFile` schema, `savePreset`, `loadPreset`, `deletePreset`
- `internal/barcli/app.go:557–694` — CLI `bar preset` subcommand routing
- `web/src/routes/+page.svelte:37–64` — `serialize()` / `deserialize()`, auto-save, URL hash
- `internal/bartui2/program.go:141` — `autoFilledTokens` pattern (reference for future TUI2 work)
- BACKLOG.md — "Cross-surface: Preset save / load / share" (Tier 2)
- BACKLOG.md — "TUI2: Out-of-order token editing" (Tier 2, related deferred TUI2 work)
