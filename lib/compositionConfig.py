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
        "Guard-edit entry point: if the response modifies an observation mechanism — a guard, assertion, test, or gate condition — for a reason not traceable to a property already declared in a 'Retained properties:' line in the transcript, the modification does not stand until the property that mechanism observes is named. "
        "This entry point activates whenever the justification for the edit originates outside the current retained property set — independent review, a failing report, a user comment, or an unexamined intuition all qualify; the trigger is that the edit changes what the mechanism observes and its reason is not already under test, not the source of the reason. "
        "If a 'Retained properties:' line already declares the property that mechanism observes, cite it by its property [N] before the modification tool call. "
        "If no such property exists in the transcript, re-enter Ground's completion procedure to derive it — completing canonicalization, scope validation, recursive decomposition, completeness, and observational-independence resolution until a new '§ ground complete' fixed point declaring that property is established — before the guard edit is valid. "
        "A modification to an observation mechanism whose target property is neither cited from an existing 'Retained properties:' line nor freshly derived to a new '§ ground complete' does not satisfy this composition. "
        "The property list for falsify's per-property cycle is exactly and only the properties declared in the 'Retained properties:' line immediately preceding '§ ground complete', iterated in the order they appear in that declaration. "
        "Properties appearing earlier in the Ground properties block but absent from the 'Retained properties:' declaration are not governed by falsify. "
        "Every 'Observing: property [N]' line must cite a property [N] declared in that 'Retained properties:' line — "
        "a falsify artifact whose preceding 'Observing:' line cites a property not present in the 'Retained properties:' declaration does not satisfy this composition. "
        "Every property [N] in the final retained property set must complete the full falsify six-step cycle — Observing:, guard establishment (step 2), Quoted test:, Test blind-spot:, Failure:/Unobservable:, Quoted implementation:, and Implementation overreach: not found — "
        "before the Coverage: sentinel is emitted; a retained property that has not received 'Implementation overreach: not found' before Coverage: is ungoverned and does not satisfy this composition. "
        "After every retained property has emitted 'Implementation overreach: not found', perform an implementation audit before emitting 'Coverage: complete'. "
        "Enumerate the observable partitions of the governed artifact — distinct execution paths, call sites, externally visible interfaces, state transitions, outputs, consumers, and configuration variants. "
        "For each partition, determine whether at least one retained property governs its externally observable behavior. "
        "If one does not, emit 'Audit: implementation gap — <description>'; derive one or more new candidate properties governing that partition and re-enter Ground's completion procedure for the affected retained-property set. "
        "Complete canonicalization, scope validation, recursive decomposition, completeness, and observational-independence resolution until a new '§ ground complete' fixed point is established. "
        "Each newly emitted valid 'Retained properties:' declaration immediately preceding a new '§ ground complete' supersedes the previous retained-property declaration for all subsequent falsify cycles. "
        "The falsify cycle must then be completed for every property in the resulting final retained set that has not already completed that cycle against its current canonical definition; "
        "if Ground removes, merges, replaces, or changes the canonical definition of a previously governed property, the prior falsify result does not govern the resulting property; "
        "if the guard or observation mechanism for an existing property is affected by the new retained set, that property must repeat steps (2) through (6); "
        "if only the quoted implementation is affected, that property need only repeat steps (5) and (6). "
        "After all properties in the resulting final retained set have completed the falsify cycle, repeat the implementation audit. "
        "Only when no ungoverned partition remains may the response emit 'Audit: implementation complete' followed immediately by 'Coverage: complete'. "
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
