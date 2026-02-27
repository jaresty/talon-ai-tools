# ADR 0148: Cross-Axis Composition Warnings in TUI2 and SPA

**Date:** 2026-02-26
**Status:** Proposed
**Authors:** jaresty

---

## Context

ADR-0147 introduced `CROSS_AXIS_COMPOSITION` — structured data capturing natural pairings and cautionary warnings for channel/form tokens. This data drives `bar help llm`'s "Choosing Channel" section for LLM users. ADR-0147 explicitly deferred:
> "Surfacing reframe descriptions in TUI2/SPA (would require new UI component)"

This ADR addresses that deferral and resolves three gaps identified during the gap analysis:

**G1 — SPA meta panel requires a click; warning arrives too late.** A user who recognizes `sim` by sight selects it without opening the meta panel, never seeing the cautionary note. The original ADR had chip badges as Phase 3 (deferred). The phase ordering was wrong: chip-level steering is the highest-value pre-selection surface.

**G2 — Meta panel only covers moment #2 (browsing), not moment #3 (after commit).** Once both `shellscript` and `sim` are selected, warnings disappear when focus moves. A persistent surface (selected-token strip or status bar) is not addressed.

**G3 — Natural pairings are invisible.** Warnings steer away from bad combos, but nothing steers toward good ones. The `natural` list in `CROSS_AXIS_COMPOSITION` already encodes this — it just isn't rendered anywhere.

**G4 — `CROSS_AXIS_COMPOSITION` coverage is too narrow for positive steering.** Current entries cover 6 channel tokens across 2 axes. Key channels (`presenterm`) and axis combinations (`codetour.audience`, `adr.completeness`, `gherkin.completeness`, `sync.task`, `html.task`) are absent, so the natural pairing lists that would drive steering are missing.

**G5 — Guidance prose redundancy.** `AXIS_KEY_TO_GUIDANCE` prose for channel tokens contains the same cross-axis avoidance text that `CROSS_AXIS_COMPOSITION` now encodes as structured data. The prose serves a different purpose (intrinsic description in meta panels) but is cluttered with cross-axis avoidance text that should be rendered structurally.

### Gap analysis — original ADR design

The original decision (meta-panel-only, contextual, Phase 1 TUI2 → Phase 2 SPA → Phase 3 chip badges) had:
- Correct direction (contextual is right for cautionary; always-on is right for natural)
- Wrong phase ordering for SPA (chip badge is higher-signal than meta panel for pre-selection)
- No coverage for positive steering
- No prose cleanup plan
- Underspecified direction-B implementation (checked in Decision, missing in Phase 1 steps)

---

## Decision

### Warning and steering model

**Always-on for natural pairings; always-on for cautionary pairings on channel/form tokens.**

When a channel or form token's meta panel or selected-item detail is open:
- Show **"Natural pairings"** — positive list of well-supported partner tokens (from `natural` list)
- Show **"Cautionary pairings"** — list of structurally-broken combinations (from `cautionary` dict)

No selection-state check is needed: the display is always-on for any channel/form token with entries. A user examining `shellscript` always sees "Natural task: make, fix, show, trans, pull" and "Caution: sim, probe." This teaches composition rules proactively, before any token is selected.

**Chip-level traffic light for partner-axis tokens when a channel/form is active.**

When a channel or form token is already in the selection and the user is browsing a partner axis (task, completeness, audience):
- Natural partner tokens get a **positive indicator** (subtle green tint or ✓ badge)
- Cautionary partner tokens get a **warning indicator** (⚠ badge)
- Unlisted tokens: neutral (no indicator; universal rule applies)

This is the primary pre-selection steering surface. It requires selection-state context but targets the moment just before a pairing is committed.

### Part A: TUI2

**Always-on meta section** (selected-item detail in `renderTokensPane`, `program.go`):

For a channel/form token currently in focus: after the guidance line, add two optional lines using structured `CrossAxisCompositionFor()` data:
```
✓ Natural: <axis>: token1, token2, ...   (using useWhenStyle, cyan)
⚠ Caution: token — first-sentence warning  (using warningStyle, amber)
```

For a task/completeness/audience token currently in focus: check if any active channel/form token has a cautionary entry for this token (direction B). If yes, add one amber line:
```
⚠ With <channel>: first-sentence warning
```

**Chip traffic light** (token list in `renderTokensPane`):

When a channel/form token is active, render a one-character prefix on each partner-axis token row:
```
✓ make   — Create new content...       (natural partner)
⚠ sim    — Playing out a scenario...   (cautionary partner)
  show   — Surface what already exists  (neutral)
```

