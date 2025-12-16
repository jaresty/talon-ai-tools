# GPT and LLM Interaction

Query language models with voice commands. Helpful to automatically generate text, fix errors from dictation automatically, and generally speed up your Talon workflow.

## SSOT regeneration

- Run `make axis-regenerate-all` to refresh axis config/catalog snapshots, README axis lines/cheatsheet, and static prompt docs/README sections into `tmp/` for review; the helper also validates the catalog for drift.
- `make axis-regenerate` is the manual variant; it now runs catalog validation after generating assets so failures are caught immediately.
- Both commands fail fast when catalog validation detects drift; fix the catalog/list/static prompt data before applying refreshed docs.
- Axis/static prompt `.talon-list` files are catalog-driven and no longer tracked; regenerate them into `tmp/` before applying updates.
- For list-only refresh, `make talon-lists` is available as an optional helper.
- To spot drift without regenerating, use `make talon-lists-check` to validate list outputs against the catalog.
- For catalog-only validation (skip list file rendering), pass `--skip-list-files` to `scripts/tools/axis-catalog-validate.py`.
- To force list checks even when skipping by default, add `--no-skip-list-files` to include talon-list validation.
- When enforcing list checks, pass `--lists-dir GPT/lists` (or your lists directory) so the validator can render `.talon-list` outputs.
- Example enforced run: `python3 scripts/tools/axis-catalog-validate.py --lists-dir /path/to/lists --no-skip-list-files`.
- Regenerate list files before enforced checks via `python3 scripts/tools/generate_talon_lists.py` (or `make talon-lists`) so the validator can diff outputs.
- Compare `tmp/readme-axis-readme.md` and `tmp/static-prompt-readme.md` before updating tracked README sections when shipping catalog changes.

## Help

## Static prompt catalog snapshots
## Static prompt catalog details


Note: Some behaviours (for example, diagrams, Presenterm decks, ADRs, shell scripts, debugging, Slack/Jira formatting, taxonomy-style outputs) now live only as form/channel/method axis values rather than static prompts; see ADR 012/013 and the README cheat sheet for axis-based recipes.

