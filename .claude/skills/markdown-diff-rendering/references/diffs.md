# Diff Rendering Reference

Render syntax-highlighted diffs using Chroma with diff lexers and terminal formatters.

## Diff Formatter

```go
import (
  "bytes"
  "github.com/alecthomas/chroma/v2"
  "github.com/alecthomas/chroma/v2/lexers/diff"
  "github.com/alecthomas/chroma/v2/styles"
  "github.com/alecthomas/chroma/v2/formatters/terminal16m"
)

func renderDiff(src string) (string, error) {
  lexer := chroma.Coalesce(diff.New())
  iterator, err := lexer.Tokenise(nil, src)
  if err != nil {
    return "", err
  }
  formatter := terminal16m.New(terminal16m.WithLineNumbers(true))
  style := styles.Get("github-dark")
  if style == nil {
    style = styles.Fallback
  }
  var buf bytes.Buffer
  if err := formatter.Format(&buf, style, iterator); err != nil {
    return "", err
  }
  return buf.String(), nil
}
```

- Wrap diff output before embedding in layouts (`lipgloss.Width` helps reserve space for line numbers).
- Choose styles that match your theme; register custom styles if necessary.

## Plain Diff Fallback

For environments without ANSI support, provide a simple colorless formatter:

```go
func renderPlainDiff(src string) string {
  lines := strings.Split(src, "\n")
  for i, line := range lines {
    switch {
    case strings.HasPrefix(line, "+"):
      lines[i] = fmt.Sprintf("+ %s", line[1:])
    case strings.HasPrefix(line, "-"):
      lines[i] = fmt.Sprintf("- %s", line[1:])
    }
  }
  return strings.Join(lines, "\n")
}
```

## Integration Notes

- Pair diff views with `lipgloss-layout-utilities` to place side-by-side with Markdown previews or command outputs.
- Expose toggles to switch between markdown and diff modes, keeping renderers cached for responsiveness.
