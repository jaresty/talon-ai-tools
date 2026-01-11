## loop-003 red | BARTUI_DEBUG_PALETTE=/tmp/palette_enter_red.log /usr/bin/expect /tmp/tui_palette_enter.exp
- timestamp: 2026-01-11T09:22:04Z
- exit status: 1
- helper:diff-snapshot=0 files changed (baseline reproduction)
- excerpt:
  ```
  spawn env BARTUI_DEBUG_PALETTE=/tmp/palette_enter_red.log NO_COLOR=1 go run ./cmd/bar tui --grammar cmd/bar/testdata/grammar.json --no-alt-screen
  Token palette (Esc closes · Tab cycles focus · Enter toggles):
    » Filter: Filter tokens
  ...
  paletteFocus=2 not observed in debug log
  ```
- debug log fragment:
  ```
  $ head -n 12 /tmp/palette_enter_red.log
  ViewSummary visible=false focus=0 detail=paletteFocus=0 ...
  ...
  ViewSummary visible=true focus=1 detail=paletteFocus=0 paletteOptions=3 ...
  ```
- observation: With the baseline layout, pressing Enter leaves the palette filter focused; the debug log never records `paletteFocus=2`, so operators cannot advance into the options column.

## loop-003 green | BARTUI_DEBUG_PALETTE=/tmp/palette_enter_green.log /usr/bin/expect /tmp/tui_palette_enter.exp
- timestamp: 2026-01-11T09:23:23Z
- exit status: 0
- helper:diff-snapshot=3 files changed, 275 insertions(+), 22 deletions(-)
- excerpt:
  ```
  spawn env BARTUI_DEBUG_PALETTE=/tmp/palette_enter_green.log NO_COLOR=1 go run ./cmd/bar tui --grammar cmd/bar/testdata/grammar.json --no-alt-screen
  Token palette (Esc closes · Tab cycles focus · Enter applies option) · Active: none
  ...
  ```
- debug log fragment:
  ```
  $ sed -n '15p' /tmp/palette_enter_green.log
  ViewSummary visible=true focus=1 detail=paletteFocus=2 paletteOptions=3 paletteIndex=0 ...
  ```
- observation: After the Enter keypress the palette advances focus to the options column (`paletteFocus=2`) and remains visible, matching the updated status copy and ADR 0071 ergonomics requirements.
