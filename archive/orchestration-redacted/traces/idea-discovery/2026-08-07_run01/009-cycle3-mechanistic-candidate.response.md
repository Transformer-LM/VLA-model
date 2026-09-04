# Cycle-3 mechanistic candidate review

独立审查结论：只保留 1 个 `CONDITIONAL-GO` 的机制型候选；若目标必须是主会级新方法，则当前宿主与 8 GPUh 约束下应判 `NO-CANDIDATE`。

## 候选：梯度门控的预测表征中介检验

核心问题不是“未来预测是否提高成功率”，而是：当 future objective 获准更新一个 VLA 动作接口表征时，任何策略增益是否真的由新形成的 future-predictive 子空间因果中介，还是仅来自普通正则化或 action-output diversity？

### 宿主与主张边界

现有 StarVLA checkpoint 的 Qwen 接口冻结，因此原始 action-token hidden states 未被 action-head 训练塑造。必须新增共享近恒等低秩 residual adapter，同时供 frozen deterministic action head 和小型 future head 使用。Qwen 与既有 action head 均冻结，仅训练 adapter 与 future head。

只允许声称“world objective 塑造新增的 shared action-interface representation”；不能声称重塑 Qwen/VLM backbone。若不加 adapter、只训练 world/action head，则不属于 H1。

### 随机化处理

从同一个预注册早期 checkpoint 出发，每个 seed 成对训练：

- treatment：action loss + future loss，future gradient 可进入 shared adapter；
- control：相同 action/future heads、target、参数、batch 和计算，但在 adapter 与 future head 边界 stop-gradient。

建议 future target 为冻结本地视觉编码器产生的 projected future-minus-current latent residual。不得复用 CF-DynAlign、其 predictor 或其缓存结论。

### 因果表征检验

在训练数据之外，用成对模型得到同一输入上的 adapter treatment delta。通过嵌套交叉拟合的 reduced-rank regression，从 delta 中提取可预测 future residual 的投影。闭环比较 control intact、treatment intact、treatment 去除 predictive component、以及 treatment 去除等范数正交 placebo component。

完整替换 treatment adapter output 为 control output 必须在同一输入上精确复现 control action，作为实现阳性对照。还需做插值和激活支持度检查，防止 patching 的离流形假象。

这种证据最多支持“受控表征干预下的必要性”，不能声称自然间接效应，也不能把示范轨迹中的可预测关系表述成物理因果。

### 严格前置门

- future head 在任务分块 heldout 上优于零残差、任务均值和等容量 current-only probe；
- treatment 相比 stop-gradient control 确实增加 heldout future decodability；
- early checkpoint 在两个预注册任务上不饱和；
- action-output diversity 作为竞争解释同时报告。

### 最小实验与预算

- 2 training arms × 3 seeds，共 6 个低秩 adapter runs；
- 2 个非饱和任务；
- 每任务、每条件 15 个完全配对初始状态；
- 4 eval conditions × 3 seeds × 2 tasks × 15 = 360 rollouts；
- 估计单卡总量约 3.5–6.8 GPUh。

必须先做 100-step 与 20-rollout 纯计时校准；若外推超过 7.2 GPUh，立即停止，不得通过删掉必要对照硬塞预算。

### Fatal falsifiers

- strict future target gate 失败；
- treatment 对 control 没有跨 3 seeds 同向的闭环增益；
- 去除 predictive component 不比 placebo 更明显地消除增益；
- 完整 activation patch 不能复现 control action；
- future decodability 提升但行为只由 action-output diversity 解释；
- 效应仅在单一任务出现，或来自 checkpoint 饱和/崩溃。

### 与最近工作的边界

VLA-JEPA、FOCA、Enfold 已覆盖 future objective、预测表征和监督消融，但没有随机化 future-gradient access 后干预 treatment-induced predictive subspace。Emergent World Representations in OpenVLA 探测 transition vector，但没有证明其被策略因果使用。VLA-Trace 与 Action Atlas 覆盖 VLA 表征干预和子空间注入，但没有 world-objective treatment。

最强近邻 arXiv:2606.13856 已在冻结 Qwen/V-JEPA 的 VLA 上研究 Jacobian parameter-nullspace 和 9–13 seeds，并发现 world-latent 指标不预测成功率、action-output diversity 才具有区分性；但其 future loss 不能塑造冻结的 action-token representation，也未做上述 predictive-mediator intervention。这是本候选剩余的窄 delta。

最终评级：适合作为严格、可证伪的机制/诊断短论文方向，不是新 world objective；若要求主会级方法贡献或跨架构结论，应停止而非强行实验。
