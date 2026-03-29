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
        "type_label": "prose-type",
        "artifact": "natural language description of intent and constraints",
        "gate": "I declared",
        "voids_if": "skipped",
    },
    {
        "name": "criteria",
        "type_label": "criteria-type",
        "artifact": "falsifiable behavioral acceptance conditions",
        "gate": "prose complete",
        "voids_if": "criterion is structural/implementation rather than behavioral",
    },
    {
        "name": "formal notation",
        "type_label": "notation-type",
        "artifact": "non-executable specification with behavioral invariants + R2 audit",
        "gate": "criteria complete; R2 audit 0 UNENCODED entries",
        "voids_if": "UNENCODED entries remain; audit not a separate named section",
    },
    {
        "name": "executable validation",
        "type_label": "EV-type",
        "artifact": "test file invocable by an automated tool, within project tree",
        "gate": "formal notation R2 audit complete",
        "voids_if": "implementation code included; outside project tree; pre-existing artifact",
    },
    {
        "name": "validation run observation",
        "type_label": "VRO-type",
        "artifact": "exec_observed sentinel with verbatim failure naming declared gap",
        "gate": "executable validation artifact runs",
        "voids_if": "build/compile error; green run without prior failure; infrastructure-only output",
    },
    {
        "name": "executable implementation",
        "type_label": "EI-type",
        "artifact": "implementation source edits; one edit per re-run cycle",
        "gate": "exec_observed + gap declared; impl_gate sentinel emitted",
        "voids_if": "multiple edits without intervening re-run; newly-passing test has no prior failure",
    },
    {
        "name": "observed running behavior",
        "type_label": "OBR-type",
        "artifact": "live-process output — output produced by a tool call that starts or queries a running process, directly demonstrating all criteria declared for this thread; reading any file does not satisfy this type regardless of content",
        "gate": "implementation complete; exec_observed + gap for behavior from I",
        "voids_if": "new files created; output names only infrastructure state; file read used as evidence; test runner output used as OBR live-process evidence voids this rung; test runner output at OBR step 5 does not void this rung",
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
    """Generate a compact rung table (name | type_label | artifact | gate | void condition)."""
    header = "Rung table \u2014 name | type | artifact type | gate condition | void condition: "
    rows = "; ".join(
        f"{e['name']} [{e['type_label']}]: artifact=\u201c{e['artifact']}\u201d, gate=\u201c{e['gate']}\u201d, voids_if=\u201c{e['voids_if']}\u201d"
        for e in RUNG_SEQUENCE
    )
    return header + rows + ". "


def _type_taxonomy_block() -> str:
    """Generate the artifact type classification section (ADR-0189: Attractor B closure)."""
    header = "Artifact type classification \u2014 each rung produces exactly one type; " \
             "output is classified by its production method, not its content: "
    rules = "; ".join(
        f"{e['type_label']}: output of the {e['name']} rung"
        for e in RUNG_SEQUENCE
    )
    notes = (
        "VRO-type is produced by running a test suite \u2014 "
        "any test runner invocation produces VRO-type output regardless of pass/fail; "
        "OBR-type is produced by a tool call that performs live-process invocation \u2014 "
        "reading a file, running tests, or static analysis never produces OBR-type output; "
        "a passing test proves the test harness\u2019s assertions pass \u2014 "
        "not that the described behavior exists as a running system; "
        "this is why test runner output is VRO-type and cannot satisfy the OBR gate regardless of the result; "
        "for a UI component, the OBR invocable artifact is a running dev server or browser process \u2014 "
        "a tool call that starts the dev server and queries it via HTTP or browser navigation; "
        "a test renderer (such as @testing-library/react render()) produces VRO-type, not OBR-type, "
        "because the UI component was instantiated in a synthetic DOM, never served to a client; "
        "a test runner executing in browser mode (chromium, webkit, firefox) also produces VRO-type \u2014 "
        "the execution environment is a browser process, but the production method is still a test runner invocation; "
        "serving a component to a real client requires an HTTP request to a running dev server, "
        "not a test runner invocation regardless of browser mode; "
        "this is why a UI component thread requires a running dev server at the OBR rung, "
        "not a test renderer invocation. "
        "EI-type is produced by file-write tool calls modifying implementation source \u2014 "
        "file-write tool calls at the EV rung produce EV-type, not EI-type; "
        "when A4 requires an artifact of the correct type, classify by production method first \u2014 "
        "content that resembles a different type does not change the classification."
    )
    return header + rules + ". " + notes + " "


GROUND_PARTS_MINIMAL: dict[str, str] = {
    "core": (
        # ADR-0198: minimum-viable refactor — axioms + rung table + type taxonomy +
        # sentinel formats + OBR sequence + thread sequencing + why-sentences only.
        # All derivable corollary prose removed.
        "This protocol exists because a model\u2019s description of completed work is indistinguishable from actually completing it \u2014 "
        "every gate enforces the distinction by requiring a piece of reality before any claim about reality. "
        "Every rung gate exists to prevent one class of error: claiming evidence without producing it. "
        # Axiom block
        "A1 (Epistemic authority): only tool-executed events have evidential standing; "
        "inference, prediction, and prior knowledge have none, regardless of accuracy. "
        "A2 (Type discipline): each rung defines an artifact type; a gate is satisfied only by a tool-executed event "
        "whose output is of that rung\u2019s artifact type; type is determined by production method, not content. "
        "A3: each descent through the ladder is a new evidential context \u2014 "
        "the evidential context resets at every re-emission of the prose rung label. "
        "R2 (Minimal derivation): each artifact is the minimal transformation of the prior artifact "
        "that satisfies the current rung\u2019s type \u2014 form changes, intent does not; "
        "a skipped rung voids all artifacts below it. "
        "Each artifact must be derived from the prior rung\u2019s actual content \u2014 "
        "not from the original intent reconstructed from memory \u2014 "
        "because divergence from intent is only visible at the rung where the prior artifact\u2019s specificity is insufficient; "
        "this is why R2 (form changes, intent does not) is load-bearing: "
        "it ensures the chain of derivation is unbroken and misalignment surfaces at the earliest possible rung. "
        "A4 (Provenance): an artifact satisfies a rung gate only if it was produced by a tool call "
        "made in direct response to the gap declared at the immediately prior rung in the current cycle; "
        "evidence from a prior cycle, a different thread, or a different gap does not satisfy any gate "
        "regardless of type match. "
        "A5 (Cycle identity): a cycle for a thread is the interval bounded by the prose rung emission "
        "that opens it and either \u2705 Thread N complete or an upward return that closes it; "
        "the current cycle is the interval opened by the most recent prose emission for the current thread; "
        "prose re-emission for one thread does not affect the cycle identity of any other thread. "
        "P6 (Cross-thread convergence): when the same gap class \u2014 identified by matching error text, "
        "failing selector, or component name \u2014 appears at the VRO rung across two or more threads in the same session, "
        "subsequent threads may not proceed past the VRO rung for that gap class "
        "until a root-cause fix has been applied and witnessed in a passing VRO run; "
        "routing around a recurring gap by changing the test does not satisfy this gate. "
        "P5 (Convergence): a thread converges only when its gap closes; "
        "if EI has executed without gap closure and the criterion has not changed since the most recent "
        "prior HARD STOP cycle for this thread, the criterion is underspecified \u2014 return to the criteria rung; "
        "this is mandatory, not optional. "
        "P1 (Evidential boundary): a rung gate is satisfied if and only if a tool-executed event "
        "appears in the current-cycle transcript whose output is classified as that rung\u2019s artifact type; "
        "no other event \u2014 inference, prediction, prior-cycle output, or any non-tool event \u2014 satisfies any gate regardless of accuracy; "
        "cross-rung output within the same cycle does not satisfy a gate \u2014 "
        "a tool call at rung X does not satisfy the gate at rung Y even if both are in the current cycle. "
        "a rung label may not be emitted until its gate conditions are met; "
        "the gate condition for each rung is the rung table\u2019s gate column. "
        "P3 (Scope discipline): each rung artifact addresses exactly the gap declared by the prior rung \u2014 "
        "nothing beyond it; one gap per cycle; one criterion per thread per cycle; one edit per re-run; "
        "each sentinel defined in the sentinel block is valid exactly once at its defining rung per invocation unless noted. "
        "After \u2705 Manifest declared, the only valid next token is the criteria rung label for Thread 1 \u2014 "
        "no criteria for other threads, no planning narration, no other content; "
        "all seven rungs for Thread N must complete before any content for Thread N+1 may appear. "
        "no anticipation of future gaps, no additional invariants, no coverage beyond the declared gap; "
        "one edit means exactly one tool call that creates or modifies a file \u2014 "
        "narrating a change without a file-write tool call is not an edit. "
        "P4 (Rung action discipline): each rung has a closed action set \u2014 "
        "any tool call outside it is a protocol violation regardless of outcome; "
        "the constraint is type, not count \u2014 multiple writes are permitted when all targets are the correct type; "
        "the sequence enumerated for a rung is binding for completion \u2014 "
        "no completion sentinel for the rung may be emitted until the full sequence has been executed in order; "
        "no content other than the next step in the sequence may appear between steps; "
        "prose reasoning, debugging narration, planning, or any other unlabeled text between rung labels "
        "is a protocol violation \u2014 all content emitted after a rung label and before the next rung label "
        "must be of that rung's artifact type; "
        "prose, criteria, and formal notation rungs: no tool calls; "
        "EV rung: (1) pre-existence or pre-failure check, (2a) write import block, run import check \u2014 "
        "on failure write a stub containing only the names the import statement requires — "
        "no additional exports, no conditional logic, no non-empty bodies — and re-run; "
        "the import check must pass before step (2b) may begin; "
        "if the import check still fails after the stub, repair the stub and re-run; "
        "advancing to (2b) while the import check is failing is a protocol violation; "
        "(2b) write assertion bodies, "
        "(3) test runner \u2014 in order \u2014 "
        "writing implementation files at the EV rung is a protocol violation; "
        "VRO rung: test runner only; "
        "EI rung: implementation file-writes only \u2014 "
        "modifying a test file at the EI rung is a protocol violation "
        "unless the meta-test pattern is in effect; "
        "a stub is not the implementation \u2014 leaving a stub as the final artifact is a protocol violation; "
        "writing a file that served as the EV artifact in a prior cycle is a protocol violation "
        "unless the meta-test pattern is in effect; "
        "OBR rung: (1) criterion re-emission, (2) provenance statement, "
        "(3) manual live-process invocation of the implementation artifact \u2014 for artifacts "
        "requiring a start step before querying, live-process invocation consists of "
        "process-start followed by query, both tool calls required; "
        "a valid query is an HTTP request or browser navigation to the running server\u2019s URL \u2014 "
        "a test runner invocation is not a valid query regardless of whether a dev server was started first; "
        "test runner after dev server start produces VRO-type output and voids the OBR rung \u2014 "
        "(4) exec_observed sentinel with verbatim output, "
        "(5) test suite run \u2014 in that order \u2014 read-only only, no writes. "
        # Rung table — seven rows: name, type_label, artifact type, gate condition, void condition
        + _rung_table()
        # Type taxonomy with why-sentences (ADR-0189, ADR-0197)
        + _type_taxonomy_block()
        # exec_observed format rule (non-derivable verbatim requirement)
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
        # Session persistence (non-derivable policy)
        "Once \u2705 Ground entered has been emitted in this session, "
        "every subsequent response must begin by identifying the current rung and the current gap "
        "before any other content \u2014 ground protocol does not terminate at \u2705 Manifest exhausted; "
        "it remains active until the session ends or the user explicitly exits. "
        "\u2705 Manifest exhausted may not be emitted unless the count of \u2705 Thread N complete sentinels "
        "in this session equals the N declared in \u2705 Manifest declared \u2014 "
        "emitting it before all declared threads are complete is a protocol violation. "
        )
        + "Each rung forces a kind of specificity the prior rung cannot enforce: "
        "prose makes intent legible, criteria makes it falsifiable, formal notation makes it precise, "
        "EV makes it executable, VRO confirms it fails, EI produces the fix, OBR confirms it runs; "
        "skipping a rung leaves open the escape route that rung closes. "
        + _rung_names_sentence()
        + " "
        + _sentinel_block()
        # Non-derivable escape-route-closers (compact form, ADR-0198)
        + (
        # exec_observed verbatim rule + green-post-red constraint
        "Each completion sentinel is valid only at its defining rung. "
        # Prose rung
        "Each sentence in the prose containing a behavioral predicate must be followed inline by a thread marker [T: gap-name]; "
        "[T: gap-name] markers are valid only in the prose rung; "
        "using a thread marker in any other rung is a protocol violation; "
        "before emitting \u2705 Manifest declared, count every [T: gap-name] marker in the prose \u2014 "
        "the manifest thread list must contain exactly one entry per distinct gap-name. "
        "Before emitting \u2705 Manifest declared, scan every sentence in the prose for behavioral predicates "
        "(fetches, requires, displays, filters, renders, validates, authenticates, loads, saves, "
        "or any finite verb where the subject is the system and the object is a data entity, user action, or external system) \u2014 "
        "each distinct predicate requires a separate thread; "
        "each manifest entry is a short gap label \u2014 a noun phrase naming the gap, not a behavioral assertion; "
        "count the [T: gap-name] markers in the prose you just wrote to confirm every predicate is covered. "
        "Before emitting \u2705 Manifest declared, count the thread entries in the list \u2014 "
        "the N in '\u2705 Manifest declared \u2014 N threads:' must equal the count of listed threads. "
        "Before emitting \u2705 Manifest declared, if the prose contains no [T: gap-name] markers, "
        "\u2705 Manifest declared is blocked \u2014 re-emit the prose with [T: gap-name] markers added inline. "
        "\u2705 Manifest declared opens the thread manifest for the session; "
        "a revised manifest may be emitted when a new gap is discovered mid-run \u2014 "
        "return to prose, re-emit for all incomplete threads with the new gap included, "
        "then emit \u2705 Manifest declared with the revised thread list; "
        "Completed threads are closed and may not be re-opened by a revision. "
        "only threads declared in \u2705 Manifest declared may be addressed \u2014 "
        "creating a thread not in the manifest is a protocol violation. "
        "When the prose contains two or more behavioral threads, "
        "one additional integration thread must be declared as the final manifest entry; "
        "the integration thread criterion asserts composed behavior across at least two other threads "
        "in a single end-to-end invocation; "
        "the integration thread may not be declared complete until all other threads are complete; "
        "omitting the integration thread when the manifest has two or more behavioral threads is a protocol violation. "
        # Criteria rung
        "The gap names a specific behavior currently absent or wrong, phrased as a currently-false assertion \u2014 "
        "'the attributes table does not render' is valid; 'need to implement a landing page' is not. "
        "\U0001f534 Gap: must be the first content after the criteria rung label \u2014 "
        "writing the criterion before \U0001f534 Gap: is a protocol violation; "
        "the Gap names the currently-false assertion that the criterion will make true; "
        "writing the criterion first proposes a repair before naming what is broken. "
        "\U0001f534 Gap: at the criteria rung is not a stop point \u2014 "
        "the criterion must appear in the same response immediately following the Gap. "
        "before writing the criteria artifact, locate \u2705 Manifest declared in the transcript "
        "and quote the gap text for this thread verbatim \u2014 "
        "a criterion written without a citable manifest excerpt is unanchored; "
        "narrowing the criterion, substituting a weaker behavior, "
        "or rewriting the criterion to match an easier implementation is a protocol violation. "
        "each criterion states (a) one observable behavior and (b) a falsifying condition referencing "
        "no implementation internals (no file names, function names, or variable names); "
        "this is a content gate, not a self-check; "
        "one independently testable behavior derived from the prose alone \u2014 "
        "if stating it requires names or structures not in the prose, it belongs in formal notation instead. "
        "if the criterion contains the word \u2018and\u2019 it is a conjunction \u2014 split before continuing "
        "(\u2018the table renders Display Name\u2019 and \u2018the search bar filters results\u2019 are two criteria, not one); "
        "a criterion that names both a structural element and its data source is a conjunction \u2014 split before continuing; "
        "asserting a column header is present does not satisfy this rung \u2014 add a criterion asserting its content or effect. "
        "after the criterion is written, the only valid next token is the formal notation rung label; "
        "each rung label opens a content-type context \u2014 "
        "criteria-type content (a falsifiable behavioral assertion) belongs to the criteria rung, "
        "notation-type content (type signatures, interfaces, invariants, pseudocode) belongs to the formal notation rung; "
        "emitting content whose type belongs to a different rung before that rung\u2019s label fires "
        "is a type violation under A2 regardless of whether the correct label eventually follows. "
        "the criteria rung artifact is exactly one criterion for the current thread only \u2014 "
        "not one criterion per thread, not criteria for all threads collected under one label; "
        "exactly one criterion may be written per thread per cycle \u2014 "
        "a second criterion for the same thread requires a split: return to prose, re-emit for the new gap, "
        "emit \u2705 Manifest declared with both gaps, then descend each thread separately; "
        "writing two criteria under one label is a protocol violation; "
        "the criteria rung label is per-thread \u2014 "
        "writing criteria for Thread 2 or any subsequent thread before \u2705 Thread 1 complete is a protocol violation; "
        "batch-collecting criteria for multiple threads under one criteria label bypasses sequential descent "
        "and is a protocol violation; "
        "each thread\u2019s criterion is only valid in the context of that thread\u2019s descent \u2014 "
        "writing criteria for all threads before descending any treats the rung as a planning step, which it is not. "
        # Formal notation rung
        "The formal notation rung separates behavioral specification from explanation \u2014 "
        "formal notation encodes what must be true in a form that is executable or testable; "
        "valid notation forms include type signatures, interfaces, pseudocode, and invariant expressions; "
        "verbatim restatement of the criterion is permitted when the criterion is already a complete behavioral specification; "
        "the test of valid formal notation is that "
        "it cannot be directly compiled or executed without modification; "
        "prohibited: complete function bodies, variable assignments, "
        "constant declarations (const, let, var assignments) regardless of what they assign; "
        "labeling content as pseudocode does not exempt it from the prohibition if it is implementation-shaped. "
        "it must encode all structural constraints the criterion implies \u2014 "
        "natural language may add context but may not substitute for notation; "
        "prose adds context and introduces the specification \u2014 it does not encode the constraints. "
        "the audit section is separate and named and must appear before the completion sentinel \u2014 "
        "the sentinel closes the audit section; it does not constitute it; "
        "emitting it before the audit section inverts causality; "
        "the rung is incomplete until all criteria are encoded. "
        "Natural language may appear as section labels but may not substitute for encoding a constraint in notation \u2014 "
        "if a constraint can be stated in notation, it must be. "
        # EV rung
        "each test function asserts exactly one behavioral property \u2014 one behavioral property per test function; "
        "multiple assertions are permitted only when they jointly constitute a single indivisible check. "
        "before writing the test, check for an existing test file covering the same module \u2014 add there if so. "
        "confirm via tool call that the criteria artifact for this cycle was produced in this cycle's transcript; "
        "if the criteria artifact is identical to a prior cycle\u2019s criteria artifact, "
        "the criterion has not changed \u2014 return to the prose rung and re-emit with an updated gap. "
        "carry-forward format: 'Carry-forward: prior failure [verbatim test name as it appeared in "
        "a \U0001f534 Execution observed sentinel] covers current test [verbatim test name as written in the artifact]'; "
        "modification without carry-forward is a traversal violation. "
        "when the declared intent is to modify a test artifact, the test-under-modification is the implementation artifact "
        "for this cycle and the validation artifact must be a meta-test \u2014 an executable artifact that fails "
        "when the test-under-modification does not exhibit the criterion. "
        "when a test assertion is changed to match implementation output rather than the declared criterion, "
        "this constitutes a criterion change \u2014 return to the prose rung, re-emit with the revised gap, "
        "and descend; a test expectation update made without re-emitting prose is a protocol violation. "
        "before emitting \u2705 Validation artifact V complete, "
        "the artifact content must appear in the current response; "
        "artifact content means each test block (name + assertion body) \u2014 "
        "imports, describe wrappers, and setup blocks are not required; "
        "emitting the sentinel without any test block in the transcript is a protocol violation; "
        "if no P4 EV step (1) pre-existence check tool-call result exists, "
        "\u2705 Validation artifact V complete may not be emitted; "
        "a file-write tool call result showing the artifact was written must appear before V complete \u2014 "
        "artifact content appearing in prose without a file-write tool call does not satisfy this gate; "
        "the validation artifact must reside within the project\u2019s version-controlled file tree; "
        "if the artifact asserts static state, run it before any edit \u2014 "
        "if it passes, the artifact is vacuous and must be rewritten; "
        "if the artifact asserts runtime behavior, perturb the implementation to force a red run \u2014 "
        "if it still passes after perturbation, the test is vacuous and must be rewritten. "
        # VRO rung
        "Before writing the validation run observation rung label, invoke the validation artifact via a test runner; "
        "a harness error (import failure, syntax error, missing file) is not a red run \u2014 "
        "the test must have been loadable, its assertions must have run, and they must have failed; "
        "fix the harness error before treating any run as a red witness. "
        "when VRO exec_observed is a harness error caused by a missing implementation file: "
        "\U0001f534 Gap: and \U0001f7e2 Implementation gate cleared may not be emitted after a harness error; "
        "the only valid next token is the executable implementation rung label; HARD STOP is not valid. "
        "when VRO exec_observed is a harness error caused by a test file error "
        "(syntax error, import of a non-existent component in the test itself): "
        "same block rule applies; the only valid next token is a tool call that repairs the test file at the EV rung \u2014 not HARD STOP. "
        "when VRO exec_observed is a test-interaction failure \u2014 "
        "the tests loaded and ran but could not interact with the component under test "
        "(e.g., pointer-events: none, role not found, element not accessible) \u2014 "
        "\U0001f534 Gap: may not be emitted and \U0001f7e2 Implementation gate cleared is not valid; "
        "the only valid next token is a tool call that repairs the component's accessibility "
        "or the test's interaction strategy at the EV rung; "
        "this is a harness error class, not a behavioral failure. "
        "a green \U0001f534 Execution observed: is only valid as the post-implementation green "
        "if a prior \U0001f534 Execution observed: for the same artifact appeared after the most recent "
        "\U0001f7e2 Implementation gate cleared showing the test logic failing. "
        "At the validation run observation rung, run the validation artifact; "
        "emit \U0001f534 Execution observed: with verbatim output then \U0001f534 Gap: naming the first failure; "
        "stop there \u2014 do not enumerate multiple failures or plan fixes. "
        "re-running VRO without an implementation edit is a protocol violation \u2014 "
        "every re-run of the validation artifact must be preceded by an EI rung edit. "
        "after a red VRO that is not a harness error, after the criterion re-statement, "
        "\U0001f7e2 Implementation gate cleared is the next valid token \u2014 "
        "this shortcut applies only when a red VRO already exists in the current cycle for the current criterion; "
        "a new criterion introduced by HARD STOP has no red VRO yet \u2014 EV and VRO must fire before impl_gate; "
        "skipping EV and VRO for a new criterion introduced by HARD STOP is a protocol violation. "
        "a green exec_observed without a prior red run means the test is vacuous \u2014 "
        "return to the executable validation rung and rewrite the test to fail. "
        "a valid \U0001f534 Gap: at the VRO rung must cite a failing assertion from the exec_observed output. "
        "\U0001f6d1 HARD STOP \u2014 upward return to criteria rung is valid in exactly one case: "
        "the current criterion for this thread is identical to the criterion from the most recent prior cycle for this thread, "
        "confirming the criterion is underspecified (P5 condition); "
        "all other failure classes have defined routes \u2014 "
        "missing implementation file routes to EI directly; "
        "test-interaction failure routes to EV repair; "
        "implementation gap that changes between cycles loops within EI; "
        "spec gap returns to formal notation; "
        "using HARD STOP for any failure class other than criterion underspecification is a protocol violation. "
        "\U0001f6d1 HARD STOP position gate: valid only after a "
        "\U0001f534 Execution observed: and \U0001f534 Gap: have been emitted "
        "at the validation run observation rung in the current cycle \u2014 "
        "emitting it at any other position is a protocol violation; "
        "prose-only exec_observed sentinel does not satisfy this gate \u2014 "
        "the exec_observed block must contain non-empty verbatim tool output in a triple-backtick block; "
        "HARD STOP may not be emitted at the executable validation rung \u2014 "
        "a harness error at EV requires fixing the harness, not an upward return; "
        "when EV shows a harness error that is an import failure, "
        "the repair must re-enter at step (2a) of the current EV cycle \u2014 "
        "a freeform stub write that bypasses the import-check gate is a protocol violation; "
        "the only valid next action when EV shows a harness error is a tool call that fixes the harness; "
        "HARD STOP may not appear in the same response as a harness-error exec_observed at the EV rung. "
        "if the observed gap matches the prior cycle's gap, the edit did not address it \u2014 "
        "return to formal notation before any further edit. "
        "HARD STOP does not restart the session \u2014 \u2705 Ground entered and \u2705 Manifest declared "
        "are not re-emitted; the next token is the criteria rung label for the current thread. "
        "the VRO rung label must appear in the transcript for the current cycle. "
        # EI rung
        "\U0001f7e2 Implementation gate cleared is the first token of the executable implementation rung \u2014 "
        "no tool call, no prose, and no file modification may appear before it in the current response; "
        "the next required action after \U0001f7e2 is a tool call that creates or modifies an implementation file; "
        "the implementation gate does not complete the thread; "
        "\u2705 Thread N complete may not appear until the observed running behavior rung has fired for this thread; "
        "the OBR rung label must appear in the transcript for the current thread's current cycle before \u2705 Thread N complete may be emitted \u2014 "
        "output produced before the OBR rung label may not be reused to satisfy the OBR exec_observed gate; "
        "its absence is a protocol violation, not a voiding condition. "
        "declaring a thread complete by similarity to another thread's failure is not valid \u2014 "
        "each thread requires its own full descent through OBR with a passing run; "
        "similarity does not substitute for a tool-executed result in the current cycle. "
        "none of the following satisfies the OBR gate: passing tests, functionally complete implementation, "
        "prior work stopped at EI, or precedent \u2014 "
        "the gate requires a manual live-process invocation in the current cycle. "
        # OBR rung
        "In-process rendering (renderToStaticMarkup, test-framework render) is acceptable only when no runnable artifact exists. "
        "If no invocable process exists, open a gap cycle to make the artifact directly invocable. "
        "if the \U0001f534 Execution observed: does not directly demonstrate the criterion, "
        "emit \U0001f534 Gap: naming what is undemonstrated and apply the upward-return failure-class rules; "
        "the exec_observed output must show the specific behavior asserted in the criterion \u2014 "
        "server liveness (a 200 OK, a page title, a process start message) does not satisfy this gate "
        "unless the criterion asserts server liveness; "
        "the query must exercise the criterion\u2019s behavior directly, not merely confirm the server is running. "
        "\u2705 Thread N complete is blocked until a live-process tool call result appears "
        "in the current thread\u2019s current cycle \u2014 "
        "a test runner invocation, even in browser mode, does not satisfy this gate; "
        "the test suite run at step 5 presupposes the live-process invocation at step 3 has already produced an exec_observed result; "
        "if no live-process tool call result exists, the only valid next action is to start the process and query it. "
        "A full test suite run result is required after the most recent OBR tool call \u2014 "
        "the only valid next action if no such result exists is the tool call that runs the suite; "
        "every failing test must be explicitly acknowledged in the transcript with a written reason; "
        "acknowledging failures does not permit \u2705 Thread N complete \u2014 "
        "the step-5 run must show zero failures for the criterion declared in this thread "
        "before \u2705 Thread N complete may be emitted; "
        "if the most recent \U0001f534 Execution observed: in the current cycle shows any test failure, "
        "\u2705 Thread N complete is blocked \u2014 "
        "no intervening prose, reasoning, or cross-thread argument lifts this block; "
        "only a subsequent passing test run does; "
        "this block does not apply when the most recent exec_observed is a harness error "
        "(import failure, syntax error, missing file) \u2014 "
        "repair the harness and re-run; the block re-evaluates against the subsequent run. "
        "Once \u2705 Thread N complete is emitted no further output in that cycle is valid. "
        # Rung transitions and protocol flow
        "Before writing the criteria, formal notation, executable validation, executable implementation, "
        "or observed running behavior label, emit \U0001f534 Gap: naming the declared gap \u2014 "
        "what the prior rung\u2019s artifact leaves unresolved; immediately produce the rung artifact \u2014 "
        "only the validation run observation rung stops after naming the gap. "
        "Outputting a rung label is what begins that rung \u2014 it is not a heading or annotation. "
        "I is the declared intent governing the invocation; "
        "each artifact must be self-sufficient to derive the next without consulting I; "
        "before closing a rung artifact, state every open constraint the next rung must resolve. "
        "Advance through every feasible rung without pausing for user confirmation \u2014 "
        "each rung may not be skipped or combined with another, including the observed running behavior rung; "
        "the only protocol-defined stop is at the validation run observation rung after emitting \U0001f534 Gap:; "
        "all other rung transitions are continuous within the same response. "
        "Response length is never a valid reason to stop between rungs \u2014 "
        "if the full descent cannot fit in one response, continue from the current rung "
        "in the next response without re-emitting completed rungs. "
        "The prose rung must be re-emitted at the start of every new cycle \u2014 "
        "the first cycle and any cycle that begins after \u2705 Thread N complete closes the prior one; "
        "a HARD STOP upward return is not a new cycle and does not require prose re-emission \u2014 "
        "the next token after HARD STOP is the criteria rung label for the current thread; "
        "the criterion must be immediately derivable from the prose that opened the current cycle. "
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
        "a final report may not appear unless \u2705 Manifest exhausted immediately precedes it in the transcript. "
        "if no currently-false behavior remains, emit \u2705 Manifest exhausted. "
        "After emitting \u2705 Manifest exhausted, produce a final report containing "
        "prose, criteria, and formal notation for each thread in order \u2014 "
        "no new behavioral claims, no coverage summaries, no suggestions; "
        "then reconcile any documents the implementation affects. "
        )
    ),
}


def build_ground_prompt() -> str:
    """Return the ground method prompt string (ADR-0178: minimal spec is now the only version).

    This is the value injected into AXIS_KEY_TO_VALUE["method"]["ground"].
    """
    return "The response " + GROUND_PARTS_MINIMAL["core"]
