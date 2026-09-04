# Final Proposal：Causal Progress Harm Audit for Long-Horizon VLA

## Problem Anchor

- 用户的 π0.5 在长时多阶段任务中会遗忘、重复、错误推进、误判完成，并在局部失败后继续执行错误阶段。
- 本项目只先研究其中一个可隔离瓶颈：**错误进度状态如何改变后续策略行为**。遗忘生成、已写入状态的撤销和 recovery competence 不在首轮方法 claim 内。
- 不以普通长上下文、文本摘要、generic verifier+replan、WAM 视频生成或新 action head 作为创新。

## 最终研究命题

在一个明确消费 progress state 的冻结 VLA 接口中，先用序列化环境状态的配对干预测量：truth-confidence 匹配的进度写入错误是否具有显著、稳定且可预测的 policy-conditional harm heterogeneity。只有该 finding 成立，才训练 cost-sensitive verifier；否则停止方法路线。

## 两个不可混淆的因果量

1. **Admission effect**：`commit(candidate assertion)` 对 `hold previous state`。
2. **Correction effect**：`wrong task state` 对 `gold corrected state`。

两者均固定 environment snapshot、policy、recovery、task memory、动作预算、horizon 和随机数；分别报告，不合并成含混的“poison score”。

## P0：接口与问题查杀

三组闭环条件：无 progress state、oracle truthful progress state、受控 corrupted progress state。

- 若 oracle state 不能明显改善 next-subtask/action validity 或端到端成功，则 π0.5 的主要瓶颈不在 progress interface，停止。
- 若 corrupted state 不能稳定复现错误推进、跳步或重复，则 commit/suppress intervention 没有生态效度，停止。

公开 OpenPI 未必包含论文中的完整高层语义接口，因此必须先明确 assertion 的载体：现有高层 subtask token、policy-facing task-context token，或固定语言前缀。整个 P0–P2 使用同一接口，不得中途改变。

## P1：Causal Progress Harm Audit

对自然边界和失败边界保存完整 snapshot，仅改变一个 progress assertion。使用 common random numbers 产生配对未来，分别测：

- 固定 horizon 成功损失；
- 无效、重复、跳步动作；
- false stage advancement；
- correction delay；
- oracle-action disagreement（仅分析，不作为唯一标签）。

主要统计量：paired effect CI、跨 seed 符号稳定率、top-k harm concentration、跨 horizon/task 排名稳定性。factual oracle 只作为 ceiling，不声称 regret 超越 truth oracle。

核心 finding 的成立条件：在相同 truth-confidence strata 内，错误写入的控制伤害仍显著异质；且这种异质性不能被步骤位置、谓词类型或一步 action divergence 完全解释。

## P2：Conditional Method

仅在 P1 通过后训练同一轻量 verifier/head 的两个版本：

- truth-only：统一 BCE / calibrated selective prediction；
- harm-aware：truth loss 保持不变，对 false-positive loss 按部署条件下可预测的 counterfactual harm 加权或排序。

运行时仍输出事实性 completion decision。false-beneficial assertions 不计为收益，不允许为了操纵 policy 提交假信息。

成功必须满足：在相同 false-commit risk 与 coverage 下，harm-aware 版本降低高代价 false advancement，并在 held-out trajectories/tasks 上改善闭环；若 short-horizon critic 或 one-step action divergence 等价，则采用简单 proxy，删除新方法 claim。

## WAM 决策

从主方案删除。P0–P2 不需要 WAM。只有简单判别模型无法预测 harm、且动作条件多模态 future 明显必要时，才把 task-latent WAM 作为后续备选，并做 matched-budget necessity test。

## 贡献边界

- 若只有 P1 成立：贡献是 diagnostic/finding-first benchmark，不声称新 VLA 架构。
- 若 P1、P2 均成立：主贡献是 VLA progress false-positive 的 policy-conditional cost-sensitive verification。
- 不声称解决全部长期记忆、自动 recovery 或通用 task belief。

## 当前裁决

`RETHINK / PILOT GO`。这是一个高信息量的研究入口，不是已验证会 work 的最终方法。
