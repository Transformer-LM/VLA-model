# Round 4 Refinement

## Problem Anchor

- **Bottom-line problem**：当任务、语言指令和对象语义不变，但功能几何使原 action chunk 的局部响应变得物理不可行时，连续动作 VLA 应只改变真正失效的响应，同时保留未受影响行为与其他可行修正方式。
- **Must-solve bottleneck**：已有工作能够在碰撞或穿透发生的时间点施加几何损失，却难以判断模型是在学“改正不可行动作”，还是把邻近的多种可行解一起压掉。
- **Non-goals**：不声称首次使用几何反事实或局部几何损失；不做部署期 planner、WAM reranking 或安全保证；不声称保留所有未知可行模式。
- **Constraints**：无触觉；冻结或参数高效微调 π0.5 连续动作头；部署仍只输入 RGB、proprioception 和语言；仿真几何真值只用于训练数据编译和评测；GPU E0 前必须先过数据可编译性门。
- **Success condition**：在从同一完整物理 checkpoint 构造的 geometry-flip BranchRecords 上，相比 active-violation geometry loss 和 whole-chunk preference，方法在相近 invalid-execution reduction 下有更低 replay/support drift、更高 roster-mode coverage 和 worst-mode success；打乱正负对应或 executed-prefix 身份后增益消失。

## Anchor Check

- 问题、claim ceiling 和部署输入均未改变。
- 本轮仅修正 π0.5 原生 flow 参数化，并把共同 padding 从单一任意样本变成显式 Monte Carlo 期望。
- 不加入 phase network、WAM、critic 或测试时搜索。

## Changes Made

1. **原生 OpenPI 参数化**：严格采用本地 OpenPI `Pi0.compute_loss` 的时间分布、插值方向与 velocity target，不再使用等价但与预训练 API 不一致的替代记号。
2. **共享随机性**：同一个 BranchRecord、positive/negative/reference 的每次比较共享相同 `t`、完整 noise tensor `xi` 和共同 suffix padding。
3. **Padding-robust estimand**：每个 BranchRecord 预计算并保存两个 frozen-reference padding；训练每步均匀抽取其中一个，得到双-padding 有限期望的无偏随机估计，验证时显式平均两者。
4. **正确 locality kill test**：未见 padding seeds 只用于离线 flow-margin 稳定性与 simulator-validity correlation，不再虚构推理期不存在的“按 padding seed 闭环效果”。
5. **恢复数据硬门**：先用 200 次 attempt 估计 yield；只有总体与逐类 yield 达标，才继续收集到预注册的绝对独立记录数。达不到则不启动 GPU。
6. **显式计算倍率**：K=2 时一个 CEFP pair update 包含 3 个 trainable candidate example-forwards、3 个 frozen-reference candidate example-forwards，以及 1+1 个 replay/reference example-forwards；按 batch 拼接而不是串行调用。

## Revised Proposal

# Common-State Executed-Prefix Flow Preference (CEFP)

## Technical Gap

`Can Explicit Physical Feasibility Benefit VLA Learning?`（arXiv:2604.17896）已经构造参考轨迹附近的障碍物、从同起点同目标重规划，并只在 active violation 时间步施加几何损失。因此，“几何反事实 + 局部碰撞损失”不是本工作的创新。

尚未被直接回答的问题是：从同一完整物理状态出发，当原 continuation 因功能几何失效而多个替代 continuation 仍可行时，能否直接移动连续动作 VLA 在**下一次实际执行的短前缀**上的条件分布，同时避免两种混杂：

1. action head 从未执行的 candidate-specific suffix 偷看正负身份；
2. 单一几何 penalty 把所有邻近行为都推离，而不是在已知可行 alternatives 间保留支持。

CEFP 的训练单位不是两条按 raw time index 对齐的完整轨迹，而是同一 simulator checkpoint 上的 competing executed prefixes。

## Method Thesis

在 edited geometry 的最新可分支共同状态上，仅保留每个候选接下来真实会执行的 `h_exec` 个动作 token；其余 token 对所有候选使用相同的 frozen-reference padding。随后用 K-positive、reference-adjusted native-flow preference 降低 invalid prefix 的相对概率，并用标准 replay/reference regularization 控制未编辑分布漂移。

## Contribution Focus

- **唯一主贡献**：common-state、prefix-identifiable、geometry-flip-conditioned 的 reference-adjusted native-flow preference。
- **必要数据条件，不单列贡献**：可恢复 simulator checkpoint、多个已验证可行 continuation、可见 render/collision mesh 一致的几何编辑。
- **标准组件，不主张创新**：replay distillation、reference model、LoRA/action-head tuning、receding-horizon execution。

## BranchRecord Compiler

一个 BranchRecord 为

`B=(z_b,c_b,a^-,{a_k^+}_{k=1..K},y,metadata)`，

