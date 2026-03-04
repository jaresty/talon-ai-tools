# ADR-0151 – Cross-Boundary Architectural Concerns: Fragmentation & Emergent Patterns

Status: Accepted
Date: 2026-03-03
Owners: Architecture Review

## Context

This ADR documents the cross-boundary architectural concerns identified during a codebase analysis. The Talon AI Tools system is organized around two parallel axis hierarchies that govern AI model behavior:

| Contract Axes (model response) | Persona Axes (communication) |
|-------------------------------|------------------------------|
| `completeness`, `scope`, `method`, `form`, `channel`, `directional` | `voice`, `audience`, `tone`, `intent` |

These axes propagate across multiple boundaries:
- Python/Talon runtime (`lib/`, `GPT/`)
- Go CLI tools (`internal/barcli`, `internal/bartui`, `internal/bartui2`)
- Web UI (`web/`)
- Help system (`helpHub.py`, `helpDomain.py`)

The system also comprises four UI canvases (`ResponseCanvas`, `SuggestionCanvas`, `PatternCanvas`, `HelpCanvas`) that surface axis/persona information to users.

## Problem

Five architectural concerns emerged from the cross-boundary analysis:

### 1. Request State Triplication

Request lifecycle state is split across three modules with implicit relationships:

| Module | Responsibility | Consumer |
|--------|---------------|----------|
| `requestGating.py` | Predicate check: `request_is_in_flight()` | All canvases |
| `requestBus.py` | Event-driven state machine: `current_state()` | modelHelpers, streamingCoordinator |
| `modelState.py` | String tracking: `GPTState.last_request_id` | GPT module |

The relationship between these three is not formalized. Debugging request state requires tracing through all three locations.

### 2. Axis Import Path Duality

Two competing paths access axis configuration data:

```
axisConfig.py → axisMappings.py → consumers
axisConfig.py → axisCatalog.py → consumers
```

- `axisMappings` is a thin wrapper around `axisConfig`
- `axisCatalog` adds caching and Talon list merging

Both are used across 36+ import sites. Changes to `axisConfig` may not propagate consistently if one path is updated but not the other.

### 3. Persona Resolution Chain (Implicit Fallback)

The `_canonical_persona_value()` function in `GPT/gpt.py` (lines 270-329) implements a 5-level fallback chain:

1. `orchestrator.canonical_intent_key()` — via personaOrchestrator
2. `orchestrator.axis_alias_map` — via personaOrchestrator
3. `orchestrator.canonical_axis_token()` — via personaOrchestrator
4. `personaConfig.normalize_intent_token()` — direct personaConfig
5. `persona_docs_map()` — from personaConfig

This creates implicit priority that's difficult to debug when aliases conflict. The behavior depends on resolution order, not an explicit contract.

### 4. Canvas Coordination (Emergent Mutual Exclusion)

Each canvas (`ResponseCanvas`, `SuggestionCanvas`, `PatternCanvas`, `HelpCanvas`) independently manages its open/close lifecycle. Coordination happens via `overlayLifecycle.close_common_overlays()` — mutual exclusion rather than a central coordinator.

Shared patterns exist (request gating, overlay lifecycle, persona/intent display) but no shared base class formalizes this.

### 5. Go/Python Rigid Coupling

Communication between Go CLI and Python/Talon is entirely via subprocess:

```
Python (promptGrammar.py) → JSON grammar → Go (embedded at compile)
                              ↓
Talon voice commands ← subprocess ← "bar build ..."
```

- Grammar JSON is the sole shared artifact
- No runtime state sharing
- Changes to axis/persona require regeneration and recompilation

## Decision

This ADR documents the above concerns as awareness-raising. No immediate refactoring is mandated. The system functions correctly; these are architectural observations that may inform future decisions.

## Triage

Three concerns have externally validated causal chains; two are currently speculative.

### Validated (evidence exists)

**Axis import duality** is the highest-priority concern. The SSOT regression pattern is a known, recurring failure — `AXIS_KEY_TO_USE_WHEN` has been zeroed twice by tooling that updated one import path but not both. The two paths are not interchangeable: `axisMappings` is a token/mapping façade; `axisCatalog` adds caching and Talon list merging. Both are widely used (~10+ production import sites each), so the recommendation is not to collapse them but to add structural enforcement that prevents silent divergence.

The critical correction to the original framing: the problem is not the existence of two paths — it is the absence of guards that detect when a change to `axisConfig` propagates via one path but not the other. This is where mitigation should focus.

**Persona resolution chain** is validated by the loop-23 bug: a 5-level fallback silently selected the wrong alias (`"to ceo"` ≠ `"to CEO"`) with no observable error. The bug was found only by targeted test coverage. The causal chain is intact: multi-step resolution with implicit priority → silent wrong resolution → observable only through behavioral tests.

**Go/Python rigidity** is validated by ADR-0146: adding `routing_concept` required coordinated changes across `staticPromptConfig.py → axisCatalog.py → promptGrammar.py → grammar.go → tui_tokens.go → SPA`. The pipeline exists and is documented precisely because it has been traversed multiple times. Iteration friction is real.

### Speculative (no causal evidence)

**Request state triplication** and **canvas coordination** remain theoretical. No race condition or canvas coordination failure has been observed or cited. These do not warrant near-term action.

## Risks

| Concern | Evidence | Impact | Priority |
|---------|----------|--------|----------|
| Axis import duality | SSOT zeroed twice | Silent config drift | **High** |
| Persona resolution chain | loop-23 slug bug | Silent wrong alias | **High** |
| Go/Python rigidity | ADR-0146 pipeline pain | Slow iteration | **Medium** |
| Request state triplication | None | Latent race conditions | Low |
| Canvas emergence | None | Code duplication | Low |

## Recommendations

Future work (not mandated), ordered by evidence:

1. **Axis Drift Guard (ast-grep lint rule)** — The workspace has `ast-grep` available. A YAML rule can detect direct imports of `axisConfig` symbols that should route through `axisMappings` or `axisCatalog`, failing CI on violation. No such rule currently exists. This addresses SSOT regression without collapsing the two façade paths (which serve different purposes and are not candidates for consolidation).

2. **Persona Resolution Observability** — Add logging or assertion at each fallback level in `_canonical_persona_value()` (lines 270–329, `GPT/gpt.py`) that fires when a lower-priority fallback is taken. Pair with regression tests seeded from known conflict cases (e.g., proper-noun slug normalization). Does not require restructuring the fallback chain.

3. **Grammar Pipeline Checklist** — ~~Formalize the update sequence as a `make` target or CI check.~~ **Resolved (pre-existing):** `make bar-grammar-check` already validates all five consumer copies (`build/prompt-grammar.json`, `internal/barcli/embed/prompt-grammar.json`, `cmd/bar/testdata/grammar.json`, `cmd/bar/testdata/tui_smoke.json`, `web/static/prompt-grammar.json`) and runs in CI. The pipeline is also documented in `MEMORY.md`. No additional action required.

4. **Request State Consolidation** — Deferred. Revisit if a race condition is observed in practice.

5. **Canvas Base Class** — Deferred. Revisit if canvas coordination failure is observed in practice.

## Metadata

Analyzed: 2026-03-03
Method: Cross-boundary code analysis via agent exploration
Scope: lib/, GPT/, internal/, cross-module dependencies
