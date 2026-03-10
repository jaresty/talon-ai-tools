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

2. **Cross-Axis Entanglement is Under-Specified**  
   - Completeness brevity limits (gist/skim) already block multi-directional tokens but the guidance lives outside the method axis; similar enforcement is absent for method tokens that demand intermediate artifacts (e.g., `derive` needs explicit generative assumptions, `calc` needs executable steps).  
   - Channel/form overrides (commit+directional, recipe+channel, etc.) show the existing rule set treats format as dominant, yet the method catalog doesn’t encode which methods require expandable surfaces or embedded notation.  
   - `grow` vs `max` is the only method/completeness contradiction documented, implying other method tokens may also want completeness semantics but currently lack guardrails.

3. **Derivation Relationships Appear Reusable**  
   - `canon` ≈ `derive + depends + sever` (single source, explicit derivation, enforce edges).  
   - `gap + drift + ground` form a feedback loop: ground defines authoritative criteria, gap surfaces implicit declarations, drift tracks under-enforced conclusions.  
   - `trade + balance + polar` can be described as force-balancing with explicit attractor/repeller modeling.  
   - Temporal trio (`trace + flow + effects`) already resembles a template for observable propagation.

4. **"grow" Acts Like Completeness, Not Method**  
   - Instruction emphasizes *when to expand depth* rather than *how to reason*, matching completeness semantics (“disciplined minimalism”) more than procedural stance.  
   - Direct contradiction with `max` is phrased as a completeness conflict (@axisConfig.py#1456-1474), not a method incompatibility, reinforcing that user expectations revolve around coverage depth.  
   - Other method tokens do not encode depth constraints; `grow` is the only one whose success criteria hinge on avoiding over-elaboration.

5. **Opportunities for Structured Bundles**  
   - Introducing named bundles (e.g., ForceBalance, Structural Cartography, Temporal Diagnostics) could let individual tokens serve as parameters while the bundle encodes shared scaffolds.  
   - Bundles would map well to routing concepts and UI hints, simplifying discoverability without deleting legacy tokens.

## Options Under Consideration (No Decisions Yet)
1. **Rehome `grow` to completeness:** treat it as a depth modifier ("expand only as needed"), optionally adding a caution that conflicts with `max` remain explicit.  
2. **Layer method bundles/metatypes:** define reusable structures (ForceBalance, Structural Cartography, Temporal Diagnostic) so existing tokens reference them, improving derivability and reducing overlap without renaming tokens.  
3. **Encode derivation metadata:** allow axis config to specify when a method is equivalent to a composition of others (e.g., canon = derive + depends + sever) so tooling can suggest or auto-compose prompts.  
4. **Add method → channel/form/complete capability requirements:** declare minimum surface area (e.g., derive requires channels that can show intermediate structure; calc requires executable or pseudo-coded sections).  
5. **Introduce divergence budget controls:** unify branch/explore/split/migrate/grow signals into a shared parameter indicating how much structural commitment is allowed, keeping token names but clarifying their comparative roles.

## Open Questions
- What numbering or naming scheme should new completeness or bundle entries follow to maintain ADR consistency?  
- How should UI surfaces display bundle relationships without overwhelming users already tracking axis tokens?  
- If `grow` moves to completeness, does the method axis lose necessary guidance for gradual scope expansion, or do other tokens already cover that cognitive stance?  
- Which existing ADRs (e.g., ADR-0104, ADR-0147) must be amended if these observations evolve into decisions?

## References
- `axisConfig.py` method/descriptions @axisConfig.py#189-318  
- Cross-axis composition + completeness-method conflicts @axisConfig.py#1260-1474  
- ADR-0104 (Reference Key and Method Reclassification) for prior taxonomy shifts @docs/adr/0104-reference-key-and-method-reclassification.md#1-179
