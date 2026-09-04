# Round 1 Refinement

## Problem Anchor

- **Bottom-line problem**：当任务、语言指令和对象语义不变，但功能几何让原 action chunk 的局部片段变得物理不可行时，连续动作 VLA 应只改变真正失效的局部响应，同时保留未受影响的行为与其他可行修正方式。
- **Must-solve bottleneck**：现有几何可行性训练可以惩罚碰撞时间点，但尚不能清楚地区分“提高可靠性”与“把邻近可行模式一起压掉”；原 BLSM 又把 negative 的违规时间索引直接套到不同阶段的 positive 上，比较对象不成立。
- **Non-goals**：不声称首次使用几何反事实、首次做 action-time-local feasibility loss、保留全部物理可行模式、提供真实机器人安全保证，或在部署期使用 WAM/MPC reranking。
- **Constraints**：无触觉；训练部署在用户个人目录；四张 A100 可用但 E0 必须先通过非 GPU 数据门；冻结或参数高效微调 π0.5/连续动作头；部署输入保持 RGB、proprioception 和语言，不增加 simulator oracle。
- **Success condition**：在共享分支状态的 geometry-flip pairs 上，相比 active-violation geometry loss 与 whole-chunk preference，方法在相近 invalid-execution reduction 下显著减少 complement drift，并提高 compiler-roster coverage / worst-mode success；错配 mask 或 pair 后增益应消失。

## Anchor Check

- 原始瓶颈仍是：局部物理不可行性调优不能破坏未受影响行为与其他可行修正。
- reviewer 建议把比较对象移动到真正共享的物理决策支持上；这强化了 anchor，没有改成规划或安全检测问题。
- 拒绝添加 learned phase estimator 或 WAM，因为它们会把一个训练目标问题扩成多模块系统。

## Simplicity Check

- 唯一主贡献改为 **common-state reference-adjusted flow preference**。
- 删除单独命名的 `L_mode`；K 个 positive 直接等权进入同一个 preference objective。
- 首个违规段只用于找到 backward-search 区域，不再宣称是独立方法贡献。
- `L_pres` 明确是标准 reference/replay preservation regularizer，不宣称新颖。

## Changes Made

1. 用 **latest branchable state + decision prefix** 替代对 positive 复用 negative mask。所有候选从完全相同的 simulator/controller/RNG state 开始；比较的是相同条件下的 competing action prefixes，而不是分叉后逐时刻状态语义。
2. 给出 π0.5 原生 flow-matching residual preference 公式：positive/negative 共享 flow time 与 base noise，reference 分支 stop-gradient，K modes 等权聚合，无额外 margin。
3. 将 feasibility 编译器改成 backward checkpoint search，并给每条 record 加 fixed-H 与 terminal-event contract。
4. 将论文 claim 收缩为：相同 branchable state 下，局部 flow preference 比 `L_geo` 与 whole-chunk preference 造成更少支持集漂移。

## Revised Proposal

# Research Proposal: Common-State Boundary Flow Preference (CBFP)

## Technical Gap

arXiv:2604.17896 已经用 counterfactual obstacle placement 与 active-violation signed-distance loss 训练 diffusion VLA，因此几何反事实和局部可行性惩罚本身不是创新。真正未解决的是：一个 shared-parameter action generator 在压低 invalid continuation 时会如何改变同一状态下其他 feasible continuations，以及能否把这种 distributional movement 限制在做出避障/适配决策所需的短前缀内。

任意成功轨迹与失败轨迹不应按 raw time 对齐。CBFP 只比较从同一完整 simulator checkpoint 出发的 competing prefixes；它不声称这些分叉轨迹在后续每一时刻处于相同技能阶段。

## Method Thesis

给定 edited geometry 中的最新可分支共同状态，使用冻结参考校正的 K-positive flow-matching preference 压低会导致首个物理违规的 continuation prefix，并用标准 reference preservation 限制其余 action support 的漂移。

## Contribution Focus

- **Dominant contribution**：common-state, geometry-flip-conditioned reference-adjusted flow preference。
- **Supporting evidence, not a second contribution**：compiler-roster coverage、worst-mode success 与 outside-prefix drift。
- **Non-contributions**：first-violation mask、planner、mode clustering、reference regularization、几何 backbone、WAM。

## Data Unit: BranchRecord

每条 record 包含：

1. 成功基础轨迹与可见的 compiler-minimal 几何编辑 `g+ → g-`；同一原 action chunk 在 `g-` 中因预注册几何事件失败，但 `g-` 仍可解。
2. 在 `g-` 重放 invalid chunk，得到首个违规时刻 `τ-`。
3. 从 `τ--1` 向前逐 checkpoint 搜索。每个 checkpoint 必须恢复完整 simulator state、controller cache 和 RNG state。选择满足下列条件的最新 checkpoint `z_b`：
   - invalid continuation `a-` 在固定 H 内触发指定违规；
   - planner/controller 能产生至少 K 个成功 continuation；
   - 所有 positive 从相同 `z_b`、相同控制频率、相同动作表示开始，并在固定 H 内满足同一 terminal predicate；
   - 至少 K 个 positive 在轨迹/接触事件聚类后仍为不同 roster modes。
