# Cycle-2 deterministic StarVLA candidate review

结论：`NO-CANDIDATE / NO-RUN`。

在 deterministic StarVLA-OFT、8 GPUh、training-only world objective 这些约束同时成立时，没有找到一个既足够新、又能完成可信匹配验证的候选。以下三个是最接近的结构性修订，但都不应升格进入实验。

## 1. Action-Readout Predictive Bottleneck

- 机制：令 8 个 action-token hidden states 先经过共享瓶颈，action MLP 与未来 DINO latent decoder 都只能读取该瓶颈，world head 推理时删除。
- 死结：若瓶颈等于 56 维预测 action chunk，路径退化为 predicted action→future latent→policy gradient，已被 ProgressVLA 占据；若瓶颈更宽，world information 仍可藏在 action-readout nullspace；若只用普通 shared penultimate bottleneck，则退化为通用多任务共享瓶颈，且近期 VLA 工作已直接讨论 Jacobian nullspace 与 output constraints。
- 必需对照：相同瓶颈 action-only、随机 target、full-hidden future target、相同参数/FLOPs。
- Fatal falsifier：future 信息仍主要位于 action Jacobian nullspace，或 random target/shared bottleneck 获得同等收益。
- 预算：短证伪 pilot 可接近 2 GPUh，但可信多臂三 seed 明显超过 8 GPUh。

## 2. Future-Defined State-Alias Separation

- 机制：同任务跨 episode 寻找 current DINO 近、future 特征远且专家 action 不同的 alias pairs，用 margin loss 分离 action-token representations，并拉近 current-near/future-near pairs。
- 碰撞：State Aliasing via Inverse Dynamics 已以 current/future observations 解决 VLA state aliasing；Sigma-Agent 已做 current-state/language 与 future-goal 的训练期 contrastive imitation learning。剩余差异只是 future-defined hard-pair mining，更像采样策略。
- 最小前置诊断：alias density 与 baseline action error 的受控相关性；必须控制 task、episode、trajectory phase。
- 必需对照：current-only hard pairs、action-distance pairs、random pairs、inverse-dynamics auxiliary。
- Fatal falsifier：受控 alias score 不能预测 action error，或 current-only/inverse-dynamics baseline 与其相当。
- 预算：可信五臂三 seed 约 40 GPUh，超过约束。

## 3. Successor-Geometry Distillation

- 机制：用真实未来构造 future-current latent displacement，并匹配其 batch Gram geometry 与 8-token action representation geometry；world loss 推理时删除。
- 碰撞：X-Tokenizer 已用 next-frame vision-language prediction 与 frozen-VLM alignment 塑造 action-token geometry；ALAM 已显式约束 latent transition 的组合与反演几何并作为 VLA auxiliary；Sigma-Agent 覆盖 future-goal contrastive geometry。剩余差异只是 relational/Gram loss swap。
- 必需对照：current Gram、temporal-shuffled future Gram、random orthogonal Gram、相同 target variance/rank/head/LoRA。
- Fatal falsifier：future Gram 不优于 current/shuffled Gram，或只改善 probe 而不改善闭环控制。
- 预算：可信五臂三 seed 约 40 GPUh，超过约束。

综合来看，deterministic host 的真正空白落在两种坏情况之间：让 world loss 直接经过 action 输出会撞 ProgressVLA；不经过 action 输出则无法排除 predictive signal 藏在 control-nullspace。其余 relational 或 state-alias 修订又被近期一手工作压缩成增量 loss/mining 变化。

建议保持 `REVISE / NO-RUN`。若继续 H1，至少需放宽一项约束：提高到约 30–40 GPUh 做 deterministic-vs-flow 受控比较，或接受“诊断/负结果”而非新方法作为主贡献。

本轮未改文件、未 SSH、未启动训练。
