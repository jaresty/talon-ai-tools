# Fix Closure Tracking

## Purpose
Track implementation status of ADR-0085 recommendations across cycles.

## Tracking Table

| ID | Cycle | Action | Token/Axis | Priority | Status | Last Seen | Notes |
|----|-------|--------|------------|----------|--------|-----------|-------|
| R36 | 11 | guidance | gist/skim + compound dirs | P1 | ✅ Implemented | Cycle 21 | In binary; 0 hits this cycle |
| R40 | 17 | tracking | shellscript + task | P1 | 🔄 Deferred | Cycle 21 | R41-grammar-hardening pending; no new data points cycle 21 |
| R41 | 19 | tracking | cross-axis enforcement | P1 | 🔄 Deferred | Cycle 20 | Schema work required |
| R42 | 21 | tracking | slack + max-compound directional | P3 | ⏳ Open | Cycle 21 | 1 data point (seed 671); observe cycle 22 |
| dim-retire | 1 | retire | dimension method | P2 | ✅ Closed | Cycle 21 | distinction-check: distinguishable — retain; original signal was name-similarity only |
| conv-retire | 1 | retire | converge method | P2 | ✅ Closed | Cycle 21 | distinction-check: distinguishable — retain; directional opposite of dimension |
| gherkin-edit | 1 | edit | gherkin channel | P0 | ✅ Resolved | Cycle 21 | Description evolved; verified in 2.102.0 |
| plain-edit | 1 | edit | plain channel | P0 | ✅ Resolved | Cycle 21 | Description evolved; verified in 2.102.0 |
| diagram-edit | 1 | edit | diagram channel | P0 | ✅ Resolved | Cycle 21 | Description evolved; verified in 2.102.0 |
| socratic-edit | 1 | edit | socratic form | P1 | ✅ Resolved | Cycle 21 | Description evolved; verified in 2.102.0 |
| announce-edit | 1 | edit | announce intent | P1 | ✅ Resolved | Cycle 21 | Description evolved; verified in 2.102.0 |
| entertain-edit | 1 | edit | entertain intent | P1 | ✅ Retired | Cycle 21 | Token no longer in catalog |
| presenterm-P3 | 20 | edit | presenterm channel | P3 | ⏳ Open | Cycle 20 | New from cycle 20 |
| probe-sim-brevity | 21 | edit | bar help llm heuristics | P2 | ✅ Implemented | Cycle 21 | "Choosing Completeness" section added to help_llm.go; build verified |

## Status Legend
- ✅ **Implemented**: Applied and verified in binary
- 🔄 **Deferred**: Known issue, awaiting future work
- ⏳ **Open**: Not yet addressed
- ❌ **Rejected**: Decision made not to implement
- ⚠️ **Reopened**: Previously implemented, issue recurred

## Update Log
- **2026-03-03**: Created tracking table for cycle 20
- **2026-03-13**: Cycle 21 — closed 5 P0/P1 description edits (resolved by evolution), retired entertain, added R42 (slack+fip-bog), added probe-sim-brevity heuristic gap
