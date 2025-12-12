# Talon-AI-Tools

**Control large language models and AI tools through voice commands using the [Talon Voice](https://talon.wiki) dictation engine.**

This functionality is especially helpful for users who:

- want to quickly edit text and fix dictation errors
- code by voice using tools like [Cursorless](https://www.cursorless.org/)
- have health issues affecting their hands and want to reduce keyboard use
- want to speed up their workflow and use AI commands across the entire desktop

**Prompts and extends the following tools:**

- Github Copilot
- OpenAI API (with any GPT model) for text generation and processing
  - Any OpenAI compatible model endpoint can be used (Azure, local llamafiles, etc)
- OpenAI API for image generation and vision

## Help and Setup:

1. Download or `git clone` this repo into your Talon user directory.
1. [Obtain an OpenAI API key](https://platform.openai.com/signup).

1. Create a Python file anywhere in your Talon user directory.
1. Set the key environment variable within the Python file

> [!CAUTION]
> Make sure you do not push the key to a public repo!

```python
# Example of setting the environment variable
import os

os.environ["OPENAI_API_KEY"] = "YOUR-KEY-HERE"
```

5. See the [GPT](./GPT/readme.md) or [Copilot](./copilot/README.md) folders for usage examples.

> [!NOTE]
> You can use this repo without an OpenAI key by [customizing the endpoint url](./GPT/readme.md#configuration) to be your preferred model.
>
> You can also exclusively use this repo with just [Copilot](./copilot/README.md) if you do not need LLM integration

### In-Talon help surfaces

- `model help hub` – central hub linking quick help, patterns, suggestions, history, docs.
- `model quick help` – grammar/axes cheat sheet; `model quick help hub/patterns/suggestions/history/docs` for nearby surfaces.
- `model patterns` / `model pattern menu <prompt>` – curated recipes and per-prompt presets.
- `model suggest` / `model suggestions` – prompt recipe suggestions picker.
- `model history drawer` / `model history list` – recent requests/responses.

### Quickstart Video

[![Talon-AI-Tools Quickstart](./.docs/video_thumbnail.jpg)](https://www.youtube.com/watch?v=FctiTs6D2tM "Talon-AI-Tools Quickstart")

## Development

- Tests run with the lightweight Talon stub harness under `tests/`; the helper `bootstrap.py` wires the stubs, so simply run `python3 -m unittest discover -s tests` or `make test`.
- Axis catalog guardrails: run `make axis-guardrails` (catalog drift check + catalog-backed cheat sheet generation) to keep axis tokens/docs aligned with the SSOT.
- `tests/stubs/talon/__init__.py` mirrors the Talon APIs required by the repo; add new behaviors there when extending commands.
- GPT orchestration code should flow through `lib/promptSession.PromptSession` rather than manually mutating `GPTState`. The typical pattern is to create a session, call `prepare_prompt(...)`, optionally `begin(reuse_existing=True)` when reusing an in-flight request, then `execute()`.
- When adding new actions, keep the `UserActions` methods thin, prefer unit tests similar to `tests/test_gpt_actions.py`, and verify they assert the prompt session interactions you expect.
