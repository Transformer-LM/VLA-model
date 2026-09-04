# WitnessWAM v4 Round 5 Blocker Micro-Verification

**Date:** 2026-08-31  
**Scope:** denominator blocker only  
**Verdict:** **READY**

## Verification

The sole Round-5 blocker is resolved consistently:

1. `D_attempt` is unambiguous: all four fixed-key attempts for every physically valid, exactly replayable, time-zero-ambiguous common parent. No key is replaced. Agreement, safety, or envelope rejection is recorded as contract-coverage failure rather than a relation outcome.
2. `D_contract` is unambiguous: the subset passing paired action agreement, five-step safety, and the command-only envelope.
3. Contract coverage is explicitly `|D_contract| / |D_attempt| ≥ 60%` per retained family, preventing a narrow contract from hiding poor applicability.
4. Truth preservation and delayed-opportunity yield both use `D_contract` as denominator. Truth transitions remain preservation violations, yield failures, and system failures. Censored attempts remain delayed-yield failures.
5. Only truth-preserving `D_contract` attempts supervise `tau_protocol`; this does not alter the gate denominator.
6. K-prefix necessity requires at least three of four keys in `D_contract`; invalid/missing keys remain recorded and are never replaced.
7. Confidence intervals resample common-parent lineages, so the four key attempts are never treated as independent.
8. Sections 1, 3, 6, and Frozen stop gates 3–5 now use the same definitions; the previous contradiction is gone.

## Final decision

**READY.** No reading-robust proposal blocker remains. The prior overall score of **9.3/10** remains applicable. Whether contract coverage, preservation, delayed-witness yield, visibility/history comparisons, and action-conditioning gates pass is now a preregistered E0 falsification risk rather than a method-definition gap.

