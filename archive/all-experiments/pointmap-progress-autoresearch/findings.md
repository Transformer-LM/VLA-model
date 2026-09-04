# Research Findings

## 2026-08-30 — E0/G0 negative result and repair route

- Tested: object-addressed RGB, complete Depth, sparse PointMap and simulator-pose Oracle on five held task families, three model seeds per fold.
- Result: the registered G0 gate failed four of five conditions. Only the PointMap input-size condition passed.
- Integrity: no fabricated GT, score self-normalization, phantom result or invalid-v1 contamination. Audit status remains WARN because full simulator replay provenance and validation threshold traces are incomplete.
- Verified failure mechanism: the learned Oracle uses non-invariant absolute pose/quaternion/raw visibility features. Training-family normalization produces extreme held-family feature shift and majority-class collapse even though an invariant rule reaches 359/360.
- Additional statistical defect: aggregation uses a five-fold t interval instead of the registered cluster-bootstrap CI.
- What not to repeat: do not rerun the same raw Oracle features, do not tune only learning rate/patience, do not advance to E1 from the current G0, and do not claim PointMap substitutes for Depth.
- Structural repair: invariant relative geometry, deterministic Oracle probe, explicit invariant representation probes, saved validation/threshold traces, corrected bootstrap protocol, then one matched fresh-hash rerun.
- Main novelty status: realized-kinematic-trace conditional value remains untested, not falsified.
## 2026-08-30 E0 v3 repair outcome

The task-invariant repair reversed the unusable v2 substrate result. Exact G0 now passes with integrity WARN: PointMap macro-F1 0.9002, IMR 0.1222 and FRR 0.0422 versus complete Depth macro-F1 0.6487 and IMR 0.3556. The result supports only controlled simulator-mask representation headroom. It does not test the proposed realized-kinematic transition value. Result-to-claim authorizes E1/B2 after a dtype-stable threshold sentinel, a frozen E1 training protocol, and explicit separation of E0 38-D diagnostics from the E1 54-D transition state.
