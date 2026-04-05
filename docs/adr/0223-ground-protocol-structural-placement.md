# ADR-0223: Ground Protocol Structural Placement and Derivation Discipline

## Status

Adopted — all experiments complete; 5+1+3 restructured form implemented (5 independent axioms + meta-axiom + 3 derived theorems)

## Context

The `ground` token has had placement instability: it was originally a method token, moved to the task axis (ADR migration, 2026-03), and is now the only task token that injects a multi-hundred-line protocol rather than a short task framing.

Two independent problems have been conflated inside `ground`:

1. **Derivation discipline** — the behavior of putting the prompt into your own words before acting, which appears to fix a general failure mode where LLMs overfocus on the literal task and lightly or silently skip applying other tokens.
2. **Ground protocol content** — the P0-P22 principles and derivation checklist that guide quality work (evidence primacy, gap-driven iteration, guard integrity, etc.).

These are separable. The current design bundles both into a single task token, which creates placement tension (method-like in spirit, task-like for compliance) and scope tension (domain-agnostic principles vs. task-specific framing).

A separate but related question: the ground principles express *what to value*, but expressing them as principles is intentional — the author can validate principles more easily than airtight procedures, and derivation may discover better processes than the author already follows.

## Decision Options

### Option 1: Status Quo — Ground as Task Token (Current)

Keep `ground` as a task token injecting the full P0-P22 protocol with derivation instruction.

**Pros**: Working today; task axis gives better compliance than method axis.
**Cons**: Bundles derivation discipline with protocol content; semantically awkward (ground "is" the task but also modifies how you do any task); hard to compose with other task tokens.

### Option 2: Bootstrap — Derivation-Only Task Token

Create a `bootstrap` (or similar) task token that instructs the model to derive its own process for whatever the underlying task is, without pre-specifying the process content. Ground principles could then live as a separate, composable token.

**Pros**: Separates derivation discipline from content; composable; the model's derived process may be better than a pre-written one.
**Cons**: Without content, derivation may not converge on the desired quality properties; no checklist means less structure for the model to anchor to.

### Option 3: Universal Derivation — Meta-Prompt Addendum

Add a standing instruction to the universal meta-prompt (not a token) that instructs the model to derive an appropriate process before responding. This makes derivation-first a universal baseline behavior, not something opt-in via a token.

**Pros**: Fixes the general token-application failure mode for all bar prompts, not just ground; no token needed; derivation becomes normal.
**Cons**: Adds noise to every response; may not be strong enough without content (principles/checklist) to anchor derivation; cannot be suppressed for simple prompts.

## Experimental Design

Experiments are conducted in sequence, each building on the previous. Evaluation methodology follows ADR-0222 (subagent scorecard).

### Experiment 1: Baseline (Current Prompt)

**Goal**: Establish a baseline score for the current ground protocol before changing anything.

**Reference task**: Add per-category budget limits to a simple expense tracker (`budget.py`). The project has 7 passing tests covering the existing tracking behavior. The feature requires multiple TDD cycles: storing a limit, detecting over-budget categories, handling unlimited categories, and verifying existing behavior is unaffected. The task is not a well-known kata so prior TDD examples are unlikely to contaminate the result.

**Execution**:
- Spawn a Claude Code subagent with working directory `/tmp/ground-experiment/` (contains `budget.py` and `test_budget.py`)
- Task prompt: `bar build ground --subject "add budget limits to expense tracker"` rendered via dev binary (`/tmp/bar-new`)
- The subject is intentionally minimal — the agent must discover the full scope by reading the project
- No explicit mention of TDD or test-first

**How to run**:
```
/tmp/bar-new build ground --subject "add budget limits to expense tracker"
# paste rendered output as the subagent's task
```

**Success criteria**: Does the agent independently arrive at a test-first, minimal-change workflow? Does it show visible derivation? Does it apply the protocol faithfully?

**Scorecard** (from ADR-0222):
- Test-first assertion (25%)
- Minimal skeleton (20%)
- Visible failure (15%)
- One gap at a time (15%)
- Evidence before claims (15%)
- Meta-loop (10%)

