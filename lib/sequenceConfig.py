# ADR-0225: Named Workflow Sequences — Python SSOT.
#
# Each sequence is a named, directed multi-step workflow pattern. Sequences encode
# the claim that step N's output makes step N+1 more effective than running N+1 cold.
# This is distinct from cross_axis_composition natural pairings, which encode
# compatibility without direction.
#
# Discovery protocol: see ADR-0225 §"Sequence discovery via shuffle".
# Promotion requires: chain test across ≥2 subjects, ordering rationale documented.

from typing import Any

SEQUENCES: dict[str, dict[str, Any]] = {
    "debug-cycle": {
        "description": "Surface root causes, fix them, then verify the fix holds.",
        "example": "A production service is returning 500s intermittently and the cause is unknown.",
        "heuristics": ["investigate then fix", "debug and verify", "find and fix", "root cause then repair", "diagnose fix verify", "something is broken fix it", "find the bug fix it check it"],
        "mode": "linear",
        "steps": [
            {
                "token": "task:probe",
                "role": "root cause investigation",
                "prompt_hint": "Use this step to surface hidden assumptions and possible causes before writing any fix.",
                "requires_user_input": True,  # user must attempt fix before verification
            },
            {
                "token": "task:fix",
                "role": "repair",
                "prompt_hint": "Use this step to implement the targeted fix once the root cause is confirmed.",
            },
            {
                "token": "task:check",
                "role": "verification",
                "prompt_hint": "Use this step to verify the fix holds and no regressions were introduced.",
            },
        ],
    },
    "experiment-cycle": {
        "description": "Frame a hypothesis before running an experiment, then review evidence afterward.",
        "example": "Testing whether adding a cache layer reduces p95 latency below 200ms.",
        "heuristics": ["run an experiment", "test a hypothesis", "scientific method", "hypothesis and evidence", "frame then test", "design an experiment", "validate with data"],
        "mode": "cycle",
        "stop_when": "The hypothesis has been confirmed or falsified — further iterations would not change the conclusion.",
        "steps": [
            {
                "token": "make form:prep verify",
                "role": "pre-experiment framing",
                "prompt_hint": "Use this step to state the hypothesis and success criteria before running the experiment.",
            },
            {
                "type": "action",
                "role": "experiment execution",
                "prompt_hint": "Run the experiment defined in the prior step. Collect results before proceeding to vet.",
                "requires_user_input": True,  # user must run the experiment before vet
            },
            {
                "token": "check form:vet audit",
                "role": "post-experiment review",
                "prompt_hint": "Use this step to evaluate the evidence against the original hypothesis.",
            },
        ],
    },
    "extract-and-package": {
        "description": "Extract a relevant subset, then package it for downstream use.",
        "example": "Pull the authentication flow from a large codebase and package it as context for a new engineer.",
        "heuristics": ["extract and package", "pull out and wrap", "extract relevant parts", "package for downstream", "extract context", "isolate and document"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "method:pull",
                "role": "extraction",
                "prompt_hint": "Use this step to identify and extract only the relevant material from the subject.",
            },
            {
                "token": "method:contextualise",
                "role": "packaging",
                "prompt_hint": "Use this step to wrap the extracted material with enough context for a downstream reader or LLM.",
            },
        ],
    },
    "gather-and-synthesize": {
        "description": "Frame what to gather, collect it in the real world, then synthesize findings into conclusions.",
        "example": "Understanding why engineers on a team are reluctant to write tests.",
        "heuristics": ["gather and synthesize", "collect and summarize", "research and conclude", "gather evidence then synthesize", "interview then analyze", "collect findings"],
        "mode": "linear",
        "steps": [
            {
                "token": "task:probe",
                "role": "gathering frame",
                "prompt_hint": "Use this step to produce interview questions, a research plan, or observation vectors the user can go execute.",
                "requires_user_input": True,  # user must gather before synthesis
            },
            {
                "token": "task:show",
                "role": "synthesis",
                "prompt_hint": "Use this step to extract patterns and generalize conclusions from the gathered findings.",
            },
        ],
    },
    "check-and-rewrite": {
        "description": "Evaluate an artifact against criteria, then rewrite it so the gaps are closed.",
        "example": "Reviewing a technical design doc and rewriting the sections that don't hold up.",
        "heuristics": ["check then rewrite", "evaluate and revise", "review then fix", "find gaps and close them", "critique then improve", "audit and rewrite"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "task:check",
                "role": "gap evaluation",
                "prompt_hint": "Use this step to evaluate the subject against criteria and surface specific gaps.",
            },
            {
                "token": "task:fix",
                "role": "form revision",
                "prompt_hint": "Use this step to rewrite the artifact so that the gaps identified in the evaluation are closed — change presentation or structure, not meaning.",
            },
        ],
    },
    "make-and-review": {
        "description": "Produce an artifact, then review it critically before treating it as done.",
        "example": "Drafting an ADR and reviewing it for gaps before publishing.",
        "heuristics": ["make then review", "draft and critique", "produce then evaluate", "write then check", "create and review", "build and vet"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "task:make",
                "role": "artifact production",
                "prompt_hint": "Use this step to produce the artifact — document, plan, design, or code.",
            },
            {
                "token": "check form:vet audit",
                "role": "critical review",
                "prompt_hint": "Use this step to review the artifact: what was produced, how it compares to intent, what is missing or weak.",
            },
        ],
    },
    "probe-and-plan": {
        "description": "Diagnose the structure and hidden assumptions of a situation, then derive a targeted action plan.",
        "example": "Figuring out why a team is slow to ship, then planning what to change.",
        "heuristics": ["diagnose then plan", "understand then act", "investigate then plan", "surface assumptions then plan", "why then what", "root cause then roadmap"],
        "mode": "linear",
        "steps": [
            {
                "token": "task:probe",
                "role": "structural diagnosis",
                "prompt_hint": "Use this step to surface hidden assumptions, root causes, and structural factors before planning.",
                "requires_user_input": True,
            },
            {
                "token": "task:plan",
                "role": "targeted action plan",
                "prompt_hint": "Use this step to produce a plan that directly addresses the findings from diagnosis.",
            },
        ],
    },
    "plan-and-retrospect": {
        "description": "Derive an action plan, implement it in the real world, then retrospectively review what worked.",
        "example": "Improving a team's code review process over two iterations.",
        "heuristics": ["plan then retrospect", "act and reflect", "implement and review", "try then learn", "plan execute review", "iterative improvement"],
        "mode": "cycle",
        "stop_when": "The process has stabilized — the retrospective finds no new gaps worth addressing in another cycle.",
        "steps": [
            {
                "token": "task:plan",
                "role": "action planning",
                "prompt_hint": "Use this step to produce concrete steps the user can go implement.",
                "requires_user_input": True,  # user must implement before retrospective
            },
            {
                "token": "check form:vet audit",
                "role": "retrospective review",
                "prompt_hint": "Use this step to evaluate what worked, what didn't, and what to adjust in the next cycle.",
            },
        ],
    },
    "scenario-to-plan": {
        "description": "Simulate a scenario, then derive the action plan it implies.",
        "example": "Planning a migration from a monolith to microservices.",
        "heuristics": ["simulate then plan", "what if then what now", "scenario planning", "model the future then plan", "anticipate then act"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "method:sim",
                "role": "scenario simulation",
                "prompt_hint": "Use this step to simulate the scenario and observe what it implies.",
            },
            {
                "token": "method:plan",
                "role": "action planning",
                "prompt_hint": "Use this step to convert the simulation's implications into a concrete action plan.",
            },
        ],
    },
    "simulate-and-make": {
        "description": "Simulate the consequences of a scenario, then produce the artifact the simulation implies is needed.",
        "example": "Simulating a security breach to determine what runbook needs to be written.",
        "heuristics": ["simulate then build", "what happens then what to make", "anticipate then produce", "simulate consequences then act"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "method:sim",
                "role": "consequence simulation",
                "prompt_hint": "Use this step to simulate the scenario and surface what it implies is missing or needed.",
            },
            {
                "token": "task:make",
                "role": "artifact production",
                "prompt_hint": "Use this step to produce the artifact the simulation revealed is needed.",
            },
        ],
    },
    "frame-eval": {
        "description": "Enumerate independent evaluation frames, execute each in isolation, then converge on a recommendation.",
        "example": "Evaluating a proposed API design from the perspectives of a security engineer, a frontend consumer, and a platform operator — each independently, with no shared priors.",
        "heuristics": ["evaluate independently", "multiple independent perspectives", "parallel evaluation", "isolated ideation", "spin up subagents", "evaluate from each angle separately", "no shared context between evaluators", "independent assessments then merge"],
        "mode": "linear",
        "steps": [
            {
                "token": "make method:prism",
                "role": "frame enumeration",
                "prompt_hint": "Enumerate independent evaluation frames that differ structurally. A frame name contains no verb and makes no causal claim. Each frame names a structural angle and the type of evidence or perspective it brings — no backtick-wrapped text, file paths, function names, or test names in frame descriptions; those belong to the dispatched agent, not this step. Do not apply any frame yet — enumeration is the only output of this step.",
            },
            {
                "type": "dispatch",
                "role": "parallel frame evaluation",
                "fan_out": "enumerate",
                "join": "all",
                "isolation": True,
                "during_dispatch": "show form:quiz",
                "prompt_hint": "Each agent receives only the subject and its assigned frame description as full context — no shared history, no cross-frame information. Return findings in a labeled block.",
            },
            {
                "token": "task:show",
                "role": "independent results collection",
                "prompt_hint": "Use this step to present the results returned from each isolated subagent evaluation — one labeled block per frame, preserving the original framing without interpretation. Do not synthesize yet.",
            },
            {
                "token": "pick method:converge",
                "role": "synthesis",
                "prompt_hint": "Use this step to narrow from the independent frame results to a recommendation, naming what each frame contributed and what was excluded.",
            },
            {
                "token": "show form:quiz",
                "role": "knowledge transfer",
                "optional": True,
                "prompt_hint": "Quiz the user on the key findings, decisions, and tradeoffs from this run — questions before answers so the user must engage before seeing the answers. Default: run the quiz. Skip only if the content is trivial or the user explicitly declines when asked.",
            },
        ],
    },
    "frame-synthesis": {
        "description": "Enumerate interpretation frames, read and summarize from each frame in parallel, then converge on a multi-perspective synthesis.",
        "example": "Reviewing a proposed API design from a security frame, a usability frame, and a performance frame — each agent reads the same material and returns a framed summary, then the results are synthesized.",
        "heuristics": ["read from multiple angles", "summarize from different perspectives", "parallel frame reading", "multi-stakeholder review", "lens-based analysis", "interpret from each angle", "no experimentation needed"],
        "mode": "linear",
        "steps": [
            {
                "token": "make method:prism",
                "role": "frame enumeration",
                "prompt_hint": "Enumerate the named interpretation frames as a governing artifact. A frame is an interpretive lens (e.g. security, usability, performance, compliance) — not a task to perform. A frame name contains no verb and makes no causal claim. Each frame must yield a distinct reading of the same material. Name the lens only — no backtick-wrapped text, file paths, function names, or test names in frame descriptions; those belong to the dispatched agent, not this step. Enumeration is the only output of this step.",
            },
            {
                "type": "dispatch",
                "role": "parallel frame reading",
                "fan_out": "enumerate",
                "join": "all",
                "isolation": True,
                "during_dispatch": "show form:quiz",
                "prompt_hint": "Each agent receives only the subject and its assigned frame. First, read the files or content named in the subject. Then run bar build using the frame as the interpretive lens. Return a labeled summary: what this frame reveals, what it foregrounds, and what it sets aside.",
            },
            {
                "token": "probe method:converge",
                "role": "cross-frame synthesis",
                "prompt_hint": "Before running bar build: reproduce each ## Derivation block from the join result verbatim. An evaluator determines compliance by counting ## Derivation headings in the join result and confirming the same count appears in the output before the bar build call — a count mismatch does not satisfy this gate. Then run bar build and use this step to synthesize across frame summaries: what each frame revealed, where frames agree or diverge, and what the combined reading supports as a conclusion or recommendation.",
            },
            {
                "token": "show form:quiz",
                "role": "knowledge transfer",
                "optional": True,
                "prompt_hint": "Quiz the user on the key findings, decisions, and tradeoffs from this run — questions before answers so the user must engage before seeing the answers. Default: run the quiz. Skip only if the content is trivial or the user explicitly declines when asked.",
            },
        ],
    },
    "frame-orbit": {
        "description": "Enumerate independent structural frames, trace behavior from each frame's vantage point, then identify invariant attractor geometry across all trajectories.",
        "example": "Exploring failure modes in a distributed payment service — each frame traces data flow from a different entry point (API gateway, queue consumer, database writer), then orbit identifies the structural pattern that recurs across all trajectories despite different starting conditions.",
        "heuristics": ["strange attractor", "what keeps recurring", "find the invariant", "what pattern holds across different entry points", "attractor geometry", "trace from multiple angles", "what's invariant despite varied starting points", "chaotic but patterned", "what structure persists across frames", "trace from multiple entry points", "what pattern emerges across starting points", "invariant across starting conditions"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "make method:prism",
                "role": "frame enumeration",
                "prompt_hint": "Enumerate independent structural frames that differ in starting conditions — each names a distinct entry point or vantage point into the system and the class of behavior observable from there. A frame name contains no verb and makes no causal claim. Frames must have genuinely different named starting conditions so that a claimed attractor can be shown to hold across them — no backtick-wrapped text, file paths, function names, or test names in frame descriptions; those belong to the dispatched agent, not this step. Enumeration is the only output of this step.",
            },
            {
                "type": "dispatch",
                "role": "parallel frame tracing",
                "fan_out": "enumerate",
                "join": "all",
                "isolation": True,
                "prompt_hint": "Each agent receives only the subject and its assigned frame. Trace the control or data flow from this frame's named entry point — narrate each intermediate step and structural change until the flow terminates, loops, or reaches a boundary. Return a labeled trajectory block naming: frame entry point, sequence of steps traversed, terminal state or loop condition, and structural anomalies observed.",
                "inner": {
                    "mode": "autonomous",
                    "steps": [
                        {
                            "token": "show method:trace",
                            "role": "trajectory narration",
                            "prompt_hint": "Narrate the sequential control or data progression from this frame's entry point. Make each intermediate step and structural change explicit. Name the terminal state, loop condition, or boundary reached.",
                        },
                    ],
                },
            },
            {
                "token": "show method:orbit",
                "role": "attractor identification",
                "prompt_hint": "Apply orbit across all trajectory blocks: the frame entry points are the varied initial conditions. Identify the invariant structural form that all trajectories tend toward — the attractor geometry that persists despite different starting conditions. A claimed attractor must name at least two trajectories with different entry points that both exhibit it. Name any trajectories that do not converge to the attractor and what they reveal about the attractor's boundary.",
            },
        ],
    },
    "frame-explore": {
        "description": "Enumerate independent frames for a problem, run an experiment cycle within each frame until a goal is reached, then converge on findings across frames.",
        "example": "Exploring whether a proposed API simplification holds up — framed from security, usability, and performance angles — each angle running hypothesis/evidence cycles until the goal condition is satisfied.",
        "heuristics": ["explore from multiple angles", "parallel frame exploration", "hypothesis cycles per frame", "experiment across frames", "multi-frame investigation", "test each angle independently", "explore then converge"],
        "mode": "linear",
        "stop_when": "Each frame's experiment cycle has reached the goal condition stated in the original subject.",
        "steps": [
            {
                "token": "make method:prism",
                "role": "frame enumeration",
                "prompt_hint": "Enumerate independent frames that differ structurally. A frame name contains no verb and makes no causal claim. Each frame names a structural angle and what the live system would show from that vantage point that would confirm or refute the goal condition — observable runtime behavior is what the live system does when viewed from this angle, not which commands to run or which files to read; commands and investigation methods are the agent's job during the cycle, not the frame definition's job. Each frame description must name a class of output whose instances cannot exist in the repository at rest — produced only by invoking the system, not readable from source files. Before naming a signal class: (1) state the root criterion; (2) enumerate paths that could nominally satisfy without governing — naming a code artifact with runtime language (type definitions, mapping tables, switch branches, schema files, function signatures), or naming a conditional prediction (would show, would appear, could be observed as) — and name the literal string closing each path; (3) proceed only when no open path remains. A valid signal class is one of: stdout lines, stderr lines, log entries, test result records, application trace. Any claimed class not in this list must demonstrate it cannot exist in the repository at rest. No backtick-wrapped text, file paths, function names, or test names in frame descriptions; those belong to the dispatched agent, not this step. Also state the goal condition from the subject as a coverage criterion under the heading `Goal condition:` — a coverage criterion names an enumerable set of cases (a plural noun phrase naming multiple items to be checked) and names what evidence for each case would look like. A conditional statement ('if X then Y') is not a valid coverage criterion. This `Goal condition:` block becomes the stop_when for each frame's experiment cycle. Only enumerate frames whose experiments are fully agent-executable via tool-executed commands, API calls, or test runs that produce new output — frames that require only static reading or human data-gathering do not belong in this sequence.",
            },
            {
                "type": "dispatch",
                "role": "parallel frame experiment cycles",
                "fan_out": "enumerate",
                "join": "all",
                "isolation": True,
                "during_dispatch": "show form:quiz",
                "prompt_hint": "Each agent receives only the subject, its assigned frame description, and the goal condition. Execute the inner sequence until stop_when is met. Return findings in a labeled block with the number of cycles run.",
                "inner": {
                    "mode": "cycle",
                    "stop_when": "The vet output for this cycle contains the literal string 'Goal condition: met' — a vet output that does not contain this exact string does not satisfy stop_when and a new cycle must begin.",
                    "steps": [
                        {
                            "token": "make form:prep verify",
                            "role": "experiment framing",
                            "prompt_hint": "Frame the hypothesis for this cycle: what would be true if the goal condition is met from this frame's angle, what evidence would confirm or refute it, and name what to run (command, API call, or test) to produce that evidence.",
                        },
                        {
                            "token": "probe survive ghost",
                            "role": "experiment execution",
                            "prompt_hint": "Before running any command: identify every factual claim about the subject's current state that this hypothesis depends on (e.g., 'fixture X has property Y', 'file Z contains value W'). For each claim, run a Bash command whose output would differ if the claim were false — a claim not verified by such a command is not a valid precondition and must not be used as the basis for a conclusion. This step is complete only when the transcript contains at least one Bash tool call producing output that could not exist in the repository at rest — one of: stdout lines, stderr lines, log entries, test result records, application trace. A Bash call using cat, head, tail, sed, awk, or equivalent file-reading operations does not satisfy this step regardless of the tool type used.",
                        },
                        {
                            "token": "check form:vet audit adversarial",
                            "role": "evidence evaluation",
                            "prompt_hint": "Before evaluating evidence: identify the tool call type the probe step used to produce it — a Bash tool call executing a command (live execution) satisfies this step; a Read tool call or a Bash call using cat, head, tail, or equivalent (file read) does not. If the probe step used only file reads, the evidence is invalid — reject it and require a live invocation before continuing. Otherwise: evaluate the live output against the hypothesis. End with exactly one of: 'Goal condition: met' (if the goal is fully satisfied from this frame's evidence) or 'Goal condition: unmet — [one sentence naming what further cycles must produce]'.",
                        },
                    ],
                },
            },
            {
                "token": "task:show",
                "role": "per-frame findings collection",
                "prompt_hint": "Use this step to present the findings returned from each frame agent — one labeled block per frame, preserving the original framing and cycle count. Do not synthesize yet.",
            },
            {
                "token": "probe method:converge",
                "role": "cross-frame synthesis",
                "prompt_hint": "Before running bar build: reproduce each ## Derivation block from the join result verbatim. An evaluator determines compliance by counting ## Derivation headings in the join result and confirming the same count appears in the output before the bar build call — a count mismatch does not satisfy this gate. Then run bar build and use this step to synthesize across frames: what each frame's experiment cycles revealed, where frames agree or diverge, and what the combined evidence supports as a conclusion.",
            },
            {
                "token": "show form:quiz",
                "role": "knowledge transfer",
                "optional": True,
                "prompt_hint": "Quiz the user on the key findings, decisions, and tradeoffs from this run — questions before answers so the user must engage before seeing the answers. Default: run the quiz. Skip only if the content is trivial or the user explicitly declines when asked.",
            },
        ],
    },
    "frame-debug": {
        "description": "Partition a problem into independent investigation frames, assign one agent per frame to cycle through hypotheses until the root cause is understood, then converge on the first confirmed explanation.",
        "example": "A service is returning intermittent 500s — partition into frames (connection layer, query layer, config layer), each agent generates and cycles through hypotheses for its frame until the root cause is identified.",
        "heuristics": ["parallel debugging", "parallel root cause analysis", "frame-per-area debugging", "independent investigation frames", "divide and diagnose", "parallel hypothesis testing"],
        "mode": "linear",
        "steps": [
            {
                "token": "make method:prism",
                "role": "frame enumeration",
                "prompt_hint": "Partition into independent investigation frames — each names a system layer or component (e.g. 'connection layer', 'query layer') that can contain multiple hypotheses. A frame name contains no verb and makes no causal claim. A frame description names a structural area. Each frame description must name a class of output whose instances cannot exist in the repository at rest — produced only by invoking the system, not readable from source files. Before naming a signal class: (1) state the root criterion; (2) enumerate paths that could nominally satisfy without governing — naming a code artifact with runtime language (type definitions, mapping tables, switch branches, schema files, function signatures), or naming a conditional prediction (would show, would appear, could be observed as) — and name the literal string closing each path; (3) proceed only when no open path remains. A valid signal class is one of: stdout lines, stderr lines, log entries, test result records, application trace. Any claimed class not in this list must demonstrate it cannot exist in the repository at rest. No backtick-wrapped text, file paths, function names, or test names in frame descriptions; those belong to the dispatched agent, not this step. Do not generate hypotheses yet — enumeration is the only output of this step.",
            },
            {
                "type": "dispatch",
                "role": "parallel frame investigation",
                "fan_out": "enumerate",
                "join": "first",
                "isolation": True,
                "during_dispatch": "show form:quiz",
                "prompt_hint": "Each agent receives only the subject and its assigned frame. For each hypothesis: (1) run `bar build make form:prep` and execute the TASK from its output; (2) run the experiment; (3) run `bar build check form:vet` and execute the TASK from its output. A vet step that rejects the hypothesis requires a new `bar build make form:prep` before the cycle may continue. Return a labeled block stating: frame investigated, hypotheses tried, root cause confirmed or ruled out, and evidence gathered.",
                "inner": {
                    "mode": "cycle",
                    "stop_when": "The vet output for this cycle contains the literal string 'Root cause: confirmed' — a vet output that does not contain this exact string does not satisfy stop_when and a new cycle must begin.",
                    "steps": [
                        {
                            "token": "make form:prep verify",
                            "role": "hypothesis framing",
                            "prompt_hint": "For this frame, identify the next untested hypothesis: what specific cause within this frame would explain the problem? State what would be true if this hypothesis is correct, what evidence would confirm or reject it, and name what to run (command, test, or script) to produce that evidence.",
                        },
                        {
                            "token": "probe survive ghost",
                            "role": "hypothesis investigation",
                            "prompt_hint": "Before running any command: identify every factual claim about the subject's current state that this hypothesis depends on (e.g., 'fixture X has property Y', 'file Z contains value W'). For each claim, run a Bash command whose output would differ if the claim were false — a claim not verified by such a command is not a valid precondition and must not be used as the basis for a conclusion. This step is complete only when the transcript contains at least one Bash tool call producing output that could not exist in the repository at rest — one of: stdout lines, stderr lines, log entries, test result records, application trace. A Bash call using cat, head, tail, sed, awk, or equivalent file-reading operations does not satisfy this step regardless of the tool type used.",
                        },
                        {
                            "token": "check form:vet audit adversarial",
                            "role": "evidence evaluation",
                            "prompt_hint": "Before evaluating evidence: identify the tool call type the probe step used to produce it — a Bash tool call executing a command (live execution) satisfies this step; a Read tool call or a Bash call using cat, head, tail, or equivalent (file read) does not. If the probe step used only file reads, the evidence is invalid — reject it and require a live invocation. Otherwise: evaluate the live Bash output against the hypothesis. If rejected, state why and name the next hypothesis to investigate — a vet rejection is complete only when followed by a new bar build make form:prep verify for the next hypothesis; a vet rejection with no subsequent prep step does not satisfy this requirement. End with exactly one of: 'Root cause: confirmed' (if the root cause is identified with sufficient evidence to act) or 'Root cause: unconfirmed — [one sentence naming what further cycles must produce]'.",
                        },
                    ],
                },
            },
            {
                "token": "pick method:converge",
                "role": "resolution explanation",
                "prompt_hint": "Before running bar build: reproduce each ## Derivation block from the join result verbatim. An evaluator determines compliance by counting ## Derivation headings in the join result and confirming the same count appears in the output before the bar build call — a count mismatch does not satisfy this gate. Then run bar build and use this step to explain the winning fix: what hypothesis was confirmed, what the fix was, what evidence verified it, and why the other hypotheses were not the cause (if known).",
            },
            {
                "token": "show form:quiz",
                "role": "knowledge transfer",
                "optional": True,
                "prompt_hint": "Quiz the user on the key findings, decisions, and tradeoffs from this run — questions before answers so the user must engage before seeing the answers. Default: run the quiz. Skip only if the content is trivial or the user explicitly declines when asked.",
            },
        ],
    },
    "frame-work": {
        "description": "Decompose a task into independent work frames, implement each in isolation using craft discipline with live coordination, then adversarially stress-test the merged result.",
        "example": "Building three independent features in parallel — each agent claims its scope in a shared coordination store, implements with full TDD discipline, and the merged result is stress-tested before converging.",
        "heuristics": ["parallel implementation", "parallel craft", "independent work streams", "parallel TDD", "coordinated parallel work", "implement in parallel then merge", "multi-agent coding"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "make method:prism",
                "role": "frame enumeration and coordination setup",
                "prompt_hint": "Enumerate the independent work frames as a governing artifact. Each frame names a distinct, non-overlapping scope area — no backtick-wrapped text, file paths, function names, or test names in frame descriptions; those belong to the dispatched agent, not this step. Also establish the coordination store: either use nn (if available) with a shared tag, or create a temp JSON file at a deterministic path. Output: (1) named frames with scope, (2) store mechanism and path/identifier, (3) coordination protocol — what each agent must read before starting and write when claiming scope or completing work. The store path/mechanism must appear explicitly in this output so it can be passed to every dispatch agent.",
            },
            {
                "type": "dispatch",
                "role": "parallel frame implementation",
                "fan_out": "enumerate",
                "join": "all",
                "isolation": True,
                "during_dispatch": "show form:quiz",
                "prompt_hint": "Each agent receives its assigned frame, the store path/mechanism, and the coordination protocol from step 1. Execute the inner sequence. The store is a live coordination channel — agents must read it before claiming scope and may read it during work to detect conflicts.",
                "inner": {
                    "mode": "autonomous",
                    "steps": [
                        {
                            "type": "action",
                            "role": "scope claim",
                            "prompt_hint": "Read the coordination store. Check for existing claims that overlap with your frame's scope. Write your frame name and the specific files/symbols you intend to modify as a claim. If overlap exists with another agent's claim, narrow your scope before proceeding and update your claim accordingly. Also write your ground derivation to the store: governing goal, behavioral dimensions, and enforcement sequence — this is required so the adversarial step can validate your work against your stated intent.",
                        },
                        {
                            "token": "make witness ground gate falsify atomic",
                            "role": "craft implementation",
                            "prompt_hint": "Implement your frame's scope using craft discipline (witness → ground → gate → falsify → atomic). Each change must be independently verifiable. On completion, update your claim in the coordination store with the artifacts produced and tests passing.",
                        },
                    ],
                },
            },
            {
                "token": "task:check adversarial perturb falsify",
                "role": "stress-test",
                "prompt_hint": "First, read derivations from the coordination store before proceeding — each frame agent wrote its governing goal, behavioral dimensions, and enforcement sequence there. Use these to validate the merged work against stated intent: check that each artifact covers its declared behavioral dimensions, and that no dimension is present in a derivation but absent from the tests. Then name every category of failure risk in the merged work (adversarial: integration gaps, assumption conflicts, coverage holes, derivation/implementation mismatches). Then introduce controlled faults — remove a function, break a dependency, corrupt a test input — and verify the test suite fires on each fault (perturb). A fault that does not produce a test failure is a governance gap requiring escalation.",
            },
            {
                "token": "pick method:converge",
                "role": "synthesis",
                "prompt_hint": "Summarize what was built across all frames, which falsify checks fired during stress-testing, any gaps that require follow-up, and the overall readiness of the merged work.",
            },
            {
                "token": "show form:quiz",
                "role": "knowledge transfer",
                "optional": True,
                "prompt_hint": "Quiz the user on the key findings, decisions, and tradeoffs from this run — questions before answers so the user must engage before seeing the answers. Default: run the quiz. Skip only if the content is trivial or the user explicitly declines when asked.",
            },
        ],
    },
    "simulate-and-review": {
        "description": "Simulate a scenario before executing it, then review actual outcomes against the simulation.",
        "example": "Migrating the auth service as a pilot for a broader microservices migration.",
        "heuristics": ["simulate then execute", "predict then review", "anticipate then evaluate", "pre-mortem then retrospective", "model then compare"],
        "mode": "linear",
        "steps": [
            {
                "token": "method:sim",
                "role": "pre-execution simulation",
                "prompt_hint": "Use this step to anticipate risks and surface hidden dependencies before the user executes.",
                "requires_user_input": True,  # user must execute before review
            },
            {
                "token": "task:check",
                "role": "outcome review",
                "prompt_hint": "Use this step to compare what actually happened against the simulation's predictions.",
            },
        ],
    },
    "assay-cycle": {
        "description": "Enumerate behavioral frames of a prompt or instruction, run a hollow-audit cycle within each frame to find structural escape routes, then converge on a ranked eval suite.",
        "example": "Auditing a dispatch protocol instruction — framing behavioral dimensions (parallel spawning, join semantics, --subject chaining) and cycling through each to surface all hollow clauses and generate a falsifiable test case per escape route.",
        "heuristics": ["write evals for this", "generate eval cases", "evaluate this prompt", "behavioral coverage", "what evals should I write", "test this prompt", "prompt audit", "generate test cases for this instruction", "eval suite", "how do I know this prompt works", "audit this instruction for compliance theater"],
        "mode": "autonomous",
        "stop_when": "Each behavioral frame has been fully audited and has at least one falsifiable, addressable test case.",
        "steps": [
            {
                "token": "make method:prism",
                "role": "behavioral frame enumeration",
                "prompt_hint": "Enumerate the independent behavioral dimensions of the prompt or instruction — each frame names one distinct behavior the instruction is trying to enforce (e.g. 'parallel spawning', 'join:first race semantics', '--subject chaining'). Each frame description names the behavior and the structural property in a compliant transcript that would confirm or refute it. Do not generate test cases yet — enumeration is the only output of this step.",
            },
            {
                "type": "dispatch",
                "role": "parallel frame hollow audits",
                "fan_out": "enumerate",
                "join": "all",
                "isolation": True,
                "prompt_hint": "Each agent receives only the assigned frame and the original prompt text. Run the hollow audit cycle for the assigned frame until all structural escape routes have been identified and each has a corresponding addressable test case. Return a labeled block per frame: escape routes found, test cases written, and a pass/fail verdict on each clause.",
                "inner": {
                    "mode": "cycle",
                    "stop_when": "No further structural escape routes exist in this frame — every clause either names an addressable string/structural property or has been rewritten to do so, and a falsifiable test case exists for each escape route found.",
                    "steps": [
                        {
                            "token": "make method:hollow form:test",
                            "role": "escape route identification and test case generation",
                            "prompt_hint": "Apply the hollow root criterion to the next unaudited clause in this frame: does the clause name, within its own text, the specific string or structural property that would be present in a compliant transcript and absent in a non-compliant one? If not, identify the escape route and draft a falsifiable test case that exercises it — the test case must name the specific string or property an evaluator checks.",
                        },
                        {
                            "token": "check method:hollow",
                            "role": "test case addressability verification",
                            "prompt_hint": "Verify the test case drafted in the previous step is itself hollow-compliant: does the eval gate name a specific string or structural property an evaluator can check without semantic inference? A test case whose gate requires semantic interpretation is itself hollow and must be rewritten before this cycle may close.",
                        },
                    ],
                },
            },
            {
                "token": "probe method:converge completeness:triage",
                "role": "ranked eval suite",
                "prompt_hint": "Synthesize the escape routes and test cases from all frames into a ranked eval suite. Order by consequence × uncertainty — high-stakes behavioral gaps first. For each eval case: name the frame, the escape route, the specific string the gate checks, and the pass/fail criterion. Omit low-stakes gaps where the consequence of missing the behavior is negligible.",
            },
        ],
    },
    "token-rewrite": {
        "description": "Audit a token definition for structural addressability gaps, derive a new root-criterion definition, verify behavioral compliance across diverse subjects in parallel, then implement with falsifiable tests.",
        "example": "Rewriting the quiz token definition — characterizing why each clause was encoded the way it was, auditing for hollow clauses where cognitive acts replace structural artifacts, drafting a new definition with a self-applicable derivation instruction, verifying parallel haiku agents perform the enumeration step before any content, then implementing in axisConfig.py with tests that FAIL against the old definition.",
        "heuristics": [
            "rewrite this token",
            "fix this token definition",
            "this token definition is too long",
            "hollow audit this token",
            "token definition has escape routes",
            "procedural token needs rewriting",
            "simplify this token definition",
            "token definition is a clause list",
            "token definition grew by patching",
        ],
        "mode": "autonomous",
        "steps": [
            {
                "token": "show mean abduce",
                "role": "root criterion characterization",
                "prompt_hint": "Generate competing hypotheses for why each structural decision in the token definition was encoded the way it was — each hypothesis names the specific evidence it explains that the alternatives do not. Identify the minimal root criterion: the single generative assumption from which all current clauses derive. Name which clauses are derivable from that criterion and which require explicit encoding to close escape routes.",
            },
            {
                "token": "show mean mint gap hollow",
                "role": "assumption derivation and addressability audit",
                "prompt_hint": "Produce a rewritten definition that an agent cannot nominally satisfy.",
            },
            {
                "token": "make",
                "role": "new definition drafting",
                "prompt_hint": "Write the new definition starting with 'The response'. Encode only the root criterion and a derivation instruction. The derivation instruction must embed sufficient hollow logic for self-application: the model names the root criterion, enumerates every path a transcript could satisfy the criterion without actually governing it, names the literal string in the transcript that closes each path, and proceeds only when no open path remains. Each added clause must close a named gap from the audit step — name the gap before adding the clause. The definition may not be longer than the original unless each added word closes a named gap.",
            },
            {
                "token": "make method:prism",
                "role": "test subject enumeration",
                "prompt_hint": "Enumerate exactly 3 diverse test subjects for the new token definition — choose subjects from different domains so that any domain-specific assumption baked into the definition would surface. Each subject is one sentence naming what the response should cover. The subjects must differ structurally, not just topically: one concrete procedural subject, one abstract conceptual subject, one interpersonal or social subject.",
            },
            {
                "type": "dispatch",
                "role": "parallel behavioral verification",
                "fan_out": "enumerate",
                "join": "all",
                "isolation": True,
                "prompt_hint": "Each agent receives the new token definition and one test subject. Apply the definition to the subject exactly as written — do not interpret or adjust. Return a labeled block containing: (1) whether the derivation phase appeared before any content (quote the first derivation line verbatim), (2) whether each named structural artifact from the definition appeared in the correct position (name the literal string and its position), (3) a pass or fail verdict with the specific string evidence for each requirement. A pass verdict requires every named structural artifact to be present and correctly positioned.",
            },
            {
                "token": "pick method:converge",
                "role": "verification synthesis",
                "prompt_hint": "Synthesize the pass/fail verdicts from all agents. If any agent returned a fail verdict: name the specific structural artifact that was absent or mispositioned, and halt — the definition must be revised before proceeding to implementation. Do not proceed to the next step until all agents returned pass. If all passed: confirm with the specific string evidence from each agent and proceed.",
            },
            {
                "token": "make witness ground gate falsify atomic",
                "role": "implementation with falsifiable tests",
                "prompt_hint": "Implement the new definition in the appropriate config file. Before any file-modifying call: write tests asserting the key literal strings from the definition (root criterion phrase, derivation instruction phrase, structural artifact names). Each test must FAIL against the old definition before the edit and PASS after. One file-modifying call per independently testable change.",
            },
        ],
    },
    "contradiction-scan": {
        "description": "Decompose a subject into structural parts, surface where those parts create irresolvable tensions, then recommend which tension to address first.",
        "example": "Reviewing a service architecture where the ownership model requires each team to own its data store but the reporting requirements demand cross-store joins — decompose the structural concerns, surface the irresolvable tension between ownership isolation and query access, then recommend the first tension to address.",
        "heuristics": [
            "find the contradiction in this design",
            "what's fighting each other structurally",
            "structural tensions in this code",
            "what can't both be true here",
            "irresolvable design conflict",
            "surface the structural contradiction",
        ],
        "mode": "linear",
        "steps": [
            {
                "token": "show method:split method:clash",
                "role": "structural decomposition and conflict identification",
                "prompt_hint": "Decompose the subject into its structural parts (modules, interfaces, invariants, lifecycle, ownership boundaries). For each part, name its structural commitment — the constraint it places on the rest of the system. Then identify where two or more parts have commitments that are locally valid but globally inconsistent: name both sides of each conflict and the condition under which each side breaks the other.",
            },
            {
                "token": "show method:mu method:operations",
                "role": "irresolution surface and tradeoff structure",
                "prompt_hint": "For each conflict identified in the prior step: enact the irresolution structurally so the reader cannot reason past it (mu) — present both claims from the subject's own text such that no amount of thinking harder resolves the tension. Then name the objective being optimized, the constraints that bound it, and the tradeoffs that must be navigated (operations) — making the structural tension explicit so decisions can be evaluated against it.",
            },
            {
                "token": "pick",
                "role": "resolution recommendation",
                "requires_user_input": True,
                "prompt_hint": "Given the visible tensions, select which contradiction to address first. Name the tension chosen, why it has the highest leverage or lowest cost to resolve, and what the first concrete action is. If the user wants to explore a different tension, restart from this step.",
            },
        ],
    },
}


