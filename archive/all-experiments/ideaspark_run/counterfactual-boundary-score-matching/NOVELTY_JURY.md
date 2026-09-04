# Boundary Score Matching for Functional-Geometry Counterfactuals：严格查新评审

评审日期：2026-08-31  
评审对象：`phase3_revise/final_candidate.json` 与 `phase4/phase4_expansion.json`  
判定阈值：**novelty 必须严格大于 7.0 才 PASS；7.0 仍为 FAIL。**

## 结论

**Verdict：PASS（仅允许进入小型 E0 证伪实验）**  
**Novelty：7.15 / 10**  
**Naturalness：6.35 / 10**  
**Feasibility：5.9 / 10（E0）；4.8 / 10（按当前 56 A100-GPU-days 完整方案）**

这不是一个“因为没有单篇论文把四个组件写在一起，所以自动算新”的高分。它只以 **0.15 分**越过门槛，原因是最强近邻已经覆盖了大约一半机制：`Can Explicit Physical Feasibility Benefit VLA Learning?` 已经构造“原始参考轨迹会被新障碍干扰、但同一目标仍可通过重新规划完成”的 counterfactual 数据，并在扩散 VLA 训练时只对发生 clearance violation 的时间步施加几何损失。因此，候选的主要剩余新意不是“几何反事实”或“局部违规监督”，而是下面这个耦合命题：

> 对同一动作因最小功能几何编辑而翻转有效性的样本，用冻结参考策略定义的、只落在首个违规段上的正负 score/flow preference 改变条件动作分布，同时显式约束违规段之外的行为和每个可行替代模式；并检验全局可行性训练是否提高可靠性却损伤可行模式覆盖。

这个耦合具有非平凡交互：局部负偏好会通过共享参数泄漏到整个 action chunk，且拒绝一个无效模式可能顺带压掉邻近的有效少数模式；`L_out` 与 mode-wise retention 因而不是完全独立的装饰项。不过，首个违规段的选择、compiler mode roster 和逐时间点因果恢复条件目前明显偏人工，决定了它只能得到边缘 PASS，而不是 8 分级 Idea。

## 证据边界

- 本次重新核验了下表中的官方 arXiv 页面；对最接近的物理可行性论文、Metamorphic Testing、CFNBC、Dream2Fix、World2Act 等还检查了官方 PDF 的方法正文。
- 2026 年 4 月论文 `Can Explicit Physical Feasibility Benefit VLA Learning?` 是此前检索中被低估的最强近邻；它显著压低本候选分数。
- 查新覆盖到 2026-08-31，但不能把“没有检索到 exact match”解释为数学意义上的不存在。当前结论是 reviewer-defensible 的有限证据判断，不是绝对优先权证明。
- 当前方法实质上是 **simulator-supervised VLA post-training**。部署时没有 WAM，训练时用的是 RoboTwin 物理模拟器与几何 oracle；除非后续真的用 learned action-conditioned world model 产生或校验边界，否则不要把论文包装成 VLA×WAM。

## 四个原子机制的独立判断

### M1｜最小、任务相关的几何编辑使同一动作从有效变无效，同时编辑场景仍可解

**独立新颖性：5.8 / 10。**

这不是空白。最强近邻先在无障碍场景规划参考轨迹 `pi-`，把障碍放到该轨迹 swept path 附近使其碰撞或接近碰撞，再从同一起点到同一目标重新规划可行 `pi+`；这已经满足“同一原动作受几何改变干扰、修改后任务仍可解”的主要语义。候选真正多出的只是：

- 从离散 compiler 参数中选“最少 increments”的编辑；
- 保留并训练使用同一无效动作，而近邻只把它用于构造障碍、最终数据不保留 `pi-`；
- 试图跨多个功能几何任务，而不是单一 close-obstacle reaching。

因此不能把 M1 单独列为论文主创新。“最少 compiler increments”也不等于连续几何意义或任务影响意义上的最小编辑，只能称为 **compiler-minimal**。

### M2｜首个连续违规段 `M`

**独立新颖性：5.5 / 10。**

最强近邻已经在 action chunk 的每个未来时间步和机器人 link 上计算 signed distance，并且只对 active violations 求平均，而不是给整段轨迹同一个安全标签。候选选择“首个连续 true run”并增加单时间区间碰撞几何恢复 replay，是更强的时间归因，但仍是局部违规监督的增量细化，不是全新范式。

此外，当前要求 `q_t>0` 恰好只在 `M` 成立、在 `P∪S` 恰好为零，过于理想化。接触和动力学具有历史依赖，恢复某一时刻的几何可能改变后续状态；真实可用的指标应是因果影响集中度，而不是精确零/非零等式。

