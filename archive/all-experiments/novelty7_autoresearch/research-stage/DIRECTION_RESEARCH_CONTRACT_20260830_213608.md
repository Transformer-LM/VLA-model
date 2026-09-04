# Direction Research Contract

**Run**: `20260830-source-aware-verification`  
**Direction**: source-aware VLA×WAM verification and counterfactual causal evaluation  
**Scope**: research only; no paper writing; no live robot motion.

## Frozen problem

An action-conditioned WAM predicts how the scene should change during a VLA action chunk. Existing execution verifiers usually convert future–reality mismatch into one trust/risk score. This run tests whether a useful robot must instead distinguish:

1. **execution failure** — the intended physical effect did not occur or was lost;
2. **WAM misspecification/out-of-support** — the action outcome is acceptable but the predictor was wrong;
3. **observation ambiguity** — the evidence is insufficient because of occlusion, view loss, or association failure.

The classes are meaningful only if they change the controller decision: `repair/replan`, `reobserve/wait`, or `distrust/update/ignore WAM residual`.

## Allowed observations

- RGB and RGB-D;
- PointMap or learned 3D geometry;
- proprioception, joint/end-effector and gripper execution traces;
- commanded/executed actions and language;
- simulator ground truth only for labels, oracles and audit, never as a deployed input.

No tactile or force sensor may be required.

## Nearest-work hard comparisons

- CheckVLA (2607.26789): action-conditioned execution verification and conformal intervention;
- When to Trust Imagination (2605.06222): future–reality consistency for adaptive WAM chunking;
- WAV (2604.01985): world-model self-verification by plausibility/reachability;
- Model-Based Runtime Monitoring (2310.17552): separate failure and OOD detectors;
- GTP-FA (2606.03385): grasp-versus-planning failure attribution;
- pose-estimation error attribution (2603.02881).

A candidate fails novelty if it reduces to concatenating failure and OOD scores, generic uncertainty, or a three-class classifier without counterfactual identification and decision-dependent evaluation.

## Candidate and novelty gate

- Generate multiple structural formulations, not naming variants.
- Exact novelty and reviewer score must be strictly `> 7.0/10`.
- The score must be accompanied by the closest competing mechanism and a falsifiable difference.
- If the gate fails, pivot to functional-geometry HOW or physical infeasibility; do not inflate the score.

## Minimum experiment logic

1. Create paired interventions from the same pre-state and command.
2. Match or stratify raw future–reality residual magnitude across sources.
3. Hold out perturbation families, task families and nuisance shifts.
4. Compare scalar mismatch, failure+OOD, WAM uncertainty, direct geometry, and source-aware variants under matched data/parameters/latency.
5. Primary evidence is intervention regret and final task outcome, not only attribution accuracy.
6. Require an oracle policy-action headroom gate before training a large WAM.

## Compute and safety

- SSH only as `liu_meng`; read/write only `<PERSONAL_RESEARCH_ROOT>`.
- No root/sudo/su, `.bashrc`, system CUDA, global Conda or shared directory changes.
- GPUs 0–3 may be used only after a fresh per-GPU process/memory check; never share or preempt.
- GPU is preferred for neural representation/training; CPU only for orchestration and small audits.
- No paid compute, private upload, or live robot action.

## Stop rules

- Oracle source label cannot reduce harmful intervention by at least 10% relative or 5 percentage points absolute: stop.
- Residual-matched source classes are not distinguishable above matched baselines: stop or publish only a negative benchmark result.
- A direct current-state geometry checker matches the full action-conditioned method: drop the WAM necessity claim.
- Gains disappear outside simulator privileged masks/poses: do not claim deployable benefit.
- Independent novelty score is `<=7.0`: pivot before full training.
