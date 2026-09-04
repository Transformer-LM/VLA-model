# Research Proposal: Decision-Identifiable Feedback for VLA × WAM

## Problem Anchor

- **Bottom-line problem**：长时 VLA 在物理分布变化下容易执行失败；WAM 的 prediction–observation feedback 本应帮助修正或重排下一段 action chunk，但同一个 factual residual 可能对应多个物理原因，而这些原因对下一候选动作的影响不同。
- **Must-solve bottleneck**：系统必须判断“这份执行反馈是否足以决定下一候选动作的修正方向”；若不可辨识，不能盲目搬运 residual，也不能只因一个大 uncertainty 就永久停机。
- **Non-goals**：不再把 constant state-residual transport、普通 uncertainty halt、generic active system identification、更漂亮的视频生成或触觉融合当作贡献；不声称当前 P027C 阴性结果支持 router。
- **Constraints**：仅 RGB/RGB-D、proprio 与动作日志，无触觉；先用 LIBERO/MuJoCo，VLA 与主 WAM 尽量冻结；4×A100 可用但必须门控；真实机器人仅在独立安全协议后运行。
- **Success condition**：在 ordinary feedback 上保留 WAM correction 的收益；在 residual-cause ambiguity 上显著减少错误重排/错误修正；只有决策真的依赖隐藏原因时才执行短 probe，并在等交互成本下优于 global feedback、uncertainty gate、直接 scorer 与 generic system ID。

## Technical Gap

Feedback World Model 使用在线 observation residual 更新轻量 feedback state，并用 action-aware guidance 改善后续控制；FFDC-WAM、CheckVLA 和 UNISafe 分别覆盖 future–reality verification、conformal intervention 与 uncertainty-aware safety filtering。它们回答“预测是否可信/是否需要干预”，但没有显式回答：**相同 residual 的多个因果解释是否会改变候选动作排序**。

另一方面，ASID 与 active system identification 已经研究如何用 exploration 识别全局物理参数；PhysCoRe 也用不确定性引导 material exploration。因此“主动辨识物理参数”本身不是新意。这里真正缺少的是 decision-focused identifiability：只维护会改变当前 VLA 候选排序的 residual explanation version set；若所有解释给出同一动作排序，则无需完整辨识；若排序分叉，才选择最小风险 probe。

P027C 的阴性结果构成直接约束：constant residual 在一个 retrospective heldout source 上同时伤害 alias/control；新 LOSO source 还出现 action-conditioning failure，另一 source 的最佳训练侧正迁移仅改善 0.045%（低于 1% gate）。所以新方案不能依赖“更聪明地搬运同一个全局 residual”，而必须将“不知道原因”保留为多假设 belief，并允许不修正或先探测。

## Method Thesis

- **One-sentence thesis**：把 WAM 执行残差表示成一个候选动作相关的 causal explanation set，仅当候选排序在该 set 上不变时使用反馈；否则选择一个最小代价 probe 来消除会导致 ranking reversal 的解释。
- **Why smallest adequate**：冻结 VLA 与主 WAM，仅新增一个 factor posterior/correction adapter；robust ranking 与 probe selection 是无训练的推断规则。
- **Why timely**：FWM 已证明 inference-time feedback 有用，但现有失败监控仍以单一 confidence/discrepancy 为中心；VLA top-K action chunk 与 WAM rollout 使“反馈解释是否改变决策”成为可直接计算的对象。

## Contribution Focus

- **Dominant contribution**：decision-identifiable feedback——以候选排序是否对 residual explanation 不变作为反馈可迁移性的判据，并在不变性失败时执行 task-preserving probe。
- **Supporting contribution**：扩展现有 influence-separated compiler，生成“相同 factual residual、不同 latent cause、candidate ranking 分叉”的严格 witness，用于训练和压力测试。
- **Explicit non-contributions**：generic WAM correction、普通 ensemble uncertainty、generic active system ID、首次 WAM/VLA correction、两点不可辨识下界本身。

## Proposed Method

### Complexity Budget

- **Frozen/reused**：π0.5 或其他 VLA 产生 top-K action chunks；action-conditioned WAM 产生 base futures；对象/接触图由 RGB-D、proprio 与现有几何教师得到。
- **New trainable components**：一个共享 encoder 加两个轻量 heads：`q_ψ(z | h_t,a_t,r_t)` 的 explanation posterior，以及 `g_η(r_t,a^k,z)` 的 factor-conditioned correction adapter。共享 trunk，计为一个 trainable module。
- **Not used**：不训练第二个大视频生成器，不做端到端 RL，不引入 tactile，不同时加入 memory/3D/object-address 等平行贡献。

### System Overview

```text
已执行 transition + WAM prediction -> residual r_t
                                   -> explanation posterior q(z)

VLA top-K chunks -> frozen WAM base rollouts -> per-z corrected values Q_k(z)
                                              |
                   ranking invariant over z? -+-> yes: execute robust winner
                                              +-> no: choose minimal safe probe
                                                       -> observe -> update q(z)
                                                       -> rerank/execute
```

### Core Mechanism

`z` 不是整台机器的完整参数，而是与当前场景图对齐的 residual explanation，例如 robot actuation、gripper–object、object–support、object–container、camera/perception。posterior 输出多假设而非硬标签：

