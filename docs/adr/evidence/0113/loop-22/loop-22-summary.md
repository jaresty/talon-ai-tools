# ADR-0113 Loop-22 Summary — Cross-Axis Health Check

**Date:** 2026-02-18
**Status:** Complete
**Dev binary:** bar version dev
**Focus:** Fresh cross-axis health check. All axes now have use_when coverage (loop-21).
           This loop tests breadth across 8 diverse task types to find remaining skill gaps.

---

## Results

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| L22-T01 | probe full struct fail adversarial checklist | 4 | Minor (cross scope) |
| L22-T02 | show mean peer_engineer_explanation plain | 3 | **Yes — wrong persona** |
| L22-T03 | plan full act time walkthrough | 5 | None |
| L22-T04 | diff full thing mean branch table | 5 | None |
| L22-T05 | make full fail good gherkin | 5 | None |
| L22-T06 | plan full struct time variants | 4 | Minor (risk dimension) |
| L22-T07 | fix full struct time diagnose | **2** | **Yes — wrong task token** |
| L22-T08 | make full struct mean adr | 5 | None |

**Mean: 4.125/5**

---

## Root Cause: Missing Heuristic Sections

Two tasks failed due to the same structural gap: the `Token Selection Heuristics` section in
`help_llm.go` had **Choosing Scope**, **Choosing Method**, and **Choosing Form** — but lacked:

1. **Choosing Task** — no positive routing for task (static) token selection. Autopilot had to
   infer task tokens from name-matching alone. "debug a race condition" → `fix` via name
   association, even though bar's `fix` is content reformatting.

2. **Choosing Persona** — no routing guidance for when to use presets vs explicit audience tokens.
   Autopilot defaulted to `peer_engineer_explanation` for an "explain to manager" task, selecting
   programmer-to-programmer audience instead of manager.

The catalog was correctly documented throughout. The `fix` use_when already warned "not for
debugging" and the `to-managers` audience token was available and correctly described. The gap
was in the heuristics that guide the autopilot's selection process.

---

## Fixes Applied

### G-L22-01: "Choosing Task" heuristic section (help_llm.go)

Added before "Choosing Scope":
```
- Explain or describe → show
- Analyze, surface structure or assumptions → probe
- Debug, troubleshoot, diagnose a problem → probe + diagnose method
- Create new content or artifacts → make
- Plan steps or strategy → plan
- Compare or contrast subjects → diff
- Reformat or restructure existing content → fix
- Verify or audit against criteria → check
- Extract a subset of information → pull
- Simulate a scenario over time → sim
- Select from alternatives → pick
- Organize into categories or order → sort
```

### G-L22-02: "Choosing Persona" heuristic section (help_llm.go)

Added after "Choosing Task":
```
- Known audience: prefer explicit audience= token over presets
  (e.g., 'explain to manager' → voice=as-programmer audience=to-managers)
- Presets are shortcuts — verify the audience matches before using
- Non-technical audience (manager, PM, CEO, stakeholder) → to-managers, to-ceo, to-stakeholders
- Technical peer → peer_engineer_explanation, teach_junior_dev
- Cross-functional → stakeholder_facilitator or compose explicitly
```

### G-L22-03: probe use_when updated (staticPromptConfig.py — SSOT)

Added debugging heuristic to `probe`'s guidance:
```
For debugging/troubleshooting: use probe + diagnose method (not fix — fix is content
reformatting, not bug-fixing). Heuristic: 'debug', 'troubleshoot', 'diagnose', 'root cause',
'why is this happening', 'investigate the error' → probe + diagnose.
```

Note: guidance lives in `staticPromptConfig.py` per SSOT convention; inline "(NOT fix)" note
removed from help_llm.go heuristic since the token's own use_when carries it.

---

## Post-Apply Validation

| Task | Pre-fix score | Post-fix correct command | Post-fix score |
|------|--------------|--------------------------|---------------|
| L22-T07 | 2 | `probe full struct time diagnose bug` | 5 |
| L22-T02 | 3 | `voice=as-programmer audience=to-managers task=show completeness=full scope=mean channel=plain` | 5 |

**Mean: 4.125 → 4.625** ✅

Grammar regenerated, dev binary rebuilt, tests pass.

---

## Coverage Notes

- Task axis: all 11 tokens now have positive routing heuristics (new "Choosing Task" section)
- Persona axis: routing guidance added for first time (new "Choosing Persona" section)
- SSOT: probe guidance updated in staticPromptConfig.py; grammar regenerated
