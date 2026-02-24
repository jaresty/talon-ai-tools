# ADR 0144: Method Vocabulary Learnability — Category Tags, Starter Packs, and Hierarchy

**Date:** 2026-02-23
**Status:** Proposed
**Authors:** jaresty

---

## Context

The bar prompt grammar's method axis has grown to 50+ tokens. Each token is carefully defined and genuinely useful, so reducing the vocabulary is not the right answer. The problem is navigational: users cannot easily discover, differentiate, or recall the right tokens for a given task.

Specific dimensions of the problem:

- **Discovery gap**: The flat catalog exceeds comfortable working memory (~7±2 items). Users have no signal about which tokens are relevant before scanning the whole list.
- **Distinctiveness blur**: Semantically adjacent tokens (`explore`, `branch`, `abduce`) require reading precise definitions to differentiate at recall time. Users fall back to familiar tokens rather than the most appropriate one.
- **Composition opacity**: Appropriate 2–3 method combinations are a second-order skill with no built-in guidance. Which methods are complementary vs. redundant is not surfaced anywhere.
- **Entry-point mismatch**: Users arrive with a task framing ("I need to debug this") not a vocabulary framing. The system offers no mapping from task framing to relevant token families.
- **Opaque naming**: Compact tokens (`boom`, `grove`, `meld`, `melody`) don't self-document meaning. Even tokens that seem obvious (`flow`, `field`, `shift`) have specialized meanings.

The vocabulary is both the system's strength and its primary barrier to adoption. The goal is better navigation, not fewer tokens.

---

## Decision

We will address method vocabulary learnability in three phases. Phase 1 must ship before or alongside Phase 2, as Phase 1 category data informs starter pack documentation. Phase 3 is deferred pending empirical signal from Phases 1 and 2.

### Phase 1 (Immediate): Category tags in help output

Each method token gains a category placing it in one of ~8 semantic families. All ~50 method tokens must be assigned — the table below is representative; the authoritative and complete assignment lives in `AXIS_KEY_TO_CATEGORY` in `lib/axisConfig.py`.

**Proposed categories and representative tokens:**

| Category | Representative tokens |
|----------|----------------------|
| Reasoning | `deduce`, `induce`, `abduce`, `argue`, `verify`, `bias` |
| Exploration | `explore`, `branch`, `split`, `domains`, `boom` |
| Structural | `analysis`, `mapping`, `depends`, `canon`, `cluster`, `order` |
| Diagnostic | `diagnose`, `adversarial`, `risks`, `resilience`, `unknowns` |
| Actor-centered | `actors`, `afford`, `field`, `jobs` |
| Temporal/Scale | `flow`, `simulation`, `systemic`, `effects`, `rigor` |
| Comparative | `compare`, `contrast`, `balance`, `trade`, `polar`, `dimension` |
| Generative | `analog`, `models`, `reify`, `grove`, `grow`, `melody` |

Tokens that plausibly span multiple categories are assigned by primary use case. The assignment is editorial; contested placements are resolved by the authors and recorded in `AXIS_KEY_TO_CATEGORY`.

**Data architecture — follows existing metadata pattern:**

| Layer | Change |
|-------|--------|
| `lib/axisConfig.py` | New `AXIS_KEY_TO_CATEGORY: Dict[str, Dict[str, str]]` dict for the method axis. New `axis_key_to_category_map()` accessor. The existing `AxisDoc.group` field holds the resolved category string. |
| `prompt-grammar.json` | New `axes.categories` key (same shape as `axes.kanji` added in ADR-0143): `{ "method": { "<token>": "<category>" } }` |
| SPA `grammar.ts` | `Grammar.axes` gains `categories?: Record<string, Record<string, string>>` |
| `help_llm.go` | Token Catalog method section renders tokens grouped by category with section headers |

**Rationale:** Zero-cost to users (no new tokens, no behavior change), low implementation cost, immediately improves catalog navigation for both new and experienced users. Category data is the prerequisite for well-informed Phase 3 family token design.

### Phase 2 (Immediate, after Phase 1): Situational starter packs

Named bundles that map a task framing to a curated set of relevant tokens. Users invoke a starter pack to get a suggested `bar build` command rather than navigating the catalog.

**Naming constraints:**
- Single pronounceable word, no spaces or hyphens
- Must not conflict with any existing bar token name (task, scope, method, form, channel, directional)
- Must not conflict with any bar axis name (`scope`, `method`, `form`, etc.)
- Checked against the token registry at definition time