- infer: I'm not telling you what to do. Infer the task.
- describe: Just describe this objectively.
- undefined: List undefined terms only.
- who: Explain who.
- what: Explain what.
- when: Explain when.
- where: Explain where.
- why: Explain why.
- how: Explain how.
- assumption: Identify and explain the assumptions behind this.
- objectivity: Assess objectivity with examples.
- knowledge: Identify relevant academic or industry fields of knowledge and explain why each applies and what perspective it offers.
- taste: Evaluate the taste of the subject by analysing harmony, proportion, restraint, authenticity, and cultural/historical appropriateness, explaining strengths, weaknesses, and contextual fit.
- tao: Classify the subject through Taoist philosophy—relate it to Dao, De, Yin/Yang, Wu Wei, Ziran, Pu, Qi, and Li; identify which apply and why.
- product: Frame this through a product lens. (defaults: completeness=gist, scope=focus, method=steps, form=bullets)
- metrics: List metrics that result in these outcomes with concrete examples. (defaults: completeness=gist, scope=focus, method=steps, form=bullets)
- operations: Infer an appropriate Operations Research or management science concept to apply. (defaults: completeness=gist, scope=focus, method=rigor)
- jobs: Identify the key Jobs To Be Done, desired outcomes, and forces shaping them. (defaults: completeness=gist, scope=focus, method=analysis, form=bullets)
- value: Describe the user/customer value and impact in a concise value narrative. (defaults: completeness=gist, scope=focus, method=analysis, form=bullets)
- pain: List pain points and obstacles with brief prioritisation or severity. (defaults: completeness=gist, scope=focus, method=filter, form=bullets)
- done: Draft a clear Definition of Done / acceptance criteria as a checklist. (defaults: completeness=full, scope=actions, method=structure, form=checklist)
- team: Map the team/roles/responsibilities and handoffs needed for the work. (defaults: completeness=gist, scope=system, method=mapping, form=table)
- challenge: Challenge this with questions so we can make it better.
- critique: This looks bad. What is wrong with it?
- retro: Help me introspect or reflect on this.
- easier: This is too much work; propose something I can accomplish in a smaller timescale.
- true: Assess whether this is true, based on the available information.
- relevant: Identify what is relevant here. (defaults: completeness=gist, scope=focus, method=filter, form=bullets)
- misunderstood: Identify what is misunderstood in this situation. (defaults: completeness=gist, scope=focus, method=filter, form=bullets)
- risky: Highlight what is risky and why. (defaults: completeness=gist, scope=focus, method=filter, form=bullets)
- split: Separate topics into clear sections; reformatted text only.
- match: Rewrite to match the provided style; modified text only.
- blend: Combine source and destination texts coherently, using the destination’s structure while reordering and renaming as needed; return only the final integrated text, treating additional_source as the destination.
- join: Merge content into one coherent part, removing redundancy.
- context: Add LLM-ready context only; do not rewrite the main text. (defaults: completeness=gist, scope=focus, method=contextualise)
- math: Consider mathematical fields that apply to this and specify which are used.
- orthogonal: Identify what is orthogonal in this situation.
- bud: Apply addition/subtraction-like reasoning non-numerically.
- boom: Apply limit/continuity-like reasoning non-numerically.
- meld: Apply set theory reasoning non-numerically.
- order: Apply order or lattice theory reasoning non-numerically.
- logic: Apply propositional or predicate logic reasoning non-numerically.
- probability: Apply probability or statistics reasoning non-numerically.
- recurrence: Calculate the recurrence relation of this idea and explain its consequences in plain language.
- map: Use data mapping and transformation concepts to describe this: identify source and target schemas, specify transformation rules, and describe information flow, including loss, duplication, or enrichment.
- mod: Modulo the first idea by the second idea non-numerically.
- dimension: Expand dimensions of this geometrically and describe each axis.
- rotation: Compute the 90-degree rotation metaphorically.
- reflection: Compute the reflection metaphorically.
- invert: Invert the concept to reveal negative space.
- graph: Apply graph or tree theory reasoning non-numerically: identify nodes and edges, describe direction, weight, and centrality, and explain how structure influences flow or dependency.
- grove: Apply integral/derivative concepts non-numerically.
- dub: Apply power/root concepts non-numerically.
- drum: Apply multiplication/division concepts non-numerically.
- document: List document or writing formats (e.g., ADRs, experiment logs, RFCs, briefs), explain why each fits, and what perspective it reveals.
- com b: Analyze the subject using the COM-B model (Capability, Opportunity, Motivation, Behavior), identify key enablers and barriers across Capability, Opportunity, and Motivation, map them to Behavior Change Wheel intervention functions and behavior change techniques, and outline a minimal, testable implementation and evaluation plan. (defaults: completeness=full, scope=focus, method=rigor)
- wardley: Generate a Wardley Map by identifying users, needs, and components, then output it as a Markdown table where rows are visibility levels and columns are evolution stages, plus a concise summary of dependencies and key strategic insights. (defaults: completeness=full, scope=focus, method=steps, form=table)
- dependency: List dependencies and what they depend on. (defaults: scope=relations)
- cochange: For multiple subjects, show how each directly cochanges with the others. (defaults: scope=relations)
- interact: Explain how these elements interact. (defaults: scope=relations)
- dependent: Explain how these elements are dependent on each other. (defaults: scope=relations)
- independent: Explain how these elements are independent. (defaults: scope=relations)
- parallel: Describe problems that could arise if these two items were parallelized. (defaults: scope=relations)
- unknown: Imagine critical unknown unknowns in this situation and how they might impact the outcome.
- jim: Analyze the subject for connascence (Strength, Degree, Locality), identify its type, compute Severity = Strength × Degree ÷ Locality, and propose remedies to reduce harmful connascence.
- domain: Perform a connascence-driven discovery of business domains: group elements by coupling where multiple forms of connascence converge, describe obligations and change scenarios, and suggest boundary-strengthening remedies.
- tune: Evaluate this design through the Concordance Frame: visibility, scope, and volatility of dependencies that must stay in tune. (defaults: completeness=full, scope=focus, method=rigor)
- melody: Analyze the system for clusters that share coordination patterns in visibility, scope, and volatility, infer the shared intent or 'tune', and recommend ways to clarify or strengthen domains by reducing coordination cost. (defaults: completeness=full, scope=focus, method=rigor)
- constraints: Identify the key constraint in this system, describe behaviours it promotes and discourages, and discuss how to balance it for long-term health. (defaults: completeness=full, scope=focus, method=rigor)
- effects: Describe the second- and third-order effects of this situation or change. (defaults: completeness=full, scope=dynamics, method=steps)
- fix: Fix grammar, spelling, and minor style issues while keeping meaning and tone; return only the modified text. (defaults: completeness=full, scope=narrow)
- todo: Format this as a todo list. (defaults: completeness=gist, scope=actions, method=steps, form=checklist)
- bridge: Guide me from the current state to the desired situation described in the additional source. (defaults: completeness=path, scope=focus, method=steps)
- Other static prompts (tokens only; see docs for semantics): (none)

