# ADR-0232: SPA Collection Sharing — Presets and History

**Status**: Proposed
**Date**: 2026-04-24

---

## Context

ADR-0165 (presets) and ADR-0231 (history) both store collections of prompt states in
`localStorage`. Currently there is no way to share a collection with another person or move it
between browsers/devices. Single-state sharing via URL hash already exists; this ADR addresses
sharing of named collections.

---

## Problem Statement

Two sharing scenarios that the current architecture cannot address:

1. **"Here's my preset pack"** — a power user has built a set of named presets for a workflow
   (e.g. "code review", "architecture diagram", "retro") and wants to share the full set with
   a teammate.

2. **"Here's my history / recent work"** — a user wants to export their history for backup,
   migration to another browser, or handoff.

URL hash sharing works for a single state snapshot. It does not scale to collections because
a collection is an ordered list of named entries, not a single state.

---

## Decisions

### Decision 1: Primary mechanism — JSON export/import (file-based)

Collections are shared via JSON file download/upload. This is the primary mechanism because:

- No size limit (URL-based sharing of large collections is impractical)
- Works offline and across any browsers/devices
- User retains full control over what they share (they download the file, inspect it, send it)
- Consistent with CLI preset file format (ADR-0165 Decision 2)

**Export**: a "Export presets" / "Export history" button downloads a JSON file.
**Import**: an "Import" button accepts a JSON file and merges entries into the local collection
(name collision on presets: prompt to overwrite or skip; history: merge by hash dedup).

### Decision 2: Export schemas

**Preset export** (`bar-presets-export.json`):
```json
{
  "version": 1,
  "exported_at": "<ISO8601>",
  "source": "spa",
  "type": "presets",
  "entries": [
    {
      "name": "<preset name>",
      "saved_at": "<ISO8601>",
      "hash": "<serialized state>",
      "tokens": ["<token>", ...]
    }
  ]
}
```

**History export** (`bar-history-export.json`):
```json
{
  "version": 1,
  "exported_at": "<ISO8601>",
  "source": "spa",
  "type": "history",
  "entries": [
    {
      "ts": "<ISO8601>",
      "hash": "<serialized state>",
      "trigger": "<trigger>",
      "subject_preview": "<string>",
      "command_preview": "<string>"
    }
  ]
}
```

Both schemas include `version` for forward compatibility and `type` so the importer can reject
wrong-type files with a clear error.

### Decision 3: URL-based preset sharing (stretch goal, not Phase 1)

For small preset collections (single preset or a few), a URL with an embedded preset hash is
appealing — "click this link and you have my preset loaded." This requires:

- Encoding the preset collection into the URL hash or a query param
- A detection step on load: does this URL contain a preset payload vs. a state payload?
- A UI prompt: "This link contains a preset named 'code review' — save it?"

**Decision: defer to Phase 2.** File-based export/import covers the primary need. URL-based
preset sharing adds UX complexity (hash format disambiguation, import confirmation flow) that
is best addressed after the file-based path is validated.

### Decision 4: Scope — which collections are in scope

| Collection | Export | Import | URL sharing |
|---|---|---|---|
| Presets | Phase 1 | Phase 1 | Phase 2 (deferred) |
| History | Phase 1 | Phase 1 | Not planned (too large; use export) |

---

## Implementation Plan

### Phase 1: File-based export/import

**Modified**: `web/src/lib/presets.ts` — add `exportPresets(entries): string` (JSON serializer),
`importPresets(json, existing): ImportResult` (merger with collision detection)

**New**: `web/src/lib/history.ts` (from ADR-0231) — add `exportHistory`, `importHistory`

**UI additions** in preset panel and history panel:
- Export button → triggers file download via `URL.createObjectURL(new Blob([json]))`
- Import button → `<input type="file" accept=".json">` hidden element, triggered on click
- Import result feedback: "Imported N presets (M skipped — already exist)"

**Tests**:
- Export produces valid JSON with correct schema
- Import merges entries correctly
- Import rejects wrong-type files with error message
- Collision handling: overwrite and skip paths

### Phase 2: URL-based preset sharing (deferred)

- Single-preset URL encoding
- Load-time detection and import confirmation UI
- Multi-preset URL encoding (if feasible within URL length limits)

---

## Consequences

**Positive**:
- Enables team sharing of curated preset packs without a backend
- Enables backup and migration of history and presets between browsers/devices
- File format is inspectable and editable by users (plain JSON)

**Neutral**:
- File-based sharing requires more steps than URL sharing for single presets; mitigated by
  Phase 2 URL sharing

**Negative / risks**:
- Import collision handling adds UI complexity; mitigated by simple "skip duplicates" default
- Schema version drift if the state format (hash encoding) changes; mitigated by including
  `hash` (self-contained restore artifact) alongside structured fields

---

## Scope

This ADR covers:
- JSON export/import for presets and history (Phase 1)
- Export schema definitions
- Import merge/collision behavior

Out of scope:
- URL-based preset sharing (Phase 2, deferred)
- CLI preset import from SPA export files (cross-surface, deferred — CLI already has its own
  `bar preset save/load` and the schemas are compatible by design per ADR-0165)

---

## Related

- ADR-0165: Preset Save / Load / Share — SPA Named Presets
- ADR-0231: SPA Prompt History
- `web/src/lib/presets.ts` — existing preset storage module
