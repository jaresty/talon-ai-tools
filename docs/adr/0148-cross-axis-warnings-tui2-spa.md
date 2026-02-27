# ADR 0148: Cross-Axis Composition Warnings in TUI2 and SPA

**Date:** 2026-02-26
**Status:** Proposed
**Authors:** jaresty

---

## Context

ADR-0147 introduced `CROSS_AXIS_COMPOSITION` — structured data capturing natural pairings and cautionary warnings for channel/form tokens. This data drives `bar help llm`'s "Choosing Channel" section for LLM users. ADR-0147 explicitly deferred:
> "Surfacing reframe descriptions in TUI2/SPA (would require new UI component)"

This ADR addresses that deferral. The gap is material: a user building prompts interactively in TUI2 or the SPA gets no warning when selecting `shellscript` + `sim`, while the same user consulting `bar help llm` sees the cautionary note. The same asymmetry applies to positive steering — nothing signals that `shellscript+make` is a natural pairing.

---

## Decision

### Surface activation model

Two surfaces, two different state requirements — made explicit here to prevent implementation divergence:

| Surface | Activation condition | State required |
|---------|---------------------|----------------|
| Meta panel natural section | Channel/form token in focus has `natural` entries in `CROSS_AXIS_COMPOSITION` | None (always-on) |
| Meta panel cautionary section | Channel/form token in focus has `cautionary` entries | None (always-on) |
| Direction-B warning (detail panel for task/completeness token) | Active selection contains a channel/form with a cautionary entry for this token | Selection state |
| Chip traffic light (TUI2 prefix / SPA chip indicator) | Active selection contains a channel/form token with entries for the browsed axis | Selection state |

The meta panel is **stateless** — a user can examine `shellscript` before any selection and always see its composition profile. The chip traffic light is **stateful** — it only activates when a relevant channel/form token is already committed.

### Chip traffic light scope

To avoid the SPA simultaneous-axes noise problem (all four non-technical audience chips showing ⚠ at once when `shellscript` is active), the chip traffic light activates for **task and completeness axes only** by default. Audience incompatibility warnings remain meta-panel-only. This scope can be revisited in Phase 3 based on observed usage.

### Part A: TUI2

**Always-on meta section** (selected-item detail in `renderTokensPane`, `program.go`):

For a channel/form token currently in focus: after the guidance line, add up to two structured lines from `CrossAxisCompositionFor()` data:
```
✓ Natural <axis>: token1, token2, ...   (useWhenStyle, cyan)
⚠ Caution: token — first sentence of warning   (warningStyle, amber)
```
If multiple cautionary entries exist, render all on separate `⚠` lines (one per cautionary token). Layout budget: truncate description to 2 lines (from 3) when either section is non-empty.

For a task/completeness token currently in focus (direction B): iterate all active channel/form tokens; for each, call `CrossAxisCompositionFor(axis, token)` and check if the current token appears in any `cautionary` map. If found, render:
```
⚠ With <channel>: first sentence of warning   (warningStyle, amber)
```

**Chip traffic light** (token list in `renderTokensPane`):

This step requires knowing the current browsing axis — available as the active category in TUI2's completions state. When an active channel/form token has entries for the current axis, render a one-character prefix on each token row. The prefix column is always present to avoid layout shift:
```
✓ make   — Create new content...        (natural partner)
⚠ sim    — Playing out a scenario...    (cautionary partner)
  show   — Surface what already exists  (neutral)
```
Scope: task and completeness axes only (matching the chip traffic light scope defined above). Skip prefix rendering for audience axis.

To handle multiple active channel/form tokens correctly: for each token row, iterate all active channel/form selections; if any has a `cautionary` entry for this token → show `⚠`; else if any has `natural` listing for this token → show `✓`; else blank. Cautionary takes precedence over natural.

Skip both meta sections and prefix column entirely if `paneHeight < 12`.

### Part B: SPA

**Always-on meta panel sections** (`TokenSelector.svelte`):

For a channel/form token chip that is clicked: after the "Notes" (guidance) section, add:
- **"Works well with"** section: natural partner tokens grouped by axis, rendered as non-interactive accent-tinted chips
- **"Caution"** section: cautionary pairs as `token — warning` lines with warning-background styling

**Chip traffic light** (`TokenSelector.svelte` chip grid):

Scope: task and completeness axes only (audience chips excluded — see above). When a channel/form token is active in the selection, apply CSS classes to chips in the task/completeness axis panels:
- `chip--natural`: subtle green left-border
- `chip--cautionary`: small `⚠` badge in top-right corner
- No class applied to neutral chips or audience chips

**Data pipeline — updated accessor signatures:**

`grammar.ts` additions:

```typescript
// For always-on meta panel: no selection state needed
getCompositionData(grammar: Grammar, axis: string, token: string)
  → { natural: Record<string, string[]>, cautionary: Record<string, Record<string, string>> } | null

// For chip traffic light: accepts full active selection to handle multiple active channel/form tokens
// Returns cautionary if any active channel/form has a cautionary entry for this chip token.
// Returns natural if any has a natural listing. Returns null if none match.
// Cautionary takes precedence over natural.
getChipState(
  grammar: Grammar,
  activeTokensByAxis: Record<string, string>,  // all currently selected tokens, keyed by axis
  chipAxis: string,
  chipToken: string
) → 'natural' | 'cautionary' | null
```

The `getChipState` multi-token signature resolves the single-active-token gap: it iterates all `channel` and `form` entries in `activeTokensByAxis` and merges results before returning.

### Part C: Guidance prose cleanup

After Parts A and B are live, trim `AXIS_KEY_TO_GUIDANCE` entries to intrinsic description only. Cleanup is scoped precisely: only remove cross-axis content that now has a structured home in `CROSS_AXIS_COMPOSITION`. Content with no structured destination (noted below) is retained.

| Token | Remove from prose | Keep in prose | Rationale |
|-------|------------------|---------------|-----------|
| `shellscript` | "Avoid with narrative tasks (sim, probe) and selection tasks... Audience incompatibility..." | "Shell script output. Delivers response as executable shell code." | Cross-axis content now in `cautionary` |
| `code` | "Avoid with narrative tasks (sim, probe)... Audience incompatibility..." | "Consists only of code or markup as the complete output." | Cross-axis content now in `cautionary` |
| `html` | "Avoid with narrative tasks (sim, probe)..." | "HTML markup output." | Cross-axis content now in `cautionary` (Tier 2) |
| `adr` | "Avoid with sort, pull, diff, sim..." + task-affinity list + form-as-lens rescue example | "Takes the shape of an ADR document with Context, Decision, and Consequences sections." | Task-affinity in `natural`; sim in `cautionary`; form-as-lens handled by Reference Key universal rule |
| `codetour` | "Best for code-navigation tasks: fix, make, show, pull..." + developer-audience note | "Delivered as a valid VS Code CodeTour JSON file." | Task affinity in `natural`; audience in `codetour.audience` |
| `gherkin` | "Primary use: make tasks..." + analysis-task reframe note | "Outputs only Gherkin Given/When/Then syntax. **Avoid with prose-structure forms (indirect, case, walkthrough, variants).**" | Task natural list replaces primary-use note; reframe covered by universal rule. **"Avoid with prose-structure forms" has no structured destination (no `gherkin × form` entry in `CROSS_AXIS_COMPOSITION`) — retain.** |
| `sync` | "Avoid pairing with max completeness..." | "Takes the shape of a synchronous session plan (agenda, steps, cues)." | Max cautionary in `sync.completeness` |
| `commit` | "Avoid deep or max completeness... and compound directionals..." | "Structures ideas as a conventional commit message." | Max/deep in `form.commit.completeness.cautionary`; compound directionals retained in separate directional guidance |

`generate_axis_config.py` must be updated with trimmed strings and regenerated.

### Part D: Coverage expansion

**Tier 1 — Extend existing channels to new axes:**

| Entry | Natural | Cautionary |
|-------|---------|-----------|
| `adr.task.cautionary` | — | `sim`: "tends to be incoherent — scenario playback is narrative; ADR is a decision artifact with no room for simulation output" |
| `adr.completeness` | `full`, `deep` | `skim`: "tends to produce incomplete decisions — ADRs need full context and consequences to be actionable" |
| `codetour.audience` | `to-programmer`, `to-principal-engineer`, `to-junior-engineer`, `to-platform-team`, `to-llm` | `to-ceo`, `to-managers`, `to-stakeholders`: "codetour produces a VS Code JSON file — inaccessible to non-technical audiences"; `to-team`: "accessible only to technical members" |
| `gherkin.completeness` | `full`, `minimal` | `skim`: "tends to produce incomplete scenarios — Gherkin steps need concrete action/assertion detail to be executable" |
| `sync.task` | `plan`, `make`, `show` | `sim`: "tends to be unfocused — scenario playback is narrative and doesn't produce a structured session agenda"; `probe`: "tends to miss the purpose — analytical probing doesn't translate into actionable session steps" |

**Tier 2 — New channels:**

| Entry | Natural | Cautionary |
|-------|---------|-----------|
| `presenterm.task` | `make`, `show`, `plan`, `pull` | `fix`: "tends to be too granular — code fixes don't translate into slide content"; `probe`: "tends to miss depth — analytical probing is hard to condense into slides" |
| `presenterm.completeness` | `minimal`, `gist` | `max`: "tends to be undeliverable — slides require brevity; max produces overloaded decks"; `deep`: "same constraint as max" |
| `html.task` | `make`, `fix`, `show`, `trans`, `pull`, `check` | `sim`: "tends to produce placeholder markup — simulation is narrative, not executable"; `probe`: "tends to miss analytical depth — valid only for narrow introspection scripts" |