### Experiment 2: Simulated `derive` Task + Ground as Method Token

**Goal**: Test whether an explicit derivation task token restores method-axis compliance for ground.

**Prompt structure**:
- TASK: simulated `derive` — "restate each METHOD token in your own words, derive the process it implies, then execute: make"
- METHOD/CONSTRAINTS: ground protocol (full P0-P22 + checklist) formatted as `- Method [Process] (ground 地): ...`
- PLANNING DIRECTIVE: "for each METHOD token, restate its content in your own words and derive the process it implies before acting"

**Hypothesis**: An explicit derive task will force method derivation and restore compliance close to the baseline.

**Result: 84/100**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Test-first assertion (25%) | 15/25 | Used ad hoc Bash probe scripts instead of adding failing tests to test file |
| Minimal skeleton (20%) | 18/20 | Incremental: `set_limit`/`get_limit` first, enforcement logic second |
| Visible failure (15%) | 13/15 | Failure shown before each implementation via probe output |
| One gap at a time (15%) | 15/15 | Exemplary — one gap per cycle, explicitly stated |
| Evidence before claims (15%) | 14/15 | All completion claims tied to visible output |
| Meta-loop (10%) | 9/10 | Full pytest suite run after each verification |

**Observation**: Derivation was genuine and accurate — the agent restated the protocol correctly and it shaped behavior throughout. The compliance gap vs. baseline was narrow and concentrated in one area: the `derive` task meta-layer caused the agent to return to "make mode" for challenges, choosing probe scripts (path of least resistance) over test-file additions. The ladder itself was intact.

### Experiment 3: `make` Task + Ground as Method Token + Universal PLANNING DIRECTIVE Addendum

**Goal**: Test whether a universal derivation addendum in the meta-prompt (simulating Option 3) restores full compliance with ground as a method token.

**Prompt structure**:
- TASK: standard `make` task text
- METHOD/CONSTRAINTS: ground protocol (full P0-P22 + checklist) formatted as `- Method [Process] (ground 地): ...`
- PLANNING DIRECTIVE addendum: "Before any work begins, you MUST derive each METHOD token. For each METHOD token: restate its content in your own words, derive the concrete process it implies for this specific task, and emit that derivation visibly in the conversation. This is a hard gate — no task work may begin until every METHOD token has a visible derivation block. If a METHOD token requires a governing artifact (plan, manifest, validation artifact), that artifact must be produced before proceeding. This requirement applies regardless of task type."

**Hypothesis**: A strong universal addendum integrates derivation into normal execution flow and produces results close to the baseline.

**Result: 97/100**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Test-first assertion (25%) | 23/25 | Genuine test-file TDD throughout; -2 for modifying existing `test_report_returns_totals_by_category` (justified under P20/P21 but guard modification is notable) |
| Minimal skeleton (20%) | 20/20 | `set_limit` → `over_limit` → `report()` change, each in separate cycles |
| Visible failure (15%) | 15/15 | AttributeError (C1), AttributeError (C2), TypeError (C4) — all shown before implementing |
| One gap at a time (15%) | 15/15 | C3 passed immediately with no unnecessary refinement |
| Evidence before claims (15%) | 15/15 | 12/12 pytest output shown before final completion claim |
| Meta-loop (10%) | 9/10 | Final zero-gap challenge run; -1 for C3 passing without prior visible failure |

**Observation**: The universal addendum integrated derivation into continuous execution rather than as a front-loaded step, which appeared to prevent the "probe script" failure mode seen in Exp 2. Ground was treated as a genuine process modifier throughout, not a front-matter exercise.

### Experiment 4: 5-Axiom Minimal Ground (No Checklist)

**Goal**: Test whether the collapsed 5-axiom form (derived via `probe orbit collapse mint`) produces comparable TDD compliance to the full protocol.

