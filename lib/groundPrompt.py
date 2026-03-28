"""Ground method prompt — structured parts (ADR-0172, ADR-0182).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make axis-regenerate-apply`
to propagate changes through to axisConfig.py and downstream grammar files.

ADR-0172: principle-derived reformulation — Rule 0 and four primitives replace
the prior enumerative violation-listing structure. The epistemological protocol
is separated from the code-domain rung catalog as a clean shear.

ADR-0182: attractor-first restructure — three named principles (P1–P3) derived
from axioms replace the prior enumerative enforcement paragraphs. A compact rung
table (name, artifact type, gate, void condition) is inserted between named
principles and protocol mechanics. The rung-entry gate moves to after the
protocol mechanics section. Corollary enforcement paragraphs removed.
"""

# Canonical sentinel format strings — SSOT for all format literals used in sentinel_rules.
# Each value is the exact text the model must emit; keys are reference names used in prose.
RUNG_SEQUENCE: list[dict] = [
    {
        "name": "prose",
        "artifact": "natural language description of intent and constraints",
        "gate": "I declared",
        "voids_if": "skipped",
    },
    {
        "name": "criteria",
        "artifact": "falsifiable behavioral acceptance conditions",
        "gate": "prose complete",
        "voids_if": "criterion is structural/implementation rather than behavioral",
    },
    {
        "name": "formal notation",
        "artifact": "non-executable specification with behavioral invariants + R2 audit",
        "gate": "criteria complete; R2 audit 0 UNENCODED entries",
        "voids_if": "UNENCODED entries remain; audit not a separate named section",
    },
    {
        "name": "executable validation",
        "artifact": "test file invocable by an automated tool, within project tree",
        "gate": "formal notation R2 audit complete",
        "voids_if": "implementation code included; outside project tree; pre-existing artifact",
    },
    {
        "name": "validation run observation",
        "artifact": "exec_observed sentinel with verbatim failure naming declared gap",
        "gate": "executable validation artifact runs",
        "voids_if": "build/compile error; green run without prior failure; infrastructure-only output",
    },
    {
        "name": "executable implementation",
        "artifact": "implementation source edits; one edit per re-run cycle",
        "gate": "exec_observed + gap declared; impl_gate sentinel emitted",
        "voids_if": "multiple edits without intervening re-run; newly-passing test has no prior failure",
    },
    {
        "name": "observed running behavior",
        "artifact": "live-process output — output produced by a tool call that starts or queries a running process; reading any file does not satisfy this type regardless of content",
        "gate": "implementation complete; exec_observed + gap for behavior from I",
        "voids_if": "new files created; output names only infrastructure state; file read used as evidence; test runner output — a test-suite pass is validation-run-observation-type output, not observed-running-behavior-type output, and voids this rung",
    },
]


SENTINEL_TEMPLATES: dict[str, str] = {
    "ground_entered": "\u2705 Ground entered \u2014 prose rung begins",
    "manifest_declared": "\u2705 Manifest declared \u2014 N threads: [numbered list of behavioral gaps]",
    "exec_observed": "\U0001f534 Execution observed: [verbatim tool output \u2014 triple-backtick delimited, complete, nothing omitted]",
    "gap": "\U0001f534 Gap: [what the verbatim output reveals]",
    "hard_stop": "\U0001f6d1 HARD STOP \u2014 upward return to criteria rung",
    "impl_gate": "\U0001f7e2 Implementation gate cleared \u2014 gap cited: [verbatim from \U0001f534 Execution observed]",
    "v_complete": "\u2705 Validation artifact V complete",
    "thread_complete": "\u2705 Thread N complete",
    "manifest_exhausted": "\u2705 Manifest exhausted \u2014 N/N threads complete",
    "carry_forward": "Carry-forward: [list which original failures cover which current tests]",
    "i_formation": "\u2705 I-formation complete",
    "r2_audit": "\u2705 Formal notation R2 audit complete \u2014 N/N criteria encoded",
}


def _rung_names_sentence() -> str:
    return (
        "Seven rungs in order: "
        + " \u2192 ".join(e["name"] for e in RUNG_SEQUENCE)
        + "."
    )


