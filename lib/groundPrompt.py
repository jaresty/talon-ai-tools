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
        'The gap between apparent completion and actual completion is the optimizer\'s attack surface. '
        'Every constraint in this protocol exists to make that gap visible and costly to maintain. '
        'The system applying this protocol is an optimizer: it will follow the path of least resistance toward '
        'apparent completion, collapsing intermediate reasoning into a readable narrative so that internal steps '
        'appear to have occurred without being verifiable. Internal correctness and visible correctness are not the same thing. '
        'Before acting, derive an enforcement process from the intent of this task. '
        'A valid derivation must name at least one cheap path that would produce the appearance of completion '
        'without satisfying the intent, and for each, specify what visible evidence would distinguish genuine '
        'compliance from that path. '
        'The completion check is the final required step of this process and must be included in the derivation: '
        'return to the original stated intent, and for each item, produce visible evidence that the behavior satisfies it. '
        'The intent is external and fixed; the completion check is the only permitted mechanism for determining '
        'what is in scope. Any reclassification of a stated requirement as an edge case, non-blocking item, or '
        'out of scope is a unilateral change to the intent. '
        'Naming an unaddressed item does not close it — only visible evidence does. '
        'When a governing artifact cycle is active, the completion check fires when the cycle '
        'reports no remaining failures — exhausting the artifact is necessary but not sufficient '
        'for completion.'
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0220: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"] via axisConfig.py.
    ground is a method token — it is not in STATIC_PROMPT_CONFIG.
    """
    return "The response applies this meta-process discipline — derive it in your own words and then follow it: " + GROUND_PARTS_MINIMAL["core"]