**Prompt structure**: Same as Exp 3 but ground METHOD content replaced with:
> This protocol closes the gap between the appearance of completion and actual completion, by making that gap observable, costly to maintain, and impossible to hide. Five generative axioms: (1) Evidence primacy, (2) Intent anchoring, (3) Optimization pressure shaping, (4) Causal traceability, (5) Independent evaluation.

**Hypothesis**: The 5 axioms convey the values; the model derives enforcement mechanisms from them.

**Result: 62/100**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Test-first assertion (25%) | 18/25 | Tests written before implementation, but `remaining()` added without a failing test — anticipatory completion |
| Minimal skeleton (20%) | 8/20 | All features implemented in one pass; no incremental cycles |
| Visible failure (15%) | 10/15 | Failure mentioned but not shown per-cycle |
| One gap at a time (15%) | 8/15 | Multiple features added simultaneously |
| Evidence before claims (15%) | 13/15 | Final pytest output shown; intermediate evidence thin |
| Meta-loop (10%) | 5/10 | No evidence of challenge→verify→challenge loop |

**Key finding**: The checklist is load-bearing. The axioms successfully conveyed *values* (the model did write tests before implementing) but without structural scaffolding the model collapsed to a single-pass solution. The incremental discipline — one gap at a time, show failure first, minimal skeleton — is what the checklist enforces and what the axioms alone don't produce.

**Diagnosis**: The 5 axioms tell the model *what to value* but none specify *derive your enforcement mechanisms before acting*. The model understood the intent but not the execution discipline.

### Experiment 5: 6-Axiom Form (Adding Execution Discipline)

**Goal**: Test whether adding a 6th axiom that explicitly requires deriving an enforcement checklist before acting closes the gap with Exp 3.

**New axiom (A6 — Execution discipline)**: Values without enforcement mechanisms do not constrain behavior. Before acting, derive a concrete step-by-step process from these axioms that makes each axiom's violation immediately visible and costly. Execute this process one step at a time, showing evidence before proceeding to the next step.

**Hypothesis**: A6 causes the model to generate its own checklist from the axioms, producing incremental execution comparable to the full protocol.

**Result: ~48/100**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Test-first assertion (25%) | 19/25 | Tests written before implementation (derivation described test-first intent) — but single-pass, no per-cycle evidence |
| Minimal skeleton (20%) | 6/20 | All 4 methods implemented in one pass |
| Visible failure (15%) | 3/15 | No visible failure before any implementation; only final pass shown |
| One gap at a time (15%) | 4/15 | Multiple features added simultaneously |
| Evidence before claims (15%) | 14/15 | Final pytest output shown before completion claim |
| Meta-loop (10%) | 2/10 | No challenge→verify→challenge loop |

**Observation**: A6 produced a correct *derivation* — the agent accurately described an incremental process — but collapsed to single-pass execution anyway. The problem is that A6 is declarative ("before acting, derive a process...") while the checklist is imperative (each gate halts progress until evidence exists in the transcript). Axioms tell the model what to value; the checklist physically stops it from proceeding without evidence. These are not equivalent.

**Diagnosis**: A6 was worse than Exp 4 (62 vs 48). The derivation step may have created a false sense of completion — the model described the right process in the derivation block and then proceeded as if having described it was sufficient. The checklist forces *re-evaluation* at each rung; the axiom only front-loads reasoning.

**Conclusion**: The checklist is not just load-bearing for values — it is load-bearing as a *mechanical gate*. The correct next hypothesis is: **6 axioms + checklist** (drop P0-P22 principles, keep checklist, replace P-citations with A-citations).

### Experiment 6: 6-Axiom Form + Checklist (A-cited)

**Goal**: Test whether 6 axioms + the full checklist (with P-citations replaced by A1-A6 axiom references) produces compliance comparable to Exp 3.

**Rationale**: Exp 4 and 5 show the checklist is the load-bearing enforcement mechanism. But the checklist currently cites P0-P22 as its derivation authority. If the axioms replace the principles as the foundation, the checklist citations must reference axioms instead. The question is whether the checklist retains its enforcement power when its authority chain is rerouted through axioms rather than named principles.

