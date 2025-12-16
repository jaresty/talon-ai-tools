# ADR-0055 – Retire Source-Only Save Paths in Favour of File Destination

Status: Accepted  
Date: 2025-03-11  
Owners: Talon AI tools maintainers

---

## Context

ADR-0039 made “save to file” a first-class `file` destination so `model pass … to file` produces human-friendly markdown containing prompt/context, response, and meta. We still carry source-only helpers and surfaces from ADR-0038, including:

- `model history save source` grammar → `_save_history_prompt_to_file` (prompt-only).
- `gpt_save_source_to_file` and `_save_source_snapshot_to_file` helpers (no grammar, but still exposed/action-tested).
- Settings/help copy that references “model source save file/history save source.”

These parallel paths add cognitive load, teach two save models, and continue to emit prompt-only artefacts that don’t meet the JTBD from ADR-0039.

## Decision

- Deprecate and remove prompt-only save surfaces and helpers; use the `file` destination for all user-facing saves.
- Route history saves through the `file` destination (prompt + response + meta) instead of bespoke prompt-only writers.
- Update docs/settings/help text to describe the unified `file` destination directory and examples (`model pass last to file`, `model pass exchange to file`).
- Keep a minimal private helper only if needed for debugging; no grammar, GUI buttons, or tests should depend on source-only saves.

## Consequences

- **Positive**: Single mental model (`model pass … to file`), saved artefacts match the archive/recall JTBD, fewer parallel code paths to maintain.
- **Risks/mitigations**: Users who relied on prompt-only saves lose that exact shape; offer `model pass exchange to file` (includes prompt) and note the migration in release notes. Ensure history `file` writes are idempotent and respect `user.model_source_save_directory`.
- **Scope**: Does not change the `file` destination’s content contract (still human-readable markdown); no change to raw log capture.

## Migration Plan

1) Remove grammar/surfaces: delete `model history save source`, confirmation/pattern GUI buttons that target source-only helpers, and any mentions in help/settings copy.  
2) Repoint internal callers: if a history save control remains, have it call `model pass … to file` (exchange variant) instead of prompt-only writers.  
3) Prune helpers/tests: delete `gpt_save_source_to_file` public action and prompt-only history saver tests; keep a private helper only if required for debugging.  
4) Add/refresh tests: ensure `file` destination writes response/exchange markdown for history-driven saves and honours `user.model_source_save_directory`.  
5) Docs: update README/settings examples to show `model pass last/exchange to file` as the canonical save flow; note that source-only saves were removed.
