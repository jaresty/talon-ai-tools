# ADR-0133 Work Log — Bar Prompt Builder SPA

helper: helper:v20251223.1
EVIDENCE_ROOT: docs/adr/evidence/0133/
ARTEFACT_LOG: docs/adr/evidence/0133/artefact-log.md
VCS_REVERT: git restore --source=HEAD web/

---

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
