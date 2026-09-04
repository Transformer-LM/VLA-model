# Round 1 Refinement

## Problem Anchor

- **Bottom-line problem：** 判断 action-conditioned predictive world objective 是否会把一个 VLA 的共享动作接口表征塑造成对闭环控制真正有用的 future-sensitive representation，而不只是改善一个 auxiliary latent loss。
- **Must-solve bottleneck：** 既有 future-objective 工作通常把“有效未来对应关系”“任意辅助梯度带来的正则化”“action-output diversity/seed lottery”和“表征被策略实际使用”混在一起；单看 world loss、probe 或平均成功率不能回答 H1。
- **Non-goals：** 不提出新的 future objective、adapter、WAM 或 VLA；不重塑 frozen Qwen/VLM backbone；不做 planning、MBRL、视频生成、SOTA、真机或跨架构泛化；不声称 natural causal mediation、物理因果或排除了所有辅助正则化。
- **Constraints：** frozen Qwen3-VL-4B 与 frozen deterministic MLPResNet action head；个人离线 LIBERO 数据、DINOv2 和 StarVLA checkpoint；所有远程产物仅在 '<PERSONAL_RESEARCH_ROOT>'；物理 GPU 2/3 优先，0/1 仅在四卡均空闲时使用；总计不超过 8 GPUh，完整路径投影不超过 7.2 GPUh；不得接触团队/共享目录或脏 CF-DynAlign 树。
- **Success condition：** 一个严格 held-out 的 action-conditioned future target 先通过 model gate；随后有效 future gradient 相对 stop-gradient 和 matched deranged-future placebo 产生跨训练 seed 一致、至少 10pp 的 paired closed-loop gain；若继续做机制层，cross-fitted predictive-component removal 必须比 action-output-matched orthogonal placebo 更明显地消除该 gain。

## Anchor Check

- **原始瓶颈：** H1 不是“再做一个 future head”，而是区分有效 future correspondence、普通辅助梯度、seed/output effects 和被策略实际使用的表征。
- **保持方式：** 仍只改变一个 shared action-interface adapter；增加的 residualization、gradient controller 和 empirical-support placebo 都是识别约束，不是平行贡献。
- **拒绝的漂移：** 不加入 simulator action forks 来声称 state-dependent causal dynamics；在普通 demonstration 的单状态单动作支持下，主张降为 **behavior-policy 下的 correspondence-specific future association**。不加入 RL、Diffusion、planner、视频 decoder 或更多 benchmark。

## Simplicity Check

- **唯一贡献：** 一个预注册、顺序门控的 future-gradient algorithmic identification contract。
- **降级为工程细节：** cache、hot switch、DINO target、adapter、projector、sign test 均不再列作 supporting contribution。
- **删除的自由度：** head 训练、数据拆分、gradient dose、checkpoint screen、seed count、P/Q 构造和 claim wording 全部由固定规则与 hash 冻结。
- **仍为最小路线：** 两个可训练件不变：adapter，以及只在预训练阶段训练的 future head。

## Changes Made

### 1. 去除当前帧捷径并隔离三套数据

- 把 raw DINO difference 改为 current-state nuisance-residualized target。
- episode 严格拆为 'D_head / D_adapter / D_post'；各自用途互斥。
- 双相机 target 使用 32+32 block projection，main-camera block 必须单独过门。
- 承认 demonstration 只能支持 predictive association，不能支持 state-dependent causal dynamics。

### 2. 把 gradient treatment 写成可执行算法

- 采用 FP32 'autograd.grad(create_graph=False)' 与 detached scale。
- A/C 的 auxiliary norm 都对齐同一个 B action-gradient reference，而不是彼此动态依赖。
- adapter 阶段改为无动量 plain SGD，避免 arm-specific Adam moments。
- C 额外匹配 target norm、初始 frozen-head loss 与 Huber saturation。

### 3. 修复 Stage 2 几何

