# ADR-0160: Method Axis Orthogonality Direction

## Status
Proposed — codifying the single-concept intent and concrete refactors

## Context
- ADR-0159 surfaced that many method tokens bundle multiple “prompt parts” (staging, governance, boundary, propagation, divergence, proof) which forces users into implicit bundles.
- The catalog goal is orthogonality: each token should contribute one structural responsibility so users can compose richer answers by mixing axes.
- New observations since ADR-0159:
  1. **Artifact vs operation** — many tokens combine “produce an artifact” (timeline, coupling sketch) with “reason about it.”
  2. **Governing layer vs execution** — governance declarations (canonical loci, dependency rules) and the actions that satisfy them are often tied together.
  3. **Control vs monitoring loops** — sequential controls and their audit/feedback paths frequently live inside a single token.

This ADR captures the updated plan: split where needed, reassign some responsibilities to other axes, and prune low-value behavior rather than add unnecessary tokens.

## Problem Statement
1. Bundled method tokens (e.g., `trace`, `entangle`, `trade`, `branch`, `derive`) combine multiple operation families, making them hard to reuse orthogonally.
2. Some bundled behavior is accidental: a token might name a reasoning move *and* impose layout or governance details better handled by other axes.
3. Without explicit decomposition, guardrails (completeness, channel) have to reason about hidden requirements, increasing cross-axis churn.

## Orthogonality Strategy

### A. Reassign or Drop Non-Method Responsibilities
- **Form axis candidates**
  - `twin` (side-by-side comparison) → treat as a comparison form option rather than a method.
  - `prep`/`vet` (experiment write-ups) → extend `spike` or create a dedicated experiment form so that structure lives outside methods.
- **Scope axis candidate**
  - `dam` (containment boundary) → reframe as a “contain” scope modifier describing what remains in-bounds; method tokens (`snag`, `mesh`, `shear`) stay focused on detection/analysis.
- **Optional pruning**
  - If a secondary operation is rarely useful (e.g., dependency handoffs in `flow`), drop it instead of creating another token. Orthogonality is enforced by refusing multi-purpose descriptions, not by proliferating tokens.

### B. Artifact vs Operation Split
- **Artifact → form/channel**
  - Timeline or sequence diagrams referenced by `trace`/`flow` become form/channel presets (e.g., “timeline” layout). Methods keep only the reasoning verbs (`stow`, `lane`).
  - Coupling sketches and containment maps move to form/channel names, leaving `snag`/`mesh` to analyze those artifacts.
- **Operation → method**
  - Method tokens become short, single-syllable verbs representing the reasoning move: `stow`, `merk`, `snag`, `mesh`, `shear`, `thrust`, `sift`, `spur`, `cull`, `root`, `forge`, `bind`, `try`.

### C. Governing Layer vs Execution Split
- **Scope/persona metadata** retains declarations such as “this domain is authoritative,” so tokens like `root`/`bind` can either move into metadata or stay as ultra-focused methods that assume the artifact already exists.
- **Execution methods** (`forge`, `try`) operate against the declared governance layer but no longer describe the declaration itself.

### D. Control vs Monitoring Split
- Forward control (`stow`, `lane`, `pulse`, `thrust`, `spur`) and monitoring/audit (`merk`, `slot`, `toll`, `cull`, `try`) become separate tokens. Channels/completeness can now gate them independently.

## Updated Token Outcomes

| Outcome | Tokens | Axis |
| --- | --- | --- |
| **Remain method tokens (single concept)** | `stow`, `merk`, `lane`, `slot`, `pulse`, `snag`, `mesh`, `shear`, `seep`, `toll`, `thrust`, `sift`, `stead`, `mag`, `spur`, `cull`, `sweep`, `root`, `forge`, `bind`, `try` | Method |
| **Move to form** | `twin` (comparison layout), `prep` / `vet` (experiment write-up structure) | Form |
| **Move to scope** | `dam` (contain boundaries) | Scope |
| **Drop** | Any secondary behavior deemed low value during implementation (e.g., dependency handoff if `slot` proves unnecessary) | — |

## Method Token Definitions (single-syllable)

