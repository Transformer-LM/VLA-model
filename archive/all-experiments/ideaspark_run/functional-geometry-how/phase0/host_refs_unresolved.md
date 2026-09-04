# Host-nominated papers that did NOT resolve to a real record

These titles could not be verified via any connector and were NOT admitted to the corpus (a likely hallucination or a title too garbled to match). Review manually if any is genuinely important.

- **Pointing-VLA: Typed Spatial Grounding Interfaces for Vision-Language-Action Manipulation** (id_hint: arXiv:2608.23138)
  - why nominated: Closest current collision: it adds object-functional grounding heatmaps, typed spatial targets, and stage-aligned PICK/PLACE guidance to a pi0.5 action policy. It is load-bearing for showing that paired target/reference PointMaps plus relation-conditioned phase-wise HOW correction add more than target-point or affordance-map injection.
- **OA-WAM: Object-Addressable World Action Model for Robust Robot Manipulation** (id_hint: arXiv:2605.06481)
  - why nominated: Direct object-centric WAM comparator: persistent addressed object slots predict future slot states while a flow-matching head emits action chunks. It is necessary to separate object addressability and learned scene evolution from an explicit two-object functional-geometry correction interface.
- **Lift3D-VLA: Lifting VLA Models to 3D Geometry and Dynamics-Aware Manipulation** (id_hint: arXiv:2607.06564)
  - why nominated: A frontier generic 3D-VLA baseline that combines explicit point-cloud reasoning, future geometric evolution prediction, and temporally coherent action chunks. It tests whether gains come from generic 3D/dynamics augmentation rather than relation-specific target/reference geometry and structured residual correction.
- **GOPLA: Generalizable Object Placement Learning via Synthetic Augmentation of Human Arrangement** (id_hint: arXiv:2510.14627)
  - why nominated: Recent hierarchical placement competitor that converts pairwise object relations into 3D affordance maps and diffusion-generated placement poses with collision costs. It is the closest recent semantic-relation-to-geometry baseline, but terminates at placement-pose planning rather than correcting grasp, approach, phase order, and infeasibility throughout a VLA chunk.
- **PointVLA: Injecting the 3D World into Vision-Language-Action Models** (id_hint: arXiv:2503.07511)
  - why nominated: The indispensable lightweight point-cloud VLA baseline: it freezes the vanilla action expert and injects 3D features through a small modular block. It directly controls for whether the proposed benefit is merely point-cloud conditioning rather than paired functional geometry and phase-structured HOW correction.
- **AnyPlace: Learning Generalized Object Placement for Robot Manipulation** (id_hint: arXiv:2502.04531)
  - why nominated: Direct placement baseline for the same insertion, stacking, and hanging regimes: a VLM selects a rough target region and source/target point clouds yield diverse precise relative placement poses. It is load-bearing for distinguishing full-skill adaptation from terminal relational 6D pose prediction.
- **ReKep: Spatio-Temporal Reasoning of Relational Keypoint Constraints for Robotic Manipulation** (id_hint: arXiv:2409.01652)
  - why nominated: A required phase-structured alternative: it represents tasks as sequences of relational 3D keypoint constraints and optimizes dense SE(3) actions, including transition behavior. It tests whether learned PointMap corrections offer robustness or efficiency beyond explicit VLM-generated constraints and trajectory optimization.
- **Shelving, Stacking, Hanging: Relational Pose Diffusion for Multi-modal Rearrangement** (id_hint: arXiv:2307.04751)
  - why nominated: Canonical RPDiff baseline for multimodal 6-DoF relational rearrangement from object and scene point clouds on shelving, stacking, and hanging. Although older, it is indispensable for isolating terminal relation-pose diffusion from phase-wise corrections to grasp, alignment, approach, depth, and feasibility.
