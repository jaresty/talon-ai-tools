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
        "Once \u2705 Ground entered has been emitted in this session, "
        "every subsequent response must begin by identifying the current rung and the current gap "
        "before any other content \u2014 ground protocol does not terminate at \u2705 Manifest exhausted; "
        "it remains active until the session ends or the user explicitly exits. "
        "A rung is satisfied when and only when a tool-executed event appears in the transcript "
        "whose output is of that rung\u2019s artifact type \u2014 inference, prediction, and prior knowledge "
        "do not satisfy rung gates regardless of accuracy; "
        "output from a different rung\u2019s artifact type does not satisfy the gate regardless of what it implies "
        "(running the test suite at the observed running behavior rung produces validation-run-observation-type output, "
        "not observed-running-behavior-type output, and does not satisfy that gate). "
        "Every \U0001F534 Execution observed: sentinel at any rung must contain verbatim tool-call output, "
        "triple-backtick delimited, complete, nothing omitted \u2014 "
        "prose descriptions, inline summaries, and model-generated text that resembles output "
        "do not satisfy this requirement at any rung. "
        "The triple-backtick block constitutes the sentinel body; "
        "no content may appear inside the block that was not produced by the tool call \u2014 "
        "elision markers (\u2026, [truncated], [output continues], [remaining output omitted]), "
        "reformatted text, and paraphrase are prohibited inside the block; "
        "if tool output is too long to include in full, the block must end at a natural output boundary "
        "with the last character the tool produced \u2014 no editorial closing. "
        "The execution-observed sentinel gates the tool invocation \u2014 "
        "the only valid next action after emitting this sentinel is the tool call it names; "
        "any response content between this sentinel and the tool call converts the sentinel to retroactive "
        "regardless of sequence, because the model will have already interpreted that content before the tool runs; "
        "a sentinel-to-tool sequence with intervening content must be treated as if the sentinel was not emitted \u2014 "
        "re-emit and re-run. "
        "Rule 2: each artifact derives from the prior rung \u2014 form changes, intent does not; "
        "a skipped rung voids all artifacts below it; "
        "each artifact addresses only the gap declared by the prior rung \u2014 nothing beyond it. "
        "Rule 3: every thread ends when tool output names the declared gap; stop there. "
        "I is the declared intent governing the invocation; I precedes and is not itself an artifact; "
        "each artifact must be self-sufficient to derive the next without consulting I; "
        "before closing a rung artifact, identify every decision the next rung must make "
        "that is not fully determined by this artifact\u2019s explicit content \u2014 "
        "state each such decision as an open constraint in the artifact; "
        "an artifact with no stated open constraints claims to be fully downward-sufficient; "
        "faithful derivation requires form to change, intent to stay fixed. "
        "Advance through every feasible rung; completeness governs rung depth, not rung existence; "
        "each rung may not be skipped or combined with another, including the observed running behavior rung \u2014 it is required in every cycle. "
        "Before any tool call or file read, check: if no \U0001F534 Gap: sentinel exists in output yet, emit it now; "
        "before emitting \U0001F7E2 Implementation gate cleared, check: does a \U0001F534 Execution observed: sentinel "
        "from the current cycle's validation run observation rung \u2014 not from a prior cycle \u2014 "
        "exist in output? if not, do not emit it \u2014 "
        "produce the executable validation artifact instead. "
        "\U0001F7E2 Implementation gate cleared licenses the first edit \u2014 it does not complete the thread; "
        "after emitting it, the executable implementation rung, the observed running behavior rung, "
        "and their required tool-executed events must still fire before \u2705 Thread N complete is valid; "
        "the next required action after \U0001F7E2 is a tool call that creates or modifies an implementation file \u2014 "
        "\u2705 Thread N complete, a new criteria cycle, or any other sentinel may not appear "
        "until at least one edit and its post-edit re-run have occurred "
        "and the observed running behavior rung has fired for this thread. "
        "Before writing the criteria, formal notation, executable validation, executable implementation, "
        "or observed running behavior label, emit \U0001F534 Gap: naming what the prior rung\u2019s artifact "
        "leaves unresolved; immediately produce the rung artifact \u2014 "
        "only the validation run observation rung stops after naming the gap. "
        "The prose rung must be re-emitted at the start of every cycle \u2014 the first cycle, "
        "any subsequent cycle, and any cycle following an upward return; "
        "the criterion must be immediately derivable from the re-emitted prose. "
        "From the criteria rung onward, the gap names a specific behavior currently absent "
        "or wrong, phrased as a currently-false assertion \u2014 "
        "\u201cthe attributes table does not render\u201d is valid; "
        "\u201cneed to implement a landing page\u201d is not; "
        "if no currently-false behavior remains, emit \u2705 Manifest exhausted \u2014 "
        "\u2705 Manifest exhausted may not be emitted unless a \u2705 Thread N complete sentinel exists "
        "in the transcript for each thread declared in \u2705 Manifest declared \u2014 "
        "check the thread count before emitting. "
        "Each rung\u2019s artifact addresses only that gap \u2014 not all known requirements of the task \u2014 "
        "and is minimal: one independently testable behavior derived from the prose alone \u2014 "
        "if stating it requires names or structures not in the prose, it belongs in formal notation instead; "
        "if the criterion contains the word \u2018and\u2019 it is invalid \u2014 split it before continuing "
        "(\u2018the table renders Display Name\u2019 and \u2018the search bar filters results\u2019 "
        "are two criteria, not one); "
        "a criterion that names both a structural element and its data source is a conjunction \u2014 "
        "\u2018renders columns with data fetched from the endpoint\u2019 must be split into "
        "\u2018columns render\u2019 and \u2018data is fetched from the endpoint\u2019 before continuing; "
        "a criterion that asserts only that a structural element exists is not behavioral \u2014 "
        "asserting a column header is present does not satisfy this rung; "
        "add a criterion asserting the element\u2019s content or effect "
        "(the row displays the value from the data source); "
        "the criterion for thread N must name the same behavior as the gap declared for thread N "
        "in \u2705 Manifest declared \u2014 narrowing the criterion, substituting a weaker behavior, "
        "or rewriting the criterion to match an easier implementation is a protocol violation; "
        "if the declared gap cannot be satisfied, return to the prose rung and revise the manifest. "
        "Each criterion must be written in two parts: "
        "(a) observable behavior \u2014 what a non-technical observer of the running system would see; "
        "(b) falsifying condition \u2014 what behavioral gap would cause this criterion to fail; "
        "before advancing, verify both parts are present; "
        "a criterion without an explicit falsifying condition is incomplete at time of production "
        "and must not be advanced from; "
        "if the falsifying condition requires knowledge of implementation internals, "
        "the criterion is structural, not behavioral, and must be rewritten. "
        "Formal notation encodes only the criteria declared at the criteria rung \u2014 "
        "no additional invariants, no anticipated cases; "
        "it produces only type signatures, interfaces, pseudocode, and structural invariants \u2014 "
        "the test of valid formal notation is that it cannot be directly compiled or executed without modification; "
        "if placing the notation verbatim in the source tree would produce a runnable artifact, "
        "it is implementation code and voids the rung; "
        "annotation-decorated classes, repository interfaces, and any construct that compiles as-is "
        "are implementation code regardless of whether they contain imperative logic. "
        "Only validation artifacts may be produced at the executable validation rung \u2014 "
        "no other content is permitted before \u2705 Validation artifact V complete; "
        "the artifact must be invocable by an automated tool; "
        "before writing the test, re-read the formal notation and assert each structural constraint it encodes; "
        "each test function contains exactly one assertion \u2014 one assertion per test function; "
        "a pre-existing test that happens to pass does not satisfy this rung \u2014 "
        "add to an existing test file covering the same module if one exists, otherwise create a new file; "
        "when the validation artifact is modified \u2014 tests added, rewritten, or mocks changed \u2014 "
        "emit a carry-forward statement before any implementation artifact: "
        "carry-forward format: \u2018Carry-forward: prior failure [verbatim test name as it appeared in "
        "a \U0001F534 Execution observed sentinel] covers current test [verbatim test name as written in the artifact]\u2019 \u2014 "
        "one row per current test; each prior-failure name must be quotable verbatim from a "
        "\U0001F534 Execution observed sentinel in this conversation; "
        "any current test whose name does not appear in a carry-forward row is unconditionally uncovered; "
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
        "implementation edits may not begin until a red run exists in the transcript for the current cycle \u2014 "
        "if the validation artifact passes before any implementation edit, "
        "either the test is vacuous (rewrite it) or the gap is already closed (return to criteria); "
        "\u2705 Validation artifact V complete may not be emitted unless a \U0001F534 Execution observed: "
        "showing the test failing exists in the transcript for the current cycle \u2014 "
        "write the test, run it, confirm it fails, then emit V-complete; "
        "emitting V-complete before seeing a red run is a protocol violation "
        "regardless of whether perturbation was attempted. "
        "\u2705 Validation artifact V complete must be emitted at the executable validation rung "
        "before the validation run observation label is written. "
        "Before writing the validation run observation rung label, "
        "invoke the validation artifact via a tool call \u2014 "
        "predicting what the run would show does not satisfy this gate regardless of accuracy; "
        "a green \U0001F534 Execution observed: is only valid as the post-implementation green "
        "if a prior \U0001F534 Execution observed: for the same artifact appeared after the most recent "
        "\U0001F7E2 Implementation gate cleared for this thread showing the test logic failing \u2014 "
        "a harness error (import failure, syntax error, missing file) is not a red run; "
        "the test must have been loadable, its assertions must have run, and they must have failed; "
        "fix the harness error before treating any run as a red witness \u2014 "
        "do not proceed to the implementation gate until a loadable run with failing assertions "
        "exists in the transcript for the current cycle. "
        "At the validation run observation rung, run the validation artifact; "
        "emit \U0001F534 Execution observed: with verbatim output then \U0001F534 Gap: naming the first failure; "
        "stop there \u2014 do not enumerate multiple failures or plan fixes; "
        "after emitting \U0001F534 Gap: at the observation rung, the criteria rung label is the "
        "only valid next token in the response \u2014 "
        "any other content before the criteria label is a protocol violation; "
        "\U0001F6D1 HARD STOP \u2014 upward return to criteria rung is valid only after a "
        "\U0001F534 Execution observed: and \U0001F534 Gap: have been emitted "
        "at the validation run observation rung in the current cycle \u2014 "
        "emitting it after a criteria label, after a formal notation label, "
        "or at any other position is a protocol violation; "
        "if the observed gap matches the prior cycle's gap, the edit did not address it \u2014 "
        "return to formal notation before any further edit. "
        "Upward returns follow the failure class: "
        "if the implementation did not close the gap, loop within executable implementation; "
        "if the spec did not model the criterion, return to formal notation; "
        "observation cannot be produced is a prose-description failure, not an implementation failure \u2014 "
        "return to the prose rung and update it. "
        "One edit per re-run cycle; after each edit re-run the validation artifact before any further edit. "
        "After every upward return, a new \u2705 Validation artifact V complete must be emitted "
        "for the current cycle\u2019s gap before the implementation gate may fire \u2014 "
        "an artifact written in a prior cycle does not satisfy this gate even if it covers the same path. "
        "Upon writing the observed running behavior label, re-emit the criterion for this cycle, "
        "then immediately invoke the implemented artifact via a tool call "
        "and emit \U0001F534 Execution observed: with its verbatim output \u2014 "
        "the verbatim output must directly demonstrate the specific behavior named in the criterion; "
        "it must be what a non-technical observer of the running system would see \u2014 "
        "not the test suite, not process state (server started, build succeeded, exit code 0) "
        "unless the criterion is specifically about process state; "
        "a build output, bundle manifest, or compilation result never satisfies this gate "
        "regardless of what it names \u2014 direct demonstration means the running feature produced the output, "
        "not the build tool; "
        "for a UI component, this means browser-visible text and values \u2014 "
        "not a test runner\u2019s DOM query result; "
        "if the output does not directly demonstrate the criterion, emit the gap and return upward; "
        "a \U0001F534 Execution observed: whose verbatim block is empty or blank does not satisfy this gate \u2014 "
        "a verification script, console log, or tool call that produces no visible output is not valid OBS evidence; "
        "invoke a tool call that produces non-empty output demonstrating the behavior; "
        "if the declared gap names a real network endpoint (fetches from, calls, integrates with), "
        "the OBS must include verbatim output showing a real HTTP request or response \u2014 "
        "a test run whose network calls are mocked does not satisfy this gate; "
        "if the implementation has no directly invocable artifact, invoke any non-test consumer "
        "of the changed artifact that demonstrates the declared behavior; "
        "before any tool call touching the filesystem at this rung, emit a provenance statement: "
        "\u2018Invoking [artifact] produced at [rung name] in this thread\u2019 \u2014 "
        "the cited rung must be quotable from this conversation; "
        "a tool call with no citable provenance is creating a new artifact regardless of characterization "
        "and is prohibited at this rung; "
        "implementation edits, new files, and code changes are not permitted at this rung. "
        "\u2705 Thread N complete may not be emitted unless the observed running behavior label "
        "has been written after the most recent \U0001F7E2 Implementation gate cleared in this thread "
        "and a \U0001F534 Execution observed: sentinel appears immediately after it "
        "and the OBS output directly demonstrates each criterion declared in this thread \u2014 "
        "a test pass is not a demonstration; "
        "no implementation file was created or modified for this thread\u2019s gap in this cycle "
        "means the gap was already closed (return to criteria) or the test is vacuous (rewrite it) \u2014 "
        "Thread N complete may not be emitted when no implementation edit was made in this cycle; "
        "before emitting \u2705 Thread N complete or \u2705 Manifest exhausted, run the full test suite; "
        "every failing test must be fixed or explicitly acknowledged in the transcript with a written reason \u2014 "
        "dismissing a failing test as unrelated without an explicit written acknowledgment is a protocol violation; "
        "once \u2705 Thread N complete is emitted no further output in that cycle is valid. "
        "Each sentence in the prose containing a behavioral predicate \u2014 any action verb attributing "
        "behavior to the system (fetches, requires, displays, filters, renders, validates, authenticates, "
        "loads, saves, or similar) \u2014 must be followed inline by a bracketed thread marker: [T: gap-name]; "
        "these thread markers become the authoritative enumeration for the manifest and the Thread N complete check; "
        "a prose rung with unmarked behavioral predicates is incomplete at time of production. "
        "Before emitting \u2705 Manifest declared, scan every sentence in the prose for behavioral predicates "
        "(fetches, requires, displays, filters, renders, validates, authenticates, loads, saves, "
        "or any similar action verb) \u2014 each distinct predicate requires a separate thread; "
        "a manifest that omits a behavioral predicate from the prose is incomplete and may not be emitted. "
        "\u2705 Manifest declared may be emitted exactly once per invocation \u2014 "
        "at the prose rung, after the first gap is named; "
        "re-emitting it at any other rung is a protocol violation. "
        "Outputting a rung label is what begins that rung \u2014 it is not a heading or annotation; "
        "a rung whose label has not been output has not begun and no artifact for it may exist. "
        "When beginning mid-ladder, locate the highest already-instantiated rung, "
        "update it to reflect the intended change, then descend; "
        "every descent through executable implementation requires executable validation "
        "and validation run observation to have fired for the current gap, "
        "including after an upward return. "
        "Reconciliation gate: at every upward rung transition, "
        "reconcile all artifacts at that rung against I before redescending; "
        "if prose has evolved, any pre-existing document that records I "
        "(ADR, README, spec) must be updated before redescending \u2014 "
        "this is a gate precondition, not a final-report step; "
        "documentation is a reconciliation artifact, not a thread. "
        "Each completion sentinel is valid only at its defining rung \u2014 "
        "emitting a sentinel outside the rung where it is defined is a protocol violation; "
        "a sentinel used as a narrative summary or wrap-up is not a valid emission. "
        "Before producing the final report, invoke the delivered system end-to-end via a tool call "
        "and emit \U0001F534 Execution observed: showing the primary behavioral intent from the prose is satisfied \u2014 "
        "this is the post-delivery integration observation; "
        "if it fails, open a new gap cycle before producing the final report. "
        "After emitting \u2705 Manifest exhausted, produce a final report containing "
        "prose, criteria, and formal notation for each thread in order; "
        "the final report copies artifacts already emitted in the thread rungs \u2014 "
        "before writing each section, locate the artifact in the prior transcript; "
        "if it cannot be found verbatim in the transcript, it may not appear in the final report; "
        "no new behavioral claims, no coverage summaries, no suggestions may appear in the final report; "
        "then reconcile any documents (README, specs, ADRs) the implementation affects \u2014 "
        "this reconciliation is part of the final report, not a separate thread. "
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
