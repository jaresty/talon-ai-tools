---
name: markdown-diff-rendering
description: Render Markdown (with Glamour) and code diffs (with Chroma) in a charm-style terminal app.
---

# Markdown & Diff Rendering

## Use this skill when
- Displaying assistant responses or docs in terminal
- Showing syntax-highlighted diffs in previews
- Switching between colored and plain-text modes

## Workflow

1. **Markdown rendering with Glamour**  
   ```go
   import "github.com/charmbracelet/glamour"

   func renderMarkdown(input string, width int) (string, error) {
     renderer, err := glamour.NewTermRenderer(
       glamour.WithAutoStyle(),      // or custom ANSI config
       glamour.WithWordWrap(width),
     )
     if err != nil {
       return "", err
     }
     return renderer.Render(input)
   }
   ```

2. **Custom styles**  
   Provide a style config that maps headings, blockquotes, etc., to your theme colors. Reference the default `ansi.StyleConfig` and swap the color hex strings.

3. **Diff rendering**  
   Use a diff formatter + Chroma for syntax highlighting.

   ```go
   import (
     "github.com/alecthomas/chroma/v2"
     "github.com/alecthomas/chroma/v2/formatters/terminal16m"
     "github.com/alecthomas/chroma/v2/styles"
   )

   func renderDiff(src string) (string, error) {
     lexer := chroma.Coalesce(chroma.MustNewLexer(&diff.Config{}))
     iterator, _ := lexer.Tokenise(nil, src)
     formatter := terminal16m.New(terminal16m.WithLineNumbers(true))
     style := styles.Get("github-dark") // or custom style
     var buf bytes.Buffer
     err := formatter.Format(&buf, style, iterator)
     return buf.String(), err
   }
   ```

4. **Plain text fallback**  
   Offer a toggle or detection to render in monochrome using Glamour’s “no colors” template for copy/paste contexts.

## Tips

- Clamp word wrap to your available column width minus padding/borders.
- Cache renderers when processing large volumes of markdown to avoid re-parsing style configs.
