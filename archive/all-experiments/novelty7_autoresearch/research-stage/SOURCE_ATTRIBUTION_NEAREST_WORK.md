# Source-Aware Verification: Nearest-Work Audit

**Cutoff**: 2026-08-30  
**Claim under test**: Similar WAM–reality residuals can have different causal sources and therefore require different robot interventions.

## Exact nearest works

| Work | What it actually does | Collision | Remaining delta |
|---|---|---|---|
| CheckVLA (2607.26789) | action-conditioned future verification, conformal first-intervention control, suffix repair, event memory | Very high | Risk head is scalar. Supplement manually labels residual failures and explicitly reports `world-model ambiguity` and unnecessary intervention, but does not learn source attribution or choose source-specific actions. |
| When to Trust Imagination (2605.06222) | future–reality consistency controls WAM execution horizon and replanning | Very high | All low consistency triggers replanning; perception noise, actuation error and contact uncertainty are acknowledged but not separated. |
| WAV (2604.01985) | verifies world-model predictions via state plausibility and action reachability; self-improves on underexplored actions | High | Diagnoses/improves the model in generated/subgoal space, not online attribution between actual execution failure, model error and observation ambiguity. |
| SC3-Eval (2606.18610) | forward–inverse, cross-view and test-time consistency for world-model policy simulation; terminates drifting simulated rollouts | High | Closest structural ancestor. It checks generated rollout self-consistency, not future prediction against a real execution observation, and has no source-specific controller decision. |
| Model-Based Runtime Monitoring (2310.17552) | separate human-intervention failure classifier and OOD detector for interactive imitation learning | High ancestor | Combines failure and OOD signals but does not construct residual-matched causal source pairs, does not distinguish predictor error from observation ambiguity, and does not use source to arbitrate repair/reobserve/distrust. |
| Foundational WM failure monitor (2603.06987) | uncertainty/conformal nonconformity detects bimanual anomalies | Medium | Detects anomalies, no source label or intervention differentiation. |
| FLARE (2608.26645) | retry/reset recovery data and an MLLM monitor for OOD state arbitration | Medium-high | Attributes policy state enough to select retry/reset, but does not audit WAM prediction error as a competing source and does not use action-conditioned expected future. |
| Robo-Dopamine 2.0 (2608.15680) | history/OOD-aware signed process reward, failure/recovery states | Medium | Robust progress reward, not discrepancy-source attribution. |
| GTP-FA (2606.03385) | attributes final manipulation failure to grasp versus motion-planning modules | Medium ancestor | Module-level post-failure attribution, not WAM/observation/execution discrimination during chunk execution. |
| Pose error attribution (2603.02881) | detect and attribute pose-estimation error sources, then target mitigation | Medium ancestor | Restricted to pose estimation; useful proof that source-specific mitigation matters. |

## Why a naive candidate would fail

The following are not novel enough:

1. concatenate WAM residual and ensemble uncertainty, then train three-class cross entropy;
2. place an OOD detector beside a failure detector;
3. use PointMap to improve failure classification;
4. rename low confidence as model uncertainty;
5. report only attribution accuracy without controller harm/rescue outcomes.

These collapse into CheckVLA + Runtime Monitoring + WAV/SC3-Eval.

## Defensible problem formulation

Construct **residual-matched counterfactual triplets** from the same pre-state and commanded action:

- `E`: perturb the realized environment/action effect so the relation genuinely fails;
- `M`: keep the task-relevant physical effect correct while applying a held-out WAM misspecification/nuisance that makes its predicted future wrong;
- `O`: preserve hidden physical state but make the observation insufficient or inconsistent.

Match or stratify the scalar WAM residual so thresholding cannot solve the task. The target is not cause naming by itself; it is the optimal intervention under the same apparent mismatch:

- `E -> repair/replan`;
- `M -> continue with an independent state check; distrust or update WAM`;
- `O -> reobserve/change view/wait`.

The model should factor evidence rather than only classify pixels:

1. forward action-effect consistency;
2. inverse action reachability / commanded-versus-realized effect consistency;
3. model support or epistemic disagreement;
4. cross-view/geometry observability.

## Claim ceiling before experiments

Potential claim:

> Scalar future–reality verification conflates execution, model and observation failures; counterfactually source-aware arbitration reduces harmful interventions under held-out perturbation families.

Not yet claimable:

- absolute robot safety;
- reliable attribution in arbitrary open-world conditions;
- real-robot benefit;
- WAM necessity if a direct current-state geometry checker matches performance.

## Provisional novelty before independent review

- Problem/benchmark novelty: `7.7/10`.
- Mechanism novelty: `7.1/10` because WAV and SC3-Eval provide forward–inverse/self-consistency ancestors.
- Combined paper-shape estimate: `7.3–7.6/10` if residual matching and decision regret are executed; `<=6.5` if reduced to a classifier.
