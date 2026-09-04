# 独立候选评审结论

**总决定：`REVISE / NO-RUN`。**

当前没有候选足以作为新的 H1 方法直接训练。C01 是唯一可被保留为主方向的候选，但它应被定位为 **DIAGNOSTIC/FINDING**，而不是新 world-model 方法；在解决 strict gate 与 placebo 训练的内部冲突、冻结任务和数值阈值之前，不应开跑。

`review_independence: same-family`  
`acceptance_status: provisional`

以下判断只基于五份指定材料。所有论文覆盖和实验结果均按 provisional evidence 处理，尚未完成外部深查新。

## 总排名与评分

分项依次为：Novelty/25，H1 mechanism/15，Causal identifiability/20，8/2 GPUh feasibility/15，Benchmark credibility/10，Negative-result value/10，Non-overlap with CF-DynAlign/5。

| 排名 | 候选 | 分项评分 | 总分 | 类型 | 决定 |
|---:|---|---|---:|---|---|
| 1 | C01 | 18/15/17/10/7/10/5 | **82** | DIAGNOSTIC/FINDING | 条件保留；唯一主方向候选 |
| 2 | C02 | 16/14/12/12/7/9/5 | **75** | DIAGNOSTIC/FINDING | 深查新；暂不训练 |
| 3 | C03 | 13/12/11/15/6/9/5 | **71** | DIAGNOSTIC/FINDING | 只能作为 C01 附属机制实验 |
| 4 | C09 | 15/12/9/7/6/10/4 | **63** | DIAGNOSTIC/FINDING | 深查新；设计尚未闭合 |
| 5 | C07 | 1/14/13/13/6/7/5 | **59** | REJECT | **硬淘汰 (a)** |
| 6 | C05 | 5/11/10/12/6/8/5 | **57** | ORDINARY ABLATION | 不作为主贡献 |
| 7 | C04 | 3/9/9/13/6/7/5 | **52** | REJECT | **硬淘汰 (a)** |
| 8 | C08 | 8/12/10/1/6/8/4 | **49** | REJECT | **硬淘汰 (c)** |
| 9 | C06 | 4/6/10/6/6/6/5 | **43** | REJECT | generic PCGrad/CAGrad route |
| 10 | C10 | 3/4/10/7/6/6/5 | **41** | REJECT | generic ForkMerge/validation gating |

没有候选达到 **NEW METHOD** 标准。

## 逐项裁决

- **C01：保留。** 完整 `future/past × correct/shuffled action` DiD 比单独的 future head 或 action perturbation 更有识别力。主要缺陷是 past/future 难度、阶段泄漏与 shuffle exchangeability；且 placebo predictor 可能无法通过项目自己的 action-agnostic strict gate，却又必须以非零 auxiliary weight 训练，当前协议内部矛盾。

- **C02：保留查新。** `C(y)` 作为事前 target-selection 指标有价值，但四种 target、只训练两极，不能支持“收益随 controllability 单调变化”；target identity、SNR、可预测性和语义内容仍与 `C(y)` 混杂。更像发现型研究，不是新 objective。

- **C03：只作附属。** 闭环 erasure 优于只做 probe，但低秩投影会产生 off-manifold intervention；同 rank/energy 随机控制只能减轻、不能完全消除该问题。它不能独立承担论文主贡献。

- **C09：保留查新。** 动机强，但当前“validity 预测 transfer”的主张与实验不相称：invalid stratum 不进入 policy training，而只有一个 valid branch 时无法估计 validity–transfer 关系。若改成 gate 方法，又容易退化为普通 model selection。现有 strict-failed F 只能离线作负诊断；任何让它以非零权重训练 policy 的方案都会触发硬淘汰 (b)。

- **C07：硬淘汰。** `action margin/action-conditioned JEPA` 已被 AquaJEPA 直接占据，SelfWAM 又覆盖 action sensitivity；符合 (a)。

- **C05：普通 ablation。** horizon 与 action chunk 对齐值得作为 secondary ablation，但多步/horizon 消融普遍存在，不能独立形成贡献。

- **C04：硬淘汰。** FLARE 的 layer sensitivity 与 GAM 的 split-layer 消融已直接覆盖核心问题；匹配 LoRA 参数量和 gradient norm 只能使消融更严谨，不能恢复 novelty，符合 (a)。

- **C08：硬淘汰。** 当前没有通过 strict holdout 的本地 frozen video prior；候选自身也规定缺失时 defer。在 2/8 GPUh 内从零获得并验证该资产没有依据，符合 (c)。

- **C06：拒绝。** 核心是 generic gradient projection。若不完成 random auxiliary、reverse/norm-matched gradient 等控制，就没有 H1-specific conclusion；完成这些控制又对 8 GPUh 预算风险很高。

- **C10：拒绝。** 本质是 ForkMerge/validation-based auxiliary weighting。即使阻止负迁移，也不能说明 predictive world objective 的机制；还容易 overfit frozen mini-validation stream 或退化为永远拒绝。