### Meta interpretation channel (ADR 019) and richer structure (ADR 020)

If your system prompt asks the model to explain how it interpreted your request, format that explanation as a trailing, clearly-marked Markdown section so Talon can treat it as non-pasteable meta. The core pattern (ADR 019) is:

1. End your main answer normally.
2. Then add a heading and short explanation, for example:

   - `## Model interpretation`  
     *(one or more lines describing how the model understood the prompt, assumptions, or chosen pattern)*

When a response follows this pattern:

- The main answer (everything before the `## Model interpretation` heading) is what gets pasted and shown as the primary body.
- The interpretation section (from the heading onward) is:
  - Stored as `last_meta`.
  - Available as a `meta` source (for example, `model meta to browser` / `context` / `query`).
  - Surfaced near last-recipe radars:
    - As a short `Meta:` line in the confirmation GUI.
    - As a “Model interpretation” preview in quick help.
    - As a “Model interpretation” section in the browser view.

ADR 020 extends this meta channel into a richer optional bundle. Inside the meta section (after `## Model interpretation`), the recommended structure is:

- `## Model interpretation` – a short paragraph explaining how the model interpreted your request and why it chose its approach.
- `### Assumptions` – 2–4 short bullets capturing key assumptions and inferred constraints.
- `### Gaps and checks` – 1–3 bullets listing major gaps/caveats and specific things you should verify.
- `### Better prompt` – a single, improved version of your request in one or two sentences.
- `### Axis tweak suggestion` – when helpful, a line like `Suggestion: completeness=gist` or `Suggestion: form=bullets` using the same axis tokens as the rest of the grammar.

All of these live in the **meta channel only**:

- They are not pasted into your documents.
- They are visible via recap surfaces and via `model meta …` commands.

### In-Talon helpers for discoverability (ADR 006)

To make the grammar easier to remember and explore, ADR 006 adds a few helpers:

- `model patterns` – opens a small GUI with curated “patterns” for common tasks (coding and writing/product/reflection), each showing:
  - A pattern name (for example, “Debug bug”, “Fix locally”, “Summarize selection”).
  - The underlying recipe (for example, `describe · full · narrow · debugging · rog`).
  - A one-line description.
  - Clicking a pattern runs the corresponding recipe via the normal `model` pipeline and closes the GUI.
  - You can also say `model coding patterns` or `model writing patterns` to open the GUI filtered to those domains, then either click or say the pattern name (for example, `debug bug`) to execute it.
- `model pattern menu <staticPrompt>` – opens a prompt-focused pattern picker for any static prompt (for example, `describe`, `fix`, `retro`), which:
  - Shows the prompt’s description and any profile defaults (completeness/scope/method/form/channel).
  - Lists a few generic, axis-driven mini-patterns (for example, “Quick gist”, “Deep narrow rigor”, “Bulleted summary”) as concrete recipes for that prompt.
  - Lets you trigger these patterns by clicking or by saying the preset names (for example, `quick gist`) while the picker is open.
- `model quick help` – opens an in-Talon “Model grammar quick reference” window listing:
  - The main axes (static prompt, completeness, scope, method, form, channel, directional lens).
  - Canonical modifier vocab, pulled from the same Talon lists that drive the grammar.
  - A few example recipes.
- You can also open axis-specific quick help:
  - `model quick help completeness`
  - `model quick help scope`
  - `model quick help method`
  - `model quick help form` / `model quick help channel` (once split help is available)
