# Feature Backlog

<!-- ================================================================
LLM INSTRUCTIONS — read this section before doing anything else
================================================================

## What this project is

talon-ai-tools is a structured prompt construction system with three surfaces:

1. **Go CLI (`bar`)** — command-line tool for composing structured prompts using token axes
   (scope, method, form, channel, completeness, directional, task, persona).
   Source: `cmd/bar/main.go`, `internal/bartui2/`, `internal/barcli/`

2. **SPA (`web/`)** — Svelte web app for interactively building bar commands.
   Source: `web/src/routes/+page.svelte`, `web/src/lib/grammar.ts`

3. **Talon voice commands (`GPT/`)** — voice interface for using bar from Talon.
   Source: `GPT/gpt.talon`, `GPT/gpt-with-context.talon`, etc.

## Grammar system

The prompt grammar lives in Python (`lib/axisConfig.py`, `lib/staticPromptConfig.py`,
`lib/personaConfig.py`) and is exported to JSON for use by the CLI and SPA.

- **Grammar SSOT**: `lib/axisConfig.py` (axis tokens), `lib/staticPromptConfig.py` (task tokens),
  `lib/personaConfig.py` (persona tokens)
- **Token metadata schema**: `definition / heuristics[] / distinctions[]` — replaces old free-form
  `use_when` / `guidance` strings. ADR-0154 (task tokens) and ADR-0155 (axis tokens) complete in
  the Python SSOT and grammar JSON. Go TUI structs use `Heuristics` / `Distinctions` (ADR-0157).
- **Exported grammar**: `build/prompt-grammar.json` (canonical) and
  `internal/barcli/embed/prompt-grammar.json` (embedded in CLI binary)
- **SPA grammar**: `web/static/prompt-grammar.json` — must be kept in sync with `build/`

## Key operational commands

```bash
# Build CLI from source (for testing local changes)
go build -o /tmp/bar-new ./cmd/bar/main.go

# Export grammar from Python SSOT to JSON + embed
make bar-grammar-update

# Sync SPA grammar (run after bar-grammar-update)
cp build/prompt-grammar.json web/static/prompt-grammar.json

# Run all tests
make test

# Regenerate axisConfig from catalog (WARNING: can zero AXIS_KEY_TO_USE_WHEN — check git diff first)
make axis-regenerate-apply

# Run grammar check (verifies JSON is in sync with embed)
make bar-grammar-check

# Run all guardrails
make guardrails
```

## ADR pattern

New features go through an ADR in `docs/adr/`. Numbered sequentially (currently at ~0157).
Active work: **ADR-0113** (task-gap-driven catalog refinement, loop-24 complete, loop-25 pending).

## How to help with this backlog

- Pick an item and ask "how would we implement this?" to get a plan before touching code
- Mark items `[x]` when done, or move them to the parking lot if they become lower priority
- Add new ideas under the appropriate tier with a one-line rationale
- When implementing, create an ADR first for non-trivial changes

================================================================ -->

---

## Tier 1 — Highest impact, most foregrounded by current affordances

### ✅ SPA: Token search / filter across metadata
**What**: The per-axis filter input in each TokenSelector panel matches against token name, label,
description, `metadata.definition`, `metadata.heuristics[]` trigger words, and
`metadata.distinctions[]` (both the `token` name and the `note` text). Searching distinctions
enables cross-token discoverability: typing "sim" surfaces tokens whose distinctions mention "sim",
letting users find adjacent and contrasting tokens by similarity.
**Why it's Tier 1**: Same discoverability gap as `bar suggest`, on the SPA surface. Searching across
`heuristics[]` is especially high-value: trigger words like "analyze", "debug", "step by step" are
the natural vocabulary users bring.
**Shape**: Per-axis filter input above each token grid (existing input extended, not a new global
search box). Filters in real-time; non-matching tokens hidden. F7 test suite pins all inclusion/
exclusion rules and case-insensitivity.
**Implemented**: `web/src/lib/TokenSelector.svelte` `filtered` derived — 7-field match predicate.
Tests: `TokenSelector.test.ts` F7-1 through F7-7.

