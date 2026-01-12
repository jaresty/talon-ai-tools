name: lipgloss-tree-rendering
description: Render hierarchical trees with lipgloss/tree for navigation maps, grammar outlines, or preset structure.
---

# Lip Gloss Tree Rendering

## Use this skill when
- Visualising a hierarchy (e.g., grammar categories → tokens → samples)
- Presenting navigation paths or dependency graphs in a terminal UI
- Creating expandable sections with tree semantics

## Workflow

1. **Import the tree package**
   ```go
   import "github.com/charmbracelet/lipgloss/tree"
   ```

2. **Define the root and children**
   ```go
   t := tree.Root("Tokens").
     Child("scope",
       tree.New().Child("system", "draft"),
     ).
     Child("method",
       tree.New().Child("analysis", "rewrite"),
     )
   ```
   - Use `tree.New()` to create subtrees.

3. **Choose an enumerator and styles**
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
   - `tree.DefaultEnumerator` produces standard `├─`/`└─` branches; `Rounded` uses curved glyphs.

4. **Render the tree**
   ```go
   treeView := t.String()
   ```
   - Trees are static strings; embed them in layout blocks as needed.

5. **Dynamic trees**
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
   - Generate trees from runtime data to reflect the current state.

## Tips
- Trees are read-only visuals; combine with keyboard shortcuts (e.g., `Ctrl+[`]) to jump to nodes if you need interactive navigation.
- Keep width in mind: long labels can break alignment; truncate with `ansi.Truncate` if necessary.
- For accessibility, ensure the root and selected node styles are distinct (bold, underline, or color) and rely on glyphs like `>`, `*`, etc., for selection cues.
