# Experiment Plan：Causal Progress Harm Audit

日期：2026-08-24

## Claim Map

| Claim | 最低可信证据 | 阶段 |
|---|---|---|
| C0：progress state 是当前 π0.5 长时失败的有效干预接口 | oracle truthful state 改善决策；corrupted state 稳定复现错误推进 | P0 |
| C1：truth-confidence 匹配的 false writes 具有稳定、非平凡的闭环伤害异质性 | 配对效应、跨 seed/horizon 稳定、简单启发式不能解释 | P1 |
| C2：部署可见特征可预测高伤害 false writes | held-out trajectory/task 上预测与校准显著优于 proxy | P2a |
| C3：harm-aware verifier 在相同事实风险与 coverage 下改善闭环 | 相同架构/数据/预算的 truth-only 对照 | P2b |

## P0：接口与 bottleneck 查杀（MUST-RUN FIRST）

### 任务

- 首选用户已经复现且能稳定 snapshot/restore 的 π0.5 评测环境。
- 选择至少 3 个、每个 4–8 个语义阶段的任务：顺序依赖、视觉状态重复、局部失败后仍可继续三类各至少一个。
- 若现有环境无法完整序列化物理状态、RNG、机器人状态与 policy context，则先修复该能力；不直接用真实机器人做因果 twin。

### 三组条件

1. `No-state`：原始 π0.5 接口。
2. `Oracle-state`：提供真实当前阶段/已完成谓词。
3. `Corrupted-state`：只翻转一个完成/阶段断言。

### 指标与 gate

- next-subtask / option validity；
- false advancement、重复或跳步动作；
- 固定 horizon 成功；
- end-to-end success。

GO 条件（预注册后冻结）：oracle-state 相对 no-state 至少满足“成功率 +5 pp”或“无效/重复动作 -20%”之一；corrupted-state 相对 oracle-state 至少让目标失败率增加 15 pp。两项任一不满足则停止该 Idea。

## P1：配对因果测量（MUST-RUN）

### Snapshot 设计

- 先收集 100–200 个 pilot snapshots，按任务、阶段、自然失败/正常边界、assertion truth-confidence 分层。
- 每个 snapshot 生成 admission pair 与 correction pair；唯一干预是 progress state。
- 使用 common random numbers；每点自适应 8–16 paired seeds，直到效应符号 CI 足够或达到上限。
- 主要独立单位是 snapshot；seed 是嵌套重复，不作为独立样本。

### 对照

- factual oracle ceiling；
- truth-only calibrated selector；
- matched hindsight-harm upper bound（在同 coverage、TP/FP 数和 truth-confidence strata 内）；
- step position、predicate type；
- one-step action-distribution divergence；
- short-horizon value critic。

### 指标

- 每个终点的 paired `ΔJ` 与 bootstrap CI；
- sign consistency；
- top-10% / top-20% harm concentration；
- task/horizon 排名相关；
- 在 truth-confidence 分层后的剩余可解释方差；
- false-beneficial 比例（只报告，不计作收益）。

### GO / NO-GO

进入 P2 至少满足：

1. top-20% false writes 占总伤害 ≥50%；
2. 高伤害样本的 paired sign consistency ≥70%；
3. matched hindsight upper bound 相对 truth-only 至少 +5 pp success 或 -20% invalid/repeated actions；
4. 结果跨至少 2 个任务、2 个 horizon 成立；
5. 不主要来自 false-beneficial assertions。

若 (1–4) 不成立，结束方法路线；可以保留负面审计结果，但不包装新模型。

## P2a：伤害可预测性（CONDITIONAL）

### 输入

只允许部署时可见：before/after RGB、proprio、已执行 chunk、候选 assertion、truth verifier posterior。禁止 simulator state、未来 rollout、oracle action 泄漏。

### 相同架构的训练目标

- Uniform truth BCE；
- calibrated/selective truth loss；
- false-positive harm-weighted truth loss；
- pairwise harm ranking；
- simple action-divergence / value proxy。

### 切分

按 trajectory 与 task 切分；rollout seeds 不可跨 train/test。至少 3 seeds；先单 backbone，后续再做跨 checkpoint。

### 指标与 gate

- high-harm false-write AUROC/AUPRC；
- harm rank correlation；
- calibration 与 risk–coverage；
- oracle advantage recovered。

若部署特征不能稳定预测 harm，或简单 proxy 等价，则不进入新方法 claim。

## P2b：闭环 gate（CONDITIONAL）

### 主表系统

1. π0.5 no progress state；
2. π0.5 + truth-only completion/progress verifier；
3. π0.5 + calibrated/selective truth gate；
4. π0.5 + harm-aware truth gate；
5. factual oracle ceiling。

所有系统匹配：assertion source、训练样本、参数量、progress interface、VLA/recovery、推理调用、动作预算和 commit coverage。

### 主指标

- end-to-end success；
- high-cost false advancement；
- invalid/repeated actions；
- false-commit risk at fixed coverage；
- latency与额外 FLOPs。

成功标准：harm-aware 在相同 false-commit risk/coverage 下，对 truth-only 有跨任务稳定闭环增益，并恢复至少 50% 的 P1 hindsight advantage。

## P3：扩展（NICE-TO-HAVE，前面通过后）

- 第二 VLA backbone/checkpoint，测试 policy specificity。
- held-out memory semantics，而不只留出对象/场景。
- 真实机器人只验证自然 false-write 与干预收益；必须另行批准安全协议。
- WAM necessity 只在判别式 predictor 失败且多模态 future 明确必要时开展。

## Run Order

| Milestone | Runs | 决策 | 估算 |
|---|---|---|---|
| M0 | snapshot/restore、RNG、assertion carrier 单元测试 | 任一状态不完全可复现则先修基础设施 | 0–1 GPU-day + 工程 |
| M1 | P0 三组 oracle/corruption | 无 headroom 或无生态效度即 stop | 50–200 GPU-hours |
| M2 | P1 100–200 snapshots 配对 rollout | 不满足 5 条 GO gate 即 stop | 100–500 GPU-hours，按顺序停止 |
| M3 | P2a 小头/简单 proxy，3 seeds | 不可预测或 proxy 等价即降级 finding-only | 30–150 A100-hours |
| M4 | P2b held-out closed loop | 同事实风险/coverage 无增益即 reject method | 100–400 GPU-hours |
| M5 | 第二 backbone / 真机 | 只在 M4 通过后 | 另行估算与批准 |

以上是上限区间，不是旧的 2/8 GPU-hour 限制；通过 sequential stopping 避免无意义扩张。GPU 2、3 优先；0、1 只有确认空闲后才使用。

## 不做的实验

- 首轮不训练 WAM、视频生成器、planner、retraction graph 或 recovery policy。
- 不以 embedding 可视化、future video quality 或单一 AUROC 作为主证据。
- 不在 P0/P1 前启动全量 π0.5 fine-tuning。
