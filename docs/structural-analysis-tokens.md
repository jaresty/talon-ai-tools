# Structural Analysis Method Tokens

This guide explains the cluster of method tokens for analyzing and fixing structural problems in code, systems, and reasoning. They fall into two parallel problem spaces — **coupling** and **implicit/explicit** — each with the same internal structure: find it → describe it → fix it. A separate **anchor** token prevents problems from recurring.

---

## The Two Problem Spaces

### Coupling Problems

Something is tangled that should be separate — responsibilities intermixed, change in one place forces change in another, ownership is unclear.

| Stage | Token | Question it answers |
|-------|-------|---------------------|
| Find it | `snag` | Where are the coupling seams? |
| Describe it | `mesh` | How does coupling propagate across each seam? |
| Rate it | `melody` | How bad is this seam? (visibility × scope × volatility) |
| Fix it (steps) | `shear` | What are the steps to separate these coupled domains? |
| Fix it (enforce) | `sever` | How do I introduce a structural separation that routes all interaction through explicit interfaces? |
| Audit it | `seep` | Is the boundary actually holding? Where is influence leaking past intended scope? |

**Typical flow:** `snag` → `mesh` → `melody` → `shear` or `sever` → `seep`

---

### Implicit/Explicit Problems

Something that should be stated is instead assumed, or exists as convention rather than enforceable structure.

| Stage | Token | Question it answers |
|-------|-------|---------------------|
| Find it (rule level) | `gap` | What assumption is being treated as a stated rule? |
| Find it (conclusion level) | `drift` | Where can conclusions diverge because derivation is underspecified? |
| Find it (region level) | `amorph` | Which regions have no stable explicit structure at all? |
| Find it (conflict level) | `clash` | Where do two explicitly stated structures contradict each other? |
| Fix it (targeted) | `reify` | I've found an implicit pattern — name it and enforce it as an explicit rule |
| Fix it (systemic) | `crystal` | Restructure the whole system so behavior follows from explicit structure, not convention |
| Fix it (derivation) | `mint` | Construct the generative assumptions explicitly so conclusions follow as direct products |

---

### Anchor

| Token | Question it answers |
|-------|---------------------|
| `ground` | I have a declared spec — treat it as a fixed authority that all representations must justify against |

`ground` is distinct from the others: it doesn't diagnose or fix a problem, it establishes a governing layer that makes drift, gap, and amorph structurally harder to accumulate in the first place.

---

## The Hardest Distinctions

### `gap` vs `amorph` vs `drift`

All three are about implicit vs. explicit, but at different levels:

- **`gap`**: Something is *assumed as stated* — a specific rule, role, or relationship that everyone treats as explicit but isn't written down. Produces coordination failures when two parties discover they assumed different things.
- **`drift`**: Conclusions are *not derivable* from the representation — the structure is loose enough that the same premises yield different outputs on re-reasoning. The problem is at the conclusion level, not the premise level.
- **`amorph`**: An entire *region* has no stable explicit structure — behavior is emergent, ownership is unclear, there's nothing to violate because nothing was stated. Broader than `gap` (which requires something to be implicitly assumed).

**Resolving question:**
- Is there something specific that's being assumed as fact? → `gap`
- Can the same premises produce different conclusions? → `drift`
- Is there just... nothing explicit here? → `amorph`

---

### `gap` vs `clash`

- **`gap`**: Failure is between implicit and explicit — something *unstated* is causing problems
- **`clash`**: Failure is between two *explicit* structures — both are stated, they just contradict each other

`clash` requires that both conflicting sides exist as declared structures. If one side is implicit, it's a `gap`.

---

### `reify` vs `crystal`

- **`reify`**: Targeted — you've identified one implicit pattern and want to give it a name and formal status. Output is a single named rule or constraint.
- **`crystal`**: Systemic — the whole system relies on convention and tacit knowledge, and you want to eliminate that dependency across the board.

`reify` is often a step *within* a `crystal`-level effort. Use `reify` when you know which pattern to formalize; use `crystal` when you want to reshape the architecture toward structural determination broadly.

---

### `snag` vs `mesh`

