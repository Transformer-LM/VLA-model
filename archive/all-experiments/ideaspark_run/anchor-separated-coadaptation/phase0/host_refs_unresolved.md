# Host-nominated papers that did NOT resolve to a real record

These titles could not be verified via any connector and were NOT admitted to the corpus (a likely hallucination or a title too garbled to match). Review manually if any is genuinely important.

- **World-VLA-Loop: Closed-Loop Learning of Video World Model and VLA Policy** (id_hint: arXiv:2602.06508)
  - why nominated: Exact collision candidate: policy failure rollouts iteratively refine the video world model, which then supplies virtual RL rollouts for the VLA; the proposal must show why an independently held reality anchor prevents a failure this co-evolving loop does not address.
- **VLAW: Iterative Co-Improvement of Vision-Language-Action Policy and World Model** (id_hint: arXiv:2602.12063)
  - why nominated: Direct iterative VLA-world-model co-training neighbor: real policy rollouts improve world-model fidelity and generated rollouts improve the policy, making it load-bearing for separating the proposed cross-fitted reality interface from naive alternation.
- **WoVR: World Models as Reliable Simulators for Post-Training VLA Policies with RL** (id_hint: arXiv:2602.13977)
  - why nominated: Explicitly targets hallucination-driven policy exploitation and maintains policy-simulator alignment through world-model-policy co-evolution; it is the closest baseline for proving that anchor separation adds more than rollout stabilization or uncertainty control.
- **Feedback World Model Enables Precise Guidance of Diffusion Policy** (id_hint: arXiv:2605.15705)
  - why nominated: Uses real post-action prediction residuals as an online feedback state to correct a world model under distribution shift, closely neighboring the reality-anchor intuition while remaining inference-time feedback rather than cross-fitted co-training.
- **World-Gymnast: Training Robots with Reinforcement Learning in a World Model** (id_hint: arXiv:2602.02454)
  - why nominated: Trains a VLA by imagined rollouts with VLM rewards and reports online iterative world-model and policy improvement; it is a direct comparator for shared-evaluator self-confirmation and for the value of an external reality anchor.
- **Imperfect World Models are Exploitable** (id_hint: arXiv:2605.15960)
  - why nominated: Formalizes model exploitation as policy-order inversion and shows low predictive error need not prevent it, providing the theory-level justification for why generic validation or prediction accuracy cannot rule out self-confirming shared errors.
- **Cross-fitted Proximal Learning for Model-Based Reinforcement Learning** (id_hint: arXiv:2604.05185)
  - why nominated: Recent explicit K-fold cross-fitting ancestor in model-based RL; although aimed at bridge estimation under hidden confounding rather than VLA-WAM co-adaptation, it is load-bearing prior art for any claimed novelty in a cross-fitted interface.
