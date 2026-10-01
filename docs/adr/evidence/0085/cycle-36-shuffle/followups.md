# Cycle 36 — followups

1. **DONE (2026-10-01):** the layer procedure gains **step 0 — look the pair up** before asking any of
   its four questions, implemented as `make pair-lookup PAIR="<a> <b>"`
   (`scripts/pair-lookup.py`). It reports whether a composition already ships, any cross-axis entry in
   either direction, whether either definition names the other token, and whether an axis description
   already governs the pair. Verified against this week's five instances: it flags `blind`+`skim`,
   `ghost`+`svg` and `faq`+`code` as having shipped compositions, and correctly reports none for
   `bug`+`code` and `audit`+`ledger`, which are genuine cautionary/axis cases. Run against
   `blind`+`skim` it prints "COMPOSITION EXISTS — a cautionary for this pair is wrong by construction"
   as its first line, which is what would have stopped cycle 36 before the first entry was written.

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
