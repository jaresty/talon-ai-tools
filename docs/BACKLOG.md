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

New features go through an ADR in `docs/adr/`. Numbered sequentially (currently at ~0163).
Active work: **ADR-0113** (task-gap-driven catalog refinement, loop-24 complete, loop-25 pending).

## How to help with this backlog

- Pick an item and ask "how would we implement this?" to get a plan before touching code
- Mark items `[x]` when done, or move them to the parking lot if they become lower priority
- Add new ideas under the appropriate tier with a one-line rationale
- When implementing, create an ADR first for non-trivial changes

================================================================ -->

---

## Tier 1 — Highest impact, most foregrounded by current affordances

### ✅ TUI2: Extend token filter to search heuristics[] trigger words
**What**: In `bartui2/program.go`, extend the completion-matching predicate to include each token's
`heuristics[]` array alongside the existing slug/value/label checks. Currently users typing natural
intent vocabulary ("debug", "root cause", "assumptions", "compare") get zero results on task and
method stages. The data exists in the grammar; the filter just doesn't use it.
**Why Tier 1**: Highest-leverage single fix — root cause of token undiscoverability across all stages,
especially method (82 tokens) and task (11 tokens). The same fix is already shipped for the SPA
(`TokenSelector.svelte` 7-field match predicate). This is a missing wire to existing data.
**Shape**: Extend the fuzzy-match predicate in `program.go` to loop over `opt.Heuristics[]` alongside
slug/label. Add harness regression tests: filter "debug" on task → `probe` visible; filter "root cause"
on method → `diagnose` visible.

### ✅ TUI2: Move persona stages to end — task-first stage order
**What**: Reorder the TUI stage sequence to start at `task` rather than `persona_preset`. Move the
five persona stages (`persona_preset`, `intent`, `voice`, `audience`, `tone`) to after `directional`.
Currently a new user must skip 5 stages to reach the first decision they actually care about.
**Why Tier 1**: Task is used in 100% of bar commands; persona in a small minority. Traversal order
has no effect on prompt output order — bar assembles tokens in grammar order regardless of the order
stages are visited.
**Shape**: Reorder `stageOrder` slice in `bartui2/program.go`. Verify `advanceToNextIncompleteStage`
still works. Update snapshot tests. Consider a keyboard shortcut to jump directly to persona stages
for users who want them.

### ✅ TUI2: Fix back + re-select — replace semantics for single-capacity axes
**What**: When a user presses Back to a completed single-capacity stage (task, completeness, form,
channel) and selects a new token, the new selection should replace the existing one. Currently
`selectCompletion()` appends, silently failing — no error, no state change, stage doesn't re-advance.
The user must explicitly deselect before selecting, which is non-obvious.
**Why Tier 1**: Silent failure on correction is the most likely cause of user abandonment after a
misclick. The fix is small but the UX impact is high — users trust that Back means "undo this choice."
**Shape**: In `selectCompletion()`, check if the target category is already at single-token capacity;
if so, remove the old token before appending the new one, then re-trigger stage advance. Add harness
regression test: `select:fix` → `back` → `select:probe` → assert `selected.task == ["probe"]` and
stage advanced.

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

### ✅ CLI: Shell completion (tab-complete token names)
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

### ✅ SPA: "Build a command" output panel
**What**: As the user selects tokens, show the resulting `bar` command in a copyable panel.
**Why Tier 2**: The SPA already renders the prompt (LLMPanel), but doesn't surface the equivalent
bar command string. Closing this loop lets SPA users take their composition back to the CLI or Talon.
**Complexity**: Low — `renderPrompt.ts` already has the state; needs a `renderCommand()` formatter.

### ✅ SPA: Selected token review panel (ADR-0158)
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

### ✅ TUI2: Harness mode for LLM-driven UX exploration (ADR-0167)
**What**: A `--harness` flag for `bar tui` that skips terminal rendering and instead reads JSON
actions from stdin / writes JSON state snapshots to stdout. An LLM (or test) can navigate axes,
select tokens, and observe the TUI's visible state without a PTY.
**Why Tier 2**: The most direct path to discovering UX gaps — an LLM acting as a user will surface
friction that manual review and ADR-0113 eval loops only catch indirectly. Also enables automated
regression tests against the TUI's state machine.
**Implemented**: `bartui2.Harness` in `internal/bartui2/harness.go`; `--harness` flag in
`internal/barcli/cli/config.go`; `runTUI2Harness` loop in `internal/barcli/tui2.go`.
Actions: nav, select, deselect, filter, skip, back, quit. 17 tests.
**ADR**: docs/adr/0167-tui-harness-mode.md (Accepted)

