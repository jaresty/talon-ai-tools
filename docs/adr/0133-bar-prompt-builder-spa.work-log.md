# ADR-0133 Work Log — Bar Prompt Builder SPA

helper: helper:v20251223.1
EVIDENCE_ROOT: docs/adr/evidence/0133/
ARTEFACT_LOG: docs/adr/evidence/0133/artefact-log.md
VCS_REVERT: git restore --source=HEAD web/

---

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
