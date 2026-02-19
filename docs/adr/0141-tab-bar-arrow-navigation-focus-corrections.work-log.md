# ADR-0141 Work Log — Tab-Bar Arrow Navigation and Focus Model Corrections

helper version: `helper:v20251223.1`

---

## Loop-1 — 2026-02-19 — K1: Correct ArrowKey focus + K3: Move shortcut legend

```
helper_version: helper:v20251223.1
focus: ADR-0141 § K1 — replace setTimeout(focusFirstChip) with setTimeout(focusActiveTab)
       in handleTabBarKey; delete F1b/F2b; add F1c/F2c.
       ADR-0141 § K3 — move shortcut-legend details below PatternsLibrary.

active_constraint: handleTabBarKey calls setTimeout(focusFirstChip) after ArrowKey, causing
  focus to escape the tab strip to the first chip of the new panel. F1b/F2b specify this
  wrong behavior. The correct ARIA tabs pattern keeps focus on the tab button after ArrowKey.
  Validation: npm test -- keyboard-navigation (F1c, F2c must go red before fix, green after).

validation_targets:
  - npm test -- keyboard-navigation (F1c: ArrowRight stays on tab button; F2c: ArrowLeft stays;
    F3c: directional wrap doesn't land on body — K2 deferred to Loop-2)
  - npm test -- keyboard-focus (F5k: shortcut legend still present after K3 move)
```