### TUI2/Harness: Improvements to enable more accurate LLM-driven UX analysis
The following harness items are NOT direct user improvements — they improve the harness as an
analysis tool, making future LLM-driven UX exploration sessions more reliable. They are only worth
doing if they would lead to discovering human UX gaps that aren't already visible.

### TUI2/Harness: Token metadata in HarnessToken
**What**: Add `heuristics []string`, `description string`, and `routing_concept string` to
`HarnessToken` in `HarnessState.visible_tokens`, populated from the same `TokenOption` fields
already available in `tui_tokens.go`.
**Why Tier 2**: Without heuristics/description/routing_concept, an LLM choosing between semantically
similar tokens (e.g., `analysis` vs `diagnose` vs `probe`) has only the short label to go on —
the same information asymmetry this harness was built to eliminate for humans. This is the highest-
leverage single fix: it makes every subsequent exploration session more accurate.
**Shape**: Extend `HarnessToken` struct; populate in `Harness.Observe()` from `cat.Options[i]` fields.

### TUI2/Harness: `commit` action + `outcome` field (must-fix)
**What**: Replace `done bool` in `HarnessState` with `outcome string` (`""` | `"committed"` |
`"quit"`), and add a `"commit"` action type to `HarnessAction` that sets `outcome="committed"`.
**Why Tier 2**: Currently `done: true` is emitted only on `quit`, making it impossible to distinguish
successful command construction from abandonment. Exploration session results are uninterpretable
without this distinction.
**Shape**: Change `HarnessState.Done bool` → `HarnessState.Outcome string`; add `"commit"` case
in `Harness.Act()`. Update 17 existing tests. Breaking change to the JSON schema.

### TUI2/Harness: Stage state vocabulary in HarnessState (must-fix)
**What**: Add `stage_statuses map[string]string` (`"empty"` | `"completed"` | `"skipped"`) and
`stages_remaining int` to `HarnessState`.
**Why Tier 2**: An LLM driver can't tell which stages are optional, which are complete, or how many
remain. It may spend effort on optional persona stages or fail to notice it's already on the last
meaningful stage. Combined with A1 (metadata), this closes the two primary orientation gaps.
**Shape**: Compute from `h.m.tokensByCategory` and `stageOrder` in `Harness.Observe()`; mark
stages with at least one non-auto-filled token as "completed", explicitly-skipped stages as
"skipped", others as "empty".

### TUI2/Harness: Auto-fill tracking in HarnessState
**What**: Add `auto_fills_applied map[string]string` (stage → token key) to `HarnessState`,
populated whenever a selection triggers auto-fills on other axes.
**Why Tier 2**: When selecting a token triggers auto-fills, the LLM observes unexplained state
changes — the command_preview changes but the LLM can't attribute the cause. It may attempt to
select already-filled tokens and receive confusing errors.
**Shape**: Capture fills in `Harness.Act()` during the `"select"` case by comparing
`tokensByCategory` before and after `selectCompletion`; store in harness struct; clear on next action.

### TUI2/Harness: Persona path indicator in HarnessState
**What**: Add `persona_path string` (`""` | `"preset"` | `"custom"`) to `HarnessState`, set to
`"preset"` after a `persona_preset` selection, `"custom"` after any `intent/voice/audience/tone`
selection.
**Why Tier 2**: The stage order lists both paths sequentially but in the real TUI they are mutually
exclusive forks. An LLM that picks a preset then attempts to set individual voice/tone produces
conflicting state with no diagnostic signal.
**Shape**: Track in `Harness` struct; set on `select` action for the relevant stage categories.

### ✅ TUI2: Group method tokens by SemanticGroup in stage display
**What**: Use the existing `SemanticGroup` field (ADR-0144) to sort and visually group the 82 method
tokens in the TUI stage, rather than presenting them as a flat alphabetical list. First visible tokens
today are `abduce, argue, bias, calc` — none of the common-use methods.
**Why Tier 2**: Complementary to heuristics filtering (Tier 1 above). Filtering helps users who know
their intent; grouping helps users who are exploring. Even a sort-by-group (without visual headers)
would move `analysis, compare, diagnose` above `abduce`.
**Shape**: In `tui_tokens.go`, sort method options by `SemanticGroup` before alphabetical within group.
Optionally render a dim group-header separator line when the group changes. First: verify `SemanticGroup`
is populated in `prompt-grammar.json` for all method tokens.

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

### ✅ CLI: Heuristic-based suggestions on unrecognized token
**What**: When `bar build` fails to recognize a token, instead of a bare error, surface the
closest matching tokens by searching `heuristics[]` for the unrecognized word. For example,
failing on `"debug"` surfaces `task:probe — Surface assumptions and implications`.
**Implemented**: `searchByHeuristics()` + `heuristicMatch()` in `internal/barcli/build.go`;
covers task, all 6 constraint axes, and all 5 persona axes. Each suggestion shows
`axis:token — Label`. 9 tests in `TestHeuristicSuggestions`.

