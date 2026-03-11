# ADR-0160: Method Axis Orthogonality Direction

## Status
Proposed — codifying the single-concept intent and concrete refactors

## Context
- ADR-0159 surfaced that many method tokens bundle multiple "prompt parts" (staging, governance, boundary, propagation, divergence, proof) which forces users into implicit bundles.
- The catalog goal is orthogonality: each token should contribute one structural responsibility so users can compose richer answers by mixing axes.
- New observations since ADR-0159:
  1. **Artifact vs operation** — many tokens combine "produce an artifact" (timeline, coupling sketch) with "reason about it."
  2. **Governing layer vs execution** — governance declarations (canonical loci, dependency rules) and the actions that satisfy them are often tied together.
  3. **Control vs monitoring loops** — sequential controls and their audit/feedback paths frequently live inside a single token.

This ADR captures the updated plan: split where needed, reassign some responsibilities to other axes, and prune low-value behavior rather than add unnecessary tokens.

## Problem Statement
1. Bundled method tokens (e.g., `trace`, `entangle`, `trade`, `branch`, `derive`) combine multiple operation families, making them hard to reuse orthogonally.
2. Some bundled behavior is accidental: a token might name a reasoning move *and* impose layout or governance details better handled by other axes.
3. Without explicit decomposition, guardrails (completeness, channel) have to reason about hidden requirements, increasing cross-axis churn.

## Naming Principle

Renaming tokens has a real discoverability cost. Users who learn a name build recall around it; arbitrary renames create churn without orthogonality benefit.

**Rule:** Keep existing token names when a token is being *narrowed* (description tightened, secondary responsibilities removed). Rename only when:
- One token splits into two, forcing disambiguation (e.g., `trace` narrows to narration; the new audit half needs a new name `mark`)
- The existing name actively misleads about the new semantics (e.g., `trans` implies "transition" but the new semantic is encode/decode/noise — `pulse` is clearer)
- The existing name is already opaque and a better one exists (e.g., `branch` → `spur`, `explore` → `sweep`)

**Applied consequences:**
- `trace`, `flow`, `verify`, `balance`, `polar` are narrowed — names retained
- `trans` → `pulse`, `trade` → `thrust`, `derive` → `forge`, `canon` → `root`, `branch` → `spur`, `explore` → `sweep`, `spill` → `seep` — renamed because semantics shift or names are opaque

## Orthogonality Strategy

### A. Reassign or Drop Non-Method Responsibilities
- **Form axis candidates**
  - `twin` (side-by-side comparison) → treat as a comparison form option rather than a method.
  - `prep`/`vet` (experiment write-ups) → extend `spike` or create a dedicated experiment form so that structure lives outside methods.
- **Scope axis candidate**
  - `dam` (containment boundary) → reframe as a "contain" scope modifier describing what remains in-bounds; method tokens (`snag`, `mesh`, `shear`) stay focused on detection/analysis.
- **Completeness axis candidate**
  - `grow` → move to completeness. Its instruction ("expand only when necessity is demonstrated") is a dynamic depth constraint, not a reasoning procedure. See Legacy Replacement Guidance.
- **Optional pruning**
  - If a secondary operation is rarely useful (e.g., dependency handoffs in `flow`), drop it instead of creating another token. Orthogonality is enforced by refusing multi-purpose descriptions, not by proliferating tokens.

### B. Artifact vs Operation Split
- **Artifact → form/channel**
  - Timeline or sequence diagrams referenced by `trace`/`flow` become form/channel presets (e.g., "timeline" layout). Methods keep only the reasoning verb.
  - Coupling sketches and containment maps move to form/channel names, leaving `snag`/`mesh` to analyze those artifacts.
- **Operation → method**
  - Method tokens narrow to a single reasoning move. Where one token covered both narration and auditing (e.g., `trace`), the narration half retains the name and the audit half becomes a new token (`mark`).

> **Blocking dependency:** The artifact→form/channel reassignment assumes form tokens for "timeline," "coupling sketch," and similar layouts will be defined. This work must be scoped before implementation of the artifact split is complete.

### C. Governing Layer vs Execution Split
- **Scope/persona metadata** retains declarations such as "this domain is authoritative," so tokens like `root`/`bind` can either move into metadata or stay as ultra-focused methods that assume the artifact already exists.
- **Execution methods** (`forge`, `verify`) operate against the declared governance layer but no longer describe the declaration itself.

