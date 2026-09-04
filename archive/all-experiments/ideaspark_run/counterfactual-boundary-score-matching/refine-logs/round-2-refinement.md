# Round 2 Refinement

## Problem Anchor

- **Bottom-line problem**：当任务、语言指令和对象语义不变，但功能几何让原 action chunk 的局部片段变得物理不可行时，连续动作 VLA 应只改变真正失效的局部响应，同时保留未受影响的行为与其他可行修正方式。
- **Must-solve bottleneck**：现有几何可行性训练可以惩罚碰撞时间点，但尚不能清楚地区分“提高可靠性”与“把邻近可行模式一起压掉”；原 BLSM 又把 negative 的违规时间索引直接套到不同阶段的 positive 上，比较对象不成立。
- **Non-goals**：不声称首次使用几何反事实、首次做 action-time-local feasibility loss、保留全部物理可行模式、提供真实机器人安全保证，或在部署期使用 WAM/MPC reranking。
- **Constraints**：无触觉；训练部署在用户个人目录；四张 A100 可用但 E0 必须先通过非 GPU 数据门；冻结或参数高效微调 π0.5/连续动作头；部署输入保持 RGB、proprioception 和语言，不增加 simulator oracle。
- **Success condition**：在共享分支状态的 geometry-flip pairs 上，相比 active-violation geometry loss 与 whole-chunk preference，方法在相近 invalid-execution reduction 下显著减少 complement drift，并提高 compiler-roster coverage / worst-mode success；错配 mask 或 pair 后增益应消失。

## Anchor Check

- reviewer 确认 anchor 保持不变；当前缺陷是 estimator 可从 suffix 泄漏候选身份，而不是问题漂移。
- 修复只改变 flow 输入支持，不新增模型或任务。
- 本轮拒绝重新引入事件对齐网络、WAM 或独立 critic。

## Simplicity Check

- 继续保持一个核心 preference loss 和一个标准 preservation regularizer。
- 将 variable decision prefix 删除，统一为部署一次实际执行的固定 `h_exec` 步。
- 使用 candidate-independent frozen-reference padding 消除 suffix 泄漏，不修改 π0.5 attention 结构。
- 删除 β 校准，固定 `β=1`；不增加 pilot-tuned scale。

## Changes Made

1. **Prefix-identifiable input**：positive/negative 只在前 `h_exec` tokens 保留候选动作；其余 H−`h_exec` tokens 对所有候选完全相同，并来自同一个冻结参考 padding chunk。双向 action expert 因此无法从 suffix 识别候选。
2. **Training–deployment contract**：`h_exec` 精确等于 receding-horizon controller 每次 replanning 前实际执行的动作数；BranchRecord 只在 feasible alternatives 已于该 prefix 内发生可测分歧时接纳。
3. **Fixed scale**：对按时间和动作维取均值的 flow residual 直接设 `β=1`，预注册且训练期间不调。

## Revised Proposal

# Research Proposal: Common-State Executed-Prefix Flow Preference (CEFP)

## Technical Gap

arXiv:2604.17896 已经用 counterfactual obstacle placement 和 active-violation signed-distance loss 训练 diffusion VLA；几何反事实与 action-time-local feasibility penalty 不是本工作创新。仍未被直接回答的是：从同一物理状态出发，当一个原 continuation 因功能几何失效、多个替代 continuation 仍可行时，能否直接移动连续动作 VLA 在**下一次真实会执行的 action prefix**上的条件分布，同时不把未执行 suffix 的身份泄漏进训练信号，也不破坏其他可行 continuation。

CEFP 把训练单位限定为同一完整 checkpoint 上的 competing executed prefixes。它不对分叉后的状态或技能阶段做逐时间对齐，也不依赖 candidate-specific suffix。

## Method Thesis

在 edited geometry 的最新可分支共同状态上，把每个 candidate action chunk 截成部署会执行的 `h_exec` 步，并将其余 tokens 替换为共同 frozen-reference padding；随后用 K-positive、冻结参考校正的 flow-residual preference 压低 invalid executed prefix，并用标准 replay/reference regularization 控制支持集漂移。

## Contribution Focus

- **唯一主贡献**：prefix-identifiable, common-state, geometry-flip-conditioned reference-adjusted flow preference。
- **测量而非贡献**：compiler-roster coverage、worst-mode success、outside-prefix output drift。
- **非贡献**：first violation、planner、mode clustering、reference regularization、WAM、几何 backbone。

## BranchRecord Compiler

### Geometry flip

从成功 base rollout 构造 RGB 可见且 render/collision mesh 一致的 compiler-minimal 编辑 `g+→g-`。同一原 action chunk 在 `g-` 中因预注册 clearance/contact/fit 事件失败，但 `g-` 仍可由 planner/controller 完成同一 terminal predicate。只称 compiler-minimal，不称连续几何最小。

### Latest branchable checkpoint

在 `g-` 中重放 invalid chunk 得到首次违规 `τ-`，然后从 `τ--1` 向前搜索 checkpoint。每次恢复完整 MuJoCo/SAPIEN state、controller cache、RNG state 和相机状态。选择满足以下条件的最新 `z_b`：

1. invalid continuation `a-` 在固定 H 内触发指定违规；
2. 至少 K 个 planner/controller continuations 在相同 H 内满足同一 terminal predicate；
3. 所有 candidates 使用相同动作表示、控制频率与初始 `z_b`；
4. K positives 经轨迹/接触事件聚类后仍代表不同 compiler-roster modes；
5. 每个 positive 与 negative 在前 `h_exec` 步的归一化动作距离超过预注册数值容差，确保替代决策确实发生在下一次执行窗口内。

