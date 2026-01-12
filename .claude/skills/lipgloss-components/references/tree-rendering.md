# Lip Gloss Tree Rendering Reference

Visualise hierarchies using `github.com/charmbracelet/lipgloss/tree`.

## Constructing Trees

```go
import "github.com/charmbracelet/lipgloss/tree"

t := tree.Root("Tokens").
  Child("scope",
    tree.New().Child("system", "draft"),
  ).
  Child("method",
    tree.New().Child("analysis", "rewrite"),
  )
```

Use `tree.New()` for subtrees when you need to branch further.

## Enumerators & Styles

```go
enumerator := tree.RoundedEnumerator
enumeratorStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("99")).MarginRight(1)
rootStyle := lipgloss.NewStyle().Bold(true)
itemStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("246"))

t = t.
  Enumerator(enumerator).
  EnumeratorStyle(enumeratorStyle).
  RootStyle(rootStyle).
  ItemStyle(itemStyle)
```

`tree.DefaultEnumerator` produces `├─`/`└─`; `Rounded` uses curved glyphs.

## Rendering

```go
treeView := t.String()
```

Embed the string within layout blocks. Trees are static; interactions happen via separate controls.

## Dynamic Trees

```go
func grammarTree(model model) tree.Tree {
  root := tree.Root("Palette")
  for _, category := range model.Categories {
    childTree := tree.New().Root(category.Name)
    for _, token := range category.Tokens {
      childTree = childTree.Child(token.Label)
    }
    root = root.Child(childTree)
  }
  return root
}
```

Generate trees from runtime data to reflect current state.

## Tips

- Keep label width short; truncate with `ansi.Truncate` if necessary.
- Differentiate selected nodes with bold, underline, or prefix glyphs.
- Pair with keyboard shortcuts to jump or expand nodes in the host Bubble Tea model.
