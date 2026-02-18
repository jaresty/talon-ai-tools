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