- 同时 residualize treatment delta 与 target。
- 只在 empirical delta span 内做 PCA/whitening 与 RRR。
- 使用 token-shared operator，不在 20,480 维 ambient space 学 free projector。
- Q 来自同一 empirical span，并匹配 latent energy、per-task/per-token action-output sensitivity；无合格 Q 就停止。
- 在任何 Stage-1 outcome 打开前构建并 hash P/Q。

### 4. 固化 checkpoint、统计与预算规则

- 写入 1k/5k/10k 的 exact path/size/SHA256。
- 两个 task 必须分别落入 20–80%，不再只看 pooled rate。
- ties 直接作为失败处理。
- 完整预算按 30 screen + 300 Stage 1 + 200 conditional Stage 2 + 所有 cache/train/load/retry 计 physical-GPU hours，并保留 ≥10% reserve。

## Revised Proposal

# 研究方案：PGR-Audit——预测梯度在 VLA 动作接口中的顺序识别

## Method Thesis

对于一个 treatment-blind-selected StarVLA checkpoint，只有当同一个 frozen future decoder 的 **正确配对梯度算法** 同时胜过 stop-gradient 和一个 task/progress/action-norm-stratified、auxiliary-gradient-norm-matched 的错配算法，并且预先冻结的 treatment-associated predictive subspace intervention 通过 placebo-relative gate，才允许说该 future objective 在这两个任务上塑造了被策略依赖的 action-interface component。

这不是物理 dynamics、natural mediation 或通用 VLA 规律。

## One Contribution

**一个预注册 sequential identification contract：**

1. held-out future-latent predictive-validity；
2. paired algorithmic treatment A/B/C；
3. conditional, empirical-support-matched representation reliance test。

所有架构与实现部件仅为执行该 contract 服务。

## Frozen Host and Interface

- StarVLA clean HEAD: '3422b9f2387b6f682cf02802904a77b23ab13afd'。
- Frozen Qwen3-VL-4B；frozen deterministic MLPResNet 7D action head。
- Frozen input hidden shape '[B,8,2560]'。
- Adapter:

\[
m_\phi(h)=h+U_\phi V_\phi\operatorname{LN}(h),\qquad r=32.
\]

同一 adapter 共享八个 token；'V' Kaiming init，'U=0'，LN 无 affine parameter。identity parity 必须在 normalized action 上达到 max absolute error < \(10^{-6}\)。

## Immutable Data Partition

对每个 task，按 'SHA256(task_id | episode_id | split_seed=1701)' 排序后做分层比例拆分：

- 'D_head': 50% episodes；
- 'D_adapter': 30%；
- 'D_post': 20%。

每部分至少含三个 episode；否则 data gate 失败。任何 't+8' 跨 episode 的样本直接删除，禁止末帧 clip padding。

'D_head' 再按同一 hash 的第二字节拆为 70% head-train、15% head-val、15% strict-test。'D_post' 固定为五个 episode-group folds：0–2 mechanism-fit，3 rank-validation，4 placebo-calibration/final offline test。所有 manifest 在第一次打开 strict-test 前写入并 hash；之后不可改变。

## Blocked Future Target

对 main/wrist camera 分别取 deterministic DINOv2 ViT-S/14 CLS：

\[
d_t^c=E_c(o_{t+8})-E_c(o_t),\qquad c\in\{main,wrist\}.
\]

每个 camera 的 whitening 只在 head-train episodes 拟合；每个 block 使用 seed 1701 的 fixed orthonormal Gaussian projection 'R_c: 384→32'。拼接得到 64-D raw target 'y_t'。

为去除 negative-current-embedding shortcut，在线性 ridge nuisance model 中使用：

\[
z_t=[E_{main}(o_t),E_{wrist}(o_t),onehot(task),progress],
\qquad
r_t=y_t-b(z_t).
\]

