# Round 3 Refinement

## Problem Anchor

- **Bottom-line problem：** 判断 action-conditioned predictive world objective 是否会把一个 VLA 的共享动作接口表征塑造成对闭环控制真正有用的 future-sensitive representation，而不只是改善一个 auxiliary latent loss。
- **Must-solve bottleneck：** 既有 future-objective 工作通常把“有效未来对应关系”“任意辅助梯度带来的正则化”“action-output diversity/seed lottery”和“表征被策略实际使用”混在一起；单看 world loss、probe 或平均成功率不能回答 H1。
- **Non-goals：** 不提出新的 future objective、adapter、WAM 或 VLA；不重塑 frozen Qwen/VLM backbone；不做 planning、MBRL、视频生成、SOTA、真机或跨架构泛化；不声称 natural causal mediation、物理因果或排除了所有辅助正则化。
- **Constraints：** frozen Qwen3-VL-4B 与 frozen deterministic MLPResNet action head；个人离线 LIBERO 数据、DINOv2 和 StarVLA checkpoint；所有远程产物仅在 '<PERSONAL_RESEARCH_ROOT>'；物理 GPU 2/3 优先，0/1 仅在四卡均空闲时使用；总计不超过 8 GPUh，完整路径投影不超过 7.2 GPUh；不得接触团队/共享目录或脏 CF-DynAlign 树。
- **Success condition：** 一个严格 held-out 的 action-conditioned future target 先通过 model gate；随后有效 future gradient 相对 stop-gradient 和 matched deranged-future placebo 产生跨训练 seed 一致、至少 10pp 的 paired closed-loop gain；若继续做机制层，cross-fitted predictive-component removal 必须比 action-output-matched orthogonal placebo 更明显地消除该 gain。

## Anchor and Simplicity Check

Anchor preserved；无 action-fork、online teacher、RL、planning、Diffusion 或 benchmark expansion。唯一贡献是 preregistered sequential identification contract。Round 3 只把 projector、equivalence、seed eligibility 和 budget edge case 写成机器可检查规则。

## Changes Made

1. 用 orthonormal basis B 显式定义 square projector \(\Pi=BB^\top\)；W+ 仅为 linear PCA/scale pseudoinverse。
2. 加入 nuisance-annihilation tolerance：predictive 与 Q basis 在 whitened nuisance subspace 上的 overlap ≤\(10^{-3}\)。
3. Q 的 final gate 从 nonsignificant p-value 改为 episode-bootstrap upper confidence bound ≤0.005。
4. fold-4 artifact table 对每个 seed 分开给出 Stage-1 与 Stage-2 eligibility；不删 seed、不补 seed。
5. rollout upper formula 始终把 wrapper overhead 加到 longest/full-horizon base time。

## Revised Proposal

# PGR-Audit：Frozen VLA Action Interface 的预测梯度顺序识别

## A. Claim Ladder

- **Model claim：** one frozen decoder predicts nuisance-residualized DINO future association on untouched episodes。
- **Stage-1 claim：** valid-target gradient algorithm beats stop-gradient and one fixed stratified scalar-dose-matched deranged-target algorithm。
- **Stage-2 claim：** policy locally relies more on one preregistered treatment-associated predictive linear component than on an empirical-support/action-output-matched orthogonal component。

No causal action dynamics、mediation、physical causality、backbone shaping、new WAM/objective/adapter、SOTA 或 generality。

## B. Host and Adapter

- clean StarVLA HEAD '3422b9f2387b6f682cf02802904a77b23ab13afd'；
- frozen Qwen3-VL-4B and frozen deterministic MLPResNet 8×7 action head；
- h shape '[B,8,2560]'；
- local offline DINOv2 ViT-S/14；
- adapter \(m_\phi(h)=h+U_\phi V_\phi LN(h)\)，rank 32，V Kaiming，U=0，shared across tokens。

Identity/cache/hot-switch normalized-action max error <\(10^{-6}\)。Only future head and adapter are ever trainable，in disjoint stages。

## C. Immutable Episode Data

Per task, SHA256(task_id|episode_id|1701) stratification:

- D_head 50%；
- D_adapter 30%；
- D_post 20%。