4. 定义 decision prefix `D=[0,d)`：`d` 是 invalid continuation 从 `z_b` 到首次违规（含违规步）的长度。positive 与 negative 只作为从相同 `z_b` 出发、长度 d 的 competing action prefixes 进行整体比较；不做逐状态 phase-equivalence claim。
5. 若任一条件不满足，记录 exclusion reason，并保留在 attempted-pair denominator。

## Native Flow Objective

选择 π0.5/flow-matching action head。对任一候选动作 `a ∈ R^(H×A)`、条件 `c_b`、flow time `t∼U(0,1)` 与 base noise `ξ∼N(0,I)`，构造：

`x_t(a)=(1-t)ξ+t a`，target velocity `u(a)=a-ξ`。

对 prefix D 定义逐时间、逐动作维归一化 residual：

`e_θ(a,c_b,D;t,ξ)=mean_{s∈D,j}[v_θ(x_t(a),c_b,t)_{s,j}-u(a)_{s,j}]²`。

positive 与 negative 在每次比较中使用相同的 `t` 和同形状 base noise `ξ` 作为 common random numbers。冻结参考检查点 `θ_ref`，并对参考输出 stop-gradient：

`g_θ(a)=stopgrad(e_ref(a,c_b,D;t,ξ))-e_θ(a,c_b,D;t,ξ)`。

第 k 个 positive 的参考校正 preference margin 是：

`m_k=g_θ(a_k+)-g_θ(a-)`。

核心 loss 为无额外 margin 的等权 K-positive logistic preference：

`L_pref=(1/K) Σ_k softplus(-β m_k)`，其中 `β` 只做 residual-scale normalization：在训练前用冻结 reference 验证对上把 margin 的 robust standard deviation 归一到约 1，随后固定。

这里没有单独 `L_mode`；每个 roster mode 的代表 continuation 以相同权重进入 `L_pref`。若使用 diffusion noise-prediction head，则只把 `v_θ/u` 换成其原生 noise residual，不混用两种参数化。

## Preservation Regularizer

`L_pres` 是明确非创新的标准 regularizer：

- 在 BranchRecord 的 `D` 外，对 positive、negative 与普通 replay actions 的可训练 flow output 匹配冻结 reference output；
- 同时保留原始 imitation minibatch 的 native flow-matching loss。

总目标：`L=L_imit+λ_pref L_pref+λ_pres L_pres`。两项 λ 在 pair-held-out validation 上按预注册网格一次选择，约束 unedited success 与 outside-prefix output drift 后最大化 invalid-vs-feasible separation。reference 全程冻结；simulator/planner 无梯度。

## Inference

部署时只保留微调后的 VLA；输入仍是 RGB、proprioception、语言。compiler、planner、几何 oracle 和 reference checkpoint 均不参与推理。

## Claim-Driven Validation

### Primary claim

给定来自同一 latest-branchable physical state 的 alternatives，reference-adjusted preference over the branch decision prefix 相比 active-violation geometry shaping 与 whole-chunk preference，在相近 invalid-execution reduction 下造成更少的 unedited/complement drift，并更好保留 compiler-roster support。

### Minimal systems

1. ordinary imitation；
2. arXiv:2604.17896-style active-violation `L_geo`；
3. whole-chunk reference-adjusted preference；
4. CBFP without `L_pres`；
5. full CBFP。

### Decisive metrics

- edited-scene success 与 invalid-reference execution；
- unedited success；
- outside-prefix flow/output drift；
- compiler-roster coverage 与 worst-mode success；
- paired simulator validity ranking 与 reference-adjusted margin 的 Spearman ρ。

### Kill tests

- 打乱 BranchRecord pair identity 后仍保留超过 50% 增益：停止；
- 用随机等长 prefix 替换 D 后仍保留超过 50% 增益：停止；
- `L_geo` 与 CBFP 在 edited success、coverage、worst-mode 上均相差 <3pp：停止；
- 去掉 `L_pres` 不增加 drift 或完整方法使 unedited success 下降 >2pp：停止；
- margin 与 simulator validity ranking 的 Spearman ρ<0.30：停止。

## Feasibility Gate

GPU 前先用 100–200 attempted episodes 验证：eligible branchable yield、visible/collision mesh 一致、checkpoint hash 可复现、固定 H/terminal contract、K-mode multiplicity。任一约束族 eligible <8%、总体 <15%，或有 ≥2 实质 roster modes 的 records 少于 eligible 的 25%，则不启动 VLA 训练。

E0 只用一个 backbone、一个 action-head/LoRA 配置、2–3 constraint families；先 1 seed sanity，再对通过的 variants 做 3 seeds。完整大训练不在本轮授权范围内。

