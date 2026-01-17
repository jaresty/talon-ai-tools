## helper:diff-snapshot

```

## manual evidence – leaks snapshot (2026-01-17T22:48Z)

```
Process 19317: 19458674 leaks for 1873232784 total leaked bytes.
    19458674 (1786M) << TOTAL >>
```

- Source: `tmp/talon-leaks-1448.txt`
- Notes: allocations present as repeated 20,480-byte IOSurface tiles retained during dispatcher fallback.


## helper:rerun python3 -m pytest _tests/test_telemetry_export.py

### red
- timestamp: 2026-01-17T22:28:03Z
- exit_status: 1
- command: `python3 -m pytest _tests/test_telemetry_export.py`
- excerpt:
  ```
  AttributeError: <module 'talon_user.lib.telemetryExport' from '/Users/tkma6d4/.talon/user/talon-ai-tools/lib/telemetryExport.py'> does not have the attribute '_fetch_ui_dispatch_inline_stats'
  ```

### green
- timestamp: 2026-01-17T22:28:17Z
- exit_status: 0
- command: `python3 -m pytest _tests/test_telemetry_export.py`
- excerpt:
  ```
  _tests/test_telemetry_export.py ........                                 [100%]
  ============================== 8 passed in 0.06s ===============================
  ```

### removal
- timestamp: 2026-01-17T22:28:26Z
- exit_status: 1
- command: `git checkout -- lib/telemetryExport.py && python3 -m pytest _tests/test_telemetry_export.py`
- excerpt:
  ```
  AttributeError: <module 'talon_user.lib.telemetryExport' from '/Users/tkma6d4/.talon/user/talon-ai-tools/lib/telemetryExport.py'> does not have the attribute '_fetch_ui_dispatch_inline_stats'
  ```
