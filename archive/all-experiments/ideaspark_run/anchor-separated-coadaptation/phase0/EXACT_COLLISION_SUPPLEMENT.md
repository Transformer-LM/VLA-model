# Web-verified exact-neighbor supplement

The Phase 0 connectors were degraded (Semantic Scholar 429; arXiv SSL EOF), so unresolved nominations must not be interpreted as absent literature. The following records were verified directly from primary arXiv pages on 2026-08-30.

| Work | Primary record | Load-bearing overlap |
|---|---|---|
| World-VLA-Loop | arXiv:2602.06508 | Closed-loop learning in which policy rollouts refine the video world model and the world model supplies experience for VLA improvement. Occupies ordinary policy-world-model co-evolution. |
| VLAW | arXiv:2602.12063 | Iterative co-improvement of a VLA policy and a world model with real policy rollouts and imagined policy training. Occupies naive alternating co-training. |
| WoVR | arXiv:2602.13977 | Uses world models as controlled simulators for RL post-training of VLA policies and explicitly discusses policy-world co-evolution. Occupies ordinary reliability filtering around imagined VLA RL. |
| World-Gymnast | arXiv:2602.02454 | Fine-tunes a VLA with RL rollouts in an action-conditioned video world model and reports online iterative world-model/policy improvement. |
| Feedback World Model | arXiv:2605.15705 | Corrects future predictions online using the discrepancy between predicted and realized observations through a latent observer. Occupies generic reality-feedback correction. |
| Do Robotic World Models Really Follow Actions? / WorldEcho + WorldSync | arXiv:2608.24885 | Diagnoses off-expert action faithfulness and aligns world-model predictions under action interventions; directly weakens novelty claims based only on policy-shifted action coverage. |
| Imperfect World Models are Exploitable | arXiv:2605.15960 | Formally defines exploitation as a reversal between policy orderings under the learned and true transition models, proves broad inevitability, and derives a safe horizon. Occupies generic exploitation/safe-horizon claims. |
| Cross-fitted Proximal Learning for Model-Based RL | arXiv:2604.05185 | Uses K-fold cross-fitting to estimate bridge functions in confounded POMDP model-based RL. It is not a robotics co-evolution method, but it is a strong ancestor against claiming sample splitting or cross-fitting itself as novel. |

## Boundary implied by these collisions

An admissible new idea must do more than alternate policy and WAM updates, mix real and imagined data, filter uncertain rollouts, test action faithfulness, feed realized observations back into the WAM, or reserve a held-out real split. The only potentially new claim in this run is a specifically defined and experimentally identifiable **shared-error amplification process** plus an intervention that breaks that process without reducing to ordinary validation/cross-fitting. If that mechanism cannot be specified, this direction is a no-go.
