# ADR-0163: `bar lookup` — intent-to-token subcommand

**Status**: Proposed
**Date**: 2026-03-14

---

## Context

The bar grammar contains ~200 tokens across task, scope, method, form, channel, completeness, directional, and persona axes. Each token has structured metadata: `heuristics[]` (trigger words), `distinctions[]` (cross-references), and `definition` text (ADR-0154/0155).

Users approach bar with intent vocabulary ("debug", "root cause", "compare options"), not grammar vocabulary ("probe", "diagnose", "diff"). The current surfaces for closing this gap are:

- **`bar help llm`** — prose routing guide optimised for LLM reading; not machine-readable
- **`bar help tokens --plain`** — full token dump (tab-separated); requires the caller to know what to grep
- **Unrecognized-token heuristic fallback** (ADR-0163 predecessor work) — `searchByHeuristics()` in `internal/barcli/build.go` searches `heuristics[]` across all axes when a token is not recognized and emits "Suggested by intent:" in the error output

None of these is optimised for the query "I want to do X — what token should I use?" asked directly. `searchByHeuristics()` already implements the core matching logic, but it is reachable only via the error path and currently searches `heuristics[]` only (not `distinctions[]` token names or `definition` text).

---

## Decision

Add a `bar lookup <query>` subcommand that exposes intent-to-token matching as a first-class operation.

### Interface

```
bar lookup <query> [--axis <axis>] [--json]
```

- **`<query>`** — required positional argument; one or more words (quote multi-word phrases)
- **`--axis <axis>`** — optional filter; restrict results to one axis (e.g., `method`, `task`, `voice`)
- **`--json`** — emit results as a JSON array instead of human-readable lines
- No stdin input; no `--subject` / `--addendum`

### Ranking tiers (applied in order, highest first)

| Tier | Condition |
|------|-----------|
| 3 (highest) | Query word exactly matches a heuristic trigger word (case-insensitive) |
| 2 | Query word is a case-insensitive substring of a heuristic trigger word |
| 1 | Query word is a case-insensitive substring of a distinction token name |
| 0 (lowest) | Query word is a case-insensitive substring of the definition text |

Within each tier, results are sorted alphabetically by `axis:token`. A token may only appear once (its highest-tier match wins). Results are capped at 10.

### Human-readable output format

```
method:diagnose — Identify likely root causes
task:probe — Surface assumptions and implications
method:abduce — Generate explanatory hypotheses
```

One result per line: `axis:token — Label`. No header. Empty result: print nothing, exit 0.

### JSON output schema

```json
[
  {
    "axis": "method",
    "token": "diagnose",
    "label": "Identify likely root causes",
    "tier": 3,
    "matched_field": "heuristics",
    "matched_text": "root cause"
  }
]
```

Fields:
- `axis` (string) — axis name
- `token` (string) — token slug
- `label` (string) — short label; empty string if not defined
- `tier` (int) — match tier 0–3
- `matched_field` (string) — `"heuristics"`, `"distinctions"`, or `"definition"`
- `matched_text` (string) — the specific heuristic phrase, distinction token name, or definition substring that matched

### Exit codes

| Condition | Exit code |
|-----------|-----------|
| Results found (any tier) | 0 |
| No results | 0 |
| Unknown `--axis` value | 1 |
| Missing query argument | 1 |

### Query matching semantics

The query is split on whitespace; each word is matched independently. A token must match **all** words to be included (AND logic). Matching is case-insensitive. The tier assigned is the highest tier achieved across all words for that token.

---

## Implementation notes

1. **Extract `searchByHeuristics`** from `internal/barcli/build.go` into a shared helper (e.g., `internal/barcli/lookup.go`) that accepts `query string`, `g *Grammar`, and `axisFilter string`. Return `[]LookupResult` rather than `[]string`.

2. **`LookupResult` struct**:
   ```go
   type LookupResult struct {
       Axis         string
       Token        string
       Label        string
       Tier         int
       MatchedField string
       MatchedText  string
   }
   ```

3. **Extend matching** to cover `distinctions[]` token names (tier 1) and `definition` text (tier 0). The existing `searchByHeuristics` covers heuristics only.

4. **Wire subcommand** in `internal/barcli/app.go`: add `"lookup"` to the top-level dispatch, parse `--axis` and `--json` flags, call the shared helper, format output.

5. **Update `formatUnrecognizedError`** in `build.go` to call the extracted helper rather than the inline implementation.

6. **Tests** (`internal/barcli/lookup_test.go` or `app_lookup_cli_test.go`):
   - Exact heuristic match returns tier 3
   - Substring heuristic match returns tier 2
   - Distinction token name match returns tier 1
   - Definition substring match returns tier 0
   - Multi-word query requires all words to match
   - `--axis method` filters out non-method results
   - `--json` emits valid JSON with correct schema
   - Unknown `--axis` exits 1
   - Missing query exits 1
   - No matches exits 0 with empty output

7. **Help string**: add `bar lookup <query> [--axis AXIS] [--json]` to `generalHelpText` in `app.go`.

---

## Consequences

**Changes:**
- New `bar lookup` subcommand available at CLI surface
- `searchByHeuristics` extracted and extended; unrecognized-token fallback continues to work via the shared helper
- `bar help llm` reference updated to document `bar lookup`
- Backlog item "CLI: `bar lookup`" marked complete

**Unchanged:**
- `bar help tokens --plain` behaviour
- Unrecognized-token error format (still shows "Suggested by intent:" section)
- Grammar JSON schema — no new fields required
- All existing tests

**Enables:**
- `bar-dictionary` skill (Tier 3 backlog) — depends on `bar lookup` as its lookup backend
- Shell scripts and LLM agents that need a ranked token-from-intent lookup without parsing full `bar help llm` output