### ✅ CLI: `bar lookup` — search tokens by heuristics and distinctions
**What**: A subcommand that takes a free-text query and returns ranked matching tokens by
searching `heuristics[]`, `distinctions[]`, and `definition` fields across all axes.
**Shape**: `bar lookup "root cause"` → ranked `axis:token — Label` matches. `--axis` filter,
`--json` output. 4-tier ranking (exact heuristic > substring heuristic > distinction token name >
definition text), AND logic across words, cap 10. 13 tests in `lookup_test.go`.
**ADR**: docs/adr/0163-bar-lookup-subcommand.md (Accepted)

### User-defined token sets — decentralized token ownership (ADR-0169)
**What**: A phased mechanism for users to bring their own token sets, merge them with the
built-in grammar at runtime, and optionally share them. Four independently shippable phases:

- **Phase 1** (lowest cost): `BAR_EXTRA_GRAMMAR` env var / `extra_grammar` config key pointing
  to a single JSON file. Merged at load time; user tokens win on same-axis+key conflict.
- **Phase 2**: Config accepts a list of paths + `~/.bar/tokens/` scan directory. All `*.json`
  files merged alphabetically. Symlink-friendly; package-manager installable by convention.
- **Phase 3**: Optional `"namespace": "myorg"` field in token set JSON. Tokens addressable as
  `myorg:token` in `bar build`. Resolves collision without filesystem isolation.
- **Phase 4**: `bar add <url>` / `bar update` / `bar remove` — thin package manager fetching
  sets into the phase-2 directory with a `~/.bar/lockfile.json`.

**Precondition** (before phase 1): Stabilize the grammar JSON schema as a public contract and
document merge-order semantics in `docs/grammar-schema.md`.
**Why Tier 2**: Unlocks team/org/domain-specific vocabularies without PRs to this repo.
Phases 1–2 have low implementation cost and deliver the core value independently.
**ADR**: docs/adr/0169-user-defined-token-sets.md (Proposed)

---

## Tier 3 — Good ideas, not yet time-sensitive

### TUI2/Harness: Cross-axis composition hints in HarnessState
**What**: Add `cross_axis_hints` per selected token to `HarnessState` — a serialized version of
what `CrossAxisCompositionFor` returns: natural partner tokens and cautionary token pairs, keyed
by axis.
**Why Tier 3**: The real TUI's most valuable guidance is "this token pairs naturally with X, clashes
with Y." Removing it from the harness means LLM exploration misses the TUI's composition guidance
system entirely. Lower priority than token metadata (A1) because fixing A1 lets the LLM reason
from descriptions; hints amplify accuracy further.
**Shape**: Add `CrossAxisHints map[string]CrossAxisEntry` to `HarnessState`; populate in `Observe()`
by calling `opts.CrossAxisCompositionFor` for each selected token.

### TUI2/Harness: Command validity signal in HarnessState
**What**: Add `command_valid bool` and `validation_error string` to `HarnessState`, computed by
attempting `barcli.Build()` against the current token selection after each action.
**Why Tier 3**: An LLM that builds an invalid command (capacity exceeded, incompatible tokens)
receives no warning in `command_preview`. The harness silently reports a preview that would fail
on execution.
**Shape**: Call `Build(grammar, currentTokens)` in `Observe()`; set `CommandValid` and
`ValidationError` from the result. Requires passing `grammar` into `Harness`.

### TUI2/Harness: Cursor fidelity — track actual focused token
**What**: Track the cursor index in the `Harness` struct; fix `HarnessState.focused_token` to
report the actually-focused token rather than always `visible[0]`; add a `"focus"` action to move
the cursor to a named token.
**Why Tier 3**: Exploration tests meant to detect "user can't find a token via keyboard navigation"
are invalid if `focused_token` always reports the first visible token. The harness overstates
discoverability for tokens that appear late in the list.
**Shape**: Add `cursorIndex int` to `Harness`; update `focused_token` in `Observe()`; add `"focus"`
case in `Act()` that finds a token by key and sets the cursor index.

### TUI2/Harness: `inspect` action for non-destructive token metadata lookup
**What**: Add an `"inspect"` action that returns token metadata (heuristics, description,
distinctions) without modifying selection state.
**Why Tier 3**: Mitigated by the token-metadata-in-HarnessToken fix (A1), which makes metadata
visible on every `Observe()`. Remaining value is for tokens not currently visible in the stage.
**Shape**: Add `"inspect"` case in `Act()`; add `InspectResult *HarnessToken` to `HarnessState`.

