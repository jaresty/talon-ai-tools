# GPT and LLM Interaction

Query language models with voice commands. Helpful to automatically generate text, fix errors from dictation automatically, and generally speed up your Talon workflow.

## Help

- See [the list of prompts](lists/staticPrompt.talon-list) for all the prompts that can be used with the `model` command.

- See the [examples file](../.docs/usage-examples/examples.md) for gifs that show how to use the commands.

- View the [docs](http://localhost:4321/talon-ai-tools/) for more detailed usage and help

For implementation details of the modifier axes and defaults, see the ADR:

- `docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md`

### Modifier axes (advanced)

The `model` command now supports several short, speech-friendly modifier axes you can tack on after the prompt:

- Completeness (`completenessModifier`): `skim`, `gist`, `full`, `max`
- Scope (`scopeModifier`): `narrow`, `focus`, `bound`
- Method (`methodModifier`): `steps`, `plan`, `rigor`
- Style (`styleModifier`): `plain`, `tight`, `bullets`, `table`, `code`

You normally say at most one or two of these per call. Examples (only using real prompts from `staticPrompt.talon-list`):

- `model fix skim plain fog` – light grammar/typo fix in plain language.
- `model fix full plain rog` – full grammar/wording pass, still straightforward.
- `model simple gist plain fog` – rewrite selected text in a simpler way, short but complete.
- `model short gist tight rog` – shorten selected text while keeping the core meaning, written tightly.
- `model todo gist bullets rog` – turn notes into a concise TODO list as bullets.
- `model flow full steps plain rog` – explain the flow of selected code or text step by step.
- `model diagram gist code fog` – convert text to a mermaid-style diagram, code-only.

If you omit a modifier, a default is inferred from:

- Global settings like `user.model_default_completeness` / `scope` / `method` / `style`, and
- Per-prompt defaults for some static prompts (for example, `fix`, `simple`, `short`, `todo`, `diagram`).

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
