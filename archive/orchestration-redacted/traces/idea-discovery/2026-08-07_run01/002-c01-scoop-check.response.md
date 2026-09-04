## C01 独立查新结论

检索截止：2026-08-07；覆盖 2018–2026。  
结论：**PARTIAL（对应 scoop-check Level 2 — High Overlap）**。

未发现任何工作已经实现完整组合：

\[
\text{future / equidistant-past}\times
\text{intact / distribution-preserving shuffled action}
\]

并在同一 VLA/策略架构、数据、参数、步数、target tokens、FLOPs 下，以 2×2 交互项同时检验策略表征和配对闭环控制。因此没有被完整 scoop。

但各组成部分已有很强先例，尤其是：

- CheckVLA 已经重训了保持动作边际分布的 action-shuffled world model，并报告闭环扰动成功率；
- VLAFlow 已经在固定 VLA 架构、数据和训练预算下比较辅助目标，并做保持目标边际分布的 batch shuffle；
- SelfWAM 已经把干净示范动作显式送入 future predictor，并做方向性动作扰动与闭环策略消融；
- CoCo、AquaJEPA 已用 inverse/zero/counterfactual actions 约束或诊断 action-causal future prediction。

所以 C01 只能定位为“新诊断协议/负控制设计”，不能声称新的 future-prediction 方法，也不能仅凭该交互项声称已识别表征的因果中介机制。

## 检索

代表性查询：

- `vision language action future latent prediction shuffled action past prediction causal control`
- `robot imitation learning predictive representation past future action conditioned`
- `temporal reversal action shuffle counterfactual future prediction difference in differences robot policy`
- `"SelfWAM" action perturbation`
- `"VLAFlow" future latent alignment`
- `"FLARE" future latent representation alignment`
- `"AquaJEPA" action margin`
- `"shuffled actions" "future prediction" robot`
- `"past" "action-shuffled" world model robot`
- `"future" "past" "shuffled actions" robot policy`
- `"difference-in-differences" auxiliary objective robot policy`

先用 arXiv、OpenReview、DBLP、OpenAlex、Semantic Scholar、Crossref 发现候选，再仅以 arXiv 全文、OpenReview/官方会议论文、官方代码库核验。Semantic Scholar 有两次 429，arXiv 有一次 503 重试，OpenAlex 有 429/504 重试；最终结论未依赖失败接口或聚合摘要。

## 新颖性四轴

- Problem framing：在固定 VLA/策略家族内，区分 future auxiliary 的真实动作–结果价值与一般正则化、目标难度、轨迹阶段相关性。
- Core mechanism：时间方向 × 动作配对的预算匹配 2×2 训练矩阵，并估计交互项。
- Key insight：若只有 future-intact 相对三个安慰剂产生额外表征和闭环收益，则收益具有“未来方向 + 动作–轨迹对齐”双重特异性。
- Domain：离线机器人模仿学习/VLA，共享表征，LIBERO 类配对闭环评估。

## 最接近工作

