# Independent Novelty Jury: GISS-2x2

**Review date:** 2026-08-31  
**Candidate:** Geometry-Induced Skill-Graph Shift (GISS-2x2)  
**Exact claim under review:** *A matched-state current-action compatibility diagnostic under visible functional-geometry changes.*

## Verdict

**Novelty: 6.7/10 — FAIL.** The strict bar is **greater than 7.0**; 7.0 itself would still fail. The candidate does not clear that bar.

**Naturalness / problem value: 7.5/10.** The problem is real and useful: ordinary task success and uncontrolled paired trials do not isolate whether a frozen VLA's current action is adapted to visible, action-relevant geometry. The proposed assay is interpretable and potentially diagnostic. Its naturalness is reduced by the need to engineer endpoint-equivalent geometry pairs, serialize all non-geometry simulator state, reset policy history/cache/seed, and define a common pre-contact state. These constraints can make the benchmark narrow and may systematically omit the contact-rich states where functional geometry matters most.

**Scoop classification: Level 2 — High Overlap.** The general diagnostic framing is occupied by metamorphic testing of VLAs, while the matched-state paired-policy-response component is occupied by counterfactual action-sensitivity auditing. GISS retains a specific unoccupied-looking composition—four-cell action-source-by-recipient-geometry cross-execution with native success—but that delta is narrower than a new evaluation paradigm.

**Decision: FAIL / NO-GO. Do not launch GPU experiments.** At this score, the candidate should not consume the proposed pi0.5/CLOVER GPU budget. A later reconsideration would require a demonstrably unoccupied claim or a substantially different scientific question, not merely a larger implementation.

## Claim boundary used for this review

The defensible claim is only:

> Given two visible, endpoint-equivalent functional geometries and an otherwise matched simulator and policy-inference state, query one current native action chunk from each geometry, cross-execute both chunks in both recipient geometries, and measure the symmetric own-source-versus-cross-source native-success interaction.

The claim is **not** a VLA or WAM training method; not proof of full functional-geometry understanding; not strategy identification; not action necessity; not global skill-graph recovery; not real-world transfer; and not evidence that a geometry-specific action is uniquely optimal. Keeping this boundary narrow prevents overclaiming, but it also exposes how little novelty remains after the closest prior work is accounted for.

## Mechanism decomposition

The proposed diagnostic has four load-bearing operations:

1. Construct visible geometry variants A/B that preserve instruction, terminal goal, and all non-geometry state while changing action-relevant collision geometry.
2. Restore a common pre-contact state and fresh, matched policy inference context; obtain chunks \(u_A\) and \(u_B\) from the two source observations.
3. Execute the four source-chunk × recipient-geometry cells, then allow a fresh closed-loop continuation in the recipient environment.
4. Report the interaction
   \[
   I_{MS}=\tfrac12[(Y_{AA}-Y_{AB})+(Y_{BB}-Y_{BA})],
   \]
   with appearance-only, identical-render, and state-jitter controls.

The fourth operation is the clearest remaining novelty. Operations 1–2 are close to existing paired/counterfactual VLA diagnostics; the broader metamorphic rationale is already explicit in prior work.

## Closest exact mechanism

