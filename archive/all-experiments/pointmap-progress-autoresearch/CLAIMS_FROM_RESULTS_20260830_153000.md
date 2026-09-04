# Claims from E0/G0 v3 results

Timestamp: 2026-08-30 15:30 +08:00  
Claim supported: **yes, only for the narrow controlled E0 headroom claim**  
Integrity: **WARN**  
Routing: **confirm E0; conditionally advance to E1/B2**  
Confidence: **high** (same-family review remains provisional)

## Supported claim

On 360 controlled LIBERO simulator samples using simulator instance masks and metric depth, the repaired 38-D object-relative PointMap representation passes all five frozen E0/G0 point-estimate gates. Learned Oracle sanity passes; PointMap retains strong cross-family relation-event signal with a much smaller verifier input tensor than complete Depth.

Key evidence:

- Oracle macro-F1 `0.9532`, achieved test FRR `0.0367`.
- PointMap macro-F1 `0.9002`, IMR `0.1222`, achieved FRR `0.0422`.
- Complete Depth macro-F1 `0.6487`, IMR `0.3556`.
- PointMap-minus-Depth macro-F1 `+0.2514`, task-family bootstrap 95% CI `[+0.0315,+0.4677]`.
- PointMap input tensor `152` bytes versus complete Depth `442,368` bytes; this excludes sensing, association and PointMap projection.

## Unsupported claims

E0 does not test or support realized action/kinematic trace value, action-conditioned counterfactual dynamics, WAM necessity or novelty, VLA improvement, task-memory correction, recovery, closed-loop success, learned/deployed masks, real-robot behavior, sim-to-real, or a universal claim that PointMap replaces Depth. PointMap is not uniformly better on every task family, and the paired IMR interval crosses zero.

## Integrity warnings that must travel with the claim

1. Legacy R011 does not bind the current geometry dependency; R025, not R011, is the exact current 38-D projection evidence.
2. The unselected no-retract sentinel is NumPy scalar-promotion sensitive; accepted selected thresholds and metrics are unchanged.
3. The global `min_epochs=20` floor was not explicitly registered and changes a small subset of RGB/Depth checkpoints, though no PointMap/Oracle checkpoint and no G0 conclusion changes.

## Conditional authorization for E1/B2

E1/B2 may begin because exact G0 passes, but only after:

- replacing the sentinel with a dtype-stable true no-retract candidate and testing exact threshold replay;
- freezing one explicit training/early-stopping protocol for every E1 variant;
- retaining all three E0 WARNs in provenance;
- keeping E0's 38-D two-frame diagnostic separate from the proposal's 54-D pre-action PointMap transition input.

No E0 grid rerun is required. The main realized-kinematic novelty remains untested; E1/B2 is the first experiment that can support or falsify it.
