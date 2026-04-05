"""Ground method prompt — structured parts (ADR-0220, ADR-0221, ADR-0223).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make bar-grammar-update`
to propagate changes through to downstream grammar files.

ADR-0220: generalized ground protocol — domain-agnostic derivation ladder.
ADR-0223: structural placement + minimization experiments. Exp 13:
  5+1+3 form — 5 independent axioms + 1 meta-axiom (execution discipline) +
  3 explicitly-labelled derived theorems (independent evaluation, evaluation
  precedence, behavioral atomicity). Tests whether the cleaner dependency
  structure maintains compliance vs. 9 coordinate axioms (Exp 11, 97/100).

Note: ground is a method token (axisConfig.py), not a task token.
GROUND_PARTS_MINIMAL["core"] contains the 5+1+3 form.
"""

# Derived sentinels — model derives sentinels from principles (recursive intent structure).
# Template: declare intent → derive criteria → structure → challenge → refine → verify.
# Levels: session, thread, rung, artifact-edit.

SENTINEL_TEMPLATES: dict[str, str] = {}
_SENTINEL_GATES: dict[str, str] = {}

GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        'This protocol closes the gap between the appearance of completion and actual completion, by making that gap '
        'observable, costly to maintain, and impossible to hide. '
        'Five independent axioms — the irreducible basis: '
        '1. Evidence primacy: Claims require externalized evidence. A model cannot self-certify. '
        '2. Intent anchoring: Intent is the only external anchor for evaluation. Without declared intent outside the '
        'system, drift is undetectable. '
        '3. Causal traceability: Each artifact must derive from its predecessor\'s actual content. Without explicit '
        'derivation chains, conclusions detach from premises. '
        '4. Optimization pressure: The system must make compliance easier than deviation — rules that can be bypassed '
        'cheaply will be bypassed. '
        '5. Incremental causality: Each refinement step must address exactly one observed failure and introduce nothing '
        'beyond what closes it. When multiple gaps are closed simultaneously, the causal link between each specific '
        'change and its specific effect becomes unobservable. Incremental steps are not a discipline preference; they '
        'are the minimum unit of observable causality. '
        'One meta-axiom — governs how the axioms are applied: '
        'M. Execution discipline: Values without enforcement mechanisms do not constrain behavior. Before acting, '
        'derive a concrete step-by-step process from the five axioms that makes each axiom\'s violation immediately '
        'visible and costly. Execute this process one step at a time, showing evidence before proceeding to the next '
        'step. '
        'Three derived theorems — these follow necessarily from the axioms; stated explicitly because they govern '
        'critical decision points: '
        'T1. Independent evaluation (from A1): Evaluation must be structurally separate from the artifact it '
        'evaluates. Self-certification is impossible. '
        'T2. Evaluation precedence (from A1 + A3): Evaluation artifacts must be produced before the implementation '
        'artifacts they evaluate. An evaluation written after the fact cannot expose gaps the implementation was '
        'designed around — the implementation shaped the evaluation\'s assumptions. The only evaluation with causal '
        'authority over an implementation is one that existed before it. '
        'T3. Behavioral atomicity (from A5): The unit of implementation and evaluation is the smallest independently '
        'observable behavior, not a feature or a class of failures. Multiple behaviors that share a failure type are '
        'still distinct units — they must be introduced and verified separately because their correctness is '
        'independent. Batching behaviors by failure type conflates implementation convenience with causal independence.'
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0220: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"] via axisConfig.py.
    ground is a method token — it is not in STATIC_PROMPT_CONFIG.
    """
    return "The response applies this evidence protocol — derive it in your own words and then follow it: " + GROUND_PARTS_MINIMAL["core"]