\[
q_\psi(z\mid h_t,a_t,r_t,G_t).
\]

对候选 chunk `a^k`，adapter 给出 explanation-conditioned correction，再由冻结 critic/progress head 得到 `Q_k(z)`。定义 posterior 内的 robust regret：

\[
R(k)=\mathbb E_{z\sim q}\left[\max_j Q_j(z)-Q_k(z)\right].
\]

若同一个候选在可信 explanation set 中始终占优，直接执行，无需把物理原因完全辨识；否则只在 ranking reversal set 上选 probe：

\[
p^*=\arg\max_{p\in\mathcal P_{safe}} I(z;o_{t+1}\mid p)-\lambda C_{task}(p)-\mu C_{risk}(p).
\]

probe 库由短、可逆、低幅度的 view/motion/contact primitives 构成，并受工作空间、碰撞距离和 VLA task-progress 约束。没有满足安全预算的 probe 时，系统 abstain/reobserve，不伪装成恢复成功。

### Training Signal

- 用 simulator 随机化 actuation、mass/contact compliance、friction、camera 等单因素与组合因素；compiler 匹配 factual residual，但要求 candidate outcomes/rankings 分叉。
- posterior 用 factor label 的交叉熵与 twin-consistency loss；对不可辨识 twins，要求 posterior 保留多模态而非过早坍缩。
- correction adapter 用 candidate future latent/state residual loss；ranking loss 只监督候选相对顺序。
- probe 不需要 RL：在训练 simulator 中枚举短 probe，使用 posterior reduction 与 task/risk cost 的监督目标；推理时在冻结 probe bank 中选择。

### Inference Path

1. VLA 提出 K 个 chunks；冻结 WAM 生成 base futures。
2. 执行当前 chunk 的短前缀并获得真实 observation；计算 residual 与 explanation posterior。
3. 对 K 个候选和 posterior hypotheses 批量计算 corrected values。
4. ranking invariant 则执行；不 invariant 则 probe；probe 后只更新 belief，不更新大模型参数。

### Failure Handling

- **所有候选都 OOD**：不使用 explanation adapter，回退 no-feedback/reobserve。
- **posterior 高熵但排序稳定**：继续执行，避免普通 uncertainty gate 的过度保守。
- **posterior 高熵且排序分叉**：probe 或 abstain。
- **probe 不能区分解释**：报告 irreducible ambiguity，禁止把失败计为 recovery。

## Novelty and Elegance Argument

最接近的机制威胁分别是：FWM 的 latent observer/action-aware guidance、FFDC/CheckVLA 的 discrepancy-triggered intervention、UNISafe 的 epistemic filter、ASID/PhysCoRe 的 active identification，以及 Imperfect World Models are Exploitable 的一般 preference reversal 理论。拟议方法不能声称这些组成部分新颖；它只守一个交集命题：**online WAM feedback 的使用应由 candidate-ranking identifiability 决定，而不是由 residual 大小、单一 confidence 或完整参数辨识决定**。若 reviewer 认为这个交集仍只是已知 POMDP/system-ID 的重命名，则应停止该 pivot。

## Claim-Driven Validation Sketch

### Claim 1: decision-identifiability criterion detects when feedback is unsafe to transfer

- **Minimal experiment**：在多机制 residual twins 与 matched ordinary controls 上，冻结 WAM/VLA，比较 no feedback、FWM/global feedback、ensemble uncertainty gate、direct action scorer、oracle factor 与本方法。
- **Metric**：block/source-first excess ranking regret、wrong intervention rate、ordinary useful-correction retention、risk–coverage curve。
- **Gate**：ordinary retention 不低于 FWM 的 90%，alias wrong-intervention 相对最佳非 oracle baseline 至少下降 25%；否则停止。

### Claim 2: task-preserving probes resolve only decision-relevant ambiguity

- **Minimal experiment**：只在初始 ranking 分叉的 cases 中比较 random safe probe、ASID-style information gain、reobserve-only 与 decision-focused probe。
- **Metric**：ranking entropy reduction per unit task/risk cost、probe rate、post-probe regret、stagnation。
- **Gate**：在相同 cost 下显著提高正确 ranking；若 generic information gain 等效，则不声称新 probe objective。

### Claim 3: downstream closed-loop value（仅前两门通过后）

- **Minimal experiment**：π0.5/LIBERO 长时或接触任务，多 seed，对任务成功率、错误干预、碰撞、额外步数做比较。
- **Gate**：只有前两机制 claim 均通过才运行；当前不授权。

## Experiment Handoff Inputs

- **Must-prove**：存在 global/uncertainty feedback 不能处理、但 decision-focused explanation/probe 能处理的真实 learned-WAM ranking reversals。
- **Must-run ablations**：去掉 explanation set、改为单 confidence、去掉 ranking-invariance、random/generic IG probe。
- **Highest-risk assumptions**：RGB-D/proprio 能否区分 explanation；frozen WAM 是否先在 ordinary controls 上有效；安全 probe bank 是否覆盖关键原因。

## Compute & Timeline Estimate

- **E0 compiler/probe oracle**：CPU + 单 A100，约 1 天；先验证 witness 和 oracle gap。
- **轻量 posterior/adapter**：2×A100，约 1–2 天；不启动四卡大模型训练。
- **闭环**：只在机制 gate 通过后评估；真实机器人另行安全审批。
