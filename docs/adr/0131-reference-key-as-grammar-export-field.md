# ADR 0131: Reference Key as Grammar Export Field

## Status

Proposed

## Context

The prompt reference key — the meta-instructions embedded in every CLI-generated prompt explaining how the LLM should interpret TASK/CONSTRAINTS/PERSONA/SUBJECT — is currently defined as a hardcoded constant in two separate files:

- `internal/barcli/render.go` — `referenceKeyText` (Go constant, used by the CLI)
- `lib/metaPromptConfig.py` — `PROMPT_REFERENCE_KEY` (Python constant, used by the API/Python path)

These two strings must stay identical in content, but there is no mechanism enforcing sync. Before ADR-0130 they had already drifted slightly in phrasing. ADR-0130 added two new rules to both files simultaneously, demonstrating the ongoing maintenance burden.

The prompt grammar JSON (`internal/barcli/embed/prompt-grammar.json`) is the established SSOT for all token→description data. It is generated from Python source files via `python -m prompts.export`, embedded in the Go binary, and read at runtime by the CLI. `SchemaVersion` is already an example of a non-token scalar field that flows from Python → grammar JSON → `Grammar` struct → `BuildResult`.

### Why the reference key belongs in the grammar

The reference key is the LLM-facing interpretation contract for the prompt vocabulary. It references token categories (Form, Channel, Scope, etc.) and their precedence relationships. As the token vocabulary evolves — new axes, new precedence rules — the reference key evolves with it. It is conceptually part of the grammar, not a separate concern.

Placing it in the grammar export means: **change `metaPromptConfig.py`, run the export, both paths are updated**. No manual sync, no drift.

---

## Decision

Add `reference_key` as a top-level field in the grammar JSON payload. `metaPromptConfig.py` remains the SSOT (Python reads it directly; no change to the Python rendering path). The Go CLI reads it from the grammar instead of a hardcoded constant.

### Implementation

#### 1. `lib/promptGrammar.py` — add to export payload

```python
from lib.metaPromptConfig import PROMPT_REFERENCE_KEY

def prompt_grammar_payload() -> dict[str, Any]:
    # ... existing section building ...

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "reference_key": PROMPT_REFERENCE_KEY,   # ← add this
        **sections,
        "checksums": checksums,
    }
    return payload
```

`reference_key` is not included in `sections` and therefore not included in `checksums`. It is a standalone scalar field like `schema_version`. (Rationale: the reference key text is long and changes for semantic reasons unrelated to token catalog integrity. Including it in checksums would cause spurious checksum mismatches on every reference key edit.)

#### 2. `internal/barcli/grammar.go` — add field to structs

```go
// Grammar struct — add alongside SchemaVersion
type Grammar struct {
    SchemaVersion string
    ReferenceKey  string   // ← add this
    Axes          AxisSection
    // ... rest unchanged
}

// rawGrammar struct — add JSON tag
type rawGrammar struct {
    SchemaVersion string         `json:"schema_version"`
    ReferenceKey  string         `json:"reference_key"`   // ← add this
    Axes          rawAxisSection `json:"axes"`
    // ... rest unchanged
}

// In the parse/load function, alongside:
//   grammar.SchemaVersion = raw.SchemaVersion
grammar.ReferenceKey = raw.ReferenceKey   // ← add this
```

#### 3. `internal/barcli/build.go` — propagate to BuildResult

`BuildResult` already carries `SchemaVersion` from the grammar. Add `ReferenceKey` the same way:

```go
// build.go — BuildResult struct
type BuildResult struct {
    SchemaVersion string `json:"schema_version"`
    ReferenceKey  string `json:"reference_key,omitempty"`   // ← add this
    // ... rest unchanged
}

// build.go — result construction (alongside SchemaVersion)
result := &BuildResult{
    SchemaVersion: s.grammar.SchemaVersion,
    ReferenceKey:  s.grammar.ReferenceKey,   // ← add this
    // ...
}
```