其中 `z_b` 是完整可恢复的 simulator/controller/RNG/camera checkpoint，`c_b` 是该状态的 RGB、proprioception 与语言条件，`a^-` 是不可行 continuation，`a_k^+` 是同一状态、同一动作表示和控制频率下的 K 个可行 continuation，`y` 是 simulator ground-truth validity/terminal predicate。

### Geometry flip

从成功 base rollout 构造 compiler-minimal、RGB 可见且 render mesh 与 collision mesh 一致的 `g+ -> g-` 编辑。原 continuation 在 `g-` 中因预注册的 clearance/contact/fit 事件失败，但 `g-` 仍能由同一 planner/controller 完成相同 terminal predicate。这里的 minimal 仅指编译器预注册的最小编辑，不声称连续几何意义上的全局最小反事实。

### Latest branchable checkpoint

在 `g-` 重放原 continuation 得到首次 violation `tau-`，从 `tau--1` 向前搜索并恢复完整状态。接受最新满足下列条件的 `z_b`：

1. `a^-` 在固定 horizon 内触发指定 violation；
2. 至少 K 个 alternatives 在相同 horizon 内满足相同 terminal predicate；
3. positives 经轨迹/接触事件聚类后仍覆盖至少两个 compiler-roster modes；
4. 每个 positive 与 negative 在前 `h_exec` 步的动作距离超过预注册数值容差；
5. 所有重放从 checkpoint hash、controller cache、RNG 和 camera state 可复现。

所有失败尝试保留 exclusion reason，并留在 attempted-pair denominator。

## Executed-Prefix Contract

`H` 为 π0.5 输出的 action horizon；`h_exec` 为部署每次 query 后实际执行、然后重新观测的步数。LIBERO/OpenPI E0 固定 `h_exec=5`。局部支持始终为 `E={0,...,h_exec-1}`，不从 negative violation mask 学习，也不把一条轨迹的 phase index 套到另一条轨迹。

对候选 `a` 和第 `r` 个共同参考 padding `p_ref^(r)`，构造

`a_tilde_s^(r)(a)=a_s` if `s<h_exec`, otherwise `p_ref,s^(r)`.

`p_ref^(r)` 由冻结 reference policy 在同一 `c_b` 下、用预注册 seed `r` 生成；在该 BranchRecord 的所有 positives、negative 和 reference evaluations 中逐元素相同且 stop-gradient。它不向网络标注候选身份。

## OpenPI-Native Flow Preference

严格沿用本地 OpenPI π0/π0.5 训练 API。对每个 padding replicate `r`，采样一次并在所有 candidates/reference 间共享：

`t ~ Beta(1.5,1) * 0.999 + 0.001`

`x_t(a_tilde)=t * xi + (1-t) * a_tilde`

`u_t(a_tilde)=xi-a_tilde`

其中 `xi` 是完整 `H x A` noise tensor。positive、negative 和 frozen-reference 在一次比较中共享同一 `t` 与同一 `xi`；共同 suffix 的 `a_tilde`、`x_t`、`u_t` 因而完全相同。action expert 即使在 H 个 action tokens 内使用双向 attention，也无法从 suffix 读取 candidate identity。

只在 executed prefix E 上计算原生 flow residual：

`e_theta(a_tilde;c_b,E,t,xi)=mean_{s in E,j} ||v_theta(x_t,c_b,t)_{s,j}-u_t(a_tilde)_{s,j}||^2`.

用冻结初始模型校正样本固有难度：

`g_theta(a_tilde)=stopgrad(e_ref(a_tilde))-e_theta(a_tilde)`.

第 k 个 positive、padding replicate r 的 margin 为：

`m_{k,r}=g_theta(a_tilde_k^{+,r})-g_theta(a_tilde^{-,r})`.

核心损失为两个预注册共同 padding 上的有限期望：

`L_pref=(1/(K*R)) sum_{k=1..K} sum_{r=1..R} softplus(-m_{k,r})`.

E0 固定 `R=2`，两个 seed 在实验前注册并由 BranchRecord id 确定，padding chunks 在训练前生成、hash 并写入 BranchRecord。训练时每个 optimizer step 从两个 replicates 中均匀抽取一个 `r`，对 `r` 的随机梯度是上述有限期望的无偏估计；pair-held-out validation 对两者显式平均。训练期间不选择最好 seed。`beta=1`、margin=0，均不通过 pilot 调参。E0 固定 `K=2` 个已验证可行 modes 并等权，不设独立 mode loss。

## Standard Preservation

`L_pres` 在普通 replay chunks 上蒸馏冻结 reference 的 native flow output，并保留原 imitation flow loss。总目标：

`L=L_imit+lambda_pref*L_pref+lambda_pres*L_pres`.

两个 lambda 只在 pair-held-out validation 上按预注册小网格选一次：先满足 unedited success 与 replay-output-drift guardrail，再比较 invalid-vs-feasible separation。simulator、compiler、planner、reference 和 padding 全部 stop-gradient。