- `model show grammar` – opens quick help with the last recipe and an exact, speakable `model …` line so you can repeat or adapt a successful combination by voice.
- `model last recipe` – shows the last prompt recipe (static prompt plus effective completeness/scope/method/form/channel and directional lens) in a notification, even if the confirmation GUI is closed.

When the confirmation GUI is open, it also:

- Displays a `Recipe:` line derived from the same axes, so you can see at a glance what combination you just used.
- Offers a `Show grammar help` button that opens quick help pre-populated with the last recipe, and an `Open pattern menu` button that opens the prompt-specific pattern menu for the same static prompt, making it easy to either study or explore nearby recipes for what you just ran.

#### Quick reference (ADR 006 commands)

- Patterns:
  - `model patterns` / `model coding patterns` / `model writing patterns`
  - `model pattern menu <staticPrompt>`
- Recap:
  - `model last recipe`
  - `model again` / `model again …`
  - Confirmation GUI `Recipe:` line
- Grammar help:
  - `model quick help`
  - `model quick help completeness` / `scope` / `method` / `form` / `channel` / `directional`
  - `model show grammar`

#### Provider switching (ADR 047)

- `model provider list` — canvas with providers, reachability hints, and current selection.
- `model provider use <name>` / `model provider next` / `model provider previous` — switch providers (aliases like `gemeni` are accepted).
- `model provider status` — show current provider, default model, streaming toggle, and reachability.
- Configure providers via `user.model_provider_current/default/extra/probe` in `talon-ai-settings.talon`.

#### Prompt recipe suggestions (ADR 008)

- `model suggest` / `model suggest for <subject>` – ask the model to propose 3–5 concrete `staticPrompt · completeness · scope · method · form · channel · directional` recipes for the current source (selection/clipboard/etc.), insert them as `Name: … | Recipe: …` lines, cache them, and open a small “Prompt recipe suggestions” window.
- In the suggestions window:
  - Click a suggestion to run that recipe via the normal `model` pipeline; the window closes after execution.
  - Say `run suggestion <number>` (for example, `run suggestion 1`) to execute a specific recipe by index.
  - Say `close suggestions` to dismiss the window.
- `model suggestions` – reopen the suggestion window based on the last `model suggest` call without re-running the model.

#### Rerun last recipe shorthand (ADR 009)

- `model last recipe` – show the last prompt recipe (static prompt plus effective completeness/scope/method/form/channel and directional lens) in a notification, even if the confirmation GUI is closed.
- `model again` – rerun the last recipe exactly, using the same static prompt, axes, and directional lens.
- `model again [<staticPrompt>] [axis tokens…]` – rerun the last recipe but override any subset of:
  - Static prompt (`<staticPrompt>`).
  - Completeness (`skim`, `gist`, `full`, etc.).
  - Scope (`narrow`, `focus`, `bound`, etc.).
  - Method (`steps`, `plan`, `cluster`, etc.).
  - Form (`bullets`, `table`, `code`, `adr`, etc.); tone sits on persona (`tone=kindly`/`directly`/`formally`, etc.).
  - Channel (`slack`, `jira`, `presenterm`, etc.).
  - Tone (`kindly`, `directly`, `formally`, `casually`, `gently`, etc.).
  - Directional lens (`fog`, `rog`, `ong`, etc.).
- Examples:
- `model again gist fog` – keep the last static prompt/scope/method/form/channel, but change completeness to `gist` and directional lens to `fog`.
- `model again todo gist fog` – change static prompt to `todo` and completeness to `gist`, reuse the last scope/method/form/channel, and set directional lens to `fog`.
- `model again steps directly rog` – keep the last static prompt/completeness/scope, but switch method to `steps`, tone to `directly`, and directional lens to `rog`.

### Persona / Intent / Contract (Who / Why / How)

When you are deciding how much of the grammar to use, it helps to think in three families (ADR 040):

- **Persona – Who**  
  - `voice` – who is speaking (for example, `as programmer`, `as teacher`).  
  - `audience` – who this is for (for example, `to junior engineer`, `to CEO`, `to team`).  
  - `tone` – emotional register (for example, `casually`, `formally`, `directly`, `gently`, `kindly`).  
  - You can usually ignore persona until you explicitly want to tailor an explanation for a specific role.

