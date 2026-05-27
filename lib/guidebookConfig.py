# ADR-0237: Token Guidebook — Python SSOT for disambiguation guide entries.
#
# Each entry covers one confusion cluster. Entries are referenced by token slug
# and surfaced via `bar guide <token>` (CLI) and the ? panel (SPA).
#
# Format:
#   id: unique slug for this entry
#   title: short human-readable title
#   tokens: list of token slugs this entry covers (guides are reachable from any listed token)
#   body: markdown disambiguation prose

from typing import Any

GUIDEBOOK: list[dict[str, Any]] = [

    # ── Form axis experiment cluster ─────────────────────────────────────────

    {
        "id": "prep-vs-vet",
        "title": "prep vs vet",
        "tokens": ["prep", "vet"],
        "body": (
            "**prep** — structures output as an *experiment design*: hypothesis, method, "
            "expected outcomes, and evaluation criteria. Use before running an experiment, "
            "making a change, or committing to a plan. Output is a write-up that guides "
            "the work ahead.\n\n"
            "**vet** — structures output as a *post-experiment review*: what was observed, "
            "how outcomes compare to expectations, what was learned, and what follows. "
            "Use after an experiment, decision, or implementation — when you have results "
            "to interpret.\n\n"
            "`prep` asks 'what should we expect and why?' before the work; `vet` asks "
            "'what actually happened and what does it mean?' after. They are designed "
            "as a complementary pair: `prep` sets the criteria, `vet` evaluates against them."
        ),
    },
    {
        "id": "prep-vs-plan",
        "title": "prep vs plan",
        "tokens": ["prep"],
        "body": (
            "**prep** — structures output as an *experiment design*: frames the upcoming "
            "work as a hypothesis to test, with explicit success criteria and expected "
            "outcomes. Output is a scientific write-up, not an action sequence.\n\n"
            "**plan** — proposes the *steps to take* to reach a goal. Output is an action "
            "sequence — ordered tasks, milestones, dependencies.\n\n"
            "Use `prep` when the goal is *learning or validation* (you want to know if "
            "something is true). Use `plan` when the goal is *execution* (you want to "
            "know what to do). A plan can follow a prep: `prep` defines the experiment, "
            "`plan` sequences how to run it."
        ),
    },
    {
        "id": "vet-vs-check",
        "title": "vet vs check",
        "tokens": ["vet"],
        "body": (
            "**vet** — a *post-experiment review*: interprets what happened relative to "
            "prior expectations, surfaces what was learned, and proposes what follows. "
            "Output is a reflective synthesis — it requires a hypothesis or plan to "
            "compare against.\n\n"
            "**check** — evaluates a subject against a *specific condition* in the present. "
            "Output is a pass/fail verdict. It does not require prior expectations.\n\n"
            "Use `vet` when you have run something and want to interpret the results "
            "relative to what you expected. Use `check` when you have a named criterion "
            "and want to know whether a subject satisfies it — no prior hypothesis needed."
        ),
    },

    {
        "id": "pick-vs-cocreate",
        "title": "pick vs cocreate",
        "tokens": ["pick", "cocreate"],
        "body": (
            "**pick** — commits to one final answer: the LLM names one option and "
            "declares it the selection. Output is a decisive, stated choice.\n\n"
            "**cocreate** (form) — scaffolds an open-ended, iterative co-creation "
            "process: the response structures itself as collaborative turns converging "
            "toward an artifact.\n\n"
            "Used together, cocreate's scaffold must converge to a decision — the "
            "collaborative process is not open-ended but aimed at the pick output. "
            "The final turn must name the selected option explicitly. A cocreate "
            "scaffold that never commits does not satisfy `pick`."
        ),
    },
    {
        "id": "pick-vs-indirect",
        "title": "pick vs indirect",
        "tokens": ["pick", "indirect"],
        "body": (
            "**pick** — selects one option and names it explicitly. The LLM commits "
            "to a declared choice. Output requires a stated selection.\n\n"
            "**indirect** (form) — withholds direct statement, hinting or scaffolding "
            "toward a conclusion rather than declaring it.\n\n"
            "These conflict: `pick` requires naming the selection; `indirect` forecloses "
            "naming it. `pick` takes precedence — the selection must be stated. `indirect` "
            "may govern surrounding framing (context, caveats, approach narration) but "
            "not the selection itself. A response that only hints at a selection without "
            "naming it does not satisfy `pick`."
        ),
    },
    {
        "id": "reset-vs-good",
        "title": "reset vs good",
        "tokens": ["reset", "good"],
        "body": (
            "**reset** — clears state and starts fresh: discards prior context, "
            "accumulated assumptions, or approach drift. Output starts from a clean slate.\n\n"
            "**good** — reinforces what is already working: names and preserves existing "
            "strengths before making changes.\n\n"
            "These point in opposite directions on the same material — you can't "
            "simultaneously clear and reinforce. Used together, treat them as sequential: "
            "`good` identifies what to preserve *before* `reset` clears everything else. "
            "Name what survives before naming what is discarded."
        ),
    },

    # ── Task axis near-neighbors ──────────────────────────────────────────────

    {
        "id": "probe-vs-check",
        "title": "probe vs check",
        "tokens": ["probe", "check"],
        "body": (
            "**probe** — use when the goal is *open-ended analysis*: surfacing hidden "
            "assumptions, mapping implications, or diagnosing a problem without a "
            "pre-specified criterion. The output is an expanded understanding.\n\n"
            "**check** — use when you have a *specific condition* and want to know "
            "whether the subject satisfies it. The output is a pass/fail verdict.\n\n"
            "Rule of thumb: if you could write the success criterion before reading "
            "the subject, use `check`. If you need to read the subject first to know "
            "what questions to ask, use `probe`."
        ),
    },
    {
        "id": "probe-vs-fix",
        "title": "probe vs fix",
        "tokens": ["fix"],
        "body": (
            "**probe** — analyzes structure, surfaces assumptions, diagnoses a problem. "
            "Output is understanding.\n\n"
            "**fix** — *reformats or restructures existing content* while preserving its "
            "meaning. Output is a transformed artifact.\n\n"
            "Confusion arises in debugging contexts: `probe` is the right token when you "
            "want to *find* the bug; `fix` is the right token when you want to *reformat* "
            "existing content (e.g. convert indentation, restructure a document). "
            "To fix a bug, use `probe` to surface the cause, then `make` to produce the fix."
        ),
    },
    {
        "id": "sim-vs-simulation",
        "title": "sim vs simulation",
        "tokens": ["sim", "simulation"],
        "body": (
            "**sim** — plays out a *specific scenario over time*: narrates what would happen "
            "if a condition were met, tracing the sequence of events. Temporal narration.\n\n"
            "**simulation** — runs a *thought experiment*: varies assumptions, highlights "
            "feedback loops, bottlenecks, and tipping points. Analytical exploration.\n\n"
            "`sim` tells a story ('here is what happens when X'); `simulation` asks structural "
            "questions ('what feedback loops emerge if X'). Use `sim` for concrete scenario "
            "walkthroughs; use `simulation` for system-level what-if analysis."
        ),
    },
    {
        "id": "sim-vs-plan",
        "title": "sim vs plan",
        "tokens": ["plan"],
        "body": (
            "**sim** — narrates what *would happen* if a condition were met. Output is a "
            "projected story of unfolding events.\n\n"
            "**plan** — proposes the *steps to take* to reach a goal. Output is an action "
            "sequence.\n\n"
            "Use `sim` when you want to understand consequences ('what happens if we deploy "
            "this?'). Use `plan` when you want a roadmap ('how do we get from here to there?')."
        ),
    },
    {
        "id": "make-vs-fix",
        "title": "make vs fix",
        "tokens": ["make"],
        "body": (
            "**make** — creates *new content* that did not previously exist.\n\n"
            "**fix** — *reformats or restructures existing content* while preserving meaning.\n\n"
            "If you are writing from scratch, use `make`. If you are transforming something "
            "that already exists (changing format, restructuring, converting), use `fix`."
        ),
    },

    # ── Correctness / rigor cluster ───────────────────────────────────────────

    {
        "id": "correctness-cluster",
        "title": "verify vs falsify vs gate vs ground vs atomic vs witness",
        "tokens": ["verify", "falsify", "gate", "ground", "atomic", "witness"],
        "body": (
            "These tokens all impose correctness discipline but at different levels and mechanisms:\n\n"
            "**verify** — apply *falsification pressure*: for each claim, name the conditions "
            "under which it would be false. Lightweight — one pass over claims.\n\n"
            "**falsify** — before implementing, run the governing artifact against the *absent* "
            "behavior to confirm it detects the absence. Requires a FAIL result in the "
            "transcript before any implementation step.\n\n"
            "**gate** — a *hard-blocking checkpoint*: the next action cannot proceed until a "
            "specific condition is satisfied by a prior tool-executed result in the transcript.\n\n"
            "**ground** — full derivation protocol: derive a governing goal from observed state, "
            "derive behavioral dimensions, build a falsifiable enforcement sequence, close with "
            "a completion check backed by tool-executed results. The heaviest correctness method.\n\n"
            "**atomic** — *one independently observable change per file-modifying tool call*, "
            "with scope and symbol committed before the call and a clean run result after.\n\n"
            "**witness** (topology) — names each assumption before relying on it; externalizes "
            "live reasoning state per segment. Unlike the method tokens, `witness` governs the "
            "*epistemic stance* of the response, not a procedural gate.\n\n"
            "Typical progression: `witness` for all reasoning → `falsify` before each change → "
            "`gate` to block on FAIL results → `atomic` for one change at a time → `ground` "
            "when the full derivation + completion check protocol is required."
        ),
    },

    # ── Structural analysis cluster ───────────────────────────────────────────

    {
        "id": "analysis-vs-systemic",
        "title": "analysis vs systemic",
        "tokens": ["analysis", "systemic"],
        "body": (
            "**analysis** — *decomposes the subject into constituent parts* and examines each "
            "for its role, properties, and interactions. Does not impose an organizing principle "
            "(no hierarchies, no feedback loops). Output: a structured description of parts.\n\n"
            "**systemic** — reasons about the subject as an *interacting whole*: identifies "
            "components, boundaries, flows, feedback loops, and emergent behavior that arise "
            "from interactions rather than parts in isolation. Output: a systems-level account.\n\n"
            "Use `analysis` to understand what something is made of. Use `systemic` to "
            "understand how the parts behave together over time."
        ),
    },
    {
        "id": "analysis-vs-diagnose",
        "title": "analysis vs diagnose",
        "tokens": ["diagnose"],
        "body": (
            "**analysis** — describes and structures the situation without seeking causes. "
            "Neutral decomposition.\n\n"
            "**diagnose** — *seeks likely root causes*: identifies hypotheses whose presence "
            "would produce the observed symptom and whose absence would not, narrowing through "
            "evidence and falsification before proposing fixes.\n\n"
            "Use `analysis` when you want to understand what is happening. Use `diagnose` "
            "when you want to understand *why* it is happening."
        ),
    },
    {
        "id": "thrust-vs-balance",
        "title": "thrust vs balance",
        "tokens": ["thrust", "balance"],
        "body": (
            "**thrust** — *catalogs* competing structural forces or design pressures, making "
            "explicit for each the specific constraint it imposes and the direction it pushes. "
            "Output: a named inventory of forces.\n\n"
            "**balance** — *resolves* competing considerations, weighing them against each "
            "other and producing a synthesis. Output: a resolved position.\n\n"
            "Use `thrust` when you want to surface and name the tensions. Use `balance` "
            "when you want the tensions resolved into a recommendation."
        ),
    },
    {
        "id": "clash-vs-adversarial",
        "title": "clash vs adversarial",
        "tokens": ["clash", "adversarial"],
        "body": (
            "**clash** — *identifies where existing structures, rules, or commitments conflict*: "
            "finds locally valid elements that produce global inconsistency or breakdown.\n\n"
            "**adversarial** — *stress-tests* by enumerating failure categories, then finding "
            "specific instances of each: edge cases, unstated assumptions, counterexamples.\n\n"
            "Use `clash` when the structures already exist and you want to find where they "
            "contradict each other. Use `adversarial` when you want to actively probe for "
            "weaknesses before they are encountered."
        ),
    },
    {
        "id": "grain-vs-robust",
        "title": "grain vs robust",
        "tokens": ["grain", "robust"],
        "body": (
            "**grain** — *finds the latent structural direction*: names where existing structure "
            "already propagates (interfaces, dependencies, data flows) and distinguishes real "
            "optionality from illusory optionality. Use when the question is 'which of these "
            "options is already foreclosed by the system's structure?'\n\n"
            "**robust** — *reasons under deep uncertainty*: explores what holds across a wide "
            "range of possible futures, surfacing strategies that remain viable even when "
            "assumptions are wrong. Use when the future is genuinely uncertain and you need "
            "to stress-test a choice against multiple scenarios."
        ),
    },
    {
        "id": "meld-vs-compare",
        "title": "meld vs compare",
        "tokens": ["meld", "compare"],
        "body": (
            "**meld** — *explores combinations, overlaps, and constraints between elements*: "
            "reasons about what happens when two things interact, balance, or are combined.\n\n"
            "**compare** — *evaluates alternatives against criteria*: produces a structured "
            "side-by-side for the reader to decide.\n\n"
            "Use `meld` when the question is 'how do these things work together?' Use "
            "`compare` when the question is 'which of these should I choose?'"
        ),
    },

    # ── Exploration / decision cluster ────────────────────────────────────────

    {
        "id": "sweep-vs-sense",
        "title": "sweep vs sense",
        "tokens": ["sweep", "sense"],
        "body": (
            "**sweep** — *enumerates the option space without evaluating*: each option named "
            "must differ from the others in at least one structural property. No option is "
            "preferred or dismissed. Use when you want to surface the full space.\n\n"
            "**sense** — *pre-reductive evaluative impression*: a lightweight first pass that "
            "characterizes the subject before analysis begins. Use when you want an initial "
            "read before committing to a method."
        ),
    },
    {
        "id": "converge-vs-pick",
        "title": "converge vs pick vs prioritize vs release vs grain",
        "tokens": ["converge", "pick", "prioritize", "release"],
        "body": (
            "These all move toward a decision but differ in how:\n\n"
            "**converge** — *narrows a set*: drops options with named criteria, carries forward "
            "a smaller set. The LLM does not make a final selection — it narrows.\n\n"
            "**pick** — *selects one*: the LLM makes the choice and names it.\n\n"
            "**prioritize** — *ranks by a named criterion*: orders items without necessarily "
            "dropping any. Output is a ranked list.\n\n"
            "**release** — *de-weights contingent features*: surfaces load-bearing constraints "
            "by removing everything that depends on assumptions. Use to find what is truly "
            "non-negotiable.\n\n"
            "**grain** — *distinguishes real from illusory optionality*: names which options "
            "are already foreclosed by existing structure. See `grain vs robust` guide.\n\n"
            "Typical sequence: `grain` → `converge` → `pick`."
        ),
    },

    # ── Causal / temporal cluster ─────────────────────────────────────────────

    {
        "id": "causal-cluster",
        "title": "effects vs grove vs trace vs systemic vs simulation vs orbit",
        "tokens": ["effects", "grove", "trace", "orbit"],
        "body": (
            "These tokens all involve reasoning about what happens over time, but differently:\n\n"
            "**effects** — traces *second and third-order downstream consequences*: effects "
            "whose causes are themselves named as effects. Chain: cause → effect → effect.\n\n"
            "**grove** — names *accumulation mechanisms*: how an effect compounds through "
            "feedback loops, network effects, or iterative growth.\n\n"
            "**trace** — *narrates sequential progression*: makes the path from input to "
            "outcome explicit through intermediate steps. Use for 'show your work'.\n\n"
            "**systemic** — reasons about the *interacting whole* and its feedback loops. "
            "See `analysis vs systemic` guide.\n\n"
            "**simulation** — runs *thought experiments* projecting evolution over time, "
            "highlighting tipping points and emergent effects. See `sim vs simulation` guide.\n\n"
            "**orbit** — finds *attractor geometry*: the invariant structural form behavior "
            "tends toward across many trajectories, despite sensitive dependence on initial "
            "conditions. Use when the system appears chaotic but may have underlying recurrence."
        ),
    },

    # ── Fault-finding cluster ─────────────────────────────────────────────────

    {
        "id": "fault-finding-cluster",
        "title": "adversarial vs inversion vs fail vs clash vs drift vs hollow",
        "tokens": ["inversion", "fail", "drift", "hollow"],
        "body": (
            "These all answer 'what could go wrong?' but from different angles:\n\n"
            "**adversarial** — enumerates *failure categories*, then finds specific instances. "
            "Proactive stress-testing before problems occur.\n\n"
            "**inversion** — reasons *from catastrophic outcomes back*: starts from a named "
            "failure state and asks what would produce or amplify it.\n\n"
            "**fail** — *names failure modes*: surfaces the ways a design or plan could fail. "
            "More enumeration-focused than inversion.\n\n"
            "**clash** — finds where *existing structures conflict*. See `clash vs adversarial`.\n\n"
            "**drift** — identifies *underenforced conclusions*: where a conclusion is treated "
            "as necessary but is not structurally enforced by the representation.\n\n"
            "**hollow** — finds *structural escape routes in prompts*: clauses that can be "
            "pattern-matched without reasoning, where a non-compliant model could satisfy the "
            "form without satisfying the substance.\n\n"
            "Use `adversarial` for general stress-testing; `inversion` for pre-mortem; "
            "`drift` and `hollow` for prompt/specification auditing."
        ),
    },

    # ── Combination entries ───────────────────────────────────────────────────

    {
        "id": "probe-plus-adversarial",
        "title": "probe + adversarial: TDD / pre-mortem combination",
        "tokens": [],
        "body": (
            "**probe** surfaces hidden assumptions and implications. "
            "**adversarial** then stress-tests the structure those assumptions support.\n\n"
            "Together they form the standard pre-implementation check: "
            "`probe` to understand what you're working with, `adversarial` to find where "
            "it breaks. This is the method-axis equivalent of TDD's red phase.\n\n"
            "Typical use: `bar build probe adversarial` before writing any implementation."
        ),
    },
    {
        "id": "thrust-plus-converge",
        "title": "thrust + converge: design decision sequence",
        "tokens": [],
        "body": (
            "**thrust** catalogs the competing structural forces — what each design constraint "
            "demands and which direction it pushes. "
            "**converge** then narrows from the option space to a smaller set, naming each "
            "dropped option and its exclusion criterion.\n\n"
            "This is the canonical two-step for architectural decisions: surface the forces, "
            "then let them eliminate options. The result is a decision with auditable reasoning.\n\n"
            "Typical use: `bar build show thrust` → read the forces → "
            "`bar build show converge` with the thrust output as subject."
        ),
    },
    {
        "id": "grain-plus-converge",
        "title": "grain + converge: structural decision-making",
        "tokens": [],
        "body": (
            "**grain** finds which options are real vs. illusory given the existing system "
            "structure — names where propagation paths already run and where they don't. "
            "**converge** then eliminates illusory options with structural criteria.\n\n"
            "When `grain` eliminates an option, it does so because the option *crosses* "
            "an existing structural direction — not because it's harder or less appealing. "
            "This makes the elimination auditable.\n\n"
            "Typical use: `bar build show grain converge` for any decision where the "
            "existing system's structure should constrain the option space."
        ),
    },
    {
        "id": "analysis-plus-diagnose",
        "title": "analysis + diagnose: ordered correctly",
        "tokens": [],
        "body": (
            "**analysis** decomposes the subject into its parts without seeking causes. "
            "**diagnose** then seeks root causes from the decomposed structure.\n\n"
            "Order matters: running `diagnose` before `analysis` produces confused output "
            "because diagnose needs the structural map that analysis provides. "
            "Always decompose first, then seek causes.\n\n"
            "Typical use: `bar build show analysis` → read the structure → "
            "`bar build probe diagnose` with the analysis output as subject."
        ),
    },

    # ── Coupling cluster (structural analysis) ───────────────────────────────

    {
        "id": "coupling-cluster",
        "title": "coupling cluster: snag → mesh → melody → shear/sever → seep",
        "tokens": ["snag", "mesh", "melody", "shear", "sever", "seep"],
        "body": (
            "The coupling tokens form a sequential flow — find it, describe it, rate it, fix it, audit it:\n\n"
            "**snag** — *find* the seams: where are coupling boundaries? Output is a map of locations.\n\n"
            "**mesh** — *trace* propagation: once you know a seam, what travels across it and how does change ripple? Requires `snag` first.\n\n"
            "**melody** — *rate* the seam across visibility, scope, and volatility. Answers 'how bad is this?' not 'how does it work?'\n\n"
            "**shear** — *procedural fix*: step-by-step plan to pull the coupled domains apart. Use when you need to navigate the separation.\n\n"
            "**sever** — *architectural fix*: introduce a boundary so all interaction must go through explicit interfaces. Use when you want enforcement.\n\n"
            "**seep** — *post-fix audit*: did the boundary hold? Where is influence leaking back through side channels?\n\n"
            "Typical flow: `snag` → `mesh` → `melody` → `shear` or `sever` → `seep`"
        ),
    },

    {
        "id": "snag-vs-mesh",
        "title": "snag vs mesh",
        "tokens": ["snag", "mesh"],
        "body": (
            "These are sequential, not alternative:\n\n"
            "**snag** comes first — find where the coupling seams are. Output is a map of coupling locations.\n\n"
            "**mesh** comes second — once you know where the seams are, describe what travels across each one "
            "and how change propagates.\n\n"
            "You cannot meaningfully `mesh` without first knowing what seam you're tracing. "
            "`snag` answers 'where?' and `mesh` answers 'what moves across it and how far?'"
        ),
    },

    {
        "id": "shear-vs-sever",
        "title": "shear vs sever",
        "tokens": ["shear", "sever"],
        "body": (
            "Both produce decoupling, but at different levels:\n\n"
            "**shear** — procedural: give me a step-by-step plan to pull these two things apart. "
            "Output is an ordered sequence of actions. Use when you need to navigate the separation practically.\n\n"
            "**sever** — architectural: introduce a structural boundary so that direct dependency is impossible "
            "and all interaction goes through a defined interface. Output is a design decision. "
            "Use when you want to make the separation permanent and enforced.\n\n"
            "`shear` might produce work that implements `sever`. "
            "For a migration plan, use `shear`. For an architectural constraint, use `sever`."
        ),
    },

    {
        "id": "gap-vs-amorph-vs-drift",
        "title": "gap vs amorph vs drift",
        "tokens": ["gap", "amorph"],
        "body": (
            "All three are about implicit vs. explicit, but at different levels:\n\n"
            "**gap** — something is *assumed as stated*: a specific rule, role, or relationship "
            "that everyone treats as explicit but isn't written down. "
            "Produces coordination failures when two parties discover they assumed different things.\n\n"
            "**amorph** — an entire *region* has no stable explicit structure — behavior is emergent, "
            "ownership is unclear, there's nothing to violate because nothing was stated. "
            "Broader than `gap` (which requires something to be implicitly assumed).\n\n"
            "**drift** — conclusions are *not derivable* from the representation — "
            "the structure is loose enough that the same premises yield different outputs on re-reasoning. "
            "The problem is at the conclusion level, not the premise level.\n\n"
            "Resolving question:\n"
            "- Is there something specific being assumed as fact? → `gap`\n"
            "- Can the same premises produce different conclusions? → `drift`\n"
            "- Is there just nothing explicit here? → `amorph`"
        ),
    },

    {
        "id": "reify-vs-crystal",
        "title": "reify vs crystal",
        "tokens": ["reify", "crystal"],
        "body": (
            "**reify** — targeted: you've identified one implicit pattern and want to give it "
            "a name and formal status. Output is a single named rule or constraint.\n\n"
            "**crystal** — systemic: the whole system relies on convention and tacit knowledge, "
            "and you want to eliminate that dependency across the board. "
            "Output is a restructured architecture where behavior follows from explicit structure.\n\n"
            "`reify` is often a step *within* a `crystal`-level effort. "
            "Use `reify` when you know which pattern to formalize; "
            "use `crystal` when you want to reshape the architecture toward structural determination broadly."
        ),
    },

    # ── Process tokens (ground / gate / chain / atomic) ───────────────────────

    {
        "id": "gate-vs-verify",
        "title": "gate vs verify",
        "tokens": ["gate", "verify"],
        "body": (
            "**gate** — temporal ordering: an evaluation artifact must *precede* the implementation artifact. "
            "Self-certification is impossible — the criteria exist before the work being evaluated. "
            "Use for TDD, planning rubrics, decision criteria.\n\n"
            "**verify** — falsification pressure: claims must be anchored to external constraints "
            "and define their own negative space (what would make them false). "
            "Timing is not the point — a `verify` constraint can apply to any claim at any time.\n\n"
            "Use `gate` when the failure mode is *post-hoc rationalization* (criteria shaped by outcome). "
            "Use `verify` when the failure mode is *unanchored assertion* (claims without external grounding)."
        ),
    },

    {
        "id": "chain-vs-trace",
        "title": "chain vs trace",
        "tokens": ["chain", "trace"],
        "body": (
            "**chain** — derivation: each step must *cite its predecessor's actual content*. "
            "Any reader should be able to reconstruct why each step follows from the previous one. "
            "The concern is logical continuity — conclusions must follow from premises.\n\n"
            "**trace** — narration: describes a sequential progression of states or events. "
            "Narration doesn't require derivation — you can trace a process without proving each step follows.\n\n"
            "Use `chain` when hidden jumps in reasoning are the risk. "
            "Use `trace` when you want a clear sequential account of what happened."
        ),
    },

    {
        "id": "ground-vs-gate-chain-atomic",
        "title": "ground vs gate / falsify / atomic",
        "tokens": ["ground", "gate", "falsify", "atomic"],
        "body": (
            "**ground** asks the model to *derive* what constraints this task needs — "
            "it's a meta-token that produces enforcement structure appropriate to the specific task. "
            "Use when the task is open-ended or novel enough that you can't anticipate the failure shape.\n\n"
            "**gate**, **falsify**, **atomic** *specify* constraints directly:\n"
            "- `gate`: evaluation artifact precedes implementation\n"
            "- `falsify`: the artifact must have fired against the absent behavior (FAIL before edit)\n"
            "- `atomic`: one independently observable change per step\n\n"
            "The combination `witness ground gate falsify atomic` is the active TDD cluster — "
            "`ground` makes the model internalize the tokens rather than passively acknowledge them, "
            "`witness` externalizes reasoning transitions, and `falsify` ensures tests detect absence.\n\n"
            "Use `ground` alone for open-ended research or planning. "
            "Use specific tokens when you already know the shape of the task and its failure modes."
        ),
    },
]
