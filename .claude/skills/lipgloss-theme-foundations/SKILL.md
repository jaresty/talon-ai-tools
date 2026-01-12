---
name: lipgloss-theme-foundations
description: Establish a reusable Lip Gloss theme anchored by Charmtone colors and expose helper styles for Bubble Tea components.
---

# Lip Gloss Theme Foundations

## Use this skill when
- Starting a new Charmbracelet TUI
- Standardizing colors/typography across components
- Sharing consistent palettes between Lip Gloss and Bubbles widgets

## Workflow

1. **Seed palette with Charmtone (optional but recommended)**  
   ```go
   import (
     "github.com/charmbracelet/lipgloss"
     "github.com/charmbracelet/x/exp/charmtone"
   )
   
   type Theme struct {
     Primary     lipgloss.Color
     Secondary   lipgloss.Color
     Background  lipgloss.Color
     Text        lipgloss.Color
     Subtle      lipgloss.Color
     AccentWarn  lipgloss.Color
     // add other semantic slots as needed
   }
   
   func NewTheme() Theme {
     return Theme{
       Primary:    lipgloss.Color(charmtone.Charple.Hex()),
       Secondary:  lipgloss.Color(charmtone.Dolly.Hex()),
       Background: lipgloss.Color(charmtone.Pepper.Hex()),
       Text:       lipgloss.Color(charmtone.Ash.Hex()),
       Subtle:     lipgloss.Color(charmtone.Squid.Hex()),
       AccentWarn: lipgloss.Color(charmtone.Zest.Hex()),
     }
   }
   ```

2. **Expose ready-made styles**  
   Create methods that return configured `lipgloss.Style` instances (e.g., base text, muted text, selected rows, border styles). This keeps all components pulling from the same source.

   ```go
   type Styles struct {
     Base        lipgloss.Style
     Muted       lipgloss.Style
     Title       lipgloss.Style
     SelectedRow lipgloss.Style
   }
   
   func (t Theme) Styles() Styles {
     base := lipgloss.NewStyle().Foreground(t.Text)
     return Styles{
       Base:        base,
       Muted:       base.Foreground(t.Subtle),
       Title:       base.Foreground(t.Primary).Bold(true),
       SelectedRow: base.Foreground(t.Background).Background(t.Primary),
     }
   }
   ```

3. **Add gradient helpers when needed**  
   Use `lipgloss.Color` gradients for headers or logo treatments.

4. **Share the theme**  
   Provide a global accessor (e.g. via a package-level `var Default Theme`) or inject through your Bubble Tea models.

## Tips

- Keep role names semantic (`Success`, `Warning`, etc.) so changing palettes later is painless.
- If the app supports dark/light switching, expose construction functions for each variant and swap them at runtime.