The prefix column is always present (blank for neutral) to avoid layout shift.

**Layout budget:** Natural + cautionary lines in the detail section replace one line of description wrapping (truncate description to 2 lines when either section is non-empty, down from 3). No additional height needed.

### Part B: SPA

**Always-on meta panel sections** (`TokenSelector.svelte`):

For a channel/form token chip that is clicked: after the "Notes" (guidance) section, add:
- **"Works well with"** section: natural partner tokens as chips (non-interactive, colored with accent tint)
- **"Caution"** section: cautionary pairs as `token — warning` items with warning-background styling

**Chip traffic light** (`TokenSelector.svelte` chip grid):

When a channel/form token is active in the selection, the task/completeness/audience chip grid shows:
- Natural partner chips: subtle green left-border or background tint
- Cautionary partner chips: small ⚠ badge in top-right corner

**Data pipeline:**
1. `grammar.ts`: Add `CrossAxisComposition` to Grammar TypeScript interface; add `getCompositionData(grammar, axis, token) → { natural: Record<string, string[]>, cautionary: Record<string, Record<string, string>> } | null` accessor for always-on display; add `getChipWarning(grammar, activeAxis, activeToken, chipAxis, chipToken) → 'natural' | 'cautionary' | null` for traffic-light classification
2. `TokenSelector.svelte`: Always-on sections in meta panel; chip traffic-light classes from `getChipWarning()`

### Part C: Guidance prose cleanup

`AXIS_KEY_TO_GUIDANCE` entries for channel tokens contain cross-axis avoidance text that is now redundant with `CROSS_AXIS_COMPOSITION`. After Parts A and B are live, trim each affected entry to intrinsic description only:

| Token | Remove from prose | Rationale |
|-------|------------------|-----------|
| `shellscript` | "Avoid with narrative tasks (sim, probe) and selection tasks... Audience incompatibility..." | Now in `cautionary` dict |
| `code` | "Avoid with narrative tasks (sim, probe)... Audience incompatibility..." | Now in `cautionary` dict |
| `adr` | "Avoid with sort, pull, diff, sim..." and task-affinity list | Now in `natural` + `cautionary` |
| `codetour` | "Best for code-navigation tasks: fix, make, show, pull..." developer-audience note | Now in `natural` + `audience.cautionary` |
| `gherkin` | Cross-axis reframe note | Now in `natural`; universal rule handles reframes |
| `sync` | "Avoid pairing with max completeness..." | Now in `cautionary` |
| `commit` | "Avoid deep or max completeness... and compound directionals..." | Now in `cautionary` |

Cleanup happens in Phase 2 after structured rendering is live. `generate_axis_config.py` must be regenerated.

### Part D: Coverage expansion

Add entries to `CROSS_AXIS_COMPOSITION` to support positive steering and fill gaps identified during the gap analysis.

**Tier 1 — Extend existing channels to new axes (high confidence; derived from guidance prose):**

| Entry | Natural | Cautionary |
|-------|---------|-----------|
| `adr.task.cautionary` | — | `sim`: "tends to be incoherent — scenario playback is narrative; ADR is a decision artifact with no room for simulation output" |
| `adr.completeness` | `full`, `deep` | `skim`: "tends to produce incomplete decisions — ADRs need full context and consequences to be actionable" |
| `codetour.audience` | `to-programmer`, `to-principal-engineer`, `to-junior-engineer`, `to-platform-team`, `to-llm` | `to-ceo`/`to-managers`/`to-stakeholders`: "codetour produces a VS Code JSON file — inaccessible to non-technical audiences"; `to-team`: "accessible only to technical members" |
| `gherkin.completeness` | `full`, `minimal` | `skim`: "tends to produce incomplete scenarios — Gherkin steps need concrete action/assertion detail to be executable" |
| `sync.task` | `plan`, `make`, `show` | `sim`: "tends to be unfocused — scenario playback is narrative and doesn't produce a structured session agenda"; `probe`: "tends to miss the purpose — analytical probing doesn't translate into actionable session steps" |

**Tier 2 — New channels (commonly used, well-understood pairings):**

| Entry | Natural | Cautionary |
|-------|---------|-----------|
| `presenterm.task` | `make`, `show`, `plan`, `pull` | `fix`: "tends to be too granular — code fixes don't translate into slide content"; `probe`: "tends to miss depth — analytical probing is hard to condense into slides" |
| `presenterm.completeness` | `minimal`, `gist` | `max`: "tends to be undeliverable — slides require brevity; max produces overloaded decks"; `deep`: "same constraint as max" |
| `html.task` | `make`, `fix`, `show`, `trans`, `pull`, `check` | `sim`: "tends to produce placeholder markup — simulation is narrative, not executable"; `probe`: "tends to miss analytical depth — valid only for narrow introspection scripts" |

