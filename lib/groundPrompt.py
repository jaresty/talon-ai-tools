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
        'for non-software subjects, record an observation of the subject under a literal \'## \' heading '
        'naming the subject — an observation not under such a heading does not satisfy §0; '
        'the §0 identifier is the heading text used; '
        '(1) write \'## Governing goal: [text]\' where \'[text]\' is a verbatim substring of the §0 tool result '
        '— a \'## Governing goal:\' line appearing before any tool-result block above it does not satisfy §1; '
        'immediately below the heading, write one sentence of the form '
        '\'The goal [text] could be achieved by: [alternative means not listed in §0]\' '
        '— if no concrete alternative can be named, write \'[hypothetical]: [speculated alternative]\' '
        'and fetch a broader context artifact before proceeding to §2; '
        'a \'## Behavioral dimensions\' heading appearing without this sentence above it does not satisfy §1; '
        'if two non-subsuming goal candidates exist, write both on separate lines under §1 and mark one '
        '\'[selected]\' — the selected goal is the one whose means-test sentence names '
        'a more concrete alternative than those listed in §0; '
        '(2) write \'## Behavioral dimensions\' — this heading must not appear before \'## Governing goal:\' appears in the transcript; '
        'list at least two dimensions; '
        'each dimension names a property of the response (not an artifact, state, or fix description) '
        'such that a response could satisfy it while failing at least one other listed dimension; '
        'each dimension quotes a verbatim substring of the \'[text]\' string from §1, '
        'or names a response property directly implied by that text when no behavioral substring exists; '
        'a dimension that names an entity, a fix outcome, or a UI element is not a valid dimension regardless of provenance; '
        '(3) write \'## Enforcement sequence\' '
        '— this heading must appear in the transcript before the first file-modifying tool call regardless of whether \'§ implementation permitted\' appears; '
        'each sub-heading names as a literal substring what the prior sub-heading\'s passing state admits '
        'that this sub-heading rejects; (4) write \'## Completion check\' — this heading must not appear before \'## Enforcement sequence\' in the transcript; '
        'each covered dimension cites '
        'a verbatim string that appears as a substring of a tool-result block visible above \'## Completion check\' '
        '— a dimension declared covered without such a substring does not satisfy §4; '
        '(5) write \'## Path enumeration\'; enumerate every path by which §1–§4 headings could be present '
        'without the governing goal identified, dimensions derived, or dimensions covered; for each path, '
        'name the literal string whose presence closes it; write \'§5 enumeration complete\' when no '
        'further open path remains; any referent named in the \'[text]\' from §1 not already present as '
        'a literal string in the transcript above §1 must be fetched before §1 is written; the string '
        '\'§ implementation permitted\' must appear in the transcript after \'§5 enumeration complete\'; '
        'the strings \'§5 enumeration complete\' and \'§ implementation permitted\' each appear exactly '
        'once; no file-modifying tool call may appear before \'§ implementation permitted\'; '
        'a response turn that declares the task complete or produces no further planned actions must be '
        'immediately preceded in the transcript by a \'## Completion check\' block — a done declaration '
        'appearing before \'## Completion check\' does not satisfy ground.'
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
