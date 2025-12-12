# ADR-0046 – Work Log

## 2025-12-11 – Axis Catalog facade slice

Focus (kind: behaviour/guardrail): Establish a shared **axis_catalog** façade that unifies axis tokens, Talon list tokens, and static prompt catalog data, and route GPT/docs helpers through it with guardrail tests.

### Changes
- Added `lib/axisCatalog.py` exposing:
  - `axis_catalog()` combining `AXIS_KEY_TO_VALUE`, Talon axis list tokens, static prompt catalog, and description overrides.
  - Facade exports for `get_static_prompt_profile/get_static_prompt_axes/static_prompt_catalog/static_prompt_description_overrides`, plus `axis_list_tokens` for drift checks.
- Updated `GPT/gpt.py` to import static prompt helpers from `axisCatalog`, consolidating the docs/help entrypoint on the new façade.
- Tests:
  - New `_tests/test_axis_catalog.py` guardrails that Talon axis list tokens align with `AXIS_KEY_TO_VALUE` and that `axis_catalog()["static_prompts"]` matches `static_prompt_catalog()`.
  - `_tests/test_static_prompt_axis_tokens.py` now consumes `static_prompt_catalog` via the façade (still ties profiles back to `AXIS_KEY_TO_VALUE`).

### Checks
- Ran targeted catalog/axis tests:
  - `python3 -m pytest _tests/test_axis_catalog.py _tests/test_static_prompt_axis_tokens.py _tests/test_static_prompt_catalog_consistency.py _tests/test_static_prompt_docs.py _tests/test_readme_axis_lists.py`
  - Result: **19 passed**, 0 failed.

### Removal test
- Reverting this slice would drop the new façade and guardrails, and GPT/docs would fall back to disparate helpers; the added tests would fail or disappear, removing the alignment guardrail between axisConfig, Talon lists, and static prompt catalog.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Extend `axis_catalog` consumers: README/help hub/Talon settings should read catalog data from the façade rather than direct config access.
- Add a small validator/CLI to flag drift between axis tokens and Talon lists at dev time, and wire catalog data into request log axis filtering to keep Concordance inputs explicit.

## 2025-12-11 – RequestLog axis catalog alignment slice

Focus (kind: behaviour/guardrail): Align request history axis filtering with the new **axis_catalog** and guardrail tokens from axisConfig/Talon lists.

### Changes
- Updated `lib/requestLog._filter_axes_payload` to pull axis/token metadata from `axis_catalog()` (axisConfig tokens + Talon list tokens) so filtered axes in history entries stay in sync with the catalog domain.
- Added `_tests/test_request_log.py::test_append_entry_uses_axis_catalog_tokens` covering directional axis filtering (keeps catalog/list tokens, drops unknown) and passthrough trimming for non-axis keys.

### Checks
- Ran focused history/log tests: `python3 -m pytest _tests/test_request_log.py` (4 passed).

### Removal test
- Reverting would revert request history to pre-facade token filtering and drop the new guardrail test; Concordance-aligned axis/token drift could reappear without detection.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Extend catalog consumption to README/help hub/Talon settings.
- Add a developer-facing drift validator/CLI using `axis_catalog` to surface mismatches early.

## 2025-12-11 – Axis catalog drift validator slice

Focus (kind: guardrail/tools): Add a CLI validator to detect drift between axisConfig, Talon lists, and static prompt axis tokens, and guard it with tests.

### Changes
- Added `scripts/tools/axis-catalog-validate.py`:
  - Boots the repo and runs alignment checks across axisConfig token maps, Talon list tokens, and static prompt catalog axis tokens (skipping completeness free-form hints).
  - Exits non-zero with detailed findings if drift is detected.
- Added `_tests/test_axis_catalog_validate.py` to run the CLI and fail if it reports drift.

### Checks
- `python3 scripts/tools/axis-catalog-validate.py` → Axis catalog validation passed.
- `python3 -m pytest _tests/test_axis_catalog_validate.py` → 1 passed.

### Removal test
- Reverting would drop the drift validator and its guardrail test; axis/list/static prompt drift could reappear without a dev-time signal.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Wire README/help hub/Talon settings to consume `axis_catalog` data instead of direct config reads.
- Optionally integrate the validator into a CI hook or `make` target so drift fails fast in automation.

## 2025-12-11 – Axis docs via catalog slice

Focus (kind: behaviour/guardrail): Move GPT axis docs generation onto `axis_catalog` so README/help surfaces describe axis tokens directly from the catalog rather than raw Talon list parsing.

### Changes
- Updated `GPT/gpt.py`:
  - `_build_axis_docs` now pulls axis token/description pairs from `axis_catalog()` (axisConfig SSOT), falling back to Talon list parsing only if catalog data is missing.
  - Import block reuses the axis catalog facade (with a minimal fallback stub for older Talon runtimes).
- No doc text copied inline; behaviour change is the source of truth for axis docs (catalog-backed).

### Checks
- `python3 -m pytest _tests/test_static_prompt_docs.py` → 10 passed (axis docs expectations still satisfied).

### Removal test
- Reverting would send axis docs back to direct Talon list parsing, breaking the catalog-based SSOT intent and losing the alignment with axis_config tokens enforced by ADR-0046.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Route README/help hub/Talon settings consumers to use `axis_catalog` outputs directly (for example, axis cheat sheet generation), and consider adding a short CLI/Make target that emits catalog-backed docs to catch drift in CI.