| Token | Operation Family | Description |
| --- | --- | --- |
| `stow` | Staging | Narrate sequential control/data progression. |
| `merk` | Audit | Capture checkpoints/evidence as the process runs. |
| `lane` | Staging | Describe linear stage ordering without extra semantics. |
| `slot` | Boundary (control) | Specify how ownership transfers between stages. |
| `pulse` | Transmission | Model encode/decode/noise for information channels. |
| `snag` | Boundary detection | Surface coupled domains or seams. |
| `mesh` | Boundary analysis | Describe how coupling propagates and what it affects. |
| `shear` | Boundary mitigation | Outline separation or realignment steps. |
| `seep` | Spill detection | Identify scope creep or influence bleed. |
| `toll` | Spill impact | Score the consequence of that spill. |
| `thrust` | Force mapping | Catalog opposing pressures/forces. |
| `sift` | Trade evaluation | Compare alternatives across explicit criteria. |
| `stead` | Equilibrium | Describe acceptable balance points/tolerances. |
| `mag` | Attractor/repeller | Model how forces pull or push states. |
| `spur` | Divergence | Generate structured parallel hypotheses. |
| `cull` | Convergence | Evaluate/prune branches or experiments. |
| `sweep` | Exploration | Enumerate option space without evaluation. |
| `root` | Governance | Declare or reference the canonical locus (if not in metadata). |
| `forge` | Proof | Produce explicit constructive derivations. |
| `bind` | Dependency | Describe dependencies without executing proofs. |
| `try` | Verification | Attach falsification pressure/tests only. |

## Simplification Benefits
1. **Reduced implicit bundles:** forms/scope capture artifacts and containment, leaving methods to express how to think.
2. **Cleaner guardrails:** channels/completeness reference artifact tokens directly; methods no longer smuggle structural requirements.
3. **Extensible metadata:** governance declarations can live in persona/scope metadata; methods merely reference them.
4. **Pruning path:** when secondary operations add little value, we drop them instead of creating redundant tokens.

## Next Steps
1. Update `axisConfig.py` with operation-family flags for all existing method tokens to identify actual overlaps.
2. Prototype the new method tokens listed above; simultaneously add form (`twin`, `prep`, `vet`) and scope (`dam`) entries if they prove valuable.
3. Replace each legacy token in `axisConfig.py` with its new definition (rename or split) rather than keeping long-term aliases; this minimizes churn once users relearn the updated semantics.
4. Refresh ADR-0159 after implementation to note which bundles became explicit forms/scope items and which behaviors were pruned.

### Legacy Replacement Guidance

| Original Token | Replacement Strategy |
| --- | --- |
| `trace` | Rename to `stow`; add new `merk` token for audits. |
| `flow` | Rename sequencing behavior to `lane`; introduce `slot` only if dependency handoffs remain necessary (otherwise retire). |
| `trans` | Rename to `pulse`; depend on `stow` when narration required. |
| `entangle` | Replace with `snag`+`mesh`; add `shear` for mitigation where needed. |
| `spill` | Replace with `seep` (detection) + `toll` (impact) and add scope token `dam`. |
| `bound` / `sever` | Keep names but update descriptions to assume input from `snag`/`mesh`. |
| `trade` | Rename to `thrust`; add `sift` for evaluation. |
| `balance` | Rename to `stead` (or `thrust`+`stead`). |
| `polar` | Rename to `mag`. |
| `effects` / `grove` | No change; optionally reference `thrust`. |
| `branch` | Rename to `spur`; introduce `cull` for pruning. |
| `explore` | Rename to `sweep`; rely on `cull`/`sift` for evaluation. |
| `split` | Keep `split`; pair with form token `twin` for comparisons. |
| `experimental` | Shift structure to form tokens `prep` / `vet`; keep method only for reasoning aspects if required. |
| `derive` | Rename to `forge`; keep `root`/`bind` for canonical/dependency responsibilities. |
| `canon` | Rename to `root` (canonical) with `bind` handling dependency wiring. |
| `verify` | Rename to `try`; governance enforcement remains with `ground`. |

## Summary
- **Decompose** bundled methods into artifact+operation, governance+execution, control+monitor building blocks.
- **Reassign** artifact or containment behaviors to form/scope axes instead of cloning methods.
- **Prune** low-value secondary responsibilities rather than multiplying the token set.
- **Maintain orthogonality** by insisting every surviving token names exactly one reasoning move.
