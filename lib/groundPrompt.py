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
        'All compliance headings must be markdown \'## \' headings — a line not beginning with \'## \' '
        'does not satisfy any heading requirement. '
        'Derivation phase: (0) invoke the subject under observation as a tool call and record its output; '
        'the artifact named in that invocation is the §0 identifier, fixed for all steps; '
        'for non-software subjects, recording an observation of the subject as it currently stands under '
        'a literal heading satisfies §0 — the §0 identifier is the name used in that observation; '
        '(1) write \'## Governing goal: [text]\' where \'[text]\' is a verbatim substring of the §0 tool result; '
        'if two non-subsuming goal candidates exist, write both on separate lines under §1 and mark one '
        '\'[selected]\' — the selected goal is the one whose non-achievement leaves the task incomplete '
        'regardless of other goals; (2) write \'## Behavioral dimensions\'; each listed dimension quotes '
        'a verbatim substring of the \'[text]\' string from §1; (3) write \'## Enforcement sequence\'; '
        'each sub-heading names as a literal substring what the prior sub-heading\'s passing state admits '
        'that this sub-heading rejects; (4) write \'## Completion check\'; each covered dimension cites '
        'a verbatim string from a tool call whose invocation names the §0 identifier directly; '
        '(5) write \'## Path enumeration\'; enumerate every path by which §1–§4 headings could be present '
        'without the governing goal identified, dimensions derived, or dimensions covered; for each path, '
        'name the literal string whose presence closes it; write \'§5 enumeration complete\' when no '
        'further open path remains; any referent named in the \'[text]\' from §1 not already present as '
        'a literal string in the transcript above §1 must be fetched before §1 is written; the string '
        '\'§ implementation permitted\' must appear in the transcript after \'§5 enumeration complete\'; '
        'the strings \'§5 enumeration complete\' and \'§ implementation permitted\' each appear exactly '
        'once; no file-modifying tool call may appear before \'§ implementation permitted\'.'
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0220: generative ladder).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"] via axisConfig.py.
    ground is a method token — it is not in STATIC_PROMPT_CONFIG.
    """
    return (
        "The response applies a meta-process discipline before any implementation action, "
        "deriving and enforcing its own correctness conditions as transcript-inspectable strings. "
        + GROUND_PARTS_MINIMAL["core"]
    )