### M3｜在 `M` 上做冻结参考校正的局部 score/flow preference，而非测试时 reranking

**独立新颖性：7.4 / 10。**

这是组合中最有价值的部分。已核验工作分别存在：

- 训练期 active-violation 几何 hinge loss；
- 扩散模型的 reference-adjusted preference 优化；
- VLA/WAM 的部署时 rollout 与候选重排序；
- VLA 的 flow-field causal projection。

但在本次 primary-source 核验范围内，没有发现把“同一动作的几何有效性翻转”转成“首个违规 action segment 上的冻结参考正负 denoising-error preference”，并保持推理接口不变的工作。它不是 WAM reranking，也不是简单的可微 SDF penalty。

仍需谨慎命名：当前 `r_theta` 是负 masked denoising error surrogate，不是对真实 `log p_theta(a|c)` 的精确 score。论文应称 **reference-adjusted masked denoising preference**，除非补出概率/score 等价推导。

### M4｜显式保护替代可行模式和 `P/S` 行为

**独立新颖性：7.3 / 10（限定于几何可行性 VLA post-training）。**

Diffusion Policy 本来就以多模态动作分布为优势；Factorized Diffusion Policy 已显式让不同模块表示不同 sub-modes，并以减少 adaptation forgetting 为动机；CFNBC 也使用 response-space coverage 选多样修复数据。因此“保护模式”不是一般机器学习意义上的新概念。

尚有空间的是：在 **同一个几何有效性翻转** 中，把无效旧模式压低的同时，把 edited scene 的每个 compiler-enumerated positive mode 当作独立保护对象，并将 worst-mode success、roster coverage、complement drift 作为可靠性训练的必要伴随指标。这个诊断命题比 `L_alt` 公式本身更有论文价值。

## 逐篇 exact-mechanism 对照

符号：`Y`=实质覆盖，`P`=部分覆盖，`N`=不覆盖。列顺序为 M1 / M2 / M3 / M4。

