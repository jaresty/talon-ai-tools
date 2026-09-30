# Cycle 32 — followups

1. **Decide whether cross-axis cautionaries should reach the `bar build` path.** (from c32-O1)
   Today they render only in the interactive TUI. 135 cautionary entries guide human token
   selection and constrain no agent. Options: (a) leave as TUI-only and say so in ADR-0085 so
   future cycles stop scoring them as delivered; (b) render active cautionaries into the build
   prompt; (c) split the layer explicitly. Needs a deliberate choice.

2. **Two independent seeds still unactioned:** ghost+skill (seed 314) — ghost traces actions
   taken, a skill spec is forward-looking. The constructor-channel cautionary on `skill` already
   covers the `check` task in that draw, so the ghost interaction has one seed, not two. Held
   below the two-seed action bar.

3. **The 44 forms with no channel-specific mapping** now inherit the general axis rule. Whether any
   of them warrant a specific construct mapping (as axiom/ontology/taxonomy have) is a question the
   general rule now makes answerable per-form, but no seed has demanded one yet.

4. Still open from prior cycles: golden-output test for the TOKENS block (nn 20260930174101-2067);
   the Python suite's pipe-read hang and telemetry-marker failure (nn 20260930174045-0290).
