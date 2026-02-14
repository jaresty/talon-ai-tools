## Task: T16 — Summarize PR / document (RE-TEST)

**Loop 1 Score:** 3  
**Loop 1 Gap:** skill-guidance-wrong — used `show` instead of `pull` for extraction  
**Fix Applied:** R-06 — Summarization / Extraction pattern using `pull+gist`  
**Task Description:** "Summarize this pull request for the team"

---

### Skill Selection Log (Run 1)

**Task Analysis:**
- User wants to *compress* a long PR into a shorter form
- Long source document (PR) → extraction, not explanation
- Per R-06: "Summarise this document" → pull; "Explain what X means" → show

**Token Selection:**
- **Task:** Considered `show` (explanation), `pull` (extraction) → chose `pull` 
  - *Correctly applied R-06: long SUBJECT to compress → pull!*
- **Completeness:** `gist` (condensed/core only — appropriate for summary)
- **Scope:** Considered `mean` (concepts), `act` (actions) → chose `mean` (what the PR conceptually does)
- **Method:** (none — extraction doesn't need method elaboration)
- **Form:** (none)
- **Channel:** `plain` (prose summary)
- **Persona:** (none — team context implied)

**Bar command constructed:**
```bash
bar build pull gist mean plain
```

**Bar output preview:**
```
The response extracts a specific subset or view of the subject.
[gist completeness (condensed), mean scope, plain channel]
```

---

### Skill Selection Log (Run 2 — Variance Check)

**Token Selection:**
- **Task:** `pull` (same — consistent extraction routing)
- **Completeness:** `gist` (same)
- **Scope:** `mean` (same)
- **Method:** (none)
- **Form:** (none)
- **Channel:** `plain`
- **Persona:** (none)

**Bar command constructed:**
```bash
bar build pull gist mean plain
```

**Variance:** None — skill consistently applies R-06 Summarization pattern. ✅

---

### Coverage Scores

| Dimension | Score | Notes |
|-----------|-------|-------|
| Token fitness | 5 | `pull+gist+mean` precisely matches "compress PR to conceptual core" |
| Token completeness | 5 | All dimensions captured; gist is perfect for summary |
| Skill correctness | 5 | Correctly applied R-06: extraction for long source compression |
| Prompt clarity | 5 | Clear extraction instruction vs explanation |
| **Overall** | **5** | **Fixed! Loop 1 gap resolved.** |

---

### Gap Diagnosis

**Gap type:** none  
**Notes:** R-06 fix successfully resolves summarization gap. Key heuristic working:
- Long SUBJECT to compress → `pull` (extraction)
- Concept explanation without long source → `show` (description)

