# ADR-0231: SPA Prompt History

**Status**: Proposed
**Date**: 2026-04-24

---

## Context

The SPA already auto-saves a single session slot (`localStorage['bar-prompt-state']`) and supports
named presets (`localStorage['bar-presets']`). Neither addresses the "I built something, used it,
and now want to find it again" case — accidental discard of a useful state that was never explicitly
saved.

Presets (ADR-0165) cover deliberate, named saves. History covers implicit, ephemeral saves — the
complement to presets, not a replacement.

---

## Problem Statement

Users who copy a prompt, share a link, or open a shared link have no way to return to that state
if they navigate away or modify their selections. The single auto-save slot is overwritten on every
change, so there is no lookback beyond the current session state.

---

## Decisions

### Decision 1: Trigger points

History entries are recorded when the user takes an action that signals "I used this":

| Trigger | Rationale |
|---|---|
| Copy command (⌘⇧C) | User copied the CLI command — it was useful |
| Copy prompt (⌘⇧P) | User copied the rendered prompt — it was useful |
| Share prompt | User shared the prompt text |
| Share link (⌘⇧U) | User shared the URL |
| Copy link (⌘⇧L) | User copied the link |
| Open shared link | User loaded a state from a URL hash — worth recording for "what was that link?" |

Passive chip toggles and typing in the subject field do not trigger history writes — too noisy.

### Decision 2: Entry schema

```json
{
  "ts": "<ISO8601>",
  "hash": "<btoa-encoded state string>",
  "trigger": "copy-command | copy-prompt | share-prompt | share-link | copy-link | open-link",
  "subject_preview": "<first 80 chars of subject, or empty string>",
  "command_preview": "<rendered CLI command tokens, e.g. 'show completeness scope'>"
}
```

- `hash` is the full serialized state (same format as `serialize()` / URL fragment) — restoring it
  via `deserialize()` recovers all axes, persona, subject, and addendum
- `subject_preview` is stored as a convenience for display; it is derived from the full state in
  `hash` so it carries no additional information. Users who are concerned about sensitive subject
  content can clear history at any time
- `command_preview` is the rendered token sequence (persona + axes) for display without
  deserializing — derived from `tokens` computed state at record time

### Decision 3: Storage

Key: `localStorage['bar-history']` as a JSON array of entries, newest first.

Max entries: 50. On write, if the array would exceed 50, the oldest entry is dropped (FIFO).

Deduplication: if the last entry has the same `hash` as the new entry, skip the write — prevents
duplicate entries from repeated copy actions on the same state.

### Decision 4: UI

- History panel rendered as a collapsible section, structurally similar to the presets panel
- Each entry shows: relative timestamp ("2 hours ago"), `command_preview`, and truncated
  `subject_preview`
- Click to restore: calls `deserialize(entry.hash)` to restore full state
- Per-entry delete button
- "Clear all" button at panel header level
- Empty state: "No history yet. History is saved when you copy or share a prompt."
- Panel location: below presets panel in the sidebar / action area (exact placement TBD at
  implementation time)

### Decision 5: Subject content in history

Subject text is stored (via `hash`, which encodes the full state including subject). Rationale:
- Typical subject content is code snippets, task descriptions, and error messages — not secrets
- Stripping subject makes history entries much less useful (entries become indistinguishable without it)
- Mitigation: per-entry delete and "clear all" give users full control
- A note in the empty state and/or panel header clarifies that history is stored locally in the browser

---

## Implementation Plan

### Phase 1: Core history

**New file**: `web/src/lib/history.ts` — pure functions: `loadHistory`, `saveHistory`,
`addHistoryEntry`, `clearHistory`, `deleteHistoryEntry`

**Modified**: `web/src/routes/+page.svelte`
- Import history functions
- Call `addHistoryEntry` in each trigger function (`copyCommand`, `copyPrompt`, `sharePromptNative`,
  `shareLink`, `copyLink`)
- Call `addHistoryEntry` in `onMount` when a URL hash is detected (open-link trigger)
- Add history panel to sidebar / action area

**Tests**: `web/src/routes/history.test.ts`
- Entry added on each trigger
- Duplicate hash suppressed
- FIFO eviction at 50 entries
- Restore from history restores full state
- Per-entry delete removes entry
- Clear all empties history

### Phase 2 (future): Export / import

- Export history as JSON file (download)
- Import history entries from a JSON file (merge, not replace)

---

## Consequences

**Positive**:
- Recovers accidentally discarded states without requiring explicit saves
- Complements presets without duplicating them — history is automatic, presets are deliberate
- No backend required; entirely localStorage-based

**Neutral**:
- Subject text is stored; users who prefer not to have this can clear history

**Negative / risks**:
- 50-entry FIFO means old entries are lost; users who need longer history must use presets
- localStorage size: each entry is ~1–2 KB (hash-encoded state + previews); 50 entries ≈ 100 KB,
  well within the 5 MB limit

---

## Scope

This ADR covers:
- History recording on copy/share/open-link triggers
- History panel UI (view, restore, delete, clear)
- localStorage schema and eviction policy

Out of scope:
- Export/import of history (Phase 2, deferred)
- Cross-surface history (CLI/TUI2 have no equivalent concept)
- Sharing a history entry as a link — already covered by the existing share-link feature

---

## Related

- ADR-0165: Preset Save / Load / Share — SPA Named Presets
- `web/src/routes/+page.svelte` — `serialize()`, `deserialize()`, trigger functions
- `web/src/lib/presets.ts` — structural reference for localStorage module pattern
