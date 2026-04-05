# ADR-0224: Ground Token Decomposition

## Status

Proposed

## Context

ADR-0223 established the `ground` method token through 14 experiments, settling on an
A0+5+1+3 form: one foundational assumption (A0), five independent axioms, one meta-axiom
(M), and three derived theorems. During that work, a `probe orbit collapse mint` analysis
on the 9-axiom form revealed that ground bundles four conceptually distinct concerns with
independent academic lineages:

| Concern | Academic lineage | Ground components |
|---------|-----------------|-------------------|
| Epistemic discipline | Popper / audit theory | A1, T1 |
| Derivation-chain enforcement | Systems engineering traceability | A4 |
| Step-granularity control | Experimental control / unit testing | A5, T3 |
| Optimizer-pressure response | Goodhart's law / mechanism design | A0, A3, M |

Two of those concerns have already been elevated to the universal EXECUTION_REMINDER
(A1 evidence primacy, A0 appearance/actuality). The remaining two — derivation-chain
enforcement and step-granularity control — are still bundled in ground but are
domain-agnostic: they apply to writing tasks, decision chains, and design work, not
only to software implementation.

This creates three problems:

1. **Ground is opaque.** Users who want incremental causality without full process
   derivation, or derivation chains without step granularity, have no way to express
   that. Ground is all-or-nothing.

2. **Ground is hard to recompose.** The TDD workflow (evaluation before implementation
   + atomic steps) is a specific combination of ground's concerns that belongs as a
   named preset, but the components aren't currently separable.

3. **Existing tokens partially overlap with ground's concerns** without owning them
   cleanly. `verify` (falsification pressure), `survive` (expose claims to live
   conditions), `mark` (capture checkpoints), and `depends` (dependency tracing) each
   touch adjacent territory without fully addressing the same failure modes.

### Academic framing (from structural analysis)

The two remaining concerns decompose as follows:

**Derivation-chain enforcement (trace-like):**
- Governs: can the output be reconstructed from prior artifacts?
- Failure mode: hidden reasoning jumps; conclusions detach from premises
- Academic home: requirements traceability, audit chains, systems engineering
- Orthogonal to step granularity: a step can be atomic yet untraceable

**Step-granularity control (atomic-like):**
- Governs: does each step change exactly one observable thing?
- Failure mode: bundled changes; causal attribution collapses
- Academic home: controlled intervention, experimental design, unit testing
- Orthogonal to derivation: a chain can be fully traceable yet contain multi-effect steps
- **Domain-agnostic**: applies to writing revision, design iteration, and decision-making,
  not only to software TDD. One argument per edit, one assumption changed per decision
  cycle, one structural change per refactoring step — all are atomic in this sense.

### Relationship to existing tokens

| Existing token | Current meaning | Overlap with proposed split |
|---------------|----------------|----------------------------|
| `verify` | Falsification pressure on claims | Partial: applies pressure to claims; does not enforce temporal ordering of evaluation vs. implementation artifacts |
| `survive` | Expose to uncontrolled live conditions | Partial: independent evaluation under real conditions; no derivation-chain or step-granularity constraint |
| `mark` | Capture checkpoints as process runs | Partial: passive evidence recording; no enforcement that evaluation precedes implementation |
| `depends` | Trace dependency relationships | Partial: dependency structure; no artifact-precedence or correction-granularity constraint |
| `trace` | Narrate sequential progression | **Name conflict**: different meaning; cannot reuse |

None of these fully own the failure modes. The proposed tokens would be additive, not
replacements — though `verify` and `survive` may want their definitions refined to
clarify boundary.

## Decision Options

### Option 1: Keep ground monolithic

No change. Ground remains the single token for all four concerns.

**Pros**: No migration; existing experiments are directly comparable.
**Cons**: Recomposition impossible; semantic bundling makes ground opaque; users who
want one concern must accept all.

### Option 2: Decompose into three new tokens + slim ground

Introduce three new method tokens and slim `ground` to its irreducible core:

**`verify` (repurpose/expand existing):** Evaluation-precedence discipline.
Evaluation artifacts must be produced before the implementation artifacts they evaluate.
Declare success criteria before acting. An evaluation written after the fact is shaped by
what it evaluates and cannot expose gaps the implementation was designed around.
*Expands existing `verify` (falsification pressure) to include temporal ordering.*

**`[new name]` (derivation chain):** Each artifact must cite its predecessor's actual
content. Without explicit derivation chains, conclusions detach from premises. Use when
multi-step reasoning or artifact sequences must remain reconstructable.
*`trace` is taken; candidates: `chain`, `derive`, `link`, `thread`.*

