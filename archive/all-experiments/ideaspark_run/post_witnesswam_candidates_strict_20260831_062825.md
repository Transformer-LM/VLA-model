# Post-WitnessWAM problem-first 候选与严格初筛

**审查日期：** 2026-08-31  
**文献截止：** 2026-08-31  
**范围：** VLA-only、WAM-only、VLA×WAM；RGB/proprio，无触觉；先在可回滚模拟器证伪  
**硬门槛：** strict novelty 区间下界必须 **> 7.0**，且 naturalness **>= 7.0**；`7.0` 仍为 FAIL  
**实验状态：** 未启动任何 CPU/GPU/远程/真实机器人实验

## 结论先行

本轮从两个独立 problem-first 发散池机械合并出 15 个机制候选，再按 exact observation / intervention / supervision / consumer 对截至 2026-08-31 的 primary literature 做碰撞检查。**没有一个候选的 strict novelty 下界稳定高于 7.0，因此最终保留 0 项。**

这不是说 15 个问题都没有研究价值，而是它们当前都存在一条足以让严格 reviewer 将贡献解释为“经典控制/规划机制 + 当前 VLA/WAM 载体”的强组合近邻。为了避免再次把“未检索到单篇完全同构论文”误当成新颖性，本轮不授权任何 E0，更不授权 4×A100 训练。

最接近门槛、但仍未通过的六项是：

| 候选 | strict novelty 区间 | naturalness | 最强威胁 | 判定 |
|---|---:|---:|---|---|
| C14 actual-cause VLA post-training | 5.8–7.0 | 8.1 | counterfactual credit assignment + rollback repair/failure-data training | FAIL |
| C4 主动构造可恢复 checkpoint | 6.2–6.9 | 7.7 | reversibility-aware RL + resilient/robust planning + B2FF/RecoveryChaining | FAIL |
| C9 稀疏因果动力学 minimax | 6.0–6.8 | 7.5 | causal-structure dynamics + robust MBRL/MPC + PROWL | FAIL |
| C8 progress–compensation 联合规划 | 5.4–6.8 | 9.0 | RecoveryChaining + contingent planning + CheckVLA | FAIL |
| C15 planner-invariant action dominance | 5.0–6.6 | 7.5 | robust/Pareto dominance + WAM exploitation/pessimistic planning | FAIL |
| C7 interventional effect quotient | 4.9–6.5 | 7.6 | QuoVLA + GEAR-VLA + action-effect abstraction | FAIL |

## 机械去重后的 15 项

下表把机制压缩成 2–4 个不可缺步骤。`E0` 只描述候选若未来发生实质机制改写后应先怎样证伪；**不是本轮实验授权。**

### C1｜Reversible Causal Graph Surgery