| Primary source | M1 | M2 | M3 | M4 | 最接近之处与关键差异 |
|---|:---:|:---:|:---:|:---:|---|
| [Can Explicit Physical Feasibility Benefit VLA Learning?](https://arxiv.org/abs/2604.17896) | Y | P/Y | N | N | 最强近邻。原轨迹附近放障碍使参考动作受干扰，保持起点/目标并重规划可行解；训练时只惩罚 action chunk 中 active clearance violations。没有 compiler-minimal pairwise dataset、冻结参考正负 preference、首个 contiguous run 与 mode retention。 |
| [Metamorphic Testing of VLA-Enabled Robots](https://arxiv.org/abs/2602.22579) | P | N | N | N | 对任务输入做保持或应变的变形，再比较 VLA 轨迹；MR5 要求目标平移引起成比例的轨迹变化。它是测试/故障发现，不做 counterfactual policy post-training，也不定位首个违规段。 |
| [CFNBC / Counterfactual Action Sensitivity Coverage](https://arxiv.org/abs/2607.27261) | N | N | N | P | 用 task-preserving 视觉 nuisance 配对，要求 expert action 不变；按 action-drift response coverage 选修复窗口，再用 inherited action BC。它研究“变化后动作应保持”，而本候选研究“几何变化后同一动作应失效”；coverage 思想相邻。 |
| [CofactVLA](https://arxiv.org/abs/2608.04396) | N | N | P | N | 在单次 forward 中建立 language-masked counterfactual branch，用 OPG 把 factual velocity field 从视觉偏差方向投影出去，并用 CCR 去混杂。它的 counterfactual 是语言屏蔽/视觉混杂，不是物理有效性翻转或时间局部动作 preference。 |
| [Dream2Fix](https://arxiv.org/abs/2603.13528) | N/P | P | N | N | 在生成式世界模型中扰动动作，合成失败视频与确定性 correction，按 failure stage 输出恢复。它改变动作而非几何，不把同一动作在成对场景中的有效性变化用于 score post-training，也不保护可行模式。 |
| [Ambient Diffusion Policy](https://arxiv.org/abs/2606.12365) | N | N/P | N | P | 通过 diffusion noise time 选择性使用 suboptimal data，并利用 action data 的 global-to-local hierarchy。这里的“local”是扩散噪声尺度，不是 action-chunk 的物理违规时间段；它提供了避免坏数据污染的邻近原则。 |
| [PhysReflect-VLA](https://arxiv.org/abs/2606.27146) | N | P | N | N | 部署时 Feasibility Operator、Action Explanation Operator 与 LLM reflection 过滤/纠正候选动作。属于在线检查与恢复，不是训练期局部 score preference。 |
| [GEAR-VLA](https://arxiv.org/abs/2606.08530) | N | N | N | N/P | 用语义对齐 3D backbone、coarse-to-fine action learning 和 embodiment canonicalization 提升几何泛化；没有 counterfactual validity flip、局部 credit 或 mode-preserving feasibility post-training。 |
| [AffordanceVLA](https://arxiv.org/abs/2606.06155) | N | N | N | N/P | Which2Act / Where2Act / How2Act 预测对象、2D affordance 与 3D 几何中间表征。解决 perception-action grounding，不监督同一动作的可行性边界。 |
| [World2Act](https://arxiv.org/abs/2603.10422) | N | N | P | N | 用 shared video-action latent 与 contrastive alignment 把 WM dynamics 迁移到 VLA post-training，避免 pixel rollout artifact。它是 latent dynamics alignment，不使用失败动作、物理违规 mask 或正负 reference preference。 |
| [RoCoDA](https://arxiv.org/abs/2411.16959) | N/P | N | N | P | 对 task-irrelevant state 子集做 causal-invariant 编辑，并用 SE(3) equivariance 同步变换动作。其目标是保持/等变动作，不是让同一动作因功能几何变化而失效；证明 counterfactual augmentation 本身并非新点。 |
| [Surface Constraint Policy](https://arxiv.org/abs/2605.31321) | N | N/P | N | N | 从示教编码 free-form surface constraint，扩散策略给 intention，再映射到 surface-constrained DMP，保证动态可行与接触稳定。它直接结构化约束控制，不做成对边界学习。 |
| [Learning Action Manifold](https://arxiv.org/abs/2605.11832) | N | N | N/P | P | 用多视角 latent 与 3D guidance 构建 G3T，并直接预测 valid action manifold。与“可行动作集合”概念相邻，但没有同一动作 validity flip、局部 reference preference 或逐模式保留审计。 |
| [DREAMSTEER](https://arxiv.org/abs/2607.02865) | N | N | N | P | 冻结 VLA 采样多个 action chunks 和 primitives，经 action-conditioned latent WM rollout 和 value model 在部署时排序。候选明确不做测试时 reranking，训练接口不同。 |
| [Factorized Diffusion Policy](https://arxiv.org/abs/2512.21898) | N | N | N | P/Y | 把复杂动作分布分解到不同 diffusion sub-mode 模块，支持增加/微调组件并缓解遗忘。它威胁“mode preservation 是新思想”的表述，但没有几何边界局部纠正。 |
| [Diffusion Policy](https://arxiv.org/abs/2303.04137) | N | N | N/P | P | 奠定 continuous action score modeling、receding horizon 和多模态动作分布；候选必须把新意放在 boundary-conditioned post-training，而不能声称 score-based multimodal action 本身新。 |

## Closest exact mechanism

最接近的是 **Can Explicit Physical Feasibility Benefit VLA Learning? An Empirical Study**，不是 DreamSteer、CofactVLA 或 Metamorphic Testing。

它与候选共享：

1. diffusion-based VLA；
2. 训练期使用机器人运动学和场景几何，推理期仍只用 RGB 与语言；
3. counterfactual obstacle construction：使无障碍参考轨迹在新几何下碰撞/近碰撞，同时保留同起点同目标的可行重规划；
4. action-time-local active violation penalty；
5. 用 obstacle perturbation 评估几何 OOD。

候选尚未被它覆盖的组合是：

1. 保留同一无效动作作为显式 negative，并把最小编辑审计成训练样本；
2. 用首个 contiguous violation run，而非全部 active violation points；
3. 使用冻结 reference 校正的 positive-vs-negative denoising preference，而非可微 signed-distance hinge；
4. 约束 mask complement drift；
5. 对 edited scene 中多个可行模式逐模式保护，并把 reliability-vs-coverage sign split 作为主实验结论。

一句话 delta：

> Unlike `Can Explicit Physical Feasibility Benefit VLA Learning?`, which places an obstacle near a reference path and backpropagates a signed-distance hinge over all active violations, BLSM retains the invalid reference as a paired negative, applies a frozen-reference denoising preference at the first certified violation run, and audits/anchors every edited-scene feasible mode, targeting higher edited-scene reliability without the mode-coverage loss of aggregate feasibility shaping.

## 组件重叠与联合差异是否 reviewer-defensible

### 1) 同一动作 validity flip：**只能作为数据协议改进，不能单独 defend novelty**

`2604.17896` 已有非常接近的 counterfactual construction。若论文写“首次用任务仍可解的几何改变使原动作失效”，会被直接反驳。可 defend 的版本必须写成“保留 identical invalid reference、compiler-minimal audit、paired preference estimand”。

### 2) 首个连续违规段：**单独较弱，作为 credit-assignment instrument 才成立**

active-violation temporal loss 已存在。首个 run 的价值必须由 mask permutation、all-active-vs-first-run、whole-chunk 三者的 matched ablation 证明；否则只是一个阈值/掩码选择。

### 3) reference-adjusted local score/flow preference：**最强且可 defend**

当前查新没有发现 exact match。关键是它必须真的比已有的 differentiable feasibility loss 更好，而不是换一种写法得到相同效果。比较基线必须直接复现 `L_geo`，不能只和“whole-chunk binary preference”比。

### 4) alternative-mode 与 P/S protection：**诊断新意强于 loss 公式新意**

reference anchoring、distillation、worst-group objective、mode balancing 都是已知工具。真正的贡献是把“几何安全 tuning 是否毁掉仍可行模式”变成 paired、可测、可证伪的 VLA 问题。若 global feasibility baseline 并不降低 roster coverage，则论文 hook 消失。

## 最强致命反对意见

### 反对 1｜正轨迹与负轨迹在 `M` 上没有时间语义对齐

`M` 是由无效动作 `a0` 的首次违规时刻定义的，却被直接拿来截取每条可行替代动作 `p_ik` 的相同时间索引。不同 grasp、approach homotopy 或 contact order 可能在相同 index 处处于完全不同的技能阶段。此时 preference 比较的不是“同一边界处可行 vs 不可行动作”，而是两个不相干阶段的动作；这是当前最危险的方法学缺陷。

**必须修复：** 为每个 positive mode 建立事件/相位对齐映射 `phi_k(M)`，或者只比较在首次边界前共享同一状态前缀的 branched alternatives。若无法构造这种对齐，M3 的因果叙事不成立，novelty 评分应降到 6.x。

### 反对 2｜“首个违规段是因果段”的精确判据不自然

候选要求逐时刻恢复原几何后 `q_t>0` 恰好只出现在 `M`，而其他时间恰好为零。接触动力学、控制闭环和数值模拟都使这个精确等式很难成立。若按此硬筛，可能只保留极少、极人工的 pair。

**必须修复：** 改成预注册的集中度阈值，例如 `sum_{t in M} q_t / sum_t q_t >= rho`，并报告全部 attempted pairs 与选择偏差；不要把近似影响集中写成 exact causal identification。

### 反对 3｜compiler roster 不等于真实可行模式集合

控制器 seed tuple 只是生成器索引。两个 seed 可能产生同一轨迹模式，一个 seed 也可能产生多种行为；未枚举到的解不能被声称已保护。

**必须修复：** 将 claim 限定为 `compiler-roster retention`，并用轨迹距离/接触事件验证各 mode 的可分性。不要声称“保留所有物理可行模式”。

### 反对 4｜视觉上不可辨识的 collision edit 会让任务信息论上不可学

部署输入没有 `Delta g`、SDF 或 pointmap；如果只改 collision mesh 而 RGB 渲染不呈现相应几何变化，冻结/微调 VLA 都无法判断动作为何应改变。

**必须修复：** 每个 edit 必须同步修改 visual geometry，并通过可见性/遮挡审计；或显式给 policy 几何输入。否则任何提升都可能来自 dataset artifact，任何失败也不能反驳算法。

## Claim ceiling

即使 E0 和后续实验成功，当前设计最多支持：

> 在 RoboTwin compiler 定义、RGB 可辨识、具有事件对齐可行替代动作的 geometry-flip pairs 上，boundary-local reference-adjusted denoising preference 相比 active-violation hinge 与 whole-chunk preference，在相近 invalid-execution reduction 下能更好保留 compiler-roster coverage 与 complement behavior。

当前不能支持：

- “适用于任意功能几何、接触和任务”；
- “保留所有物理可行模式”；
- “首次利用几何反事实训练 VLA”；
- “首次对 action chunk 做局部物理可行性监督”；
- “WAM 赋予 VLA 物理纠错能力”；
- “真实机器人安全保证”。

如果想把 claim 扩到一般 functional geometry，至少需要三类不同约束：纯 clearance、接触建立/保持、目标-容器几何配合；并且要有 held-out task family，而不只是 held-out mesh 参数。

## 最小 non-GPU falsifier

在任何 VLA 训练前，只用 RoboTwin CPU physics/compiler 做 100–200 个 attempted base episodes，至少覆盖 3 个不同约束族。输出完整 attempted-pair ledger，并检验：

1. **Pair eligibility**：原动作在 `g+` 成功、在 `g-` 因预定几何原因失败、`g-` 仍可解、`0<|M|<T`。
2. **Minimality audit**：在 compiler 邻接图中验证没有更少 increments 的 edit 也能翻转 validity；只称 compiler-minimal。
3. **Visual observability**：编辑后的几何在 policy RGB 中可见，且 visual mesh 与 collision mesh 一致；排除仅碰撞层改变和 renderer artifact。
4. **Causal concentration**：用 interval restore replay 测 `q_t`，报告影响是否集中于 M，而不是要求精确零/非零。
5. **Positive alignment**：对每条替代轨迹做事件/相位对齐，检验 `phi_k(M)` 是否对应同一功能阶段。若只能用相同 raw index，则记录错位率。
6. **Roster reality**：每个 pair 至少存在 2 个经过轨迹/事件聚类后仍可区分的 successful modes，并报告模式间距离与每模式样本量。

### Non-GPU kill criteria

满足任一条即停止当前 BLSM 形式：

- eligible pairs 少于 attempted pairs 的 **15%**，或任一约束族低于 **8%**；
- 超过 **10%** 的 accepted edits 在 RGB 中不可辨识，或 visual/collision geometry 不一致；
- `M` 的因果影响集中度中位数低于 **0.60**；
- 超过 **20%** 的 positive trajectories 无法与负轨迹边界做事件/相位对齐；
- 具有至少 2 个实质可分 positive modes 的 pairs 少于 eligible pairs 的 **25%**；
- 所谓不同 mode_id 中超过 **50%** 在轨迹/接触事件空间合并成同一模式。

## E0 GPU 实验与 kill criteria

只有 non-GPU gate 通过后，才进行小型 E0。E0 不应启动 56 GPU-days 的完整计划；使用一个小 action head / LoRA 子集、单一 backbone、2–3 个 task families、3 seeds，并纳入以下五个 matched 方法：

1. ordinary imitation；
2. `2604.17896` 的 active-violation differentiable `L_geo`；
3. whole-chunk positive-vs-invalid preference；
4. first-run local preference、无 complement/mode protection；
5. 完整 BLSM。

必须额外做 `all-active violations` 对 `first contiguous run`，否则不能声称 first-run 必要。

### E0 primary metrics

- edited-scene success；
- invalid-reference execution rate；
- ordinary unedited success；
- complement score/output drift；
- roster mode coverage；
- worst-mode success；
- risk/coverage 或 reliability/diversity Pareto curve；
- mask permutation、pair-identity permutation、no-`L_out`、no-`L_alt`。

### E0 kill criteria

满足任一条即不进入全量训练：

- active-violation `L_geo` 在 edited success 上与完整 BLSM 的差距小于 **3 个百分点**，且 roster coverage / worst-mode 差距也小于 **3 个百分点**；
- global/whole-chunk feasibility tuning 并未造成至少 **5 个百分点** 的 roster coverage 或 worst-mode 损失，则主 hook“可靠性提升伴随模式损失”没有成立；
- first-run 与 all-active-violation mask 的结果差异小于 **2 个百分点**，或 all-active 更优且 drift 不更差；
- mask permutation 或 pair-identity permutation 保留了完整方法相对 whole-chunk 增益的 **50% 以上**；
- 去掉 `L_alt` 后 worst-mode success 与 coverage 变化均小于 **3 个百分点**；
- 去掉 `L_out` 后 complement drift 不显著变差，或完整 BLSM 的 ordinary unedited success 下降超过 **2 个百分点**；
- 参考校正 masked denoising margin 与真实 simulator validity ranking 的 Spearman `rho < 0.30`；
- 三个 seeds 的效果方向不一致，或主要增益仅来自单一 task/geometry family。

## 最终评语

这是一个**可以做 E0、但还不能直接做大规模论文实验**的 Idea。它越过 7.0 的原因不是几何反事实、局部安全 loss 或 mode preservation 各自新，而是将三者组织成一个可证伪的可靠性—模式覆盖实验命题，并采用训练期 reference-adjusted boundary preference，区别于已有的 SDF hinge 和部署时 WAM reranking。

最关键的下一步不是启动四卡长跑，而是先修复 positive/negative 的边界相位对齐，并让 CPU compiler gate 证明：eligible pairs、因果集中段和多个实质可分的 positive modes 确实以非偶然比例存在。若这一步失败，7.15 的 novelty 没有可实现载体，应立即放弃当前形式。
