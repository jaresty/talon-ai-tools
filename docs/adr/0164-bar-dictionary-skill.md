# ADR-0164: `bar-dictionary` — shared token-lookup skill for bar skills

**Status**: Proposed
**Date**: 2026-03-15

---

## Context

The bar skill ecosystem currently has three skills that require token knowledge to function:
`bar-autopilot`, `bar-workflow`, and `bar-manual`. Each embeds its own inline token guidance
in its `SKILL.md`:

- **`bar-autopilot`** and **`bar-workflow`** carry a full "Token Selection Strategy" section with
  embedded heuristics (e.g., "for debugging: look for method tokens about diagnosis") and
  fallback discovery logic. These heuristics duplicate — and can drift from — the `heuristics[]`
  field in the grammar SSOT.
- **`bar-manual`** documents specific tokens by name, which drift when tokens are renamed, retired,
  or semantically shifted.

The grammar SSOT already contains authoritative, structured token guidance:
- `heuristics[]` — trigger phrases that map user intent to token
- `distinctions[]` — cross-references to adjacent tokens
- `definition` — one-sentence description

`bar lookup` (ADR-0163) exposes this data as a ranked, queryable CLI command. `bar help tokens --plain`
provides a machine-readable full-axis dump. These are the authoritative lookup paths — but no skill
currently delegates to them. Skills carry their own copies instead.

The result: every grammar edit (new token, retired token, updated heuristic) must also be reflected
manually in each skill's SKILL.md. This never happens reliably.

---

## Decision

Create a `bar-dictionary` Claude skill at `.claude/skills/bar-dictionary/SKILL.md`.

The skill's purpose is narrow: **accept a token-selection query and return ranked results from the
live grammar**. It does not run `bar build`. It does not produce structured prompts. It is a lookup
primitive — a shared dependency that other skills call instead of maintaining their own token
knowledge.

### Operations

`bar-dictionary` exposes three operations, all backed by CLI tools:

**1. Intent lookup** — given a user intent phrase, return ranked token matches:
```
bar lookup "<phrase>" [--axis <axis>] [--json]
```
Example: `bar lookup "debug this"` → `method:diagnose`, `method:experimental`, `task:probe`, …

**2. Token describe** — given `axis:token`, return full metadata:
```
bar lookup "<token>" --axis <axis> --json
```
Combined with the grammar JSON or `bar help tokens --plain` to surface `definition`,
`heuristics[]`, `distinctions[]`, and label for a specific token.

**3. Axis listing** — return all tokens on an axis with labels and heuristics:
```
bar help tokens --plain <axis>
```
Output: tab-separated `axis:slug \t label \t heuristics \t distinctions` per line.

### Invocation contract

Other skills invoke `bar-dictionary` via the Skill tool:

```
Use bar-dictionary to find tokens matching "<intent>"
```

Or directly, when the calling skill's SKILL.md instructs Claude to run `bar lookup` as a
subprocess — either invocation pattern is valid. Skills choose based on whether they need a
full session context (Skill tool) or just a CLI result (Bash tool with `bar lookup`).

### Dependency chain

```
grammar SSOT (axisConfig.py, staticPromptConfig.py, personaConfig.py)
  └─► bar lookup (ADR-0163)  ←── bar-dictionary skill
        └─► bar help tokens --plain
```

`bar-dictionary` has no runtime dependencies beyond `bar` being installed. It does not require
`bar help llm` (that is the full-reference path for skills that run `bar build`).

### What moves out of existing skills

| Skill | What to remove | What replaces it |
|-------|---------------|-----------------|
| `bar-autopilot` | "Legacy Token Selection" heuristics section; embedded fallback axis heuristics | Reference `bar-dictionary` for any targeted lookup; `bar help llm` already covers the primary discovery path |
| `bar-workflow` | Same embedded heuristics sections as autopilot | Same replacement |
| `bar-suggest` | "Legacy Option Generation" fallback heuristics (scope/method/form lookup phrases) | Same replacement as autopilot/workflow |
| `bar-manual` | Any static enumeration of specific token names/descriptions | Instruct user to run `bar lookup` or invoke `bar-dictionary` |

The dynamic discovery sections (`bar help llm`, `bar help tokens --plain`) in existing skills
are **not** replaced — those are the runtime reference load paths and remain in place. Only
static, hardcoded token guidance is migrated.

### Migration approach

Migration is incremental. No existing skill breaks if `bar-dictionary` is not yet delegated to.
The skill can be created first; migration of each calling skill is a separate, low-risk edit.

Priority order:
1. Create `bar-dictionary` skill (this ADR)
2. Migrate `bar-manual` (most static token descriptions; highest drift risk)
3. Migrate `bar-autopilot`, `bar-workflow`, and `bar-suggest` "Legacy Token Selection" / "Legacy
   Option Generation" fallback sections (lowest urgency — fallback paths only, invoked when
   `bar help llm` is unavailable)

---

## Implementation notes

### Skill file

`.claude/skills/bar-dictionary/SKILL.md` — contains:
- Trigger: invoked when a skill or user needs to look up what token matches an intent, what a
  specific token means, or what tokens are available on an axis
- Workflow: map query type → CLI command → parse and return results
- Output contract: what format the skill returns to the calling skill

### Skill trigger description

```yaml
description: >
  Shared token-lookup skill for bar. Accepts an intent phrase and returns ranked matching
  tokens from the live grammar using bar lookup and bar help tokens --plain. Use this
  skill instead of hardcoding token descriptions — it always reflects the current grammar.
  Call it when you need to find what token matches a user's intent, or when you need the
  definition/heuristics for a specific token.
```

### Validation

The skill is correct when:
- `bar lookup "debug this"` returns `method:diagnose` in the top 3 results
- `bar lookup "root cause"` returns `method:diagnose` at tier 3 (exact heuristic match)
- `bar help tokens --plain method | grep diagnose` returns a tab-separated line with
  label and heuristics populated
- A calling skill that invokes `bar-dictionary` for token discovery does not carry any
  hardcoded token names in its SKILL.md

---

## Consequences

**Changes:**
- New `.claude/skills/bar-dictionary/SKILL.md` skill
- `bar-autopilot` SKILL.md: "Legacy Token Selection" fallback heuristics section removed or
  reduced to a pointer to `bar-dictionary`
- `bar-workflow` SKILL.md: same
- `bar-suggest` SKILL.md: "Legacy Option Generation" fallback heuristics section same treatment
- `bar-manual` SKILL.md: static token enumerations replaced with `bar lookup` invocation
- Backlog item "Skills: `bar-dictionary` shared skill for token lookup" marked complete

**Unchanged:**
- `bar-autopilot` primary discovery path (`bar help llm`) — not replaced
- `bar-workflow` primary discovery path — not replaced
- Grammar SSOT, CLI, grammar JSON — no changes
- All existing tests

**Enables:**
- Future skills can be written without any hardcoded token knowledge — they delegate to
  `bar-dictionary` and remain correct across grammar evolution
- `bar-dictionary` becomes the single integration point to update when the lookup interface
  changes (e.g., new `bar lookup` flags, schema changes in `--json` output)