- **机制：** (1) WAM 将 action–effect 历史实例化为局部关系因果图；(2) 在不破坏已完成关系的可逆动作集中执行一次区分候选因果边的微干预；(3) 用结果增删/定向图边；(4) 从改写后的图合成控制。
- **最强近邻：** counterfactual active fault diagnosis、dual control、[Counterexample-Guided Repair](https://arxiv.org/abs/2105.06537) 与一般 causal model repair。
- **不可约 delta：** 真实物理微干预后直接做 task-graph edge surgery，并改变后续可行计划族。
- **致命反对：** 图节点/边和可逆动作库必须先人工给定；一旦给定，剩余机制就是经典主动系统辨识与模型修复。
- **评分：** novelty `5.5–6.5`；naturalness `6.9`；**FAIL**（同时触发 active-FDI 硬排除）。
- **kill E0：** privileged graph 下，单次 probe 的边定位率 <80%，或重复失败下降 <30% 即 kill。
- **4卡可行性：** 中低；算力足够，但主要瓶颈是可审计图定义与干预数据，不是 GPU。

### C2｜Task-Null Instrumental Perturbations

- **机制：** (1) 从局部 action→effect Jacobian 求不改变目标谓词的 task-nullspace；(2) 在其中执行一次安全 probe 区分 WAM 误差方向；(3) 用真实 residual 修正 Jacobian；(4) 将 planner 优化投影出 exploit direction。
- **最强近邻：** active system identification/dual control、ACDD 类主动诊断、local controllability probing、WorldSimProbe/WorldEcho 式 action intervention。
- **不可约 delta：** probe 同时应保持任务效果并专门估计 planner 可利用的 WAM 误差方向。
- **致命反对：** “task-null”由错误 WAM 定义时没有物理保持保证；用 simulator/解析 Jacobian 定义时又退化成经典 instrument design。
- **评分：** novelty `5.3–6.4`；naturalness `7.1`；**FAIL**（同时触发 active-FDI 硬排除）。
- **kill E0：** oracle task-null probe 与真实 exploit direction 的 median cosine <=0.5，或 best-of-N 仍随 N 恶化即 kill。
- **4卡可行性：** 中；冻结 WAM 可算有限差分，但真实安全 probe 不适合在模拟器通过前部署。

### C3｜Residual-to-Intervention Compiler

- **机制：** (1) 将 WAM 预期 effect 与实际 effect 的差表示为关系残差；(2) inverse solve 最小补偿动作并约束已完成关系不被破坏；(3) 执行补偿后接回原计划未执行后缀。
- **最强近邻：** [Imagining Recovery / CoRe](https://arxiv.org/abs/2608.14822) 已做“最小 realignment 后重接 imagined continuation”；CheckVLA 做 committed-suffix repair；A2C2 做连续残差修正。
- **不可约 delta：** 关系残差到受保护连续干预的显式编译。
- **致命反对：** CoRe + constrained inverse dynamics 已基本给出同一自然解法；若补偿只改 action suffix，则 A2C2/CheckVLA 进一步压缩剩余差异。
- **评分：** novelty `4.2–5.8`；naturalness `8.1`；**FAIL**。
- **kill E0：** oracle inverse dynamics 两个 chunk 内恢复且继续前进比例 <60%，或不优于完整 replan 即 kill。
- **4卡可行性：** 中高；但 novelty 先失败。

### C4｜Deliberate Recoverability Construction

- **机制：** (1) WAM/可达性模型预测未来不可逆边界及失败后可达集；(2) 先执行一个保持当前进度、但改善局部逆动力学条件的实体动作，构造 checkpoint；(3) 从 checkpoint 执行主任务；(4) 失败时沿预合成逆控制返回。
- **最强近邻：** [There Is No Turning Back](https://arxiv.org/abs/2106.04480) 的 reversibility-aware control、resilient manipulation planning、[RecoveryChaining](https://arxiv.org/abs/2410.13979)、[B2FF](https://arxiv.org/abs/2606.09258) 的 recoverability-aware milestone。
- **不可约 delta：** 不是选已有 checkpoint，而是先改变物理世界来创造新的可恢复 checkpoint。
- **致命反对：** 这可被 reviewer 解释为 robust planning 中的 preparatory/funnel action；若 checkpoint 类型需要任务脚本，便不是通用 VLA/WAM 机制。
- **评分：** novelty `6.2–6.9`；naturalness `7.7`；**FAIL**。
- **kill E0：** oracle reachability 下可恢复扰动比例不比直接执行高，或无扰动成功损失 >10% 即 kill。
- **4卡可行性：** 中；oracle E0 轻，学习版可由 4 卡支持，但当前不授权。

### C5｜Counterexample-Guided Plan Constraint Compilation

- **机制：** (1) 将计划表示为带 action realization 的事件程序；(2) 从失败 rollout 找最早被否定转移及最小因果条件；(3) 将其编译成排除整个同构失败计划族的 hard constraint；(4) 在收缩后的可行域重规划。
- **最强近邻：** [Counterexample-Guided Repair for Symbolic-Geometric Action Abstractions](https://arxiv.org/abs/2105.06537)；[Conflict-driven Interface between Symbolic Planning and Nonlinear Constraint Solving](https://arxiv.org/abs/2211.15275) 已提取最小不可行约束集并回写逻辑搜索。
- **不可约 delta：** VLA/WAM execution counterexample 被 lift 成 plan-family constraint。
- **致命反对：** exact causal/constraint loop 已由 2021/2022 TAMP 工作覆盖；换成 VLA action realizer 不构成 >7 novelty。
- **评分：** novelty `2.5–4.1`；naturalness `8.5`；**FAIL**。
- **kill E0：** 同构失败复发不降 >=50%，或误删可行计划 >10% 即 kill。
- **4卡可行性：** 高；主要是 symbolic compiler，不需要 4 卡。

### C6｜Observation-Contingent Action Trees

- **机制：** (1) VLA 一次输出共享短前缀、typed future observation event 与 2–3 个条件后缀；(2) simulator rollback 用同前缀编译 success/miss/ambiguous outcomes；(3) 执行前缀；(4) 新观测到来后绑定已生成后缀，无需再调用大模型或 WAM rerank。
- **最强近邻：** classical contingent/POMDP policy trees；contact-uncertainty partial policies；[DREAM-Chunk](https://arxiv.org/abs/2606.18589)、[CheckVLA](https://arxiv.org/abs/2607.26789) 与 [A2C2](https://arxiv.org/abs/2509.23224) 已覆盖 chunk 内反馈/选择/修正。
- **不可约 delta：** native VLA action head 一次性生成一个 depth-1 closed-loop policy tree，而非单 chunk 或事后重规划。
- **致命反对：** decision object 是经典 policy tree；VLA-native decoder 只是新载体，且 typed branch labels 可能是另一种手工 option interface。
- **评分：** novelty `4.8–6.3`；naturalness `8.6`；**FAIL**。
- **kill E0：** oracle branch 深度 2 在等动作预算下不优于每 5 步重规划，或 branch miss >15% 即 kill。
- **4卡可行性：** 中高；π0.5 action head 改动和 rollback compiler 可做，但 novelty 未过。

### C7｜Interventional Effect-Equivalence Quotient Interface

- **机制：** (1) 只在 chunks 跨 nuisance interventions 产生同一任务关系 effect、且保护同一关系时判为等价；(2) 学 quotient encoder 与 geometry/embodiment-conditioned decoder；(3) VLA 预测 effect class，decoder 实例化具体 chunk；(4) 真实 effect 冲突时才 split class。
- **最强近邻：** [QuoVLA](https://arxiv.org/abs/2605.24890)、[GEAR-VLA](https://arxiv.org/abs/2606.08530)、latent-action/action-manifold work、经典 bisimulation/action abstraction。
- **不可约 delta：** equivalence 由跨干预的 object-relation effect 与 protected relations 定义，而非 prompt redundancy、trajectory similarity 或 embodiment canonicalization。
- **致命反对：** 这是 bisimulation/action abstraction 的机器人实例；effect predicates 若人工给出，创新被压缩，若学习得到，则等价关系稳定性难以审计。
- **评分：** novelty `4.9–6.5`；naturalness `7.6`；**FAIL**。
- **kill E0：** oracle quotient 在固定查询预算下不增加独特可达 effects，或 decoder realization 成功率 <80% 即 kill。
- **4卡可行性：** 中低；数据编译与多 embodiment 比 GPU 更难。

### C8｜Joint Progress–Compensation Planning

- **机制：** (1) 对每个不可逆边界联合生成 forward suffix 与有限 failure branches 的 compensators；(2) WAM 在共享扰动下联合优化 forward progress 和 compensation 后的 continuation reachability；(3) 执行 forward；(4) 已建模 residual 直接进入对应 compensator。
- **最强近邻：** [RecoveryChaining](https://arxiv.org/abs/2410.13979)、B2FF、[FLARE](https://arxiv.org/abs/2608.26645) 和 classical contingency planning。
- **不可约 delta：** nominal action 只有携带已验证 compensation 才进入可行集，而不是失败后再外挂 recovery。
- **致命反对：** joint nominal/backup policy 是经典 contingency/robust planning；预注册 failure branches 还会严重限制开放世界泛化。
- **评分：** novelty `5.4–6.8`；naturalness `9.0`；**FAIL**。
- **kill E0：** oracle compensator 在等总动作预算下不优于 nominal + failure-time replan 即 kill。
- **4卡可行性：** 中；rollout 数量高但 4 卡足够做小规模，当前不授权。

### C9｜Sparse Causal-Dynamics Minimax Planning

- **机制：** (1) 将 WAM dynamics 分解成少量可干预机制；(2) 内层 adversary 找与近期真实 transitions 一致、但能使候选计划失效的最小稀疏机制改写；(3) 外层选择在这些改写下仍推进的 trajectory；(4) 新真实 transitions 收缩改写集。
- **最强近邻：** [Learning Causal Structure Distributions for Robust Planning](https://arxiv.org/abs/2508.06742)、[Causal Model-Based Policy Optimization](https://arxiv.org/abs/2503.09719)、distributionally robust MBRL/MPC，以及 [PROWL](https://arxiv.org/abs/2605.18803) 的 adversarial high-error WAM training。
- **不可约 delta：** adversary 只允许稀疏 mechanism surgery，而非 state/action noise、ensemble confidence 或全局 uncertainty set。
- **致命反对：** 这是 structured ambiguity-set robust control；若机制由人工指定则算法差异小，若从 RGB WAM 学习则可识别性和计算代价都很弱。
- **评分：** novelty `6.0–6.8`；naturalness `7.5`；**FAIL**。
- **kill E0：** oracle 单机制 shift 不能被 uncertainty set 单独包含，或 best-of-N 仍随 N 恶化即 kill。
- **4卡可行性：** 低到中；bilevel rollout 很重，4 卡只能做受限机制 E0。

### C10｜Event-Surface Action Semantics

- **机制：** (1) 将 VLA chunk 实例化为局部 feedback field + RGB/proprio 可判定的 physical effect surface + timeout escape；(2) surface 到达前连续调节时长/幅度；(3) 事件而非固定 token 数终止 primitive；(4) 到达 surface 后才切换下一 primitive。
- **最强近邻：** options/SMDP termination、dynamic movement primitives、event-triggered/hybrid control，以及 [Adaptive Action Chunking](https://arxiv.org/abs/2604.04161) 与 A2C2。
- **不可约 delta：** 用任务物理 effect surface 同时定义 VLA action 的持续时间、反馈律和阶段交接。
- **致命反对：** 这是 option termination/hybrid guard 的 VLA 实现；若 effect surface 是人工 predicate，创新有限，若完全 RGB 学习，又易退化成 event classifier。
- **评分：** novelty `4.0–5.6`；naturalness `9.1`；**FAIL**。
- **kill E0：** oracle event termination 对 overshoot、under-execution、重复动作合计不降 >=30% 即 kill。
- **4卡可行性：** 高；但 novelty 下界未过。

### C11｜Online Action-Patch Algebra

- **机制：** (1) 根据已执行前缀的 expected/actual effect residual 估计 patch-basis Jacobian；(2) 在保护已完成关系的约束下求最小 time-stretch/gain/frame-offset patch；(3) 组合变换未执行 suffix；(4) 用真实 effect 在线更新 Jacobian。
- **最强近邻：** [A2C2](https://arxiv.org/abs/2509.23224) 已逐控制步读取新 observation、原 chunk action、时间和 base features，输出 bounded residual correction；CheckVLA 做 suffix repair。
- **不可约 delta：** 有闭包/组合律的显式 patch basis，而非自由 residual head。
- **致命反对：** “algebra”若没有证明的闭包、可交换/非可交换语义和跨任务收益，只是给 A2C2 residual action 手工选基。
- **评分：** novelty `2.7–4.2`；naturalness `8.8`；**FAIL**。
- **kill E0：** oracle patch 不优于取消 chunk + π0.5 重规划，或组合误差随 patch 数超线性增长即 kill。
- **4卡可行性：** 高；机制重叠使实验无意义。

### C12｜Counterfactual Physical Infeasibility Certificate + Minimal Repair

- **机制：** (1) 将指令编译为 reachability/collision/containment/order/robot-limit constraints；(2) 若无解，输出最小不可满足 core；(3) 用逐项 simulator relaxation 验证必要性；(4) 选择最小 enabling manipulation/允许的 referent edit，再执行原任务。
- **最强近邻：** [Do What? Teaching VLA Models to Reject the Impossible](https://arxiv.org/abs/2508.16292)；PNTC 的 minimal infeasible constraint subsets；TAMP 中的 enabling actions/constraint repair。
- **不可约 delta：** VLA negative capability 被物理 counterfactual 证书约束，并能触发最小实体 repair。
- **致命反对：** minimal unsat core + enabling action 是成熟规划组合；VLA 只作为感知/realizer，不足以把方法 novelty 推过 7。
- **评分：** novelty `5.2–6.8`；naturalness `8.2`；**FAIL**。
- **kill E0：** certificate necessity <90%，或最小 repair 不优于普通 TAMP replan 即 kill。
- **4卡可行性：** 高；主要依赖 constraint compiler，不依赖大训练。

### C13｜Causal Identity from Action-Effect Histories

- **机制：** (1) 为对象 slot 保存近期 robot action/contact-mode 到对象 motion/relation-change 的 response signature；(2) 遮挡/相同外观 swap 后按 effect likelihood 绑定历史角色；(3) 仍歧义时选择一个 policy-supported、同时推进任务并分离预测响应的普通操作动作；(4) 从结果更新 binding。
- **最强近邻：** [OA-WAM](https://arxiv.org/abs/2605.06481) 的 persistent object address 与 causal slot-intervention swap；[Action-Effect Memory](https://arxiv.org/abs/2606.12499) 的 action-conditioned history；active object perception 与 Bayesian data association。
- **不可约 delta：** object identity 本身由 intervention response history 定义，并让“任务动作”兼具 progress 与 identity disambiguation，而不是只靠外观/位置。
- **致命反对：** 这是 active data association/system identification；OA-WAM+AEM 已占据对象地址与 action-effect history，两者自然组合后的 residual 不足以给稳定 >7 下界。
- **评分：** novelty `4.3–5.8`；naturalness `7.8`；**FAIL**。
- **kill E0：** matched identical-object swaps 下 oracle response signature 的 ID accuracy <85%，或 dual-purpose action 不优于 appearance tracker+reobserve 即 kill。
- **4卡可行性：** 中；模拟器数据可编译，学习器可在 4 卡内完成，但 novelty 未过。

### C14｜Actual-Cause VLA Post-Training

- **机制：** (1) 对失败 episode rollback；(2) 以成功 alternative 替换早期 chunk 的不同子集，并尽量固定其余 policy；(3) 找到改变 terminal outcome 且任一严格子集都不足的 minimal actual-cause set；(4) 只更新这些决策并约束其余成功 chunk 分布不漂移。
- **最强近邻：** counterfactual credit assignment、causal contribution/actual-cause analysis、failure rollback/data repair，以及 FLARE 类 failure-aware post-training。
- **不可约 delta：** simulator 以 subset replacement 编译 chunk-level actual cause，并将它作为 VLA 参数更新 support，而不是仅作解释或 reward shaping。
- **致命反对：** later actions 无法在 counterfactual state 下真正“固定”，使 actual-cause estimand 不稳定；机制也可被解释为昂贵的 counterfactual credit assignment。
- **评分：** novelty `5.8–7.0`；naturalness `8.1`；**FAIL**。
- **kill E0：** minimal cause set 对 seed/alternative library 的 Jaccard <0.6，或只更新 cause chunks 不优于 TD/advantage weighting 即 kill。
- **4卡可行性：** 中低；rollback 组合爆炸，4 卡只适合短 horizon 小集合。

### C15｜Planner-Invariant Action Dominance

- **机制：** (1) 从 paired simulator interventions 学三值关系：A dominates B / B dominates A / incomparable；(2) 只有当 A 在所有注册 nuisance 下 task effect 不差且 protected-relation violation 不高时才允许 dominance；(3) planner 仅剪掉被支配动作，保留 incomparable modes；(4) 评估真实性能对 search budget N 的不变性。
- **最强近邻：** Pareto/robust dominance、distributionally robust optimization、pessimistic model-based planning，以及 Imperfect World Models are Exploitable/SCWC 的 optimizer's-curse framing。
- **不可约 delta：** WAM 不输出 scalar reward/confidence，而输出跨干预可审计的 partial order；其 consumer 只能做 dominance pruning。
- **致命反对：** robust Pareto dominance 是现成决策对象；WAM 只是估计关系，且“所有 nuisance”在有限训练集上无法支持强 dominance claim。
- **评分：** novelty `5.0–6.6`；naturalness `7.5`；**FAIL**。
- **kill E0：** oracle partial-order pruning 不能让真实性能对 N 的负斜率消失，或误剪可行 mode >5% 即 kill。
- **4卡可行性：** 中；pairwise labels 昂贵但可模拟，当前不授权。

## 淘汰逻辑汇总

1. **被单篇 exact mechanism 高度覆盖：** C5（counterexample-guided symbolic-geometric repair/PNTC）、C11（A2C2）、C3（CoRe + CheckVLA）。
2. **被成熟经典机制 + 当前载体自然组合覆盖：** C1/C2（active diagnosis/dual control）、C4/C8（reversibility/contingency/recovery planning）、C6（POMDP policy tree）、C9（robust causal MBRL）、C10（option termination/hybrid guard）、C15（robust Pareto dominance）。
3. **近期 VLA/WAM 组件已占去大部分空间：** C7（QuoVLA/GEAR-VLA/latent action）、C12（IVA + TAMP）、C13（OA-WAM + AEM）、C14（counterfactual credit assignment + failure-aware post-training）。

最重要的审查原则是：**“没有一篇论文同时包含全部组件”不是 >7 novelty 的充分条件。** 当组件之间的组合是该问题的标准自然解法、且没有新的不可约统计对象、控制保证或因果识别结果时，严格下界必须降到 7.0 或以下。

## Search integrity

- 使用了本地 research-wiki/既有 strict-jury 证据池，并针对 action tree、物理不可行性、counterexample constraint、effect quotient、action-effect identity、recoverability、causal minimax、event termination、actual-cause credit 和 robust dominance 做 exact-mechanism 检索。
- 关键结论只依赖 primary arXiv/论文页面；未将第三方摘要或搜索引擎未命中当作“不存在”。
- 统一 paper-search 的 arXiv connector 出现 SSL EOF，Semantic Scholar 多次 429；这些只记为检索限制，不作为 novelty 正证据。
- 本轮停止继续扩展检索，以免在低下界候选上无边界搜索。

## Fresh-jury 复核

按 novelty-check 要求，本轮只调用了一名 fresh strict jury（`gpt-5.6-sol`, xhigh）。它没有看到本报告的评分结论，只读取两个未排序候选池，并自行核验 primary sources。由于 reviewer 与 executor 同属 OpenAI 模型家族，其裁决按规则记为 **same-family provisional**，不是独立外部证明。

该 jury 机械规范化后的 15 项同样得到 **KEEP 0/15**；最高项是 Actual-Cause VLA Post-Training，区间仅 `[5.8, 7.0]`。它还给出三条比本执行器更强的负面判断：OA-WAM + Action-Effect Memory 把因果身份压到 `[4.3,5.8]`；classical contingent contact planning + A2C2/DREAM-Chunk 把 action tree 压到 `[4.8,6.3]`；Counterexample-Guided Repair + ReSYNC 把 plan-family constraint compilation 压到 `[2.5,4.1]`。因此，无论采用本执行器较宽松的区间还是 fresh jury 更保守的区间，都没有候选通过硬门槛。

## 最终裁决

**严格保留：0 / 15。**  
**实验授权：无。**  
**4×A100：本轮未使用。**

下一轮若继续，不应在上述机制上再加一个 memory/confidence/WAM head；必须先提出一个无法被 classical planning/control + 当前 VLA/WAM 直接分解吸收的新 decision/intervention/optimization/causal object，再做 fresh exact-mechanism jury。