'b' 在 head-train episodes 上做五折 episode cross-fitting以生成训练 residual，再在全部 head-train 上 refit；ridge grid 为 \(\{10^{-4},10^{-3},10^{-2},10^{-1},1,10\}\)，head-val 最低 nMSE、tie 取较大 regularization。固定后的 'b' 用于 head-val、strict-test、D_adapter 与 D_post。

该 target 只表示 behavior-policy support 下、超过当前视觉/任务进度可解释部分的 future-latent association。

## Frozen Future Decoder

输入：

- mean-pooled parameter-free-LN action tokens，Linear(2560,256)+GELU；
- demonstrated normalized 56-D action chunk，Linear(56,128)+GELU；
- concatenate → Linear(384,256)+GELU → Linear(256,64)；
- 无 dropout。

Head seed 1701；AdamW lr \(3\times10^{-4}\)，weight decay \(10^{-4}\)，batch 256，最多 100 epochs；head-val nMSE early stopping patience 10、min delta \(10^{-4}\)；选择最小 val nMSE，tie 取更早 epoch。训练完成后把 decoder、nuisance、whitening、R、optimizer config、split manifest 与 preprocessing manifest 全部 hash，decoder 切到 eval 并永久冻结。

Controls 独立训练、相同 schedule 与输出维度：

- full interaction 'q(m,a)'；
- state-only 'q(m,0)'；
- action-only 'q(0,a)'；
- current-DINO-plus-action 'q(E_t,a)'；
- additive 'q_s(m)+q_a(a)'；
- nuisance-only / task-progress mean / zero。

Strict-test 只打开一次。Full 必须在 joint 64-D 和 main 32-D 上都满足：

- 相对最强 control 至少 5% nMSE improvement；
- episode bootstrap one-sided 95% lower bound > 0；
- task×progress-stratified action derangement 使 nMSE 至少恶化 5%，lower bound > 0；
- cross-episode representation derangement使 nMSE 至少恶化 5%，lower bound > 0。

任一失败即 NO-RUN；不把结果称为 state-dependent action dynamics。

## C Derangement

在 D_adapter 内，donor 必须：

- 来自不同 episode；
- future window 不重叠；
- 在 task × episode-progress decile × action-norm tercile 内；
- 无 fixed point。

每个 stratum 用 fixed minimum-cost derangement，cost 只含 standardized target norm 与 identity-head Huber loss distance。若 stratum 不可行，按预先固定顺序先合并相邻 action-norm bin，再合并相邻 progress bin；所有 merge 与 donor map 持久化。

在训练开始前，C 与 A 必须满足：

- dataset target-norm ratio ∈ [0.9,1.1]；
- identity-head loss ratio ∈ [0.9,1.1]；
- Huber saturated-coordinate rate 差 ≤ 5 percentage points。

否则 C placebo invalid。

## Exact A/B/C Gradient Controller

每个 seed 内 A/B/C 从相同 identity adapter、batch order 与 plain SGD state 开始。Adapter optimizer：SGD lr \(10^{-3}\)，momentum 0，weight decay 0，500 steps，batch 256；total-gradient global clip 1.0。

每步用 FP32、'create_graph=False' 计算 U/V 上的手工梯度：

\[
g^{act}_j=\nabla_{\phi_j}L_{action},\quad
g^{fut}_A=\nabla_{\phi_A}L_{future}(q(m_A,a),r),\quad
g^{fut}_C=\nabla_{\phi_C}L_{future}(q(m_C,a),\pi(r)).
\]

共同 dose：

\[
\rho=0.30\lVert g^{act}_B\rVert_2,\qquad
s_j=\operatorname{clip}\left(
\frac{\rho}{\lVert g^{fut}_j\rVert_2+10^{-12}},
10^{-3},10^{3}\right),\quad j\in\{A,C\}.
\]

所有 norm/scale detached。更新前：

\[
g_A=g^{act}_A+s_A g^{fut}_A,\quad
g_B=g^{act}_B,\quad
g_C=g^{act}_C+s_C g^{fut}_C.
\]