Every partition and **every D_post fold** must include at least one episode from each task；D_head/D_adapter/D_post each require ≥3 episodes/task。t+8 crossing terminal is removed；no clip padding。

D_head: 70/15/15 train/val/strict-test。  
D_post:

- folds 0–1 mechanism/nuisance fit；
- fold 2 ridge/rank validation；
- fold 3 Q calibration/matching；
- fold 4 locked final offline gate。

All manifests are hashed before strict-test。Fold 4 stays unopened until every selected seed has frozen A/B/C/P/Q artifacts。

## D. Target, Head and Strict Predictive Gate

For main and wrist:

\[
d_t^c=E_c(o_{t+8})-E_c(o_t).
\]

Whitening fits only D_head-train。Fixed seed-1701 orthonormal Gaussian \(R_c:384\to32\) gives blockwise 64-D y。Current nuisance:

\[
z=[E_{main}(o_t),E_{wrist}(o_t),onehot(task),progress],\quad
r=y-b(z).
\]

Linear ridge b uses fivefold episode cross-fitting on D_head-train，then refits；grid \(10^{-4}\ldots10\)，val nMSE lowest，tie stronger regularization。

Frozen decoder: mean-LN m→256；56-D action→128；concatenate 384→256→64 GELU MLP，no dropout。Seed1701，AdamW lr \(3e{-4}\)，wd \(1e{-4}\)，batch256，max100 epochs，patience10，best val nMSE，tie earliest。All artifacts/hash freeze before strict-test。

Controls: state-only，action-only，current-DINO+action，additive state+action，nuisance/task-progress/zero。On D_head strict-test，full must on joint64 and main32:

- ≥5% nMSE gain over strongest control and episode-bootstrap one-sided LCB>0；
- action derangement and representation derangement each worsen nMSE ≥5% with LCB>0。

Failure=NO-RUN；claim remains behavior-policy association。

## E. Fixed C and A/B/C Training

C donors: different episode，nonoverlapping future window，same task×progress-decile×action-norm-tercile，no fixed point。Minimum-cost derangement uses only target norm and identity-head Huber-loss distance；fixed sparse-bin merge order。Pretrain match：target-norm/loss ratios [0.9,1.1]，Huber saturation difference ≤5pp。Hash donor map before training。

Per seed，A/B/C share identity init、batches、500 steps、batch256。Plain SGD lr \(10^{-3}\)，momentum/wd0，global clip1.0。

\[
g_j^{act}=\nabla L_{action},\quad
g_A^{fut}=\nabla L_{future}(q(m_A,a),r),\quad
g_C^{fut}=\nabla L_{future}(q(m_C,a),\pi(r)).
\]

FP32，create_graph=False，scales detached：

\[
\rho=.30\lVert g_B^{act}\rVert,\quad
s_j=clip(\rho/(\lVert g_j^{fut}\rVert+10^{-12}),10^{-3},10^3).
\]

Updates: \(g_A=g_A^{act}+s_Ag_A^{fut}\)，\(g_B=g_B^{act}\)，\(g_C=g_C^{act}+s_Cg_C^{fut}\)。B performs the same frozen future forward/loss log，no shadow VJP。A/C auxiliary-dose error ≤1%；nonfinite stop；cap/zero fallback ≤1%；≥99% batches pass。Log all loss/norm/cosine/clip/update/residual diagnostics。

## F. Treatment-Blind Screen

Exact candidates:

1. steps1000 path '<PERSONAL_RESEARCH_ROOT>/checkpoints/cf-dynalign/cf_dynalign_baseline_libero_all_20260727_185501/checkpoints/steps_1000_pytorch_model.pt'；9,785,060,316 B；SHA256 '6e2f52758054f0da6d76640dfcfc3dd324b0a14f2cf24d4626262781fd1d4735'
2. steps5000 path '<PERSONAL_RESEARCH_ROOT>/checkpoints/cf-dynalign/cf_dynalign_baseline_libero_all_20260727_185501/checkpoints/steps_5000_pytorch_model.pt'；9,785,060,316 B；SHA256 '4b0067d806a321065d1521f4940d34920de234902ae4fe83a2a642ab984b277a'
3. steps10000 path '<PERSONAL_RESEARCH_ROOT>/checkpoints/cf-dynalign/cf_dynalign_baseline_libero_all_20260727_185501/checkpoints/steps_10000_pytorch_model.pt'；9,785,061,050 B；SHA256 '1687afbdcab4f4593c6261d64ac478fd151a0ebd7b641236b60ce1a01fbdee7b'