**Proposed initial starter packs:**

| Pack name | Task framing | Suggested `bar build` command |
|-----------|-------------|-------------------------------|
| `debug` | Diagnosing a bug or system failure | `bar build probe diagnose adversarial unknowns` |
| `design` | Architectural or interface design decision | `bar build show branch trade balance` |
| `review` | Code or document review | `bar build check adversarial risks verify` |
| `dissect` | Deep structural understanding of a system | `bar build probe analysis mapping depends` |
| `pitch` | Making a case to stakeholders | `bar build make argue trade analog` |
| `audit` | Compliance, quality, or consistency check | `bar build check verify canon rigor` |
| `model` | Scenario simulation or what-if analysis | `bar build sim simulation systemic effects` |
| `charter` | Planning a project or feature | `bar build plan branch prioritize risks` |
| `explain` | Explaining a concept or system to an audience | `bar build show analog actors jobs` |
| `compare` | Structured comparison between alternatives | `bar build diff branch trade polar` |

Note: `charter` is used instead of `scope` to avoid collision with the `scope` axis name.

**Token coverage:** Starter packs specify task and method tokens only. Scope, completeness, form, and channel are intentionally omitted — these are too context-dependent for a general-purpose default and should remain the user's choice after applying the pack.

**Starter packs are suggestions, not constraints.** The user receives a ready-to-run `bar build` command and can modify any token before running it.

**Data architecture:**

Starter packs are stored separately from usage patterns (`GrammarPattern`) because they have a different purpose (task-framing entry point vs. usage example) and a different shape.

| Layer | Change |
|-------|--------|
| `lib/starterPacks.py` | New file. `STARTER_PACKS: list[StarterPack]` where `StarterPack` is a dataclass with `name: str`, `framing: str`, `command: str`. Validated at import time: pack names checked against token registry and axis names. |
| `prompt-grammar.json` | New top-level `starter_packs` key: `[{ "name": "debug", "framing": "...", "command": "bar build ..." }]` |
| SPA `grammar.ts` | `Grammar` gains `starter_packs?: StarterPack[]` where `StarterPack = { name: string; framing: string; command: string }` |
| SPA `PatternsLibrary.svelte` | Renders starter packs as a separate section from usage patterns within the same component. Clicking a pack pre-fills token slots via the existing `onLoad` callback by parsing the `command` string. |
| TUI2 | No UI change in MVP. Users run `bar starter <name>` from the shell and paste the output into TUI2's command input. |

**`bar starter` CLI:**

`bar starter` is a new top-level subcommand (alongside `bar build`, `bar help`, etc.).

```
bar starter list              # Prints all pack names with one-line framings
bar starter <name>            # Prints the suggested bar build command, ready to copy or pipe
bar starter <unknown-name>    # Exits non-zero; prints "unknown pack '<name>'. Available: ..."
```

`bar starter <name>` output is a bare `bar build ...` command string with no surrounding text, so it can be piped directly: `$(bar starter debug) --subject "my problem"`.

**Rationale:** Meets users at their natural task-framing entry point. Doubles as living documentation of recommended token combinations. Low implementation cost; reuses existing SPA infrastructure.

### Phase 3 (Deferred): Two-tier method hierarchy

Once Phase 1 and 2 have been in use, introduce generic "family" tokens that alias to a sensible default sub-token. Users invoke a family name for breadth or a specific token for precision.

**Phase 3 prerequisites — all must hold before design begins:**
1. All method tokens have stable category assignments (no contested placements merged in the prior 90 days)
2. At least 5 distinct starter packs show active use (measurable via CLI invocation counts)
3. At least one user has explicitly requested family/alias tokens

**Family token design constraints (when Phase 3 begins):**
- Family token names follow the same single-word pronounceable constraint as starter packs
- Family names must not conflict with existing specific token names or axis names
- Each family token specifies its default sub-token and its member list explicitly (e.g., `reason` → default: `abduce`, members: `[deduce, induce, abduce, argue, verify, bias]`)
- Default sub-token selection rationale must be documented alongside the token definition
- Family tokens are valid anywhere a method token is valid; when combined with a specific sub-token from the same family (e.g., `reason verify`), the family token is ignored and the specific token takes precedence

**The hierarchy is deferred because** designing family boundaries before empirical category data is available risks encoding incorrect groupings, and this is a vocabulary change (new tokens) requiring more careful design than a navigation change.

---

## Rejected Alternatives

### Progressive disclosure tiers