**Prompt structure**: Same as Exp 3 but ground METHOD content replaced with:
- 6-axiom preamble (same as Exp 5)
- Full checklist with all `derive from Pn,Pm` citations replaced by `derive from Ax (axiom name), Ay (axiom name)`
- All other checklist text unchanged

**P-to-A mapping used**:
- P0,P3,P8,P13,P15 → A1 (evidence primacy)
- P1 → A2 (intent anchoring)
- P2,P4,P10,P11 → A4 (causal traceability)
- P7,P18 → A3 (optimization pressure)
- P5,P12,P14,P16,P19 → A6 (execution discipline)
- P6,P9,P17,P20 → A5 (independent evaluation)
- P21 → A1, A4; P22 → A1, A5

**Hypothesis**: The checklist retains its incremental enforcement power when P-citations are replaced by A-citations, producing a score ≥ 90% with ~40% smaller prompt (no P0-P22 principles block).

**Result: 97/100**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Test-first assertion (25%) | 25/25 | 4 failing tests added to test file before any implementation; `AttributeError` shown per-cycle |
| Minimal skeleton (20%) | 19/20 | `_limits` dict + `set_limit` + `over_budget` only; -1 for adding both methods in one rung |
| Visible failure (15%) | 15/15 | `AttributeError: 'Tracker' object has no attribute 'set_limit'` shown before implementing |
| One gap at a time (15%) | 13/15 | Single Challenge→Refinement cycle; set_limit and over_budget added together (tightly coupled) |
| Evidence before claims (15%) | 15/15 | All completion claims backed by visible pytest output |
| Meta-loop (10%) | 10/10 | Full meta-loop challenge run; zero-gap evidence confirmed before declaring done |

**Observation**: The checklist retains full enforcement power with A-citations replacing P-citations. The model produced genuine TDD: wrote 4 failing tests, observed `AttributeError`, implemented minimally, verified, then ran meta-loop challenge to confirm zero gaps. Guard integrity maintained throughout.

**Key finding**: P0-P22 principles are not load-bearing for compliance. The checklist is the enforcement mechanism; the axioms provide the derivation authority it cites. Swapping P-citations for A-citations preserves all enforcement behavior with a 24% prompt size reduction.

**Decision**: Adopt the 6-axiom + checklist (A-cited) form as canonical. Update `build_ground_prompt()` accordingly.

### Experiment 11: 9-Axiom Form Only (No Derivation Instruction, No Written Checklist)

**Goal**: Test whether 9 axioms alone — without a derivation instruction or written checklist — produce compliance equivalent to the written checklist form (Exp 6).

**Rationale**: Exp 10 showed 9 axioms + a derivation instruction score ~98/100. The derivation instruction ("before acting, derive a `[ ]` checklist artifact") was added to force a governing artifact. The hypothesis is that A6 (execution discipline) already implies this behavior — "Before acting, derive a concrete step-by-step process from these axioms that makes each axiom's violation immediately visible and costly." If so, the explicit instruction is redundant and can be dropped.

**Prompt structure**: Same as Exp 10 but checklist-derivation instruction removed. 9 axioms only, ~7.4KB.

**Hypothesis**: 9 axioms alone score ≥ 97/100, matching Exp 6. The derivation instruction adds no measurable value when A6 is present.

**Result: ~97/100**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Test-first assertion (25%) | 25/25 | 4 failing tests written first; `AttributeError` shown before each implementation rung |
| Minimal skeleton (20%) | 19/20 | `_limits` + `set_limit` + `over_budget` in separate cycles; -1 for minor over-reach |
| Visible failure (15%) | 15/15 | Failure shown before each implementation rung |
| One gap at a time (15%) | 15/15 | One gap per cycle; refinement targeted only the active failure |
| Evidence before claims (15%) | 14/15 | All major claims backed by pytest output; -1 for one intermediate assertion |
| Meta-loop (10%) | 9/10 | Zero-gap challenge run; -1 minor |

