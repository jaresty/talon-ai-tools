# ADR-0216: Ground Prompt — Derivable Restatements Pass

**Status**: Accepted
**Date**: 2026-03-29

---

## Context

Following ADR-0215's ~1,643-char reduction, the core is at 30,447 chars. A full pass applying the same A/B/C/D taxonomy to all remaining sections identifies four additional restatement targets. Unlike ADR-0215's targets, these are smaller and distributed across the prompt rather than concentrated in contiguous blocks.

**Taxonomy:**
- **A** — direct axiom restatement (derivable from axiom block)
- **B** — policy/sequencing restatement (derivable from a rule already present)
- **C** — non-derivable; keep
- **D** — structural redundancy; compress

---

## Reduction Targets

### Target 1 — Formal notation: natural-language restatement (~170 chars)

Lines 322-323 (post-audit-section):
```
Natural language may appear as section labels but may not substitute for encoding a constraint
in notation — if a constraint can be stated in notation, it must be.
```

Already stated at lines 315-317:
```
natural language may add context but may not substitute for notation;
prose adds context and introduces the specification — it does not encode the constraints.
```

**Classification**: B — lines 322-323 restate the natural-language prohibition already present 12 lines earlier. The post-audit placement creates the appearance of a separate rule, but the constraint is identical. "If a constraint can be stated in notation, it must be" follows directly from "natural language may not substitute for notation."

**Non-target**: The audit-section rules (lines 318-321) are non-derivable and kept.

---

### Target 2 — VRO shortcut: conclusion restatement (~90 chars)

Current last sentence of the shortcut block:
```
skipping EV and VRO for a new criterion introduced by HARD STOP is a protocol violation.
```

Already stated by the preceding clause:
```
a new criterion introduced by HARD STOP has no red VRO yet — EV and VRO must fire before impl_gate;
```

**Classification**: B — the prohibition restates the conditional. Once "EV and VRO must fire before impl_gate" is established, "skipping EV and VRO is a protocol violation" is derived from the protocol-violation definition applied to that requirement.

---

### Target 3 — HARD STOP valid-cases block: routing table restatements (~200 chars)

The HARD STOP valid-cases block (lines 382-387) lists failure-class routes:
```
all other failure classes have defined routes —
missing implementation file routes to EI directly;
test-interaction failure routes to EV repair;
implementation gap that changes between cycles loops within EI;
spec gap returns to formal notation;
using HARD STOP for any failure class other than criterion underspecification is a protocol violation.
```

The first two routes ("missing implementation file → EI directly" and "test-interaction failure → EV repair") now also appear in the compact routing table added by ADR-0215. The HARD STOP context adds: "these routes preclude HARD STOP." But the routing table header already states "all three block... HARD STOP is not valid" for harness errors, and the HARD STOP valid-cases block establishes that HARD STOP is only valid for criterion underspecification — making the two harness routes derivable from the conjunction.

**Classification**: B — the two harness routes in the HARD STOP block are derivable: routing table says harness errors block HARD STOP; valid-cases block says HARD STOP only valid for underspecification; models can derive the specific routes from the routing table.

**Keep**: "implementation gap that changes between cycles loops within EI" and "spec gap returns to formal notation" — non-derivable routes not in the routing table.

Additionally, lines 398-399 in the HARD STOP position gate:
```
the only valid next action when EV shows a harness error is a tool call that fixes the harness;
```
This restates the preceding clause ("HARD STOP may not be emitted at the executable validation rung — a harness error at EV requires fixing the harness, not an upward return") and the routing table. **Classification**: B.

---

### Target 4 — P1: "no other event" clause (~130 chars)

P1 contains:
```
no other event — inference, prediction, prior-cycle output, or any non-tool event — satisfies
any gate regardless of accuracy;
```

A1 already states: "only tool-executed events have evidential standing; inference, prediction, and prior knowledge have none, regardless of accuracy." A4 states: "evidence from a prior cycle... does not satisfy any gate regardless of type match."

**Classification**: A — "inference, prediction" restates A1; "prior-cycle output" is A4 applied; "any non-tool event" is A1's contrapositive. The non-derivable part of P1 — the cross-rung clause — is kept.

**Risk**: Models explicitly rationalize "I already produced output this cycle, does that satisfy a gate?" The cross-rung clause addresses this, but the broader "no other event" enumeration may provide additional friction against A1 violations in non-cross-rung contexts. **Disposition**: Downgrade to optional — defer to ADR-0217 if escape-route testing shows regression.

---

## Decision

Apply Targets 1, 2, and 3 (definite B classifications). Defer Target 4 (P1) pending escape-route testing.

### Change 1 — Remove formal notation natural-language restatement

**Remove** (~170 chars):
```
Natural language may appear as section labels but may not substitute for encoding a constraint
in notation — if a constraint can be stated in notation, it must be.
```

**Rationale**: Lines 315-317 already state this. Post-audit placement creates false appearance of a new rule.

### Change 2 — Remove VRO shortcut conclusion restatement

**Remove** (~90 chars):
```
skipping EV and VRO for a new criterion introduced by HARD STOP is a protocol violation.
```

**Rationale**: Derivable from "EV and VRO must fire before impl_gate" (preceding clause) plus the protocol-violation definition.

### Change 3 — Remove HARD STOP routing restatements

**Remove** from valid-cases block (~120 chars):
```
missing implementation file routes to EI directly;
test-interaction failure routes to EV repair;
```
**Keep**: "implementation gap that changes between cycles loops within EI; spec gap returns to formal notation;"

**Remove** from position gate (~80 chars):
```
the only valid next action when EV shows a harness error is a tool call that fixes the harness;
```

**Rationale**: Routing table (ADR-0215) covers harness error routes. HARD STOP position gate already states "a harness error at EV requires fixing the harness, not an upward return."

---

## Classification Audit

| Rule | Category | Disposition |
|---|---|---|
| Formal notation natural-language restatement (post-audit) | B — restates lines 315-317 | Remove |
| VRO shortcut "skipping EV and VRO is a protocol violation" | B — restates "EV and VRO must fire" clause | Remove |
| HARD STOP: "missing implementation file routes to EI directly" | B — routing table covers this | Remove |
| HARD STOP: "test-interaction failure routes to EV repair" | B — routing table covers this | Remove |
| HARD STOP position gate: "only valid next action is a tool call that fixes the harness" | B — restates prior clause | Remove |
| HARD STOP: "implementation gap loops within EI" | C — non-derivable | Keep |
| HARD STOP: "spec gap returns to formal notation" | C — non-derivable | Keep |
| P1 "no other event" clause | A — restates A1+A4 | Defer to ADR-0217 |

---

## Consequences

**Expected reduction**: ~460 chars (from 30,447 → ~29,990).

**Escape-route durability test**: After applying, run ground on 2–3 transcripts that previously triggered:
- Formal notation annotation-as-encoding (to confirm natural-language prohibition at lines 315-317 covers it)
- HARD STOP for harness error (to confirm routing table + position gate covers it without the explicit routes)
- VRO shortcut misapplication for new HARD STOP criterion (to confirm "EV and VRO must fire" clause covers it)

**Implementation**: Edit `GROUND_PARTS_MINIMAL["core"]` directly. Run `make axis-regenerate-apply`. Update tests for removed phrases following ADR-0215 pattern.
