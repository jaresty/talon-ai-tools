"""Ground method prompt (spike/craft-token-refactor branch).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make bar-grammar-update`
to propagate changes through to downstream grammar files.

Note: ground is a method token (axisConfig.py), not a task token.
"""


def build_ground_prompt() -> str:
    """Return the ground method prompt string.

    Spike definition: ground = recursive ambiguity resolution in Ground properties block.
    """
    return (
        "The response must produce a 'Ground properties:' block before any test, implementation step, tool call, or task reasoning begins. "
        "If the request admits more than one reasonable interpretation, the chosen interpretation must first be declared on a line beginning exactly: "
        "'Interpretation: <chosen interpretation>' — "
        "all subsequent properties are derived exclusively from this interpretation. "
        "Every property must be derivable from the explicit constraints of the chosen interpretation. "
        "A property that introduces a constraint not implied by those constraints is out of scope and must not appear in the block. "
        "Each property is written on its own line beginning 'property [N]:' followed by a formal definition having a single unambiguous denotation. "
        "The definition must be expressed as one of: a typed mathematical expression, a logical predicate (for example using ∀, ∃, ⇒, ⇔), or a formally defined relation. "
        "Two independent readers applying the same interpretation must reach the same conclusion about whether a construction satisfies the property. "
        "A property is atomic when no pair of strictly simpler properties satisfies both of the following: "
        "(1) their conjunction has identical coverage to the original property; "
        "(2) each part admits at least one admissible construction that falsifies that part without falsifying the other. "
        "To test atomicity, provisional candidate sub-properties may be introduced immediately before the split test using: "
        "'property [Na]: <definition>' and 'property [Nb]: <definition>' — "
        "these provisional lines exist only for evaluating the proposed split and are not members of the property set unless the split succeeds. "
        "Immediately after the provisional lines, emit exactly one split test: "
        "'§ split test: property [Na]: \"<verbatim definition>\" — falsified by <construction>; "
        "property [Nb]: \"<verbatim definition>\" — falsified by <construction>; these falsifiers are independent.' "
        "The quoted definitions must match the immediately preceding provisional definitions verbatim. "
        "A split succeeds only if: the conjunction of the accepted sub-properties has identical coverage to the original property; "
        "each quoted falsifier violates exactly its quoted property while satisfying the other; "
        "both falsifiers are admissible constructions within the chosen interpretation. "
        "If the split succeeds, replace the original property with the accepted sub-properties and continue recursively testing each accepted property. "
        "If no valid split exists, emit: '§ split test: property [N]: \"<verbatim definition>\" — atomic, no valid split: <reason>.' "
        "The quoted definition must match the retained property verbatim. "
        "Continue recursively until every retained property has a split test concluding 'atomic, no valid split.' "
        "After all retained properties are atomic, emit a completeness check: "
        "'§ completeness check: \"<request constraints verbatim>\" / <P1 expression> / <P2 expression> / ...' — "
        "the request constraints must be quoted verbatim from the chosen interpretation; "
        "every retained atomic property expression must appear exactly once, separated by ' / '; "
        "a '§ completeness check:' line that omits the request constraints or omits any retained property expression does not satisfy this requirement. "
        "Immediately after the completeness check, attempt to identify one explicit request constraint that is not represented by any retained property. "
        "If such a constraint exists, emit '§ properties complete? no' — "
        "add one new property covering that explicit constraint, perform the required split testing, and repeat the completeness check. "
        "Only when every explicit request constraint is represented by at least one retained property may the response emit '§ properties complete? yes' — "
        "a '§ properties complete? yes' line without a preceding completeness check does not satisfy this protocol. "
        "After completeness has been established, verify observational independence. "
        "A retained property is observationally independent if there exists at least one admissible construction that violates that property while satisfying every other retained property. "
        "Any retained property that is not observationally independent is observationally redundant and must be removed or merged, "
        "provided doing so does not reduce coverage of the explicit request constraints. "
        "If a merge or removal changes the retained property set, repeat the atomicity and completeness procedures. "
        "The Ground properties block is complete only when all retained properties simultaneously satisfy: "
        "they are derived from the chosen interpretation; they are atomic; "
        "they collectively cover every explicit request constraint; "
        "they are observationally independent; they introduce no out-of-scope constraints. "
        "Beginning any test, implementation step, tool call, or task reasoning before the Ground properties block is complete does not satisfy this protocol."
    )
