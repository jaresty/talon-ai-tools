# ADR-0133 Work Log — Bar Prompt Builder SPA

helper: helper:v20251223.1
EVIDENCE_ROOT: docs/adr/evidence/0133/
ARTEFACT_LOG: docs/adr/evidence/0133/artefact-log.md
VCS_REVERT: git restore --source=HEAD web/

---

## Loop 5 — 2026-02-17 — LLM integration panel green

```yaml
helper_version: helper:v20251223.1
focus: ADR-0133 D6 — direct LLM API calls from browser; provider config stored in localStorage; Anthropic, OpenAI, Ollama support
active_constraint: >
  No LLM integration exists — users cannot send bar prompts directly to an LLM from the UI.
  Falsifiable: grep for 'bar-llm-config\|anthropic-version' in build/_app exits 1 before, 0 after.
validation_targets:
  - "cd web && npm run build && grep -r 'bar-llm-config\\|anthropic-version' build/_app --include='*.js' -l"
evidence:
  - "red    | 2026-02-17T05:40:00Z | exit 1 | grep bar-llm-config|anthropic-version build/_app — no matches"
  - "green  | 2026-02-17T05:42:00Z | exit 0 | build/_app/immutable/nodes/2.BHrLxOHM.js matched"
  - "removal| 2026-02-17T05:43:00Z | exit 1 | git stash + npm run build + grep — no matches; git stash pop restores green"
rollback_plan: "git restore --source=HEAD web/src/routes/+page.svelte && rm web/src/lib/LLMPanel.svelte"
delta_summary: >
  helper:diff-snapshot: web/src/lib/LLMPanel.svelte (new, ~200 lines),
  web/src/routes/+page.svelte: +3 lines (import LLMPanel, <LLMPanel> usage)
  LLMPanel.svelte: provider dropdown (anthropic/openai/ollama), model text input,
  API key password field with show/hide toggle, temperature range slider,
  all config persisted to localStorage under bar-llm-config,
  Send button calls provider-specific fetch (Anthropic messages API with
  anthropic-dangerous-direct-browser-access header, OpenAI chat completions,
  Ollama generate), response displayed in scrollable pre block with Copy button.
  Build composites command + subject + addendum into a single user message.
loops_remaining_forecast: "0 loops: Phase 1-4 of MVP are complete. Phase 5 (usage patterns library) and deploy verification are low-priority residuals. Confidence: high."
residual_constraints:
  - id: RC-05
    description: >
      LLM API calls require CORS headers from providers. Anthropic requires
      anthropic-dangerous-direct-browser-access:true header. OpenAI allows browser
      direct access. Ollama requires CORS configured on localhost server.
    severity: Low
    mitigation: Documented in ADR D6; user-facing notes can be added if needed
    monitoring: User reports if API calls fail with CORS errors
    owning_adr: ADR-0133 D6
  - id: RC-04
    description: >
      Deploy workflow (deploy-spa.yml) untested end-to-end on GitHub Actions.
    severity: Low
    mitigation: Push to origin/main will trigger first real deploy run
    monitoring: GitHub Actions run
    owning_adr: ADR-0133 D2
next_work:
  - "Behaviour: deploy-spa.yml runs green on GitHub Actions | Validation: gh run view after push"
  - "Behaviour: usage patterns library (Phase 5) | Validation: build + grep for template tokens"
```

## Loop 4 — 2026-02-17 — localStorage persistence + URL hash sharing green

```yaml
helper_version: helper:v20251223.1
focus: ADR-0133 D4/D5 — localStorage auto-save; URL hash sharing (btoa base64 encode/decode); Share + Clear buttons
active_constraint: >
  Prompt state is ephemeral — page reload loses all token selections, subject, and addendum.
  No URL sharing mechanism exists.
  Falsifiable: grep for 'bar-prompt-state\|btoa' in build/_app exits 1 before, 0 after.
validation_targets:
  - "cd web && npm run build && grep -r 'bar-prompt-state\\|btoa' build/_app --include='*.js' -l"
evidence:
  - "red    | 2026-02-17T05:34:00Z | exit 1 | grep bar-prompt-state|btoa build/_app — no matches"
  - "green  | 2026-02-17T05:35:00Z | exit 0 | build/_app/immutable/nodes/2.CI5OPyHh.js matched"
  - "removal| 2026-02-17T05:36:00Z | exit 1 | git stash + npm run build + grep — no matches; git stash pop restores green"
rollback_plan: "git restore --source=HEAD web/src/routes/+page.svelte"
delta_summary: >
  helper:diff-snapshot: web/src/routes/+page.svelte — 79 insertions(+), 5 deletions(-)
  Added: STORAGE_KEY constant, serialize()/deserialize() using btoa/atob,
  onMount restores from URL hash then localStorage fallback,
  $effect auto-saves to localStorage on every state change,
  sharePrompt() encodes state as base64 hash + copies full URL to clipboard,
  clearState() resets all state + clears hash + removes localStorage entry,
  Share and Clear buttons added to action-row alongside Copy.
loops_remaining_forecast: "~1 loop: Phase 1 MVP polish (deploy workflow validation, GitHub Pages CNAME). Confidence: high."
residual_constraints:
  - id: RC-04
    description: >
      Deploy workflow (deploy-spa.yml) has not been executed end-to-end against GitHub Pages.
      Grammar copy step and CNAME configuration are untested in CI.
    severity: Low
    mitigation: Loop 5 — trigger workflow or document manual deploy steps
    monitoring: GitHub Actions run on push to main
    owning_adr: ADR-0133 D2
next_work:
  - "Behaviour: deploy-spa.yml workflow runs green on GitHub Actions | Validation: gh run view or manual push trigger"
```

