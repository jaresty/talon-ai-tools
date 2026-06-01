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
        'Derivation phase (required before any file-modifying tool call): name the root criterion — '
        '(0) before naming the governing goal, run the subject under observation and record its output '
        'under a literal heading — the governing goal heading must contain as a literal substring a string '
        'present verbatim in that tool-executed result; a governing goal heading with no such substring '
        'has not been derived from observed state and does not satisfy this requirement; '
        'for non-software subjects, observing the subject as it currently stands satisfies the §0 '
        'run requirement — record what is observed under a literal heading and derive the governing '
        'goal from a literal substring of that observation; '
        '(1) the governing goal must appear under a literal heading in the transcript before any '
        'implementation action, identified as the goal no other stated goal subsumes; (2) behavioral '
        'dimensions must appear under a literal heading, each naming as a literal substring the specific '
        'clause in the governing goal it derives from; (3) each artifact in the enforcement sequence must '
        'appear under a literal heading naming, as a literal substring, what the prior artifact\'s passing '
        'state admits that this artifact rejects; (4) each behavioral dimension must be covered by a '
        'verbatim string from a tool-executed result appearing under a literal completion-check heading; '
        '(5) enumerate every path by which a transcript could satisfy the §1, §2, §3, and §4 heading '
        'requirements without the governing goal having actually been identified, dimensions actually '
        'derived, or dimensions actually covered — the enumeration must include at least one path entry '
        'for each of §1, §2, §3, and §4; for each path, name the literal string in the transcript that '
        'closes it — a path is closed only when naming that string makes the non-compliant transcript '
        'distinguishable from the compliant one without assessing intent; a path that cannot be closed '
        'by naming a string must be eliminated by ensuring the required structural property is present '
        'before the heading is written; no file-modifying tool call may appear before this enumeration '
        'is present in the transcript; the literal strings named during enumeration as path closures are '
        'binding — a heading or structural property that does not match the committed string verbatim '
        'does not satisfy the corresponding requirement. Proceed to implementation only when §0–§5 are '
        'present as text above this point in the transcript. Any noun phrase in the governing goal that names a file path, '
        'URL, ticket number, or document title not already present in the transcript must be fetched '
        'before the governing goal heading is written — derivation is blocked until the referent is '
        'resolved. No file-modifying tool call may appear before the completion-check heading. The '
        'response is not permitted to end until the completion-check heading appears in the transcript '
        'and every covered dimension must cite a verbatim string from a tool-executed result whose invocation names the '
        'subject under observation directly — a tool-executed result whose invocation names an artifact that evaluates '
        'or reports on the subject rather than the subject itself does not satisfy this requirement.'
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0220: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"] via axisConfig.py.
    ground is a method token — it is not in STATIC_PROMPT_CONFIG.
    """
    return (
        "The response applies a meta-process discipline before any implementation action. "
        + GROUND_PARTS_MINIMAL["core"]
    )
