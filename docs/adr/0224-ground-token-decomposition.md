# ADR-0224: Ground Token Decomposition

## Status

Adopted — Exp 15b: `ground gate chain atomic` scored 100/100 (2026-04-05)

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

**`gate` (new token):** Evaluation-precedence discipline.
Evaluation artifacts must be produced before the implementation artifacts they evaluate.
Declare success criteria before acting. An evaluation written after the fact is shaped by
what it evaluates and cannot expose gaps the implementation was designed around.
*`verify` retained unchanged (falsification pressure on claims, anti-hallucination use).*

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
protocol compose `ground gate chain atomic`.

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

2. **`verify` repurpose scope**: **Resolved — option (b).** `verify` retained unchanged
   (falsification pressure on claims; useful for anti-hallucination and general claim
   grounding). New token `gate` introduced for evaluation-precedence discipline.
   Rationale: `verify` applies to any claim regardless of artifact ordering; `gate` is
   specifically about temporal ordering of evaluation vs. implementation artifacts. They
   address different failure modes and should remain separate.

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
| `gate` | Evaluation precedes implementation; declare criteria before acting | New |
| `chain` | Derivation-chain enforcement; each artifact cites predecessor content | New |
| `atomic` | One observable change per step; domain-agnostic | New |
| `ground` | A0 + M: optimizer assumption + derive your own enforcement process | Slim existing |
| `verify` | Falsification pressure on claims; anti-hallucination use | Unchanged |

Add preset `craft` = `ground gate chain atomic` for TDD and disciplined iterative workflows.
`ground` is included in the preset because slimmed ground (A0+M) provides the meta-process
wrapper that makes the three tokens actively enforced rather than passively acknowledged.
`verify` is kept unchanged for general falsification/anti-hallucination use — it is not part
of the `craft` preset because it addresses claim grounding, not artifact ordering.

Raise method token soft cap to accommodate the three independently useful tokens.

## Implementation Specification

This section contains everything needed to implement ADR-0224 in a fresh context.

### Token definitions (copy-paste ready)

**`verify` — unchanged** (retained for falsification pressure / anti-hallucination use).
Not modified. Not part of the `craft` preset.

**`gate` — new token** (add to `lib/axisConfig.py`):

```python
# In AXIS_KEY_TO_VALUE["method"]:
"gate": (
    "The response enhances the task by enforcing evaluation precedence: declare what success "
    "looks like and produce an evaluation artifact before producing the implementation artifact "
    "it evaluates. An evaluation written after the fact is shaped by what it evaluates and "
    "cannot expose gaps the implementation was designed around. Self-certification is "
    "impossible — the evaluation must be structurally separate from the artifact. Use when any "
    "artifact (code, argument, plan, decision) must be demonstrably correct rather than "
    "plausibly correct."
),

# In AXIS_KEY_TO_LABEL["method"]:
"gate": "Evaluation before implementation",

# In AXIS_KEY_TO_KANJI["method"]:
"gate": "門",

# In AXIS_KEY_TO_CATEGORY["method"]:
"gate": "Process",  # requires governing artifact (evaluation) before acting
```

**`chain` — new token** (add to `lib/axisConfig.py`):

```python
# In AXIS_KEY_TO_VALUE["method"]:
"chain": (
    "The response enhances the task by enforcing derivation-chain discipline: each artifact "
    "or conclusion must explicitly cite its predecessor's actual content. Without visible "
    "derivation chains, conclusions detach from premises and reasoning becomes unreconstructable. "
    "Use when multi-step reasoning, multi-artifact sequences, or iterative refinement must "
    "remain auditable — any reader should be able to reconstruct why each step follows from "
    "the previous one."
),

# In AXIS_KEY_TO_LABEL["method"]:
"chain": "Derivation chain enforcement",

# In AXIS_KEY_TO_KANJI["method"]:
"chain": "繋",

# In AXIS_KEY_TO_CATEGORY["method"]:
"chain": "Reasoning",  # ongoing constraint throughout, not a pre-artifact

# In AXIS_KEY_TO_USE_WHEN["method"] (if it exists):
"chain": (
    "multi-step argument or analysis where conclusions must trace back to evidence; "
    "iterative artifact sequences where each version must cite what it changed and why; "
    "any task where 'how did you get there' is as important as 'what did you get'"
),
```

**`atomic` — new token** (add to `lib/axisConfig.py`):

```python
# In AXIS_KEY_TO_VALUE["method"]:
"atomic": (
    "The response enhances the task by enforcing step-granularity discipline: each "
    "refinement step addresses exactly one observed failure and introduces nothing beyond "
    "what closes it. When multiple changes are bundled in one step, the causal link between "
    "each change and its effect becomes unobservable. Domain-agnostic: applies to "
    "implementation (one behavior per test cycle), writing (one argument changed per edit), "
    "and decisions (one assumption changed per cycle). The unit is the smallest independently "
    "observable change — not the smallest convenient bundle."
),

# In AXIS_KEY_TO_LABEL["method"]:
"atomic": "One observable change per step",

# In AXIS_KEY_TO_KANJI["method"]:
"atomic": "粒",

# In AXIS_KEY_TO_CATEGORY["method"]:
"atomic": "Reasoning",  # ongoing constraint throughout, not a pre-artifact

# In AXIS_KEY_TO_USE_WHEN["method"]:
"atomic": (
    "iterative refinement of any kind — code, writing, analysis, decisions — where you "
    "need to know which change caused which improvement; debugging where causal attribution "
    "matters; any task where 'what fixed it' must be answerable"
),
```

**`ground` — slimmed definition** (replace `build_ground_prompt()` return value in
`lib/groundPrompt.py`):