- **Intent – Why**  
  - `intent` – interaction-level intent (for example, `for information`, `for deciding`, `for brainstorming`, `for teaching`, `for evaluating`).  
  - Pick a intent when you care about “why we’re talking” (teach vs decide vs explore), not about output container or reasoning steps.

- **Contract – How**  
  - `completeness` – how much coverage (`skim`, `gist`, `full`, `max`, `minimal`, `deep`).  
  - `scope` – what territory is in-bounds (`narrow`, `focus`, `bound`, `actions`, `relations`, `system`, `dynamics`, etc.).  
  - `method` – how to think/decompose (`steps`, `plan`, `debugging`, `xp`, `diverge`, `converge`, `mapping`, etc.).  
  - `form` – container/shape (`bullets`, `table`, `code`, `adr`, `story`, `checklist`, `faq`, `recipe`, `bug`, `spike`, `log`, `cards`, `commit`, `gherkin`, `shellscript`).  
  - `channel` – medium bias (`slack`, `jira`, `presenterm`, `remote`, `sync`, `html`, `codetour`, `diagram`, `svg`).

In day-to-day use you can:

- Start with just a static prompt and directional lens (for example, `model describe fog`).
- Add **How** (contract axes) when you want more control over depth, territory, reasoning, or output shape.
- Only reach for **Who** (persona) and **Why** (intent) when you specifically want to change who you’re speaking as/to, or whether you’re teaching vs deciding vs brainstorming.

#### Who / Why / How – examples

A couple of common prompts decomposed into the three families:

- “Explain simply to a junior engineer”  
  - **Persona (Who)**: `as teacher` + `to junior engineer` + `tone=kindly`.  
  - **Intent (Why)**: `for teaching`.  
- **Contract (How)**: `completeness=gist` or `minimal`, `scope=focus`, `method=scaffold`, plus an optional form/channel when the medium matters (for example, `form=bullets`, `channel=slack`).  
  - **Do not** try to encode this entirely as a new audience or intent token; treat it as a recipe across existing axes.

- “Executive brief for CEO” vs “Deep technical write-up for engineers”  
  - **Persona (Who)**:  
    - Exec brief → `as programmer` + `to CEO` + `tone=directly`/`formally`.  
    - Deep write-up → `as programmer` + `to programmer`/`to principal engineer`.  
  - **Intent (Why)**:  
    - Exec brief → often `for deciding` or `for information`.  
    - Deep write-up → usually `for information` or `for evaluating`.  
  - **Contract (How)**:  
    - Exec brief → `completeness=gist`, `scope=focus`, `method=structure` (headline-first delivery in the prose), optionally `form=bullets`.  
    - Deep write-up → `completeness=full` or `deep`, `scope=system`/`relations`, `method=structure`/`analysis`, `form=adr` or `form=table`, optionally `tone=directly` if you want a firmer stance.
  - Again, keep persona and intent focused on Who/Why; put coverage, territory, reasoning, and container into the contract axes.

### Modifier axes (advanced)

The `model` command now supports several short, speech-friendly modifier axes you can tack on after the prompt:

