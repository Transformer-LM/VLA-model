# Preliminary Idea Map: VLA × WAM Correction and Memory

**Date**: 2026-08-24  
**Status**: preliminary; not novelty-cleared; no pilots run

## Ranking

| Rank | Idea | Core gap | WAM role | Risk | 1–3 day kill-test |
|---:|---|---|---|---|---|
| 1 | Error Attribution Gate | prediction–reality mismatch may be WM error or robot failure | calibrated action-effect distribution and epistemic uncertainty | medium | construct matched execution-failure vs WM-shift pairs; test attribution over binary discrepancy |
| 2 | Pending Postcondition Memory | actions are marked complete before delayed/occluded effects are verified | create temporally scoped expected-effect obligations | medium | delayed-effect/occlusion tasks; compare pending obligations with immediate completion and fixed delay |
| 3 | Last-Correctable-Time Hazard | failure AUROC ignores whether detection is early enough to recover | roll out recovery feasibility and predict remaining rescue horizon | medium-high | oracle last-correctable-time trigger vs perfect late detector and fixed-early trigger |
| 4 | Recoverability Signature | failure type does not specify which recovery actions remain feasible | predict feasibility vector over a small recovery action library | medium-high | oracle feasibility vector vs oracle failure class/residual on held-out stage×failure pairs |
| 5 | Belief Update Firewall | recurrent belief can permanently absorb one bad observation or bad WM prediction | prior/posterior disagreement plus evidence-gated write/rollback | high | inject one corrupted observation; compare gated update, RSSM filtering, reset and raw recurrence |
| 6 | Memory-Semantics Router | recurrence transfers poorly when a new task requires a different memory rule | infer/select object, count, order, spatial or progress update operator | high | oracle memory-rule routing on held-out semantics; kill if no headroom over one recurrent state |
| 7 | Verify–Repair–Recover Factorial Audit | published gains entangle detection, state correction and added recovery data | WAM is one interchangeable verifier, not the whole system | low-medium | 2×2×2 learned/oracle component cross; estimate main effects and interactions |
| 8 | Policy–WAM Exploitation Stress Test | planner/VLA can choose actions that exploit WM blind spots | independent support/OOD monitor and adversarial candidate search | medium | optimize candidates only in WM; measure imagined–real ranking gap and support-aware shield benefit |

## Top 3

### 1. Error Attribution Gate

Build an action-conditioned task-latent model that predicts the distribution of expected object and robot effects. After execution, route mismatch into `execution failure`, `world-model uncertainty`, or `observation ambiguity`. Only the first corrects VLA task state or triggers recovery; the second abstains/updates the WM; the third requests evidence.

Closest work: CheckVLA and When to Trust Imagination detect mismatch but primarily use it to intervene; the proposed question is whether the mismatch is attributable to the robot or to the verifier itself.

### 2. Pending Postcondition Memory

Every action chunk creates a small set of expected postconditions with a valid time window. A task step remains `pending`, not completed, until evidence discharges the obligation. Missing, late or contradictory evidence updates progress differently. This is memory of unresolved action effects rather than raw frames or completed-step text.

Closest work: CheckVLA compares future and reality, KEMO stores event frames, RB-VLA stores an implicit belief. The narrow gap is asynchronous/delayed postcondition bookkeeping and its effect on premature progress commits.

### 3. Last-Correctable-Time Hazard

Use simulator rewind and a fixed recovery policy to label the last time at which a failure can still be rescued. Train a hazard head to predict whether one more VLA chunk will cross that boundary. Optimize correction lead time at a fixed intervention budget, not generic failure AUROC.

Closest work: early monitors and viability shields. Main risk: the label depends on the recovery policy and may not transfer.

## Suggested route

Start with Idea 1 if the user wants a genuine WAM-centric method. Start with Idea 7 if the user wants the fastest, least speculative diagnostic. Start with Idea 2 if the main motivation remains π0.5 long-horizon memory and false completion.

Do not combine the top three before each oracle test passes.
