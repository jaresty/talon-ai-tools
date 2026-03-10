# ADR-0160: Method Axis Orthogonality and Decomposition

## Status
Proposed — capturing orthogonality intent, motif clustering, and decomposition options

## Context
- ADR-0159 documented that many method tokens bundle multiple structural responsibilities (staging, governance, boundary, propagation, divergence, proof), leading to implicit bundles and cross-axis entanglement.
- The current taxonomy aspires to "single concept per token" so users can compose orthogonal prompts, but several tokens enforce multiple operation types simultaneously.
- Patterns already observed:
  - **Operation families** (staging/transmission, governance/canonicalization, boundary/influence, propagation/force, divergence/exploration, transformative reasoning) recur across `axisConfig.py` descriptions.
  - **Reasoning motifs** (complementary operations, guardrail-driven co-selection, shared intermediate artifacts) explain why certain tokens travel together.
  - **Orthogonality intent** now explicit: each token should encode one structural responsibility; overlapping tokens likely require decomposition.

## Problem
- Tokens such as `trace`, `entangle`, `trade`, `branch`, `experimental`, and `derive` currently combine multiple operation types (e.g., sequential staging + audit, seam detection + mitigation, force mapping + adjudication, divergence + evaluation).
- This coupling leads to multi-token recipes that feel unavoidable, reducing flexibility and making new combinations harder to reason about.
- Without a decomposition strategy, future additions risk worsening this implicit bundling, defeating the orthogonality goal.

## Motifs Driving Bundling
1. **Complementary operations** — e.g., branch → variants → scope, where each step supplies missing parts of a reasoning workflow.
2. **Guardrail co-selection** — cross-axis cautions force certain tokens to be paired when their structural needs collide (staging depth vs channel/form constraints).
3. **Shared intermediate artifacts** — multiple tokens require the same dependency graph, option matrix, or force diagram, making the set behave like a pre-defined bundle.

## Cluster A Focus — Decomposition of Multi-Operation Tokens (Overview)
- Goal: identify tokens that encode more than one operation type and split them into atomic replacements.
- High-priority candidates:
  - `trace` (staging narrative + audit logging)
  - `entangle`/`spill` (boundary leak detection + mitigation prescription)
  - `trade`/`balance`/`polar` (force enumeration + decision adjudication)
  - `branch`/`explore` (option generation + evaluation scaffolds)
  - `derive`/`canon` (proof generation + canonical locus enforcement)
- Decomposition should align each new token with exactly one operation family, so combinations remain orthogonal.

The remaining sections adopt single-syllable, pronounceable token names for each atomic concept. Mapping reference:

| New Token | Role | Former Working Name |
| --- | --- | --- |
| `stow` | stage narration | stage-trace |
| `merk` | audit checkpoints | audit-trace |
| `lane` | linear sequencing | sequence-flow |
| `slot` | dependency handoff | handoff-flow |
| `pulse` | channel encoding/decoding | channel-trans |
| `snag` | boundary coupling detection | detect-entangle |
| `mesh` | coupling analysis detail | analyze-entangle |
| `shear` | boundary mitigation | mitigate-entangle |
| `seep` | scope-creep detection | spill-detect |
| `toll` | spill impact scoring | spill-impact |
| `dam` | containment planning | spill-contain |
| `thrust` | force mapping | force-map |
| `sift` | trade-off evaluation | trade-evaluate |
| `stead` | decision equilibrium | decision-balance |
| `mag` | attractor/repeller modeling | polarize |
| `spur` | branch generation | diverge-branch |
| `cull` | branch pruning | prune-branch |
| `sweep` | option enumeration | option-explore |
| `twin` | compare decomposed parts | split-compare |
| `prep` | experiment design | design-experiment |
| `vet` | experiment evaluation | evaluate-experiment |
| `root` | canonical locus declaration | declare-canon |
| `forge` | constructive derivation | prove-derive |
| `bind` | dependency enforcement | enforce-depends |
| `try` | falsification evidence | verify-evidence |

## Concrete Decomposition (Cluster A)

### 1. Staging vs Audit (`trace`, `flow`, `trans`)

| Current Token | Embedded Responsibilities | Proposed Split | Resulting Behavior |
| --- | --- | --- | --- |
| `trace` | (a) Step-by-step transformation narration, (b) audit trail / verification checkpoints | `stow` (narrate control/data progression), `merk` (capture evidence + checkpoints) | Users can narrate process without implying audit artifacts, or attach audits to other methods without forcing stage narration.
| `flow` | (a) Control/data sequencing, (b) dependency transfer semantics | `lane` (linear stage articulation), `slot` (emphasize dependency transfer rules) | Sequencing orthogonal to governance of handoffs.
| `trans` | (a) Shannon-style channel modeling, (b) multi-stage staging | `pulse` (encode/decoding/noise modeling), reuse `stow` if stage narrative needed | Communication semantics separated from stage depth.

Artifacts: staging tokens require “sequence diagram / timeline” slots; audit tokens require “evidence table / checkpoints”. Channels/forms/completeness can now reason about each independently.

### 2. Boundary Detection vs Mitigation (`entangle`, `spill`, `bound`, `sever`)