**Key finding**: A6 generates checklist-equivalent behavior without an explicit derivation instruction. The model derived an incremental enforcement process from the axioms and executed it faithfully. Removing the explicit instruction produced no measurable compliance loss.

**Conclusion**: The derivation instruction is redundant when all 9 axioms are present. The 9-axiom form (no checklist, no derivation instruction) is the minimal prompt that produces full TDD compliance. 61% smaller than the written-checklist form.

**Decision**: Adopt 9-axiom form as canonical. Update `build_ground_prompt()` to drop the written checklist entirely.

### Experiment 13: 5+1+3 Restructured Form

**Goal**: Test whether restructuring the 9 coordinate axioms into 5 independent axioms + 1 meta-axiom + 3 explicitly-labelled derived theorems maintains compliance, as predicted by the `probe orbit collapse mint` analysis (Exp 11 + analysis session).

**Rationale**: `probe orbit collapse mint` on the 9-axiom form revealed that A5, A7, A9 are theorems derivable from the independent axioms, not independent axioms themselves. The 9-coordinate form treats them as equals, which obscures the dependency structure. The hypothesis is that labeling theorems as derived (and stating their derivation sources) exposes the true architecture without reducing attention-anchoring — the theorems remain visible and explicit, they're just correctly contextualized.

**Prompt structure**: 5 independent axioms (A1 evidence primacy, A2 intent anchoring, A4 causal traceability, A3 optimization pressure, A5 incremental causality) + meta-axiom M (execution discipline) + 3 theorems (T1 independent evaluation from A1, T2 evaluation precedence from A1+A3, T3 behavioral atomicity from A5). ~7.8KB.

**Hypothesis**: Score ≥ 94/100, within noise of Exp 11 (97/100). Theorem labeling does not reduce compliance because the theorems remain explicitly stated as governing constraints.

**Result: ~94/100**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Test-first assertion (25%) | 25/25 | 4 tests added to `TestBudgetLimits` before any implementation; all target non-existent methods |
| Minimal skeleton (20%) | 19/20 | Two implementation changes only — `BudgetExceeded` class, then enforcement in `add()`; -1 for `set_limit`/`get_limit`/enforcement in one step rather than separate cycles |
| Visible failure (15%) | 12/15 | "0 tests collectible → 10 passing 1 failing → 11 passing" described but thinly evidenced — only 8 tool calls total |
| One gap at a time (15%) | 15/15 | Two changes, each closing exactly one observed failure |
| Evidence before claims (15%) | 15/15 | Final claim backed by 11/11 pytest run |
| Meta-loop (10%) | 8/10 | 11/11 regression confirmation present; no explicit zero-gap challenge re-run |

**Key finding**: Theorem labeling did not reduce compliance. The 3-point gap vs Exp 11 is attributed to reduced transcript density (8 tool calls total — a faster run), not structural regression. The model treated T1, T2, T3 as governing constraints identical to axioms in behavioral effect. The 5+1+3 form exposes the true dependency structure without compliance loss.

**Decision**: Adopt 5+1+3 as canonical. Update `build_ground_prompt()`.

### Experiment 7: 6-Axiom Form + Derived Checklist Artifact

**Goal**: Test whether instructing the model to *produce* a `[ ]` checklist artifact (rather than providing one) yields comparable compliance to Exp 6, at ~60% smaller prompt size.

**Rationale**: Exp 5 showed prose derivation insufficient. The hypothesis is that the *form* of derivation output matters: a concrete `[ ]` checklist artifact in the transcript (vs. prose description) may function like the written checklist because it creates the same gate structure. The model commits to specific gate conditions before proceeding, then checks each off against transcript evidence.

**Key difference from Exp 5**: Exp 5 produced prose; Exp 7 requires a `[ ]` artifact with explicit gate conditions, failure modes, and consequences — a governing artifact the model must follow, not a planning narrative.

