# Host-nominated papers that did NOT resolve to a real record

These titles could not be verified via any connector and were NOT admitted to the corpus (a likely hallucination or a title too garbled to match). Review manually if any is genuinely important.

- **CofactVLA: Deconfounding Vision-Language-Action Models via Counterfactual Intervention** (id_hint: arXiv:2608.04396)
  - why nominated: 直接把反事实干预用于 VLA 后训练，并在动作流与特征层消除视觉混杂；虽不构造功能几何可行性翻转对，却是判定几何反事实方案是否真正新增因果监督的最新边界先例。
- **DREAMSTEER: Latent World Models Can Steer VLA Policies During Deployment Without Any Finetuning** (id_hint: arXiv:2607.02865)
  - why nominated: 从 VLA 与运动原语采样多个动作块，以潜在世界模型预演并用价值模型排序；它不做后训练，但直接承载多候选有效模式保留与局部可行性评分的强对照。
- **PhysReflect-VLA: Physical Feasibility and Self-Reflective Regulation for Reliable Vision-Language-Action Policies** (id_hint: arXiv:2606.27146)
  - why nominated: 显式学习动作诱导状态转移的物理可行性并用闭环反思纠错，最接近局部 violation-segment 评分的替代机制；必须据此收窄后训练而非执行时筛选的增量。
- **AffordanceVLA: A Vision-Language-Action Model Empowering Action Generation through Affordance-Aware Understanding** (id_hint: arXiv:2606.06155)
  - why nominated: 用 Which2Act、Where2Act 与 How2Act 的结构化可供性中间监督连接视觉、3D 几何和动作，直接覆盖无触觉条件下学习功能几何约束的最近邻。
- **World2Act: Latent Action Post-Training via Skill-Compositional World Models** (id_hint: arXiv:2603.10422)
  - why nominated: 直接研究 VLA 后训练，并以世界模型视频动力学潜变量对齐动作表示；它是判断局部可行性翻转评分相对一般世界模型后训练是否必要的载荷基线。
- **RoCoDA: Counterfactual Data Augmentation for Data-Efficient Robot Learning from Demonstrations** (id_hint: arXiv:2411.16959)
  - why nominated: 把因果不变性与 SE(3) 等变变换结合为机器人示范的反事实增强，直接界定几何反事实数据构造的既有范围；新方案必须证明其最小可行性翻转不是 RoCoDA 式增强的直接实例。
