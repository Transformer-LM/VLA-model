# E0 result-to-claim verdict

- claim_supported: no
- integrity_status: warn
- routing_action: repair
- confidence: high
- review_independence: same-family
- acceptance_status: provisional

## What the evidence supports

- The controlled E0/B0 dataset and exact 60-run v2 grid completed.
- Under the current feature/training design, PointMap performs worse than complete Depth on held-family macro-F1 and invalidation miss rate.
- PointMap has a much smaller registered head input and lower head-only latency, excluding sensing, association and projection.
- The learned Oracle fails under held-family shift; the current E0 is therefore not a valid representation-headroom test.

## What it does not support

- PointMap as a Depth substitute.
- Intrinsic inferiority of PointMap.
- Any realized-action-trace, WAM, VLA, recovery or closed-loop claim.

## Revised claim

> On five controlled LIBERO task definitions, the registered E0/G0 diagnostic completed but failed Oracle sanity and PointMap-vs-Depth gates. The current PointMap head is tensor-efficient, but PointMap representation headroom remains unestablished; no action-conditioned WAM conclusion follows.

## Required route

1. Add and save a deterministic invariant Oracle probe.
2. Repair the learned Oracle with task-invariant relative features and saved validation traces.
3. Add cheap invariant direct/linear probes for PointMap and Depth.
4. Correct the registered cluster-bootstrap CI implementation.
5. If those sanity checks pass, rerun the complete matched four-modality grid under a new shared hash.
6. Start E1/B2 only after repaired G0 passes.

The negative E0 result does not test or falsify the main realized-trace-conditioned WAM novelty claim; it only blocks its current PointMap substrate.
