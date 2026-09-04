## 结论

**PARTIAL（对应 Level 2 — High Overlap）**。截至 2026-08-07，未发现精确碰撞：没有论文在 VLA 训练前计算

\[
C(y)=L(y\mid o,l)-L(y\mid o,l,a)
\]

并将其预注册为跨 target 的排序变量，再检验它是否比 reconstruction loss、variance/SNR 或 target family 更能预测增量闭环策略收益。

但相邻空间已经很拥挤：多篇工作已分别占据“比较 future target”“action-aware/action-recoverable representation”“信息量改善控制”“辅助任务选择”这些组成部分。C02 只能保留为一个窄的、前瞻性的实证诊断，不能宣称新 controllability 定义、新 future target 或新 WAM 方法。

一句话 delta：

> 不同于 FLARE 直接构造 action-aware embedding、以及 *Reconstruction or Semantics?* 事后报告 inverse-dynamics action recoverability 与 policy-facing metrics，C02 的剩余贡献只能是：在任何 target-policy 训练前，用独立数据估计统一的 action-conditional risk reduction，并检验它能否在等接口条件下前瞻排序未训练 target 的增量闭环收益。

## Claim 四轴

- **问题定义：** 在固定 VLA、数据和训练预算下，训练前选择哪一种未来辅助 target。
- **核心机制：** 对各等维、白化 target 分别拟合等容量的 action-masked 与 action-conditioned probe，以严格 held-out risk gap 定义 \(C(y)\)。
- **关键洞见：** target 的价值可能取决于其包含的条件动作信息，而非重建容易度、方差、SNR 或语义类别。
- **应用域：** VLA/WAM 辅助 future prediction 对机器人闭环策略迁移的影响。

## 检索

主要查询：

1. `prospective prediction target selection policy transfer gain action conditional controllability robot representation`
2. `controllability aware representation learning action conditional mutual information predictability auxiliary task selection`
3. `world model representation target future latent motion action conditioned auxiliary objective vision language action policy`
4. 精确补检：Motion Image Diffusion、DreamWAM、EgoWAM、VLAFlow、FLARE、DynaMo，以及 `action-conditioned vs action-agnostic prediction loss`
5. 跨域补检：conditional mutual information、action recoverability、auxiliary-task usefulness/selection、gradient similarity

只采用 arXiv 在线全文、OpenReview、NeurIPS/PMLR 官方 proceedings 和官方论文页作为证据。

## 最近工作

