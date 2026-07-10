---
name: bar-dictionary
description: Use when user asks which token fits an intent — looks up bar tokens by intent phrase and returns ranked matches.
  token matches a user's intent, when you need the full metadata for a specific token, or
  when you need all tokens on an axis.
---

# Bar Dictionary Skill

## Purpose

`bar-dictionary` is a **lookup primitive** — it maps user intent to bar tokens by querying
the live grammar. It does **not** run `bar build` or produce structured prompts. Its only job
is to answer: "what token should I use for X?"

Use this skill instead of hardcoding token names or descriptions in other skills. Token
metadata changes as the grammar evolves; `bar-dictionary` always reflects the current state.

## Scope boundary

**In scope:**
- Finding tokens that match an intent phrase
- Returning full metadata for a known token
- Listing all tokens on an axis with labels and heuristics

**Out of scope:**
- Running `bar build` (use `bar-autopilot` or `bar-workflow` for that)
- Generating or structuring prompts
- Selecting tokens on the user's behalf (return results; let the caller decide)

---

## Operation 1: Intent lookup

**Use when:** You have a user intent phrase and need to find matching tokens, starter packs, or sequences.

Results include three kinds, distinguished by the `kind` field:
- `kind=token` — a single grammar token to append to `bar build`
- `kind=pack` — a starter pack; the runnable `bar build` command appears inline in text output and in the `command` field in JSON
- `kind=sequence` — a named multi-step workflow; step count and `bar sequence show <name>` appear inline

```bash
bar lookup "<phrase>"               # search across all axes (tokens + packs + sequences)
bar lookup "<phrase>" --axis method # restrict to one axis (tokens only when axis filter set)
bar lookup "<phrase>" --json        # structured output; each result has kind, token, command fields
bar lookup debug                    # → pack:debug (→ bar build probe diagnose adversarial unknowns), sequence:debug-cycle, tokens
```

**Output (human-readable):** one result per line, ranked by match quality. Tokens with a guidebook entry show `[guide]`; use `bar guide <token>` to read it.

```
[T3] pack:debug — Diagnosing a bug or system failure  → bar build probe diagnose adversarial unknowns
[T3] task:probe — Surface assumptions and implications  [guide]  [matched heuristics: "debug"]
[T2] sequence:debug-cycle — Surface root causes, fix them...  [3 steps → bar sequence show debug-cycle]
[T2] method:diagnose — Identify likely root causes
```

**Output (--json):** array of objects with `axis`, `token`, `label`, `kind`, `command` (packs only), `tier` (0–3), `matched_field`, `matched_text`, `has_guide` (true when a guidebook entry exists).

```json
[
  {
    "axis": "pack",
    "token": "debug",
    "label": "Diagnosing a bug or system failure",
    "kind": "pack",
    "command": "bar build probe diagnose adversarial unknowns",
    "tier": 3,
    "matched_field": "token",
    "matched_text": "debug"
  },
  {
    "axis": "task",
    "token": "probe",
    "label": "Surface assumptions and implications",
    "kind": "token",
    "tier": 3,
    "matched_field": "heuristics",
    "matched_text": "debug",
    "has_guide": true
  }
]
```

**Tier meanings:** 3 = exact name/heuristic match, 2 = substring match,
1 = distinction token name match, 0 = definition text match. Higher tier = stronger signal.

**Multi-word queries use AND logic:** all words must match. Quote phrases:
```bash
bar lookup "root cause"           # matches tokens where both words appear
bar lookup "debug" --axis method  # debug-related method tokens only (no packs/sequences)
```

---

## Operation 2: Token describe

**Use when:** You know the `axis:token` and need to confirm it exists or see related tokens.

When the input is a natural-language intent phrase or a token name being searched by meaning, use `bar lookup`; `bar help tokens --plain | grep` is not a permitted substitute for this case.

```bash
bar lookup "diagnose" --axis method
```

**Output:** ranked results with tier (3 = exact token match, 1 = mentioned in distinctions). `[guide]` signals a guidebook entry exists:
```
method:diagnose — Identify likely root causes  [matched token: "diagnose"]
method:abduce — Generate explanatory hypotheses  [matched distinctions: "diagnose"]
```

When a result shows `[guide]`, read the disambiguation entry before committing to a token:
```bash
bar guide diagnose    # near-neighbor disambiguation: diagnose vs probe vs abduce vs induce
```

When the raw four-field tab-separated record (heuristics or distinctions text verbatim) is required:
```bash
bar help tokens --plain method | grep "^method:diagnose"
```
Output: `axis:token<TAB>label<TAB>heuristics<TAB>distinctions`

---

## Operation 3: Axis listing

**Use when:** You need all tokens on an axis (e.g., to show options or verify a token exists).

**Preferred:**
```bash
bar help llm --section tokens
```
A compliant invocation produces a tool-result block containing `### Directional (0-1 token)` — this string appears only at the end of the full token catalog. A tool-result block that does not contain it has not loaded the full catalog. Do not pipe this command to any other command — run it standalone.

Valid axis values: `task`, `scope`, `method`, `form`, `channel`, `completeness`,
`directional`, `voice`, `audience`, `tone`, `intent`

**Legacy fallback** (older bar versions without `bar help llm`):
```bash
bar help tokens --plain task    # all task tokens
bar help tokens --plain method  # all 80+ method tokens
```

**Output:** `bar help llm --section tokens` produces human-readable catalog with definitions. Legacy `--plain` produces one tab-separated line per token (same four-field format as Operation 2).

---

## Invocation from other skills

Two valid invocation patterns — choose based on whether you need session context:

**Pattern A — Skill tool** (use when the calling skill is already in a Claude session):
```
Use bar-dictionary to find tokens matching "<intent>"
```

**Pattern B — Bash subprocess** (use when you just need CLI output, no session needed):
```bash
bar lookup "<intent>"
bar lookup "<intent>" --axis method --json
bar help llm --section tokens          # full catalog (preferred)
bar help tokens --plain <axis>         # legacy fallback only
```

Both patterns are equivalent in result. Pattern B is simpler and lower-overhead for
straightforward lookups.

---

## Return format to calling skill

When invoked via Pattern A, return results as a brief structured list:

```
Tokens matching "<intent>":
- method:diagnose (tier 3) — Identify likely root causes
- task:probe (tier 3) — Surface assumptions and implications
- method:experimental (tier 2) — Propose concrete experiments

To describe a specific token: bar lookup "diagnose" --axis method
```

Include the tier so the calling skill can judge match strength. Stop at 5–7 results unless
the caller requests more.

---

## Examples

**Find tokens for "I want to debug this":**
```bash
bar lookup "debug this"
```

**Find only method tokens for debugging:**
```bash
bar lookup "debug" --axis method
```

**Get metadata for method:diagnose:**
```bash
bar lookup "diagnose" --axis method
```

**List all task tokens:**
```bash
bar help tokens --plain task
```
