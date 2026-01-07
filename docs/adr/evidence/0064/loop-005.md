## loop-005 analysis
- Observed that ADR 0064 no longer reflected the outstanding gaps raised during review:
  - No shared hydration helper was documented even though the implementation relies on ad-hoc quick-help changes.
  - Passive guard semantics were described in prior loops, but the ADR never called out the requirement to keep `close_common_overlays(..., passive=True)` side-effect free or to maintain drop-reason cleanup when suppression flags are active.
- Updated the ADR decision and implementation plan to capture these missing commitments so subsequent loops can deliver them.