| Current Token | Responsibilities | Proposed Split |
| --- | --- | --- |
| `entangle` | (a) Identify mixed domains, (b) describe coupling effects, (c) prescribe separation strategies | `snag` (surface coupled domains), `mesh` (detail interaction effects), `shear` (suggest boundary adjustments) |
| `spill` | (a) Describe scope creep, (b) evaluate risk, (c) propose containment | `seep`, `toll`, `dam` |
| `bound` / `sever` | Already emphasize enforcement; keep as “boundary enforcement” tokens once detection/analysis split off |

Result: user combines `detect-entangle` + `spill-impact` when they only need analysis, adding `mitigate-entangle` or `bound` when separation is desired. Each token now maps to a single operation family (detection vs governance enforcement vs mitigation planning).

### 3. Force Enumeration vs Adjudication (`trade`, `balance`, `polar`, `effects`, `grove`)

- **New tokens:**
  - `thrust` – catalog competing pressures / actors (propagation & force family).
  - `sift` – compare alternatives across explicit criteria without modeling forces.
  - `mag` becomes pure attractor/repeller modeling; adjudication handled by `stead`.

| Current | New Atomic Tokens | Notes |
| --- | --- | --- |
| `trade` | `thrust` + `sift` | `thrust` describes axes/pressures; `sift` handles scorecards/choices.
| `balance` | `thrust` + `stead` | Distinguish between visualizing equilibrium vs deciding tolerance.
| `polar` | `mag` (pure attractor/repeller description) + optional `thrust` | Removes comparison step from `polar`.
| `effects`/`grove` | remain propagation tokens but can optionally reference `thrust` when higher-order analysis needed |

### 4. Divergence vs Evaluation (`branch`, `explore`, `split`, `experimental`)

| Current | Responsibilities | Proposed Tokens |
| --- | --- | --- |
| `branch` | (a) generate parallel reasoning paths, (b) compare/prune | `spur` (generate structured hypotheses), `cull` (evaluate/prune branches) |
| `explore` | (a) enumerate option space, (b) highlight criteria | `sweep` (breadth-first listing), reuse `cull` or `sift` for comparison |
| `split` | (a) decomposition, (b) isolated analysis | Keep `split` as pure decomposition token; create `twin` if cross-analysis needed |
| `experimental` | (a) design experiments, (b) specify evaluation rubrics | `prep` (setups only), `vet` (criteria + next steps) |

This separation allows users to call only the generation half (diverge) or only the evaluation half (compare/prune), enabling orthogonal assembly with other method tokens.

### 5. Governance vs Proof Mechanics (`derive`, `canon`, `depends`, `verify`)

- Introduce tokens:
  - `root` – specify single authoritative locus.
  - `forge` – force explicit constructive derivation steps.
  - `bind` – describe dependency relationships without proofs.
  - `try` – attach falsification/tests only.

| Current | Embedded Ops | Resulting Split |
| --- | --- | --- |
| `derive` | (a) express generative assumptions, (b) link to canonical rule store | `forge` (derivation steps) + `root` or `bind` as needed |
| `canon` | (a) canonical store description, (b) dedup mapping, (c) dependency enforcement | `root` + `bind` |
| `verify` | (a) design falsification tests, (b) enforce governance layer | `try` (tests only), governance stays with `ground` |

### Resulting Structure

1. **Operation alignment:** each new token maps to exactly one operation family (staging, governance, boundary, propagation, divergence, proof). This enables a metadata table where every token sets a single flag.  
2. **Recipe clarity:** former bundle recipes (Decision-Making, Architecture Documentation) now reference atomic tokens (e.g., `diverge-branch` + `prune-branch` + `trade-evaluate`) making the composition explicit.
3. **Cross-axis constraints:** completeness/channel rules can target the new atomic tokens directly (e.g., `stage-trace` requires expandable channel; `audit-trace` requires completeness ≥ full), simplifying guardrails.
4. **Migration path:** existing tokens become aliases pointing to combinations of the new tokens during transition (e.g., selecting legacy `trace` inserts `stage-trace + audit-trace`).
5. **Optional pruning:** when a bundled token’s secondary responsibility offers low marginal value, drop that behavior instead of introducing a new token (e.g., keep `line` but retire `pass` if dependency handoffs rarely matter). This prevents token explosion while still enforcing single-concept semantics.

## Next Steps
1. Annotate each current token with operation-family flags to confirm decomposition targets.
2. Prototype the new atomic tokens in `axisConfig.py` with temporary aliases for backward compatibility.
3. Update ADR-0159 references once decomposition is finalized, documenting which bundles are now formal recipes instead of implicit behavior.

## Summary of Orthogonality Options
- **Cluster A (decomposition):** split multi-operation tokens into atomic staging, detection, propagation, divergence, or proof tokens (detailed above).
- **Cluster B (metadata):** record operation-type flags and artifact requirements per token so overlaps become explicit even before decomposition.
- **Cluster C (micro-axes/knobs):** introduce selectors for staging depth, boundary treatment, or force modeling to externalize multi-part responsibilities without adding tokens.
- **Cluster D (procedural severance):** define formal recipes/patterns so legacy multi-step behaviors are represented as compositions of atomic tokens rather than encoded inside a single token.