### D. Control vs Monitoring Split
- Forward control (`trace`, `flow`, `pulse`, `thrust`, `spur`) and monitoring/audit (`mark`, `cull`, `verify`) become separate tokens. Channels/completeness can now gate them independently.

## Updated Token Outcomes

| Outcome | Tokens | Axis |
| --- | --- | --- |
| **Keep as method tokens (narrowed or new)** | `trace`, `mark` (new), `flow`, `pulse`, `snag`, `mesh`, `shear`, `seep`, `thrust`, `sift`, `balance`, `polar`, `spur`, `cull`, `sweep`, `root`, `forge`, `bind`, `verify` | Method |
| **Move to form** | `twin` (comparison layout), `prep` / `vet` (experiment write-up structure), timeline/coupling artifacts | Form |
| **Move to scope** | `dam` (contain boundaries) | Scope |
| **Move to completeness** | `grow` (dynamic depth constraint) | Completeness |
| **Drop** | `slot` (handoff), `toll` (impact scoring) — unless a compelling reuse case emerges | — |

## Method Token Definitions

| Token | Operation Family | Description |
| --- | --- | --- |
| `trace` | Staging | Narrate sequential control/data progression. (narrowed: excludes audit checkpoints) |
| `mark` | Audit | Capture checkpoints/evidence as the process runs. (new token for the audit half of former `trace`) |
| `flow` | Staging | Describe linear stage ordering without extra semantics. (narrowed: excludes handoffs) |
| `pulse` | Transmission | Model encode/decode/noise for information channels. |
| `snag` | Boundary detection | Surface coupled domains or seams. |
| `mesh` | Boundary analysis | Describe how coupling propagates and what it affects. |
| `shear` | Boundary mitigation | Outline separation or realignment steps. |
| `seep` | Spill detection | Identify scope creep or influence bleed. |
| `thrust` | Force mapping | Catalog opposing pressures/forces. |
| `sift` | Trade evaluation | Compare alternatives across explicit criteria. |
| `balance` | Equilibrium | Describe acceptable balance points/tolerances. (narrowed: excludes force cataloging) |
| `polar` | Attractor/repeller | Model how forces pull or push states. (narrowed: excludes equilibrium description) |
| `spur` | Divergence | Generate structured parallel hypotheses. |
| `cull` | Convergence | Evaluate/prune branches or experiments. |
| `sweep` | Exploration | Enumerate option space without evaluation. |
| `root` | Governance | Declare or reference the canonical locus (if not in metadata). |
| `forge` | Proof | Produce explicit constructive derivations. |
| `bind` | Dependency | Describe dependencies without executing proofs. |
| `verify` | Verification | Attach falsification pressure/tests only. (narrowed: excludes governance enforcement) |

## Simplification Benefits
1. **Reduced implicit bundles:** forms/scope capture artifacts and containment, leaving methods to express how to think.
2. **Cleaner guardrails:** channels/completeness reference artifact tokens directly; methods no longer smuggle structural requirements.
3. **Extensible metadata:** governance declarations can live in persona/scope metadata; methods merely reference them.
4. **Pruning path:** when secondary operations add little value, we drop them instead of creating redundant tokens.
5. **Lower relearning cost:** tokens narrowed in place preserve user recall; renames are limited to cases where the old name would actively mislead.

### Sample Combinations (for experimentation)
| Combo | Interpretation |
| --- | --- |
| `trace` + `mark` + timeline form | Narrate a process while logging checkpoints; the form renders a sequence diagram with evidence rows. |
| `snag` + `mesh` + `shear` | Detect coupled domains, explain how influence propagates, then propose mitigation steps. |
| `thrust` + `sift` + `balance` | Map opposing forces, evaluate options across criteria, and declare the acceptable equilibrium. |
| `spur` + `cull` + `verify` | Generate hypotheses, prune them, then run falsification tests on the survivors. |
| `sweep` + `twin` (form) + `sift` | Enumerate options, lay them out side-by-side, and score each against explicit criteria. |
| `pulse` + `cull` | Model channel transmission then audit the checkpoints where losses occur. |
| `forge` + `root` + `bind` | Produce a constructive derivation anchored to a canonical locus with explicit dependency wiring. |