没有候选因 inference-time planning 或“world loss 单独作为成功”而被接受；所有幸存方向仍必须用闭环 action endpoint 验收。

## 深查新名单

最多推荐以下三个：

1. **C01**：查 `time-arrow × action-identity` 的完整 factorial causal design 是否已用于 VLA closed-loop transfer。
2. **C02**：查 action-conditional predictability、conditional mutual information 或 controllability score 是否已被用作 future-target 选择并预测 policy gain。
3. **C09**：重点尝试证伪，查 world-model validity gate 与 auxiliary-task selection、safe multi-task learning、validation gating 的重叠。

C03 不应作为新颖贡献查新；把它当标准机制工具即可。

## 条件主方向：C01

**类型与路线：** `DIAGNOSTIC/FINDING`；R3、training-time U6/shared-representation，固定离线数据，部署仍为 action-only，不进入规划路线。

**精确一句话主张：**

> 在固定 StarVLA 初始化、相同 LIBERO 离线样本以及参数、target token 和训练 FLOPs 匹配到 ±5% 的条件下，latent auxiliary 对闭环 success 的增量只出现在 `future_correct`，使预注册的 `(future_correct−future_shuffle)−(past_correct−past_shuffle)` 为正，而不是来自通用正则化、时间相关或动作边际分布。

**最近工作碰撞边界：**

SelfWAM 已占据 action perturbation，VLA-JEPA、Fast-WAM 和 LiLa-WAM 已占据普通 future-latent/removable-head 路线。C01 只能声称“matched 2×2 factorial identification 与闭环 DiD”；不能声称新 future head、新 action conditioning、新 JEPA objective 或新的高性能 VLA。

**最小 matched pilot：**

- 从一个冻结的 action-only checkpoint 分出四个分支：`future_correct`、`future_shuffle`、`past_correct`、`past_shuffle`。
- 只用两个预先锁定的 LIBERO tasks：一个 LIBERO-Object、一个 LIBERO-Spatial；仅根据 action-only 结果选择 baseline success 位于 30%–80% 的任务，禁止查看 treatment 后再选。
- 每格一个训练 seed；相同数据顺序、LoRA 模块、head 形状、target 维数、optimizer、steps、loss token 和近似 FLOPs。
- action shuffle 仅在 task × phase × speed bin 内进行，并报告置换前后的动作分布差异。
- 每格每任务至少 50 个相同 initial-state/evaluation-seed 的 paired rollouts。
- `future_correct` 必须先在 strict episode/temporal holdout 上超过 persistence 和 action-agnostic predictor，并显示 action-shuffle sensitivity。
- 该 pilot 只决定是否继续，不能支持 venue-level claim；最终主张至少需要三 training seeds。若剩余 6 GPUh 无法容纳冻结配置的多种子复验，应停止而不是降低证据标准。

**预注册正阈值：**

- 主 endpoint：closed-loop success DiD 点估计至少 **+10 percentage points**；
- 两个任务的 task-wise DiD 均不得为负；
- 对 paired evaluation seeds 的 one-sided 90% bootstrap lower bound 必须大于 0；
- strict prediction diagnostic 的对应 interaction 必须同号且 standardized effect 至少 **0.20**；
- world loss 降低、action loss 改善或单任务提升均不能单独过门。

**Kill criteria：**

- `future_correct` 未通过 strict world/model gate；
- 任一 interface、时间索引或 future leakage 检查失败；
- shuffle 后任务阶段或速度分布不可匹配；
- 核心分支参数/token/FLOPs 差异超过 ±5%；
- policy DiD 小于 +10 pp、两个任务异号，或只剩 world-loss 信号；
- 效应由单一任务、checkpoint selection 或未预注册 exclusion 驱动；
- 无法在总预算内完成至少三 training seeds；
- 使用 strict-failed CF-DynAlign F 训练 policy，或令 `lambda_cf != 0`。

**实施前最小修订：**

新增一页冻结的 preregistration，同时完成三件事：命名两个具体 LIBERO task、写死上述 estimand/阈值/预算，并明确解决“所有 predictor 必须过 strict gate”与“placebo 分支必须以非零 auxiliary weight 训练”之间的冲突。若项目规则不允许给预声明的 placebo control 一个有限例外，则 C01 本身不可执行，应返回 `NO-RUN`。

## 唯一允许的附属机制实验

可在 C01 已产生的 checkpoint 上复用 **C03**，不新增训练：

- 从 held-out trajectory 拟合 `S_dyn`；
- 比较擦除 `S_dyn`、同 rank/energy 随机子空间和 appearance/language 子空间；
- 只在 paired rollouts 上检验 treatment 相对 placebo 的增益是否被特异消除。

该结果最多支持“action-specific future information 对效果具有必要性证据”，不能宣称完整 causal mediation。

综上，C01 可以成为一个严谨的 H1 诊断方向，但当前版本仍是 **`REVISE / NO-RUN`**；不得为了流程推进把它包装成新方法并立即训练。