LIBERO-10 fixed tasks ID3 black bowl in bottom drawer and close；ID6 white mug on plate and chocolate pudding right of plate。Screen states0..4，env/NumPy seed7，10 dummy actions，520 policy actions，chunk8；done=True only success；horizon failure。Pre-action infra error one retry；repeat/post-action error invalidates screen。

30 rollouts。Both tasks separately SR∈[.2,.8]。Choose qualifying checkpoint pooled SR closest .5，tie earlier step。Final states：10-seed 5..9；5-seed 5..14。

## G. Offline Predictive Projector

For each seed，using folds0–1:

\[
\bar\delta=\frac1{8}\sum_k(m_A^k-m_B^k)\in\mathbb R^{2560}.
\]

Offline z=[current DINO, demonstrated action, task, progress] is used only to cross-fit:

\[
\tilde\delta=\bar\delta-\widehat E[\bar\delta|z],\quad
\tilde r=r-\widehat E[r|z].
\]

Fit PCA/whitening \(W:\mathbb R^{2560}\to\mathbb R^d\) on \(\tilde\delta\)，95% variance，d≤128。W means linear rotation/scale after explicit raw center \(\mu_\delta\)；\(W^+\) is its linear pseudoinverse and never restores \(\mu_\delta\)。

Ridge-RRR grids ridge \(\{1e{-4},1e{-3},1e{-2},1e{-1},1\}\)，rank \(\{4,8,16,32\}\)。Fold2 picks lowest nMSE，tie lower rank/stronger ridge。

Let \(B_N\) be an orthonormal basis for the whitened nuisance-predictable delta subspace \(W\widehat E[\bar\delta|z]\)。Project the predictive RRR basis into complement of \(B_N\)，re-orthonormalize to \(B_{pred}\)，and define:

\[
\Pi_{pred}=B_{pred}B_{pred}^{\top}.
\]

Nuisance annihilation gate:

\[
\frac{\lVert B_{pred}^{\top}B_N\rVert_F}{\sqrt{rank(B_{pred})}}\le10^{-3}.
\]

Fold2 P gate: incremental R²≥.02 and 1,000 episode-block permutation p<.05。

### Q

Generate 100 fixed-seed orthonormal \(B_Q\) bases in same whitened empirical span，orthogonal to \(B_{pred}\) and \(B_N\)，same rank；\(\Pi_Q=B_QB_Q^\top\)。Fold3 selection requires:

- latent removed-energy ratio [0.9,1.1]；
- per-task/per-token frozen-action-output perturbation ratio [0.9,1.1]；
- calibration point incremental R²≤.005；
- nuisance annihilation \(||B_Q^\top B_N||_F/\sqrt r≤10^{-3}\)。

Select closest deterministic match；no pass→Stage2 ineligible。After selection all artifacts freeze/hash。

### Rollout Map

Available online: h, m_A(h), m_B(h)。No DINO/action oracle/progress nuisance。

\[
x=W(\bar\delta-\mu_\delta),
\quad
v_{pred}=W^+\Pi_{pred}x,
\quad
v_Q=W^+\Pi_Qx.
\]

Apply \(m_{A,-pred}^k=m_A^k-v_{pred}\) and \(m_{A,-Q}^k=m_A^k-v_Q\) for every token k。All dimensions explicit；no mean re-addition。

## H. Locked Fold-4 Eligibility Table

Before fold4 opens，every selected seed has frozen A/B/C/P/Q/code/config hashes。Open fold4 once and never tune afterward。

For each seed separately record:

### Stage-1 eligibility

- A correct-target joint/main nMSE beats identity/B/C ≥5%，episode-bootstrap LCB>0；
- adapter residual RMS ≤10% h RMS；
- cache/direct/hot-switch parity <\(10^{-6}\)；
- C/dose/optimization gates pass。

**All selected seeds must pass Stage-1 eligibility. No drop/replacement. Any failure forbids Stage 1.**

