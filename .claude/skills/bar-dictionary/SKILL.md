---
name: bar-dictionary
description: >
  Shared token-lookup skill for bar. Accepts an intent phrase and returns ranked matching
  tokens from the live grammar using bar lookup and bar help tokens --plain. Use this
  skill instead of hardcoding token descriptions — it always reflects the current grammar.
  Call it when you need to find what token matches a user's intent, when you need the
  full metadata for a specific token, or when you need all tokens on an axis.
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

**Use when:** You have a user intent phrase and need to find matching tokens.

```bash
bar lookup "<phrase>"               # search across all axes
bar lookup "<phrase>" --axis method # restrict to one axis
bar lookup "<phrase>" --json        # structured output for programmatic use
```

**Output (human-readable):** one result per line, `axis:token — Label`, ranked by match quality.

```
task:probe — Surface assumptions and implications
form:prep — Experiment design write-up
method:diagnose — Identify likely root causes
```

**Output (--json):** array of objects with `axis`, `token`, `label`, `tier` (0–3),
`matched_field`, `matched_text`.

```json
[
  {
    "axis": "task",
    "token": "probe",
    "label": "Surface assumptions and implications",
    "tier": 3,
    "matched_field": "heuristics",
    "matched_text": "debug"
  }
]
```

**Tier meanings:** 3 = exact heuristic match, 2 = substring heuristic match,
1 = distinction token name match, 0 = definition text match. Higher tier = stronger signal.

**Multi-word queries use AND logic:** all words must match. Quote phrases:
```bash
bar lookup "root cause"         # matches tokens where both words appear
bar lookup "debug" --axis method  # debug-related method tokens only
```

---

## Operation 2: Token describe

**Use when:** You know the `axis:token` and need its full metadata (definition, heuristics,
distinctions).

```bash
bar help tokens --plain <axis> | grep "^<axis>:<token>"
```

**Example:**
```bash
bar help tokens --plain method | grep "^method:diagnose"
```

**Output:** tab-separated line with four fields:
```
method:diagnose	Identify likely root causes	what is causing this,root cause,...,debug this	abduce:abduce = generate competing hypotheses; diagnose = narrow to single most likely cause
```

Fields: `axis:token` | `label` | `heuristics (comma-separated)` | `distinctions (pipe-separated token:note pairs)`

---

## Operation 3: Axis listing

**Use when:** You need all tokens on an axis (e.g., to show options or verify a token exists).

```bash
bar help tokens --plain <axis>
```

Valid axis values: `task`, `scope`, `method`, `form`, `channel`, `completeness`,
`directional`, `voice`, `audience`, `tone`, `intent`

**Example:**
```bash
bar help tokens --plain task    # all task tokens
bar help tokens --plain method  # all 80+ method tokens
```

**Output:** one tab-separated line per token (same four-field format as Operation 2).

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
bar help tokens --plain <axis>
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

To describe a specific token: bar help tokens --plain method | grep "^method:diagnose"
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

**Get full metadata for method:diagnose:**
```bash
bar help tokens --plain method | grep "^method:diagnose"
```

**List all task tokens:**
```bash
bar help tokens --plain task
```