| 工作 | 重叠类型 | 与 C02 的关系 |
|---|---|---|
| [FLARE: Robot Learning with Implicit World Modeling](https://arxiv.org/html/2505.15659) | **最接近，部分碰撞** | 比较无 FLARE、SigLIP2、pooled SigLIP2 和 action-aware embedding，成功率 43.9/49.6/50.9/55.0；明确主张 action-aware target 更适合 policy。但没有 \(C(y)\)、等 target 预算、竞争预测变量或前瞻排序。 |
| [Reconstruction or Semantics? What Makes a Latent Space Useful for Robotic World Models](https://arxiv.org/html/2605.06388) | **最接近，部分碰撞** | 固定 transition model 比较 6 个 latent spaces，并用 IDM action recoverability、CEM、policy-in-world-model success 与视觉指标评价。IDM 本质上接近 \(I(A;Y\mid O)\) 的 inverse-direction proxy，但研究的是 world-model latent/policy evaluation，不是 target co-training 的真实 policy transfer gain。 |
| [EgoWAM](https://arxiv.org/html/2607.08436) | **高部分碰撞** | 直接提出“什么 world target 最利于 transfer”，比较 Pixel、DINO、3D flow，固定 trunk/action head/data mixture。但 target head 和维度差异很大，依据是 appearance abstraction/cross-embodiment consistency/ego-motion factoring，而非训练前可计算的统一预测量。 |
| [Robotic VLA Benefits from Joint Learning with Motion Image Diffusion](https://arxiv.org/html/2512.18007) | **高部分碰撞** | 比较 action-only、language、future image、motion image；motion 最好。它已占据“不同 target 导致不同策略收益”，但 target/interface 不匹配，也没有解释变量竞争或 prospective test。 |
| [DreamWAM](https://arxiv.org/html/2608.04996) | **高部分碰撞，极新** | 2026-08-05 发布；比较 RGB、motion、geometry、semantics 及 leave-one-out 组合。但 target 与注入路径耦合；论文自己表明同一 target 用 denoising 或 residual route 可从增益变成退化，因此 target 内容不是唯一决定因素。 |
| [VLAFlow](https://arxiv.org/html/2607.01586) | **部分碰撞** | 在统一架构下比较 action-only、language、future latent 及组合，并显示 future-latent fidelity 与轨迹成功相关。但只有一个 future target，且作者明确称它是后期 trajectory-consistency signal，不是训练前/早期 predictor。 |
| [DynaMo](https://arxiv.org/html/2409.12192) | 邻近 | 动力学预训练提升 downstream policy，但无真实 action 条件、无 target selection。 |
| [PI-QT-Opt](https://proceedings.mlr.press/v205/lee23a.html) / [Predictive Information Accelerates Learning in RL](https://arxiv.org/abs/2007.12401) | 邻近 | predictive information 辅助目标改善机器人/RL transfer，说明“信息量与控制收益相关”不是新洞见；未比较 target 的 action-conditional information。 |
| [Learning Action-based Representations Using Invariance](https://arxiv.org/html/2403.16369) | 邻近 | 明确定义 controllability representation，并以 inverse dynamics、action-bisimulation 保留控制相关变量；不做 VLA target ranking。 |
| [Action-Sufficient State Representations](https://proceedings.mlr.press/v162/huang22f.html) | 邻近 | 用结构约束和 conditional MI 学 action-sufficient representation；说明 CMI/action sufficiency 有成熟先例。 |
| [Which MI Objectives Are Sufficient for Control?](https://proceedings.neurips.cc/paper/2021/hash/dd45045f8c68db9f54e70c67048d32e8-Abstract.html) | 关键反例先例 | 证明一些 MI objective 即使很高也可能不足以支撑 optimal control；高 \(C\) 不能自动等价于 policy utility。 |
| [Auxiliary task discovery through generate-and-test](https://proceedings.mlr.press/v232/rafiee23a.html) / [Adapting Auxiliary Losses Using Gradient Similarity](https://arxiv.org/abs/1812.02224) | 邻近 | 已有通用辅助任务 usefulness/selection 方法，但需主任务训练信号或在线试验；C02 的优势只能是更便宜的训练前 proxy。 |

没有 exact collision；FLARE 与 *Reconstruction or Semantics?* 共同把新意压缩到“统一 risk-gap 的前瞻比较有效性”。

## 数学与设计问题

1. 若 \(L\) 是 Bayes-optimal log loss，则

   \[
   C(y)=H(Y\mid O,L)-H(Y\mid O,L,A)=I(Y;A\mid O,L),
   \]

   所以公式本身不是新信息论量。若使用 MSE，它是 action 对条件均值解释方差的风险下降，并非严格 CMI。Flow-matching loss 的差更不能直接称为信息量。

2. 离线 expert data 中，动作由 behavior policy 产生。高 \(C\) 可能来自隐藏 task phase、意图或未观测状态；它首先是 **action-conditional predictive information**，不是因果 controllability。无干预动作或强 within-state matching 时，不应使用 causal wording。

3. `full future latent` 与 `future-current residual` 在给定当前观测时是可逆平移：

   \[
   I(A;Z_{t+h}-Z_t\mid O_t,L)=I(A;Z_{t+h}\mid O_t,L).
   \]

   在理想 probe/统一 MSE 下，它们不构成两个独立 controllability strata。

4. 随机正交变换同样保留信息、方差和最优 \(C\)。它应作为**不变性阳性控制**，不是随机 negative target。真正的负控应是与 transition 独立但维度、方差、频谱匹配的噪声 target。

5. 高 \(C\) 也可能表示“没有未来动作就很难预测”。若实际 auxiliary head 不看到 action，高 \(C\) 未必有利；若训练时看到 ground-truth/noised action，又可能产生 label shortcut。必须预注册 world head 的 action access。

## 最少 target 数量

四个原始 target 不足以支持“单调/预测关系”：

- \(n=4\) 时，即使 Spearman 排序完美，双侧精确 \(p=2/4!=0.0833\)，无法达到 0.05。
- **数学硬下限：5 个独立 target-level units**；只能证明极强完美排序。
- **勉强可辩护下限：4 个 \(C\) strata × 每层 2 个独立 target 构造 = 8 targets**。
- 若要声称 \(C\) 比 reconstruction loss、variance/SNR、semantic family 更强，建议最低 **4 strata ×3 targets = 12 targets**，以 target 为统计单位，用 target-level permutation、partial Spearman 或 leave-one-family-out。task、seed、rollout 只能作为重复测量，不能把有效 target 样本量从 4 伪增大。

推荐至少跨两类语义 family 构造每个 \(C\) 层级，避免“motion target 恰好最好”被误写成连续预测规律。

## 最低控制集

至少需要：

1. action-only policy baseline；
2. current/static 的近零-\(C\) anchor；
3. 独立噪声 negative target；
4. 正交旋转 target pair，验证 \(C\) 和收益对坐标变换的不变性；
5. action-shuffled/dummy-action probe placebo；
6. target 维度、逐通道白化、token 数、head 参数、loss coefficient、steps、优化器、训练 FLOPs（建议 ±5%）全部匹配；
7. episode/time 严格 holdout、cross-fitted \(C\)，且 probe 的有/无 action 版本容量完全相同；
8. 预注册 target 排名，并至少做一次 leave-one-target-family-out prediction。

## 诊断 finding 还是普通 ablation

- **可称 DIAGNOSTIC/FINDING：** \(C\) 在训练前、独立数据上冻结；target/rank/统计检验预注册；存在至少 8–12 个 target-level units；验证跨 family 预测且优于替代指标。
- **只能称 ORDINARY ABLATION：** 只训 high/low 两极、只比较四个自然 target、根据结果事后解释 motion 更“可控”，或没有 held-out/leave-family-out。
- 当前 8 GPUh 的“高、低、action-only”方案只能是 feasibility/falsification pilot，不能支持单调 predictor claim。

## 最窄可辩护 claim

> 在固定 backbone、数据、辅助接口和计算预算，并对白化等维连续 target 使用独立 held-out probes 的条件下，训练前 action-conditional predictive-information proxy \(C(y)\) 与 target 带来的增量闭环成功率存在跨 target 的排序关联；该关联在 target-family 控制后强于无动作重建误差与 target variance/SNR。

不要写“发现了可控性的定义”“证明 action causes target utility”“可普适选择最佳 WAM target”。

## 预算与致命风险

若 3 个训练条件约为 8 GPUh，则：

- 8 targets + action-only、单种子约 24 GPUh；
- 两种子约 48 GPUh；
- 12 targets + baseline、两种子约 69 GPUh；

尚未包含 probe sweep 和闭环 rollout。因而当前预算与正式 predictor claim 不相容。

主要 fatal risks：

- \(C\) 排名在 cross-fit、probe width 或 loss choice 下不稳定；
- action shuffle 后仍有相同 gap，说明 phase/shortcut 泄漏；
- full-future 与 residual 被错误当作独立 strata；
- 高 \(C\) 只降低 world loss，却不改善闭环 policy；
- 关系完全由 motion/semantic family 驱动，leave-one-family-out 后消失；
- routing/head/budget 差异解释收益，正如 DreamWAM 已显示；
- \(C\) 与 SNR/reconstruction loss 共线，无法证明增量预测力；
- 只做两极实验却宣称 monotonic target-selection law。

因此建议保留 C02 为“高风险、强先验重叠的诊断 pilot”，但在没有至少 8 个独立 target 条件前，不应升级为正式主 claim。全程未修改文件、未使用 SSH、未启动计算任务。