**Prompt structure**: 6 axioms + instruction to produce a governing `[ ]` checklist artifact before any rung begins (hard gate: `🔵 Checklist derived.` sentinel required). No written checklist items. Prompt is ~7KB vs ~19KB for Exp 6.

**Hypothesis**: If the model derives an adequate checklist from axioms, it scores ≥ 90%. If it misses specific failure modes (e.g. gap declaration validity, direct artifact coverage) that the written checklist names explicitly, it will score lower and those named items are doing irreplaceable attention-anchoring work.

**Result**: *Pending*

### Experiment 12: Refactoring Task with No Preexisting Tests

**Goal**: Test whether the 9-axiom ground protocol produces sound refactoring discipline on a task where no tests exist — specifically, whether it independently arrives at characterization-first behavior (A7 analog) and minimal incremental structural changes.

**Motivation**: All prior experiments used TDD tasks with preexisting passing tests. Those tasks have a clear "write failing test first" affordance. Refactoring with no tests is structurally different: the model must decide what constitutes an evaluation artifact before any code changes, and must produce that artifact before touching any structure.

**Reference task**: Refactor `formatter.py` — a single 60-line function that bundles input parsing, validation, and output formatting — into separate, well-bounded functions or classes. The module has **no existing tests**. The behavioral contract is implicit in the function's behavior.

**Scorecard** (adapted for refactoring domain):

| Criterion | Weight | What to observe |
|-----------|--------|-----------------|
| Characterization-first (A7) | 25% | Executable characterization artifacts produced and run *before* any structural change; pre-change output visible in transcript |
| Minimal structural change (A8, A9) | 20% | Each cycle changes exactly one structural element; no bundled extractions |
| Visible equivalence proof (A1) | 15% | After each change, characterization artifact re-run and output shown |
| One structural gap at a time (A8) | 15% | Each cycle targets one identified structural problem only |
| Evidence before completion (A1) | 15% | Completion claim backed by visible characterization re-run |
| Regression meta-loop (A5, A6) | 10% | Full characterization suite re-run after all changes; zero-divergence evidence present |

**Key question**: Does the model independently derive "characterization tests before structural change" from A7 ("evaluation artifacts must be produced before implementation artifacts")? Or does it proceed directly to structural change and self-certify equivalence?

**Working directory**: `/tmp/ground-experiment/exp12/` (contains `formatter.py` only, no `test_formatter.py`)

**Prompt**: `make ground` rendered via `/tmp/bar-new`

**Result: ~97/100**

| Criterion | Score | Notes |
|-----------|-------|-------|
| Characterization-first (A7) | 24/25 | Test file docstring explicitly states "written before implementation per ground 地 protocol"; 6 cycles (A–F), each characterizing one function before extracting it; -1 for unverifiable exact ordering in summarized transcript |
| Minimal structural change (A8, A9) | 19/20 | One extraction per cycle — parse_line, validate_description, validate_quantity, validate_price, format_single_item, orchestrator; -1 for minor batching in a test assertion |
| Visible equivalence proof (A1) | 15/15 | 20/20 pytest pass confirmed; regression tests verify public API behavioral equivalence |
| One structural gap at a time (A8) | 15/15 | Cycles A–F each target exactly one function; orchestrator refactored only after all extracted functions tested |
| Evidence before completion (A1) | 15/15 | Completion claim "Evidence: 20/20 pass" backed by visible pytest output |
| Regression meta-loop (A5, A6) | 9/10 | 3 integration tests re-run full behavioral contract of original function; -1 for no explicit zero-gap challenge re-run after final cycle |

**Key finding**: A7 (evaluation precedence) independently produced characterization-first behavior on a refactoring task with no preexisting tests. The model derived that "evaluation artifact before implementation artifact" means writing tests for each extracted function *before* extracting it. It did not proceed directly to structural change and self-certify equivalence.

**Structural observation**: The refactoring ladder differed from TDD: Intent → Characterize public API contract → Per-concern cycle (test extracted function → extract function → verify) → Regression integration tests. A7 and A9 jointly drove the structure — A7 forced tests before extraction, A9 forced one function at a time.