### ✅ CLI/TUI: Remove old `internal/bartui`, complete TUI2 migration (ADR-0157)
**What**: Delete `internal/bartui/` entirely and remove all remaining references. TUI2 is already
the recommended path (`bar tui2`); the old TUI is dead weight in the help string, test scaffolding,
and binary surface area.
**Also**: Rename `UseWhen string` field in TUI token structs (`bartui2/program.go`, `barcli/tui_tokens.go`)
to `Heuristics` — the field is already populated from `meta.Heuristics`; the name is a stale artifact
of ADR-0142. Update stale ADR-0142 comments in `help_llm.go` and `tui_tokens.go`.
**Why it's Tier 1**: Active maintenance debt — two TUI implementations creates confusion about which
to use and which to maintain. Tests reference `bartui` directly.
**Complexity**: Medium — needs test migration and help-string update, but no behavior change.

### ✅ ADR-0113 Loop-25 (validation)
**What**: Post-apply validation of the loop-24 persona voice/tone heuristics added to `help_llm.go`.
**Why it's Tier 1**: Active in-flight work — loop-24 edits landed but haven't been validated against
the eval rubric. Re-test T01–T05 (voice axis), T10–T13 (tone/team), T13 (adversarial carve-out).
**Shape**: Run eval loop per ADR-0113 protocol; target ≥4.5 mean.

---

## Tier 2 — High value, moderate implementation effort

### CLI: Shell completion (tab-complete token names)
**What**: `bar <TAB>` completes axis keys; `bar scope=<TAB>` completes valid tokens for that axis.
**Why Tier 2**: Daily friction for power users. The token list is machine-readable from the grammar;
shell completion is a known pattern in Go CLIs (cobra, etc.).
**Shape**: `bar completion bash` / `bar completion zsh` subcommand outputs completion script.

### ✅ CLI: `bar help tokens --plain` with heuristics and distinctions
**What**: Extended the one-token-per-line plain output to four tab-separated fields.
**Final format**: `task:probe\tSurface assumptions and implications\tanalyze,debug,...\tpull,fix`
- Field 1: `axis:slug`
- Field 2: label
- Field 3: comma-joined `heuristics[]` trigger words (intent-matching vocabulary)
- Field 4: comma-joined distinction token names (cross-reference "see also" list)
**Open question resolved**: Distinction token names (not note text) are included as field 4.
They act as a "see also" pointer for LLMs — finding `probe` via heuristics surfaces `pull,fix` as
related tokens to consider. Token names are precise canonical identifiers, not freeform text, so
false-positive risk is low. Note text remains excluded.
**Implemented**: `grammar.TaskHeuristics`, `grammar.AxisTokenHeuristics`,
`grammar.TaskDistinctionTokens`, `grammar.AxisTokenDistinctionTokens` accessors in `grammar.go`;
`renderTokensHelp` plain format in `app.go`; 5 tests in `app_test.go`.

### SPA: "Build a command" output panel
**What**: As the user selects tokens, show the resulting `bar` command in a copyable panel.
**Why Tier 2**: The SPA already renders the prompt (LLMPanel), but doesn't surface the equivalent
bar command string. Closing this loop lets SPA users take their composition back to the CLI or Talon.
**Complexity**: Low — `renderPrompt.ts` already has the state; needs a `renderCommand()` formatter.

### SPA: Selected token review panel
**What**: A persistent summary strip or collapsible panel showing all currently selected tokens
across all axes, with one-click deselect for each.
**Why Tier 2**: With 9 axes and chips scattered across the page, it's easy to lose track of what's
selected — especially when axis sections are collapsed or off-screen. A consolidated view closes
the "what have I built?" loop.
**Shape**: Fixed bottom bar or side panel listing `axis=token` pairs; click to deselect; mirrors
the bar command that would be generated.

