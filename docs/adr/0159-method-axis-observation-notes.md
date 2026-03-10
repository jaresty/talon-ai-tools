# ADR-0159: Method Axis Observation Notes (No Decisions)

## Status
Under observation — documenting signals only

## Context
- The method axis in `axisConfig.py` (@axisConfig.py#189-318) currently carries 90+ reasoning modifiers spanning structural, diagnostic, comparative, generative, and temporal semantics.
- Cross-axis guardrails (e.g., completeness vs directional, channel vs form) expose structural tensions: brevity-focused completeness tokens (`gist`, `skim`) conflict with compound directionals, and format-constrained forms (e.g., `commit`) override expansive method pushes (@axisConfig.py#1260-1446).
- Token `grow` is defined as “expand only when necessity is demonstrated” and presently lives on the method axis, yet ADR-0147 cross-axis notes highlight a direct contradiction between `grow` and completeness token `max`, implying `grow` behaves like a depth constraint (@axisConfig.py#1456-1474).

## Observations
1. **Method Clusters Behave Like Families**  
   - Reasoning primitives (abduce/deduce/induce/derive/calc) operate as transformations applied to an explicit premise set. They often require the same structural scaffolding the completeness axis already governs.  
   - Structural shapers (align/bound/canon/crystal/depends/preserve/reset/sever) describe topology manipulations rather than distinct reasoning procedures, hinting at derivable composites.  
   - Diagnostic stressors (adversarial/diagnose/gap/drift/entangle/perturb/triage/unknowns/verify) all rely on a declared-vs-observed duality; several can be expressed as parameterized stress-tests rather than unique methods.  
   - Exploration tokens (branch/explore/split/migrate/grow/boom/domains/experimental) largely differ by how much structural commitment is allowed, suggesting a shared “divergence budget” control.  
   - Temporal propagation tokens (flow/effects/grove/operations/systemic/trace/trans) stack naturally: once a temporal scaffold exists, multiple tokens collapse into metadata about sequence depth or observation checkpoints.

2. **Prompt “Parts” and Uses Are Encoded Inside Many Methods**  
   - `trans` forces explicit staging (source → encoding → channel → decoding → destination → feedback) and requires analysts to separate message vs signal and noise handling steps (@axisConfig.py#311-314).  
   - `trace` and `flow` insist on observable intermediate steps and control/data movement, effectively decomposing responses into step logs rather than final summaries (@axisConfig.py#247-309).  
   - `ground` defines a governing layer (tests/acceptance criteria) that every structure must satisfy, introducing a persistent “intent vs verification artifact” split (@axisConfig.py#250-253).  
   - `canon` names a single authoritative locus for each proposition, so responses must map duplicates back to a parent representation—shaping how evidence, rules, and dependencies are referenced (@axisConfig.py#213-218).  
   - `afford` distinguishes logical possibility, perceived action salience, and structural constraints, meaning prompts must discuss both environment design and actor-perceived options (@axisConfig.py#194-199).  
   - `entangle`, `spill`, and `bound` define how influence crosses or stays within boundaries, steering answers toward interface descriptions vs leakage analysis (@axisConfig.py#239-304).  
   - `migrate` mandates a staged transition path with dual compatibility periods, separating “current state,” “bridge,” and “target” sections within a single response (@axisConfig.py#265-268).  
   Together these tokens already specify internal response parts (stages, loci, governing layers, boundary treatments) independent of bundling proposals.

3. **Cross-Axis Entanglement is Under-Specified**  
   - Completeness brevity limits (gist/skim) already block multi-directional tokens but the guidance lives outside the method axis; similar enforcement is absent for method tokens that demand intermediate artifacts (e.g., `derive` needs explicit generative assumptions, `calc` needs executable steps).  
   - Channel/form overrides (commit+directional, recipe+channel, etc.) show the existing rule set treats format as dominant, yet the method catalog doesn’t encode which methods require expandable surfaces or embedded notation.  
   - `grow` vs `max` is the only method/completeness contradiction documented, implying other method tokens may also want completeness semantics but currently lack guardrails.

4. **Derivation Relationships Appear Reusable**  
   - `canon` ≈ `derive + depends + sever` (single source, explicit derivation, enforce edges).  
   - `gap + drift + ground` form a feedback loop: ground defines authoritative criteria, gap surfaces implicit declarations, drift tracks under-enforced conclusions.  
   - `trade + balance + polar` can be described as force-balancing with explicit attractor/repeller modeling.  
   - Temporal trio (`trace + flow + effects`) already resembles a template for observable propagation.

5. **"grow" Acts Like Completeness, Not Method**  
   - Instruction emphasizes *when to expand depth* rather than *how to reason*, matching completeness semantics (“disciplined minimalism”) more than procedural stance.  
   - Direct contradiction with `max` is phrased as a completeness conflict (@axisConfig.py#1456-1474), not a method incompatibility, reinforcing that user expectations revolve around coverage depth.  
   - Other method tokens do not encode depth constraints; `grow` is the only one whose success criteria hinge on avoiding over-elaboration.

6. **Latent Bundle-Like Patterns**  
   - `USAGE_PATTERNS` in `axisConfig.py` (@axisConfig.py#1576-1599) already promotes multi-token packages (e.g., "Decision-Making" = branch + variants + thing, "Architecture Documentation" = analysis + case + struct) because those tokens each supply a different required prompt part (divergence logic, output comparison frame, scope lens). The combination reconstructs a complete reasoning workflow, so the catalog naturally presents them as a single unit.  
   - Cross-axis guidance such as the commit-form caution table (@axisConfig.py#1260-1343) and completeness vs directional warnings (@axisConfig.py#1387-1446) talks about token sets together precisely when their structural demands collide (e.g., multi-stage methods needing formats that can express intermediate steps). That interdependence between required prompt parts is why they appear bundle-like even without formal grouping.

7. **Cross-Axis Propagation Concerns**  
   - Methods that demand explicit staging (trans, migrate, trace) inherit requirements on form/channel axes (need surfaces that can show intermediate checkpoints or dual-state tables).  
   - Completeness tokens implicitly set the maximum number of prompt parts; e.g., gist cannot support the six-stage `trans` breakdown without losing fidelity, suggesting completeness should gate which methods are selectable.  
   - Directional compounds (fig/bog/dip*) expect both abstract and concrete parts; when paired with methods that already enforce multi-stage outputs, the prompt risks exploding into contradictory instructions without tool support.

8. **Implications of Updated Observations**  
   - The catalog already encodes micro-structures (governing layers, canonical loci, staged migrations); bundling or reclassification work should respect these intrinsic “prompt parts” instead of flattening them into high-level themes.  
   - If `grow` moves to completeness, method-axis guidance would rely more heavily on these part-defining tokens to keep responses organized—strengthening the case for derivation metadata and capability flags.  
   - Future ADRs that introduce decisions should call out how each change affects the mapping between methods and their expected internal sections so downstream tooling remains coherent.

9. **Operation Families Emerging from Current Tokens**  
   - *Staging & Transmission:* `trans`, `trace`, `flow`, `migrate`, `simulation` all impose multi-stage narratives (source→encoding→channel, current→bridge→target, scenario playback). Their prompts already expect discrete sections for checkpoints and evolution.  
   - *Governance & Canonicalization:* `ground`, `canon`, `derive`, `verify`, `depends` insist on governing layers, canonical loci, and explicitly traced derivations; analyses naturally split into “rules/tests vs structures vs proofs”.  
   - *Boundary & Influence:* `entangle`, `spill`, `bound`, `sever`, `align`, `afford` emphasize how responsibilities or affordances cross seams, so answers describe interior models, boundaries, leakage, and mitigation as separate parts.  
   - *Propagation & Force:* `effects`, `grove`, `operations`, `systemic`, `trade`, `balance`, `polar` frame systems through feedback loops or opposing pressures, calling for sections on forces, interactions, and equilibria.  
   - *Divergence & Exploration:* `branch`, `explore`, `split`, `grow`, `boom`, `domains`, `experimental` revolve around option-space expansion and experiment design, creating natural parts for hypotheses, branches, and evaluation criteria.  
   - *Transformative Reasoning:* `abduce`, `deduce`, `induce`, `calc`, `argue`, `probability`, `rigor` focus on premise sets, inference rules, calculations, and rebuttals; their prompts embed proof-like structures.  
   These families exist as observational groupings — they highlight operation types already present without proposing new taxonomy changes yet.

10. **Reasoning Motifs That Produce Bundle Behavior**  
    - Complementary operations: each promoted package covers a minimum set of reasoning moves (e.g., divergence → comparison → scoping) that together satisfy both the task intent and the cross-axis constraints; omitting one would leave part of the workflow unsupported.  
    - Guardrail-driven co-selection: cross-axis cautions (channel/form/completeness) force certain tokens to travel with others so structural requirements (multi-stage space, canonical proof slots, branch counts) are simultaneously satisfied.  
    - Shared intermediate artifacts: many methods demand the same intermediate artifacts (e.g., dependency graphs, option matrices, force diagrams); when multiple tokens reference the same artifact, the prompt effectively reuses that structure across them, making the set act like a pre-defined bundle even though it is built ad hoc.

11. **Orthogonality Intent (Single Concept per Token)**  
    - Target intent: each token should encode exactly one structural responsibility so users can compose them orthogonally.  
    - Misalignment signal: tokens that currently demand multiple operation types (e.g., both staging and boundary leakage analysis) reduce orthogonality and create implicit bundles.  
    - Observation linkage: the operation families above provide the axes along which to test whether a token needs decomposition—if it simultaneously occupies multiple families, it may warrant splitting into simpler parts.

## Open Questions
- What numbering or naming scheme should new completeness or bundle entries follow to maintain ADR consistency?  
- How should UI surfaces display bundle relationships without overwhelming users already tracking axis tokens?  
- If `grow` moves to completeness, does the method axis lose necessary guidance for gradual scope expansion, or do other tokens already cover that cognitive stance?  
- Which existing ADRs (e.g., ADR-0104, ADR-0147) must be amended if these observations evolve into decisions?

## References
- `axisConfig.py` method/descriptions @axisConfig.py#189-318  
- Cross-axis composition + completeness-method conflicts @axisConfig.py#1260-1474  
- ADR-0104 (Reference Key and Method Reclassification) for prior taxonomy shifts @docs/adr/0104-reference-key-and-method-reclassification.md#1-179
