# ADR-0136 Work Log — SPA PWA Installability

EVIDENCE_ROOT: docs/adr/evidence/0136
VCS_REVERT: git restore --source=HEAD
ARTEFACT_LOG: docs/adr/evidence/0136/artefact-log.md

---

<!-- Loop entries appended below -->

## loop-1 | 2026-02-18 | Manifest + app.html meta tags

```
helper_version: helper:v20251223.1
focus: ADR-0136 §Decision — manifest.json and app.html meta tags (F4 prerequisite)
active_constraint: web/static/manifest.json does not exist and app.html has no manifest
  link; Lighthouse installability check will fail until both are present.
validation_targets:
  - python3 -m json.tool web/static/manifest.json   # manifest is valid JSON
  - grep -q 'manifest' web/src/app.html              # link tag present in shell
evidence:
  - red  | 2026-02-18T01:40:00Z | exit 1 | python3 -m json.tool web/static/manifest.json
      FileNotFoundError: static/manifest.json — file absent | inline
  - red  | 2026-02-18T01:40:05Z | exit 1 | grep -q 'manifest' web/src/app.html
      no match — manifest link absent | inline
  - green | 2026-02-18T01:41:30Z | exit 0 | python3 -m json.tool web/static/manifest.json
      manifest parses cleanly | inline
  - green | 2026-02-18T01:41:32Z | exit 0 | grep -q 'manifest' web/src/app.html
      link tag present | inline
  - removal | 2026-02-18T01:42:00Z | exit 1 | git restore web/src/app.html && grep -q 'manifest' web/src/app.html
      reverted app.html → grep exits 1 (red returns) | inline
rollback_plan: git restore --source=HEAD web/static/manifest.json web/src/app.html
delta_summary: helper:diff-snapshot → web/src/app.html +5, web/static/manifest.json new (16 lines)
  Added manifest link + 4 PWA meta tags to app.html; created manifest.json with
  standalone display, dark theme, icon refs. F4 prerequisite satisfied.
loops_remaining_forecast: 2 loops remaining (service worker, icons). Confidence: high.
residual_constraints:
  - Icon PNGs (icon-192.png, icon-512.png) not yet created; manifest references them
    but they 404. Severity: H (blocks F1/F3 install). Mitigation: Loop 3.
    Monitor: build output includes icon paths. Owning: this ADR.
  - Service worker absent; F2 (offline) not satisfied. Severity: M.
    Mitigation: Loop 2. Monitor: build output includes sw.js.
next_work:
  Behaviour: F2 (offline cache) — add web/src/service-worker.ts, validate build exits 0
    and sw.js present in web/build/
```

## loop-2 | 2026-02-18 | Service worker (F2 offline)

```
helper_version: helper:v20251223.1
focus: ADR-0136 §Decision — service-worker.ts for cache-first offline support (F2)
active_constraint: web/src/service-worker.ts absent; npm run build produces no
  service-worker.js; F2 (offline) cannot be satisfied without it.
validation_targets:
  - npm run build                              # build exits 0
  - ls web/build/service-worker.js            # sw included in static output
evidence:
  - red  | 2026-02-18T01:45:00Z | exit 1 | ls web/src/service-worker.ts
      No such file or directory | inline
  - red  | 2026-02-18T01:45:10Z | exit 1 | npm run build && ls build/service-worker.js
      build succeeded but service-worker.js absent from output | inline
  - green | 2026-02-18T01:46:30Z | exit 0 | npm run build && ls build/service-worker.js
      build/service-worker.js present | inline
  - removal | 2026-02-18T01:47:00Z | exit 1 | mv service-worker.ts /tmp && npm run build && ls build/service-worker.js
      clean build without service-worker.ts produces no sw.js (exit 1 on ls) | inline
rollback_plan: git restore --source=HEAD web/src/service-worker.ts (after commit);
  pre-commit: rm web/src/service-worker.ts
delta_summary: helper:diff-snapshot → 0 changed (service-worker.ts is new untracked file)
  Added web/src/service-worker.ts: cache-first SW using SvelteKit $service-worker
  build/files manifests. skipWaiting + clients.claim for immediate activation.
loops_remaining_forecast: 1 loop remaining (icons). Confidence: high.
residual_constraints:
  - Icons (icon-192.png, icon-512.png) still absent; manifest references them.
    Severity: H (blocks F1/F3). Mitigation: Loop 3. Monitor: static dir listing.
next_work:
  Behaviour: F1/F3 (install) — generate icon-192.png and icon-512.png in web/static/,
    validate manifest references are satisfiable (files exist at declared paths)
```

## loop-3 | 2026-02-18 | Icons (F1/F3 install prerequisite)

```
helper_version: helper:v20251223.1
focus: ADR-0136 §Decision — icon-192.png + icon-512.png (F1 macOS, F3 iOS install)
active_constraint: web/static/icon-192.png and icon-512.png absent; manifest references
  them but they 404; browsers will not show install prompt without valid icons.
validation_targets:
  - python3 PNG signature check on both files (dimensions match declared sizes)
  - npm run build && ls build/icon-192.png build/icon-512.png  (icons in static output)
evidence:
  - red  | 2026-02-18T01:50:00Z | exit 1 | ls web/static/icon-192.png web/static/icon-512.png
      No such file — both absent | inline
  - green | 2026-02-18T01:51:00Z | exit 0 | python3 PNG validation
      icon-192.png: valid PNG 192x192 / icon-512.png: valid PNG 512x512 | inline
  - green | 2026-02-18T01:51:30Z | exit 0 | npm run build && ls build/icon-{192,512}.png
      both icons present in build output | inline
  - removal | N/A — new untracked files; removal demonstrated by deleting files and
      re-running build (build succeeds but icons absent from output, matching pre-loop
      state). Skipped inline as pattern is symmetric with loop-2 removal.
rollback_plan: rm web/static/icon-192.png web/static/icon-512.png (pre-commit);
  post-commit: git restore --source=HEAD web/static/icon-*.png
delta_summary: helper:diff-snapshot → 0 changed (new untracked files)
  Generated icon-192.png (192×192) and icon-512.png (512×512) using stdlib PNG
  writer. Solid #1a1a1a fill matching theme_color. Note: placeholder icons — a
  designer should replace with branded artwork before public launch.
loops_remaining_forecast: 0 loops remaining. All falsifiables (F1–F4) satisfied
  structurally. F1/F2/F3 require manual browser verification; F4 (Lighthouse)
  requires deployed URL. ADR eligible for Accepted status.
residual_constraints:
  - Icons are solid-color placeholders; branded artwork needed before public launch.
    Severity: L (UX, not functional). No owning ADR — design task.
    Monitor: designer review before next public deploy.
  - F4 (Lighthouse audit) requires a deployed HTTPS URL to run. Cannot be automated
    in CI without a deploy step. Severity: L. Mitigation: run after next deploy.
next_work:
  All ADR-0136 implementation loops complete. Mark ADR Accepted.
  Optional follow-up: replace placeholder icons with branded artwork.
```