### SPA: Persona page layout reformat
**What**: Redesign the persona section to give voice / audience / tone / intent (formerly "purpose",
now `intent`) clear visual hierarchy — currently the four axes are rendered similarly with no
affordance for which is primary.
**Why Tier 2**: Persona is the most compositionally complex section; the flat layout doesn't
communicate that `preset` collapses to voice+audience+tone+intent, or that overrides work per-key.
**Shape**: Preset selector at top; voice/audience/tone/intent as subordinate overrides below;
visual treatment distinguishing preset from axis-level selection.

### Cross-surface: Preset save / load / share
**What**: Save a named token configuration (all axes + persona) and reload it later; share as a
URL or short code; load a saved preset into TUI2.
**Why Tier 2**: Talon already has `{user.model} preset save/list` but it's Talon-only. SPA and
TUI2 have no save/load. A shared preset store (JSON file or URL-encoded) would let users move
configurations across all three surfaces.
**Shape**:
- SPA: save/load panel (localStorage + shareable URL with encoded state)
- TUI2: `--preset <name>` flag to load a named preset at launch; Ctrl+S to save
- CLI: `bar preset save <name> [tokens...]` / `bar preset load <name>` (subcommand may already
  exist — check `bar preset` in current help)

### TUI2: Clipboard shortcut for text fields
**What**: A keyboard shortcut (e.g., Ctrl+V or a dedicated key) that reads the system clipboard
and inserts it into the currently focused text field (Run Command, Subject).
**Why Tier 2**: Pasting doesn't work reliably in terminal UIs due to bracketed paste / readline
conflicts. A `bar tui2 --command "$(pbpaste)"` workaround exists but isn't discoverable.
**Shape**: Intercept a key in the focused input; call `pbpaste` (macOS) or `xclip`/`wl-paste`
(Linux) via subprocess; inject the result into the text model.

### TUI2: Out-of-order token editing
**What**: Allow users to navigate back to a previously completed axis stage and change their
selection without restarting from the beginning.
**Why Tier 2**: The stage-based flow is efficient for forward progression but makes it hard to
refine — changing `scope` after setting `method` currently requires restarting or manually editing
the command string. This is the biggest UX gap for iterative use.
**Shape**: A token summary sidebar (similar to the selected token review above) where clicking
any axis navigates back to that stage; or a non-linear mode where all axes are always accessible.

---

## Tier 3 — Good ideas, not yet time-sensitive

### Cross-surface: Token variation comparison ("compare mode")
**What**: Given a base command and a set of token variants on one axis, generate output that shows
how the response changes across variants — so the user can see what a token actually *does* rather
than reading its description.
**Two approaches (both worth supporting eventually)**:
- **A — Single comparison prompt** (simpler): Generate one prompt instructing the LLM to respond
  N times, once per token variant, labeled. The LLM simulates the contrast in a single call.
  Best for tokens with clearly distinct semantics; cheapest; the LLM's description of the difference
  may be more useful than the difference itself for tokens that are subtly distinct.
- **B — Parallel prompts** (more honest): Generate N independent bar prompts (one per variant),
  run them separately, display outputs side by side. Actual divergent responses rather than simulated;
  more expensive; better for testing tokens where the real output behavior is the question.
**Relationship to `bar shuffle`**: Shuffle already varies tokens, but randomly. Compare mode is
intentional — the user fixes the subject and varies exactly one axis dimension to isolate the effect.
**Relationship to ADR-0113**: Directly useful for loop evaluation — instead of manually constructing
eval tasks, generate a comparison prompt and see token effects empirically.
**Shape (CLI)**: `bar compare method=prioritize,explore,diagnose "my subject"` → emits Approach A
prompt by default; `--parallel` flag triggers Approach B (requires LLM runner).
**Shape (SPA)**: A "compare" toggle on an axis; selecting multiple chips enters compare mode and
shows a multi-pane output.
**Open question**: Start with Approach A (no additional infrastructure); Approach B needs a
prompt-runner layer that doesn't exist yet.

### CLI: `bar explain` command
**What**: Given a bar command, explain in plain English what each token does and why the combination
is or isn't well-formed.
**Shape**: `bar explain "scope=narrow method=prioritize form=table"` → per-token explanations + compatibility check.

