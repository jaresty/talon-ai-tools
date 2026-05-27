# ADR-0237: Token Guidebook — Disambiguation Layer for Bar Tokens

**Status**: Proposed
**Date**: 2026-05-27

---

## Context

Bar's existing per-token help (`bar help token <slug>`) provides definition, heuristics, and
distinctions for individual tokens. This covers the "what does this token mean?" question but
leaves two gaps unaddressed:

1. **Near-neighbor disambiguation**: When two tokens on the same axis look similar (e.g. `dig`
   vs `narrow`, `sweep` vs `sense`), the existing `distinctions` field provides a one-directional
   "don't confuse me with X" note. It does not provide relational guidance in the form "use A
   when X, use B when Y" — content that requires both tokens to be in view simultaneously.

2. **Combination guidance**: When tokens from different axes interact in a non-obvious way
   (e.g. `sweep + fog` vs `sweep + dig` producing meaningfully different output shapes), there
   is no existing artifact for that interaction. The help system has no combination-level entries.

Users working in the SPA or CLI encounter the near-neighbor problem frequently at the moment of
token selection — they know they want something in the vicinity of a concept but can't resolve
which token to pick.

---

## Problem Statement

The `distinctions` field on a token record is single-token scoped and one-directional. It cannot
serve the "here are two tokens, when do you pick each one?" use case because that content belongs
to neither token alone. There is no existing artifact type for relational or combination-level
guidance, so this content has no home in the current grammar or help system.

---

## Decision

Introduce a **guidebook** — a curated layer of disambiguation content for bar tokens. The
guidebook has two entry types:

### Entry types

**Type 1 — Single-token disambiguation entry**
Covers near-neighbor pairs on the same axis. Content: "use token A when X; use token B when Y."
This is the higher-value entry type to build first. Each entry has a clear, bounded scope and
addresses the most common failure mode (picking the wrong token from a similar pair).

**Type 2 — Combination entry**
Covers multi-axis pairs or triples with non-obvious interaction behavior. Reserved for cases
where the emergent output of a combination is genuinely surprising and not derivable from
reading each token's definition in isolation. Several clusters have known high-value combination
entries and will be authored at launch alongside Type 1 entries (see §Initial content scope).

### CLI surface

A new top-level subcommand: `bar guide <token>`.

- Positioned alongside `build`, `help`, `lookup` in the CLI help index
- Returns the guidebook entry for the named token — specifically, the disambiguation entry
  covering that token and its near-neighbors
- Extensible to variadic args (`bar guide <token1> <token2>`) in a later phase when combination
  entries are authored
- Preferred over a `--guide` flag on `bar help token` because a top-level subcommand is
  discoverable without prior knowledge that the feature exists

### SPA surface

Each token chip in the axis selection panels gets a `?` icon as a secondary tap/click target.
The icon is present on **every token that has rich metadata** (definition, heuristics,
distinctions — which covers most tokens via ADR-0154/0155), not only tokens with guide entries.

This replaces and extends the existing hover meta-panel pattern, which had an existing pain
point: the panel could not scroll, so heuristics and distinctions were frequently cut off.

**Two-panel model:**

*Lightweight panel* — triggered by hovering a chip (desktop) or tapping the chip body (mobile):
- Token name, label, description (1–2 sentences)
- Select / Deselect button (mobile only)
- No heuristics, distinctions, or guide content

*Full reference panel* — triggered by clicking/tapping the `?` icon (all surfaces):
- Full definition prose
- Heuristics (trigger phrases)
- Distinctions (near-neighbor notes, existing per-token data)
- **Guide entries** (new disambiguation content where present)
- Composition: Works well with / Caution

**Rationale for the split:**
The hover panel's height is constrained and non-scrollable; it was already a pain point before
guide content existed. Moving rich content to an explicit `?` action gives users a way to access
it without fighting hover height limits, and gives guide content a clear, permanent home.