Completeness (`completenessModifier`): `full`, `gist`, `max`, `minimal`, `skim`
Scope (`scopeModifier`): `actions`, `activities`, `bound`, `dynamics`, `edges`, `focus`, `interfaces`, `narrow`, `relations`, `system`
Method (`methodModifier`): `adversarial`, `analysis`, `case`, `cluster`, `cocreate`, `compare`, `contextualise`, `converge`, `debugging`, `deep`, `diagnose`, `direct`, `diverge`, `experimental`, `facilitate`, `filter`, `flow`, `indirect`, `ladder`, `liberating`, `mapping`, `motifs`, `plan`, `prioritize`, `probe`, `rewrite`, `rigor`, `samples`, `scaffold`, `socratic`, `steps`, `structure`, `systemic`, `taxonomy`, `visual`, `walkthrough`, `wasinawa`, `xp`
Form (`formModifier`): `adr`, `bug`, `bullets`, `cards`, `checklist`, `code`, `commit`, `faq`, `gherkin`, `log`, `recipe`, `shellscript`, `spike`, `story`, `table`, `visual`
Channel (`channelModifier`): `codetour`, `diagram`, `html`, `jira`, `presenterm`, `remote`, `slack`, `svg`, `sync`
Directional (`directionalModifier`): `bog`, `dig`, `dip bog`, `dip ong`, `dip rog`, `fig`, `fip bog`, `fip ong`, `fip rog`, `fly bog`, `fly ong`, `fly rog`, `fog`, `jog`, `ong`, `rog`
  - Additional form/channel notes:
    - `cards` – format the answer as discrete cards/items with clear headings and short bodies.
    - `story` – format the output as a user story using “As a…, I want…, so that…”, optionally with a short prose description and high-level acceptance criteria.
    - `bug` – format the output as a structured bug report (Steps to Reproduce, Expected Behavior, Actual Behavior, Environment/Context).
    - `spike` – format the output as a research spike: short problem/decision statement plus a list of key questions to answer.
    - `log` – write as a concise work or research log entry (dates/times optional, short bullet-style updates, enough context for future you).
    - `codetour` (channel) – output only a valid VS Code CodeTour `.tour` JSON document; no extra prose.
    - `diagram` (channel) – output only Mermaid diagram code; obey Mermaid safety constraints (no raw `()` in labels, escape `|` as `#124;`, etc.).
    - `remote` – emphasise remote-friendly delivery: distributed/online context hints and tooling tips.
    - `sync` – shape the answer as a synchronous/live session plan with agenda/steps/cues.

Directional lenses (required) are a separate axis:

- Direction (`directionalModifier`): core lenses like `fog`, `fig`, `dig`, `ong`, `rog`, `bog`, plus combined forms (for example, `fly ong`, `fip rog`, `dip bog`).
  - Every `model` command that uses this grammar should include exactly one directional lens token; composite aliases (fly/fip/dip) are advanced and hidden from primary help.

Axis multiplicity:

- Completeness is **single-valued**: you pick at most one completeness token per call.
- Scope and method are **multi-valued** tag sets; form and channel are single-valued:
  - You can speak more than one modifier on these axes in a single `model` command.
  - Under the hood, tokens are normalised into sets with small soft caps:
    - Scope: ≤ 2 tokens.
    - Method: ≤ 3 tokens.
    - Form: 1 token.
    - Channel: 1 token.
  - For example:
    - `model describe actions edges structure flow story jira fog`
      - Static prompt: `describe`.
      - Completeness: default/profile (`full` unless overridden).
      - Scope: `actions edges`.
      - Method: `structure flow`.
      - Form: `story`.
      - Channel: `jira`.

Some recommended multi-tag combinations:

- Scope:
  - `actions edges` – focus on concrete actions and the interactions between edges/interfaces.
- Method:
  - `structure flow` – emphasise both structural decomposition and stepwise flow.
- Form/Channel examples:
  - `bullets slack` – concise bullet list with Slack channel bias.
  - `adr presenterm` – ADR-format output with Presenterm channel bias.

When you use these modifiers—either by speaking them or via a pattern/pattern menu—their semantics are applied in two places:

- As part of the **system prompt contract** (via `Completeness/Scope/Method/Form/Channel` fields), which shapes how the model reasons and responds.
- As explicit **Constraints:** lines in the user prompt, where the Talon lists expand keys like `gist` or `focus` into the full “Important: …” descriptions you see in logs or confirmation text.

You normally say at most one or two of these per call. Examples:

- `model fix skim fog` – light grammar/typo fix.
- `model fix full rog` – full grammar/wording pass.
- `model todo gist checklist rog` – turn notes into a concise TODO list as an actionable checklist.
- `model describe flow rog` – explain the flow of selected code or text step by step using the `flow` method.
- `model describe diagram fog` – convert text to a mermaid-style Mermaid diagram, code-only.

If you omit a modifier, a default is inferred from global settings like:

- `user.model_default_completeness` / `scope` / `method` / `form` / `channel`.

You can adjust these defaults by voice:

- `model set completeness skim` / `model reset completeness`
- `model set scope narrow` / `model reset scope`
- `model set method steps` / `model reset method`
- `model set form bullets` / `model reset form`
- `model set channel slack` / `model reset channel`

