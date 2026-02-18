# ADR-0136: SPA Progressive Web App (PWA) Installability

## Status

Accepted

## Context

The bar prompt-builder SPA (`web/`) is a SvelteKit static build deployed as a hosted web
page. Users access it exclusively through a browser tab. The question arose whether the
SPA could be extended to work as an iOS or desktop widget.

### Widget platform analysis

A feasibility evaluation found:

**iOS/macOS WidgetKit** — not feasible. WidgetKit renders SwiftUI timelines with no
WebView support. Interactivity is severely constrained (iOS 17+ App Intents only). The
entire interactive token selection model is structurally incompatible with WidgetKit
widgets. A widget surface would require a full native Swift rewrite.

**Windows Widgets** — not feasible as a full SPA. The Windows Widgets board uses
Adaptive Cards, not WebView2. Arbitrary HTML/JS cannot run in that context.

**Progressive Web App (PWA)** — feasible with minimal changes. A PWA manifest and
service worker turn the existing SPA into an installable app on every major platform:

| Platform | Install path | Result |
|---|---|---|
| macOS | Safari → File → Add to Dock | Standalone window in Dock |
| Windows | Edge/Chrome → install icon | Standalone window in taskbar |
| iOS | Share → Add to Home Screen | Fullscreen web app |
| Android | Chrome → install prompt | Fullscreen web app |

All existing SPA logic (grammar loading, token selection, conflict detection, prompt
rendering, URL hash sharing) works unchanged in the installed context.

### What makes this viable now

The SPA already satisfies most PWA requirements:
- Served over HTTPS (static CDN deploy)
- No server-side dependencies
- `grammar.json` is a static file — cacheable via service worker for offline use
- `renderPrompt.ts` is pure client-side logic with no browser API dependencies

The only missing pieces are a `manifest.json` and a service worker.

---

## Decision

Add PWA installability to the bar SPA by shipping a Web App Manifest and a minimal
service worker.

### `web/static/manifest.json`

```json
{
  "name": "bar prompt builder",
  "short_name": "bar",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a1a",
  "theme_color": "#1a1a1a",
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

### `web/src/app.html`

Add the manifest link tag to `<head>`:

```html
<link rel="manifest" href="%sveltekit.assets%/manifest.json" />
<meta name="theme-color" content="#1a1a1a" />
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
```

### Service worker (`web/src/service-worker.ts`)

Cache-first strategy for the grammar file and static assets; network-first for
navigation. SvelteKit exposes `$service-worker` for build-time asset manifests.

```typescript
import { build, files, version } from '$service-worker';

const CACHE = `bar-${version}`;
const ASSETS = [...build, ...files];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    )
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then((cached) => cached ?? fetch(event.request))
  );
});
```

### Icons

Add `icon-192.png` and `icon-512.png` to `web/static/`. These should use the existing
bar visual identity (dark background, `bar` wordmark or monogram).

---

## Consequences

### Positive

- Install-to-Dock on macOS requires zero user tooling beyond Safari — low friction
- Offline capability: grammar JSON is cached after first visit, SPA works without network
- Installed window has no browser chrome — closer to native app feel
- iOS home screen install gives fullscreen experience on mobile
- No changes to SPA logic, routing, or grammar pipeline

### Tradeoffs

- Service worker caching means grammar updates require a cache bust (handled automatically
  by SvelteKit's versioned asset filenames)
- Icons must be created (192px and 512px PNGs) — small design task

### Risks

- Low — PWA plumbing is additive and does not touch existing components
- Service worker scope must match the deploy path; if the SPA is served from a subpath,
  `start_url` and service worker scope need adjustment

---

## Falsifiables

**F1 (macOS install):** After visiting the SPA in Safari on macOS Sonoma, File → Add to
Dock is available and creates a standalone window that opens without browser chrome.

**F2 (offline):** After first visit, disabling network and reloading the installed app
shows the full SPA (grammar loads from cache, token selection works).

**F3 (iOS):** Share → Add to Home Screen on iOS creates a fullscreen icon that launches
without Safari UI.

**F4 (manifest validity):** Lighthouse PWA audit in Chrome DevTools passes installability
checks with no errors.

---

## Implementation Order

1. Create `icon-192.png` and `icon-512.png` in `web/static/`
2. Add `web/static/manifest.json`
3. Add manifest/meta tags to `web/src/app.html`
4. Add `web/src/service-worker.ts`
5. Verify with Lighthouse PWA audit
6. Test install on macOS (Safari), iOS (Safari), and Windows/Chrome