## Next Steps
1. Define form tokens for timeline, coupling sketch, and similar artifacts before implementing the artifact→form split.
2. Update `axisConfig.py` with operation-family flags for all existing method tokens to identify actual overlaps.
3. Prototype the new tokens listed above (`mark`, `pulse`, `snag`, `mesh`, `shear`, `seep`, `thrust`, `sift`, `spur`, `cull`, `sweep`, `root`, `forge`, `bind`); simultaneously add form (`twin`, `prep`, `vet`) and scope (`dam`) entries.
4. Narrow existing tokens in place (`trace`, `flow`, `verify`, `balance`, `polar`) rather than replacing them; update descriptions only.
5. Refresh ADR-0159 after implementation to note which bundles became explicit forms/scope items and which behaviors were pruned.

### Legacy Replacement Guidance

Tokens not listed below are kept as-is on the method axis; their current descriptions satisfy orthogonality without modification.

| Original Token | Replacement Strategy |
| --- | --- |
| `grow` | Move to completeness axis. Its success criterion ("expand only when necessity is demonstrated") is a dynamic depth constraint, not a reasoning procedure — matching completeness semantics more than method semantics. The constraint is distinct from static brevity tokens (`gist`, `skim`): it starts minimal and allows justified expansion. Exploration/divergence coverage on the method axis passes to `sweep` and `spur`. |
| `trace` | Narrow to narration only; add new `mark` token for audit checkpoints. Name retained. |
| `flow` | Narrow to linear stage sequencing; retire `slot`. Name retained. |
| `trans` | Rename to `pulse` — semantics shift to encode/decode/noise channel model; "trans" implies transition rather than transmission. |
| `entangle` | Split into `snag` (detection) + `mesh` (analysis); add `shear` for mitigation where needed. |
| `spill` | Rename to `seep` (detection, more precise about gradual bleed); containment boundary moves to scope token `dam`. |
| `bound` / `sever` | Keep names; update descriptions to assume input from `snag`/`mesh`. |
| `trade` | Rename to `thrust` — force mapping is the primary operation; `trade` implied comparison which is `sift`'s role. Add `sift` for evaluation. |
| `balance` | Narrow to equilibrium/tolerance description. Name retained. |
| `polar` | Narrow to attractor/repeller modeling. Name retained. |
| `effects` / `grove` | No change; optionally reference `thrust`. |
| `branch` | Rename to `spur` — "branch" implies tree structure; "spur" better captures generating parallel hypotheses. Introduce `cull` for pruning. |
| `explore` | Rename to `sweep` — semantics shift to "enumerate without evaluating"; `cull`/`sift` handle evaluation. |
| `split` | Keep `split`; pair with form token `twin` for comparisons. |
| `experimental` | Shift structure to form tokens `prep` / `vet`; keep method only for reasoning aspects if required. |
| `derive` | Rename to `forge` — constructive derivation is clearer. Keep `root`/`bind` for canonical/dependency responsibilities. |
| `canon` | Rename to `root` — canonical locus is the core concept. `bind` handles dependency wiring. |
| `verify` | Narrow to falsification/testing only; governance enforcement remains with `ground`. Name retained. |

## Resolved Questions from ADR-0159

- **`grow` axis assignment**: Resolved — move to completeness. The depth-constraint semantics and direct contradiction with `max` both confirm it belongs there.
- **Method axis losing gradual expansion guidance after `grow` moves**: No — `sweep`+`spur` cover divergent exploration; "when to expand" is a depth constraint that belongs on completeness, not a reasoning procedure.
- **Which existing ADRs must be amended**: ADR-0159 (refresh after implementation); ADR-0104 (review for taxonomy alignment after renames); ADR-0147 (`grow`/`max` contradiction is now resolved by axis reassignment).

## Summary
- **Decompose** bundled methods into artifact+operation, governance+execution, control+monitor building blocks.
- **Reassign** artifact or containment behaviors to form/scope axes; `grow` to completeness.
- **Prune** low-value secondary responsibilities rather than multiplying the token set.
- **Name carefully**: narrow in place when possible; rename only when the old name would mislead.
- **Maintain orthogonality** by insisting every surviving token names exactly one reasoning move.