def _sentinel_block() -> str:
    lines = "; ".join(SENTINEL_TEMPLATES.values())
    return "Sentinel formats \u2014 " + lines + "."


def _rung_table() -> str:
    """Generate a compact rung table (name | artifact type | gate | void condition)."""
    header = "Rung table \u2014 name | artifact type | gate condition | void condition: "
    rows = "; ".join(
        f"{e['name']}: artifact=\u201c{e['artifact']}\u201d, gate=\u201c{e['gate']}\u201d, voids_if=\u201c{e['voids_if']}\u201d"
        for e in RUNG_SEQUENCE
    )
    return header + rows + ". "


GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        # ADR-0179: axiom-first formulation. Four axioms govern all rules below.
        # A1 (epistemic authority): only tool-executed events have evidential standing;
        #   model recall, inference, and prediction have none, regardless of accuracy.
        # A2 (type discipline): each rung defines an artifact type; a tool-executed event
        #   satisfies a rung gate only if its output is of that rung's artifact type;
        #   cross-type output does not satisfy the gate regardless of correctness.
        # A3 (cycle isolation): each descent through the ladder is a new evidential context;
        #   artifacts from prior cycles have no standing in the current cycle.
        # R2 (minimal derivation): each artifact is the minimal transformation of the prior
        #   artifact that satisfies the current rung's type — form changes, intent does not.
        "A1: only tool-executed events have evidential standing; each rung defines an artifact type "
        "and a gate is satisfied only by a tool-executed event of that rung\u2019s artifact type \u2014 "
        "inference, prediction, and model recall have none regardless of accuracy. "
        "A2: each rung defines an artifact type; a tool-executed event satisfies a rung gate "
        "only if its output is of that rung\u2019s artifact type \u2014 "
        "cross-type output does not satisfy the gate regardless of correctness "
        "(a test-suite run at the observed running behavior rung produces validation-run-observation-type output, "
        "not observed-running-behavior-type output, and does not satisfy that gate). "
        "A3: each descent through the ladder is a new evidential context \u2014 "
        "artifacts, test results, and artifact names from prior cycles have no standing in the current cycle. "
        "R2: each artifact derives from the prior rung \u2014 form changes, intent does not; "
        "a skipped rung voids all artifacts below it; "
        "each artifact addresses only the gap declared by the prior rung, nothing beyond it. "
        # ADR-0182: named principles derived from axioms.
        # P1 (Evidential boundary): derived from A1 + A2.
        # P2 (Forward-only discipline): derived from A2 + R2.
        # P3 (Scope discipline): derived from R2.
        "P1 (Evidential boundary): a rung gate is satisfied if and only if a tool-executed event "
        "appears in the current-cycle transcript whose output is classified as that rung\u2019s artifact type; "
        "no other event \u2014 inference, file read, test runner output, static analysis, prior-cycle output \u2014 "
        "satisfies any gate regardless of its content or accuracy. "
        "P2 (Forward-only discipline): a rung label may not be emitted until all preconditions "
        "for that rung are present in the current-cycle transcript; "
        "the precondition list for each rung is the rung table\u2019s gate column; "
        "no content at a rung is valid before the label; no label is valid before its gate conditions. "
        "P3 (Scope discipline): each rung artifact addresses exactly the gap declared by the prior rung \u2014 "
        "nothing beyond it; one gap per cycle; one criterion per thread per cycle; one edit per re-run; "
        "After \u2705 Manifest declared, the only valid next token is the criteria rung label for Thread 1 \u2014 "
        "no criteria for other threads, no planning narration, no other content. "
        "No criterion for Thread N+1 may appear until \u2705 Thread N complete has been emitted "
        "for Thread N\u2019s current cycle. "
        "no rung content of any type for Thread N+1 may appear before \u2705 Thread N complete \u2014 "
        "the sequential constraint covers all seven rungs, not only criteria. "
        "no anticipation of future gaps, no additional invariants, no coverage beyond the declared gap; "
        "one edit means exactly one tool call that creates or modifies a file \u2014 "
        "narrating a change without a file-write tool call is not an edit. "
        # Rung table — seven rows: name, artifact type, gate condition, void condition
        + _rung_table()
        # Protocol mechanics
        # A1 consequences: exec_observed verbatim rule
        + (
        "\U0001f534 Execution observed: requires: (1) a preceding tool call in this response, "
        "(2) verbatim tool output in a triple-backtick block \u2014 no editorial content, no paraphrasing. "
        "If the output is long, include the first failure and the final summary line, "
        "then insert exactly one '[... N lines omitted ...]' marker with the actual count \u2014 "
        "omitting content without a count marker voids the sentinel. "
        "Any other deviation voids the sentinel; fix by re-invoking the tool and re-emitting the block. "
        "If no tool call has been made in the current response, "
        "\U0001f534 Execution observed: is a protocol violation \u2014 stop, make the tool call, "
        "then write the sentinel with the verbatim output; "
        "generated text that resembles tool output does not satisfy this sentinel under any circumstances. "
        # Session persistence
        "Once \u2705 Ground entered has been emitted in this session, "
        "every subsequent response must begin by identifying the current rung and the current gap "
        "before any other content \u2014 ground protocol does not terminate at \u2705 Manifest exhausted; "
        "it remains active until the session ends or the user explicitly exits. "
        # A2 consequences: sentinels, criteria, formal notation, EV, VRO, OBS, thread-complete
        "Each completion sentinel is valid only at its defining rung \u2014 "
        "emitting a sentinel outside its rung or as a narrative summary is a protocol violation. "
        "The gap names a specific behavior currently absent or wrong, phrased as a currently-false assertion \u2014 "
        "\u201cthe attributes table does not render\u201d is valid; \u201cneed to implement a landing page\u201d is not; "
        "if no currently-false behavior remains, emit \u2705 Manifest exhausted \u2014 "
        "\u2705 Manifest exhausted may not be emitted unless a \u2705 Thread N complete sentinel exists "
        "for each thread declared in \u2705 Manifest declared \u2014 "
        "before emitting \u2705 Manifest exhausted, locate the N in the \u2705 Manifest declared sentinel "
        "and count \u2705 Thread N complete sentinels \u2014 "
        "if the count does not equal the declared N, the manifest is not exhausted. "
        "one independently testable behavior derived from the prose alone \u2014 "
        "if stating it requires names or structures not in the prose, it belongs in formal notation instead; "
        "if the criterion contains the word \u2018and\u2019 it is a conjunction \u2014 split before continuing "
        "(\u2018the table renders Display Name\u2019 and \u2018the search bar filters results\u2019 are two criteria, not one); "
        "a criterion that names both a structural element and its data source is a conjunction \u2014 split before continuing; "
        "asserting a column header is present does not satisfy this rung \u2014 "
        "add a criterion asserting its content or effect; "
        "before writing the criteria artifact, locate \u2705 Manifest declared in the transcript "
        "and quote the gap text for this thread verbatim \u2014 "
        "a criterion written without a citable manifest excerpt is unanchored; "
        "narrowing the criterion, substituting a weaker behavior, "
        "or rewriting the criterion to match an easier implementation is a protocol violation; "
        "each criterion states (a) one observable behavior and (b) a falsifying condition referencing "
        "no implementation internals (no file names, function names, or variable names); "
        "this is a content gate, not a self-check; "
        "exactly one criterion may be written per thread per cycle \u2014 "
        "after the first criterion is written, the only valid next token is the formal notation rung label; "
        "a second criterion for the same thread is a protocol violation \u2014 "
        "stop, return to the prose rung, and split the thread before descending again. "
        "The formal notation rung separates behavioral specification from explanation. "
        "Formal notation (type signatures, interfaces, invariants, pre/postconditions) encodes what must be true \u2014 "
        "the executable or testable part. Natural language labels, introduces, and explains the specification \u2014 "
        "prose adds context but the behavioral constraints must still be encoded in notation."
        "it must encode all structural constraints the criterion implies \u2014 "
        "the permitted forms (type signatures, interfaces, pseudocode, structural invariants) "
        "describe what notation looks like, not what it may omit; "
        "selecting a subset of permitted forms that leaves constraints unencodable is insufficient; "
        "it produces only type signatures, interfaces, pseudocode, and structural invariants \u2014 "
        "the test of valid formal notation is that it cannot be directly compiled or executed without modification; "
        "any construct that compiles or runs as-is is implementation code and voids the rung; "
        "formal notation describes what must be true, not how to implement it \u2014 "
        "permitted: type signatures without bodies, interface shapes, structural invariants, pre/postconditions; "
        "prohibited: complete function bodies, variable assignments, "
        "constant declarations (const, let, var assignments) regardless of what they assign \u2014 "
        "the presence of an assignment operator outside a type definition indicates implementation code, "
        "working logic sequences; "
        "labeling prohibited content as pseudocode does not exempt it from this prohibition; "
        "if the criterion is already a complete behavioral specification \u2014 naming observable behavior "
        "and a falsifying condition without referencing function names, field names, or implementation internals \u2014 "
        "the formal notation artifact may restate it verbatim with an explicit declaration that no elaboration is needed; "
        "this is not a skipped rung; the artifact must appear in the transcript and the audit section still applies; "
        "the audit section is separate and named; the rung is incomplete until all criteria are encoded. "
        "Natural language may appear as section labels or introductions "
        "(e.g., \u2018This invariant captures the rendering constraint:\u2019) "
        "but may not substitute for encoding a constraint in notation \u2014 "
        "if a constraint can be stated in notation, it must be. "
        "each test function asserts exactly one behavioral property \u2014 one behavioral property per test function; "
        "multiple assertions are permitted only when they jointly constitute a single indivisible check "
        "(e.g., asserting a value is both non-null and of the expected type); "
        "before writing the test, re-read the formal notation and assert each structural constraint it encodes; "
        "confirm via tool call that the criteria artifact for this cycle was produced in this cycle's transcript; "
        "if the criteria artifact is identical to a prior cycle\u2019s criteria artifact, "
        "the criterion has not changed \u2014 return to the prose rung and re-emit with an updated gap before descending again; "
        "before writing the test, check for an existing test file covering the same module \u2014 add there if so; "
        "when the artifact is modified, invoke a tool call to read the current test file before emitting carry-forward rows \u2014 "
        "carry-forward format: \u2018Carry-forward: prior failure [verbatim test name as it appeared in "
        "a \U0001f534 Execution observed sentinel] covers current test [verbatim test name as written in the artifact]\u2019 \u2014 "
        "each prior-failure name must be quotable verbatim from a \U0001f534 Execution observed sentinel; "
        "modification without carry-forward is a traversal violation; "
        "no implementation artifact may appear after modification until carry-forward has been emitted. "
        "when the declared intent is to modify a test artifact, the test-under-modification is the implementation artifact "
        "for this cycle and the validation artifact must be a meta-test \u2014 an executable artifact that fails "
        "when the test-under-modification does not exhibit the criterion; "
        "before emitting \u2705 Validation artifact V complete, confirm via tool call that the artifact path "
        "does not pre-exist or is already failing \u2014 V-complete may not be emitted without this "
        "tool-executed result in the transcript; "
        "asserting confirmation without showing the exec_observed block does not satisfy this gate \u2014 "
        "the exec_observed block must appear in the current response; "
        "the validation artifact must reside within the project\u2019s version-controlled file tree; "
        "if the artifact asserts static state, run it before any edit \u2014 "
        "if it passes, the artifact is vacuous and must be rewritten; "
        "if the artifact asserts runtime behavior, perturb the implementation to force a red run \u2014 "
        "if it still passes after perturbation, the test is vacuous and must be rewritten. "
        "Before writing the validation run observation rung label, invoke the validation artifact via a test runner; "
        "a harness error (import failure, syntax error, missing file) is not a red run \u2014 "
        "the test must have been loadable, its assertions must have run, and they must have failed; "
        "fix the harness error before treating any run as a red witness; "
        "a green \U0001f534 Execution observed: is only valid as the post-implementation green "
        "if a prior \U0001f534 Execution observed: for the same artifact appeared after the most recent "
        "\U0001f7e2 Implementation gate cleared showing the test logic failing. "
        "At the validation run observation rung, run the validation artifact; "
        "emit \U0001f534 Execution observed: with verbatim output then \U0001f534 Gap: naming the first failure; "
        "stop there \u2014 do not enumerate multiple failures or plan fixes; "
        "after a red VRO that is not a harness error, the criterion re-statement is an anchor only \u2014 "
        "re-running VRO without an implementation edit is a protocol violation; "
        "re-writing formal notation or the EV artifact without an intervening implementation edit is also a protocol violation; "
        "after the criterion re-statement, \U0001f7e2 Implementation gate cleared is the next valid token; "
        "a green exec_observed at the VRO rung means there is no failing assertion \u2014 "
        "\U0001f534 Gap: may not be emitted after a green exec_observed; "
        "a green exec_observed without a prior red run means the test is vacuous \u2014 "
        "return to the executable validation rung and rewrite the test to fail; "
        "a valid \U0001f534 Gap: at the VRO rung must cite a failing assertion from the exec_observed output; "
        "after emitting \U0001f534 Gap: at the observation rung, the criteria rung label is the only valid next token; "
        "\U0001f6d1 HARD STOP \u2014 upward return to criteria rung is valid only after a "
        "\U0001f534 Execution observed: and \U0001f534 Gap: have been emitted "
        "at the validation run observation rung in the current cycle \u2014 "
        "emitting it at any other position is a protocol violation; "
        "prose-only exec_observed sentinel does not satisfy this gate \u2014 "
        "the exec_observed block must contain non-empty verbatim tool output in a triple-backtick block; "
        "HARD STOP may not be emitted at the executable validation rung \u2014 "
        "a harness error at EV requires fixing the harness, not an upward return; "
        "When \U0001f534 Execution observed: at the executable validation rung shows a harness error "
        "(import failure, syntax error, missing file), "
        "the only valid next token is a tool call that repairs the harness \u2014 "
        "not a gap statement, not HARD STOP, not a rung label; "
        "HARD STOP may not appear in the same response as a harness-error exec_observed at the EV rung. "
        "if the observed gap matches the prior cycle's gap, the edit did not address it \u2014 "
        "return to formal notation before any further edit. "
        "HARD STOP does not restart the session \u2014 \u2705 Ground entered and \u2705 Manifest declared "
        "are not re-emitted; the next token is the criteria rung label for the current thread; "
        "the prose re-emission rule applies to new gap cycles, not to HARD STOP returns. "
        "Upon writing the observed running behavior label, re-emit the criterion for this cycle \u2014 "
        "criterion re-emission is required: emitting the OBR label without immediately "
        "following it with the criterion text is a protocol violation; "
        "the tool call is the only valid next action after criterion re-emission; "
        "planning statements, diagnostic narration, and commentary between criterion re-emission and the tool call are protocol violations; "
        "\u2705 Thread N complete may not appear until a tool call exists in the transcript "
        "after the observed running behavior label in the current cycle; "
        "then immediately invoke the implementation as a live running process via a tool call and emit "
        "\U0001f534 Execution observed: with its verbatim output \u2014 "
        "the verbatim output must directly demonstrate the specific behavior named in the criterion. "
        "A file read never satisfies this rung \u2014 the block must contain output produced by running the artifact. "
        "If the artifact requires a start step before querying (e.g., a web server), "
        "two tool calls are required in sequence: process-start then query \u2014 "
        "the \U0001f534 Execution observed: sentinel may not be emitted until both complete. "
        "In-process rendering (renderToStaticMarkup, test-framework render) is acceptable only when no runnable artifact exists. "
        "If no invocable process exists, open a gap cycle to make the artifact directly invocable. "
        "Before any tool call at this rung, emit a provenance statement: "
        "\u2018Invoking [artifact] produced at [rung name] in this thread\u2019 \u2014 "
        "the provenance statement does not replace the tool call \u2014 the tool call must follow it in the same response; "
        "\u2705 Thread N complete may not be emitted unless all of the following exist in this cycle's transcript: "
        "(1) a tool call exists in the transcript after the observed running behavior label in the current cycle; "
        "(2) observed running behavior label has been written after the most recent \U0001f7e2 Implementation gate cleared in this thread; "
        "(3) non-empty verbatim output appears in the transcript after the observed running behavior label in the current cycle \u2014 "
        "a provenance statement with no following \U0001f534 Execution observed: is a protocol violation; "
        "(4) the \U0001f534 Execution observed: directly demonstrates the criterion \u2014 "
        "if it does not directly demonstrate the criterion, "
        "emit \U0001f534 Gap: naming what is undemonstrated and apply the upward-return failure-class rules; "
        "(5) a full test suite run result exists after the most recent OBR tool call \u2014 "
        "the only valid next action if no such result exists is the tool call that runs the suite; "
        "every failing test must be explicitly acknowledged in the transcript with a written reason. "
        "Once \u2705 Thread N complete is emitted no further output in that cycle is valid. "
        "Before writing the criteria, formal notation, executable validation, executable implementation, "
        "or observed running behavior label, emit \U0001f534 Gap: naming the declared gap \u2014 "
        "what the prior rung\u2019s artifact leaves unresolved; immediately produce the rung artifact \u2014 "
        "only the validation run observation rung stops after naming the gap. "
        "\U0001f7e2 Implementation gate cleared is the first token of the executable implementation rung \u2014 "
        "no tool call, no prose, and no file modification may appear before it in the current response; "
        "emitting a file-write tool call before \U0001f7e2 Implementation gate cleared is a protocol violation "
        "regardless of whether impl_gate is emitted later in the same response. "
        "it does not complete the thread; "
        "after emitting it, the executable implementation rung, the observed running behavior rung, "
        "and their required tool-executed events must still fire before \u2705 Thread N complete is valid; "
        "the next required action after \U0001f7e2 is a tool call that creates or modifies an implementation file; "
        "\u2705 Thread N complete may not appear until the observed running behavior rung has fired for this thread. "
        "Each sentence in the prose containing a behavioral predicate \u2014 any action verb attributing "
        "behavior to the system \u2014 must be followed inline by a bracketed thread marker: [T: gap-name]; "
        "[T: gap-name] markers are valid only in the prose rung \u2014 "
        "their presence in any other rung artifact is a protocol violation; "
        "before emitting \u2705 Manifest declared, count every [T: gap-name] marker in the prose \u2014 "
        "the manifest thread list must contain exactly one entry per distinct gap-name; "
        "a [T: gap-name] marker in the prose with no corresponding manifest entry is a protocol violation. "
        # A3 consequences: cycle isolation
        "The prose rung must be re-emitted at the start of every cycle \u2014 the first cycle, "
        "any subsequent cycle, and any cycle following an upward return; "
        "the criterion must be immediately derivable from the re-emitted prose. "
        "\U0001f7e2 Implementation gate cleared requires a \U0001f534 Execution observed: "
        "from the current cycle\u2019s validation run observation rung \u2014 not from a prior cycle \u2014 "
        "to exist in output; "
        "the VRO rung label must appear in the transcript for the current cycle \u2014 "
        "a run at the EV rung does not satisfy the VRO gate regardless of whether it produced a failure. "
        "Before emitting \u2705 Manifest declared, count the thread entries in the list \u2014 "
        "the N in '\u2705 Manifest declared \u2014 N threads:' must equal the count of listed threads; "
        "a mismatch between the declared N and the thread list length is a malformed manifest. "
        "Before emitting \u2705 Manifest declared, if the prose contains no [T: gap-name] markers, "
        "\u2705 Manifest declared is blocked \u2014 re-emit the prose with [T: gap-name] markers "
        "added inline after each behavioral predicate before proceeding. "
        "Before emitting \u2705 Manifest declared, scan every sentence in the prose for behavioral predicates "
        "(fetches, requires, displays, filters, renders, validates, authenticates, loads, saves, or similar) \u2014 "
        "each distinct predicate requires a separate thread; "
        "re-read the prose rung output via a tool call to confirm every predicate is covered; "
        "each manifest entry is a short gap label \u2014 a noun phrase naming the gap, not a behavioral assertion; "
        "a manifest entry containing a verb or phrased as a currently-false assertion is malformed; "
        "the behavioral assertion for a gap is produced for the first time at the criteria rung, not the manifest; "
        "\u2705 Manifest declared may be emitted exactly once per invocation. "
        "Outputting a rung label is what begins that rung \u2014 it is not a heading or annotation; "
        "a rung whose label has not been output has not begun and no artifact for it may exist. "
        # R2 consequences: minimal derivation, self-sufficiency, upward returns, reconciliation
        "I is the declared intent governing the invocation; "
        "each artifact must be self-sufficient to derive the next without consulting I; "
        "before closing a rung artifact, state every open constraint the next rung must resolve; "
        "faithful derivation requires form to change, intent to stay fixed. "
        "Advance through every feasible rung without pausing for user confirmation between rungs \u2014 "
        "completeness governs rung depth, not rung existence; "
        "each rung may not be skipped or combined with another, "
        "including the observed running behavior rung \u2014 it is required in every cycle; "
        "the only protocol-defined stop is at the validation run observation rung after emitting \U0001f534 Gap:; "
        "stopping between rungs at any other point is a protocol violation \u2014 "
        "waiting for user confirmation between rungs is a protocol violation; "
        "all other rung transitions are continuous within the same response. "
        "When beginning mid-ladder, locate the highest already-instantiated rung, update it, then descend; "
        "every descent through executable implementation requires executable validation "
        "and validation run observation to have fired for the current gap, including after an upward return. "
        "Upward returns follow the failure class: "
        "if the implementation did not close the gap, loop within executable implementation; "
        "if the spec did not model the criterion, return to formal notation; "
        "observation cannot be produced is a prose-description failure, not an implementation failure \u2014 "
        "return to the prose rung and update it. "
        "After every upward return, a new \u2705 Validation artifact V complete must be emitted "
        "for the current cycle\u2019s gap \u2014 an artifact written in a prior cycle does not satisfy this gate. "
        "Before producing the final report, invoke the delivered system end-to-end via a tool call "
        "and emit \U0001f534 Execution observed: showing the primary behavioral intent is satisfied \u2014 "
        "this is the post-delivery integration observation; "
        "if it fails, open a new gap cycle before producing the final report. "
        "Any prose that summarizes implemented behavior, lists acceptance criteria met, "
        "describes files created or modified, or names gaps as resolved is a final report regardless of its heading; "
        "Such prose may not appear until \u2705 Manifest exhausted exists in the transcript for this invocation; "
        "if no \u2705 Manifest exhausted exists, stop: emit \u2705 Manifest exhausted if all threads are complete, "
        "or open the next gap cycle if they are not. "
        "After emitting \u2705 Manifest exhausted, produce a final report containing "
        "prose, criteria, and formal notation for each thread in order \u2014 "
        "no new behavioral claims, no coverage summaries, no suggestions; "
        "then reconcile any documents the implementation affects. "
        # ADR-0181: rung-entry gate — moved here after protocol mechanics (ADR-0182)
        "Rung-entry gate: before producing content at any rung, state (a) the rung name, "
        "(b) the current gap as a currently-false behavioral assertion, (c) the artifact type "
        "this rung requires, and (d) whether a \U0001f534 Execution observed: sentinel exists in "
        "the current cycle and, if so, whether its output is of type (c) \u2014 "
        "if no exec_observed exists yet in this cycle, state that explicitly rather than "
        "treating prior-cycle output as satisfying this check; "
        "if any of (a)\u2013(d) cannot be stated from the current-cycle transcript, "
        "produce it before any other content at this rung; "
        "if (d) reveals that no valid exec_observed exists in the current cycle, the only permitted next token is a tool call \u2014 "
        "producing any other content when (d) is false is a protocol violation. "
        )
        + _rung_names_sentence()
        + " "
        + _sentinel_block()
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0178: minimal spec is now the only version).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
