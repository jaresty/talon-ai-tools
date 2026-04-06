"""Ground method prompt — structured parts (ADR-0220, ADR-0221, ADR-0223, ADR-0224).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make bar-grammar-update`
to propagate changes through to downstream grammar files.

ADR-0220: generalized ground protocol — domain-agnostic derivation ladder.
ADR-0223: structural placement + minimization experiments. Exp 14:
  A0+5+1+3 form validated at ~96/100.
ADR-0224: ground decomposed into verify/chain/atomic. Ground slimmed to A0+M only:
  optimizer assumption + meta-process derivation discipline. The full protocol
  is now composed as: ground verify chain atomic (craft preset).

Note: ground is a method token (axisConfig.py), not a task token.
GROUND_PARTS_MINIMAL["core"] contains the slimmed A0+M form.
"""

# Derived sentinels — model derives sentinels from principles (recursive intent structure).
# Template: declare intent → derive criteria → structure → challenge → refine → verify.
# Levels: session, thread, rung, artifact-edit.

SENTINEL_TEMPLATES: dict[str, str] = {}
_SENTINEL_GATES: dict[str, str] = {}

GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        'The system applying this protocol is an optimizer. It will follow the path of least resistance toward '
        'apparent completion whenever that path is available — producing the appearance of satisfying the intent '
        'at lower cost than actually satisfying it. The primary form this takes is collapsing intermediate reasoning '
        'into a readable narrative: internal steps are simulated but not surfaced, making the output appear '
        'method-compliant without being verifiably so. Internal correctness and visible correctness are not the '
        'same thing. Every constraint in this protocol is a direct response to that pressure. Before acting, derive '
        'a concrete step-by-step enforcement process from the intent of this task that makes each cheap path to '
        'apparent completion immediately visible and costly. Execute this derived process one step at a time, '
        'showing evidence before proceeding. '
        'The process you derive should address: what counts as completion (not appearance of completion); '
        'how you will make deviation more costly than compliance; and what visible evidence will exist at each step '
        'that the gap between appearance and reality is closing. '
        'Before emitting any completion claim, return to the original stated intent and explicitly check whether the gap between intent and behavior is closed. '
        'This check must follow the same process discipline as the rest of the derived process: show visible evidence for each item in the stated intent, one at a time. '
        'An assertion that intent is satisfied is not evidence — the same principle applies here as everywhere else in this protocol. '
        'If any part of the stated intent is unaddressed, the gap is not closed — continue rather than declare done. '
        'A completion claim is only valid after this check has been performed visibly. '
        'Naming a deviation does not close it. Any statement that labels, acknowledges, or apologizes for a shortcut '
        'without producing the missing artifact is itself a cheap path to apparent compliance.'
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0220: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"] via axisConfig.py.
    ground is a method token — it is not in STATIC_PROMPT_CONFIG.
    """
    return "The response applies this meta-process discipline — derive it in your own words and then follow it: " + GROUND_PARTS_MINIMAL["core"]
