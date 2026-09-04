# C09 查新结论：Strict Validity–Transfer Gate

## 结论

- Verdict：**PARTIAL / Level 2 — High Overlap**。
- 定位：只能作为 **VLA-specific 诊断性科学发现 + 预注册准入协议**，不是新的优化方法。
- 当前状态：**REVISE / NO-RUN**。8 GPUh 只够“能否找到一个严格过门 predictor”的证伪型 pilot，不足以支撑完整 validity→transfer 论文主张。

## 尚存的新颖性轴

最窄可辩护问题是：在等初始化、数据、参数、步数和近似 FLOPs 的离线 VLA auxiliary co-training 中，一个由严格 holdout、persistence、同容量 action-agnostic predictor 与 matched action-shuffle 共同构成的 action-specific validity score，能否预测 predictive auxiliary 对闭环策略迁移的符号和幅度，而普通 validation loss 不能。

已有工作已经分别占据：

- persistence + action shuffle + downstream MPC（Hallucination in World Models）；
- action corruption strata → policy-ranking reliability（dWorldEval）；
- validation-based auxiliary rejection（ForkMerge）；
- offline world metric → closed-loop performance 与 Objective Mismatch。

因此唯一剩余差异是 **world validity 是否预测该 world objective 作为 VLA 参数更新信号时的迁移**，而不是 simulator、evaluator 或 planner 的效用。

## 进入实验前的硬要求

1. predictor training、gate calibration、locked strict test、final policy evaluation 必须逻辑四分；现有被反复查看过的 strict cache 不能充当最终证据。
2. 至少 4–6 个 predictor strata，并由两种以上独立操纵产生；两点 valid/invalid 不足以估计关系。
3. action-agnostic control 必须与 action-conditioned predictor 等容量、等数据、等优化、同 target。
4. policy arms 必须匹配初始化、样本序列、action loss、target tokens、参数、更新数与近似 FLOPs，并加入 dummy/random-target control。
5. 统计单位必须是 predictor/checkpoint/stratum；多 rollout 不能伪装成多个 predictor 样本。
6. 必须先存在至少一个在 locked holdout 上同时胜过 persistence、action-agnostic 且具有合理 shuffle sensitivity 的 predictor。
7. 最终主张需要多任务、多 policy seed 和 prospective gate test。

## 致命识别冲突

若 invalid predictor 永远令 `lambda=0`，则无法估计 validity→transfer 关系，因为 predictor validity 与 treatment intensity 同时变化；若要估计关系，就必须让若干低有效性 predictor 在隔离的负控 policy arms 中以相同非零权重进入训练。若不接受这些负控臂，C09 只能检验 gate 是否运行，不能证明 validity 能预测迁移。

## 对现有资产的含义

当前个人目录中的 CF-DynAlign predictor 在 strict heldout 上失败，不能作为 positive stratum，也不得开启其 `lambda_cf`。它最多只能作为隔离的失败案例或负控；在获得独立过门 predictor 前，不允许启动正向 policy co-training。

完整查新原文与来源矩阵见 `.aris/traces/idea-discovery/2026-08-07_run01/003-c09-scoop-check.response.md`。
