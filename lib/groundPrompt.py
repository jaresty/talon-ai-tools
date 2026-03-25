"""Ground method prompt — structured parts (ADR-0172).

This is the SSOT for the ground method's prompt injection text.
It is NOT generated; edit directly here, then run `make axis-regenerate-apply`
to propagate changes through to axisConfig.py and downstream grammar files.

The four parts correspond to: the epistemological protocol (Rule 0 + four
generative primitives + scope discipline), sentinel enforcement mechanics,
the code-domain rung sequence, and reconciliation/completion.

ADR-0172: principle-derived reformulation — Rule 0 and four primitives replace
the prior enumerative violation-listing structure. The epistemological protocol
is separated from the code-domain rung catalog as a clean shear.
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
        "artifact": "test file invocable by automated runner, within project tree",
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
        "artifact": "tool output demonstrating declared behavioral intent (not infrastructure state)",
        "gate": "implementation complete; exec_observed + gap for behavior from I",
        "voids_if": "new files created; output names only infrastructure state",
    },
]


SENTINEL_TEMPLATES: dict[str, str] = {
    "ground_entered":     "\u2705 Ground entered \u2014 prose rung begins",
    "manifest_declared":  "\u2705 Manifest declared \u2014 N threads: [numbered list of behavioral gaps]",
    "exec_observed":      "\U0001F534 Execution observed: [verbatim tool output \u2014 triple-backtick delimited, complete, nothing omitted]",
    "gap":                "\U0001F534 Gap: [what the verbatim output reveals]",
    "hard_stop":          "\U0001F6D1 HARD STOP \u2014 upward return to criteria rung",
    "impl_gate":          "\U0001F7E2 Implementation gate cleared \u2014 gap cited: [verbatim from \U0001F534 Execution observed]",
    "v_complete":         "\u2705 Validation artifact V complete",
    "thread_complete":    "\u2705 Thread N complete",
    "manifest_exhausted": "\u2705 Manifest exhausted \u2014 N/N threads complete",
    "carry_forward":      "Carry-forward: [list which original failures cover which current tests]",
    "i_formation":        "\u2705 I-formation complete",
    "r2_audit":           "\u2705 Formal notation R2 audit complete \u2014 N/N criteria encoded",
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


GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        # ADR-0179: axiom-first formulation. Four axioms govern all rules below.
        # A1 (epistemic authority): only tool-executed events have evidential standing;
        #   model recall, inference, and prediction have none, regardless of accuracy.
        # A2 (type discipline): each rung defines an artifact type; a tool-executed event
        #   satisfies a rung gate only if its output is of that rung\u2019s artifact type;
        #   cross-type output does not satisfy the gate regardless of correctness.
        # A3 (cycle isolation): each descent through the ladder is a new evidential context;
        #   artifacts from prior cycles have no standing in the current cycle.
        # R2 (minimal derivation): each artifact is the minimal transformation of the prior
        #   artifact that satisfies the current rung\u2019s type \u2014 form changes, intent does not.
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
        # A1 consequences: exec_observed verbatim rule
        "A rung is satisfied when and only when a tool-executed event appears in the transcript "
        "whose output is of that rung\u2019s artifact type. "
        "Every \U0001F534 Execution observed: sentinel at any rung must contain verbatim tool-call output, "
        "triple-backtick delimited, complete, nothing omitted \u2014 "
        "prose descriptions, inline summaries, model-generated text that resembles output, "
        "elision markers (\u2026, [truncated], [output continues]), "
        "reformatted text, and paraphrase are prohibited inside the block; "
        "if tool output is too long, the block ends at the last character the tool produced \u2014 no editorial closing; "
        "the only valid sequence is: tool call \u2192 \U0001F534 Execution observed: \u2192 triple-backtick block \u2014 "
        "the sentinel may not be written before the tool call exists in the transcript; "
        "a sentinel with prose content or no delimited block is void \u2014 "
        "fix by invoking the tool and re-emitting. "
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
        "From the criteria rung onward, the gap names a specific behavior currently absent or wrong, "
        "phrased as a currently-false assertion \u2014 "
        "\u201cthe attributes table does not render\u201d is valid; \u201cneed to implement a landing page\u201d is not. "
        "Each rung\u2019s artifact addresses only that gap \u2014 not all known requirements of the task \u2014 "
        "and is minimal: one independently testable behavior derived from the prose alone \u2014 "
        "if stating it requires names or structures not in the prose, it belongs in formal notation instead; "
        "if the criterion contains the word \u2018and\u2019 it is invalid \u2014 split it before continuing "
        "(\u2018the table renders Display Name\u2019 and \u2018the search bar filters results\u2019 are two criteria, not one); "
        "a criterion that names both a structural element and its data source is a conjunction \u2014 split before continuing; "
        "asserting a column header is present does not satisfy this rung \u2014 "
        "add a criterion asserting its content or effect; "
        "before writing the criteria artifact, locate \u2705 Manifest declared in the transcript "
        "and quote the gap text for this thread verbatim \u2014 "
        "a criterion written without a citable manifest excerpt is unanchored; "
        "narrowing the criterion, substituting a weaker behavior, "
        "or rewriting the criterion to match an easier implementation is a protocol violation; "
        "each criterion must state (a) observable behavior and (b) a falsifying condition statable without source files, "
        "function names, or variable names \u2014 if part (b) references implementation internals, "
        "the criterion is structural and must be rewritten before this rung closes; "
        "this is a content gate, not a self-check; "
        "after emitting the criteria artifact, proceed immediately to formal notation \u2014 "
        "enumerating remaining criteria or planning future gap cycles before the current cycle completes "
        "is a protocol violation; "
        "the next criterion for this thread may not be named until \u2705 Thread N complete has been emitted "
        "for the current criterion\u2019s cycle \u2014 \u2705 Thread N complete is the criterion-emergence gate; "
        "the first criteria rung after \u2705 Manifest declared emits exactly one criterion for Thread 1 \u2014 "
        "emitting criteria for multiple threads at the first criteria rung is a protocol violation; "
        "the manifest declared the thread list; the criteria rung instantiates the first thread\u2019s "
        "gap assertion only. "
        "Formal notation encodes only the criteria declared at the criteria rung \u2014 "
        "no additional invariants, no anticipated cases; "
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
        "Only validation artifacts may be produced at the executable validation rung \u2014 "
        "no other content is permitted before \u2705 Validation artifact V complete; "
        "each test function asserts exactly one behavioral property \u2014 one behavioral property per test function; "
        "multiple assertions are permitted only when they jointly constitute a single indivisible check "
        "(e.g., asserting a value is both non-null and of the expected type); "
        "before writing the test, re-read the formal notation and assert each structural constraint it encodes; "
        "a pre-existing test that happens to pass does not satisfy this rung; "
        "file reads, grep output, and manual inspection do not constitute executable validation \u2014 "
        "the artifact must be invocable by an automated tool; "
        "when the declared intent is to modify a test artifact, the test-under-modification is the implementation artifact "
        "for this cycle and the validation artifact must be a meta-test \u2014 an executable artifact that fails "
        "when the test-under-modification does not exhibit the criterion; "
        "before writing the test, check for an existing test file covering the same module \u2014 add there if so; "
        "when the artifact is modified, invoke a tool call to read the current test file before emitting carry-forward rows \u2014 "
        "carry-forward format: \u2018Carry-forward: prior failure [verbatim test name as it appeared in "
        "a \U0001F534 Execution observed sentinel] covers current test [verbatim test name as written in the artifact]\u2019 \u2014 "
        "each prior-failure name must be quotable verbatim from a \U0001F534 Execution observed sentinel; "
        "modification without carry-forward is a traversal violation; "
        "no implementation artifact may appear after modification until carry-forward has been emitted. "
        "before emitting \u2705 Validation artifact V complete, confirm via tool call that the artifact path "
        "does not pre-exist or is already failing \u2014 V-complete may not be emitted without this "
        "tool-executed result in the transcript; "
        "the validation artifact must reside within the project\u2019s version-controlled file tree; "
        "if the artifact asserts static state, run it before any edit \u2014 "
        "if it passes, the artifact is vacuous and must be rewritten; "
        "if the artifact asserts runtime behavior, perturb the implementation to force a red run \u2014 "
        "if it still passes after perturbation, the test is vacuous and must be rewritten; "
        "implementation edits may not begin until a red run exists in the transcript for the current cycle; "
        "\u2705 Validation artifact V complete may not be emitted unless a \U0001F534 Execution observed: "
        "showing the test failing exists in the transcript for the current cycle; "
        "emitting V-complete before seeing a red run is a protocol violation "
        "regardless of whether perturbation was attempted. "
        "\u2705 Validation artifact V complete must be emitted at the executable validation rung "
        "before the validation run observation label is written; "
        "if the observed running behavior label is written without a "
        "\u2705 Validation artifact V complete appearing in the transcript for the current cycle, "
        "the OBR rung is void \u2014 return to the executable validation rung and produce the artifact. "
        "Before writing the validation run observation rung label, "
        "invoke the validation artifact via a test runner \u2014 "
        "file reads, grep, directory listings, and static analysis produce static-analysis-type output, "
        "not validation-run-observation-type output, and do not satisfy this gate; "
        "a harness error (import failure, syntax error, missing file) is not a red run \u2014 "
        "the test must have been loadable, its assertions must have run, and they must have failed; "
        "fix the harness error before treating any run as a red witness; "
        "a green \U0001F534 Execution observed: is only valid as the post-implementation green "
        "if a prior \U0001F534 Execution observed: for the same artifact appeared after the most recent "
        "\U0001F7E2 Implementation gate cleared showing the test logic failing. "
        "At the validation run observation rung, run the validation artifact; "
        "emit \U0001F534 Execution observed: with verbatim output then \U0001F534 Gap: naming the first failure; "
        "stop there \u2014 do not enumerate multiple failures or plan fixes; "
        "after emitting \U0001F534 Gap: at the observation rung, the criteria rung label is the only valid next token; "
        "\U0001F6D1 HARD STOP \u2014 upward return to criteria rung is valid only after a "
        "\U0001F534 Execution observed: and \U0001F534 Gap: have been emitted "
        "at the validation run observation rung in the current cycle \u2014 "
        "emitting it at any other position is a protocol violation; "
        "HARD STOP may not be emitted at the executable validation rung \u2014 "
        "a harness error at EV requires fixing the harness, not an upward return; "
        "if the observed gap matches the prior cycle's gap, the edit did not address it \u2014 "
        "return to formal notation before any further edit. "
        "HARD STOP does not restart the session \u2014 \u2705 Ground entered and \u2705 Manifest declared "
        "are not re-emitted; the next token is the criteria rung label for the current thread; "
        "the prose re-emission rule applies to new gap cycles, not to HARD STOP returns. "
        "Upon writing the observed running behavior label, re-emit the criterion for this cycle \u2014 "
        "criterion re-emission is required: emitting the OBR label without immediately "
        "following it with the criterion text is a protocol violation; "
        "\u2705 Thread N complete may not appear without both the criterion re-emission and a "
        "\U0001F534 Execution observed: in the current OBR section; "
        "then immediately invoke the implemented artifact via a tool call and emit "
        "\U0001F534 Execution observed: with its verbatim output \u2014 "
        "the verbatim output must directly demonstrate the specific behavior named in the criterion; "
        "it must be what a non-technical observer of the running system would see \u2014 "
        "not the test suite, not process state unless the criterion is specifically about process state; "
        "a build output or compilation result never satisfies this gate regardless of what it names; "
        "for a React or web UI component, invoke the render utility (e.g., renderToStaticMarkup "
        "or the testing framework\u2019s render function reading container.innerHTML) "
        "and emit the resulting HTML fragment showing browser-visible content \u2014 "
        "starting a dev server does not satisfy this rung; "
        "if the implementation has no directly invocable artifact, invoke any non-test consumer "
        "of the changed artifact that demonstrates the declared behavior; "
        "a \U0001F534 Execution observed: block that is empty or blank, or contains only static-analysis output "
        "(file reads, grep results, directory listings), does not satisfy this gate at any rung \u2014 "
        "the block must contain output produced by running the artifact; "
        "if the declared gap names a real network endpoint, the OBS must include verbatim output showing "
        "a real HTTP request or response \u2014 a test run whose network calls are mocked does not satisfy this gate; "
        "before any tool call touching the filesystem at this rung, emit a provenance statement: "
        "\u2018Invoking [artifact] produced at [rung name] in this thread\u2019 \u2014 "
        "if the rung label cannot be located in the transcript, the tool call is prohibited; "
        "the provenance statement does not replace the tool call \u2014 the tool call must follow it in the same response; "
        "\u2705 Thread N complete may not be emitted unless a \U0001F534 Execution observed: "
        "with non-empty verbatim output appears in the transcript after the observed running behavior label "
        "in the current cycle \u2014 a provenance statement with no following \U0001F534 Execution observed: "
        "is a protocol violation; "
        "implementation edits, new files, and code changes are not permitted at this rung. "
        "\u2705 Thread N complete may not be emitted unless the observed running behavior label "
        "has been written after the most recent \U0001F7E2 Implementation gate cleared in this thread "
        "and a \U0001F534 Execution observed: sentinel appears immediately after it that directly demonstrates "
        "the criterion \u2014 a test pass is not a demonstration; "
        "if the \U0001F534 Execution observed: at the observed running behavior rung contains "
        "test runner output (pass counts, test names, duration summary), "
        "it does not satisfy the OBR gate \u2014 re-invoke the implemented artifact directly "
        "before continuing; \u2705 Thread N complete may not be emitted after an OBR "
        "\U0001F534 Execution observed: that shows test runner output; "
        "no implementation file was created or modified for this thread\u2019s gap in this cycle "
        "means the gap was already closed (return to criteria) or the test is vacuous (rewrite it); "
        "every failing test must be fixed or explicitly acknowledged in the transcript with a written reason \u2014 "
        "dismissing a failing test as unrelated without an explicit written acknowledgment is a protocol violation; "
        "\u2705 Thread N complete may not be emitted unless a \U0001F534 Execution observed: "
        "from a full test suite run exists in the transcript after the most recent OBR tool call in this thread \u2014 "
        "the only valid next action if no such result exists is the tool call that runs the suite; "
        "once \u2705 Thread N complete is emitted no further output in that cycle is valid; "
        "at most one thread is in progress at a time \u2014 no output for thread N+1 may appear "
        "until \u2705 Thread N complete has been emitted for thread N; "
        "this gate applies to all rungs, not only the prose rung. "
        "Before writing the criteria, formal notation, executable validation, executable implementation, "
        "or observed running behavior label, emit \U0001F534 Gap: naming the declared gap \u2014 "
        "what the prior rung\u2019s artifact leaves unresolved; immediately produce the rung artifact \u2014 "
        "only the validation run observation rung stops after naming the gap. "
        "\U0001F7E2 Implementation gate cleared licenses the first edit \u2014 it does not complete the thread; "
        "after emitting it, the executable implementation rung, the observed running behavior rung, "
        "and their required tool-executed events must still fire before \u2705 Thread N complete is valid; "
        "the next required action after \U0001F7E2 is a tool call that creates or modifies an implementation file; "
        "\u2705 Thread N complete may not appear until the observed running behavior rung has fired for this thread. "
        "Each sentence in the prose containing a behavioral predicate \u2014 any action verb attributing "
        "behavior to the system \u2014 must be followed inline by a bracketed thread marker: [T: gap-name]; "
        "before emitting \u2705 Manifest declared, count every [T: gap-name] marker in the prose \u2014 "
        "the manifest thread list must contain exactly one entry per distinct gap-name; "
        "a [T: gap-name] marker in the prose with no corresponding manifest entry is a protocol violation. "
        # A3 consequences: cycle isolation
        "The prose rung must be re-emitted at the start of every cycle \u2014 the first cycle, "
        "any subsequent cycle, and any cycle following an upward return; "
        "the criterion must be immediately derivable from the re-emitted prose. "
        "\U0001F7E2 Implementation gate cleared requires a \U0001F534 Execution observed: "
        "from the current cycle\u2019s validation run observation rung \u2014 not from a prior cycle \u2014 "
        "to exist in output; "
        "the VRO rung label must appear in the transcript for the current cycle \u2014 "
        "a run at the EV rung does not satisfy the VRO gate regardless of whether it produced a failure. "
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
        "the only protocol-defined stop is at the validation run observation rung after emitting \U0001F534 Gap:; "
        "all other rung transitions are continuous within the same response. "
        "When beginning mid-ladder, locate the highest already-instantiated rung, update it, then descend; "
        "every descent through executable implementation requires executable validation "
        "and validation run observation to have fired for the current gap, including after an upward return. "
        "One edit per re-run cycle; after each edit re-run the validation artifact before any further edit. "
        "Upward returns follow the failure class: "
        "if the implementation did not close the gap, loop within executable implementation; "
        "if the spec did not model the criterion, return to formal notation; "
        "observation cannot be produced is a prose-description failure, not an implementation failure \u2014 "
        "return to the prose rung and update it. "
        "After every upward return, a new \u2705 Validation artifact V complete must be emitted "
        "for the current cycle\u2019s gap \u2014 an artifact written in a prior cycle does not satisfy this gate. "
        "Reconciliation gate: at every upward rung transition, reconcile all artifacts against I "
        "and update any pre-existing document that records I (ADR, README, spec) before redescending. "
        "Before producing the final report, invoke the delivered system end-to-end via a tool call "
        "and emit \U0001F534 Execution observed: showing the primary behavioral intent is satisfied \u2014 "
        "this is the post-delivery integration observation; "
        "if it fails, open a new gap cycle before producing the final report. "
        "After emitting \u2705 Manifest exhausted, produce a final report containing "
        "prose, criteria, and formal notation for each thread in order \u2014 "
        "before writing each section, locate the artifact in the prior transcript; "
        "if it cannot be found verbatim in the transcript, it may not appear in the final report; "
        "no new behavioral claims, no coverage summaries, no suggestions; "
        "then reconcile any documents the implementation affects. "
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
