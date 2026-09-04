# Research Proposal：Policy-Conditional Commit Regret for Long-Horizon VLA

## Problem Anchor

- Bottom-line problem：π0.5 在长时多阶段任务中会遗忘已完成事项、错误推进、误判完成，并在局部失败后继续执行错误阶段。
- Must-solve bottleneck：可靠估计、验证并纠正任务进度，且不能把普通长上下文、文本摘要或 generic verifier+replan 重新包装为创新。
- Non-goals：不追求新 action head、通用视频生成、完整 world model、通用 planner 或单纯更高 progress classification accuracy。
- Constraints：π0.5 可作主 baseline，也可换第二 VLA；有 4×A100 和真实机器人，但本阶段不消耗 GPU/机器人；WAM 可选且必须证明必要。
- Success condition：在匹配 truth accuracy、提交率、数据、参数和推理预算后，方法显著减少高代价错误推进并改善闭环成功；否则停止。

## Technical Gap

已有 memory、latent belief、completion head 和 outcome verifier 主要优化历史保留、状态真值、当前置信度或失败检测。它们没有回答：某个进度断言即使同样可能出错，对固定 VLA 的未来控制代价是否相同。若不同，只按 truth loss 训练会把验证预算浪费在低伤害误差上，并遗漏少量会级联破坏后续动作的写入。

## Method Thesis

用同一 simulator snapshot 的 `commit/suppress` 配对干预定义候选进度断言对固定 VLA 的多步控制 regret，并在事实一致性硬约束下蒸馏轻量 admission gate，可比纯 truth/calibration gate 更有效地阻止高代价错误推进。

## Contribution Focus

- Dominant contribution：VLA-specific paired-snapshot commit-regret supervision 与其是否提供 truth accuracy 之外信息的因果验证。
- Supporting contribution：Causal Progress Corruption Atlas，报告不同断言错误的伤害分布与 persistence horizon。
- Explicit non-contributions：不发明 decision-focused learning、selective prediction、memory graph、WAM 或 recovery policy。

## Proposed Method

### Complexity Budget

- Frozen：VLA executor、action head、recovery policy、task interface、rollout horizon。
- New trainable component：一个小型 harm/gate head。
- Intentionally excluded：回滚图、多模型 planner、视频解码器、联合训练 recovery。

### System Overview

`before/after observation + executed chunk + candidate assertion + truth uncertainty → harm head → commit / abstain → frozen VLA`

训练标签来自：

`same snapshot → do(commit) / do(suppress) → paired future rollouts → ΔJ`

### Core Mechanism

- 输入：部署时可见的前后观察、proprioception、action chunk、候选断言及 verifier uncertainty。
- 输出：未来伤害分布或排序分数；gate 在匹配 coverage 下决定提交。
- 训练：pairwise ranking/regression loss 预测 paired `ΔJ`，外加 truth constraint。按 snapshot 分组，避免 rollout seed 伪重复。
- 推理：只对不确定候选计算 harm；明显真/假由 truth constraint 处理。

### Failure Handling

- 若 WAM/critic prediction OOD：abstain，不写入。
- 若 harm 与 truth 冲突：truth constraint 优先，禁止 false-beneficial 写入。
- 若策略或 checkpoint 改变：重新校准；不声称 policy-independent。

## Claim-Driven Validation Sketch

### Claim 1：commit regret 提供 truth 之外的控制信息

- Minimal experiment：50–100 snapshots、3 个长任务、每点 4–8 paired seeds；比较 oracle truth 与 oracle regret。
- Decisive metrics：true-harmful 比例、ΔJ 符号稳定性、oracle advantage、harm concentration、truth–harm conditional mutual information。
- Stop：未达到预注册 headroom 即终止。

### Claim 2：可部署 gate 恢复 oracle advantage 的有意义比例

- Baselines：calibrated truth/SelectiveNet、SeqVLA-style completion、step position、one-step action divergence、short-horizon critic。
- Metrics：end-to-end success、false advancement、invalid/repeated actions、risk–coverage、oracle advantage recovered、latency。
- WAM necessity：仅作为可选 predictor；不优于 discriminative critic 就删除。

## Compute & Timeline Estimate

- Oracle pilot：主要是 simulator rollout；约 1–2 天工程准备，随后 100–500 GPU rollout-hours，取决于环境并行和 VLA 推理速度。
- Gate training：小头训练预计 10–40 A100 GPU-hours/配置，3 seeds 后再扩大。
- Real robot：仅在 simulation/recorded pilot 通过后，采用用户批准的安全扰动协议；本计划不自动执行。