These are sequential, not alternative:

- **`snag`** comes first: find where the seams are. Output is a map of coupling locations.
- **`mesh`** comes second: once you know where the seams are, describe what travels across each one and how change propagates.

You cannot meaningfully `mesh` without first knowing what seam you're tracing.

---

### `shear` vs `sever`

Both produce decoupling, but at different levels:

- **`shear`**: Procedural — "give me a step-by-step plan to pull these two things apart." Output is an ordered sequence of actions. Use when you need to navigate the separation practically.
- **`sever`**: Architectural — "introduce a structural boundary so that direct dependency is impossible and all interaction goes through a defined interface." Output is a design decision. Use when you want to make the separation permanent and enforced.

`shear` might produce work that implements `sever`. For a migration plan, use `shear`. For an architectural constraint, use `sever`.

---

### `seep` — the post-install audit

`seep` is the missing step most people skip. After running `sever` (or `shear`), run `seep` to verify the boundary is holding:

- Did influence from the separated domain leak back through a side channel?
- Is scope creep re-introducing the coupling through a different path?
- Are there concerns crossing boundary lines uninvited?

`seep` answers "did it work?" where `snag` answers "where is it broken?" They are bookends.

---

### `melody` — rating, not tracing

`melody` is easy to confuse with `mesh` because both deal with coupling seams. The difference:

- **`mesh`**: Structural — describes the propagation topology. "What does a change to X reach, and how?"
- **`melody`**: Evaluative — rates seam quality across three dimensions:
  - **Visibility**: How explicit and discoverable is the contract? (named interfaces = high; scattered helpers = low)
  - **Scope**: How many locations require simultaneous edits when this seam changes?
  - **Volatility**: How tightly does temporal or structural coupling force synchronized change sets?

Use `mesh` to understand the coupling. Use `melody` to assess how risky it is.

---

### `ground` vs `crystal`

- **`crystal`**: Shapes the system *toward* explicit structure — removes implicit coupling and convention
- **`ground`**: Treats a *declared* governing layer as fixed authority and requires all representations to justify against it

`crystal` is structural design; `ground` is a validation discipline. You can crystal a system without ground, and ground a process without crystalizing the system.

---

### `bound` vs `sever`

- **`bound`**: Constrains *propagation* — limits how far effects spread. Additive: you add a propagation boundary to an existing structure.
- **`sever`**: Introduces a *separation* — restructures the system so interaction must go through explicit interfaces. More invasive: changes the shape of the dependency graph.

`bound` contains; `sever` separates.

---

### `mint` vs `ground`

- **`mint`**: Constructs generative assumptions *forward* — builds derivations so conclusions follow as direct products of the model
- **`ground`**: Treats a declared layer as *fixed authority* that representations must justify against

`mint` generates structure from assumptions; `ground` validates structure against a fixed spec. They operate in opposite directions.

---

## Supporting Tokens

These tokens from related clusters work closely with the above:

| Token | Role | Works with |
|-------|------|-----------|
| `domains` | Identify bounded contexts (DDD) | `sever` — identify contexts before enforcing separations |
| `bound` (method) | Constrain propagation proactively | `seep` — bound proactively, seep audits post-hoc |
| `dam` (scope) | Focus analysis on containment boundaries | Pairs with any coupling token |

---

## Quick Decision Guide

**"Something is broken but I don't know where"**
→ `snag` (coupling) or `gap` / `amorph` (implicit/explicit)

**"I know there's coupling — how bad is it?"**
→ `mesh` to trace propagation, `melody` to rate it

**"I need to fix the coupling"**
→ `shear` for a plan, `sever` for architectural enforcement

**"I fixed the coupling — did it work?"**
→ `seep`

**"Something is assumed but not stated"**
→ `gap` (specific assumption) or `amorph` (whole region)

**"Conclusions are inconsistent"**
→ `drift`

**"Two rules conflict"**
→ `clash`

**"I want to name and enforce an implicit pattern"**
→ `reify`

**"I want to make the whole system explicit"**
→ `crystal`

**"I have a spec — make everything justify against it"**
→ `ground`
