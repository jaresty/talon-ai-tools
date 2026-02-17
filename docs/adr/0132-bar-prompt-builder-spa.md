# ADR-0132: Client-Only Bar Prompt Builder SPA

## Status

Accepted

## Context

bar is a CLI tool for constructing structured prompts via token composition. Users want a web-based interface for building bar prompts without requiring a backend server. The interface should make token selection intuitive, validate compositions in real-time, and integrate directly with LLM APIs.

This ADR captures the architectural decisions for building a client-only SPA that provides these capabilities.

---

## Decisions

### D1: Tech Stack — SvelteKit in SPA Mode

Use **SvelteKit** configured for **static site generation (SPA mode)**. Svelte's reactive model maps naturally to token selection state, and SvelteKit produces minimal bundles suitable for static hosting.

**Rationale:**
- React/Vue require more boilerplate for reactive state
- Svelte stores provide built-in state management without external dependencies
- SPA mode produces a single HTML/CSS/JS bundle deployable anywhere

### D2: Build & Hosting — Static Adapter + Cloudflare Pages

Build with **@sveltejs/adapter-static** and host on **Cloudflare Pages**.

**Rationale:**
- Zero cost, global CDN, custom domain support
- Fast edge delivery for static assets
- Simple CI/CD via git push

### D3: Grammar Data — Embedded JSON

Embed the grammar definition (tokens, descriptions, guidance, incompatibilities) as **JSON bundled with the app**, with optional CDN fallback.

**Rationale:**
- Single source of truth extracted from `axisConfig.py`
- Works offline after initial load
- No server needed to serve grammar

### D4: Persistence — localStorage

Store saved prompts and user preferences in **localStorage**.

**Rationale:**
- No backend required
- Works offline
- Simple implementation

### D5: Sharing — URL Hash (Base64)

Share prompts via **URL hash containing base64-encoded prompt state**.

**Format:**
```
https://bar-prompt-builder.pages.dev/#<base64-json>
```

**Rationale:**
- No database or backend needed
- Copy-pasteable links
- Minified keys keep URLs manageable

### D6: LLM Integration — Direct API Calls with User-Provided Keys

Allow users to configure their own API keys (stored in localStorage) and make **direct fetch calls** to LLM providers.

**Rationale:**
- No backend proxy needed
- Users retain full control of their API keys
- Supports OpenAI, Anthropic, Ollama via provider abstraction

### D7: Styling — CSS Variables + Scoped Styles

Use **CSS variables for theming** and **Svelte scoped styles** for component-level CSS.

**Rationale:**
- Lightweight (no Tailwind/UnoCSS build complexity)
- Easy to theme
- Svelte handles scoping automatically

---

## UI Components

### Token Selector Panel
- Tabbed/accordion interface grouped by axis
- Search/filter tokens
- Inline descriptions and guidance tooltips
- Visual indication of selected tokens

### Prompt Builder / Composition Area
- Ordered chip-based interface
- Drag-drop reordering (respecting grammar order)
- Real-time validation feedback

### Subject / Addendum Input
- Two textarea fields
- Character/word count

### Live Preview Panel
- Real-time prompt preview
- Copy-to-clipboard

### LLM Integration Panel
- Provider dropdown (OpenAI, Anthropic, Ollama)
- API key input
- Streaming response display
- Token usage stats

### Prompt History Sidebar
- Save/load prompts
- Search history
- Export/import JSON

### Grammar Validation Feedback
- Inline alerts for soft cap warnings
- Incompatibility alerts with fix suggestions

### Usage Patterns Library
- Pre-composed token templates
- One-click load

---

## Data Model

### Prompt State
```javascript
{
  tokens: {
    task: string | null,
    completeness: string | null,
    scope: string[],
    method: string[],
    form: string | null,
    channel: string | null,
    directional: string | null,
    persona: { voice, audience, tone, intent }
  },
  subject: string,
  addendum: string
}
```

### Saved Prompt
```javascript
{
  id: string,
  name: string,
  tokens: { ... },
  subject: string,
  addendum: string,
  createdAt: timestamp,
  tags: string[]
}
```

### LLM Config
```javascript
{
  provider: 'openai' | 'anthropic' | 'ollama',
  apiKey: string,
  model: string,
  temperature: number
}
```

---

## Validation Logic

The core validation module enforces:

1. **Required token**: `task` must be present
2. **Soft caps**: `scope ≤ 2`, `method ≤ 3`, others ≤ 1
3. **Incompatibilities**: Channel conflicts, form/channel conflicts, persona conflicts
4. **Token ordering**: Grammar order enforced in UI

---

## MVP Phases

| Phase | Features |
|-------|----------|
| 1 | Token selector + builder + preview + validation |
| 2 | localStorage history + save/load |
| 3 | URL sharing |
| 4 | LLM integration |
| 5 | Usage patterns library |

---

## Consequences

### Positive

- **No backend**: Zero server cost, simple deployment
- **Offline capable**: Works after initial load
- **Portable**: Can be hosted anywhere (GitHub Pages, Vercel, Cloudflare Pages)
- **Fast**: Static assets, no server round-trips

### Negative / Tradeoffs

- **No real-time sync**: History lives in localStorage per-device
- **CORS limitations**: May need browser extension or proxy for some LLM providers
- **No collaboration**: No shared prompts without export/import

---

## Alternatives Considered

| Alternative | Why Not |
|-------------|---------|
| React + Vercel | More boilerplate, larger bundle |
| Go → WASM | Complexity of cross-compilation, debugging difficulty |
| Backend server | Costs, maintenance, deployment complexity |
| IndexedDB over localStorage | localStorage sufficient for MVP |