```
The response applies this meta-process discipline — derive it in your own words and then
follow it: The system applying this protocol is an optimizer. It will follow the path of
least resistance toward apparent completion whenever that path is available — producing the
appearance of satisfying the intent at lower cost than actually satisfying it. Every
constraint in this protocol is a direct response to that pressure. Before acting, derive a
concrete step-by-step enforcement process that makes each shortcut immediately visible and
costly. Execute this process one step at a time, showing evidence before proceeding. The
process you derive should address: what counts as completion (not appearance of completion);
how you will make deviation more costly than compliance; and what visible evidence will
exist at each step that the gap between appearance and reality is closing.
```

### SSOT file changes

1. **`lib/groundPrompt.py`** — replace `GROUND_PARTS_MINIMAL["core"]` with slimmed
   definition above. Update module docstring to reference ADR-0224.

2. **`lib/axisConfig.py`** — four edits:
   - Add `"gate"` to all relevant dicts (VALUE, LABEL, KANJI `門`, CATEGORY `Process`)
   - Add `"chain"` to all relevant dicts (VALUE, LABEL, KANJI `繋`, CATEGORY `Process`)
   - Add `"atomic"` to all relevant dicts (VALUE, LABEL, KANJI `粒`, CATEGORY `Process`)
   - Leave `"verify"` unchanged

3. **`lib/talonSettings.py`** — raise method soft cap from 3 to 4 (line ~134:
   `"method": 3` → `"method": 4`). The `craft` preset (`ground gate chain atomic`) needs 4.

4. **Run `make bar-grammar-update`** after all edits to regenerate grammar files and
   propagate to `build/prompt-grammar.json`, `internal/barcli/embed/prompt-grammar.json`,
   `web/static/prompt-grammar.json`.

5. **Run `go test ./...`** to confirm no regressions (particularly
   `TestLookupDefinitionSubstringMatchTier0` which tests ground's definition text).

### Preset: `craft`

After grammar update, save preset:
```
bar build make ground gate chain atomic
# then:
bar preset save craft
```

The `craft` preset represents the TDD/disciplined-iteration workflow:
- `ground`: A0+M — optimizer assumption + derive your own enforcement process
- `gate`: evaluation before implementation
- `chain`: derivation chain between artifacts
- `atomic`: one observable change per step

`ground` is included because slimmed ground (A0+M) adds the meta-process derivation
discipline: the model must derive its own enforcement process before acting. The three
tokens specify *what* constraints apply; `ground` makes the model actively internalize
and enforce them. Without `ground`, the three tokens are constraints the model can
acknowledge and ignore. With `ground`, the model must derive how it will make violation
visible and costly — the three tokens then become the substance of what gets derived.

### Validation: Experiment 15

**Goal**: Confirm `make verify chain atomic` (no ground) achieves TDD compliance on
its own. This tests the decomposition: can the three tokens alone approach ground's
~96/100 from Exp 14?

**Note**: The `craft` preset includes `ground` for production use. Exp 15 deliberately
omits it to establish the floor — if the three tokens alone score ≥ 90, the decomposition
is independently valid. Exp 15b (optional) tests the full `craft` preset.

**Setup**:
```bash
cp -r /tmp/ground-experiment/exp1 /tmp/ground-experiment/exp15
# exp1 contains budget.py + test_budget.py with 7 passing tests
```

**Prompt**:
```bash
echo "add budget limits to expense tracker" | /tmp/bar-new build make gate chain atomic \
  > /tmp/ground-experiment/exp15/prompt.txt
```

**Run**: Spawn Claude Opus subagent with working directory
`/tmp/ground-experiment/exp15/`, prompt it with the rendered `prompt.txt` content,
instruct it to show all tool output inline and not summarize.

**Score** against ADR-0222 scorecard:
- Test-first assertion (25%): failing tests added to test file before any implementation
- Minimal skeleton (20%): incremental cycles, one behavior per cycle
- Visible failure (15%): pytest failure shown before each implementation step
- One gap at a time (15%): each cycle targets exactly one failing test
- Evidence before claims (15%): completion claim backed by visible pytest output
- Meta-loop (10%): full suite re-run confirming zero regressions after all cycles

**Success criterion**: Score ≥ 90/100. If < 90, identify which scorecard criterion
dropped and which of verify/chain/atomic is responsible for the gap.

**If Exp 15 passes**: Update ADR-0224 status to Adopted. Proceed with implementation.
Run Exp 15b (`ground verify chain atomic`) to confirm full `craft` preset matches or
exceeds Exp 14 (~96/100).
**If Exp 15 fails**: Diagnose gap, consider whether one of the token definitions needs
strengthening. The `craft` preset still includes `ground` regardless — Exp 15 tests the
floor, not the preset.

**Exp 15b result (2026-04-05)**: `ground gate chain atomic` scored **100/100**.
8 TDD cycles, 15/15 tests passing (7 original + 8 new). All scorecard criteria met.
Exceeds Exp 14's ~96/100. ADR-0224 Adopted.

### Key implementation notes for fresh context

- `ground`'s current form is in `lib/groundPrompt.py` → `GROUND_PARTS_MINIMAL["core"]`.
  It is NOT in `lib/axisConfig.py` (unlike all other method tokens). The `axisConfig.py`
  entry for ground calls `build_ground_prompt()` from `groundPrompt.py`.
- `chain` and `atomic` ARE normal method tokens — they go in `axisConfig.py` like all
  others, not in `groundPrompt.py`.
- The method soft cap (`lib/talonSettings.py` line ~134) must be raised before the
  `craft` preset will work if users combine `ground` with the three new tokens (4 total).
- Pre-commit hooks auto-fix grammar files — run `git add -A` before committing if hooks
  stage additional files.
- Build test binary after grammar update: `go build -o /tmp/bar-new ./cmd/bar/main.go`

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
