# P025-v5 cross-task gate result

Status: mechanism-feasibility gate passed; matched-baseline and WAM-harm claims remain pending.

## Registered scope

- Three frozen-StarVLA natural-success LIBERO-GOAL trajectories.
- Eight policy-supported action boundaries.
- ISRAC contact-subtraction selector, selector seed 0, at most three blocks per boundary.
- Three preregistered compliance endpoints per selected block and complete pairwise comparison.
- Every execution begins from a fresh seeded reset, applies the named benchmark initial state,
  and replays the wait actions plus the complete policy prefix before the candidate suffix.

## Observed result

- Eligible boundaries: 8 / 8.
- Selected and uniquely certified physical blocks: 18.
- Passing endpoint certificate pairs: 52.
- Replay-to-saved-boundary maximum error: 0 for every boundary.
- Nominal-repeat maximum error: 0 for every boundary.
- Independent formal verification: 8 / 8 manifests, all 18 blocks and all 52 pairs.
- Authenticated source transcripts: 17/11/10 policy chunks and 133/85/78 executed steps,
  depending on task trajectory.
- Adversarial audit: 10 / 10 tamper classes rejected, including raw pixels, contacts,
  initial proprioception, certificate measurements, non-target physics, source JSON hash,
  source success flag, source action chunks, benchmark initialization, and controller reset mode.

## Claim boundary

This shows that the influence-separated compiler can repeatedly construct auditable physical
twins on several tasks without target-WAM access. It does **not** yet show that ISRAC is more
efficient than candidate-contact or random-scene selection, nor that a held-out feedback WAM
makes a harmful decision on these twins. Those are the next two falsification gates.

## Remote evidence

- `<PERSONAL_RESEARCH_ROOT>/results/israc/P025V5_GATE_FORMAL_VERIFICATION.json`
- `<PERSONAL_RESEARCH_ROOT>/results/israc/P025V5_TAMPER_AUDIT_02/AUDIT.json`
- `<PERSONAL_RESEARCH_ROOT>/results/israc/P025V5_GATE_MASTER.log`
