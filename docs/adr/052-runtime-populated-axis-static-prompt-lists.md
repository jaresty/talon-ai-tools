# 052 – Runtime-populated axis/static prompt lists

## Status
Accepted

## Context
- Axis/static prompt semantics already live in Python (`axisConfig`, `staticPromptConfig`, `axis_catalog`), but Talon grammars also load tokens from `GPT/lists/*Modifier.talon-list` and `GPT/lists/staticPrompt.talon-list`.
- The .talon-list files are not the true source of truth: adding/removing tokens still requires editing Python. However, we maintain parity across Python, lists, and README/help via tests (for example, `test_readme_axis_lists.py`), which creates churn and drift risk.
- Consumers like `axis_catalog.axis_list_tokens`, `lib/talonSettings.py` fallbacks, and README generation parse the list files for validation even though the same data is available in the Python catalog.
- Goal: reduce duplicate artefacts and make it clear that the catalog/config is authoritative while still allowing user-extensible lists (models, destinations, custom prompts) to remain file-backed.

## Decision
- Populate Talon grammar lists for axes and static prompts at runtime from the Python catalog: set `ctx.lists["user.<axis|staticPrompt>"]` using `axis_catalog`/`staticPromptConfig` during module init.
- Do not keep axis/static prompt .talon-lists on disk; the catalog is the SSOT and runtime populates Talon lists dynamically. Only user-extensible lists (for example, `customPrompt`, `modelDestination`, `modelSource`) remain file-backed.
- Update README/help/tests to consume the catalog as the primary source (not files) for axis/static prompt vocab; adjust drift checks accordingly.
- Preserve compatibility shims in `GPT/gpt.py`/`lib/talonSettings.py` by reading from the catalog first and only falling back to files if the catalog is unavailable (for older Talon runtimes).

### Implementation notes
- Talon lists for axes/static prompts are populated at runtime from `axis_catalog`; list files are now optional and treated as overrides.
- Catalog helpers merge list tokens with SSOT tokens so partial lists cannot drop vocab.
- Catalog validation defaults to catalog-only (`--skip-list-files` with no `--lists-dir`); list-file checks are opt-in (`--no-skip-list-files` + `--lists-dir`).
- Optional helper: `scripts/tools/generate_talon_lists.py` can export axis/static prompt lists locally for debugging; generator `--check` verifies ad-hoc list directories.
- Guardrails: catalog validation (`scripts/tools/axis-catalog-validate.py`), help/canvas tests using the catalog, Make guardrail targets (`axis-guardrails`, `axis-guardrails-ci`, `axis-guardrails-test`, `ci-guardrails`, `guardrails`), and optional generator parity tests.

### Ops / guardrails
- No tracked axis/static prompt .talon-lists: runtime populates lists from the catalog. Guardrails focus on catalog validity and help/canvas parity; user-extensible lists remain file-backed and can be validated ad-hoc.
- `make axis-guardrails`/`axis-guardrails-ci` run catalog validation (verbose, skip list files by default) plus the cheat sheet; `make axis-guardrails-test`/`guardrails`/`ci-guardrails` add parity tests. `make talon-lists`/`talon-lists-check` are optional helpers for local exports/drift checks, not tracked outputs.
- Ad-hoc: `python3 scripts/tools/axis-catalog-validate.py --lists-dir <dir> --no-skip-list-files` validates a user-extensible Talon lists directory when present (lists-dir required when enforcing list checks); omit `--no-skip-list-files` to stay catalog-only. Example: `python3 scripts/tools/axis-catalog-validate.py --lists-dir /path/to/lists --no-skip-list-files`.

## Consequences
- Reduced duplication and clearer SSOT: changing an axis/static prompt happens in Python and flows automatically to grammar/help/README without maintaining generated list artefacts.
- Eliminates drift failures from stale on-disk axis/static prompt lists; validation targets the catalog itself.
- Users no longer assume editing axis/static prompt .talon-lists changes behaviour; the editable surface is explicit (Python or designated user lists). User-extensible lists remain file-backed where appropriate.
- Risk: regression in environments that relied on editing axis/static prompt list files directly; mitigated by documenting the new flow and clarifying that only user-extensible lists remain on disk.

## Follow-ups / Implementation sketch
- Add a small loader that builds `ctx.lists` for `staticPrompt`, `completenessModifier`, `scopeModifier`, `methodModifier`, `formModifier`, `channelModifier`, `directionalModifier` from `axis_catalog`/`static_prompt_catalog`.
- Update README/help/tests to consume the catalog instead of list files and retain linting for user-extensible lists.
- Adjust `axis_catalog.axis_list_tokens` and related drift checks to accept runtime-generated lists (or treat file reads as optional).
- Document the new contract in CONTRIBUTING (axes/static prompts are catalog-driven; only user-extensible lists are file-editable).
