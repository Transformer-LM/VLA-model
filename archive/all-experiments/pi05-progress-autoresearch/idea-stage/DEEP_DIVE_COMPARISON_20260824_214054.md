# Deep Dive Comparison: Attribution versus WAM Exploitation

**Date:** 2026-08-24  
**Status:** provisional comparison; no pilot run

| Question | Idea A: attribution-conditioned intervention | Idea B: search-conditioned exploitation |
|---|---|---|
| system stage | after an action is physically executed | before execution, during candidate selection |
| core failure | mismatch is assigned to the wrong cause | search selects a favorable WAM error |
| strongest artifact | matched-cause benchmark plus routing method | inference-scaling audit plus search-conditioned calibration |
| dependence on pi0.5 | low; pi0.5 can remain frozen | medium; requires diverse action-chunk sampling |
| dependence on a strong WAM | moderate | high |
| closest collisions | CheckVLA, Foresight, WAV, uncertainty monitors | exploitation theory, RENEW, PROWL, DREAM-Chunk, tau0-WM |
| present novelty outlook | better | weaker and more fragile |
| cheapest decisive test | matched residual attribution | candidate-count exploitation curve |

## Recommendation

Prioritize Idea A as the main candidate and use Idea B as a short finding-first audit. Do not merge them now.

They can form a later two-stage system only if both independent premises pass:

1. before execution, search-conditioned risk prevents choosing WAM-favored artifacts;
2. after execution, attribution-conditioned routing decides whether the remaining mismatch is physical, model-side, or perceptual.

Merging before those tests would create a large safety architecture with no isolated mechanism claim.

## Proposed run order

1. **A0 matched-cause identifiability test.** This is the most relevant to the user's pi0.5 long-horizon correction problem.
2. **B0 cached-candidate scaling audit.** It is cheap and can kill the broad exploitation route without training.
3. Continue only the route whose phenomenon is both strong and not explained by a simpler baseline.

