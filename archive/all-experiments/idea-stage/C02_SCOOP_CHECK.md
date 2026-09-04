# C02 查新结论：Controllability-Matched Target Ladder

## 结论

- Verdict：**PARTIAL / Level 2 — High Overlap**。
- 精确组合尚未被完整覆盖，但贡献只能压缩为 **训练前 target 排序诊断**，不能称为新的 controllability 定义、future target 或 WAM 方法。
- 当前状态：**REVISE / NO-RUN**。当前 8 GPUh 预算只能支持少数条件的证伪型 pilot，不能支撑正式排序规律。

## 最窄可辩护问题

对等维、白化 target，用独立 held-out 数据拟合等容量的 action-masked 与 action-conditioned probes，定义

\[
C(y)=L(y\mid o,l)-L(y\mid o,l,a),
\]

再前瞻检验该 action-conditional predictive-information proxy 是否比 reconstruction loss、variance/SNR 或 target family 更能排序 target 带来的增量闭环收益。

若使用 Bayes-optimal log loss，\(C(y)\) 等价于条件互信息；MSE 下只能解释为动作对条件均值的风险下降，不能称为因果 controllability。

## 已有工作的挤压

- FLARE 已比较 action-aware 与普通视觉 target，并显示 action-aware embedding 更有利于 policy。
- *Reconstruction or Semantics?* 已用 inverse-dynamics action recoverability 衡量 world-model latent 的控制相关性。
- EgoWAM、Motion Image Diffusion、DreamWAM、VLAFlow 已比较不同 future target 或 route 对策略的影响。
- predictive information、action-sufficient representation 与通用 auxiliary-task selection 都有成熟先例。

因此剩余 delta 仅是：**在 target-policy 训练前，用统一 risk gap 前瞻排序尚未训练的 target，并与竞争预测变量做严格比较。**

## 样本量硬约束

- 4 个 target 即便 Spearman 完美排序，双侧精确 \(p=0.0833\)，无法达到 0.05。
- 数学硬下限是 5 个 target-level units，但仅能检验极强完美排序。
- 勉强可辩护下限：4 个 \(C\) strata × 每层 2 个独立 target = **8 targets**。
- 若要证明优于 reconstruction/SNR/family，建议最低 **12 targets**，并做 target-level permutation、partial Spearman 与 leave-one-family-out。

task、seed 与 rollout 只能作为重复测量，不能把有效 target 样本量从 4 伪增大。

## 进入正式实验前的硬要求

1. action-only、near-zero-C static/current、独立噪声 target、正交旋转阳性控制、action-shuffled probe placebo。
2. 统一 target 维度、白化、token 数、head 参数、loss weight、steps、优化器与近似 FLOPs。
3. episode/time strict holdout、cross-fitted \(C\)，且有/无 action probes 完全等容量。
4. 预注册 target 排名，并至少做一次 leave-one-target-family-out prediction。
5. 明确 auxiliary head 是否看到 ground-truth/noised action；否则高 \(C\) 的含义会改变。

## 当前预算判断

若 3 个训练条件已约 8 GPUh，则 8 targets + action-only 单 seed 约 24 GPUh，两 seed 约 48 GPUh；12 targets 两 seed 约 69 GPUh，且尚未计入 probes 与闭环评估。因此 C02 在当前预算下不能升级为正式主 claim。

完整查新原文与来源矩阵见 `.aris/traces/idea-discovery/2026-08-07_run01/004-c02-scoop-check.response.md`。