For the full design of these axes (scalar completeness; multi-tag scope/method with soft caps and incompatibilities; single form/channel), see ADR 026 in `docs/adr/026-axis-multiplicity-for-scope-method-style.md`.

### Common axis recipes (cheat sheet)

Some high-frequency combinations you can say directly:

- Completeness:
  - `skim`, `gist`, `full`, `max`, `minimal`, `deep`.
- Diagrams:
  - `model describe diagram fog` – sketchy Mermaid diagram, code-only.
- Presentations:
  - `model describe presenterm rog` – Presenterm slide deck.
- ADRs:
  - `model describe adr rog` – Architecture Decision Record.
- Shell scripts:
  - `model describe shellscript rog` – shell script only.
- Debugging:
  - `model describe debugging rog` – debugging-style analysis of the current code or text.
- Methods:
  - `model describe systemic fog` – systems-thinking sketch of the subject.
  - `model describe experimental fog` – experimental/scientific plan and hypotheses.
  - `model describe flow rog` – explain the flow of code or text step by step.
  - `model describe motifs fog` – scan for recurring motifs and patterns (often with `scope relations`).
  - `model describe xp ong` – XP-flavoured stance: tiny slices, tests, and production feedback.
  - `model describe adversarial rog` – adversarial review: look for weaknesses, edge cases, and unstated assumptions.
  - `model describe scaffold fog` – explain for a beginner from first principles using gradual scaffolding.
  - `model describe socratic fog` – explore the topic by asking short, targeted questions before giving conclusions.
  - `model describe samples diverge fog` – generate multiple options with approximate probabilities.
  - `model describe liberating rog` – Liberating Structures-style facilitation framing.
  - `model describe diverge fog` – open up the option space and explore alternatives.
  - `model describe converge rog` – weigh options and narrow towards a decision.
  - `model describe mapping fog` – emphasise mapping elements and relationships over linear exposition.
  - `model describe analysis fog` – analysis-only, non-prescriptive description (no actions or recommendations).
- Directional lenses:
  - `fog` – upwards/generalising lens (bias toward gist + system/relations).
  - `dig` – downwards/grounding lens (bias toward deep + actions/narrow).
  - `fig` – span abstraction levels (bias toward ladder/mapping across system + actions).
  - `ong` – act/extend lens (bias toward concrete next steps, path + actions).
  - `rog` – reflect/structure lens (bias toward frameworks, structure, and reflection).
  - `bog` – blended act/reflect lens (hold action and reflection together as one stance).
  - `jog` – neutral confirmation / phrase end (reuse existing axes; avoid extra meta-questions).
- Types / taxonomy:
  - `model describe taxonomy rog` – express a type/taxonomy: categories, subtypes, and relationships.
- Channel formatting:
  - `model describe slack fog` – format for Slack (Markdown, mentions, code blocks).
  - `model describe jira fog` – format for Jira markup.
  - `model describe faq rog` – format as an FAQ page with question headings and concise answers.

### Legacy tokens → new grammar (quick mapping)

If you were using some older, now-retired tokens, here are the closest replacements using the current axes:

- Voices / stance:
  - `as XP enthusiast` → `as programmer` + `method=xp` (for example, `model describe xp ong`).  
  - `as adversary` → suitable voice + `method=adversarial` + `for evaluating`.  
  - `as liberator` → `as facilitator` + `method=liberating` (or use the “Liberating facilitation” pattern).
- Audiences:
  - `to receptive` / `to resistant` → keep the audience (for example, `to managers` / `to stakeholders`) and add `method=receptive` / `method=resistant`.  
- `to dummy` → keep a friendlier audience (for example, `to junior engineer`) and add `method=novice` + `gist`/`minimal` + `tone=kindly`.
- Intents / shape:
  - `for coding` → `goal=solve` + `form=code`.  
  - `for debugging` → `goal=solve` + `method=debugging`.  
  - `for slack` / `for table` / `for presenterm` / `for code tour` → `channel=slack` / `form=table` / `channel=presenterm` / `channel=codetour`.  
  - `for diverging` / `for converging` → `for brainstorming` + `method=diverge`; `for deciding` + `method=converge`.  
  - `for mapping` → `method=mapping` + relations/system/dynamics scope (often with `diagram` channel, `table` form, or `visual` method).