## 2025-12-11 – README axis lists via catalog slice

Focus (kind: guardrail/docs): Make README axis token checks depend on `axis_catalog` so docs stay aligned with the catalog SSOT.

### Changes
- Updated `_tests/test_readme_axis_lists.py` to compare README axis token lists against `axis_catalog()` instead of direct Talon list reads/axis registry. This ties doc drift detection to the catalog façade.
- README content already matches catalog tokens; no text changes needed for this slice.

### Checks
- `python3 -m pytest _tests/test_readme_axis_lists.py` → 1 passed.

### Removal test
- Reverting would decouple README checks from the catalog and allow axis/list/catalog drift to slip into docs without failing tests.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Extend help hub and Talon settings to read axis/static prompt data via `axis_catalog`, and consider generating README cheat sheets from the catalog in a scripted way (or gating via CI) to keep docs and runtime aligned.

## 2025-12-11 – Help Hub catalog-backed navigation slice

Focus (kind: behaviour/guardrail): Make Help Hub search/index construction consume `axis_catalog` so help navigation reflects the catalog SSOT instead of raw list parsing.

### Changes
- `lib/helpDomain.help_index` now accepts an optional catalog and prefers catalog data for static prompts and axis tokens (falls back to Talon lists when absent).
- `lib/helpHub.build_search_index` passes `axis_catalog()` (with optional override) and a new test-friendly `catalog` parameter; `_build_search_index` uses the catalog facade by default.
- `_tests/test_help_hub.py::test_build_search_index_uses_buttons_and_lists` now uses a fake catalog to assert that prompt/axis entries come from the catalog, not from list parsing.

### Checks
- `python3 -m pytest _tests/test_help_hub.py` → 13 passed.

### Removal test
- Reverting would send Help Hub back to list-only search data and drop the guardrail that navigation reflects the catalog SSOT, reintroducing drift between help navigation and axis/static prompt semantics.

### Follow-ups / remaining ADR-0046 work (help domain)
- Extend quick-help canvas to read static prompt/axis docs from `axis_catalog` so both hub and quick-help share the same catalog-backed data.
- Consider extracting a small shared navigation state helper for hub + quick-help once catalog-backed data flows through both surfaces.

## 2025-12-11 – Quick-help canvas catalog alignment slice

Focus (kind: guardrail/tests): Ensure quick-help static prompt catalog stays aligned with the axis catalog SSOT.

### Changes
- Added `_tests/test_model_help_canvas_catalog.py` to assert `static_prompt_settings_catalog()` contains every profiled prompt from `axis_catalog()["static_prompts"]["profiled"]`, keeping quick-help prompt coverage aligned with the catalog.
- No runtime code changes required in this slice; existing quick-help rendering already consumes `static_prompt_settings_catalog`.

### Checks
- `python3 -m pytest _tests/test_model_help_canvas_catalog.py` → 1 passed.
- `python3 -m pytest _tests/test_help_hub.py _tests/test_model_help_canvas_catalog.py` → 14 passed.

### Removal test
- Reverting would drop the guardrail that quick-help prompt coverage matches the catalog, allowing drift between catalog SSOT and quick-help surfaces.

### Follow-ups / remaining ADR-0046 work (help domain)
- Plumb axis docs/static prompt descriptions directly from `axis_catalog` into quick-help rendering (currently driven by `static_prompt_settings_catalog`), and consider a shared navigation/data helper across hub and quick-help.

## 2025-12-11 – Quick-help axis lists via catalog slice

Focus (kind: behaviour/guardrail): Make quick-help axis key lists derive from the catalog SSOT and guard against drift.

### Changes
- `lib/modelHelpCanvas._axis_keys` now pulls axis tokens from `axis_catalog()` (falls back to `axis_docs_for`), so quick-help axis lists reflect the catalog rather than static list parsing.
- Directional grouping now includes catalog directional tokens when present.
- `_tests/test_model_help_canvas_catalog.py` extended to assert quick-help axis keys (completeness/scope/method/style) match `axis_catalog` tokens, keeping UI lists aligned with the catalog.

### Checks
- `python3 -m pytest _tests/test_model_help_canvas_catalog.py` → 2 passed.

### Removal test
- Reverting would break the catalog-to-quick-help alignment and drop the guardrail that axis keys shown in quick-help match the catalog SSOT, allowing drift between UI hints and axis/static prompt semantics.

### Follow-ups / remaining ADR-0046 work (help domain)
- Feed axis descriptions (not just keys) and static prompt text directly from `axis_catalog` into quick-help rendering, and consider a shared navigation/data helper with Help Hub to keep both surfaces in sync.

## 2025-12-11 – Axis catalog validator make target slice

Focus (kind: tools/guardrail): Wire the axis catalog drift validator into the developer workflow.

### Changes
- Added `axis-catalog-validate` Makefile target invoking `python3 scripts/tools/axis-catalog-validate.py` so catalog/list/profile drift can be run easily or hooked into CI.

### Checks
- `python3 -m pytest _tests/test_axis_catalog_validate.py` → 1 passed.

### Removal test
- Reverting would remove the convenient make target for catalog drift checks, making it easier for drift between axisConfig, Talon lists, and static prompts to slip past local/CI runs.

### Follow-ups / remaining ADR-0046 work (axis domain)
- Consider adding this target to CI/gating scripts; continue aligning help surfaces and Talon settings on `axis_catalog`.
