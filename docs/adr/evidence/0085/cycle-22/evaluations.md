# ADR-0085 Cycle 22: Topology Axis Coherence (Seeds 696–735)
**Date:** 2026-05-14
**Seeds:** 696–725 broad sweep (30), 726–735 topology deep-dive (10)
**Bar version:** dev build `/tmp/bar-new` (post-commit 308d59cb — topology in shuffle pool)
**Dev repo ahead of binary:** Yes — topology shuffle fix not yet in Homebrew release
**Focus:** Topology axis coherence — first cycle with topology tokens in shuffle pool

---

## Calibration Header

**Evaluator:** Single-evaluator (Claude, human-assisted)
**Calibration status:** Using established boundary rationale from cycle 21.
Within-evaluator max delta ≤ 1 expected.
**Boundary rationale:** 5 = coherent, tokens reinforce each other; 4 = minor rough edges; 3 = usable but tension; 2 = structural incompatibility; 1 = contradictory/broken.
**Topology-specific criterion:** Does the topology token's epistemic framing (who observes reasoning) fit naturally with the task + other constraints? Topology shapes *how much reasoning state is externalized and for whom* — it should not conflict with the task or channel.

---

## Broad Sweep Evaluations (seeds 696–725, 15 sampled)

### Seed 696 — `['peer_engineer_explanation', 'pull', 'narrow', 'stable', 'cluster', 'fly rog']`
**Topology:** none
**Score:** 4 — `pull narrow` is a tight extraction scope; `stable` (invariants) + `cluster` (grouping) compose naturally. `fly rog` (abstract+acting, structural) is a mild tension with `narrow` (small slice) but workable.
**Notes:** No topology — baseline control. Coherent.

### Seed 697 — `['as storyteller', 'directly', 'sim', 'grow', 'rigor', 'jog']`
**Topology:** none
**Score:** 4 — `sim grow` (simulation that expands depth) is a good pairing. `rigor` (method) + `jog` (directional: pace-setting) compose coherently for a storyteller delivering a simulation with growing depth.
**Notes:** No topology — baseline control.

### Seed 698 — `['product_manager_to_team', 'fix', 'solo', 'formal']`
**Topology:** solo
**Score:** 4 — `fix solo` = fix something with synthesis-optimized reasoning (no need to externalize state for an observer). `formal` channel + PM-to-team persona is a slight awkwardness (formal notation for a team communication), but `solo` fits: the reasoning doesn't need to be inspectable, just the output delivered formally.
**Notes:** Topology coherent. `formal` + PM persona is mild category tension (formal notation vs. team Slack/email register) — score 4 not 5.

### Seed 699 — `['as writer', 'to LLM', 'kindly', 'fix', 'narrow', 'argue', 'code']`
**Topology:** none
**Score:** 3 — `argue` (method: construct argument) + `code` channel is a cautionary combination (argumentative prose in code-only output). `to LLM` + `kindly` tone is unusual but valid for prompt engineering. `narrow` scopes appropriately.
**Notes:** No topology. Pre-existing cautionary: argue+code.

### Seed 700 — `['designer_to_pm', 'show', 'minimal', 'sync', 'fly ong']`
**Topology:** none
**Score:** 4 — `show minimal` (explain briefly) + `sync` (channel: synchronous delivery) + designer-to-PM persona. `fly ong` (abstract+acting) gives the explanation forward-momentum. Coherent.
**Notes:** No topology — baseline control.

### Seed 702 — `['fun_mode', 'sort', 'solo', 'authority', 'seep', 'scaffold', 'draw']`
**Topology:** solo
**Score:** 4 — `sort solo` (categorize with synthesis-optimized reasoning) is coherent: sorting a set doesn't need inspectable step-by-step reasoning. `seep` (influence propagation) + `scaffold` (build up from first principles) compose well for sorting by authority actors. `draw` (ASCII layout) is natural for organizing. `fun_mode` adds a tonal layer.
**Notes:** Topology coherent with task. `solo` fits sorting — synthesis efficiency over inspectable reasoning.

### Seed 703 — `['designer_to_pm', 'probe', 'audit', 'dip rog']`
**Topology:** audit
**Score:** 5 — `probe audit` is an excellent pairing: probing the structure of something while making each claim locally defensible (adversarial scrutiny). `dip rog` (concrete+structural) reinforces a rigorous, ground-up analysis. Designer-to-PM persona frames the output for a product-adjacent audience.
**Notes:** Topology coherent. Audit is the natural topology for adversarial probing.