**`atomic`:** The unit of implementation, revision, or evaluation is the smallest
independently observable change. Each refinement step addresses exactly one observed
failure and introduces nothing beyond what closes it. Domain-agnostic: applies to writing
(one argument per edit), decisions (one assumption per cycle), and implementation (one
behavior per test).
*`atomic` is pronounceable (3 syllables) and has no existing token conflict.*

**`ground` (slimmed):** Retains only A0 (optimizer assumption) + M (execution
discipline: derive your own enforcement process before acting). This is ground's
irreducible unique contribution — meta-process derivation. Users who want the full
protocol compose `ground verify atomic [chain-token]`.

### Option 3: Decompose into two tokens only (merge derivation into verify)

Merge derivation-chain enforcement into an expanded `verify` and keep `atomic`
standalone.

**Pros**: Fewer tokens; simpler vocabulary.
**Cons**: Loses the orthogonality distinction — derivation continuity and epistemic
justification are different failure modes. A claim can be epistemically justified yet
untraceable (see ADR rationale above).

### Option 4: Preset only, no new tokens

Create a `tdd` preset (name TBD — not pronounceable) that bundles existing tokens for
TDD workflows, without introducing new tokens.

**Pros**: No token count increase; existing tokens unchanged.
**Cons**: Doesn't solve the orthogonality problem; users still can't express individual
concerns; the TDD failure modes (evaluation-before-implementation, atomic steps) remain
unnamed and unenforceable separately.

## Open Questions

1. **Name for derivation-chain token**: `trace` is taken (narrates sequential
   progression). Candidates: `chain`, `derive`, `link`, `thread`. Recommendation:
   `chain` — short, unambiguous, evokes artifact dependency.

2. **`verify` repurpose scope**: The existing `verify` (falsification pressure) is
   adjacent but narrower. Two sub-options:
   - (a) Expand `verify` in-place to add temporal ordering / evaluation-precedence
   - (b) Keep existing `verify` unchanged and introduce a new token (e.g. `prior`,
     `gate`) for evaluation precedence

   The ADR-0223 experiments showed evaluation precedence (T2) is the most critical
   behavioral gate — it's what caused the 45→91 score jump when A7 was added. Merging
   it into `verify` risks diluting both.

3. **`atomic` outside TDD**: Confirmed domain-agnostic by the GPT structural analysis.
   Examples: one argument changed per writing revision (to know what improved the draft);
   one assumption changed per decision cycle (to know what shifted the outcome). The token
   should not be described as TDD-specific.

4. **Method token cap**: Current soft cap may need raising. Orthogonality is more
   valuable than a hard limit — three genuinely independent tokens that compose cleanly
   are better than one opaque bundled token. Recommend raising cap to accommodate.

5. **Preset name for TDD workflow**: `tdd` is not pronounceable as a word. Candidates:
   - `testfirst` — descriptive but long
   - `disciplined` — too generic
   - `rigor` — already exists as a method token ("disciplined, well-justified reasoning")
   - `craft` — evocative of disciplined making
   - `forge` — making under constraint
   Recommendation: `craft` — short, pronounceable, evokes deliberate incremental making.

## Recommended Decision

Adopt Option 2 with the following token names:

| Token | Role | Status |
|-------|------|--------|
| `verify` | Evaluation precedes implementation; declare criteria before acting | Expand existing |
| `chain` | Derivation-chain enforcement; each artifact cites predecessor content | New |
| `atomic` | One observable change per step; domain-agnostic | New |
| `ground` | A0 + M: optimizer assumption + derive your own enforcement process | Slim existing |

Add preset `craft` = `verify chain atomic` for TDD and disciplined iterative workflows.

Raise method token soft cap to accommodate the three independently useful tokens.

## Consequences

**If adopted:**
- `ground` becomes smaller and more honest: it owns only the meta-process derivation
  concern, not the full protocol
- `verify`, `chain`, `atomic` become independently usable for writing, design, and
  decision tasks
- The TDD workflow becomes expressible without `ground`'s full process-derivation overhead
- Existing `ground`-only prompts continue to work (ground still contains M which drives
  derivation of verify/chain/atomic behaviors — just less explicitly)
- Experiments 1–14 in ADR-0223 remain valid as ground baselines; new experiments needed
  to validate individual token behavior and preset compliance

**Validation plan:**
- Exp 15: `verify atomic chain` (no ground) on budget-limits TDD task — does it match
  ground's ~96 score?
- Exp 16: `atomic` alone on a writing revision task — does one-argument-per-edit
  discipline hold?
- Exp 17: `chain` alone on a multi-step analysis — does derivation-chain enforcement
  hold without atomic?

## Relationship to Other ADRs

- ADR-0220: ground protocol origin
- ADR-0221: ground canonical essence
- ADR-0222: evaluation methodology (scorecard used to validate)
- ADR-0223: structural placement and minimization (experiments 1–14; ground's current form)