B 在 detached shadow 'm_B' 上执行同样 future VJP 并丢弃，保持 compute path；它不获得 auxiliary update。A/C auxiliary pre-clip norm 对 \(\rho\) 的相对误差必须 ≤1%。任何 nonfinite 立即停；scale-cap/zero-gradient fallback 不得超过 1% batches；至少 99% valid batches 满足 dose gate。报告 action/aux cosine、raw/scaled norm、total norm、clip rate、update norm、loss、adapter residual RMS。

C 的数据和 scalar dose 被匹配，但方向、协方差、曲率与 action-gradient interaction 未被匹配；claim 只相对这一个 fixed placebo。

## Untouched Post-Training Predictive Gate

在 D_post 第 4 fold、且任何 environment treatment outcome 打开前，使用 frozen q 与正确 r：

- A 的 joint 与 main-block nMSE 必须分别比 identity、B、C 至少低 5%；
- episode-bootstrap one-sided lower bound >0；
- A adapter residual RMS 不超过 frozen h RMS 的 10%；
- cache/direct and hot-switch action parity < \(10^{-6}\)。

失败即不运行 Stage 1，因为 treatment 未在独立数据上形成可验证的 predictive change。

## Treatment-Blind Checkpoint Screen

Preregistered checkpoints:

1. '<PERSONAL_RESEARCH_ROOT>/checkpoints/cf-dynalign/cf_dynalign_baseline_libero_all_20260727_185501/checkpoints/steps_1000_pytorch_model.pt'  
   size 9,785,060,316 B; SHA256 '6e2f52758054f0da6d76640dfcfc3dd324b0a14f2cf24d4626262781fd1d4735'
2. same directory 'steps_5000_pytorch_model.pt'  
   size 9,785,060,316 B; SHA256 '4b0067d806a321065d1521f4940d34920de234902ae4fe83a2a642ab984b277a'
3. same directory 'steps_10000_pytorch_model.pt'  
   size 9,785,061,050 B; SHA256 '1687afbdcab4f4593c6261d64ac478fd151a0ebd7b641236b60ce1a01fbdee7b'

Tasks are fixed:

- LIBERO-10 ID 3: 'put the black bowl in the bottom drawer of the cabinet and close it'；
- LIBERO-10 ID 6: 'put the white mug on the plate and put the chocolate pudding to the right of the plate'。

Screen initial-state indices 0..4；env/NumPy seed 7；10 dummy settle steps；max policy horizon 520 steps after settle；open-loop chunk 8；success only when env done=True；horizon exhaustion is failure。Infrastructure exception is logged and retried once only if it occurs before the first policy action；a second exception or any exception after action starts makes the screen incomplete and fails the gate，不得当作普通 failure 隐藏。

三 checkpoint × 两 task × 五 state = 30 rollouts。每个 task 的 SR 都必须独立位于 [0.2,0.8]。在合格 checkpoint 中选 pooled SR 最接近 0.5者，tie 取更早 step。没有合格 checkpoint 则 stop。Final evaluation states：10-seed design 用 5..9；5-seed fallback 用 5..14。

Final claim 使用 “treatment-blind-selected checkpoint from a preregistered set”。

## Immutable GPU-Hour Ledger and Seed Rule

每次 GPU launch 前读取 physical 0–3 的 memory/util/process。默认只用 2/3；0/1 只有在四卡当时都空闲时可用。GPUh = 每张 occupied physical GPU 的 wall time 求和。

在打开任何 A/B/C environment outcome 前，先实测：

- 完整 cache；
- head/nuisance/control training；
- 一个完整 500-step lockstep triplet；
- 30 baseline-screen rollouts，包括 model loads；
- Stage-2 offline builder sample；
- 所有已发生 failure/retry。