| 工作 | 关键重合 | 缺失项 | 分类 |
|---|---|---|---|
| [CheckVLA](https://arxiv.org/html/2607.26789) | 重训 observation-only 和保持动作 token 边际的 action-shuffled world model；timely recall 77.9%/37.9%，扰动成功 47.6%/31.0% | 独立冻结 verifier，不塑造 VLA 表征；无 past 行、完整 2×2 或交互估计 | 最强局部撞车 |
| [VLAFlow](https://arxiv.org/html/2607.01586) | 同一 pi0-style 架构、动作空间、数据、步数、优化器下比较 action/language/future-latent 目标；语言 target 在 batch 内置乱并保持词表、长度和边际分布 | shuffle 作用于语言目标，不是 future predictor 的动作身份；无 past 行 | 强方法学先例 |
| [SelfWAM](https://arxiv.org/html/2608.00725) | 干净示范动作只供 future visual queries 使用；方向扰动与连续动作插值检验 action sensitivity；闭环策略评估 | 无 shuffled-action 训练、past target 或 2×2 | 强机制先例 |
| [FLARE](https://arxiv.org/html/2505.15659) | 共享 DiT 内 action tokens 与 future tokens 交互，预测 t+H latent；闭环策略收益 | 无 past/shuffle，且未做完整等 FLOPs 因果矩阵 | 部分重合 |
| [AquaJEPA](https://arxiv.org/html/2607.29393) | action-conditioned future JEPA；executed action 对 inverse/zero action 的 margin；统一 planner、120 个配对环境 | 不是共享 VLA policy；无 past/shuffle；对 state-only 的闭环优势统计上未决 | 部分重合 |
| [dWorldEval](https://arxiv.org/html/2604.22152) | batch-wise derangement 保持动作边际，检验 action–future 依赖 | 只在测试时诊断世界模型，不是策略共训 | 部分重合 |
| [CoCo](https://arxiv.org/html/2608.04653) | reference/inverse/zero-action 三分支，inverse rollout 回到初态，直接针对动作因果捷径 | 反向回滚是可逆性约束，不是 past placebo；无 VLA 表征或 factorial 设计 | 部分重合 |
| [Hallucination in World Models](https://arxiv.org/html/2606.27326) | 用 batch-shuffled actions 的 one-step error ratio 诊断 action marginalization，并关联 MPC | 仅世界模型诊断，无 past/策略共训 | 邻近 |
| [Past-Token Prediction](https://arxiv.org/html/2505.09561) | 同一扩散策略联合预测过去和未来动作，显著改善闭环长历史任务 | 过去 target 是已执行动作，不是 past observation latent；无 shuffle/因果交互 | 时间目标先例 |
| [TRASS](https://arxiv.org/pdf/1810.01128) | 反转状态轨迹用于机器人控制 | 明确不对反向轨迹使用动作，因为动作通常不可逆 | 时间反转先例 |
| [SPR](https://arxiv.org/abs/2007.05929) | action-conditioned 多步未来 latent self-prediction 改善 RL 表征和控制 | 无负控制矩阵 | 基础邻近 |
| [TACO](https://proceedings.neurips.cc/paper_files/paper/2023/file/96d00450ed65531ffe2996daed487536-Paper-Conference.pdf) | 当前状态 + 动作序列与对应未来状态做 InfoNCE，学习控制相关 state/action 表征 | 负样本是 future-state batch negatives，不是 matched action shuffle；无 past | 基础邻近 |
| [V-JEPA 2](https://arxiv.org/html/2506.09985) | action-conditioned JEPA world model与真实机器人图像目标规划 | 独立规划模型，无 VLA auxiliary factorial test | JEPA 邻近 |

两个特别重要的事实：

- VLAFlow 的 MindWPI 明确禁止 future-latent tokens 关注 noisy action tokens；因此它的 latent predictor 本身并没有检验动作身份。
- SelfWAM 中“只加 action-conditioned future RGB”从 FastWAM 的 91.84% 降到 90.80%；加入 self-mask 后才到 92.62%。这直接说明“动作条件 future 本身改善策略”不能作为既定事实。

## 最窄可辩护主张

> 截至 2026-08-07，我们未发现先前工作在同一预算匹配的 VLA 策略家族内，将目标时间方向与逐样本动作–轨迹配对正交操纵，并用训练臂间的 2×2 factorial interaction 同时检验表征诊断和配对闭环成功；该协议测试的是收益是否对“future × intact action–trajectory alignment”具有特异性，而不是单凭交互项证明动作因果世界模型或表征中介。

Delta：

> 不同于 CheckVLA 只比较 aligned 与边际保持的 action-shuffled 执行 verifier，C01 再加入等距非因果 past target，并在共享、等预算的 VLA 共训框架中估计时间方向 × 动作配对交互，从而检验时间箭头特异性，而不只是动作依赖性。

建议全文用“**intact vs shuffled**”，不要在 past 行使用“correct action”。

## 致命或近致命方法问题

1. **past-correct 动作语义不成立。**

   - 若 past target z(t-h) 配当前未来动作 a(t:t+h-1)，动作不可能导致过去；只能称 intact/observed-associated，而非 correct。
   - 若配前一段动作 a(t-h:t-1)，任务变成由当前状态和历史动作做逆动力学/历史重建，不再是无因果效应的 placebo。
   - 若把动作反序或取逆，LIBERO 的抓取、接触、遮挡和开合状态通常不可逆。TRASS 正因反向转移通常不成立而明确避免给反向模型输入动作。

   最可修复的定义是：past 行仍接收与该时刻真实样本绑定的未来 action chunk，但把它定义为 negative-control outcome；结论只能依赖负控制假设。

2. **等时间距离不等于等难度。** 过去可能已在历史输入中、可直接复制；也可能因遮挡和不可逆事件比未来更不可恢复。future 通常具有多模态不确定性。相同维度、方差、token 数和 FLOPs 不会匹配条件熵或 Bayes risk，交互可能只是 headroom 差异。

3. **shuffle 同时引入标签噪声和条件分布外样本。** 保持边际分布不等于保持 p(a|o,l,phase)。future-shuffle 更差可能因为矛盾监督，而非 future-intact 更好。没有 no-action/dummy 控制时，正交互无法区分“正确分支获益”与“置乱分支被独特伤害”。

4. **把统计量叫 DiD 容易过度因果化。** 这里是随机化训练臂的 2×2 factorial interaction，不是有平行趋势假设的经典前后期 DiD。代数相同，但建议正文称“factorial interaction contrast”。

5. **表征中介不能由 probe + 闭环同号证明。** 训练臂可因随机分配支持“目标改变了表征/控制结果”，但不能证明控制收益由该表征变化中介；至少需要 activation/subspace intervention 或正式 mediation，线性 probe 仅是可解码性。

6. 若 past latent 已包含在策略历史输入中，存在直接 target leakage，应立即否决该实现。四格各一训练 seed 只能作为可行性 pilot，不能支撑交互推断。

## 必需控制

- action-only、dummy-head/noise-target、no-action predictor 三个额外基线；每个 2×2 cell 都报告相对 action-only 的变化。
- past target 对策略输入严格不可见；冻结同一 target encoder。
- clean/intact action 只能进入 auxiliary predictor，不能泄漏到 action-prediction queries，可采用 SelfWAM 的单向 attention。
- shuffle 使用 derangement，并按 task、instruction、阶段、proprioception、速度/动作范数、chunk mask 分层或最近邻匹配；同时报告 conditional-support 距离。
- 每格报告 action-agnostic Bayes proxy、初始/最终 world loss、target variance、current-target similarity、梯度范数和梯度方差。
- 至少 3–5 个独立训练 seed；闭环使用相同 simulator initial states 和 common random numbers，episode 嵌套于 training seed，按 seed/task 分层 bootstrap。
- 二元 success 用配对风险差的 factorial interaction；避免把每个 rollout 当独立训练重复。
- 预注册一个表征指标和一个闭环指标；表征指标最好是跨任务检验的 action–outcome binding，而非训练内 probe。
- 只有当 future predictor 在严格 holdout 上优于 persistence、observation-only 和 action-agnostic predictor，且 shuffle sensitivity 合理时，才解释策略交互。
- 在不可逆/遮挡事件上单独分层；若交互只来自 gripper/contact 段，应归因于 past-target 不可逆性，而不是 future 的独特因果价值。

