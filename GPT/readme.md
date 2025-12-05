# GPT and LLM Interaction

Query language models with voice commands. Helpful to automatically generate text, fix errors from dictation automatically, and generally speed up your Talon workflow.

## Help

- See [the list of prompts](lists/staticPrompt.talon-list) for the current static prompts that can be used with the `model` command; note that some behaviours (for example, diagrams, Presenterm decks, ADRs, and shell scripts) now live only as style/method axis values rather than static prompts (see ADR 012/013).

- See the [examples file](../.docs/usage-examples/examples.md) for gifs that show how to use the commands.

- View the [docs](http://localhost:4321/talon-ai-tools/) for more detailed usage and help

For implementation details of the modifier axes, defaults, helpers, and rerun shorthand, see the ADRs:

- `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`
- `docs/adr/006-pattern-picker-and-recap.md`
- `docs/adr/008-prompt-recipe-suggestion-assistant.md`
- `docs/adr/009-rerun-last-recipe-shorthand.md`
- `docs/adr/012-style-and-method-prompt-refactor.md`
- `docs/adr/013-static-prompt-axis-refinement-and-streamlining.md`
- `docs/adr/015-voice-audience-tone-purpose-decomposition.md`

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
- `### Axis tweak suggestion` – when helpful, a line like `Suggestion: completeness=gist` or `Suggestion: style=bullets` using the same axis tokens as the rest of the grammar.

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
  - Shows the prompt’s description and any profile defaults (completeness/scope/method/style).
  - Lists a few generic, axis-driven mini-patterns (for example, “Quick gist”, “Deep narrow rigor”, “Bulleted summary”) as concrete recipes for that prompt.
  - Lets you trigger these patterns by clicking or by saying the preset names (for example, `quick gist`) while the picker is open.
- `model quick help` – opens an in-Talon “Model grammar quick reference” window listing:
  - The main axes (static prompt, completeness, scope, method, style, directional lens).
  - Canonical modifier vocab, pulled from the same Talon lists that drive the grammar.
  - A few example recipes.
- You can also open axis-specific quick help:
  - `model quick help completeness`
  - `model quick help scope`
  - `model quick help method`
  - `model quick help style`
- `model show grammar` – opens quick help with the last recipe and an exact, speakable `model …` line so you can repeat or adapt a successful combination by voice.
- `model last recipe` – shows the last prompt recipe (static prompt plus effective completeness/scope/method/style and directional lens) in a notification, even if the confirmation GUI is closed.

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
  - `model quick help completeness` / `scope` / `method` / `style`
  - `model show grammar`

#### Prompt recipe suggestions (ADR 008)

- `model suggest` / `model suggest for <subject>` – ask the model to propose 3–5 concrete `staticPrompt · completeness · scope · method · style · directional` recipes for the current source (selection/clipboard/etc.), insert them as `Name: … | Recipe: …` lines, cache them, and open a small “Prompt recipe suggestions” window.
- In the suggestions window:
  - Click a suggestion to run that recipe via the normal `model` pipeline; the window closes after execution.
  - Say `run suggestion <number>` (for example, `run suggestion 1`) to execute a specific recipe by index.
  - Say `close suggestions` to dismiss the window.
- `model suggestions` – reopen the suggestion window based on the last `model suggest` call without re-running the model.

#### Rerun last recipe shorthand (ADR 009)

- `model last recipe` – show the last prompt recipe (static prompt plus effective completeness/scope/method/style and directional lens) in a notification, even if the confirmation GUI is closed.
- `model again` – rerun the last recipe exactly, using the same static prompt, axes, and directional lens.
- `model again [<staticPrompt>] [axis tokens…]` – rerun the last recipe but override any subset of:
  - Static prompt (`<staticPrompt>`).
  - Completeness (`skim`, `gist`, `full`, etc.).
  - Scope (`narrow`, `focus`, `bound`, etc.).
  - Method (`steps`, `plan`, `cluster`, etc.).
  - Style (`plain`, `bullets`, `tight`, etc.).
  - Directional lens (`fog`, `rog`, `ong`, etc.).
- Examples:
  - `model again gist fog` – keep the last static prompt/scope/method/style, but change completeness to `gist` and directional lens to `fog`.
  - `model again todo gist fog` – change static prompt to `todo` and completeness to `gist`, reuse the last scope/method/style, and set directional lens to `fog`.
  - `model again steps tight rog` – keep the last static prompt/completeness/scope, but switch method to `steps`, style to `tight`, and directional lens to `rog`.

### Modifier axes (advanced)

The `model` command now supports several short, speech-friendly modifier axes you can tack on after the prompt:

- Completeness (`completenessModifier`): `skim`, `gist`, `full`, `max`, `minimal`, `deep`, `framework`, `path`
- Scope (`scopeModifier`): `narrow`, `focus`, `bound`, `edges`, `relations`, `dynamics`, `interfaces`, `system`, `actions`
- Method (`methodModifier`): `steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`, `systemic`, `experimental`, `debugging`, `structure`, `flow`, `compare`, `motifs`, `wasinawa`, `ladder`, `contextualise`, `samples`, `xp`, `adversarial`, `headline`, `case`, `scaffold`, `liberating`, `diverge`, `converge`, `mapping`, `analysis`, `socratic`
- Style (`styleModifier`): `plain`, `tight`, `bullets`, `table`, `code`, `checklist`, `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`, `taxonomy`, `cards`, `codetour`, `story`, `bug`, `spike`, `faq`
  - Additional styles:
    - `cards` – format the answer as discrete cards/items with clear headings and short bodies.
    - `story` – format the output as a user story using “As a…, I want…, so that…”, optionally with a short prose description and high-level acceptance criteria.
    - `bug` – format the output as a structured bug report (Steps to Reproduce, Expected Behavior, Actual Behavior, Environment/Context).
    - `spike` – format the output as a research spike: short problem/decision statement plus a list of key questions to answer.

Directional lenses (required) are a separate axis:

- Direction (`directionalModifier`): core lenses like `fog`, `fig`, `dig`, `ong`, `rog`, `bog`, plus combined forms (for example, `fly ong`, `fip rog`, `dip bog`).
  - Every `model` command that uses this grammar should include exactly one directional lens token.

When you use these modifiers—either by speaking them or via a pattern/pattern menu—their semantics are applied in two places:

- As part of the **system prompt contract** (via `Completeness/Scope/Method/Style` fields), which shapes how the model reasons and responds.
- As explicit **Constraints:** lines in the user prompt, where the Talon lists expand keys like `gist` or `focus` into the full “Important: …” descriptions you see in logs or confirmation text.

You normally say at most one or two of these per call. Examples:

- `model fix skim plain fog` – light grammar/typo fix in plain language.
- `model fix full plain rog` – full grammar/wording pass, still straightforward.
- `model todo gist checklist rog` – turn notes into a concise TODO list as an actionable checklist.
- `model describe flow rog` – explain the flow of selected code or text step by step using the `flow` method.
- `model describe diagram fog` – convert text to a mermaid-style Mermaid diagram, code-only.

If you omit a modifier, a default is inferred from global settings like:

- `user.model_default_completeness` / `scope` / `method` / `style`.

You can adjust these defaults by voice:

- `model set completeness skim` / `model reset completeness`
- `model set scope narrow` / `model reset scope`
- `model set method steps` / `model reset method`
- `model set style bullets` / `model reset style`

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
  - `model describe socratic for teaching` – explore the topic by asking short, targeted questions before giving conclusions.
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
  - `to dummy` → keep a friendlier audience (for example, `to junior engineer`) and add `method=novice` + `gist`/`minimal` + `plain`.
- Purposes / shape:
  - `for coding` → `goal=solve` + `style=code`.  
  - `for debugging` → `goal=solve` + `method=debugging`.  
  - `for slack` / `for table` / `for presenterm` / `for code tour` → `style=slack` / `table` / `presenterm` / `codetour`.  
  - `for diverging` / `for converging` → `for brainstorming` + `method=diverge`; `for deciding` + `method=converge`.  
  - `for mapping` → `method=mapping` + relations/system/dynamics scope (often with `diagram`, `table`, or `abstractvisual` style).

## OpenAI API Pricing

The OpenAI API that is used in this repo, through which you make queries to GPT 3.5 (the model used for ChatGPT), is not free. However it is extremely cheap and unless you are frequently processing large amounts of text, it will likely cost less than $1 per month. Most months I have spent less than $0.50

## Configuration

To add additional prompts, copy the [Talon list for custom prompts](lists/customPrompt.talon-list.example) to anywhere in your user directory and add your desired prompts. These prompts will automatically be added into the `<user.modelPrompt>` capture.

If you wish to change any configuration settings, copy the [example configuration file](../talon-ai-settings.talon.example) into your user directory and modify settings that you want to change.

| Setting                  | Default                                                                                                                                                                                                                                                            | Notes                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| user.openai_model        | `"gpt-5-nano"`                                                                                                                                                                                                                                                    | The model to use for the queries. NOTE: To access certain models you may need prior API use |
| user.model_endpoint      | `"https://api.openai.com/v1/chat/completions"`                                                                                                                                                                                                                     | Any OpenAI compatible endpoint address can be used (Azure, local llamafiles, etc)           |
| user.model_request_timeout_seconds | `120`                                                                                                                                                                                                                                                    | Maximum time in seconds to wait for a single model HTTP request before timing out           |
| user.model_shell_default | `"bash"`                                                                                                                                                                                                                                                           | The default shell used when outputting shell commands (for example, when using the `shellscript` style) |
| user.model_system_prompt | `"Output just the main answer to the user's request as the primary response. Do not generate markdown formatting such as backticks for programming languages unless it is explicitly requested or implied by a style/method axis (for example, 'code', 'table', 'presenterm'). If the user requests code generation, output just code in the main answer and not additional natural-language explanation. After the main answer, append a structured, non-pasteable meta section starting with the heading '## Model interpretation'. In that meta section only (not in the main answer), briefly explain how you interpreted the request and chose your approach; list key assumptions and constraints as short bullets; call out major gaps or caveats and up to three things the user should verify; propose one improved version of the user's original prompt in one or two sentences; and, when helpful, suggest a single axis tweak in the form 'Suggestion: <axis>=<token>' using the existing axis token vocabulary."` | The meta-prompt for how to respond to all prompts (you can override this if you prefer a different meta format) |
