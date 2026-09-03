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
            "its 'Prerequisite:' step reaches a confirming record, does not satisfy this composition."
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
]


__all__ = ["COMPOSITIONS"]
