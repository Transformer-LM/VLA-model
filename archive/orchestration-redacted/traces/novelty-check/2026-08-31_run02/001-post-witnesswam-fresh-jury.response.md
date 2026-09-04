# Raw fresh-jury return

## Verdict

**最终保留：0/15。** 所有候选均 KILL；没有候选同时满足 strict novelty lower bound `>7.0` 与 naturalness `>=7.0`。最高为 Actual-Cause VLA Post-Training，但区间仅 `[5.8,7.0]`，下界 5.8。

Jury 明确记录：arXiv API SSL EOF、Semantic Scholar 429；点名高威胁论文改用 official arXiv primary pages 核验，检索缺口只降低、不抬高 novelty 下界。

## Exact scores returned

| Candidate | Novelty interval | LB | Naturalness | Verdict |
|---|---:|---:|---:|---|
| Observation-Contingent Action Tree | [4.8, 6.3] | 4.8 | 8.6 | KILL |
| Low-Rank Within-Chunk Feedback Fields | [2.7, 4.0] | 2.7 | 8.8 | KILL |
| Minimal Physical Task-Repair VLA | [5.6, 7.0] | 5.6 | 8.2 | KILL |
| Counterfactual Infeasibility Certificates | [4.8, 6.4] | 4.8 | 7.4 | KILL |
| Causal Identity from Action-Effect Histories | [4.3, 5.8] | 4.3 | 7.8 | KILL |
| Intervention-Commuting Object Addresses | [2.1, 3.5] | 2.1 | 8.0 | KILL |
| Interventional Effect-Quotient Action Interface | [4.9, 6.5] | 4.9 | 7.6 | KILL |
| Predicate-Preservation Action Policies | [3.6, 5.0] | 3.6 | 8.7 | KILL |
| Compensable Action Chunks | [5.4, 6.8] | 5.4 | 9.0 | KILL |
| Task-Equivalent Recovery Targets | [3.9, 5.2] | 3.9 | 8.4 | KILL |
| Actual-Cause VLA Post-Training | [5.8, 7.0] | 5.8 | 8.1 | KILL |
| Search-Adversarial WAM Training | [2.0, 3.4] | 2.0 | 8.6 | KILL |
| Planner-Invariant Action Dominance | [5.0, 6.6] | 5.0 | 7.5 | KILL |
| Counterexample-Guided Plan Constraint Compilation | [2.5, 4.1] | 2.5 | 8.5 | KILL |
| Event-Surface Action Semantics | [4.0, 5.6] | 4.0 | 9.1 | KILL |

## Strongest primary-source threats returned

- A2C2 2509.23224: per-control-step observation-conditioned correction of a base VLA chunk.
- CheckVLA 2607.26789: action-conditioned WAM execution verification, risk triggering and suffix rewrite.
- DREAM-Chunk 2606.18589: multiple chunks, latent WAM rollout and observation-matched branch selection.
- Do What?/IVA 2508.16292: impossible-instruction detection, correction and actionable alternatives.
- OA-WAM 2605.06481: persistent object address, address-only routing, joint world/action interface and causal slot-intervention swap-binding test.
- Action-Effect Memory 2606.12499: action-conditioned visual-history state evolution for control.
- QuoVLA 2605.24890: quotient representation under identical optimal-action behavior.
- GEAR-VLA 2606.08530: latent actions, geometry-aware representation and embodiment canonicalization.
- PROWL 2605.18803: adversarial policy exposure of WAM high-error trajectories and continual WAM correction.
- Counterexample-Guided Repair 2105.06537: physical counterexamples repair symbolic-geometric action abstractions.
- RecoveryChaining 2410.13979: recovery to any state from which nominal controllers can finish.
- ReSYNC 2606.18328: failure/recovery experience revises relational abstractions and planning models.

## Strongest fatal objections returned

- Action tree is classical contingent policy-tree structure placed inside a VLA chunk.
- Feedback fields are A2C2 with a low-rank parameterization.
- Physical repair depends on a hand-designed edit cost/permission model and reduces to standard TAMP enabling actions.
- Infeasibility certificates use standard planning unsat cores and privileged predicates.
- Causal identity becomes active FDI if physical probes are used; without them symmetric identities remain unidentifiable.
- Commuting addresses are nearly a restatement of OA-WAM's intervention test.
- Effect quotient is a natural composition of QuoVLA, GEAR-VLA and action effects.
- Predicate preservation is classical STRIPS delete-effect / causal-link threat resolution.
- Compensable chunks are standard contingency/backup policy planning.
- Task-equivalent recovery is already the target semantics of RecoveryChaining.
- Actual-cause post-training cannot generally keep the later trajectory counterfactually fixed after replacing an earlier chunk.
- Search-adversarial WAM is strongly covered by PROWL.
- Robust partial-order pruning is standard Pareto/robust planning.
- Counterexample constraint compilation is directly covered by counterexample-guided repair + ReSYNC/CEGAR.
- Event-surface semantics is classical hybrid/options event termination under a VLA name.

**KEEP: none.**