失败的尝试保留 exclusion reason，并留在 attempted-pair denominator。

### Receding-horizon contract

`H` 是策略输出 chunk 长度；`h_exec` 是部署每次 query 后实际执行的前缀长度，并固定为基线原有值。LIBERO/openpi E0 使用 `h_exec=5`，随后立即重新观测和 query。训练与评估均保持该执行器不变。BranchRecord 不以可变 `D` 训练；局部支持恒为 `E={0,…,h_exec−1}`。

## Prefix-Identifiable Flow Inputs

冻结参考策略在同一条件 `c_b` 下、使用 pair-level 固定 seed 生成 padding chunk `p_ref∈R^(H×A)`；它只依赖 `c_b`，对该 BranchRecord 的所有 candidates 完全相同并 stop-gradient。

对 candidate `a` 构造：

`ã_s(a)=a_s` 若 `s<h_exec`；否则 `ã_s(a)=p_ref,s`。

positive/negative 使用同一个 flow time `t` 和同一个 base-noise tensor `ξ`。因此在 `s≥h_exec` 上，`ã`、flow-interpolated input 和 noise 都逐元素相同。即便 action expert 对 H 个 token 使用双向 attention，suffix 也不携带 candidate identity。loss 只读取前 `h_exec` 输出。

## Native π0.5 Flow Preference

对任一 `ã`：

- `x_t(ã)=(1−t)ξ+tã`；
- target velocity `u(ã)=ã−ξ`；
- executed-prefix residual：`e_θ(ã,c_b,E;t,ξ)=mean_{s∈E,j}[v_θ(x_t(ã),c_b,t)_{s,j}−u(ã)_{s,j}]²`。

冻结 reference 并 stop-gradient：

`g_θ(ã)=stopgrad(e_ref(ã,c_b,E;t,ξ))−e_θ(ã,c_b,E;t,ξ)`。

每个 roster positive 的 margin：`m_k=g_θ(ã_k+)−g_θ(ã−)`。

核心目标：`L_pref=(1/K)Σ_k softplus(−m_k)`。residual 已按 `h_exec×A` 取均值，固定 `β=1`、margin=0；二者预注册并不经实验调参。所有 K modes 等权，无独立 `L_mode`。

## Standard Preservation

`L_pres` 不主张新颖：在普通 replay chunks 上匹配冻结 reference 的 native flow output，并保留原 imitation flow loss。它不在 BranchRecord candidate-specific suffix 上构造额外规则，因为 suffix 已被共同 padding 消除。

总目标：`L=L_imit+λ_pref L_pref+λ_pres L_pres`。λ 只在 pair-held-out validation 上按预注册网格一次选择；先满足 unedited success 与 replay-output drift 约束，再最大化 invalid-vs-feasible separation。reference、padding 与 simulator/planner 全部 stop-gradient。

## Inference

部署只运行微调后 VLA。每次 query 输出 H 步、执行前 `h_exec=5` 步、重新观测再 query。输入仍为 RGB、proprioception 和语言；无 compiler、planner、reference、geometry oracle 或 WAM。

## Primary Claim

给定来自同一 latest-branchable physical state 的 alternatives，prefix-identifiable reference-adjusted flow preference over the actually executed receding-horizon prefix，相比 active-violation geometry shaping 与 whole-chunk preference，在相近 invalid-execution reduction 下造成更少的 replay/support drift，并更好保留 compiler-roster support。

## Minimal E0 Systems

1. ordinary imitation；
2. arXiv:2604.17896-style active-violation `L_geo`；
3. whole-chunk reference-adjusted preference；
4. CEFP without `L_pres`；
5. full CEFP。

保持同一 backbone、trainable subset、BranchRecords、optimizer steps、batch composition 和执行器。whole-chunk baseline 使用完整 candidate chunks；CEFP 只替换 prefix 与 common padding。

## Metrics and Kill Tests

- 主指标：edited success、invalid-reference execution、unedited success、replay-output drift、compiler-roster coverage、worst-mode success、margin-vs-simulator validity Spearman ρ。
- pair identity permutation 或 prefix identity permutation 保留 >50% CEFP 增益：停止。
- 把 common suffix padding 改回 candidate suffix 后若效果相同但 suffix-only probe 能预测 label：CEFP 的 prefix-local解释才被支持；否则停止 locality claim。
- `L_geo` 与 CEFP 在 edited success、coverage、worst-mode 均相差 <3pp：停止。
- 去掉 `L_pres` 不增加 drift，或 full CEFP 使 unedited success 下降 >2pp：停止。
- ρ<0.30：停止。

## Pre-GPU Feasibility Gate

先用 100–200 attempted episodes 检验总体 eligible branchable yield≥15%、每个约束族≥8%、render/collision 一致、checkpoint hash 可复现、`h_exec` 内确有分歧、固定 H/terminal contract 成立，且至少 25% eligible records 含 ≥2 个实质 roster modes。任一 gate 失败则不启动训练。

## Compute

一个 backbone、一个 action-head/LoRA 配置、2–3 constraint families；先 1-seed overfit/sanity，再只对仍有机制差异的 systems 做 3 seeds。估计 20–60 A100 GPU-hours；不启动完整 56 A100-GPU-days 方案。

