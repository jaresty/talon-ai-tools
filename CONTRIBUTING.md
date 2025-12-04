# Contributing

Thank you for your interest in contributing to `talon-ai-tools`. We are happy to receive new contributions. If you have any questions about contributing, feel free to ask.

## Contributing Python

- For all PRs please describe the purpose of the PR and give an example of any non-trivial functionality.
- Do not use external Python dependencies with `pip install`
  - This pollutes the Talon Python interpreter and can have unintended side effects
- Prefix all actions exposed from a module with `gpt_` or another appropriate prefix to distinguish it in the global namespace
  - i.e. Write a function like `actions.user.gpt_query()` not `actions.user.query()`
- Do not expose any actions globally with talon action classes if they don't need to be called from `.talon` files
- Comment all functions with doctrings and type annotations for arguments
- Any code that is intended to be reused within the repo should be placed within the `lib/` folder
- GPT orchestration should flow through `PromptPipeline`/`PromptSession`, and new actions should add unit tests mirroring `tests/test_gpt_actions.py` to pin expected pipeline calls.
- When implementing recursive flows, use `RecursiveOrchestrator` so controller directives stay JSON-encoded and the final delegate/controller output preserves the requested format.

## Contributing Talonscript

- Talon commands should follow a grammar that is intuitive for users or mimics the grammar of existing tools like Cursorless
  - Prefix all commands with an appropriate prefix like `model` or `pilot` to make sure they aren't accidentally run
- Duplicate commands following a similar syntax should be condensed into captures or lists _only_ if it improves readability for users or significantly reduces duplicate code for maintainers
  - It is better to duplicate code to make a command explicit and readable rather than overly condense the command within a fancy talon capture.
  - The commands inside a `.talon` file, to the extent possible, should be intuitive for a new user to understand. Numerous talon lists chained together requires a user to introspect code and adds friction to discoverability.
  - It is best to use talon commands that are very expliciti, even if overly verbose, and let the user customize them if desired. Brevity risks confusion.
- Any command that requires a capture or list should include a brief inline comment above it showing an example of the command and a one line description of what it does
- If a list is needed, `.talon-list` files should be used instead of defining lists inside Python
  - This makes it easier to customize list items by overriding the `.talon-list` and not needing to fork the Python.
- Avoid any configuration pattern that requires a user to fork this repository

## GPT prompts, axes, and ADRs

- Before adding or changing **static prompts** or axis lists, read:
  - `docs/adr/012-style-and-method-prompt-refactor.md`
  - `docs/adr/013-static-prompt-axis-refinement-and-streamlining.md`
  - `docs/adr/015-voice-audience-tone-purpose-decomposition.md`
- Design rules (summarised from those ADRs):
  - Prefer **axes + patterns** (completeness/scope/method/style + directional lenses) for new behaviours.
  - Add new static prompts only for clearly semantic/domain lenses or structured tasks that are not easily expressed via axes alone.
  - Keep Talon lists, pattern GUIs, help surfaces, and tests in sync whenever you change prompts or axes.
  - Name axis tokens for speech: use short, single, pronounceable words without hyphens (for example, `shellscript` instead of `shell-script`); avoid punctuation or multi-word phrases in axis keys so they remain easy to speak and remember.
  - Do **not** reintroduce axis-only behaviours (for example, `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `debug`, `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`, `taxonomy`) as static prompts; they should remain on the style/method axes with patterns/recipes.
  - When changing prompts or axes, run and update the guardrail tests described in ADR 012 (for example, `tests/test_axis_mapping.py`, `tests/test_static_prompt_docs.py`, `tests/test_model_pattern_gui.py`, `tests/test_model_help_gui.py`) so docs, patterns, and behaviour stay in sync.
  - When deprecating or demoting a static prompt, follow the “Mini-checklist: deprecating a static prompt” subsection in ADR 012 to keep config, patterns, docs, and tests aligned.