### Stage-2 eligibility

- P point incremental R²≥.02 and episode-bootstrap 95% LCB>0；
- Q episode-bootstrap 95% UCB≤.005；
- permutation P p<.05 and Q p≥.10 are supporting only；
- P/Q energy/action-output matching remains [0.9,1.1]；
- P/Q nuisance annihilation ≤\(10^{-3}\)；
- full A→B cached/2 reserved deterministic trace action parity <\(10^{-6}\)；
- α∈{0,.5,1} PCA Mahalanobis ≤fold4 99th percentile and actions within training range。

If any seed fails Stage-2 eligibility，Stage 1 may still run if all Stage-1 rows pass，but **Stage 2 is globally forbidden**；no seed may be dropped/replaced。

## I. Physical GPU Ledger

Fresh check before every launch；default physical2/3；0/1 only if all four freshly idle。GPUh sums occupied physical-GPU wall time。

Before seed decision measure cache/head/control，30 screen，one complete triplet，one-seed P/Q through fold3，loads/errors，and wrapper overhead over 65 cached chunks。

Let:

- \(t_{fail}\): longest observed/forced full-520-step base GPU seconds；
- \(t_{screen,max}\): longest screen rollout GPU seconds；
- \(t_{wrap}\): incremental A+B+P/Q wrapper GPU seconds for 65 chunks；
- \(u_{roll}=1.10[\max(t_{fail},t_{screen,max})+t_{wrap}]/3600\) GPUh；
- \(u_{triplet}=1.10×\) measured full triplet GPUh；
- \(u_{PQ}=1.10×\) measured one-seed builder GPUh。

If no screen failure reaches horizon，run one timing-only 520-step trace and discard its outcome。

\[
H_n=H_{spent}+(n-1)u_{triplet}+n u_{PQ}
+500u_{roll}+H_{future-load/retry}+H_{reserve},
\]

\(H_{future-load/retry}≥.2\) GPUh，\(H_{reserve}=\max(.10H_{pre-reserve},.3)\)。Screen and seed0 work are in H_spent；parity traces/analysis included。Choose n=10 iff H10≤7.2；else n=5 iff H5≤7.2；else stop。Freeze decision before remaining seeds/treatment outcomes。Actual≤8。

## J. Stage 1 and Stage 2

Stage1 always 300 rollouts：

- 10 seeds×2 tasks×3 arms×5 states，or
- exploratory 5×2×3×10。

For both A−B and A−C: ≥9/10 positive (ties nonpositive, p=.0107) or 5/5 (p=.03125)；pooled≥10pp；each task mean≥0；C≥B−5pp and valid。Failure forbids Stage2。

Stage2 only if all seed Stage-2 eligibility and Stage1 pass：200 rollouts (10×2×2×5 or 5×2×2×10)。Primary SR(A_Q)−SR(A_pred): same sign rule；mean≥10pp；each task≥0；A_Q within5pp intact A；A_pred erases≥50% A−B and not below B by>10pp。

## K. Immutable Order, Safety and Claim Ceiling

Order: personal isolated source→hash/splits/cache/head→strict target gate→C→seed0 triplet/PQ/timing→screen→seed count→remaining triplets→folds0–3 P/Q freeze→one-time fold4 table→Stage1→conditional Stage2→audit。

Remote only liu_meng and '<PERSONAL_RESEARCH_ROOT>'；personal code/env/cache/tmp/log/checkpoint/metric/video/W&B/result only；never shared/team/root/sudo/su/.bashrc/global Conda/system CUDA/dirty CF tree/process interference。

Full-pass ceiling:

> On one treatment-blind-selected deterministic StarVLA checkpoint and two preregistered LIBERO tasks, a frozen valid-target gradient algorithm produced a seed-consistent closed-loop gain relative to stop-gradient and one stratified scalar-dose-matched deranged-target algorithm; removing one offline-learned, nuisance-annihilated, rollout-available treatment-associated predictive projector harmed performance more than removing an empirical-support/action-output-matched Q projector, providing task-local placebo-relative reliance evidence.

Stage1-only result stays an algorithmic contrast。Any negative gate narrows or stops the claim；budget failure is NO-RUN，不删 controls。