### SPA: Side-by-side token comparison
**What**: Select two tokens on the same axis and see their `definition`, `distinctions[]`, and routing concept
side-by-side.
**Shape**: Click a "compare" toggle; selecting a second token opens a split view.
**Why Tier 3**: Useful for onboarding and token selection, but requires UI surface not currently present.

### Talon: Context-aware token suggestions
**What**: Detect the active application/context (e.g., editor vs. browser vs. terminal) and suggest
a default token configuration.
**Why Tier 3**: Ambitious — requires modeling which contexts map to which token profiles. The Talon
context system could support this, but it needs a mapping layer that doesn't exist yet.

### Grammar: Per-token concrete prompt examples
**What**: Each token in the grammar gets one illustrative example of a prompt that uses it effectively.
**Why Tier 3**: Complements `heuristics[]` and `definition` with a concrete case. High-value for
documentation and future `bar suggest` training data, but high-effort to author well across 150+ tokens.

### Grammar: Method axis audit — structure and factoring
**What**: A research task, not a feature. The method axis has grown to 78 tokens — the largest axis
by ~2.5× — and may have structural issues worth addressing before it grows further.
**Questions to answer before writing an ADR**:
- Are any tokens functionally duplicate? (e.g., does `analysis` overlap substantially with `diagnose`
  or `explore`? Does `simulation` overlap with `experimental`?)
- Is there a missing subcategory abstraction? Looking at the current 78 tokens, rough clusters emerge:
  _reasoning primitives_ (abduce/deduce/induce), _analytical frameworks_ (jobs, actors, mapping),
  _structural operations_ (split, meld, cluster, branch), _evaluative stances_ (prioritize, triage,
  adversarial), _domain lenses_ (product, operations, resilience). If these are genuinely distinct
  kinds of methods, a subcategory field might improve discoverability more than token pruning would.
- Should some tokens be retired in favor of combinations? Or are the current distinctions well-earned?
**Shape**: Start with a written analysis (can be an ADR context section); then decide: prune,
subcategorize, or leave as-is with better `distinctions[]` between similar tokens.

### SPA: History and undo/redo
**What**: Track token selection changes in a history stack; Ctrl+Z / Ctrl+Shift+Z to step through.
**Why Tier 3**: Useful for exploration ("what did I have before I swapped method?") but adds
meaningful state management complexity on top of Svelte's existing reactive state.
**Shape**: History array of snapshots; bounded depth (e.g., 20 steps); stored in memory only (not
persisted across page refresh).

### CLI: Custom tokens via YAML / config file
**What**: Allow users to define additional tokens in a local config file, which are merged into
the grammar at runtime.
**Why Tier 3**: Enables team-specific or project-specific tokens without forking the grammar.
**Open questions**: Schema design (how does a custom token declare its axis, description,
heuristics?); merge strategy (what if a custom token conflicts with a canonical one?); whether
this belongs in `~/.config/bar/tokens.yaml` or a project-level `.bar.yaml`.

---

## Parking lot — low priority or needs more thought

- `bar suggest` (CLI) — LLM-backed suggestion is already a skill; CLI-only version would either
  be a pipe-to-LLM formatter (thin wrapper over `bar help llm`) or heuristic matching against
  `heuristics[]` fields. Neither adds enough value over the existing skill.
- `bar validate` — check a command for incompatibilities before running (overlaps with existing
  conflict detection; worth doing once shell completion lands)
- Multi-turn prompt history in SPA — scroll back through previous prompts in the session
  (distinct from undo/redo — this is about replaying prior submissions, not reverting selections)
- Export grammar as interactive HTML (standalone, no server) — for sharing/embedding
- `bar diff` — compare two bar commands and explain what changes between them
- New catalog refinement processes — ADR-0113 loop program covers task-gap-driven refinement;
  unclear what additional process would systematically surface gaps not already caught by loops.
  Worth revisiting after loop-25 completes.
