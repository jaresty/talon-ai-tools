## loop-081 red | BARTUI_DEBUG_PALETTE=/tmp/palette_state.log /usr/bin/expect /tmp/tui_palette.exp
- timestamp: 2026-01-11T08:39:23Z
- exit status: 0
- helper:diff-snapshot=internal/bartui/program.go | 29 +++++++++++++++++++++++++++++
- excerpt:
  ```
  $ BARTUI_DEBUG_PALETTE=/tmp/palette_state.log /usr/bin/expect /tmp/tui_palette.exp
  ...
  Equivalent CLI: bar build --prompt '\t\u0010copy command\003' [Ctrl+B copies]
  ...
  $ wc -l /tmp/palette_state.log
        57 /tmp/palette_state.log
  $ head -n 12 /tmp/palette_state.log
  View visible=false focus=0 detail=
  WindowSize visible=false focus=0 detail=width=0 height=0
  View visible=false focus=0 detail=
  UpdateKey visible=false focus=0 detail=key="\\t\\u0010" type=runes palette=false focus=0
  View visible=false focus=0 detail=
  View visible=false focus=0 detail=
  View visible=false focus=0 detail=
  View visible=false focus=0 detail=
  View visible=false focus=0 detail=
  View visible=false focus=0 detail=
  $ grep -n 'openTokenPalette' /tmp/palette_state.log || echo "(no openTokenPalette entries)"
  (no openTokenPalette entries)
  ```
- impact: Palette toggle logging shows the UI immediately renders with `tokenPaletteVisible=false`, so the `Ctrl+P` accelerator never leaves the condensed summary and pilots cannot access token options despite the ADR requirement that the palette remain docked and visible.
- observation: The `grep` check confirms no `openTokenPalette` log entry was emitted, reinforcing that the palette closes before a view render; the expect transcript simultaneously shows the UI collapsing to the condensed subject line, matching user reports that the Token section is absent.
