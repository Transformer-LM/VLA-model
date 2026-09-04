# Research Proposal: Branch-Aligned Boundary Preference for Functional-Geometry VLA Post-Training

## Problem Anchor

- **Bottom-line problem**：当任务、语言指令和对象语义不变，但功能几何让原 action chunk 的局部片段变得物理不可行时，连续动作 VLA 应只改变真正失效的局部响应，同时保留未受影响的行为与其他可行修正方式。
- **Must-solve bottleneck**：现有几何可行性训练可以惩罚碰撞时间点，但尚不能清楚地区分“提高可靠性”与“把邻近可行模式一起压掉”；原 BLSM 又把 negative 的违规时间索引直接套到不同阶段的 positive 上，比较对象不成立。
- **Non-goals**：不声称首次使用几何反事实、首次做 action-time-local feasibility loss、保留全部物理可行模式、提供真实机器人安全保证，或在部署期使用 WAM/MPC reranking。
- **Constraints**：无触觉；训练部署在用户个人目录；四张 A100 可用但 E0 必须先通过非 GPU 数据门；冻结或参数高效微调 π0.5/连续动作头；部署输入保持 RGB、proprioception 和语言，不增加 simulator oracle。
- **Success condition**：在共享分支状态的 geometry-flip pairs 上，相比 active-violation geometry loss 与 whole-chunk preference，方法在相近 invalid-execution reduction 下显著减少 complement drift，并提高 compiler-roster coverage / worst-mode success；错配 mask 或 pair 后增益应消失。

## Technical Gap

`Can Explicit Physical Feasibility Benefit VLA Learning?`（arXiv:2604.17896）已经在参考轨迹附近放置障碍，并只对 active clearance violations 施加几何 loss。因此，“几何反事实 + 时间局部安全监督”不能作为本工作创新。剩余问题是：安全调优会通过共享参数改变整个条件动作分布，拒绝一个 invalid continuation 时可能同时压低仍可行的少数 continuation，而现有工作没有把这个 reliability–coverage trade-off 变成成对、可测、可训练的命题。

原候选用 negative 轨迹的首个违规段 M 截取任意 positive 的相同 raw time index。不同 positive 可能处于不同技能阶段，因此这一比较缺少共同物理语义。最小修复不是添加 phase model，而是改变数据单位：所有 positive 与 negative 都从 edited scene 的同一个 pre-violation simulator checkpoint 分支，并统一为固定 H 步 continuation。这样时间 0 表示同一物理状态下的决策边界，局部 preference 不再依赖跨轨迹阶段猜测。

## Method Thesis

- **One-sentence thesis**：从同一 pre-violation checkpoint 构造 invalid 与多个 feasible continuation，用冻结参考校正的局部 denoising preference 压低 invalid continuation，并用 complement anchoring 与 mode-wise retention 显式约束可靠性调优造成的分布外溢。
- **Smallest adequate intervention**：只新增一种 branch-aligned 训练记录和三个 loss 项；不训练 WAM、phase estimator、critic 或部署期 planner。
- **Why now**：连续动作 VLA/flow-diffusion action head、可恢复 simulator checkpoint 和几何可行性 oracle 已经可用，使成对 counterfactual post-training 可直接实现。

## Contribution Focus

- **Dominant contribution**：把 geometry-induced invalidation 转化为共享分支状态上的 reference-adjusted local action-distribution preference。
- **Supporting contribution**：以 compiler-roster coverage、worst-mode success 和 complement drift 揭示并约束 feasibility tuning 的可靠性–多样性副作用。
- **Explicit non-contributions**：几何感知 backbone、通用 motion planner、新 WAM、全局安全证明、完整可行模式枚举。

## Proposed Method

### Complexity Budget

- **Frozen / reused**：π0.5 或兼容的连续动作策略、RoboTwin/SAPIEN simulator、已有碰撞/任务成功判据、现有 motion planner/controller。
- **Trainable**：原策略的 action head/LoRA 子集；不超过一个可训练策略组件。
- **Intentionally excluded**：RGB-D/PointMap encoder、learned WAM、phase network、online reranker、LLM recovery module。

### System Overview

```text
successful base rollout in g+
  -> compiler-minimal visible geometry edit g-
  -> replay same chunk, locate first violation τ
  -> restore edited-scene checkpoint z_b immediately before τ
  -> branch: invalid suffix a- and K planner-verified feasible continuations a+_k
  -> score all continuations from identical z_b and elapsed-time origin
  -> local reference-adjusted preference + outside-window anchor + per-mode retention
  -> parameter-efficient VLA post-training; unchanged inference interface
```

### Core Mechanism

