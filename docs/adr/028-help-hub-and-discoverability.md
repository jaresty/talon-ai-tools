# 028 – Help hub and discoverability consolidation

## Status
Accepted

## Context
- New users face fragmented help: browser HTML (`model help`), canvas quick help, pattern picker, prompt pattern menu, suggestions GUI, confirmation buttons, plus ADRs/README. Each surface is partial; none routes to the others.
- Terminology collisions (`help`, `quick help`, `patterns`, `pattern menu`, `suggestions`, `show grammar`) force recall over recognition. Voice triggers for GUIs are hidden and only active while windows are open.
- Static prompts/axes live in list files; defaults/caps/normalisation feedback live in code/ADRs; there is no searchable index inside Talon. When axes are dropped (caps/compat), users get minimal guidance.
- ADRs hold semantic explanations but are unreachable in-flow.

## Decision
Build a unified, in-Talon “Help Hub” with search, cross-links, and onboarding, and wire all help/pattern/suggestion surfaces to and from it.

## Relationship to existing ADRs and surfaces
- Reuse the **canvas quick help** as the grammar/detail surface (ADR 022 + ADR 025), not replace it; the Hub simply links into it and can host its search/filter.
- Treat the existing **pattern picker** (ADR 006) and **prompt pattern menu** as the pattern surfaces the Hub opens; no new pattern UX is invented here.
- Keep the **suggestion GUI** and `model suggest` flow (ADR 008) as-is; the Hub can open it when a cached source exists.
- Keep **recipe/meta recap** in confirmation (ADR 006/019/020) and only add outbound buttons (Help Hub, Suggestions) without changing the confirmation behaviour.
- Keep **HTML help generation** (ADR 005 work-log slices) as the full docs surface; the Hub links to it and exposes the cheat-sheet copy action.

## Key elements
- **Help Hub command**: add `model help hub` (and a button in confirmation and quick help) opening a small canvas chooser with: Quick Help, Patterns, Prompt Pattern Menu (prompt dropdown), Suggestions, Full HTML Docs, and “Copy cheat sheet”. Each item has a one-line description. Phased delivery: hub shell/buttons first, then search/filter, then hints/links/normalization, then cheat sheet/onboarding.
- **Searchable index**: add a text filter in Help Hub (and optionally quick help) that matches static prompts, axis tokens, pattern names, and suggestion commands; results are grouped (Prompts/Axes/Patterns/Suggestions/Docs) and only open the relevant surface or copy a link—no direct model execution. Recognition over recall. Canvas input uses a captured key buffer (faux input) with Esc/Backspace support; provide a voice fallback (e.g., `model help filter <phrase>`) if key capture is unavailable.
- **Cross-links**:
  - Quick help gains buttons: Open Patterns, Open Prompt Pattern Menu (pre-filled if last static prompt exists), Open Suggestions (if last source cached), Open HTML Docs.
  - Pattern/prompt pattern GUIs gain an “Axes/help” button jumping to quick help focused on that prompt/axis summary.
  - Confirmation window keeps “Show grammar help” but also “Open Help Hub” and “Open Suggestions” when a last-suggest source exists.
  - Add a “History” entry in Help Hub to open the request history drawer/list (ADR 027 surfaces) so past responses are discoverable without recalling commands.
- **Normalization visibility**: surface axis caps/normalisation drops inline in Help Hub/quick help (e.g., show “style ≤3; extras dropped: …” after merges) so users see what tokens will be kept.
- **Voice trigger hints**: show the active voice commands for each open surface inside the Hub (e.g., pattern GUI triggers, suggestion GUI commands) to reduce hidden affordances. Derive dynamically from Talon lists/config to avoid drift; hide if unavailable.
- **ADR links**: include a short “Learn why” section in Help Hub with links to relevant ADRs (005/006/008/009/012/013/019/020); expose as “Copy link” to clipboard (notify), not auto-open, to respect sandboxing.
- **Cheat sheet**: generate a compact Markdown one-pager (static prompts, axis tokens, top patterns, core commands). Link it from Help Hub (“Copy cheat sheet”) and HTML help.
- **Onboarding nudges**: add `model onboarding` to open Help Hub with a short 3-step overlay (try patterns, quick help, again overrides). Show once on first run or via command.
- **Error fallback**: if a help surface fails to render, Help Hub shows a fallback text list of commands and a “Copy HTML link” action to keep users unblocked; also notify succinctly.

## Consequences
- Discoverability improves via a single entrypoint and in-surface links; users can hop between grammar, patterns, suggestions, and docs without remembering commands.
- Search/filter reduces token memorisation and surfaces pattern names.
- Additional UI wiring adds modest code complexity (button handlers, state plumbing) but centralises help logic.
- Future help additions plug into Help Hub, reducing sprawl.
- Backwards compatibility is preserved: existing quick help, patterns, suggestions, and HTML help stay authoritative; the Hub layers navigation and hints on top rather than replacing behaviours defined in ADR 006/008/022/025.
- Modal coordination is explicit: opening Hub closes patterns/prompt-pattern/suggestions/quick help; launching those from Hub closes Hub; confirmation stays separate.
- Search is non-executing and disambiguated by group; normalization notes are scoped to last recipe and only show when drops occur; ADR links/cheat sheet use clipboard copy to avoid sandbox issues.
- Tests must cover hub open/close, modal transitions, search grouping, normalization note rendering, voice-hint derivation, and copy actions to prevent regressions.
- Integration with ADR 027: treat Hub as another surface managed by the request/UI controller so it follows the same open/close rules; when a request starts, controller closes Hub to avoid conflicts. Do not add Hub to the pill/toast surfaces; keep confirmation additions minimal (single button). Reuse ADR 027 toast mechanics for error fallback. Ensure Hub key handling (Esc/backspace) coexists with quick help/pill bindings.
- UI/UX mitigations:
  - Use opaque backgrounds, borders, and non-click-through canvases (`block_mouse`) where supported; if unavailable, warn and close overlapping surfaces aggressively.
  - Keep content within bounds: enable body scroll, wrap or truncate long labels/descriptions, and clamp search results; avoid hardcoded heights that cause overlap.
  - Provide clear affordances: hover/active states, visible drag handle, and explicit filter focus/feedback (cursor or placeholder); display a fallback message when key capture fails.
  - Avoid surprising reopen flows: do not auto-open Hub on close hotspots unless user explicitly opts in; default close hotspots to just close.
  - Make fallback explicit: when Hub cannot open, notify with retry guidance and explicit “copy cheat sheet” messaging instead of silent copy.