设 'u_roll' 为 30 screen rollouts 中每个 task 的 mean GPU-seconds/rollout 的较大值，再乘 1.25 failure-length factor；'u_triplet' 为完整 triplet 实测 GPUh 的 1.10 倍；其他组件各用实测 ×1.10。Full projection：

\[
H_{10}=H_{spent}+9u_{triplet}+300u_{roll}+200u_{roll}
       +H_{P/Q}+H_{loads/retries}+H_{reserve},
\]

其中已测的一个 triplet 在 'H_spent'，'H_reserve=max(0.10×pre-reserve total,0.3 GPUh)'。五 seed 公式把 remaining triplets 改为 4，rollout 总数仍为 500。30 screen 已包含于 H_spent；两条 A→B parity traces 与所有 GPU-side analysis 必须进入 loads/retries 或 reserve。

- 若 \(H_{10}\le7.2\)，冻结 seeds 0..9；
- 否则若 \(H_5\le7.2\)，冻结 seeds 0..4，并把所有结论标为 exploratory/provisional；
- 否则 stop。

Decision JSON 在训练剩余 seeds 或打开任何 treatment rollout 前写入并 hash。实际累计绝不超过 8 GPUh。并行不减少 GPUh。

## Stage 1: Controlled Algorithmic Effect

Preferred: 10 seeds × 2 tasks × 3 arms × 5 shared states = 300 rollouts。每个 seed 先等权聚合两 task。

两个 one-sided intersection-union contrasts 都必须：

- 在全部 10 seeds 中至少 9 个严格 positive；tie 计 non-positive；
- exact sign \(p=P[Binom(10,0.5)\ge9]=0.0107\)；
- pooled gain ≥10pp；
- 两个 task 的 mean contrast 都 ≥0；
- C 不得比 B 低超过 5pp，且 C audit pass。

五 seed fallback 要求 5/5 strict positive、\(p=0.03125\)，其他 gate 相同。Rollout 不是 training replicate。Action diversity/effective rank/cosine 只作为 competing diagnostic 报告，不事后替换主 contrast。

Stage 1 失败后禁止 Stage 2。

## Pre-Outcome Stage-2 Builder

虽然 environment Stage 2 只有在 Stage 1 pass 后执行，但每个 seed 的 P/Q 必须在 Stage-1 outcomes 打开前构建、freeze、hash。

在 D_post：

\[
\bar\delta=\frac1{8}\sum_{k=1}^{8}(m_A^k-m_B^k).
\]

用 frozen nuisance covariates 'z=[current DINO, action chunk, task, progress]' 在 mechanism-fit folds 上 cross-fit linear ridge，残差化 \(\bar\delta\) 与 r：

\[
\tilde\delta=\bar\delta-\widehat E[\bar\delta\mid z],\qquad
\tilde r=r-\widehat E[r\mid z].
\]

只用 \(\tilde\delta\) 拟合 PCA/whitening；保留 95% variance、最多 128 dims。再做 ridge RRR，ridge grid \(\{10^{-4},10^{-3},10^{-2},10^{-1},1\}\)，rank grid \(\{4,8,16,32\}\)，rank-validation fold 选 OOF nMSE 最低，tie 取更低 rank/更高 ridge。

必须满足 held-out incremental \(R^2\ge0.02\)，且 1,000 次 episode-block target permutation 的 one-sided \(p<0.05\)。否则该 seed 无 predictive operator，Stage 2 不得运行。Ten-seed/five-seed路径分别要求全部 10/5 seed artifact pass。

由于 decoder mean-pool tokens，使用 structured lift：

\[
P=P_{token}\otimes T_{feat},\qquad
P_{token}=\mathbf1\mathbf1^\top/8.
\]

Whitening/unwhitening 与 centering 都是 artifact 一部分；不学习 free 20,480-D projector。

生成 100 个 fixed-seed Q candidates，均在同一 whitened empirical delta span、与 T_feat covariance-orthogonal、同 rank、同 token structure。只在 placebo-calibration fold 选择：