### Seed 704 — `['appreciate', 'to managers', 'gently', 'probe', 'relay', 'triage', 'jobs', 'notebook', 'fip rog']`
**Topology:** relay
**Score:** 4 — `probe relay` (probe something so another party can continue mid-stream) fits: the probe's state is externalized for handoff. `triage` (stakes-proportionate depth) + `jobs` scope compose well. `notebook` channel is a natural for relay — Jupyter notebooks are handoff artifacts. `fip rog` (full vertical + structural) is complex but workable. `appreciate` persona + `gently` tone with managers is coherent.
**Notes:** Topology coherent. `relay + notebook` is a strong natural combination (notebooks are handoff artifacts by design).

### Seed 707 — `['teach_junior_dev', 'sort', 'audit', 'thing', 'dip rog']`
**Topology:** audit
**Score:** 4 — `sort audit` (sort entities while making each classification locally defensible). Teaching a junior dev to classify things with auditable reasoning is coherent. `thing` scope (entities/boundaries) + `dip rog` (concrete+structural) reinforce.
**Notes:** Topology coherent. Minor: audit framing for a teaching context is slightly heavy — audit implies adversarial scrutiny which conflicts mildly with the teach persona's supportive register. Score 4.

### Seed 708 — `['coach', 'as writer', 'directly', 'sim', 'witness', 'gist', 'authority']`
**Topology:** witness
**Score:** 4 — `sim witness` (simulate something with surfaced assumptions at each transition) is coherent — simulation benefits from visible assumption-surfacing. `gist` completeness is a mild tension with `witness` (witness asks for inspectable reasoning steps, gist asks for brief output). Coach persona + writer voice + direct tone compose.
**Notes:** witness+gist tension noted: inspectable reasoning steps vs. brief output. Workable but produces a compressed witness trace. Score 4.

