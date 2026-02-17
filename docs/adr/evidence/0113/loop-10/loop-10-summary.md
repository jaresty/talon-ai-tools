# ADR-0113 Loop-10 Summary — Output Channel Discoverability

**Date:** 2026-02-17
**Status:** Complete
**Focus:** Whether bar-autopilot correctly selects output channel tokens

---

## Summary

Loop-10 tested output channel tokens — whether autopilot discovers the right channel
for 13 tasks spanning code tooling, documentation, visual output, and collaboration.

- **Tasks evaluated:** 13 (T183–T195)
- **Mean score:** 4.15/5
- **Target:** ≥ 4.0 ✅ (barely)
- **Gapped tasks (≤3):** 4 tasks (T188, T189, T190, T193)

---

## Central Finding

**Channels with explicit, well-known names are fully discoverable. Channels that
represent subtle format preferences or tool-specific output modes are not.**

### High discoverability (user-directed or self-describing):
- `adr` — user says "ADR" (score 5)
- `presenterm` — user says "Presenterm slide deck" (score 5)
- `shellscript` — user says "shell script" (score 5)
- `gherkin` — user says "Gherkin" (score 4)
- `jira` — user says "Jira markup" (score 5)
- `svg` — user says "SVG" (score 5)
- `slack` — user says "Slack message" (score 5)
- `codetour` — user says "CodeTour" (score 5)
- `html` — user says "HTML" (score 5)

### Low discoverability (requires usage patterns or use_when):
- `sync` — "session plan" maps to plan+facilitate form, not sync channel (score 3)
- `sketch` — "D2 diagram" might route to `diagram` (Mermaid) instead (score 3)
- `plain` — "no bullets / plain prose" not routed to plain channel (score 3)
- `remote` — "remote setting" is context description, not channel trigger (score 3)

---

## Task Scores

| Task | Channel | Score | Notes |
|------|---------|-------|-------|
| T183 | adr | 5 | Explicit — "ADR" |
| T184 | presenterm | 5 | Explicit — "Presenterm" |
| T185 | shellscript | 5 | Explicit — "shell script" |
| T186 | gherkin | 4 | Explicit; minor make/check ambiguity |
| T187 | jira | 5 | Explicit — "Jira" |
| T188 | sync | 3 | No usage pattern; autopilot → plan+facilitate |
| T189 | sketch | 3 | "D2 diagram" may route to diagram (Mermaid) |
| T190 | plain | 3 | "No bullets" not routed to plain channel |
| T191 | svg | 5 | Explicit — "SVG" |
| T192 | slack | 5 | Explicit — "Slack" |
| T193 | remote | 3 | Ambiguous; no usage pattern |
| T194 | codetour | 5 | Explicit — "CodeTour" |
| T195 | html | 5 | Explicit — "HTML" |

**Mean: 4.15/5**

---

## Gaps Found

### G-L10-01 — plain: No usage pattern for prose-preference requests
**Gap type:** undiscoverable-token
**Severity:** High — "no bullets" requests are common; channel prevents LLM from using bullets
**Fix:** Add "Plain Prose Output" usage pattern + use_when entry

### G-L10-02 — sync: No usage pattern for session planning tasks
**Gap type:** undiscoverable-token
**Severity:** High — session planning is common; sync channel adds agenda/timing structure
**Fix:** Add "Synchronous Session Plan" usage pattern + use_when entry

### G-L10-03 — sketch: D2 vs Mermaid disambiguation missing
**Gap type:** undiscoverable-token
**Severity:** Medium — D2 users must know to say "sketch"; "D2 diagram" may not route correctly
**Fix:** Add use_when entry distinguishing sketch (D2) from diagram (Mermaid)

### G-L10-04 — remote: Ambiguous channel signal
**Gap type:** undiscoverable-token
**Severity:** Low — "remote" context usually still produces useful output without the channel
**Fix:** Add use_when entry clarifying delivery-optimization intent

---

## Infrastructure Fix (SSOT Regression)

**Critical:** `AXIS_KEY_TO_USE_WHEN` in `lib/axisConfig.py` was empty in the working tree
despite HEAD containing the form use_when entries (from loop-9 fix, commit a539dd6).
This is the same SSOT regression found and fixed in loop-9. Root cause unclear —
possibly a `make axis-regenerate-apply` run regenerated the file without the data.

**Fix applied:** Restored all 9 form use_when entries AND added 4 channel use_when entries.
Grammar regenerated via `make bar-grammar-update`. All tests pass.

---

## Changes Applied

| Rec | Change | File |
|-----|--------|------|
| R-L10-05 | Restored form use_when entries (SSOT regression fix) | lib/axisConfig.py |
| R-L10-01 | Added plain channel use_when entry | lib/axisConfig.py |
| R-L10-02 | Added sync channel use_when entry | lib/axisConfig.py |
| R-L10-03 | Added sketch channel use_when entry | lib/axisConfig.py |
| R-L10-04 | Added remote channel use_when entry | lib/axisConfig.py |
| R-L10-01 | Added "Plain Prose Output" usage pattern | internal/barcli/help_llm.go |
| R-L10-02 | Added "Synchronous Session Plan" usage pattern | internal/barcli/help_llm.go |
| — | Updated patternTokens test list (plain, sync) | internal/barcli/help_llm_test.go |
| — | Regenerated grammar files | build/, internal/barcli/embed/, cmd/bar/testdata/ |

---

## Comparison to Prior Loops

| Loop | Focus | Mean Score |
|------|-------|------------|
| Loop-5 | Scope validation | 4.875 |
| Loop-6 | Token guidance (ADR-0128) | 4.5 |
| Loop-7 | Directionals + persona | 4.75 |
| Loop-8 | Specialist forms | 3.38 |
| Loop-9 | Post-apply validation (loop-8) | 5.0 |
| **Loop-10** | **Output channels** | **4.15** |

The 4.15 mean masks the bimodal distribution: 9 tasks at 5 and 4 tasks at 3.
The gapped channels are not a new class of problem — they follow the same pattern as
specialist forms: systematically undiscoverable without explicit naming by the user.

---

## Pattern Confirmed

Loop-8 found specialist forms invisible. Loop-10 confirms the same applies to channels:
**Any token that is not self-naming needs a use_when entry or usage pattern to be
discovered by bar-autopilot for real user task phrasings.**

The fix is now applied for channels (plain, sync, sketch, remote). The SSOT infrastructure
issue with `AXIS_KEY_TO_USE_WHEN` being zeroed has recurred — monitoring needed.

---

## Conclusion

✅ 9 channels are fully discoverable via explicit naming
✅ 4 underspecified channels now have use_when entries
✅ 2 new usage patterns added (plain, sync)
✅ AXIS_KEY_TO_USE_WHEN SSOT restored + extended for channel axis
✅ All tests pass
⚠️ SSOT regression recurred — consider making make bar-grammar-update preserve existing use_when data