- removed latent energy ratio to P ∈ [0.9,1.1]；
- 每 task、每 token 的 frozen-action-output perturbation norm ratio ∈ [0.9,1.1]；
- held-out target incremental \(R^2\le0.005\)，且 permutation \(p\ge0.10\)。

无 candidate pass 则 Stage 2 stop。P/Q 选择完全不使用 LIBERO success。

Positive control：exact pre-head 'm_A-\delta=m_B' 的 cached normalized-action max error < \(10^{-6}\)，并在两个 reserved deterministic traces 上逐 chunk action parity < \(10^{-6}\)。Interpolation α∈{0,0.5,1} 必须使 empirical PCA Mahalanobis distance 不超过 D_post 99th percentile 且 normalized action 留在 training range；否则 intervention invalid。

## Stage 2: Placebo-Relative Reliance

Interventions:

\[
m_{A,-pred}=m_A-\operatorname{unwhiten}(P\,\tilde\delta),\qquad
m_{A,-orth}=m_A-\operatorname{unwhiten}(Q\,\tilde\delta).
\]

Preferred: 10 seeds × 2 tasks × 2 interventions × 5 shared states = 200 rollouts。Primary contrast 'SR(A_orth)-SR(A_pred)'：

- 至少 9/10 strict positive，ties fail；
- mean ≥10pp；
- 每 task mean ≥0；
- A_orth 相对 intact A 的 harm ≤5pp；
- A_pred 至少 erase 50% of A−B gap；
- A_pred 不得低于 B 超过 10pp。

Five-seed fallback 要求 5/5 positive，仍仅 exploratory。Clustered intervals descriptive。

通过只支持：

> controlled, placebo-relative reliance on a preregistered linear treatment-associated predictive subspace.

## Artifact Order

严格顺序：

1. source/data/checkpoint hashes；
2. D_head/D_adapter/D_post manifests；
3. target/nuisance/head/control artifacts；
4. strict predictive-validity report；
5. derangement map 与 C matching report；
6. adapter/cache parity 与一个 lockstep triplet timing；
7. checkpoint screen；
8. seed-count/budget decision；
9. remaining A/B/C training；
10. untouched D_post predictive gate；
11. P/Q/positive-control artifacts；
12. **freeze and hash all Stage-2 choices**；
13. Stage-1 rollouts and gate；
14. only if pass, Stage-2 rollouts。

任一顺序被打破即停止正向 claim。

## Claim Ceiling

若 Stage 1 与 Stage 2 全部通过，最强表述为：

> 对一个从预注册集合中 treatment-blind 选择的 StarVLA checkpoint、两个预注册 LIBERO tasks、一个 frozen future decoder 和指定 low-rank action interface，valid-target gradient algorithm 相对 stop-gradient 与一个 stratified、auxiliary-gradient-norm-matched deranged-target algorithm 产生了 training-seed-consistent closed-loop gain；在另行冻结、cross-fitted、empirical-support/action-output-matched 的干预下，移除 DINO-future-associated treatment-delta component 比移除一个正交成分更伤害性能，提供 task-local、placebo-relative reliance evidence。

不得写 causal mediation、state-dependent causal dynamics、physical causality、Qwen reshaping、新 objective/adapter/WAM、排除所有 generic regularization、LIBERO/VLA generality、SOTA 或 real-robot conclusion。

## Failure Interpretation

- predictive-validity fail：chosen target/head 未证明超越当前状态/任务/动作捷径；
- D_post gate fail：未来梯度未在新 episode 中形成可验证 predictive change；
- Stage 1 fail：未观察到一个大且跨 seed 一致的 local algorithmic effect；不排除 5–10pp 小效应；
- P/Q gate fail：不能构造可信 mechanism intervention；
- Stage 2 fail：即使 Stage 1 有 total effect，也没有 proposed subspace reliance evidence；
- budget fail：evidence-gated NO-RUN，不删除 controls 硬塞预算。