## OpenAI API Pricing

The OpenAI API that is used in this repo, through which you make queries to GPT 3.5 (the model used for ChatGPT), is not free. However it is extremely cheap and unless you are frequently processing large amounts of text, it will likely cost less than $1 per month. Most months I have spent less than $0.50

## Configuration

To add additional prompts, copy the [Talon list for custom prompts](lists/customPrompt.talon-list.example) to anywhere in your user directory and add your desired prompts. These prompts will automatically be added into the `<user.modelPrompt>` capture.

If you wish to change any configuration settings, copy the [example configuration file](../talon-ai-settings.talon.example) into your user directory and modify settings that you want to change.

| Setting                  | Default                                                                                                                                                                                                                                                            | Notes                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| user.openai_model        | `"gpt-5-nano"`                                                                                                                                                                                                                                                    | The model to use for the queries. NOTE: To access certain models you may need prior API use |
| user.model_provider_current | `"openai"`                                                                                                                                                                                                                                                      | Active provider id (see `model provider list` / `model provider use <name>`)                |
| user.model_provider_default | `"openai"`                                                                                                                                                                                                                                                      | Default provider id when current is unset                                                   |
| user.model_provider_extra | `{}`                                                                                                                                                                                                                                                              | Optional dict/list of extra providers (id/display/endpoint/api_key_env/default_model/aliases/features) |
| user.model_provider_token_openai | `""`                                                                                                                                                                                                                                                         | Optional token for the built-in `openai` provider when env vars are unavailable                                                |
| user.model_provider_token_gemini | `""`                                                                                                                                                                                                                                                         | Optional token for the built-in `gemini` provider when env vars are unavailable                                                |
| user.model_provider_model_gemini | `""`                                                                                                                                                                                                                                                         | Optional default model for the built-in `gemini` provider (used when switching providers or building requests)                |
| user.model_provider_model_aliases_gemini | `""`                                                                                                                                                                                                                                                 | Optional comma-separated spoken aliases for Gemini models (for example `one five pro:gemini-1.5-pro,flash:gemini-1.5-flash`) |
| user.model_provider_model_aliases_openai | `""`                                                                                                                                                                                                                                                 | Optional comma-separated spoken aliases for OpenAI models (for example `four o:gpt-4o,four point one:gpt-4.1`)               |
| user.model_provider_probe | `0`                                                                                                                                                                                                                                                               | Set to 1 to include reachability probes in provider list/status canvases                    |
| user.model_endpoint      | `"https://api.openai.com/v1/chat/completions"`                                                                                                                                                                                                                     | Any OpenAI compatible endpoint address can be used (Azure, local llamafiles, etc)           |
| (env) OPENAI_API_KEY / GEMINI_API_KEY | *unset* | Optional: set provider tokens via environment variables; `gemini` uses `GEMINI_API_KEY` by default. |
| user.model_request_timeout_seconds | `120`                                                                                                                                                                                                                                                    | Maximum time in seconds to wait for a single model HTTP request before timing out           |
| user.model_shell_default | `"bash"`                                                                                                                                                                                                                                                           | The default shell used when outputting shell commands (for example, when using the `shellscript` style) |
| user.model_system_prompt | `"Output just the main answer to the user's request as the primary response. Do not generate markdown formatting such as backticks for programming languages unless it is explicitly requested or implied by a style/method axis (for example, 'code', 'table', 'presenterm'). If the user requests code generation, output just code in the main answer and not additional natural-language explanation. After the main answer, append a structured, non-pasteable meta section starting with the heading '## Model interpretation'. In that meta section only (not in the main answer), briefly explain how you interpreted the request and chose your approach; list key assumptions and constraints as short bullets; call out major gaps or caveats and up to three things the user should verify; propose one improved version of the user's original prompt in one or two sentences; and, when helpful, suggest a single axis tweak in the form 'Suggestion: <axis>=<token>' using the existing axis token vocabulary."` | The meta-prompt for how to respond to all prompts (you can override this if you prefer a different meta format) |
