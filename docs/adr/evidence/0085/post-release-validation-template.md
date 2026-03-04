# Post-Release Validation Template

## Purpose
Verify that applied catalog changes are visible in the installed binary and resolve the original evidence cases.

## Procedure

When a recommendation is applied and a new bar release is made:

1. **Verify binary version**
   ```bash
   bar --version
   ```

2. **Check guidance is visible**
   ```bash
   bar help llm | grep -A 3 "<token-name>"
   ```

3. **Re-run evidence seeds**
   ```bash
   bar shuffle --seed <evidence-seed>
   ```

4. **Evaluate if issue is resolved**
   - Does the new guidance prevent the problematic combination?
   - Does the token behave as expected?

## Example

**Recommendation applied:** R36 - Add compound directional warning to skim token

**Verification:**
- Binary version: 2.75.0
- Guidance check: ✅ "Avoid pairing compound directionals with skim" present
- Evidence seed: seed 532 (skim + fly-ong)
- Pre-fix score: 2
- Post-fix assessment: Guidance now warns against this combination

**Result:** ✅ Resolved