The closest single paper is **Metamorphic Testing of Vision–Language Action–Enabled Robots** ([arXiv:2602.22579](https://arxiv.org/abs/2602.22579), primary full text inspected). It already treats VLA evaluation as source/follow-up test construction under controlled input or environment transformations, specifies when trajectories should remain consistent or vary, fixes the simulator seed, measures behavioral trajectory differences, and shows that behavior-level metamorphic checks expose failures that endpoint symbolic success can miss. Its trajectory-variation relation for target relocation is particularly close: the robot should alter its motion in response to a meaningful spatial change.

GISS differs in three precise ways: the treatment is functional collision geometry rather than target relocation; the unit under test is the current native action chunk at a matched state rather than an entire paired rollout; and the outcome is a four-cell cross-execution success interaction rather than paired trajectory distance. Those differences are technically meaningful, but they resemble a new metamorphic relation plus a stronger causal execution protocol—not an entirely new diagnostic principle.

The closest component-level composition is:

- **Metamorphic Testing** for the controlled-transformation VLA diagnostic and expectation of behavior change under relevant perturbations.
- **It's Not Just More Demos: Counterfactual Action Sensitivity Coverage for Data-Efficient Robust Robot Imitation** ([arXiv:2607.27261](https://arxiv.org/abs/2607.27261), primary full text inspected) for paired observations at the same underlying task/robot state and direct auditing of policy action sensitivity.

## Mandatory high-threat comparison: CASC versus GISS

| Dimension | Counterfactual Action Sensitivity Coverage | GISS-2x2 |
|---|---|---|
| Treatment semantics | The visual change is an **irrelevant nuisance**; the expert action should be preserved. | The visible functional geometry is **action relevant**; a useful current action may need to change. |
| Matched quantity | Clean and nuisance observations share the underlying task/robot state. | Geometry A/B share the non-geometry simulator state and policy-inference context. |
| Policy measurement | Normalized offline drift between predicted actions. | Two source action chunks crossed into two recipient geometries. |
| Desired response | Invariance to the nuisance. | Geometry-conditioned compatibility, expressed as an own-source advantage in both recipients. |
| Outcome | Offline action drift; no rollout is required. | Native downstream success in a matched-state 2×2 execution assay. |
| Known limitation relevant here | Local action drift can miss delayed/closed-loop errors, and large drift can reflect valid alternative actions. | Native success addresses some local-drift ambiguity, but continuation policy, decoder stochasticity, and state tolerance can dilute attribution. |

Thus CASC does **not** exactly implement GISS: its treatment semantics are opposite and its outcome is offline drift. It nevertheless occupies the matched-state paired action-response audit. Together with metamorphic testing, it makes the GISS composition look incremental.

## Primary-source collision matrix

| Work | Primary mechanism | Overlap with the exact claim | Threat |
|---|---|---|---|
| [Metamorphic Testing of Vision–Language Action–Enabled Robots, 2602.22579](https://arxiv.org/abs/2602.22579) | Controlled source/follow-up tests; trajectory consistency/variation relations; fixed-seed paired execution; Fréchet trajectory comparison plus task success | Same VLA diagnostic framing, controlled meaningful environment transformation, and behavior-level oracle beyond endpoint success; lacks current-chunk cross-execution 2×2 | **Very high** |
| [It's Not Just More Demos, 2607.27261](https://arxiv.org/abs/2607.27261) | Same-state clean/nuisance pairs; policy action drift; targeted data repair | Same-state paired policy-response audit; different invariance semantics and no execution crossover | **High** |
| [When Vision Overrides Language / LIBERO-CF, 2602.17659](https://arxiv.org/abs/2602.17659) | Counterfactual instructions in visually plausible scenes; action grounding diagnostics | Shares controlled counterfactual VLA testing and native success, but not geometry treatment or action crossover | Medium |
| [GemBench, 2410.01345](https://arxiv.org/abs/2410.01345) | Geometry-focused manipulation benchmark spanning placements, rigid shapes, articulated objects, and long-horizon tasks | Shares geometry-generalization problem and task success; no matched checkpoint or crossed current actions | Medium |
| [RADAR, 2602.10980](https://arxiv.org/abs/2602.10980) | Benchmarking spatial/physical intelligence and dynamics with autonomous 3D metrics | Functional/spatial diagnosis only; no matched-state action-source arbitration | Low–medium |
| [AffordanceVLA, 2606.06155](https://arxiv.org/abs/2606.06155) | Which2Act/Where2Act/How2Act affordance decomposition for policy learning | Geometry/affordance relevance, but it is a training architecture rather than an evaluation assay | Low–medium |
| [GEAR-VLA, 2606.08530](https://arxiv.org/abs/2606.08530) | Geometry-aware action representation and 3D/canonical alignment | Geometry-conditioned policy learning, not matched-state diagnosis | Low–medium |
| [RoboTwin2.0, 2506.18088](https://arxiv.org/abs/2506.18088) | Scalable digital-twin data generation, object/task assets, and domain randomization | Provides a possible implementation substrate; does not claim the diagnostic | Low |
| [SC3-Eval, 2606.18610](https://arxiv.org/abs/2606.18610) | Action-conditioned video evaluation using forward/inverse, cross-view, and test-time consistency | Shares behavior/action consistency evaluation, but not functional-geometry counterfactual execution | Low–medium |
| [Pointing-VLA, 2608.23138](https://arxiv.org/abs/2608.23138) | Typed normalized point and geometry representations for VLA action generation | Geometry-explicit policy representation; no paired diagnostic | Low |
| [Action with Visual Primitives (AVP), 2605.22183](https://arxiv.org/abs/2605.22183) | VLM-produced target/visual-primitive tokens condition an action expert | Functional visual conditioning, but a policy method rather than an assay | Low |
| [ForeTime-VLA, 2608.20735](https://arxiv.org/abs/2608.20735) | Future-token distillation for VLA learning | Future prediction/training only; no relevant diagnostic mechanism | Low |
| [Any3D-VLA, 2602.00807](https://arxiv.org/abs/2602.00807) | Diverse point-cloud fusion for 3D-aware VLA control | 3D geometry representation/training; no matched action crossover | Low |
| [CLOVER, 2409.09016](https://arxiv.org/abs/2409.09016) | Generative expectations, online feedback, and replanning | A candidate frozen policy/evaluation backbone; not the same diagnostic | Low |
| [Functional Manipulation Benchmark (FMB), 2401.08553](https://arxiv.org/abs/2401.08553) | Procedurally generated functional manipulation tasks | Shares functional manipulation and controlled assets; no current-action compatibility assay | Low–medium |

No inspected named neighbor was found to contain all four GISS operations. That negative finding is weaker than proving field-wide absence, and the unoccupied-looking operation is still a narrow protocol delta over two close diagnostic families.

## Is this merely a narrow engineering variant of metamorphic testing?

**Mostly yes, provisionally.** It is not a trivial implementation tweak: crossing source actions into both recipient geometries yields a more causal compatibility test than comparing two independently closed-loop trajectories, and the symmetric interaction cancels some geometry-specific baseline difficulty. However, the scientific framing—controlled transformations, expected policy variation under relevant changes, behavior-level diagnosis, and endpoint-success insufficiency—is already stated by the metamorphic-testing paper. A skeptical reviewer can describe GISS as one specialized trajectory-variation metamorphic relation with simulator state restoration and a 2×2 execution oracle.

To escape that characterization, the work would need to establish a new phenomenon that existing trajectory-difference and action-drift tests systematically cannot detect, not merely argue that the new oracle is cleaner. For example, it would need preregistered cases where paired trajectories or offline action drift are ambiguous or misleading, while the crossed native-success interaction uniquely resolves compatibility—and show this across enough task/geometry families to constitute a reusable diagnostic result. The current documents propose such a possibility but do not yet establish it.

## Fatal overlap

The fatal overlap is the conjunction of two priors:

1. **Metamorphic Testing** already owns the broad contribution that controlled VLA input/environment transformations should induce specified behavioral invariance or variation, and that trajectory-level diagnostics complement or outperform endpoint symbolic success.
2. **Counterfactual Action Sensitivity Coverage** already owns same-underlying-state paired visual interventions for auditing whether a robot policy's action changes appropriately, albeit under nuisance-invariance semantics and with an offline drift outcome.

After subtracting those contributions, GISS can claim only the relevant-functional-geometry treatment and the four-cell native-success interaction. That is a credible protocol contribution, but on the present evidence it is below the novelty bar for a standalone CoRL/RSS/NeurIPS paper claim.

## Full-text-degraded penalty

The candidate's Phase 3 review explicitly recorded `fulltext_degraded=true` and advanced mainly on abstract-level differentiation. That matters because the initially missed high-threat papers contain mechanism details not recoverable from titles alone.

For this jury, the two decisive works—Metamorphic Testing and Counterfactual Action Sensitivity Coverage—were inspected in primary full text, as were LIBERO-CF and GemBench. The remaining named June–August 2026 works were verified from their primary arXiv records/abstracts; attempted bulk PDF retrieval failed because of transport/SSL errors. Their abstracts are sufficient to classify them as training methods, benchmarks, or representation methods rather than the exact 2×2 assay, but not sufficient for a strong global non-overlap claim.

I therefore apply a **0.2-point evidence penalty**: provisional mechanism score 6.9, final novelty **6.7**. This penalty is deliberately modest because the most dangerous collisions were read in full, but it prevents treating incomplete retrieval as positive novelty evidence.

## Falsifiable novelty proposition

The narrow novelty proposition that survives is:

> As of 2026-08-31, no prior VLA evaluation holds non-geometry simulator state and policy-inference state fixed across two visible, endpoint-equivalent collision geometries; queries one native current action chunk from each geometry; executes both chunks in both recipient geometries; and reports the symmetric own-source-versus-cross-source native-success interaction.

This proposition is falsified by any prior paper, supplement, or public implementation that performs all four operations, even if it uses different terminology. It is also scientifically hollowed out—though not literally bibliographically falsified—if, on the same preregistered cases, the GISS interaction reveals no reliable failure ordering or information beyond Metamorphic Testing's trajectory-variation metric and CASC-style same-state action drift.

## Minimum non-GPU falsification package

Because the novelty score is at or below the threshold, **do not start a four-A100 or other GPU experiment**. The minimum admissible next check is literature/protocol falsification only:

1. Inspect the code and supplements of arXiv:2602.22579 and arXiv:2607.27261 for action-source swapping, state snapshot/restore, and recipient-geometry native outcomes. Discovery of these operations kills the residual claim.
2. Freeze a formal protocol before any model run: pair-construction rules, exact serialized-state fields and tolerances, policy history/cache reset, decoder seed/repetition rule, continuation boundary, success definition, and state-jitter gate. If these cannot be made deterministic and auditable, kill the diagnostic.
3. On a tiny simulator-only hand check with scripted actions—not a learned VLA and not a GPU run—verify that both diagonal cells can succeed and both off-diagonal cells can fail for at least two geometry mechanisms. If the interaction cannot be made structurally identifiable without changing non-geometry state, kill the premise.

Passing these checks would justify renewed novelty review, not an experiment launch or a paper claim.

## Final jury decision

**6.7/10, FAIL. No candidate-level novelty pass and no GPU authorization.** GISS-2x2 is a thoughtful and relatively clean causal specialization of VLA metamorphic evaluation. Its four-cell native-success interaction appears more specific than the inspected neighbors, but the general problem, diagnostic rationale, and matched-state policy-response components are already occupied. At present it is best viewed as a narrow engineering/reliability contribution or benchmark protocol, not a sufficiently novel standalone research mechanism.

