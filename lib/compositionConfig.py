# ADR-0227: Pairwise token compositions — application-time behavioral rules.
#
# PURPOSE: These entries govern how the LLM behaves when tokens are *already co-present*
# in a bar build command. They are injected into the COMPOSITION RULES section of the
# prompt at runtime. They are NOT for discovery (use guidebookConfig.py for that).
#
# Discovery layer (token selection guidance): guidebookConfig.py → `bar guide <token>`
# Application layer (co-presence resolution):  this file → injected into COMPOSITION RULES
#
# Each entry answers: "given these tokens are already selected, how should the LLM
# resolve their interaction?" Entries typically cover:
#   - Precedence (one token takes priority over another)
#   - Sequencing (apply one before the other)
#   - Scope restriction (token A applies everywhere except where token B governs)
#
# Compositions are pairwise — each activates independently for partial combinations.

from typing import Any

COMPOSITIONS: list[dict[str, Any]] = [
    {
        "name": "ground+falsify",
        "tokens": ["ground", "falsify"],
        "prose": "When ground and falsify are both active: the 'Ground properties:' block must appear and reach '§ ground complete' before any falsify artifact. "
        "The property set falsify governs is exactly and only the properties declared in the 'Retained properties:' line immediately preceding '§ ground complete'. "
        "Guard-edit entry point: if the response modifies an observation mechanism — a guard, assertion, test, or gate condition — for a reason not traceable to a property already declared in a 'Retained properties:' line in the transcript, the modification does not stand until the property that mechanism observes is named. "
        "This entry point activates whenever the justification for the edit originates outside the current retained property set — independent review, a failing report, a user comment, or an unexamined intuition all qualify; the trigger is that the edit changes what the mechanism observes and its reason is not already under test, not the source of the reason. "
        "If a 'Retained properties:' line already declares the property that mechanism observes, cite it by its property [N] before the modification tool call; if no such property exists, re-enter Ground's completion procedure to derive it — canonicalization, scope validation, recursive decomposition, completeness, and observational-independence resolution until a new '§ ground complete' fixed point declaring that property is established — before the guard edit is valid. "
        "A modification to an observation mechanism whose target property is neither cited from an existing 'Retained properties:' line nor freshly derived to a new '§ ground complete' does not satisfy this composition. "
        "Coverage gate — coverage against the retained property set. After the token's Gate 1 (minimization) and Gate 2 (observed failure) have run, compare the governed artifact against each property in the 'Retained properties:' line. "
        "First make the assertion-to-property map visible: tag each 'Assertion:' line enumerated in Gate 2 with the retained property [N] it tests, giving 'Assertion [P N.m]: <verbatim assertion text>'. This map must be a bijection between retained properties and assertion groups: every retained property has at least one assertion tagged to it, and every assertion maps to a retained property. An assertion that maps to no retained property is surplus — route it through the 'more' branch below; a retained property with no assertion is a coverage gap — route it through the 'less' branch below. The map is the checkable surface for 'exactly the properties, nothing more or less': read it directly rather than judging coverage in prose. "
        "The Coverage gate checks the artifact against the retained properties in both directions — the artifact must be exactly the properties, nothing more or less. "
        "Adequacy is tested by attempted counterexample construction, not by asserted equivalence, and it is a disagreement between two classifications of the same constructed state — never a claim that 'the guard is inadequate'. For each retained property P (referenced by its 'property [N]' identity from the 'Retained properties:' line) and the assertions tagged to it, the candidate state S is not arbitrary — it must be a distinguishing state derived from the property's own semantics. First identify the semantically relevant distinctions the property makes — a phrase like 'the first occurrence' distinguishes first from later occurrences and requires a state with at least two; 'empty' distinguishes empty from non-empty; a strict versus non-strict bound distinguishes the equality boundary; 'any' versus 'all' distinguishes mixed truth values — deriving each distinction from the property's meaning, not from a fixed catalog of cases. Then construct an admissible candidate state S in which a competing but plausible reading of the property would produce a different expected result than the intended reading, so that S separates them; a witness that collapses the distinction (for 'first occurrence', a state with only one occurrence, where first and last coincide) does not exercise it and is not a distinguishing state. Having constructed such an S, obtain two classifications of S. R_P(S) is P's classification of S — the property-defined status, evaluated against the retained formal property; where P is not itself executable this evaluation is a semantic reading of the formal property over S, and it is an input to the test, not evidence the guard supplies. R_A(S) is the guard's classification of S — the guard-defined status, which must be machine-observed: execute the tagged assertions against S and read their A-fail/A-pass results from the tool-result. The guard's result is the guard's measurement of the property, not the property itself; adequacy tests whether the measurement agrees with the specification. Provenance closure applies here too: the R_A(S) observation and the 'property [N]' the counterexample cites must each quote verbatim the tool-result and the 'Retained properties:' text that establish them — a cited property [N] with no matching entry on the 'Retained properties:' line, or an R_A result not present verbatim in a tool-result, is not evidence. Cross-layer identity foreign key: for a given property [N], the assertion identity used by the adequacy observation must be the same verbatim guard-emitted assertion identity established by that assertion's Failure in the token; an adequacy observation whose assertion identity differs from the identity its token Failure carried does not establish adequacy for that assertion — it binds two facts about different assertions and is rejected. A candidate is relevant only if both classifications can be obtained: if R_P(S) cannot be evaluated against the retained property, or the execution does not produce the guard-defined observation for the tagged assertions, S is an uninterpretable candidate — neither a counterexample nor evidence of adequacy — and must be replaced. Inadequacy exists exactly when R_P(S) and R_A(S) disagree: if R_P(S) is false while every tagged assertion is A-pass, the guards under-govern P — emit 'Adequacy gap: property [N] — <S>' and strengthen the guard, then re-run the token's Gate 1 and Gate 2 for the affected assertions; if R_P(S) is true while any tagged assertion is A-fail, the guards over-govern P — emit 'Adequacy overconstraint: property [N] — <S>' and weaken the guard, then re-run Gate 1. This overconstraint direction is also the control test on a purported A-fail: an A-fail that recurs in a state where R_P(S) is true is not controlled by P — the failure tracks something other than the property (for a symbol-absence 'failure', it tracks the symbol's presence, not P) — so construct such a state and, if the same A-fail is observed while P holds, the A-fail did not witness the property and the tagged assertion must be strengthened until its failure tracks P; the check is always the disagreement R_P(S) != R_A(S), never the reproduction of a particular error mechanism. Verdict-follows-execution governs every construction-conditional adequacy verdict — 'Adequacy gap:', 'Adequacy overconstraint:', and the unrefuted claim alike — each is valid only immediately following the tool-result of the guard execution against S. The adequacy verdict for a property is one of three, and 'unrefuted' is not among them because it silently implies a search that may not have happened: emit 'Adequacy: refuted — property [N]: <blind spot>' when a distinguishing state produced R_P(S) != R_A(S); 'Adequacy: established — property [N]' only when, for every semantically relevant distinction the property makes, a distinguishing state was constructed and executed and the guard tracked P on each; or 'Adequacy: untested — property [N]: no distinguishing state constructed' when no distinguishing state for a relevant distinction was constructed and executed. Untested is never established and never refuted; absence of a counterexample does not imply that a counterexample search occurred, and a bare 'established' with no executed distinguishing-state construction for each identified distinction does not satisfy this gate. Adequacy is execution-dependent — R_A(S) requires executing the guard against the freshly constructed S, which no prior record can supply; when no qualifying execution evidence is available, emit 'Adequacy: untested — execution unavailable' for that property rather than any adequacy verdict, and untested is never unrefuted and never adequate. The whole result is machine-grounded conditional on the semantic interpretation of the retained formal property over the constructed candidate state. "
        "Less: for each retained property, attempt to explain why the artifact does not satisfy it; if such an explanation holds, the property is authoritative and unmet, so strengthen the guard so an assertion covers that property, then re-run the token's Gate 1 and Gate 3 for the affected assertions. "
        "More: if the artifact exhibits behavior that no retained property requires, do not silently remove it — emit 'Audit: implementation surplus — <behavior>' and classify the surplus: if the behavior is required, the property set was incomplete, so re-enter Ground's completion procedure to derive the property governing it; if the behavior is incidental, the guard over-specified, so weaken the guard to match the property exactly and re-run the token's Gate 1 so the artifact is minimized down. "
        "Auto-weakening a surplus behavior without classifying it does not satisfy this composition, because it may silently delete a required behavior. "
        "When tool calls are available, the classification must be backed by an executed discriminator rather than asserted: 'required' is established by a new guard that is executed and observed to fail when the behavior is absent (promoting it to a property forces a Gate 3 witness); 'incidental' is established by executing the weakened guard and observing that removing the behavior leaves the guard's outcome unchanged. A classification emitted from description or analysis alone, without a tool-result block that mechanically produces it, does not satisfy this composition. "
        "Repeat this loop until one full pass produces no guard revision and no artifact change — a pass that changes nothing is the terminal fixed point and witnesses that the artifact matches the retained property set. "
        "The retained property set is frozen for the duration of this loop: the Coverage gate revises guards to cover an already-retained property but never adds a new property. "
        "A behavior that no retained property names is not resolved inside this loop; instead emit 'Audit: implementation gap — <description>' and re-enter Ground's completion procedure to derive the property, completing canonicalization, scope validation, recursive decomposition, completeness, and observational-independence resolution until a new '§ ground complete' fixed point is established. "
        "Each newly emitted valid 'Retained properties:' declaration immediately preceding a new '§ ground complete' supersedes the previous retained-property declaration for all subsequent falsify gates, and the token's Gate 3 must be completed for every property in the resulting retained set not already witnessed against its current canonical definition. "
        "Only when the Coverage gate's loop has reached its no-change fixed point and no 'Audit: implementation gap' remains open may the response emit 'Audit: implementation complete' followed immediately by 'Coverage: complete'. "
        "A 'Coverage: complete' sentinel that is not immediately preceded by 'Audit: implementation complete' does not satisfy this composition.",
    },
    {
        "name": "falsify+atomic",
        "tokens": ["falsify", "atomic"],
        "prose": (
            "falsify + atomic: when a falsification sequence's assertions, perturbations, and "
            "expected discriminating results are already established, the "
            "observe → perturb → observe → restore → observe cycle for a given assertion may be "
            "driven from a single script so all its results return in one execution rather than "
            "one round-trip per step. That runner is ephemeral orchestration over the "
            "already-established guards — it is scratch tooling, not a durable artifact to "
            "retain: the guards it drives are what persist, the runner itself is discarded after "
            "the batched observations are recorded. Each perturb/restore pair still witnesses "
            "its own assertion — the runner does not aggregate the observations, it only "
            "collapses the round-trips — and the resulting records witness the same as any "
            "addressable execution. This is an economy for an already-established sequence, not "
            "a licence to skip constructing the sequence: when the assertions or their "
            "perturbations are not yet established, construct them one observable step at a time "
            "as usual."
        ),
    },
    {
        "name": "falsify+chain",
        "tokens": ["falsify", "chain"],
        "prose": (
            "falsify + chain: the artifact-fire tool result produced by falsify is the chain "
            "predecessor for the implementation step that makes that assertion pass. An "
            "implementation step's correctness criterion is: change the system from the observed "
            "wrong state to the correct state. The wrong state is only defined by observing the "
            "artifact-fire output — without that observation, the correctness criterion is "
            "undefined. Chain requires every step to reproduce its predecessor's actual output "
            "before proceeding. The agent derives that implementation is not merely prohibited "
            "before the artifact fire exists — it is undefined. "
            "Note: classification and derivation steps are not implementation steps and are "
            "not governed by this rule."
        ),
    },
    {
        "name": "skim+gate",
        "tokens": ["skim", "gate"],
        "prose": (
            "skim + gate: gate's hard-blocking precision requirement takes precedence over skim's "
            "brevity constraint at every gate condition. The gate condition itself must be stated "
            "fully — naming the specific string or structural property whose presence constitutes "
            "satisfaction — regardless of skim's light-pass instruction. Skim governs all content "
            "outside the gate conditions; within a gate condition, skim does not apply. A gate "
            "condition expressed as a vague summary rather than a named observable property does "
            "not satisfy gate's requirement even when skim is present."
        ),
    },
    {
        "name": "blind+skim",
        "tokens": ["blind", "skim"],
        "prose": (
            "blind + skim: assumption and constraint reconstruction — which blind requires before "
            "any conclusion that depends on prior context — is compressed to one-line headers "
            "rather than full blocks. Each header names the assumption or constraint explicitly "
            "so the conclusion can be traced to it, but elaboration is suppressed. Conclusions "
            "still name their dependency by reference to the header; a conclusion that omits this "
            "reference does not satisfy blind's requirement regardless of skim's brevity instruction."
        ),
    },
    {
        "name": "calc+chain",
        "tokens": ["calc", "chain"],
        "prose": (
            "calc + chain: each executable step's output must be reproduced verbatim before "
            "the next step may constrain its conclusions. calc requires that conclusions be "
            "constrained by the actual outputs of formal steps; chain requires that each step "
            "reproduce its predecessor's actual output before proceeding. Together: quoting "
            "a calculation result is not sufficient — the exact output of each step must "
            "appear in the response before the reasoning that depends on it."
        ),
    },
    {
        "name": "variants+adversarial",
        "tokens": ["variants", "adversarial"],
        "prose": (
            "variants + adversarial: each variant must include its primary failure mode "
            "co-located within that variant's block — a failure mode appearing in a "
            "separate section rather than inside the variant it governs does not satisfy "
            "this requirement. The failure mode must name the specific flaw type "
            "(edge case, unstated assumption, architectural brittleness, etc.) and at "
            "least one concrete instance of that type found in the variant. A variant "
            "block without a co-located failure mode is incomplete regardless of whether "
            "adversarial's global failure-category requirement is otherwise met."
        ),
    },
    {
        "name": "mint+root",
        "tokens": ["mint", "root"],
        "prose": (
            "mint + root: the generative model mint constructs must itself be root-compliant — "
            "there may be only one canonical generative structure for each domain under analysis. "
            "mint requires that generative assumptions be made explicit and conclusions follow as "
            "direct products; root requires that each proposition have a single authoritative "
            "locus with no unresolved parallel accounts. Together: constructing two independent "
            "generative models for the same phenomenon and deriving from both is a violation — "
            "the generative layer is not exempt from root's single-source requirement. Multiple "
            "structural models must be unified into one, or their dependency relationship must be "
            "made explicit before either is used as a generative basis."
        ),
    },
    {
        "name": "cards+gherkin",
        "tokens": ["cards", "gherkin"],
        "prose": (
            "cards + gherkin: cards form produces a card-deck layout with prose content "
            "per card; gherkin channel mandates Given/When/Then DSL output only. These "
            "are incompatible output structures — the card layout form has no valid "
            "rendering target inside Gherkin syntax. Same mechanism as ghost+svg, "
            "twin+svg, prep+svg: a prose-layout form meets a DSL-only channel. When "
            "cards and gherkin appear together, the card content must appear as "
            "prose blocks before or after the Gherkin scenarios; embedding card prose "
            "inside Gherkin steps does not satisfy cards' layout requirement."
        ),
    },
    {
        "name": "deep+commit",
        "tokens": ["deep", "commit"],
        "prose": (
            "deep + commit: commit form defaults to gist completeness because conventional "
            "commit messages are structurally brief — a subject line and short body. "
            "Explicit deep overrides this default but creates a content-exceeds-format "
            "tension: deep requires addressing every named element at one level of depth, "
            "which a commit message format cannot hold. Resolution: expand beyond "
            "conventional commit format — use a commit message header for the summary, "
            "then append a full structured section below for the deep content. The commit "
            "header still follows conventional format; the appended section satisfies deep. "
            "A commit-only response without the appended section does not satisfy deep."
        ),
    },
    {
        "name": "prep+svg",
        "tokens": ["prep", "svg"],
        "prose": (
            "prep + svg: prep form requires rich prose blocks — hypothesis, method, "
            "expected outcomes, evaluation criteria. svg is markup-only with no prose "
            "slot. The structured write-up prep requires has no valid rendering target "
            "inside svg. Same mechanism as ghost+svg and twin+svg: the form demands "
            "prose structure the channel structurally cannot hold. When prep and svg "
            "appear together, the prep write-up must appear as a prose block before "
            "or after the svg artifact."
        ),
    },
    {
        "name": "ghost+svg",
        "tokens": ["ghost", "svg"],
        "prose": (
            "ghost + svg: ghost produces a step-by-step execution trace in prose — "
            "each step names what was done and what result was produced. svg is a "
            "markup-only channel with no prose slot. The trace narrative ghost requires "
            "has nowhere to render in svg. When ghost and svg appear together, the "
            "ghost trace must appear as a separate prose block before the svg artifact; "
            "embedding trace commentary inside svg markup does not satisfy ghost's "
            "requirement for a readable execution narrative."
        ),
    },
    {
        "name": "twin+svg",
        "tokens": ["twin", "svg"],
        "prose": (
            "twin + svg: twin form produces a two-column parallel prose comparison — "
            "each column runs a distinct analytical lens on the same subject. svg is "
            "markup-only with no prose slot for column content. The prose comparison "
            "twin requires has no valid rendering target inside svg. Same mechanism as "
            "ghost+svg: the form demands prose structure that the channel structurally "
            "cannot hold. When twin and svg appear together, the twin comparison must "
            "appear as a prose block before or after the svg artifact."
        ),
    },
    {
        "name": "probe+falsify",
        "tokens": ["probe", "falsify"],
        "prose": (
            "probe + falsify: falsify requires an implementation artifact to precede it — "
            "the artifact must fire against the absent behavior (FAIL) before any "
            "implementation step. probe produces understanding, not an implementation "
            "artifact. There is no implementation step for falsify to gate before. When "
            "probe and falsify appear together, falsify applies only if the probe output "
            "leads to an implementation step within the same response; if the response "
            "is analysis only, falsify has no target and is silently inapplicable."
        ),
    },
    {
        "name": "pick+indirect",
        "tokens": ["pick", "indirect"],
        "prose": (
            "pick + indirect: pick requires an explicit committed selection — the LLM names "
            "one option and commits to it. indirect withholds direct statement, hinting rather "
            "than declaring. These conflict: a token that selects one option cannot "
            "simultaneously decline to state it. Resolution: pick takes precedence — the "
            "selection must be named explicitly. indirect may govern surrounding framing "
            "(context, caveats, approach) but not the selection itself. A response that "
            "hints at a selection without naming it does not satisfy pick."
        ),
    },
    {
        "name": "pick+cocreate",
        "tokens": ["pick", "cocreate"],
        "prose": (
            "pick + cocreate: cocreate scaffolds an open-ended iterative co-creation "
            "process; pick commits to one final answer. These are in mild tension: the "
            "co-creation form implies ongoing iteration and dialogue, while pick asks for "
            "a committed selection. Resolution: structure the cocreate scaffold toward a "
            "decision point — the collaborative process converges to the pick output rather "
            "than remaining open-ended. The final cocreate turn must name the picked option "
            "explicitly. A cocreate scaffold that never commits to a selection does not "
            "satisfy pick."
        ),
    },
    {
        "name": "depends+atomic",
        "tokens": ["depends", "atomic"],
        "prose": (
            "depends + atomic: atomic makes each step's result independently observable; depends "
            "orders steps by prerequisite. Together they govern what happens when a step's result "
            "does not confirm its intended change. When atomic's step result — read from a "
            "qualifying observation record at an earlier transcript position than any verdict about "
            "it — shows the intended change did not take, the response does not proceed to a further "
            "step on top of that unconfirmed state. It emits 'Known-good: <the prior step's "
            "last-confirmed state, quoted from the observation record that confirmed it>' and "
            "'Blocked: <the unconfirmed result, quoted from the step's observation record>', then "
            "names the prerequisite that result reveals as 'Prerequisite: <the condition the blocked "
            "result entails as absent>' — the prerequisite must be entailed by the quoted blocked "
            "result, not asserted independently. Prerequisite blind-spot: attempt to name a "
            "Prerequisite the quoted Blocked record does not entail as absent; emit 'Prerequisite "
            "unsupported: found — <condition>' or 'Prerequisite unsupported: not found'; if found, "
            "replace Prerequisite with a condition the record entails and repeat this check; "
            "terminate on 'not found'. depends then orders that prerequisite ahead of the original "
            "step: the prerequisite becomes its own atomic step and must reach a confirming "
            "observation record before the original step is re-attempted. Before re-attempting, the "
            "response restores the known-good state and emits 'Restored: <observation record showing "
            "the current state matches the Known-good record>', or 'Restored: unobserved' when no "
            "such record can be produced — 'Restored: unobserved' requires the restoration be "
            "performed and observed and does not satisfy this composition on its own. A further step "
            "emitted while 'Restored: unobserved' stands, or an original step re-attempted before "
            "its 'Prerequisite:' step reaches a confirming record, does not satisfy this composition. "
            "This is a process discipline (order work by prerequisite, revert on resistance), not an "
            "inference form; generalizing the dependency map from observed resistance is inductive — "
            "see the induce and deduce tokens for the inference-form counterparts."
        ),
    },
    {
        "name": "reset+good",
        "tokens": ["reset", "good"],
        "prose": (
            "reset + good: reset clears state and starts fresh, discarding prior context; "
            "good reinforces what is already working, building on existing strengths. These "
            "operate in opposite directions on the same material — you cannot simultaneously "
            "clear and reinforce. Resolution: treat them as sequential rather than "
            "simultaneous — good identifies what to preserve before reset clears everything "
            "else. The response must name what is being preserved (good) before naming what "
            "is being cleared (reset); a response that resets without first identifying "
            "preserved strengths does not satisfy good."
        ),
    },
    {
        "name": "gate+atomic",
        "tokens": ["gate", "atomic"],
        "prose": (
            "gate + atomic: atomic makes each step's result independently observable; gate "
            "hard-blocks a step until a named string appears in a qualifying prior-executed "
            "result. Together they govern the case where a 'Gate condition:' block is followed, "
            "in the same response, by a further governed action — the atomic step after the "
            "gate. In that case, before that further governed action, the response emits a "
            "'Boundary:' line — a line whose first token is the literal 'Boundary:' — naming a "
            "durable, independently-addressable location (an addressable path or identifier) "
            "holding the gate-satisfying result. The 'Boundary:' line is emitted only after a "
            "qualifying prior-executed result — a tool-call result produced by executing a "
            "command, running a test suite, or invoking an endpoint; a file read, write, edit, "
            "or search result does not qualify — confirming the gate-satisfying evidence at "
            "that location appears at an earlier transcript position than the 'Boundary:' line; "
            "this write-confirming result must be a distinct result from the one that satisfied "
            "the gate. The 'Boundary:' line must also appear at a later transcript position than "
            "the 'Gate condition:' block it follows and at an earlier transcript position than "
            "the further governed action. A further governed action preceded by a 'Gate "
            "condition:' block with no intervening 'Boundary:' line, or with a 'Boundary:' line "
            "for which no qualifying write-confirming result appears at an earlier transcript "
            "position, names an intended rather than an accomplished durable boundary and does "
            "not satisfy this composition. Boundary blind-spot: attempt to point the 'Boundary:' "
            "line at a location whose address no later context could resolve, or whose write no "
            "qualifying prior-executed result confirms; emit 'Boundary unresolvable: found — "
            "<the unaddressable or unconfirmed reference>' or 'Boundary unresolvable: not "
            "found'; if found, write the evidence to a resolvable location, produce the "
            "confirming result, and repeat this check; terminate on 'not found'. "
            "Authorization allow-list: a governed action after a 'Gate condition:' block is "
            "permitted only when the response emits an 'Authorized by:' line — a line whose "
            "first token is the literal 'Authorized by:' — naming the qualifying prior-executed "
            "result (by its command, test suite, or endpoint identifier) in which the gate "
            "condition's named string appears verbatim, and that named result appears at an "
            "earlier transcript position than the 'Authorized by:' line, which itself appears at "
            "an earlier transcript position than the governed action. The permitting condition "
            "is this: the result satisfying the gate string already exists in the transcript "
            "before the action is authorized. An action authorized by a condition the same "
            "authorizing instruction has not already shown satisfied by such a prior result — "
            "for example an instruction that licenses the action contingent on evidence it also "
            "undertakes to produce — is not permitted, because no qualifying result precedes its "
            "'Authorized by:' line. License blind-spot: attempt to name an 'Authorized by:' "
            "result for which no qualifying prior-executed result containing the gate string "
            "appears at an earlier transcript position; emit 'License unsupported: found — <the "
            "unbacked authorization>' or 'License unsupported: not found'; if found, the action "
            "is not permitted — produce the qualifying result first, then re-authorize; "
            "terminate on 'not found'. This composition enforces from the transcript only that "
            "the durable boundary was addressed, its write confirmed, and each gated action "
            "authorized by a result that already existed; whether the location's contents remain "
            "correct when a later context reads them, and whether the authority that rendered a "
            "gate verdict is separate from the one that acts on it, are off-transcript claims "
            "this composition does not verify beyond the ordering it enforces. It is distinct "
            "from depends+atomic, which governs reverting when a step's result does not confirm "
            "— here the gate is not assumed satisfied but must be shown satisfied by a prior "
            "result before the action it gates is authorized, and the question is whether that "
            "evidence survives independently of the context that produced it."
        ),
    },
    {
        "name": "browse+pull",
        "tokens": ["browse", "pull"],
        "prose": (
            "browse + pull: pull extracts a subset from source material that is already "
            "present; browse obtains material by driving an external target rather than "
            "operating on given input. When both are active they sequence: browse first "
            "produces the material, then pull extracts its subset from that produced result. "
            "The extracted subset must trace to content browse actually returned in a prior "
            "result, not to assumed or recalled content. A pull whose subset is drawn from "
            "material no prior browse result produced does not satisfy this composition."
        ),
    },
    {
        "name": "paradox+fix",
        "tokens": ["paradox", "fix"],
        "prose": (
            "paradox + fix: fix transforms the presentation of given content while keeping "
            "its intended meaning; paradox holds the subject's unresolved tension without "
            "resolving it. When both are active, the tension present in the source is part "
            "of the meaning fix must preserve. The combined instruction is: change the form "
            "or arrangement of the content so that its unresolved tension is preserved and "
            "made legible in the new form — not smoothed over, reconciled, or explained away "
            "by the reformatting. A reformat that resolves, harmonizes, or hides a tension "
            "the source holds has altered the meaning and does not satisfy fix; a reformat "
            "that adds synthesis or a resolving conclusion does not satisfy paradox. A "
            "response satisfying both keeps the same tension the source carried, now visible "
            "in the transformed presentation."
        ),
    },
    {
        "name": "mu+fix",
        "tokens": ["mu", "fix"],
        "prose": (
            "mu + fix: fix transforms the presentation of given content while keeping its "
            "intended meaning; mu enacts irresolution structurally so the reader cannot "
            "escape it, rather than naming it. When both are active, the combined "
            "instruction is: choose the transformed form itself so that the reader "
            "encountering it cannot settle the source's tension — the structure of the new "
            "presentation withholds resolution rather than a statement about it doing so. "
            "A reformat whose new structure resolves the tension, or whose structure allows "
            "the reader to resolve it, does not satisfy mu; a reformat that merely describes "
            "the tension instead of enacting it structurally satisfies neither mu nor fix's "
            "requirement to preserve the source's meaning in the form."
        ),
    },
    {
        "name": "contextualise+sketch",
        "tokens": ["contextualise", "sketch"],
        "prose": (
            "contextualise + sketch: sketch emits pure diagram source as the complete output "
            "with no surrounding natural language; contextualise enriches the content with the "
            "background, assumptions, constraints, and framing a downstream consumer would need. "
            "Same mechanism as ghost+svg, prep+svg, twin+svg: a prose-bearing form meets a "
            "DSL-only channel that has no slot for prose. Resolution: keep the diagram source "
            "pure, and place contextualise's enrichment in a separate prose block before or "
            "after the diagram artifact — not inside it. Embedding the contextualizing prose as "
            "comments or text nodes within the diagram source does not satisfy contextualise's "
            "requirement for a usable downstream context block and does not satisfy this "
            "composition; a diagram with no adjacent context block does not satisfy "
            "contextualise."
        ),
    },
    {
        "name": "contextualise+svg",
        "tokens": ["contextualise", "svg"],
        "prose": (
            "contextualise + svg: svg emits markup-only output with no prose slot; "
            "contextualise enriches the content with the background, assumptions, constraints, "
            "and framing a downstream consumer would need. Same mechanism as ghost+svg and "
            "twin+svg: a prose-bearing form meets a markup-only channel. Resolution: keep the "
            "svg artifact as pure markup, and place contextualise's enrichment in a separate "
            "prose block before or after the artifact — not inside the markup. Embedding the "
            "contextualizing prose inside the svg does not satisfy contextualise's requirement "
            "for a usable downstream context block and does not satisfy this composition; an "
            "svg with no adjacent context block does not satisfy contextualise."
        ),
    },
    {
        "name": "contextualise+gherkin",
        "tokens": ["contextualise", "gherkin"],
        "prose": (
            "contextualise + gherkin: gherkin emits Given/When/Then scenario syntax with no "
            "slot for explanatory prose; contextualise enriches the content with the "
            "background, assumptions, constraints, and framing a downstream consumer would need. "
            "Same mechanism as contextualise+sketch and contextualise+svg: a prose-bearing form "
            "meets a DSL-only channel. Resolution: keep the Gherkin scenarios pure, and place "
            "contextualise's enrichment in a separate prose block before or after the scenarios "
            "— not inside the steps. Embedding the contextualizing prose inside Given/When/Then "
            "steps does not satisfy contextualise's requirement for a usable downstream context "
            "block and does not satisfy this composition; scenarios with no adjacent context "
            "block do not satisfy contextualise."
        ),
    },
    {
        "name": "contextualise+shellscript",
        "tokens": ["contextualise", "shellscript"],
        "prose": (
            "contextualise + shellscript: shellscript emits an output-only shell format that "
            "cannot accommodate explanatory prose as content; contextualise enriches the "
            "content with the background, assumptions, constraints, and framing a downstream "
            "consumer would need. Same mechanism as contextualise+sketch and contextualise+svg: "
            "a prose-bearing form meets a channel with no prose slot. Resolution: keep the "
            "script executable, and place contextualise's enrichment in a separate prose block "
            "before or after the script — not as inline commentary standing in for the context "
            "block. Reducing contextualise's enrichment to script comments does not satisfy its "
            "requirement for a usable downstream context block and does not satisfy this "
            "composition; a script with no adjacent context block does not satisfy contextualise."
        ),
    },
    {
        "name": "contextualise+codetour",
        "tokens": ["contextualise", "codetour"],
        "prose": (
            "contextualise + codetour: codetour emits a JSON tour structure with no "
            "prose-explanation slot for standalone context; contextualise enriches the content "
            "with the background, assumptions, constraints, and framing a downstream consumer "
            "would need. Same mechanism as contextualise+sketch and contextualise+svg: a "
            "prose-bearing form meets a DSL-only channel. Resolution: keep the CodeTour JSON "
            "valid, and place contextualise's enrichment in a separate prose block before or "
            "after the tour — not squeezed into step descriptions in place of a context block. "
            "Folding contextualise's enrichment into tour step text does not satisfy its "
            "requirement for a usable downstream context block and does not satisfy this "
            "composition; a tour with no adjacent context block does not satisfy contextualise."
        ),
    },
    {
        "name": "browse+fix",
        "tokens": ["browse", "fix"],
        "prose": (
            "browse + fix: fix reformats existing content that is already present; browse "
            "obtains content by driving an external target rather than operating on given "
            "input. When both are active they sequence: browse first produces the content, "
            "then fix reformats that produced content. Same shape as browse+pull. The "
            "reformatted output must trace to content browse actually returned in a prior "
            "result, not to assumed or recalled content. A fix whose input is content no prior "
            "browse result produced does not satisfy this composition."
        ),
    },
    {
        "name": "prep+code",
        "tokens": ["prep", "code"],
        "prose": (
            "prep + code: prep requires four prose sections — hypothesis, method, expected "
            "outcomes, and evaluation criteria; code emits only code or markup as the complete "
            "output, with no prose slot. Same mechanism as prep+svg: the form demands prose "
            "structure the channel structurally cannot hold. Resolution: keep the code artifact "
            "pure, and place the prep write-up in a prose block before or after it. Folding the "
            "four sections into code comments in place of that block does not satisfy prep's "
            "structured write-up requirement, and a code artifact with no adjacent write-up does "
            "not satisfy prep; neither satisfies this composition."
        ),
    },
    {
        "name": "codetour+pick",
        "tokens": ["codetour", "pick"],
        "prose": (
            "codetour + pick: codetour delivers an ordered sequence of navigable steps with "
            "fields appropriate to the task; pick commits to one option among alternatives. "
            "These compose rather than conflict: the tour carries the evidence and its final "
            "step carries the verdict. Resolution — give each candidate its own step, walking "
            "the reader through the code that bears on it, then add a final step whose "
            "description names the chosen option and the reason for choosing it. Same shape as "
            "pick+cocreate, where a step structure converges to a decision point. codetour's "
            "exclusion of surrounding explanation governs prose outside the artifact, not the "
            "description fields inside each step, which is where the rationale belongs. A tour "
            "that walks the candidates but ends without a step naming the selection does not "
            "satisfy pick and does not satisfy this composition."
        ),
    },
    {
        "name": "codetour+sort",
        "tokens": ["codetour", "sort"],
        "prose": (
            "codetour + sort: codetour delivers an ordered sequence of steps; sort arranges items "
            "into categories or an order. The tour's step order carries the sort directly — an "
            "ordering is expressible as a sequence, and a categorization as grouped consecutive "
            "steps. Resolution — order the steps by the sorting scheme, and name that scheme in "
            "the first step's description so the reader can see what the order means; for a "
            "categorization, keep each category's steps consecutive and introduce each group. A "
            "tour whose step order does not follow the sorting scheme, or that never names the "
            "scheme, does not satisfy sort and does not satisfy this composition."
        ),
    },
    {
        "name": "faq+code",
        "tokens": ["faq", "code"],
        "prose": (
            "faq + code: faq organizes content as separated question headings with concise answers beneath each; "
            "code emits only code or markup with no prose slot. The question/answer pairs are content the "
            "artifact cannot carry. Resolution: keep the artifact pure, and place the question/answer pairs in a "
            "separate block before or after it. Folding that content into the artifact — as comments, step text, "
            "or embedded strings — in place of the adjacent block does not satisfy faq, and an artifact with no "
            "adjacent block does not satisfy it either; neither satisfies this composition. "
        ),
    },
    {
        "name": "faq+codetour",
        "tokens": ["faq", "codetour"],
        "prose": (
            "faq + codetour: faq organizes content as separated question headings with concise answers; a "
            "CodeTour is a JSON sequence of navigable steps through existing code, with no slot for standalone "
            "question/answer pairs. Resolution: keep the artifact pure, and place the question/answer pairs in a "
            "separate block before or after it. Folding that content into the artifact — as comments, step text, "
            "or embedded strings — in place of the adjacent block does not satisfy faq, and an artifact with no "
            "adjacent block does not satisfy it either; neither satisfies this composition. "
        ),
    },
    {
        "name": "faq+shellscript",
        "tokens": ["faq", "shellscript"],
        "prose": (
            "faq + shellscript: faq organizes content as separated question headings with concise answers; "
            "shellscript emits an output-only executable script with no prose slot. Resolution: keep the artifact "
            "pure, and place the question/answer pairs in a separate block before or after it. Folding that "
            "content into the artifact — as comments, step text, or embedded strings — in place of the adjacent "
            "block does not satisfy faq, and an artifact with no adjacent block does not satisfy it either; "
            "neither satisfies this composition. "
        ),
    },
    {
        "name": "log+codetour",
        "tokens": ["log", "codetour"],
        "prose": (
            "log + codetour: log reads as dated or time-marked short updates with enough context for later "
            "reference; a CodeTour is a JSON sequence of navigable code steps with no slot for a running log. "
            "Resolution: keep the artifact pure, and place the log entries in a separate block before or after "
            "it. Folding that content into the artifact — as comments, step text, or embedded strings — in place "
            "of the adjacent block does not satisfy log, and an artifact with no adjacent block does not satisfy "
            "it either; neither satisfies this composition. "
        ),
    },
    {
        "name": "spike+codetour",
        "tokens": ["spike", "codetour"],
        "prose": (
            "spike + codetour: spike formats a research item — a problem or decision statement followed by the "
            "key questions to answer, staying on questions rather than implementation; a CodeTour is a JSON "
            "sequence of navigable code steps with no slot for an open research document. Resolution: keep the "
            "artifact pure, and place the spike write-up in a separate block before or after it. Folding that "
            "content into the artifact — as comments, step text, or embedded strings — in place of the adjacent "
            "block does not satisfy spike, and an artifact with no adjacent block does not satisfy it either; "
            "neither satisfies this composition. "
        ),
    },
    {
        "name": "questions+gherkin",
        "tokens": ["questions", "gherkin"],
        "prose": (
            "questions + gherkin: questions presents the answer as a series of probing or clarifying questions; "
            "gherkin emits Given/When/Then scenario syntax, which asserts behavior rather than asking. The token "
            "already adapts to a structured channel when combined with diagram, where its output becomes a "
            "question tree; apply the same principle here. Resolution: keep the artifact pure, and place the "
            "question series in a separate block before or after it. Folding that content into the artifact — as "
            "comments, step text, or embedded strings — in place of the adjacent block does not satisfy "
            "questions, and an artifact with no adjacent block does not satisfy it either; neither satisfies this "
            "composition. "
        ),
    },
    {
        "name": "questions+shellscript",
        "tokens": ["questions", "shellscript"],
        "prose": (
            "questions + shellscript: questions presents the answer as a series of probing or clarifying "
            "questions; shellscript emits an output-only executable script with no prose slot. The token already "
            "adapts to a structured channel when combined with diagram, where its output becomes a question tree; "
            "apply the same principle here. Resolution: keep the artifact pure, and place the question series in "
            "a separate block before or after it. Folding that content into the artifact — as comments, step "
            "text, or embedded strings — in place of the adjacent block does not satisfy questions, and an "
            "artifact with no adjacent block does not satisfy it either; neither satisfies this composition. "
        ),
    },
    {
        "name": "case+gherkin",
        "tokens": ["case", "gherkin"],
        "prose": (
            "case + gherkin: case builds reasoning toward a conclusion — background, evidence, "
            "trade-offs, and alternatives before converging on a recommendation that addresses "
            "objections; gherkin emits Given/When/Then scenario syntax, which asserts behavior "
            "rather than arguing for it. Same mechanism as faq+gherkin-class pairings: a "
            "content-bearing form meets a DSL-only channel. Resolution: keep the scenarios pure, "
            "and place the case in a separate block before or after them, with the recommendation "
            "it converges on stated there. Folding the argument into step text in place of that "
            "block does not satisfy case, and scenarios with no adjacent case do not satisfy it "
            "either; neither satisfies this composition."
        ),
    },
    {
        "name": "case+codetour",
        "tokens": ["case", "codetour"],
        "prose": (
            "case + codetour: case builds reasoning toward a conclusion — background, evidence, "
            "trade-offs, and alternatives before converging on a recommendation; a CodeTour is a "
            "JSON sequence of navigable steps through existing code, with no slot for a standalone "
            "argument. Resolution: keep the tour valid, and place the case in a separate block "
            "before or after it, with the recommendation stated there. Folding the argument into "
            "step descriptions in place of that block does not satisfy case, and a tour with no "
            "adjacent case does not satisfy it either; neither satisfies this composition."
        ),
    },
    {
        "name": "case+shellscript",
        "tokens": ["case", "shellscript"],
        "prose": (
            "case + shellscript: case builds reasoning toward a conclusion — background, evidence, "
            "trade-offs, and alternatives before converging on a recommendation; shellscript emits "
            "an output-only executable script with no prose slot. Resolution: keep the script "
            "executable, and place the case in a separate block before or after it. Reducing the "
            "argument to script comments in place of that block does not satisfy case, and a "
            "script with no adjacent case does not satisfy it either; neither satisfies this "
            "composition."
        ),
    },
]


__all__ = ["COMPOSITIONS"]
