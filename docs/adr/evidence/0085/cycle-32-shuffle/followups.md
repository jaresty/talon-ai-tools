# Cycle 32 — followups

1. **RESOLVED (same session).** The question as posed rested on a false premise: cautionaries are not
   TUI-only. `bar help llm --section heuristics` carries them and is agent-reachable. The real split is
   by role — SELECTION paths carry them, EXECUTION paths (`bar build`, `bar help token`) do not — which
   is correct by design. Option (b) is rejected: injecting a cautionary into a build prompt tells the
   model it should have picked different tokens when the tokens are already fixed. Recorded as an
   ADR-0085 scoring rule instead: a cautioned pair in a shuffle draw was never guided, so its low score
   is not evidence about the catalog. See c32-O1.

2. **Two independent seeds still unactioned:** ghost+skill (seed 314) — ghost traces actions
   taken, a skill spec is forward-looking. The constructor-channel cautionary on `skill` already
   covers the `check` task in that draw, so the ghost interaction has one seed, not two. Held
   below the two-seed action bar.

3. **The 44 forms with no channel-specific mapping** now inherit the general axis rule. Whether any
   of them warrant a specific construct mapping (as axiom/ontology/taxonomy have) is a question the
   general rule now makes answerable per-form, but no seed has demanded one yet.

4. Still open from prior cycles: golden-output test for the TOKENS block (nn 20260930174101-2067);
   the Python suite's pipe-read hang and telemetry-marker failure (nn 20260930174045-0290).
