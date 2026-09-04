# GISS 失败后的有界方法 Pivot：5 个候选

**日期：** 2026-08-31  
**约束：** 无触觉/力觉；只保留方法或学习机制，不做纯诊断/benchmark；预算上限为 4×A100；未启动任何实验。  
**筛选规则：** 预估 novelty 区间上界必须严格大于 7.0。以下恰好五项均满足；分数是查新后的风险区间，不是通过声明。

> **Provisional caveat：** 本轮完成了两路只读 candidate generation、exact-key 机械去重和当前 primary-source 威胁核验。计划中的 fresh strict jury 在有界等待内未返回，已按主线程要求终止等待。因此下述取舍属于 `same-family / provisional`，不能视为独立接受裁决。尤其是 2026 年 6–8 月的密集近邻仍可能压低区间。

## 证据边界与先行淘汰

本轮显式扣除了以下已占据机制：

- [Metamorphic Testing, 2602.22579](https://arxiv.org/abs/2602.22579) 已占据 controlled transformation + VLA behavior diagnostic；[CASC, 2607.27261](https://arxiv.org/abs/2607.27261) 已占据 matched-state paired action-sensitivity audit。
- [DreamSteer, 2607.02865](https://arxiv.org/abs/2607.02865) 已占据“VLA 提候选—WAM rollout—value rerank”；普通 WAM reranking 不再作为候选。
- [WALL-WM, 2606.01955](https://arxiv.org/abs/2606.01955) 已占据 semantic-event pretraining 与 variable-length event execution。因此“只把 chunk 切到事件边界”的路线预估上界降至 7.0，淘汰。
- [Act, Think or Abstain, 2603.05147](https://arxiv.org/abs/2603.05147) 与 [PhysReflect-VLA, 2606.27146](https://arxiv.org/abs/2606.27146) 已分别覆盖复杂度分类式 abstention 和 feasibility-check + reflection；纯拒绝分类器淘汰。
- [Learning Action Manifold, 2605.11832](https://arxiv.org/abs/2605.11832) 已使用“action manifold”表述，但其实际机制是 clean-action prediction，并非显式 set-valued feasible support。下文仅在这个更窄、可证伪的差异上保留候选 1。
- 单 chunk repair field、barrier distillation 和 test-time trajectory refinement 受到 DreamSteer、DreamTrajectory、World Pilot、constrained diffusion 等组合威胁，当前预估上界不稳定或不超过 7.0，未保留。

## 候选 1：Action-Fiber Set Diffusion

**Problem。** 对同一指令、状态和功能几何，正确动作通常不是唯一轨迹，而是一组不同的无碰撞 approach/contact modes。单条 demonstration 的 behavior cloning 把“一个观察到的解”误当成“全部可行支持集”，在新槽宽、挂点和遮挡布局下容易 mode collapse。

**核心机制。**

1. 对每个 simulator state 与可见功能几何，用示范扰动、短程 planner 和 rollback execution 构造无序的可行 action-chunk 集合；保留不同通道、绕行侧和 contact schedule，而不是只留最优一条。
2. 让 geometry-conditioned diffusion head 一次生成 (K) 个 chunk；用 permutation-invariant unbalanced optimal transport 对齐生成集与目标集，同时惩罚未覆盖的可行 mode 和落在不可行区域的概率质量。
3. 闭环时只采样一个 mode 执行短前缀，重新观察后再生成集合；不增加 feasibility classifier，也不对 WAM rollout 候选排序。

**为什么不是已知机制。**

- 不是 Metamorphic Testing：它改变训练目标和 action support，不输出 transformation diagnostic。
- 不是 CASC：几何变化是 action-relevant，目标不是 nuisance 下保持 action invariance，也不以 offline drift 为结果。
- 不是 AffordanceVLA：不是 Which/Where/How 的单点 affordance decomposition，而是显式监督整段可行 action set 的覆盖与无效质量。
- 不是 GEAR-VLA：不是给既有 decoder 加 geometry feature/canonical action；改变的是生成分布的集合级学习对象。
- 不是 DreamSteer：不是多候选想象后 argmax；训练后单个 actor 本身表示多模态可行支持。
- 不是 RPDiff：RPDiff 生成 terminal relational 6-DoF placement poses；这里学习带时间和接触顺序的 action-chunk set。
- 不是普通 WAM reranking：主机制不需要 WAM、value head 或 candidate scoring。

**最危险近邻。** [RPDiff, 2307.04751](https://arxiv.org/abs/2307.04751) 的 local-geometry-conditioned multimodal relational pose diffusion。精确重叠是“几何条件下多解分布”；剩余差异是 terminal pose distribution 对比 rollback-verified、temporally extended feasible-action set，以及 set-to-set coverage objective。次级威胁是 2605.11832 的“action manifold”命名。

**预估 novelty：7.3–7.9/10。** 上界成立的前提是 prior art 中没有同样的 viable-chunk-set supervision + unbalanced set transport；若只是给普通 diffusion 多采样，分数立即降至 6.x。

**自然性：8.5/10。** 多个可行接触/绕行 mode 是机器人操作的原生结构，而非为了论文构造的 latent。主要不自然点是目标集合由 planner 近似，无法声称穷尽真实可行集。

**最强反对意见。** planner 生成的“集合”可能只是昂贵的数据增广；收益也可能完全来自更多 successful trajectories，而非集合目标。

**最小 kill experiment。** 在 held-out aperture、shelf、hook 三个 geometry family 上，固定数据量、backbone、训练步数和测试采样数，对比普通 conditional diffusion。预注册 kill：在 fixed precision 下 viable-mode recall 未提升至少 **10 个百分点**，或 native closed-loop success 未提升至少 **5 个百分点**，或把 baseline 的 sample count 匹配到 (K) 后增益消失，则杀死集合学习主张。

**4×A100 feasibility。** 冻结 pi0.5/VLM backbone，只训练 action diffusion adapter；simulator/CPU 离线缓存约 5–10 万个 state 的 (Kleq8) rollback chunks。预计 48–80 A100-GPU-hours，即 4 卡约 12–20 小时训练，另加 1–2 天并行数据生成。无需 foundation-scale WAM，也无需触觉。

**Route card。** Representation：geometry-conditioned action-set latent（不属于 WAM prediction）；control use：direct generative VLA policy；update regime：frozen backbone + action-head/LoRA；data regime：offline simulator.

## 候选 2：Counterfactual Boundary Score Matching

**Problem。** 正示范只告诉模型“这条 action 在此 geometry 成功”，没有告诉它哪一个可见结构使动作有效。随机负样本又过于容易，且会错误压低其他合法 mode。需要 minimally feasibility-flipping 的功能几何 hard negative，而不是外观 nuisance。

**核心机制。**

1. 对成功 chunk 做最小功能几何编辑，使同一 chunk 从 valid 变 invalid；保留两个 geometry 下各自的 alternative-positive chunks，并用 simulator 确定首次 clearance/contact violation 时间段。
2. 对 action diffusion score 做局部 pairwise shaping：在原 geometry 吸引该 chunk，在反事实 geometry 只于 violation segment 排斥它，避免把整条技能都标成坏动作。
3. 用 alternative-positive envelope 约束排斥梯度，使 hard negative 远离 invalid support 的同时，不降低其他可行 action modes 的密度。

**为什么不是已知机制。**

- 不是 Metamorphic Testing：paired intervention 被用于训练 score field，而非测试 trajectory variation。
- 不是 CASC：CASC 的 nuisance 应保持 expert action；这里的 functional edit 被设计成翻转同一 action 的物理可行性。
- 不是 AffordanceVLA：监督单位是 action×geometry 的 counterfactual compatibility，不是 where/how affordance label。
- 不是 GEAR-VLA：不是几何 feature alignment；新增的是 collision-localized counterfactual score loss。
- 不是 DreamSteer：不是部署时采样、rollout、打分；训练后直接生成适应该 geometry 的 chunk。
- 不是 RPDiff：不是学习目标物体的终端相对位姿；负样本作用在完整 action chunk 的局部时间段。
- 不是普通 WAM reranking：WAM 可完全缺席，且没有 test-time candidate set。

**最危险近邻。** [RoCoDA, 2411.16959](https://arxiv.org/abs/2411.16959) 已把 counterfactual augmentation、causal invariance 与 SE(3) equivariance 用于 robot imitation。精确差异是 RoCoDA 修改 task-irrelevant subsets 或变换正样本；本候选使用 task-relevant geometry edit 来翻转同一 action 的 feasibility，并把 negative signal 定位到 violation segment。[CofactVLA, 2608.04396](https://arxiv.org/abs/2608.04396) 的 language-masked counterfactual flow projection 是另一高威胁，但其干预语义是去除 visual confounding，而非物理可行性翻转。

**预估 novelty：7.4–8.0/10。** 这是五项中最清楚的 training-mechanism pivot，但若已有工作使用 minimal collision-flip pairs 对 diffusion score 做同类局部 repulsion，上界会快速坍塌。

**自然性：8.8/10。** “外观几乎相同但 action 物理含义相反”正是视觉策略难以从正示范学到的边界信息；局部 violation supervision 与控制失败直接对应。

**最强反对意见。** simulator 生成的 hard negatives 可能带 renderer/mesh artifact，模型学到 intervention fingerprint，而不是真正的功能几何。

**最小 kill experiment。** 在训练未见的 minimal edits 上对比 positive-only、random-negative、整段 pairwise-negative 和本方法。预注册 kill：transferred-action collision rate 相对最强 baseline 未下降至少 **20%**；或 nominal success 下降超过 **2 个百分点**；或 alternative-mode entropy/coverage 下降超过 **10%**，任一成立即杀死。

**4×A100 feasibility。** 冻结 pi0.5 backbone，训练 LoRA + action head；离线生成约 10 万 paired states/chunks 与 violation masks。预计 32–64 A100-GPU-hours，4 卡约 8–16 小时，主要成本在 simulator pair generation。无需训练完整 WAM。

**Route card。** Representation：原 VLA visual/action latent；control use：direct policy；update regime：paired counterfactual post-training；data regime：offline simulator.

## 候选 3：Surface-Pair Gauge Action Representation

**Problem。** base-frame 或 end-effector-relative action 仍把 motion 绑定到训练对象的尺寸和布局；真正决定 insertion、hanging、sliding 的是两个相互作用功能表面之间的局部几何关系，而不是单一物体坐标系。

**核心机制。**

1. 从 RGB 派生的 geometry tokens 或 simulator mesh 中选择有序 functional surface pair，使用两侧 centroid、normal、principal tangent、间距和相对 curvature 构造局部 gauge。
2. 把一个 relation event 内的示范运动编码为 gauge-covariant twist-spline coefficients 与 gripper events；VLA 预测 surface pair 和 coefficients，而非 Cartesian waypoints。
3. 在未见 geometry 上重新计算 gauge，解析实例化完整 trajectory，再用小型 learned dynamics residual 修正 reachability；不做多候选搜索。

**为什么不是已知机制。**

- 不是 Metamorphic Testing：它是可训练 action coordinate system，不是变换一致性测试。
- 不是 CASC：不要求 nuisance invariance，也不测 action drift；目标是 functional geometry 下可迁移的协变解码。
- 不是 AffordanceVLA：AffordanceVLA 给出 where/how act；这里以两个表面共同定义完整 event trajectory 的 gauge。
- 不是 GEAR-VLA：GEAR-VLA 的主要威胁是 geometry-aware/canonical action，但本候选不是单一 end-effector/embodiment canonicalization，而是 dynamic two-surface relational frame 与 covariant spline。
- 不是 DreamSteer：没有 WAM rollout 或 value ranking。
- 不是 RPDiff：RPDiff 在 local geometry 上生成 terminal relative pose；这里解析生成从 approach 到 relation change 的整段 motion。
- 不是普通 WAM reranking：直接一次解码，无 imagined candidate comparison。

**最危险近邻。** [GEAR-VLA, 2606.08530](https://arxiv.org/abs/2606.08530)。重叠是显式 geometry prior 与 canonicalized action representation；可保留 delta 必须是“ordered interacting surface pair 决定 trajectory gauge”，且要证明这不是 end-effector-relative canonicalization 的换名。RPDiff 是第二危险近邻。

**预估 novelty：7.2–7.8/10。** 高度依赖对 GEAR-VLA full method 与相关 surface-frame manipulation 的进一步代码级核验；这是区间较宽的原因。

**自然性：8.3/10。** 功能操作本来就是 surface-to-surface relation 的变化；用两侧共同坐标表达 motion 比对象中心或机器人基座更贴合任务。风险是 reliable surface-pair extraction 可能成为新的 perception bottleneck。

**最强反对意见。** 贡献可能被描述成“手工设计 coordinate frame + spline decoder”，而非学习机制；若 surface detector 用 privileged mesh，视觉 VLA 主张也站不住。

**最小 kill experiment。** 在训练范围外的 slot width、rack curvature、object scale、hinge layout 上，以相同 backbone/data 比较 base-frame、EEF-relative、single-surface frame 和 two-surface gauge。预注册 kill：平均 success 对最强表示增益小于 **5 个百分点**；或移除任一 surface 后下降小于 **2 个百分点**；或 RGB-estimated gauge 的收益不足 privileged gauge 收益的 **50%**，任一成立即杀死核心机制。

**4×A100 feasibility。** 冻结 VLM/pi0.5 主干，训练 patch-pair selector、spline coefficient head 与轻量 residual controller；simulator mesh 只用于训练标签，测试必须从 RGB-derived geometry 获得 surface。预计 48–96 A100-GPU-hours，4 卡约 12–24 小时，加 1–2 天 preprocessing。

**Route card。** Representation：explicit relational geometry/action representation（近 R4，但无独立 future simulator）；control use：direct action decoding；update regime：frozen backbone + structured heads；data regime：offline simulator.

## 候选 4：Geometry-Conditioned Backward Viability Tubes

**Problem。** forward imitation 或短程 collision cost 会选择“当前无碰撞、未来却无解”的 branch，例如进入错误侧的狭窄通道、错误预抓位或不可逆的 contact configuration。功能几何改变的是 goal-reachable predecessor set，而不只是下一步安全性。

**核心机制。**

1. 从成功 goal-contact states 出发，在 simulator rollback transitions 上训练 geometry-conditioned reverse-dynamics diffusion，生成多模态的 collision-free predecessor/action tubes。
2. 把 reverse samples 压缩成当前观察条件下的 viability tube；forward VLA decoder 只从与当前 robot/object state 相交的 tube segment 生成动作。
3. 若当前状态不在任何 goal tube 内，生成朝最近可达 tube segment 的 recovery trajectory，而不是继续 nominal task action。

**为什么不是已知机制。**

- 不是 Metamorphic Testing：它改变规划/生成的可达支持，不是行为诊断。
- 不是 CASC：不以 paired observation drift 为信号；目标是几何条件下的 backward goal reachability。
- 不是 AffordanceVLA：不是选择局部 affordance；tube 编码多步动态连通性。
- 不是 GEAR-VLA：不是更强 3D 表征或 action canonicalization；核心是 reverse reachable support。
- 不是 DreamSteer：没有对有限 forward candidates 做 WAM-value argmax。
- 不是 RPDiff：RPDiff 给终端 relational pose；tube 给从目标反向延展的 state-action predecessor distribution。
- 不是普通 WAM reranking：world model 若存在，是反向生成模型并直接约束 actor support，不是 rollout scorer。

**最危险近邻。** [BaRC, 1806.06161](https://arxiv.org/abs/1806.06161) 与 reverse curriculum generation 已用 backward reachability 扩展训练初态。精确 delta 是：它们把 reachability 用作 RL curriculum；本候选学习随可见 functional geometry 变化的 multimodal predecessor tube，并在 VLA 推理时作为 action-support condition。若最终只剩“从目标倒着采样训练数据”，则 novelty 不成立。

**预估 novelty：7.2–7.8/10。** 理论母机制不新，但把 geometry-conditioned backward viable support 变成视觉 VLA 的在线 action representation 仍有明显空位；实现若退化为 reverse curriculum，分数低于 7。

**自然性：8.1/10。** goal reachability 比单步 collision avoidance更接近机器人在狭窄功能结构中的真实决策。代价是 reverse dynamics 在接触/摩擦下多值且难学，无触觉条件进一步限制可观测性。

**最强反对意见。** 反向 contact dynamics 未必物理可逆；simulator rollback 产生的 predecessor tube 可能无法对应真实 forward policy distribution。

**最小 kill experiment。** 先用 oracle simulator tube 做机制门：设计 locally safe 但只有一条 branch goal-reachable 的三类 geometry。若 oracle tube 相对 short-horizon collision MPC 未把 dead-end entry 降低至少 **15 个百分点**，直接 kill；oracle 通过后，若 learned tube 的 success 增益不足 **5 个百分点**或 false-recovery rate 超过 **10%**，同样 kill。

**4×A100 feasibility。** 使用 RoboTwin/ManiSkill 类 simulator 的 snapshot/rollback 生成 predecessor data；训练低维 reverse diffusion + tube encoder + 小型 VLA adapter，冻结基础 pi0.5。预计 80–128 A100-GPU-hours，4 卡约 20–32 小时；四卡预算可行，但这是五项中 simulator engineering 风险最高者。

**Route card。** Representation：R4 explicit/latent reverse dynamics hybrid；control use：U2/U4-like goal-conditioned support generation，不做 candidate rerank；world-model update：offline frozen after training；data regime：simulator.

## 候选 5：Recovery-Support Diffusion for Physical Refusal

**Problem。** 当可见几何使请求暂时或永久不可能时，普通 VLA 的 action distribution 仍只有 task-progress demonstrations，因此会持续挤压、碰撞或重复无效动作。仅输出一个“refuse”类别不能提供安全撤离，也无法在几何重新可行时恢复任务。

**核心机制。**

1. 程序化构造 matched feasible/impossible geometry pairs；对 impossible cases 用 constrained MPC/scripted controllers 收集 safe hold、retract、reobserve、regrasp trajectory sets，而非二分类 refusal labels。
2. 训练一个 geometry-conditioned trajectory diffusion，使其 support 随 feasibility sweep 从 task-progress trajectories 连续转移到 recovery trajectories，并对 near-boundary feasible cases 保留任务支持。
3. 在 recovery target 尾部加入 absorbing safe-hold segment；只有新视觉证据重新使 goal tube/clearance 可行时，replanning 才能离开 safe support 并恢复任务。

**为什么不是已知机制。**

- 不是 Metamorphic Testing：impossible pairs 是生成式 recovery supervision，不是 pass/fail metamorphic oracle。
- 不是 CASC：functional infeasibility 应改变动作，不是 nuisance 下保持 expert action；输出是安全 trajectory distribution 而非 drift。
- 不是 AffordanceVLA：不是判断 where/how 可作用，而是当所有 task-progress support 消失时生成 hold/retract/reobserve，并支持后续恢复。
- 不是 GEAR-VLA：不是几何 feature 或 canonical action；训练分布显式包含 impossible-case recovery support。
- 不是 DreamSteer：当候选集合中没有可行动作时，reranking 只能选“最不坏”；本机制直接生成训练过的 recovery trajectories。
- 不是 RPDiff：不是 terminal placement pose；处理的是动态不可行区间的安全动作和恢复条件。
- 不是普通 WAM reranking：无需 imagined candidate score；单一生成策略直接在 task/recovery support 间转移。

**最危险近邻。** [PhysReflect-VLA, 2606.27146](https://arxiv.org/abs/2606.27146) 已做 candidate physical-feasibility evaluation、action explanation 和 reflection-guided correction；[Act, Think or Abstain, 2603.05147](https://arxiv.org/abs/2603.05147) 已做 abstention routing。可保留 delta 是“不是检测/路由，而是 impossible-case 的生成式 recovery support，以及 feasibility 恢复后的可逆恢复”。如果最终实现只是 feasibility head + STOP token，则立刻撞车。

**预估 novelty：7.1–7.6/10。** 这是刚过筛选线、撞车风险最高的保留项。其论文性必须由恢复轨迹支持和可逆 resume 机制承担，不能以“VLA 学会拒绝”作为主标题。

**自然性：8.0/10。** 安全失败应是一个动作技能，而不是分类标签；hold/retract/reobserve 与机器人部署直接相关。局限是 simulator 中的 impossible 标签可能过于干净，且无触觉时接触后的真实可行性不可完全观测。

**最强反对意见。** 该方法可能只是把 scripted recovery demonstrations 混入 diffusion policy；拒绝质量来自数据，而非 support-transport learning。

**最小 kill experiment。** 使用 opening-too-small、blocked articulation、unreachable contact 三类 matched pairs，并包含临界可行宽度。预注册 kill：impossible cases 的 damaging task motion 未相对最强 abstain/reflect baseline 降低至少 **50%**；或 near-boundary feasible success 下降超过 **3 个百分点**；或 geometry 恢复后在规定 horizon 内 resume success 低于 **70%**，任一成立即杀死。

**4×A100 feasibility。** 冻结 pi0.5/VLM backbone，训练 trajectory diffusion adapter；recovery 数据由 simulator MPC/script 生成，无需触觉。约 5–8 万 paired episodes，预计 48–96 A100-GPU-hours，4 卡约 12–24 小时；无需训练大 WAM。必须单独记录数据量，避免把更多 recovery demonstrations 误写成机制收益。

**Route card。** Representation：geometry-conditioned task/recovery action support（非 WAM）；control use：direct generative policy；update regime：offline post-training；data regime：simulator.

## 收束结论

保留 **5/14** 项，均为方法/学习机制，且预估 novelty 上界严格大于 7.0。当前最值得继续做纯纸面查新的两项是 **Counterfactual Boundary Score Matching** 与 **Action-Fiber Set Diffusion**；这不是实验授权。下一步只能先做各自的 exact-mechanism code/supplement audit 与数据可构造性检查，之后再决定是否进入 feasibility E0。本轮未启动 GPU 或 simulator 实验。

