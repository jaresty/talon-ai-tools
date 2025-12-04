## 2025-12-04 – Slice: add method/style tokens and retire axis-shaped static prompts

**ADR focus**: 013 – Static Prompt Axis Refinement and Streamlining  
**Loop goal**: Implement the first concrete slice of ADR 013 by moving several axis-shaped static prompts fully into the method/style axes and updating patterns to avoid them.

### Summary of this loop

- Extended axis vocabularies:
  - `GPT/lists/methodModifier.talon-list`:
    - Added `structure`, `flow`, `compare`, `motifs`, `wasinawa` with descriptions that mirror the original static prompt intents.
  - `GPT/lists/styleModifier.talon-list`:
    - Added `taxonomy` as a style for type/taxonomy-like outputs.
- Updated patterns:
  - `lib/modelPatternGUI.py`:
    - Changed the "Explain flow" pattern from `recipe="flow · gist · focus · steps · fog"` to `recipe="describe · gist · focus · flow · fog"`, so it now uses the new `flow` method modifier instead of the `flow` static prompt.
- Retired several axis-shaped static prompts:
  - `lib/staticPromptConfig.py`:
    - Removed profile entries for `structure`, `flow`, `relation`, `type`, `compare`, `clusters`, `experiment`, `science`, and `wasinawa` so they are no longer profiled static prompts.
  - `GPT/lists/staticPrompt.talon-list`:
    - Removed `structure`, `flow`, `relation`, `type`, `compare`, `clusters`, and `motifs` from the “Analysis, Structure, and Perspective” section.
    - Left the filter-style prompts (`pain`, `question`, `relevant`, `misunderstood`, `risky`) and reflection prompts (`wasinawa`, `experiment`, `science`) in place as static prompts for now; their semantics now lean more heavily on the new method tokens but remain discoverable as names.

### Behaviour impact

- New method/style tokens are now available to users and patterns:
  - Commands like `model describe structure fog`, `model describe flow rog`, `model describe compare rog`, or `model describe type taxonomy rog` can now be expressed directly via the method/style axes instead of relying on dedicated static prompts.
- The "Explain flow" pattern no longer depends on the `flow` static prompt:
  - It uses `staticPrompt="describe"` + `methodModifier="flow"`, aligned with ADR 013’s goal of separating “what” from “how”.
- Retiring static prompt profiles for `structure`, `flow`, `relation`, `type`, `compare`, `clusters`, `experiment`, `science`, and removing some of their tokens reduces static prompt surface area:
  - Any previous behaviour that used these prompts should now be expressed via the new method/style modifiers (or through patterns that embed them).

### Notes and follow-ups

- Future ADR 013 slices should:
  - Decide, case by case, whether remaining static prompts like `wasinawa`, `pain`, `question`, `relevant`, `misunderstood`, `risky`, `experiment`, and `science` should be fully retired in favour of axis tokens and pattern recipes, or kept as named recipes.
  - Update docs/help (for example, ADR 005/007/012/013 and `GPT/readme.md`) to:
    - Mention the new method/style tokens explicitly.
    - Show axis-first examples using `structure`, `flow`, `compare`, `motifs`, and `taxonomy` styles.