## Loop 3 — 2026-02-16 — Incompatibility validation + subject/addendum inputs green

```yaml
helper_version: helper:v20251223.1
focus: ADR-0133 D3/UI — incompatible token conflict warnings; subject/addendum inputs; command --subject/--addendum flags
active_constraint: >
  Selected tokens can conflict silently; command has no --subject/--addendum.
  Falsifiable: grep incompatib and --subject in build/_app JS exits 1 before, 0 after.
validation_targets:
  - "cd web && npm run build && grep -r 'incompatib\\|--subject' build/_app --include='*.js' -l"
evidence:
  - "red  | 2026-02-16T00:00:00Z | exit 1 | grep incompatib build/ — no matches"
  - "green| 2026-02-16T00:00:00Z | exit 0 | grep found build/_app/immutable/nodes/2.*.js"
rollback_plan: "git restore --source=HEAD web/src/"
delta_summary: >
  helper:diff-snapshot: incompatibilities.ts (findConflicts using hierarchy.axis_incompatibilities),
  +page.svelte updated with conflict warning panel (amber border + token pair list),
  subject/addendum textareas that append --subject/--addendum to command string,
  copy button with ✓ feedback, command box amber border when conflicts exist.
loops_remaining_forecast: "~1 loop: URL sharing + localStorage (L4). Phase 1 MVP complete. Confidence: high."
residual_constraints:
  - id: RC-04
    description: No URL sharing or localStorage persistence yet (Phase 2-3)
    severity: Low
    mitigation: Loop 4
    monitoring: n/a
next_work:
  - "Behaviour: prompt state persists in localStorage + shareable URL hash | Validation: npm run build + manual verify"
```

## Loop 2 — 2026-02-16 — Grammar loading + token selector UI green

```yaml
helper_version: helper:v20251223.1
focus: ADR-0133 D3 — grammar JSON loads in browser; form token slugs present in build
active_constraint: >
  Grammar JSON not loaded in browser; page renders no token data.
  Falsifiable: build/prompt-grammar.json present in web/build/ and wardley appears in it.
validation_targets:
  - "cd web && npm run build && grep -r wardley build/ --include='*.json' -l"
evidence:
  - "red  | 2026-02-16T00:00:00Z | exit 1 | grep wardley web/src — no grammar loaded yet"
  - "green| 2026-02-16T00:00:00Z | exit 0 | build/prompt-grammar.json present in web/build/ with wardley"
rollback_plan: "git restore --source=HEAD web/src/ web/static/ Makefile"
delta_summary: >
  helper:diff-snapshot: grammar.ts (loadGrammar, getAxisTokens, getTaskTokens helpers),
  TokenSelector.svelte (chip grid, filter, use_when dot indicator), +page.svelte (full
  token selector + live command preview). Makefile bar-grammar-check and bar-grammar-update
  both now cp build/prompt-grammar.json web/static/ and include it in drift check.
  web/static/prompt-grammar.json committed as derived-but-tracked artifact.
loops_remaining_forecast: "~2 loops: validation feedback (L3), localStorage + URL sharing (L4). Confidence: medium."
residual_constraints:
  - id: RC-02
    description: No incompatibility validation in UI yet — user can select conflicting tokens
    severity: Medium
    mitigation: Loop 3 adds inline conflict alerts from hierarchy.axis_incompatibilities
    monitoring: visual check after token selection
  - id: RC-03
    description: No subject/addendum input or --subject flag in command output
    severity: Medium
    mitigation: Loop 3 or 4
    monitoring: n/a
next_work:
  - "Behaviour: incompatible token pairs surface as inline warnings | Validation: npm run build + visual check"
  - "Behaviour: subject/addendum fields append to command string | Validation: npm run build"
```

## Loop 1 — 2026-02-16 — SvelteKit scaffold + build green

```yaml
helper_version: helper:v20251223.1
focus: ADR-0133 D1/D2 — scaffold web/ directory; SvelteKit static SPA buildable end-to-end
active_constraint: >
  web/ does not exist; npm run build exits 1 because there is no package.json.
  Falsifiable: `ls web/build/index.html` exits 1 before the loop and 0 after.
validation_targets:
  - "cd web && npm ci && npm run build && ls build/index.html"
evidence:
  - "red  | 2026-02-16T00:00:00Z | exit 1 | ls web/ → No such file or directory"
  - "green| 2026-02-16T00:00:00Z | exit 0 | cd web && npm run build → build/index.html exists"
rollback_plan: "git restore --source=HEAD web/ && rm -rf web/"
delta_summary: >
  helper:diff-snapshot: web/ created with package.json, svelte.config.js, vite.config.ts,
  src/app.html, src/app.css, src/routes/+layout.svelte, src/routes/+layout.ts,
  src/routes/+page.svelte, static/favicon.png, .gitignore.
  Build exits 0, produces build/index.html. Favicon 404 fixed by adding placeholder.
loops_remaining_forecast: "~4 loops: grammar loading (L2), token selector UI (L3), prompt builder + preview (L4), polish/deploy (L5). Confidence: medium."
residual_constraints:
  - id: RC-01
    description: Grammar JSON not yet copied into static/ (deploy workflow does it at CI time)
    severity: Low
    mitigation: Loop 2 will load grammar from static path; CI workflow handles copy
    monitoring: deploy-spa.yml workflow run on next push
next_work:
  - "Behaviour: grammar JSON loads in browser and token list renders | Validation: npm run build + browser check that axes.form tokens appear in page source"
```
