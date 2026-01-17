## helper:diff-snapshot

```
_tests/stubs/talon/__init__.py |  49 ++++++++++--
_tests/test_canvas_font.py     | 127 +++++++++++++++++++++++-----
lib/canvasFont.py              | 191 ++++++++++++++++++++++++++++-------------
3 files changed, 288 insertions(+), 79 deletions(-)
```

## helper:rerun python3 -m pytest _tests/test_canvas_font.py

### red
- timestamp: 2026-01-17T23:20:11Z
- exit_status: 1
- command: `python3 -m pytest _tests/test_canvas_font.py`
- excerpt:
  ```
  AssertionError: 2 != 1 : apply_canvas_typeface should reuse cached Skia typefaces
  AssertionError: 2 != 1 : draw_text_with_emoji_fallback should reuse cached emoji typefaces
  ```

### green
- timestamp: 2026-01-17T23:20:48Z
- exit_status: 0
- command: `python3 -m pytest _tests/test_canvas_font.py`
- excerpt:
  ```
  _tests/test_canvas_font.py ....                                          [100%]
  ============================== 4 passed in 0.02s ===============================
  ```

### removal
- timestamp: 2026-01-17T23:21:16Z
- exit_status: 1
- command: `git checkout -- lib/canvasFont.py && python3 -m pytest _tests/test_canvas_font.py`
- excerpt:
  ```
  AssertionError: 2 != 1 : apply_canvas_typeface should reuse cached Skia typefaces
  AssertionError: 2 != 1 : draw_text_with_emoji_fallback should reuse cached emoji typefaces
  ```