### TUI2/Harness: Transition metadata in HarnessState
**What**: Add `transition_from string` to `HarnessState` to record which stage was just exited
(set after `select`, `skip`, `back`, and `nav` actions; cleared after `Observe()`).
**Why Tier 3**: Useful for debugging multi-step LLM sessions and understanding auto-advance behavior
("TUI moved from task to completeness because task was just completed").
**Shape**: Set in `Act()` before model mutation; read and clear in `Observe()`.

### TUI2/Harness: Bulk-clear action for a stage
**What**: Add a `"clear"` action that deselects all tokens in the current stage (or a named stage
via `target`).
**Why Tier 3**: Workaround (multiple `deselect` actions) exists. Convenience for test scripts that
want to reset an axis without iterating token-by-token.
**Shape**: Add `"clear"` case in `Act()`; remove all non-auto-filled tokens for the target stage.

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

### Grammar: Eliminate duplicate definition storage in axisConfig.py
**What**: `lib/axisConfig.py` stores each method/scope/form/etc. token definition twice: once in a
flat string dict (~lines 217–330, used for prompt rendering) and once in the `AXIS_TOKEN_METADATA`
nested dict (~lines 3800+, used for `bar help tokens --plain` and the grammar JSON). These can
silently drift — editing one without the other produces prompts that disagree with the catalog.
**Why**: Discovered during structural-analysis-token audit (2026-03-17): melody, drift, and ground
definitions were updated in `AXIS_TOKEN_METADATA` but the rendered prompt text was unchanged until
the flat dict was also updated. The two-copy pattern is a latent SSOT violation.
**Shape**: Consolidate to a single source. Options: (a) drive prompt rendering from
`AXIS_TOKEN_METADATA["definition"]` directly, deprecating the flat dict; (b) generate the flat dict
from `AXIS_TOKEN_METADATA` at export time via `make bar-grammar-update`. Either way the grammar
export pipeline (`promptGrammar.py`) needs to be the join point.
**Precondition**: Audit which code paths read the flat dict vs `AXIS_TOKEN_METADATA["definition"]`
and confirm the two fields are always identical (or note where they differ).

### Grammar: Method axis audit — structure and factoring
**What**: A research task, not a feature. The method axis has 80 tokens — the largest axis
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

### ✅ Skills: `bar-dictionary` shared skill for token lookup
**What**: A standalone Claude skill that exposes token lookup by heuristics/distinctions, used
as a shared dependency by other bar skills (`bar-workflow`, `bar-autopilot`, etc.) instead of
each skill carrying its own inline explanation of what tokens mean.
**Why Tier 3**: Current bar skills embed token guidance in their own `skill.md` definitions,
which drift from the grammar SSOT. A `bar-dictionary` skill backed by `bar lookup` (or `bar help
tokens --plain`) would give all skills a single authoritative lookup path and remove the
duplication.
**Shape**: Skill that accepts a user intent phrase and returns matching tokens with definitions;
other skills call it via tool use or pipe rather than hardcoding token descriptions. Depends on
`bar lookup` landing first.
**ADR**: docs/adr/0164-bar-dictionary-skill.md (Proposed)

### SPA: History and undo/redo
**What**: Track token selection changes in a history stack; Ctrl+Z / Ctrl+Shift+Z to step through.
**Why Tier 3**: Useful for exploration ("what did I have before I swapped method?") but adds
meaningful state management complexity on top of Svelte's existing reactive state.
**Shape**: History array of snapshots; bounded depth (e.g., 20 steps); stored in memory only (not
persisted across page refresh).

### ~~CLI: Custom tokens via YAML / config file~~
Superseded by ADR-0169 (user-defined token sets). See Tier 2 entry below.

---

## Parking lot — low priority or needs more thought

- `bar suggest` (CLI) — LLM-backed suggestion is already a skill; CLI-only version would either
  be a pipe-to-LLM formatter (thin wrapper over `bar help llm`) or heuristic matching against
  `heuristics[]` fields. The heuristic path is now covered by `bar lookup` (ADR-0163) and the
  unrecognized-token fallback; neither adds enough value over those plus the existing skill.
- `bar validate` — check a command for incompatibilities before running (overlaps with existing
  conflict detection; worth doing once shell completion lands)
- Multi-turn prompt history in SPA — scroll back through previous prompts in the session
  (distinct from undo/redo — this is about replaying prior submissions, not reverting selections)
- Export grammar as interactive HTML (standalone, no server) — for sharing/embedding
- `bar diff` — compare two bar commands and explain what changes between them
- New catalog refinement processes — ADR-0113 loop program covers task-gap-driven refinement;
  unclear what additional process would systematically surface gaps not already caught by loops.
  Worth revisiting after loop-25 completes.
