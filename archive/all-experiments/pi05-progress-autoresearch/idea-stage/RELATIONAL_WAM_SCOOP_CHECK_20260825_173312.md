# Relational WAM for VLA Verification：Scoop Check

日期：2026-08-25

## Verdict

**Level 2 — High Overlap.** 原始宽泛 claim 已被多个最近邻工作的并集严重覆盖。CheckVLA 覆盖 action-conditioned WAM execution verification、校准触发和 suffix repair；ReKep 覆盖语言指定的关系约束、实时闭环检查、关系失效后的 stage backtracking，并在多阶段、双臂和 reactive manipulation 中验证。OA-WAM、SOLD、Object-Centric World Model for Language-Guided Manipulation、EvoScene-VLA 分别进一步覆盖对象寻址、action-conditioned object dynamics、语言引导对象未来和 action-updated scene belief。

## Delta

Unlike CheckVLA, which verifies pooled global latent predictions, and ReKep, which checks deterministic VLM-generated keypoint constraints under a local rigidity model, the only defensible proposed delta is to learn **calibrated action-conditioned distributions over language-selected relation edges** and show that edge-localized verification improves timely failure detection and cross-task relation-composition generalization under matched inputs, parameters, false-intervention rate, and policy-call budget.

这个 delta 仍然脆弱：如果 matched CheckVLA-style global verifier 或 ReKep-style constraint checker 达到相同效果，方法贡献消失。

## Decomposed claim

- **Problem framing**：冻结 VLA 在执行 action chunk 时，任务相关对象关系可能建立失败或中途失效；需要执行期验证与重规划。
- **Core mechanism**：语言选择可变对象关系子图；action-conditioned graph dynamics 预测逐边未来分布；观测到的关系偏离预测时校准触发。
- **Key insight**：任务关系边比全局视觉/latent residual 更能隔离物理失败、定位失效实体并抵抗背景/相机 nuisance。
- **Application domain**：跨抓取、包含、推动、工具、关节、多执行器等机器人操作任务，冻结 π0.5 或其他 chunked VLA。

## Structured papers

### 1. CheckVLA: Execution-Time Verification with Action-Conditioned World Model for Long-Horizon Mobile Manipulation

- Date: 2026-07; arXiv:2607.26789.
- Problem framing: committed VLA chunks在执行后发生偏差，需在线验证与修复。
- Core mechanism: frozen action-conditioned latent WM、prediction-observation residual、causal risk head、functional conformal threshold、latency-aware suffix rewrite、keyframe memory。
- Key insight: action chunk也是对未来观察的可检验预测。
- Domain: RoboCasa365 long-horizon mobile manipulation，simulation。
- Overlap: 3/4；problem、key insight、domain 高度匹配，representation 从 global latent 改为 relation graph。
- Source: https://arxiv.org/abs/2607.26789

### 2. ReKep: Spatio-Temporal Reasoning of Relational Keypoint Constraints for Robotic Manipulation

- Date: 2024-09; CoRL 2024.
- Problem framing: 用语言定义跨对象/机器人关系，并在闭环操作中保持或恢复这些关系。
- Core mechanism: VLM 生成 relational keypoint constraint functions；3D keypoint tracking；receding-horizon optimization；constraint violation 后 backtrack 到可满足阶段。
- Key insight: manipulation 可表示为跨阶段、跨实体的时空关系约束。
- Domain: single-arm、dual-arm、multi-stage、in-the-wild、reactive real-robot manipulation。
- Overlap: 3/4；只在 learned probabilistic action-conditioned dynamics 上显著不同。
- Source: https://arxiv.org/abs/2409.01652

### 3. OA-WAM: Object-Addressable World Action Model for Robust Robot Manipulation

- Date: 2026-05; arXiv:2605.06481.
- Problem framing: holistic WAM 难以稳定绑定语言指定对象。
- Core mechanism: persistent identity address + time-varying content/pose；address-only attention routing；next-slot world head + action head。
- Key insight: identity 与动态状态在 tensor level 分离。
- Domain: LIBERO、SimplerEnv、LIBERO-Plus。
- Overlap: 2/4；覆盖语言对象绑定和对象状态，但不做候选动作条件的逐关系执行验证。
- Source: https://arxiv.org/abs/2605.06481

