# Cycle 36 — followups

1. **Proposed ADR-0085 step: run the double-layer check BEFORE writing a cautionary**, not as a
   post-commit invariant. Five instances this week of writing a cautionary where a composition exists
   or a definition already resolves it; the check is one command and encodes the decision reliably.

2. **`blind` × `aloud`** (cycle 35 seed 602, one seed) — still open. Note the capacity clause added
   this cycle does NOT cover it: `aloud`'s problem is that speech has no stable referenceable label,
   not that it caps depth.

3. **`presenterm` + enumerating methods at `full`** (cycle 34, one seed) — still open.

4. **`falsify` semantic-red clause** — decision still open; my recommendation remains not to ship on
   one instance of my own misapplication.

5. **The eval on the form/channel axis rule** — still the highest-value unaddressed item. Four commits
   and 52×32 token pairs of behaviour, zero behavioural validation. Cycle 36 adds a second axis clause
   (topology capacity) with the same absence of evidence.

6. Carried: Python full-suite verification blocked by two pre-existing defects (nn 20260930174045-0290).
