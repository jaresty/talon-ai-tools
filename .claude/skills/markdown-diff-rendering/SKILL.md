---
name: markdown-diff-rendering
description: Capsule for terminal Markdown and diff previews with references for renderer setup.
---

# Markdown & Diff Rendering (Skill Capsule)

## Use this skill when
- Terminal apps need to display Markdown responses, help text, or documentation.
- You want syntax-highlighted diffs alongside other views with graceful monochrome fallbacks.
- The task spans both Glamour-based Markdown rendering and Chroma diff formatting.

## Quickstart
- Choose a layout width first (from `lipgloss-layout-utilities`) and reuse it for both Markdown and diff renderers to avoid wrapping mismatches.
- Cache Glamour and Chroma renderers so repeated renders stay responsive.
- Offer plain-text fallbacks for copy/paste or limited-color environments.

## Dive deeper
- `references/markdown.md` — Glamour setup, custom styles, and performance tips.
- `references/diffs.md` — Chroma diff formatting, fallback renderers, and integration notes.

## Checklist
- [ ] Renderer instances cached for repeated use.
- [ ] Word wrap width matches surrounding layout constraints.
- [ ] Plain-text mode available for accessibility/export.
- [ ] Theme colors align with `lipgloss-theme-foundations` when customizing styles.