### 4. EvoScene-VLA: Evolving Scene Beliefs Inside the Action Decoder for Chunked Robot Control

- Date: 2026-08; arXiv:2605.21862v2.
- Problem framing: chunked VLA 缺少跨 chunk 的 action-updated scene prior。
- Core mechanism: recurrent scene prefix；action-scene co-denoising；未来 3D feature supervision；新观测纠正 prior。
- Key insight: scene state必须持久、被动作推进并由新观测纠正。
- Domain: 31 RoboTwin tasks + Galaxea dual-arm real robot。
- Overlap: 2/4；覆盖 action-updated belief 和跨任务 VLA，但非显式关系图或执行 verifier。
- Source: https://arxiv.org/abs/2605.21862

### 5. Object-Centric World Model for Language-Guided Manipulation

- Date: 2025-03; arXiv:2503.06170.
- Problem framing: 语言条件下高效预测对象未来并用于控制。
- Core mechanism: SAVi slots + language-conditioned LSlotFormer autoregressive future slots + inverse action decoder。
- Key insight: object-centric latent prediction比视频扩散更紧凑。
- Domain: language-table simulation，block manipulation。
- Overlap: 2/4；覆盖语言、对象未来和控制，但不是 action-conditioned execution verification。
- Source: https://arxiv.org/abs/2503.06170

### 6. SOLD: Slot Object-Centric Latent Dynamics Models for Relational Manipulation Learning from Pixels

- Date: 2024-10/2025-02 revision; arXiv:2410.08822.
- Problem framing: holistic MBRL 难以处理对象交互和 relational manipulation。
- Core mechanism: SAVi slots；temporal + relational attention；action-conditioned slot dynamics；imagined actor-critic learning。
- Key insight: structured object dynamics改善 relational behavior learning。
- Domain: visual robotic MBRL benchmarks。
- Overlap: 2/4；覆盖 action-conditioned object relational dynamics，缺语言/VLA执行验证。
- Source: https://arxiv.org/abs/2410.08822

### 7. World Action Verifier: Self-Improving World Models via Forward-Inverse Asymmetry

- Date: 2026-04; arXiv:2604.01985.
- Problem framing: WMs 在 underexplored actions 上不能可靠验证自己的预测。
- Core mechanism: state plausibility + action reachability 分解；video subgoal generator；sparse inverse dynamics；forward-inverse cycle；verification-guided exploration。
- Key insight: action-relevant sparse features比完整 forward prediction 更易验证。
- Domain: MiniGrid、RoboMimic、ManiSkill。
- Overlap: 2/4；verification 与 sparse task-relevant state 相邻，但验证对象是 WM 自身、用途是采数/self-improvement，不是在线 VLA execution repair。
- Source: https://arxiv.org/abs/2604.01985

### 8. FOCUS: Object-Centric World Models for Robotics Manipulation

- Date: 2023/2025 journal; arXiv:2307.02427.
- Core mechanism: object-centric state用于 goal/exploration 与 manipulation learning。
- Overlap: 1/4；是 object-centric WM 基础最近邻，不覆盖语言关系执行验证。
- Source: https://arxiv.org/abs/2307.02427

### 9. Planning for Multi-Object Manipulation with Graph Neural Network Relational Classifiers

- Date: 2023; ICRA 2023.
- Core mechanism: GNN relational classifiers用于多物体操作规划。
- Overlap: 2/4；关系图和操作规划匹配，但非 VLA/WAM execution verification。
- Source: https://doi.org/10.1109/ICRA48891.2023.10161204

### 10. Goal-VLA: Image-Generative VLMs as Object-Centric World Models Empowering Zero-shot Robot Manipulation

- Date: 2025-06; arXiv:2506.23919.
- Core mechanism: object-centric generative goal/world prediction连接 zero-shot manipulation。
- Overlap: 1/4；不做关系边 verifier。
- Source: https://arxiv.org/abs/2506.23919

