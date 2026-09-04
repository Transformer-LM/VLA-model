# Terminal Decision — Active Causal Discrepancy Diagnosis

**Date:** 2026-08-31  
**Decision:** **ARCHIVE / NO-GO**  
**Strict novelty:** **6.90/10** (required: strictly greater than 7.0)

The problem is real: a WAM–observation discrepancy can come from execution failure, WAM misspecification, or ambiguous perception, and the wrong diagnosis can corrupt long-horizon task memory. However, the proposed mechanism—hypothesis-specific outcome models, information-gain diagnostic actions under task cost, and a Bayesian posterior update—has a near-direct prior in counterfactual active fault diagnosis (arXiv:2509.18460), with safe active fault estimation additionally covered by s-FEAST.

The remaining VLA×WAM-specific contribution is a matched-residual benchmark and the downstream memory-integrity consequence. That is useful, but it does not clear the requested method-novelty gate. The deterministic routing rules `model failure -> preserve progress` and `perception ambiguity -> do not retract` are also not causally sufficient.

No dataset compiler, CPU pilot, or GPU experiment is authorized for this formulation. The matched-residual evaluation protocol may be reused only inside a materially different future method.

Primary evidence: [NOVELTY_JURY.md](./NOVELTY_JURY.md).
