## helper:diff-snapshot

```
_tests/test_canvas_font.py      | 15 ++++++++++++
_tests/test_telemetry_export.py |  8 +++++++
lib/canvasFont.py               | 52 ++++++++++++++++++++++++++++++++++++++++-
lib/telemetryExport.py          | 11 +++++++++
lib/uiDispatch.py               | 14 +++++++++++
5 files changed, 99 insertions(+), 1 deletion(-)
```

## helper:rerun python3 -m pytest _tests/test_canvas_font.py _tests/test_telemetry_export.py

### red
- timestamp: 2026-01-19T02:31:13Z
- exit_status: 1
- command: `python3 -m pytest _tests/test_canvas_font.py _tests/test_telemetry_export.py`
- excerpt:
  ```
  AttributeError: module 'talon_user.lib.canvasFont' has no attribute 'canvas_font_stats'
  ```

### green
- timestamp: 2026-01-19T02:31:55Z
- exit_status: 0
- command: `python3 -m pytest _tests/test_canvas_font.py _tests/test_telemetry_export.py`
- excerpt:
  ```
  _tests/test_canvas_font.py ....                                          [ 33%]
  _tests/test_telemetry_export.py ........                                 [100%]
  ============================== 12 passed in 0.06s ==============================
  ```

### removal
- timestamp: 2026-01-19T02:32:30Z
- exit_status: 1
- command: `python3 -m pytest _tests/test_canvas_font.py _tests/test_telemetry_export.py`
- excerpt:
  ```
  AttributeError: module 'talon_user.lib.canvasFont' has no attribute 'canvas_font_stats'
  ```