### 11. Mem-World: Memory-Augmented Action-Conditioned World Models for Persistent Robot Manipulation

- Date: 2026-06; arXiv:2606.18960.
- Core mechanism: memory-augmented action-conditioned WM，处理 persistent manipulation。
- Overlap: 2/4；覆盖历史和 action conditioning，但非任务关系边校准验证。
- Source: https://arxiv.org/abs/2606.18960

### 12. DREAM-Chunk: Reactive Action Chunking with Latent World Model

- Date: 2026-06; arXiv:2606.18589.
- Core mechanism: 从 VLA 采样多个 chunks，latent WM rollout 后选择更可靠 chunk。
- Overlap: 2/4；覆盖 chunked VLA + WM action selection，不做显式关系状态。
- Source: https://arxiv.org/abs/2606.18589

### 13. VLA-Corrector: Lightweight Detect-and-Correct Inference for Adaptive Action Horizon

- Date: 2026-07; arXiv:2607.01804.
- Core mechanism: latent visual monitor检测 dynamics deviation，触发 chunk truncation 和 corrective replanning。
- Overlap: 2/4；覆盖执行检测与纠错，缺 action-conditioned relation graph。
- Source: https://arxiv.org/abs/2607.01804

### 14. Language-Conditioned Change-point Detection to Identify Sub-Tasks in Robotics Domains

- Date: 2023-09; arXiv:2309.00743.
- Core mechanism: language-conditioned subtask change-point detection。
- Overlap: 1/4；与关系事件/进度边界相邻，但不是 action-conditioned WAM verifier。
- Source: https://arxiv.org/abs/2309.00743

## Comparison result

- **Proposed work**
  - Problem: cross-task VLA action-chunk relation failure verification.
  - Mechanism: language-selected variable relation graph + action-conditioned probabilistic edge dynamics + calibrated trigger.
  - Insight: task-edge discrepancy should outperform global latent discrepancy.
  - Domain: general chunked-VLA manipulation.

- **CheckVLA**
  - Matches: problem framing, execution-time action-conditioned mechanism family, application domain.
  - Differs: pooled global latent versus explicit task-relation edge distribution.
  - Axes matching: 3/4 → **Level 2, High Overlap**.

- **ReKep**
  - Matches: language-selected relations, online relation violation/backtracking, general manipulation domain.
  - Differs: deterministic VLM-generated keypoint constraints/local rigidity versus learned calibrated action-conditioned relation dynamics.
  - Axes matching: 3/4 → **Level 2, High Overlap**.

- **OA-WAM**
  - Matches: language-object structured state and WAM manipulation domain.
  - Differs: no execution-time edge-discrepancy verification.
  - Axes matching: 2/4 → **Level 3, Medium Overlap**.

- **EvoScene-VLA**
  - Matches: action-updated scene belief and chunked VLA domain.
  - Differs: no explicit relation edges or calibrated intervention.
  - Axes matching: 2/4 → **Level 3, Medium Overlap**.

- **Object-Centric WM for Language-Guided Manipulation**
  - Matches: language-guided object future and manipulation domain.
  - Differs: language-conditioned rather than candidate-action-conditioned; no verifier.
  - Axes matching: 2/4 → **Level 3, Medium Overlap**.

- **SOLD**
  - Matches: action-conditioned object-relational dynamics and control domain.
  - Differs: MBRL without language/VLA execution verification.
  - Axes matching: 2/4 → **Level 3, Medium Overlap**.

- **World Action Verifier**
  - Matches: WM verification and sparse task-relevant state insight.
  - Differs: verifies WM for exploration/self-improvement, not policy execution.
  - Axes matching: 2/4 → **Level 3, Medium Overlap**.

## Decision

**REVISE, not run full system.** 不应声称“首次用对象关系 WAM 验证和纠正 VLA”。下一步只值得做一个 oracle/matched diagnostic：在相同输入、参数、误报率与调用预算下，edge-wise learned relation verifier 是否显著优于 CheckVLA-style global latent verifier 和 ReKep-style deterministic constraint checker。若 timely recall 没有至少 +10pp 或跨 relation composition 增益不成立，则终止该方法 claim。

