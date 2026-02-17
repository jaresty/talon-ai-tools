# ADR-0133: Client-Only Bar Prompt Builder SPA

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

### D2: Build & Hosting — Static Adapter + GitHub Pages

Build with **@sveltejs/adapter-static** and host on **GitHub Pages**.

**CI/CD:** `.github/workflows/deploy-spa.yml` triggers on push to `main` when `web/**` or `build/prompt-grammar.json` changes. The workflow copies `build/prompt-grammar.json` into `web/static/` before building, so the deployed SPA always ships with the grammar matching the same commit.

**Rationale:**
- Zero cost, no account required beyond existing GitHub repo
- Simple CI/CD via GitHub Actions on push to main — same repo, no external services
- Custom domain support via CNAME
- Grammar JSON is bundled at build time, eliminating CORS concerns entirely (no runtime fetch needed)

### D3: Grammar Data — Embedded JSON with Version Detection

Embed the grammar definition as **JSON bundled with the app** at build time, sourced directly from `build/prompt-grammar.json` (the same artifact produced by `prompts/export.py`).

The JSON already contains all metadata needed for a rich UI:
- `definitions` — token descriptions (main tooltip body)
- `labels` — short CLI-facing labels (ADR-0109)
- `guidance` — constraint/conflict notes (ADR-0110); surface as warning indicators
- `use_when` — task-type selection heuristics (ADR-0132); surface as "When to use" helper text
- `checksums` + `reference_key` — available for future versioning if needed

**Rationale:**
- Single source of truth: all token metadata flows from `axisConfig.py` through the existing export pipeline
- Bundled at build time (not fetched at runtime) — no CORS issue, works offline, no external dependency
- `use_when` and `guidance` fields enable richer token selector UX without any extra data work

**Grammar versioning:** The deploy workflow (`deploy-spa.yml`) copies `build/prompt-grammar.json` at build time, so the deployed SPA is always in sync with the grammar at that commit. Grammar updates trigger a redeploy via the `build/prompt-grammar.json` path trigger.

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
https://<github-username>.github.io/bar-prompt-builder/#<base64-json>
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
- Note: Ollama (localhost) requires CORS headers configured on the Ollama server; some providers may require a proxy

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
- Tooltip layers sourced from the grammar JSON:
  - **Description** — what the token does (from `definitions`)
  - **Notes** — constraint/conflict warnings (from `guidance`, ADR-0110)
  - **When to use** — task-type selection heuristic (from `use_when`, ADR-0132); shown for specialist form tokens
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

All validation rules are derived from the embedded JSON (`hierarchy.axis_soft_caps`, `hierarchy.axis_incompatibilities`) — no hardcoded rule lists in the SPA.

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

- **No backend**: Zero server cost, simple deployment on GitHub Pages
- **Offline capable**: Works after initial load
- **Rich metadata for free**: `use_when`, `guidance`, and `labels` from the existing export pipeline power the token selector UI without extra work
- **Fast**: Static assets, no server round-trips

### Negative / Tradeoffs

- **No real-time sync**: History lives in localStorage per-device
- **LLM CORS limitations**: Grammar JSON has no CORS issue (bundled). Ollama (localhost) requires CORS configured server-side; some LLM providers may need a proxy for browser API calls
- **No collaboration**: No shared prompts without export/import
- **Grammar staleness**: Bundled JSON is fixed at build time; grammar updates require a redeploy

---

## Alternatives Considered

| Alternative | Why Not |
|-------------|---------|
| Cloudflare Pages | GitHub Pages is free with no additional account needed |
| React + Vercel | More boilerplate, larger bundle |
| Go → WASM | Complexity of cross-compilation, debugging difficulty |
| Backend server | Costs, maintenance, deployment complexity |
| IndexedDB over localStorage | localStorage sufficient for MVP |