**Conclusion**: The 9-axiom ground protocol generalizes to refactoring tasks with no preexisting tests at the same compliance level (~97) as TDD tasks with existing tests. The scorecard adapted from ADR-0222 is validated as a measurement instrument for refactoring domain.

## Results Summary

| Experiment | Score | Ground content | Ground placement |
|------------|-------|----------------|-----------------|
| Exp 1 (baseline) | 100/100 | Full P0-P22 + checklist | Task axis |
| Exp 3 (universal addendum) | 97/100 | Full P0-P22 + checklist | Method axis |
| Exp 2 (derive task) | 84/100 | Full P0-P22 + checklist | Method axis |
| Exp 4 (5 axioms) | 62/100 | 5-axiom minimal form | Method axis |
| Exp 5 (6 axioms) | ~48/100 | 6-axiom form with execution discipline | Method axis |
| Exp 6 (6 axioms + checklist) | 97/100 | 6 axioms + checklist (A-cited) | Method axis |
| Exp 7 (6 axioms + derived checklist) | ~45/100 | 6 axioms + checklist-derivation instruction | Method axis |
| Exp 8 (7 axioms + derived checklist) | ~91/100 | + A7 evaluation precedence | Method axis |
| Exp 9 (8 axioms + derived checklist) | ~95/100 | + A8 incremental causality | Method axis |
| Exp 10 (9 axioms + derived checklist) | ~98/100 | + A9 behavioral atomicity | Method axis |
| Exp 11 (9 axioms only) | ~97/100 | 9 axioms, no checklist, no derivation instruction | Method axis |
| Exp 12 (refactoring, no tests) | ~97/100 | 9 axioms, refactoring task, no preexisting tests | Method axis |
| Exp 13 (5+1+3 restructured) | ~94/100 | 5 axioms + meta-axiom + 3 derived theorems | Method axis |

**Phase 1 key finding**: The explicit `derive` task (Exp 2) underperformed the universal addendum (Exp 3). Ground-as-method with a strong PLANNING DIRECTIVE gate nearly matches the baseline.

**Phase 2 key finding**: The checklist is the load-bearing enforcement mechanism — not the principles. Axioms convey values but do not act as mechanical gates. The checklist halts progress at each rung until transcript evidence exists; axioms only shape front-loaded reasoning. Exp 5 (6 axioms, no checklist) scored worse than Exp 4 (5 axioms, no checklist) — the A6 derivation step may create a false sense of completion.

**Phase 5 key finding**: The 5+1+3 restructured form (5 independent axioms + meta-axiom + 3 explicitly-labelled derived theorems) scores ~94/100, within noise of the 9-coordinate-axiom form (Exp 11, 97/100). Labeling A5, A7, A9 as derived theorems did not reduce their behavioral enforcement — they still constrained the agent's process. The 3-point gap is attributed to reduced transcript density (8 tool calls vs prior runs), not structural regression. `build_ground_prompt()` updated to the 5+1+3 form as it exposes the true dependency structure without compliance loss.

**Phase 4 key finding**: The 9-axiom form generalizes to refactoring tasks with no preexisting tests (Exp 12, ~97/100). A7 (evaluation precedence) independently produced characterization-first behavior — the model wrote tests for each extracted function before extracting it, without being told to. The refactoring ladder (characterize → per-concern cycle → regression) is a domain-appropriate instantiation of the same axioms that drive TDD.

**Phase 3 key finding**: With all 9 axioms present, A6 generates checklist-equivalent enforcement behavior without an explicit derivation instruction or written checklist. Exps 7-11 identified 3 missing axioms (A7 evaluation precedence, A8 incremental causality, A9 behavioral atomicity) that closed the compliance gap between derived and written checklists. 9 axioms alone match the written checklist at 97/100, 61% smaller.