**Mobile interaction:**
- Tap chip body → lightweight panel (description + select button)
- Tap `?` icon → full reference panel (slide-up or inline sheet)

**Desktop interaction:**
- Hover chip → lightweight panel (description only, transient)
- Click `?` icon → full reference panel (persistent, scrollable)

The `?` icon appears on every token with metadata. Tokens without metadata (rare) show no icon.
Guide entries appear as an additional section within the full reference panel, after distinctions.

### Why not the review panel chip gutter

The review panel chips have a single committed tap action (deselect/toggle). Splitting a chip
into two tap zones (body=dismiss, icon=guide) crosses the existing structural grain of the chip
element and is geometrically implausible for small token labels on mobile at 44px touch target
sizing. The axis selection panel has no conflicting primary action on a secondary icon element.

### Initial content scope

The following clusters are known to produce user confusion and will have guidebook entries at
launch. This list is illustrative, not exhaustive — entries are authored as needed.

**Type 1 — Near-neighbor disambiguation (same axis)**

| Tokens | Confusion pattern |
|--------|------------------|
| `probe` vs `check` | Both involve evaluation; `probe` surfaces assumptions broadly, `check` evaluates against a named criterion |
| `probe` vs `fix` | `fix` is reformat; `probe` is analysis — superficially similar when debugging |
| `sim` vs `simulation` | `sim` = temporal scenario narration; `simulation` = thought experiment with feedback loops |
| `sim` vs `plan` | `sim` narrates what plays out; `plan` proposes steps to take |
| `analysis` vs `systemic` | `analysis` decomposes into parts; `systemic` reasons about the interacting whole |
| `analysis` vs `diagnose` | `analysis` describes structure; `diagnose` seeks causes |
| `thrust` vs `balance` | Both handle competing forces; `thrust` catalogs them, `balance` resolves them |
| `clash` vs `adversarial` | `clash` finds where existing structures conflict; `adversarial` stress-tests for failure modes |
| `grain` vs `robust` | `grain` finds where structure already propagates; `robust` reasons under deep uncertainty |
| `meld` vs `compare` | `meld` explores combinations and overlaps; `compare` evaluates alternatives against criteria |
| `fourfold` vs `sweep` | `fourfold` exhausts logical stances; `sweep` enumerates options without asserting any |
| `afford` vs `field` vs `systemic` | All model behavior at system level but from different frames |
| `verify` vs `check` vs `ground` | All involve correctness — different strength and mechanism |
| `abduce` vs `diagnose` vs `induce` | All generate explanations from evidence; different reasoning direction |

**Type 2 — Combination entries (multi-axis)**

| Combination | Why non-obvious |
|-------------|----------------|
| `probe + adversarial` | Together: structural analysis + stress-testing — the TDD/pre-mortem combination; individually they're close enough that users often pick one and miss the other |
| `probe + verify` | Surfacing assumptions + applying falsification pressure — natural pairing for auditing a claim |
| `systemic + simulation` | Systems thinking + scenario walkthrough — feedback loop exploration; easy to conflate with `systemic` alone |
| `thrust + converge` | Catalog competing forces, then narrow to a committed choice — the design decision sequence |
| `grain + converge` | Find real optionality, then eliminate illusory options — structural decision-making pair |
| `analysis + diagnose` | Decompose first, then seek causes — ordered correctly; reversed order produces confused output |
| `adversarial + inversion` | Stress-test + pre-mortem — both are failure-finding; combined they cover attack surface AND catastrophic outcome paths |

The sort-cluster analysis identified 14 additional confusion clusters beyond the initial seed
list above. Priority clusters for early guidebook entries:

- **Rigor family**: `verify` / `rigor` / `gate` / `ground` / `atomic` / `chain` — all impose
  correctness discipline but differ in mechanism; high confusion, high stakes
