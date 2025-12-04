# GPT and LLM Interaction

Query language models with voice commands. Helpful to automatically generate text, fix errors from dictation automatically, and generally speed up your Talon workflow.

## Help

- See [the list of prompts](lists/staticPrompt.talon-list) for all the prompts that can be used with the `model` command.

- See the [examples file](../.docs/usage-examples/examples.md) for gifs that show how to use the commands.

- View the [docs](http://localhost:4321/talon-ai-tools/) for more detailed usage and help

For implementation details of the modifier axes, defaults, helpers, and rerun shorthand, see the ADRs:

- `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`
- `docs/adr/006-pattern-picker-and-recap.md`
- `docs/adr/009-rerun-last-recipe-shorthand.md`

### In-Talon helpers for discoverability (ADR 006)

To make the grammar easier to remember and explore, ADR 006 adds a few helpers:

- `model patterns` – opens a small GUI with curated “patterns” for common tasks (coding and writing/product/reflection), each showing:
  - A pattern name (for example, “Debug bug”, “Fix locally”, “Summarize selection”).
  - The underlying recipe (for example, `debug · full · narrow · rigor · rog`).
  - A one-line description.
  - Clicking a pattern runs the corresponding recipe via the normal `model` pipeline and closes the GUI.
  - You can also say `model coding patterns` or `model writing patterns` to open the GUI filtered to those domains, then either click or say the pattern name (for example, `debug bug`) to execute it.
- `model pattern menu <staticPrompt>` – opens a prompt-focused pattern picker for any static prompt (for example, `describe`, `fix`, `retro`), which:
  - Shows the prompt’s description and any profile defaults (completeness/scope/method/style).
  - Lists a few generic, axis-driven mini-patterns (for example, “Quick gist”, “Deep narrow rigor”, “Bulleted summary”) as concrete recipes for that prompt.
  - Lets you trigger these patterns by clicking or by saying the preset names (for example, `quick gist`) while the picker is open.
- `model quick help` – opens an in-Talon “Model grammar quick reference” window listing:
  - The main axes (goal/static prompt, directional lens, completeness, scope, method, style).
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

- Completeness (`completenessModifier`): `skim`, `gist`, `full`, `max`, `minimal`, `deep`
- Scope (`scopeModifier`): `narrow`, `focus`, `bound`, `edges`, `relations`
- Method (`methodModifier`): `steps`, `plan`, `rigor`, `rewrite`, `diagnose`, `filter`, `prioritize`, `cluster`
- Style (`styleModifier`): `plain`, `tight`, `bullets`, `table`, `code`, `checklist`, `diagram`, `presenterm`, `html`, `gherkin`, `shellscript`, `emoji`, `slack`, `jira`, `recipe`, `abstractvisual`, `commit`, `adr`
  - Additional style: `cards` – format the answer as discrete cards/items with clear headings and short bodies.

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
- `model flow full steps plain rog` – explain the flow of selected code or text step by step.
- `model describe diagram fog` – convert text to a mermaid-style Mermaid diagram, code-only.

If you omit a modifier, a default is inferred from global settings like:

- `user.model_default_completeness` / `scope` / `method` / `style`.

You can adjust these defaults by voice:

- `model set completeness skim` / `model reset completeness`
- `model set scope narrow` / `model reset scope`
- `model set method steps` / `model reset method`
- `model set style bullets` / `model reset style`

## OpenAI API Pricing

The OpenAI API that is used in this repo, through which you make queries to GPT 3.5 (the model used for ChatGPT), is not free. However it is extremely cheap and unless you are frequently processing large amounts of text, it will likely cost less than $1 per month. Most months I have spent less than $0.50

## Configuration

To add additional prompts, copy the [Talon list for custom prompts](lists/customPrompt.talon-list.example) to anywhere in your user directory and add your desired prompts. These prompts will automatically be added into the `<user.modelPrompt>` capture.

If you wish to change any configuration settings, copy the [example configuration file](../talon-ai-settings.talon.example) into your user directory and modify settings that you want to change.

| Setting                  | Default                                                                                                                                                                                                                                                            | Notes                                                                                       |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| user.openai_model        | `"gpt-5-nano"`                                                                                                                                                                                                                                                    | The model to use for the queries. NOTE: To access certain models you may need prior API use |
| user.model_endpoint      | `"https://api.openai.com/v1/chat/completions"`                                                                                                                                                                                                                     | Any OpenAI compatible endpoint address can be used (Azure, local llamafiles, etc)           |
| user.model_shell_default | `"bash"`                                                                                                                                                                                                                                                           | The default shell for `model shell` commands                                                |
| user.model_system_prompt | `"You are an assistant helping an office worker to be more productive. Output just the response to the request and no additional content. Do not generate any markdown formatting such as backticks for programming languages unless it is explicitly requested."` | The meta-prompt for how to respond to all prompts                                           |