#### 4. `internal/barcli/shuffle.go` — propagate to BuildResult

`Shuffle` already receives `*Grammar`. Set it on the result the same place `SchemaVersion` would be set:

```go
result.ReferenceKey = g.ReferenceKey   // ← add alongside SchemaVersion assignment
```

#### 5. `internal/barcli/render.go` — read from result, keep constant as fallback

```go
// render.go — in RenderPlainText
refKey := result.ReferenceKey
if refKey == "" {
    refKey = referenceKeyText   // backward compat: cached builds pre-ADR-0131
}
writeSection(&b, sectionReference, refKey)
```

The `referenceKeyText` constant is **kept** for now as a fallback for cached builds that predate this change. It can be removed in a future cleanup once the cached build window has passed (or when the state schema version is bumped for other reasons).

### Files changed

| File | Change |
|------|--------|
| `lib/promptGrammar.py` | Add `"reference_key": PROMPT_REFERENCE_KEY` to payload |
| `internal/barcli/grammar.go` | Add `ReferenceKey string` to `Grammar` and `rawGrammar`; set in parse |
| `internal/barcli/build.go` | Add `ReferenceKey string` to `BuildResult`; set from grammar at build time |
| `internal/barcli/shuffle.go` | Set `result.ReferenceKey = g.ReferenceKey` |
| `internal/barcli/render.go` | Read `result.ReferenceKey` with fallback to `referenceKeyText` constant |
| `internal/barcli/embed/prompt-grammar.json` | Regenerated by export — gains `reference_key` field |
| `lib/metaPromptConfig.py` | No change — remains the SSOT |

### Workflow after this change

To update the reference key:

```
1. Edit PROMPT_REFERENCE_KEY in lib/metaPromptConfig.py
2. python -m prompts.export          # regenerates prompt-grammar.json
3. go build ./cmd/bar                # embeds updated grammar
4. Commit both .py and .json changes
```

This is identical to the existing workflow for updating axis token descriptions.

---

## Consequences

### Positive

- **Single edit point**: change `metaPromptConfig.py`, run export, both paths stay in sync automatically
- **No Python path changes**: `modelTypes.py` still imports `PROMPT_REFERENCE_KEY` directly — zero changes to Python rendering
- **Consistent pattern**: follows the exact `SchemaVersion` precedent already established in the codebase
- **Auditable**: the reference key text appears in the grammar JSON, making it visible in diffs and review alongside the token changes that motivated it
- **Backward compatible**: the `referenceKeyText` fallback in render.go handles pre-ADR-0131 cached builds

### Tradeoffs

- **Export required for CLI changes**: updating the reference key now requires running `python -m prompts.export` before rebuilding the Go binary. Previously you could edit the Go constant directly and rebuild. This is intentional — it enforces the SSOT discipline.
- **`reference_key` in BuildResult**: the reference key text (~1KB) is included in every serialized `BuildResult`. This is the same tradeoff as `SchemaVersion` (a few bytes) but larger. Acceptable: cached builds already store the full rendered prompt text, which is larger.
- **`referenceKeyText` constant lingers**: the Go fallback constant stays until a future cleanup. This temporarily maintains the duplication it was meant to eliminate. A follow-up that bumps the state schema version can remove it cleanly.

### Risks

- **Export discipline**: if a developer edits `metaPromptConfig.py` without running export, the CLI and Python paths will diverge until the next export. This is the same risk as any other Python→grammar change. Mitigations: CI check on grammar freshness (already exists or can be added), commit hook.

---

## Related

- ADR-0130: Conflict Resolution via Reference Key and Token Guidance (the content changes that motivated this consolidation)
- ADR-0109: Axis Token Labels (established `labels` as a grammar export field — same pattern)
- ADR-0110: Axis Token Guidance (established `guidance` as a grammar export field — same pattern)