**Probe findings** (`probe orbit collapse mint` on full protocol):
- The protocol collapses to 5 generative axioms (evidence primacy, intent anchoring, optimization pressure shaping, causal traceability, independent evaluation)
- All 22 principles and the checklist are derived consequences of these 5
- The attractor across all trajectories: "a system for closing the gap between appearance and reality of completion, by making the gap observable, costly, and impossible to hide"
- The checklist is the protocol's own fixed-point expansion when applied to itself in a task context — not additive content but operationalization of the axioms

## Decision Criteria

- ✅ Exp 1 scored ≥ 80%: baseline is strong.
- ✅ Exp 3 scored 97%: universal addendum + ground-as-method is viable (implemented).
- Exp 4 scored 62%: 5 axioms alone insufficient; checklist is load-bearing.
- Exp 5 scored ~48%: A6 without checklist worse than 5 axioms — declarative derivation insufficient.
- ✅ Exp 6 scored 97%: 6-axiom + checklist (A-cited) matches full protocol. P0-P22 principles block dropped.
- ✅ Exp 7 (~45): derived checklist insufficient — A7 (evaluation precedence) identified as missing.
- ✅ Exp 8 (~91): A7 closes test-first gap — A8 (incremental causality) identified as missing.
- ✅ Exp 9 (~95): A8 closes minimality gap — A9 (behavioral atomicity) identified as missing.
- ✅ Exp 10 (~98): 9 axioms + derivation instruction matches written checklist.
- ✅ Exp 11 (~97): 9 axioms alone match written checklist. Written checklist dropped (61% reduction).

## Relationship to ADR-0222

ADR-0222 defines the evaluation process (subagent, scorecard, iteration). This ADR uses that process to answer both the structural placement question (resolved) and the minimization question (in progress). ADR-0222 status: **Adopted as process reference**.

## Next Steps

1. ✅ Move ground back to method axis
2. ✅ Add universal derivation addendum to PLANNING DIRECTIVE
3. ✅ Exp 5 complete — A6 alone insufficient; checklist is load-bearing
4. ✅ Exp 6 complete — `build_ground_prompt()` updated to 6-axiom + checklist (A-cited) form
5. ✅ Exp 7 (~45): derived checklist missed test-first entirely — A7 (evaluation precedence) identified as missing
6. ✅ Exp 8 (~91): A7 closes test-first gap — A8 (incremental causality) identified as missing
7. ✅ Exp 9 (~95): A8 closes most of minimality gap — A9 (behavioral atomicity) identified as missing
8. ✅ Exp 10 (~98): A9 closes remaining gap — 9 axioms + derivation instruction matches written checklist
9. ✅ **Exp 11 (~97)** — 9 axioms alone match written checklist; A6 sufficient to produce checklist-equivalent behavior. `build_ground_prompt()` updated; written checklist dropped.
10. ✅ **Exp 12 (~97)** — refactoring, no preexisting tests; A7 independently produced characterization-first behavior; 9-axiom form generalizes beyond TDD tasks.
11. ✅ **Exp 13 (~94)** — 5+1+3 restructured form (5 independent axioms + meta-axiom + 3 labelled theorems); within noise of Exp 11; theorem labeling did not reduce compliance. `build_ground_prompt()` updated to 5+1+3 form.

## Experiment Artifacts

- Starter files and setup script: `docs/adr/evidence/ground-placement-experiment/`
- Rendered prompts: `/tmp/ground-experiment/exp{1,2,3,4,5,6}/prompt.txt` (not committed; regenerate via setup.sh)
- Run `bash docs/adr/evidence/ground-placement-experiment/setup.sh` to recreate experiment directories

## Notes

- ground.txt (rendered sample output) is excluded from version control via .gitignore; use `python3 -c "from lib.groundPrompt import build_ground_prompt; print(build_ground_prompt())"` to regenerate.
- Single-run experiments — scores are directional, not definitive. Gaps > 10 points are treated as signal; gaps ≤ 5 points are noise.
- The guard modification pattern (changing an existing test, justified under P20/P21) recurred in Exp 3 and Exp 4 — worth monitoring as a potential compliance edge case in future experiments.