**Tier 3 — Deferred:**

`plain`, `remote`, `diagram`, `jira`, `slack`, `svg` — no empirical data from ADR-0085 cycles; low cross-axis constraint tokens. Form tokens (vast majority) — no strong composition constraints identified. `directional × form` (commit + compound directionals) — deferred per ADR-0147.

---

## Consequences

### Positive

- **Pre-selection steering** via chip traffic light: users see ✓/⚠ on chips before committing a pairing
- **Proactive grammar teaching** via always-on meta panel: natural + cautionary visible whenever a channel/form token is examined
- **Single SSOT** drives all surfaces: `CROSS_AXIS_COMPOSITION` → help_llm, TUI2, SPA
- **Guidance prose cleaned**: `AXIS_KEY_TO_GUIDANCE` entries become concise intrinsic descriptions; cross-axis info is structural
- **Symmetric treatment**: both positive (natural) and negative (cautionary) pairings are surfaced

### Risks

**R1 — TUI2 layout budget.** Natural + cautionary lines add 1–2 lines to the selected-item detail. Mitigation: truncate description to 2 lines (from 3) when these sections are non-empty. Skip both if `paneHeight < 12`.

**R2 — SPA chip grid noise.** Cautionary ⚠ badges on all four non-technical audience chips when `shellscript` is active may dominate the audience section. Mitigation: evaluate signal-to-noise during Phase 2 implementation; if too noisy, show only task/completeness chip indicators and keep audience warnings in meta panel only.

**R3 — Coverage asymmetry.** Channels with entries show natural/cautionary; channels without entries (plain, remote, etc.) show nothing. Users may incorrectly infer uncovered channels have no composition constraints. Mitigation: add a note to uncovered channel meta panels: "No specific pairing guidance — any task or completeness applies via the universal rule."

**R4 — Prose cleanup coordination.** Trimming `AXIS_KEY_TO_GUIDANCE` prose before structured rendering is live removes guidance from TUI2/SPA meta panels temporarily. Mitigation: strict Phase ordering — cleanup happens in Phase 2 only after structured rendering is verified.

**R5 — `generate_axis_config.py` regression.** Prose changes will be overwritten if `make axis-regenerate-apply` is run before updating the regen script. Mitigation: update `generate_axis_config.py` as part of Phase 2 before any regeneration.

---

## Implementation Plan

### Phase 1: Coverage expansion + TUI2 always-on display

1. Add Tier 1 + Tier 2 entries to `CROSS_AXIS_COMPOSITION` in `lib/axisConfig.py`; update `scripts/tools/generate_axis_config.py`; run `make bar-grammar-update`
2. TUI2 selected-item detail: add natural + cautionary sections in `program.go` using `CrossAxisCompositionFor()`; test with extended TUI2 smoke fixture
3. TUI2 chip prefix: render `✓`/`⚠`/` ` prefix column for partner-axis tokens when channel/form is active

### Phase 2: SPA always-on meta panel + guidance prose cleanup

1. `grammar.ts`: Add `CrossAxisComposition` type; add `getCompositionData()` and `getChipWarning()` accessors
2. `TokenSelector.svelte`: Add "Works well with" + "Caution" sections in meta panel; add chip traffic-light class from `getChipWarning()`
3. After structured rendering verified: trim cross-axis avoidance text from `AXIS_KEY_TO_GUIDANCE` entries per Part C table; update `generate_axis_config.py`; run `make bar-grammar-update`; verify meta panel still shows correct info from structured data

### Phase 3: Evaluate SPA chip noise + Tier 3 coverage

1. Observe signal-to-noise of chip indicators in real usage; adjust audience-axis chip display if noisy
2. Evaluate Tier 3 channel additions (plain, remote) based on ADR-0085 shuffle cycle data
3. Consider persistent warning on selected-token strip for committed cautionary pairs (addresses G2)

---

## Deferred

- G2 persistent warning on selected-token strip / status bar — useful but lower priority once chip traffic light is live
- Tier 3 channel coverage (plain, remote, diagram, etc.) — no empirical data yet
- `directional × form` cautionary entries (commit + compound directionals) — already captured in guidance prose; low priority
- "No pairing guidance" note on uncovered channel meta panels — implement after observing user confusion in practice