def validate_sequences(sequences: dict[str, Any], known_tokens: set[str]) -> list[str]:
    """Return a list of validation errors. Empty list means valid.

    Checks:
    - Each sequence has description (str) and steps (list of ≥2).
    - Each step has token (str) and role (str).
    - Each step token references a known axis:slug.
    """
    errors: list[str] = []
    for name, seq in sequences.items():
        if not isinstance(seq.get("description"), str) or not seq["description"]:
            errors.append(f"{name}: missing or empty description")
        steps = seq.get("steps", [])
        if not isinstance(steps, list) or len(steps) < 2:
            errors.append(f"{name}: steps must be a list of ≥2 entries")
            continue
        for i, step in enumerate(steps):
            if not isinstance(step.get("role"), str) or not step["role"]:
                errors.append(f"{name} step {i}: missing role")
            step_type = step.get("type", "prompt")
            if step_type == "dispatch":
                if "token" in step:
                    errors.append(f"{name} step {i}: dispatch step must not have a token field")
                if not step.get("fan_out"):
                    errors.append(f"{name} step {i}: dispatch step missing fan_out")
                if not step.get("join"):
                    errors.append(f"{name} step {i}: dispatch step missing join")
            elif step_type == "action":
                if "token" in step:
                    errors.append(f"{name} step {i}: action step must not have a token field")
            else:
                if not isinstance(step.get("token"), str) or not step["token"]:
                    errors.append(f"{name} step {i}: missing token")
                elif known_tokens and step["token"] not in known_tokens:
                    errors.append(f"{name} step {i}: unknown token {step['token']!r}")
    return errors


__all__ = ["SEQUENCES", "validate_sequences"]