### Seed 712 — `['executive_brief', 'fix', 'blind', 'story']`
**Topology:** blind
**Score:** 4 — `fix blind` (fix something such that a future reader can reconstruct the context from scratch). `story` form (user story) + `executive_brief` persona is an interesting pairing — brief for an executive, but as a user story. `blind` fits: user stories should be self-contained with explicit assumptions for future replay.
**Notes:** Topology coherent. `executive_brief + story` is mildly unusual (executives don't usually receive Jira-style stories) but valid.

### Seed 713 — `['as storyteller', 'kindly', 'sim', 'witness', 'grow', 'authority', 'chain', 'adr', 'fly ong']`
**Topology:** witness
**Score:** 3 — `sim witness` coherent (see seed 708). `chain` method (conclusion-chain) + `witness` (surface assumptions at each transition) compose naturally — both demand visible reasoning. `adr` channel + `as storyteller` persona is the tension: ADR format is technical/formal, storyteller is narrative; `kindly` tone softens it but doesn't resolve. `grow` + `fly ong` add complexity.
**Notes:** Core topology+method composition is strong. Channel/persona clash scores this down to 3.

### Seed 714 — `['product_manager_to_team', 'probe', 'audit', 'grow', 'cross', 'sever', 'diagram']`
**Topology:** audit
**Score:** 5 — `probe audit` (see seed 703 — natural pairing). `grow` completeness (expands where needed) + `cross` scope (cross-cutting concerns) + `sever` method (introduce separations) + `diagram` channel. All compose coherently: auditable probe of cross-cutting concerns, separating them, delivered as a diagram. PM-to-team persona fits.
**Notes:** Excellent combination. Audit reinforces the rigor of sever (making separations defensible).

### Seed 716 — `['product_manager_to_team', 'pick', 'blind', 'motifs', 'meld', 'checklist', 'code', 'dig']`
**Topology:** blind
**Score:** 3 — `pick blind` (choose options such that a future reader can reconstruct context). `blind + code` channel is the tension: code output doesn't naturally carry the explicit assumption blocks that blind requires. `checklist + code` is also a known cautionary. `motifs` (recurring structural forms) + `meld` (blend/overlap) + `dig` directional compose, but the topology+channel conflict reduces coherence.
**Notes:** Gap candidate: `blind + code` channel — code output structurally resists the explicit assumption/context blocks that `blind` requires.

### Seed 724 — `['teach', 'as prompt engineer', 'diff', 'audit', 'triage', 'assume', 'taxonomy']`
**Topology:** audit
**Score:** 5 — `diff audit` (compare two things while making each comparison claim locally defensible). `triage` completeness (stakes-proportionate) + `assume` scope (explicit premises) + `taxonomy` form (classification). All compose: audited diff of assumptions, classified by taxonomy, depth proportionate to stakes. Prompt engineer persona fits.
**Notes:** Strongest combination in the broad sweep. Audit + assume scope is a natural pairing.

---

## Topology Deep-Dive Evaluations (seeds 726–735)

### Seed 726 — `['inform', 'to product manager', 'check', 'audit', 'gherkin']`
**Topology:** audit
**Score:** 4 — `check audit` (evaluate something with locally defensible claims). `gherkin` channel + audit is interesting: Gherkin scenarios should be independently verifiable (each scenario stands alone without narrative dependency) — this is structurally coherent with audit. `inform` tone + PM audience fits.
**Notes:** `audit + gherkin` is a natural pairing: Gherkin's Given/When/Then structure mirrors audit's local-defensibility requirement.

### Seed 727 — `['stakeholder_facilitator', 'pull', 'solo', 'struct', 'story', 'jira', 'dip bog']`
**Topology:** solo
**Score:** 4 — `pull solo` (extract a subset with synthesis-optimized reasoning). `jira` channel + `story` form is redundant (Jira tickets are already stories). `struct` scope + `dip bog` (concrete+full-horizontal) compose. `solo` fits pulling: extraction doesn't need inspectable reasoning. Stakeholder facilitator persona is appropriate.
**Notes:** `story + jira` redundancy is a pre-existing catalog note, not a topology issue. Topology coherent.

### Seed 728 — `['scientist_to_analyst', 'plan', 'relay', 'bog']`
**Topology:** relay
**Score:** 5 — `plan relay` (produce a plan such that another party can continue it mid-stream). `bog` (full horizontal: reflective+acting) reinforces: the plan covers both the reflective/structural dimension and the acting/extension dimension — making it maximally continuation-safe. Scientist-to-analyst is a natural handoff persona.
**Notes:** Excellent. `relay + plan` is a paradigmatic topology use case. `scientist_to_analyst` persona makes the handoff framing explicit.

### Seed 729 — `['announce', 'as future historian', 'make', 'relay', 'fail', 'facilitate', 'diagram']`
**Topology:** relay
**Score:** 4 — `make relay` (create something continuation-safe). `fail` scope (failure modes) + `facilitate` form + `diagram` channel. `as future historian` persona + `relay` topology is an interesting compound: historian writes for future readers, relay writes for continuation — both externalize state but for different purposes (relay = handoff mid-stream, historian = future replay). Minor conceptual overlap with `blind`. `announce` tone is mild tension with historian persona.
**Notes:** `relay` vs. `blind` distinction slightly blurred by persona. Score 4. Worth noting in distinctions feedback.

### Seed 730 — `['designer_to_pm', 'show', 'witness', 'dam', 'gate']`
**Topology:** witness
**Score:** 5 — `show witness` (explain something with surfaced assumptions at each step). `dam` scope (containment/boundaries) + `gate` form (hard-blocking checkpoint structure). `witness` + `gate` form is a natural pairing: gate requires visible preconditions, witness requires surfaced assumptions — both demand inspectable reasoning. Designer-to-PM persona.
**Notes:** `witness + gate` is a strong natural combination. Gate's blocking structure benefits from witness's assumption-surfacing.

### Seed 731 — `['announce', 'kindly', 'plan', 'audit', 'full', 'authority', 'jira']`
**Topology:** audit
**Score:** 4 — `plan audit` (produce a plan where each planning claim is locally defensible). `full` completeness + `authority` scope (actors with authority) + `jira` channel. `jira + full` is a mild tension (Jira tickets are usually terse). `announce` tone + `kindly` with audit's adversarial framing is mildly contradictory — you can be kind and rigorous, but the combination creates an unusual register.
**Notes:** Tone/topology register tension (kindly + audit). Workable but notable.

### Seed 732 — `['executive_brief', 'make', 'witness', 'reset', 'cards', 'rog']`
**Topology:** witness
**Score:** 4 — `make witness` (create something with surfaced assumptions). `reset` method (start fresh, clear state) + `witness` topology is coherent: resetting requires surfacing what assumptions you're leaving behind. `cards` form + `executive_brief` persona works. `rog` (structural/reflective) reinforces.
**Notes:** Coherent. `reset + witness` is a natural pairing.

### Seed 733 — `['as teacher', 'to junior engineer', 'probe', 'witness', 'skim', 'product', 'checklist']`
**Topology:** witness
**Score:** 3 — `probe witness` (probe with surfaced assumptions) is coherent. `skim` completeness + `witness` is the same tension as seed 708: witness needs visible reasoning steps, skim wants brief output. `checklist` form + probe is mild tension (probes are usually analytical, not checklist-structured). Teaching persona is coherent.
**Notes:** `witness + skim` combination produces compressed traces — same issue as seed 708. Consistent finding.

### Seed 734 — `['product_manager_to_team', 'diff', 'blind', 'narrow', 'mean', 'spike', 'code', 'rog']`
**Topology:** blind
**Score:** 2 — `diff blind` (compare things such that future reader can reconstruct context). `blind + code` channel is the same structural conflict as seed 716: code output cannot carry the explicit assumption/context blocks that `blind` requires. `narrow` completeness (very small slice) further compresses the space available for assumption reconstruction. `mean` + `spike` form composition is also a pre-existing pattern.
**Notes:** **Gap candidate (score 2):** `blind + code` is a structural incompatibility — code channel output has no natural place for explicit assumption blocks. Should appear in cross-axis composition guidance. Consistent with seed 716 finding.

### Seed 735 — `['as PM', 'directly', 'fix', 'witness', 'zoom', 'storage', 'quiz', 'fig']`
**Topology:** witness
**Score:** 4 — `fix witness` (fix something with surfaced assumptions at each step — useful for debugging). `zoom` method + `witness` topology compose naturally (zoom = focus in, witness = surface what you're assuming as you focus). `storage` scope + `quiz` form + `fig` directional. PM persona + direct tone.
**Notes:** Coherent. `zoom + witness` is a natural pairing.

---

## Score Summary

| Seed | Topology | Score | Key Finding |
|------|----------|-------|-------------|
| 696 | none | 4 | baseline |
| 697 | none | 4 | baseline |
| 698 | solo | 4 | solo+formal minor tension |
| 699 | none | 3 | argue+code cautionary (pre-existing) |
| 700 | none | 4 | baseline |
| 702 | solo | 4 | solo coherent for sorting |
| 703 | audit | 5 | probe+audit natural |
| 704 | relay | 4 | relay+notebook natural handoff pairing |
| 707 | audit | 4 | audit mild tension with teach persona |
| 708 | witness | 4 | witness+gist tension |
| 712 | blind | 4 | blind+story coherent |
| 713 | witness | 3 | adr channel vs storyteller persona |
| 714 | audit | 5 | probe+audit+sever+diagram excellent |
| 716 | blind | 3 | blind+code structural conflict |
| 724 | audit | 5 | diff+audit+assume natural |
| 726 | audit | 4 | audit+gherkin natural pairing |
| 727 | solo | 4 | story+jira redundancy (pre-existing) |
| 728 | relay | 5 | plan+relay paradigmatic |
| 729 | relay | 4 | relay/blind persona blur |
| 730 | witness | 5 | witness+gate natural pairing |
| 731 | audit | 4 | kindly+audit register tension |
| 732 | witness | 4 | reset+witness natural |
| 733 | witness | 3 | witness+skim same as seed 708 |
| 734 | blind | 2 | **blind+code structural incompatibility** |
| 735 | witness | 4 | zoom+witness natural |

**Mean (all 25):** 4.04
**Mean (topology seeds only, 20):** 4.0
**Mean (non-topology seeds, 5):** 3.8

---

## Gap Findings

### G1 (Score 2): `blind + code` channel — structural incompatibility
**Seeds:** 716 (score 3), 734 (score 2)
**Finding:** `blind` topology requires explicit assumption/context blocks before conclusions. `code` channel output (code-only, no surrounding natural language) has no natural location for these blocks. The combination produces either: (a) assumption blocks that violate the code channel requirement, or (b) code output with no assumption reconstruction, violating blind.
**Recommendation:** Add `blind + code` as a cautionary entry in `CROSS_AXIS_COMPOSITION` for the topology axis (or code channel). Document: "blind requires explicit prose assumption blocks; code channel produces code-only output — the two structural requirements are incompatible."

### G2 (Score 3, recurring): `witness + skim/gist` — inspectable-vs-brief tension
**Seeds:** 708 (score 4 witness+gist), 733 (score 3 witness+skim)
**Finding:** `witness` requires each reasoning transition to surface its assumptions (verbose by nature). `skim`/`gist` require brief output. The combination systematically produces compressed assumption traces that satisfy neither goal fully.
**Recommendation:** Add to "Choosing Topology" or "Choosing Completeness" guidance: "witness with gist/skim produces compressed assumption traces — if brevity is required, prefer solo (no externalized reasoning) or explicit user instruction to surface only critical assumptions."

### G3 (Observation): Natural pairings identified for catalog
**Positive patterns to document:**
- `audit + probe` (adversarial analysis — mutually reinforcing)
- `relay + notebook` (handoff + notebook channel — structural alignment)
- `relay + plan` (continuation-safe planning)
- `witness + gate` (surfaced assumptions + blocking checkpoints)
- `witness + chain` method (both demand visible reasoning steps)
- `audit + gherkin` (local defensibility + Given/When/Then isolation)
- `zoom + witness` (focus in + surface assumptions as you focus)
