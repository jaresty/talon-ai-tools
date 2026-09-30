# ADR-0085 Cycle 32 — stratified channel-bearing shuffle

**Date:** 2026-09-30 | single-evaluator | binary: fresh build from HEAD+edits

## Stratification (ADR-0085 channel-stratification rule)

Surveyed seeds 300-337 (38 seeds). 24 of 38 were channel-bearing. Selected 6 with
**distinct channels** and at least one method or form present, favouring channels thin
in the catalog. Channels drawn: presenterm, skill, video, html, code, remote.

## Scores

| Seed | Draw | Score | Note |
|---|---|---|---|
| 305 | sim + ration + thing + visual + presenterm | 4 | ration is distributive, not an absolute cap — a 12-slide deck can carry an allocation. No gap. |
| 314 | check + full + ghost + skill + dig | 2 | `skill` cautions `check` (correct). Second, independent collision: ghost (trace of actions taken) vs a skill spec (forward-looking). |
| 319 | pull + relay + narrow + jobs + story + video | 2 | `video` cautions `pull` (correct). |
| 321 | sim + audit + deep + lever + mapping + html + fip-ong | 3 | `html` cautions `sim` (correct). |
| 326 | show + relay + full + unknowns + bug + code | 4 (revised from 2) | Initially scored 2 on an apparent bug-vs-code prose collision. Falsification found the resolving rule already exists at metaPromptConfig.py:145 — the score was wrong, not the catalog. |
| 333 | plan + audit + full + assume + adversarial + remote + rog | 4 | `remote` is a delivery-mechanism channel; composes additively. Coherent. |

**Mean: 3.17/5 across 6 seeds, 6 of 6 channel-bearing.**

Per the ADR Risks entry, this mean is not evidence of progress at this sample size.
Reported with its channel-bearing count for comparability with c27/c28/c31 only.

## Corrections made during this cycle

1. **Seed 326 rescored 2 → 4.** The `bug`+`code` "collision" dissolved once the
   falsification step located `metaPromptConfig.py:145`. Recorded rather than quietly
   fixed, because the same reasoning error (reading a pairwise collision where an axis
   rule already governs) is the one this cycle's finding is about.
2. **"Cautionaries fired" was imprecise.** What fired was my reading of the config, not observed
   delivered text. I first claimed cautionaries were TUI-only; execution refuted that —
   `bar help llm --section heuristics` carries them and is agent-reachable. The accurate split is
   by role: the SELECTION paths (help llm heuristics, TUI) carry them; the EXECUTION paths
   (`bar build`, `bar help token`) do not. Since a shuffle draw arrives with tokens already
   chosen, no cautionary has ever guided a shuffle response. See c32-O1.