**Tier 3 — Deferred:** `plain`, `remote`, `diagram`, `jira`, `slack`, `svg` — no empirical data. Form tokens (vast majority) — no strong composition constraints. `directional × form` — deferred per ADR-0147.

---

## Consequences

### Positive

- Pre-selection steering via chip traffic light (task/completeness axes) before a pairing is committed
- Proactive grammar teaching via always-on meta panel: composition profile visible on any channel/form inspection
- Single SSOT: `CROSS_AXIS_COMPOSITION` → `bar help llm`, TUI2, SPA (all three surfaces consistent)
- `bar help llm` "Choosing Channel" section automatically expands with Tier 1/2 entries — no additional work
- Guidance prose cleaned to intrinsic descriptions; cross-axis info is structural and consistent
- Symmetric: natural and cautionary both surfaced

### Risks

**R1 — TUI2 layout budget.** Natural + cautionary lines add 1–2 lines. Mitigation: truncate description to 2 lines when composition sections are non-empty; skip both if `paneHeight < 12`.

**R2 — SPA chip grid noise.** Resolved by design: audience chips excluded from chip traffic light. Task and completeness only. Audience incompatibilities surface in meta panel.

**R3 — Coverage asymmetry.** Channels without entries show no composition data. Users may infer no constraints exist. Mitigation: deferred to Phase 3 — add "universal rule applies" note to uncovered channel meta panels only if user confusion is observed. Premature addition would clutter every uncovered channel.

**R4 — Prose cleanup coordination.** Trimming prose before structured rendering is live removes guidance temporarily. Mitigation: Part C cleanup happens in Phase 2 step 3, only after meta panel rendering is verified end-to-end.

**R5 — `generate_axis_config.py` regression.** Trimmed prose strings will be overwritten by a naive regen run. Mitigation: update `generate_axis_config.py` with trimmed strings as part of Phase 2 step 3 before running `make bar-grammar-update`.

---

## Implementation Plan

### Phase 1a: Coverage expansion data

1. Add Tier 1 + Tier 2 entries to `CROSS_AXIS_COMPOSITION` in `lib/axisConfig.py`
2. Update `scripts/tools/generate_axis_config.py` to render the new entries
3. Run `make bar-grammar-update`
4. Verify: `go build -o /tmp/bar-new ./cmd/bar/main.go && /tmp/bar-new help llm | grep presenterm` — confirms `renderCrossAxisComposition()` picks up new entries automatically (side effect of grammar expansion)

### Phase 1b: TUI2 always-on meta sections

1. In `program.go` selected-item render: add natural + cautionary sections for channel/form tokens using `CrossAxisCompositionFor()` (direction A); add direction-B warning for task/completeness tokens (iterate active channel/form tokens)
2. Layout: truncate description to 2 lines when composition sections present; skip if `paneHeight < 12`
3. Test: extend TUI2 smoke fixture to cover natural/cautionary render paths

### Phase 1c: TUI2 chip prefix column

*(Separate step from 1b due to higher complexity: requires active-category context and per-row prefix logic)*

1. In `renderTokensPane`, when active category is task or completeness and an active channel/form token has entries for that axis: render one-char prefix column (`✓`/`⚠`/` `) on each completion row
2. Iteration: for each row token, check all active channel/form selections; cautionary takes precedence over natural
3. Test: extend TUI2 smoke fixture to cover prefix rendering; verify no layout shift for neutral tokens

### Phase 2: SPA always-on meta panel + guidance prose cleanup

1. `grammar.ts`: Add `CrossAxisComposition` type; implement `getCompositionData()` and `getChipState()` with the multi-active-token signature
2. `TokenSelector.svelte`: Add "Works well with" + "Caution" sections in meta panel for channel/form tokens; add `chip--natural`/`chip--cautionary` CSS classes for task/completeness chips from `getChipState()`
3. After rendering verified: trim `AXIS_KEY_TO_GUIDANCE` entries per Part C table; update `generate_axis_config.py`; run `make bar-grammar-update`; verify SPA meta panel still shows correct info from structured data
4. Test: all 110+ SPA tests pass; add cases for "Works well with" + "Caution" sections

### Phase 3: Noise evaluation + Tier 3 + G2 persistent warning

1. Observe audience chip noise in practice; if needed, evaluate extending traffic light to audience axis
2. Evaluate Tier 3 channel coverage based on ADR-0085 shuffle data
3. Evaluate persistent warning on selected-token strip for committed cautionary pairs (G2)
4. Add "universal rule applies" note to uncovered channel meta panels if confusion observed (R3)

---

## Deferred

- G2 persistent warning on selected-token strip — lower priority once chip traffic light is live
- R3 coverage-asymmetry note — implement only if user confusion observed (Phase 3)
- Tier 3 channel coverage — no empirical data yet
- `directional × form` cautionary entries (commit + compound directionals) — already in guidance prose
- `gherkin × form` incompatibility entry — would need new axis pair in `CROSS_AXIS_COMPOSITION`; currently retained in guidance prose ("Avoid with prose-structure forms")
