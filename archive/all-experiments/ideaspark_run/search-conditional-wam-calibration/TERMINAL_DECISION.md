# Terminal Decision — Search-Conditional WAM Calibration

**Date:** 2026-08-31  
**Decision:** **ARCHIVE / NO-GO**  
**Strict novelty:** **6.90/10** (required: strictly greater than 7.0)  
**Naturalness:** **8.6/10**  
**Feasibility:** **7.8/10**

The failure mode is important: enlarging a WAM-guided candidate search can amplify optimistic model error, so the selected action may become worse in the real simulator even while its imagined score improves. However, the proposed solution does not clear the strict novelty gate.

The decisive objection is that a fixed end-to-end searcher can be treated as a single prediction algorithm. Ordinary split conformal risk control can calibrate its selected output while absorbing its internal optimization step. Budget/support conditioning, pessimistic score adjustment, abstention, and fallback then read as a natural combination of conformal selection/risk-control methods, pessimistic MBRL, DreamSteer-style WAM search, and the already-established WAM exploitation problem.

No full method training or GPU experiment is authorized for this formulation. A cached, non-GPU search-amplification premise audit remains scientifically useful as an evaluation asset, but it cannot validate the claimed novelty by itself.

Evidence:

- [CONCEPT_JURY.md](./CONCEPT_JURY.md)
- [NOVELTY_JURY.md](./NOVELTY_JURY.md)
