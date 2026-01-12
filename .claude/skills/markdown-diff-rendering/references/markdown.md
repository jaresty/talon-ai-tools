# Markdown Rendering Reference

Render Markdown in terminal UIs using `github.com/charmbracelet/glamour`.

## Basic Renderer

```go
import "github.com/charmbracelet/glamour"

func renderMarkdown(input string, width int) (string, error) {
  renderer, err := glamour.NewTermRenderer(
    glamour.WithAutoStyle(),
    glamour.WithWordWrap(width),
  )
  if err != nil {
    return "", err
  }
  return renderer.Render(input)
}
```

- `WithAutoStyle` picks a style based on terminal background; swap with custom ANSI configs when needed.
- Always pass an explicit wrap width (layout width minus padding/border).

## Custom Styles

```go
config := glamour.DarkStyleConfig
config.CodeBlock.Chroma = "dracula"
renderer, err := glamour.NewTermRenderer(
  glamour.WithStyles(config),
  glamour.WithWordWrap(width),
)
```

Use shared palette colors from `lipgloss-theme-foundations` when overriding style tokens.

## Performance Tips

- Cache renderers when rendering many documents to avoid reparsing the style config.
- Normalize line endings (`\r\n` → `\n`) before rendering to prevent double spacing.

## Plain Text Fallback

Offer a monochrome mode for copy/paste contexts:

```go
renderer, err := glamour.NewTermRenderer(
  glamour.WithStylePath("./styles/no-color.json"),
  glamour.WithWordWrap(width),
)
```

Swap renderers on demand or keep both cached.