## Inference

部署只运行微调后 π0.5：输入 RGB、proprioception 和语言，输出 H 步，执行前 5 步，重新观测并再次 query。无 geometry oracle、BranchRecord compiler、planner、WAM、reference ensemble 或候选 reranking。

## Primary Claim

给定从同一 latest-branchable physical state 编译出的 geometry-flip alternatives，CEFP 相比 active-violation geometry shaping 和 whole-chunk preference，在相近 invalid-reference reduction 下造成更小 replay/support drift，并更好保留 compiler-roster 中已验证的多种可行 continuation。claim 仅覆盖编译器可生成的局部功能几何翻转，不外推到一般安全或所有未枚举可行模式。

## Minimal E0 Systems

1. ordinary imitation/reference model；
2. arXiv:2604.17896-style active-violation `L_geo`；
3. whole-chunk reference-adjusted preference；
4. CEFP without `L_pres`；
5. full CEFP。

所有系统共享 backbone、trainable subset、BranchRecords、optimizer steps、batch composition 和 receding-horizon executor。只有 objective/support construction 改变。

## Metrics and Falsification

- 主指标：edited success、invalid-reference execution rate、unedited success、replay-output drift、compiler-roster coverage、worst-mode success、margin-vs-simulator-validity Spearman rho。
- **Correspondence kill**：打乱 pair identity 或 executed-prefix identity 后仍保留超过一半 CEFP 增益，停止因果解释。
- **Padding invariance kill**：在训练未使用的三个固定 reference-padding seeds 上，只离线重算 paired margins、margin sign/rank agreement 和 margin-vs-simulator-validity correlation。若 margin 的主要符号/排序或 validity correlation 方向依赖某个 seed，则停止 prefix-local claim；不把 padding seed 与单个 padding-free deployed model 的闭环结果相联系，也不挑选最好 seed。
- **Support kill**：`L_geo` 与 CEFP 在 edited success、coverage 和 worst-mode success 均相差小于 3 percentage points，停止新增方法 claim。
- **Preservation kill**：移除 `L_pres` 不增加 drift，或 full CEFP 使 unedited success 下降超过 2 percentage points，停止 preservation claim。
- **Validity kill**：held-out `rho<0.30`，停止把 flow margin 解释为 simulator validity proxy。

## Pre-GPU Feasibility Gate

采用两阶段、不可事后放宽的数据门：

1. **Yield pilot**：每个候选 constraint family 先做 100 次、总计 200 次 attempted base episodes。总体 eligible branchable yield 必须 `>=15%`，每个保留 family 的 yield 必须 `>=8%`；完整 attempted-pair ledger 保留失败原因。
2. **Absolute floor**：pilot 通过后继续同一编译协议，最多累计 800 次 attempts；GPU 启动前必须获得至少 **120 个独立 BranchRecords**，按 base episode/checkpoint lineage 去重，不能用相邻 checkpoint、重复 planner seed 或同一轨迹扰动凑数。至少保留两个 constraint families、每个 family 至少 30 个独立 records，并且至少 30 个 records 含两个实质 roster modes。
3. **Fixed split**：按 base-episode lineage 分为 72 train / 24 validation / 24 test；test 中每个 retained family 至少 10 个 records。padding seeds、planner seeds、相邻 checkpoint 不得跨 split。
4. 所有 records 仍必须满足 render/collision mesh 一致、checkpoint hash 可复现、候选在 `h_exec=5` 内分歧、固定 horizon/terminal contract 成立。任一绝对或相对门失败，不启动训练。

## Compute

先做单卡、单 seed overfit/sanity；只有 compiler gate、native-flow implementation tests、padding invariance dry-run 和机制指标都通过，才对仍有差异的系统做三种子。

K 固定为 2，训练每步只抽取一个 padding replicate。一个 CEFP BranchRecord update 的显式上界是：3 个候选（2 positive + 1 negative）乘 trainable/reference 两套 flow evaluation，共 6 candidate example-forwards；再加 1 个 replay example 的 trainable/reference evaluation，共 **8 example-forwards**。三类 candidate 在 batch 维拼接；frozen reference 通过同一基础 checkpoint 关闭 trainable adapter 计算，不复制第二套大模型。两个 padding chunks 可预计算，但由于 `t,xi` 每步重采样，reference residual 不伪称可缓存。

在任何长训练前，记录 ordinary-imitation 与 CEFP 的单步 wall time、峰值显存和每 100 steps 吞吐；总 GPU-hour 预算由该实测值推导并写入 tracker。20--40 A100 GPU-hours 仅为先验估计，若实测 8-example-forward batching 使完整 E0 超过 80 A100 GPU-hours，则先只完成单 seed mechanism E0，不自动扩展三种子或四卡长跑。