Dividing methods into Tier 1 (basic), Tier 2 (intermediate), Tier 3 (specialist) and hiding non-Tier-1 tokens by default.

**Rejected because:** The tier assignment imposes editorial judgment about which methods are "basic" onto users who may legitimately need Tier 2/3 methods immediately. A user doing diagnostic work needs `diagnose` and `adversarial` from the start — these would be wrongly hidden. Tiers imply a skill hierarchy that doesn't reflect how tokens are actually used, and they create friction without proportional learnability benefit.

### Recommendation engine

A system that suggests contextually appropriate methods given a task token and scope selection.

**Rejected (for now) because:** Highest implementation cost. Requires good pairing data or heuristics that don't yet exist. Starter packs encode exactly that pairing data — if they prove valuable, the recommendation engine is the natural successor. Deferred, not permanently rejected.

---

## Exposure Points

Each phase must be surfaced consistently across all relevant interfaces.

### Phase 1: Category tags

| Surface | Change |
|---------|--------|
| `bar help llm` | Token Catalog method section groups tokens by category with section headers. Category name appears in each token row. |
| `bar help tokens` | Same category grouping applied to terminal-facing token list output. |
| SPA token catalog | Method tokens visually grouped by category; category label shown as a chip or section header. Users can filter/collapse by category. |
| TUI2 token picker | Method tokens rendered in category groups; category heading shown as a non-selectable separator row. |

### Phase 2: Starter packs

| Surface | Change |
|---------|--------|
| `bar starter list` | Lists all pack names with one-line framings. |
| `bar starter <name>` | Prints the suggested `bar build` command. Pipeable. Non-zero exit on unknown name. |
| `bar help llm` | New "Starter Packs" section after Token Catalog listing pack names, framings, and commands. |
| SPA | Starter packs rendered as a distinct section in `PatternsLibrary.svelte` (separate from usage patterns). Clicking pre-fills token slots. |
| TUI2 | No dedicated UI. `bar starter <name>` output is pasted into TUI2 command input. |

### Phase 3: Hierarchy family tokens

| Surface | Change |
|---------|--------|
| `bar build <family>` | Family tokens accepted as valid method tokens; resolve to default sub-token at prompt generation time. |
| `bar help llm` | Family tokens in Token Catalog with `→ default: <token>` and `family members: [...]` annotations. |
| SPA token picker | Family tokens shown as collapsible parents; expanding reveals member tokens. |
| TUI2 | Family tokens shown with expand indicator; selecting presents member tokens as a follow-up choice. |

---

## Success Criteria

**Phase 1:**
- All ~50 method tokens have assigned categories in `AXIS_KEY_TO_CATEGORY`
- `bar help llm` renders methods grouped by category (validated by test)
- SPA and TUI2 token pickers render category groupings

**Phase 2:**
- `bar starter list` and `bar starter <name>` work correctly for all 10 initial packs
- Starter packs appear in SPA `PatternsLibrary` as a distinct section
- CLI invocation counts for `bar starter` are measurable (instrumentation in place)
- Pack name conflict check runs at test time against the token registry

**Phase 3 gate (leading indicators for proceeding):**
- Stable category assignments (no contested placements in 90 days)
- At least 5 packs with measurable active use
- Explicit user request for family/alias tokens

---

## Consequences

**Positive:**
- New users have a navigable catalog (Phase 1) and task-framed entry points (Phase 2) without needing to learn the full vocabulary first
- Experienced users lose nothing — all tokens remain available, composition rules unchanged
- The category metadata pattern (`AXIS_KEY_TO_CATEGORY`) follows the established convention, minimising implementation surprise
- Starter packs are pipeable CLI output, making them composable with existing shell workflows
- Category data from Phase 1 informs Phase 3 hierarchy design with empirical evidence rather than armchair taxonomy

**Negative / risks:**
- Category assignments are editorial; some tokens plausibly belong to multiple families — contested placements require author resolution
- Starter packs can go stale as the method vocabulary evolves; they need maintenance when tokens are added or renamed
- Phase 3 family tokens introduce new vocabulary that must be named carefully to avoid conflicts with specific tokens and axis names
- Overly prescriptive starter pack suggestions could discourage users from exploring the full vocabulary

**Out of scope for MVP:**
- Talon voice wiring — the single-word naming constraint is preserved to keep this feasible later
- Recommendation engine — deferred pending starter pack pairing data
- Phase 3 hierarchy — deferred pending Phase 1/2 signal
