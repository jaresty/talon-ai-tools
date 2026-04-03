# ADR-0223: Ground Protocol Structural Placement and Derivation Discipline

## Status

Experiments complete — pending decision on implementation

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

## Results Summary

| Experiment | Score | Ground placement | Derivation mechanism |
|------------|-------|-----------------|----------------------|
| Exp 1 (baseline) | 100/100 | Task | Built into task text |
| Exp 2 (derive task) | 84/100 | Method | Explicit `derive` task token (simulated) |
| Exp 3 (universal addendum) | 97/100 | Method | Universal PLANNING DIRECTIVE addendum |

**Key finding**: The explicit `derive` task (Exp 2) underperformed the universal addendum (Exp 3). The likely cause: a dedicated derive task creates a meta-layer that the agent discharges and then exits, returning to normal "make mode" for execution. The universal addendum keeps derivation integrated throughout execution rather than treating it as a precondition to check off.

**Surprising result**: Exp 3 nearly matches the baseline (Exp 1) despite ground living in the METHOD section. This suggests the original method-axis compliance failure was not caused by the method axis itself, but by the *absence of a strong derivation gate* in the meta-prompt. With a sufficiently strong gate, ground-as-method produces near-baseline compliance.

## Decision Criteria

- ✅ Exp 1 scored ≥ 80%: baseline is strong; ground-as-task works.
- Exp 2 scored 84% vs Exp 1 100%: explicit derive task is not sufficient alone; probe-script failure mode is a meaningful gap.
- ✅ Exp 3 scored 97% vs Exp 1 100%: universal addendum approach is viable; gap is within noise for a single-run experiment.
- Option 3 (universal derivation in meta-prompt) is the strongest structural path: it restores ground to the method axis where it belongs semantically, and the addendum benefits *all* bar prompts, not just ground.

## Relationship to ADR-0222

ADR-0222 defines the evaluation process (subagent, scorecard, iteration). This ADR uses that process to answer the structural placement question. ADR-0222 status updated to: **Adopted as process reference**.

## Next Steps

1. **Move ground back to method axis** — revert the task-axis migration; restore to `AXIS_KEY_TO_VALUE["method"]`
2. **Add universal derivation addendum to PLANNING DIRECTIVE** in the bar meta-prompt — the exact wording from Exp 3 is the candidate
3. **Phase 2: minimize ground axioms** — with placement resolved, run ADR-0222 compression experiments to reduce P0-P22 to the minimal set that preserves Exp 3-level compliance

## Experiment Artifacts

- Starter files and setup script: `docs/adr/evidence/ground-placement-experiment/`
- Rendered prompts: `/tmp/ground-experiment/exp{1,2,3}/prompt.txt` (not committed; regenerate via setup.sh)
- Run `bash docs/adr/evidence/ground-placement-experiment/setup.sh` to recreate experiment directories

## Notes

- ground.txt (rendered sample output) is excluded from version control via .gitignore; use `python3 -c "from lib.groundPrompt import build_ground_prompt; print(build_ground_prompt())"` to regenerate.
- Single-run experiment — scores should be treated as directional, not definitive. The 3-point gap between Exp 3 and Exp 1 is within plausible single-run variance.
- The guard modification in Exp 3 (changing an existing test) is worth monitoring in Phase 2 experiments — it was justified under P20/P21 but represents a potential compliance edge case.