- **Fault-finding family**: `adversarial` / `inversion` / `fail` / `clash` / `drift` / `hollow`
  — all answer "what could go wrong?" but from different angles
- **Decision family**: `converge` / `pick` / `prioritize` / `release` / `grain` — all feel like
  "help me decide" but operate differently
- **Causal family**: `effects` / `grove` / `trace` / `orbit` / `systemic` / `simulation` —
  temporal and causal reasoning tokens that are easy to conflate

### Ongoing curation

Guidebook entries are living content. Two processes keep them current:

**1. Shuffle-driven discovery**
The `bar shuffle` command surfaces unexpected token combinations. Any shuffle session that
produces a combination where the output was surprising or the token choice was non-obvious is a
candidate for a new guidebook entry. Shuffle sessions run by developers or during ADR-0113-style
evaluation loops should include a step: "did any token choice require explanation that a guidebook
entry would have pre-empted?" If yes, file a new entry.

**2. Task-driven refinement (ADR-0113 loop integration)**
The ADR-0113 evaluation loop tests token routing. When a loop iteration surfaces a
misrouting — a task where the wrong token was chosen — the root cause is often a near-neighbor
confusion. These misroutings are the primary signal for new guidebook entries. The loop should
explicitly check: "is there a guidebook entry that would have prevented this misrouting?" If not,
one should be authored and the entry added before the next loop iteration.

Both processes produce entries in the same format; neither requires a separate ADR for individual
new entries. The guidebook entry set is maintained as a flat catalog alongside the grammar data.

### Discovery

Guidebook entries must be discoverable at the two moments of confusion: token selection and
intent search.

**`bar lookup` integration**
When `bar lookup "<intent>"` returns results, any token in the result set that has a guidebook
entry should surface a `kind=guide` result (or annotate the `kind=token` result with a
`has_guide: true` field). This signals to the user that disambiguation content exists before
they commit to a token.

**`bar guide` as a first-class command**
`bar guide <token>` is listed in `bar help llm` navigation output alongside `bar lookup` and
`bar help token`. It is not buried as a flag — it appears in the top-level command index.

**Skill integration**
The `bar-dictionary` skill (which resolves token intent to grammar entries) should check for
guidebook entries and surface them when the intent query matches a token that has one. Similarly,
the `bar-autopilot` skill should note when a chosen token has a near-neighbor with a guidebook
entry, so the agent can surface the disambiguation before committing.

**SPA `?` icon**
Described in §SPA surface above — conditional icon in axis selection panels, present only when
a guidebook entry exists for that token.

---

## Consequences

### Benefits

- Fills a gap that the `distinctions` field cannot: relational, bidirectional disambiguation
  between near-neighbor token pairs
- Places disambiguation content at the highest-value moment: the selection decision, not after
- Works on mobile (tap-only) without special-casing
- CLI subcommand is discoverable alongside existing commands; does not require knowledge of a
  flag on an existing command
- Conditionally rendered icon means tokens without guidebook entries are visually unaffected

### Risks and Mitigations

- **Risk**: `?` icon adds visual noise to the axis selection panels.
  Mitigation: the icon is small and secondary; it appears on all tokens with metadata (most
  tokens), so it becomes a consistent affordance rather than a sporadic signal.
- **Risk**: Touch target sizing on mobile for the `?` icon alongside a short token label.
  Mitigation: allocate a fixed icon zone of ≥44px regardless of label length; test on mobile
  viewport before shipping.
- **Risk**: Guidebook content authoring cost. Mitigation: initial scope is bounded to the
  clusters listed in §Initial content scope — high-confusion near-neighbor pairs and known
  high-value combinations. New entries are added incrementally as confusion patterns surface.

---

## Out of scope (this ADR)

- Guidebook content authoring format and storage schema — to be defined when implementation begins
- `bar guide <token1> <token2>` variadic CLI form — deferred; combination entries will initially
  be accessible via `bar guide <token>` on either token in the pair