1. **BoundaryFlip compiler**：只接受原 chunk 在 g+ 成功、同一 chunk 在可见的 g- 因预注册几何事件失败、g- 仍可解的 pair。几何编辑只称 compiler-minimal，并保存全部 attempted-pair ledger。
2. **Shared branch checkpoint**：在 g- 中重放 invalid chunk，到首个违规前的固定 lead-in 步恢复 checkpoint z_b。negative 是从 z_b 开始的 H 步原后缀；K 个 positive 由 planner/controller 从同一 z_b、同一控制频率和 H 生成，并经 simulator ground truth 验证成功。不同 positive 只按预注册的轨迹/接触事件聚类称为 compiler-roster modes。
3. **Boundary-local preference**：冻结参考策略 π_ref。对同一观测条件 z_b，以 masked denoising-error surrogate 比较每个 positive 与 negative 相对 π_ref 的变化，只让 invalid continuation 的首个违规窗口进入 preference 项。窗口之外不声称参数不变，而是测量并用 reference anchoring 抑制 spillover。
4. **Mode-wise retention**：对每个 roster mode 等权施加 reference retention；主报告使用 worst-mode success 与 roster coverage，不把 roster 宣称为完整可行集合。
5. **Deployment**：移除 simulator/planner/compiler，仅运行 post-trained VLA；输入接口和基线一致。

### Training Objective

总目标为原 imitation loss，加上：

- L_boundary：共享 z_b 条件下，positive 相对 invalid 的冻结参考校正 masked denoising preference；
- L_comp：违规窗口外的 reference drift penalty；
- L_mode：每个 compiler-roster positive 的等权 retention penalty。

E0 中损失权重只在固定验证对上选择一次，并报告完整 Pareto 曲线；不把单一权重结果当作机制证据。

### Failure Modes and Diagnostics

- **pair 太稀少**：报告 attempted/eligible 比；低于预注册比例即停止。
- **视觉不可辨识**：审计 render mesh 与 collision mesh 一致性及 RGB 可见性；不可见 edit 排除并计入分母。
- **branch checkpoint 仍不一致**：对 simulator state、controller cache、随机状态做序列化 hash；不一致即拒收。
- **roster 是伪多模态**：按轨迹距离与接触事件聚类，合并重复 seed。
- **局部 loss 通过共享参数外溢**：以 complement output/score drift 和 unedited success 直接验收，不作结构性零外溢承诺。

## Novelty and Elegance Argument

最强近邻 2604.17896 使用 signed-distance hinge 惩罚所有 active violations；本方法保留 invalid continuation 作为显式 negative，从完全相同 pre-violation state 构造多个 feasible branches，并训练冻结参考校正的局部生成分布 preference，同时审计每个可行 roster mode 和边界外行为。Dream2Fix 生成失败—恢复数据，Ambient Diffusion Policy 选择性使用次优数据，PhysReflect-VLA 在部署期做可行性检查；它们都没有这一共享分支状态上的训练期 reliability–coverage 命题。

## Claim-Driven Validation Sketch

### Claim 1：shared-branch local preference 优于已有 active-violation shaping

- **Minimal experiment**：2–3 个 constraint families，比较 imitation、2604.17896-style L_geo、whole-chunk preference、local preference、完整方法。
- **Metric**：edited success、invalid-reference execution、unedited success、complement drift。
- **Decisive evidence**：完整方法相对 L_geo 在 edited success 或 invalid execution 有明确增益，且 complement drift/unedited success 不更差；否则主机制停止。

### Claim 2：mode/complement protection 不是装饰项

- **Minimal experiment**：删除 L_mode、删除 L_comp、打乱 mask、打乱 pair identity，并比较 roster coverage 与 worst-mode success。
- **Decisive evidence**：删除保护项出现预注册幅度的 coverage/worst-mode 或 drift 退化；permutation 保留不到一半主增益。

## Experiment Handoff Inputs

- **Must-prove**：共享分支 pair 可稳定生成；reference-adjusted margin 与 simulator validity ranking 相关；保护项影响真实策略行为而非只影响 loss。
- **Highest-risk assumptions**：eligible pair 密度、视觉可辨识性、同一 checkpoint 序列化正确、至少两个实质可分 positive modes。
- **Immediate gate**：先运行 CPU/non-training compiler audit；通过后才启动小 action-head/LoRA E0，禁止直接进入 56 GPU-days 全量方案。

## Compute & Timeline Estimate

- **Non-GPU gate**：100–200 attempted base episodes，CPU physics/compiler。
- **E0**：单 backbone、2–3 task families、5 个主 variants；先 1 seed sanity，再仅对通过的 variants 做 3 seeds。估计 20–60 A100 GPU-hours，而非完整方案的 56 A100-GPU-days。

