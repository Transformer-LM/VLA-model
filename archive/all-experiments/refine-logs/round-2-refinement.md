# Round 2 Refinement

## Problem Anchor

- **Bottom-line problem：** 判断 action-conditioned predictive world objective 是否会把一个 VLA 的共享动作接口表征塑造成对闭环控制真正有用的 future-sensitive representation，而不只是改善一个 auxiliary latent loss。
- **Must-solve bottleneck：** 既有 future-objective 工作通常把“有效未来对应关系”“任意辅助梯度带来的正则化”“action-output diversity/seed lottery”和“表征被策略实际使用”混在一起；单看 world loss、probe 或平均成功率不能回答 H1。
- **Non-goals：** 不提出新的 future objective、adapter、WAM 或 VLA；不重塑 frozen Qwen/VLM backbone；不做 planning、MBRL、视频生成、SOTA、真机或跨架构泛化；不声称 natural causal mediation、物理因果或排除了所有辅助正则化。
- **Constraints：** frozen Qwen3-VL-4B 与 frozen deterministic MLPResNet action head；个人离线 LIBERO 数据、DINOv2 和 StarVLA checkpoint；所有远程产物仅在 '<PERSONAL_RESEARCH_ROOT>'；物理 GPU 2/3 优先，0/1 仅在四卡均空闲时使用；总计不超过 8 GPUh，完整路径投影不超过 7.2 GPUh；不得接触团队/共享目录或脏 CF-DynAlign 树。
- **Success condition：** 一个严格 held-out 的 action-conditioned future target 先通过 model gate；随后有效 future gradient 相对 stop-gradient 和 matched deranged-future placebo 产生跨训练 seed 一致、至少 10pp 的 paired closed-loop gain；若继续做机制层，cross-fitted predictive-component removal 必须比 action-output-matched orthogonal placebo 更明显地消除该 gain。

## Anchor Check

- 原问题未改变：仍识别 future correspondence 是否塑造被 deterministic VLA policy 使用的 action-interface component。
- 不加入同状态 action forks，因此只声称 behavior-policy predictive association。
- 不加入 online DINO、demonstrated-action oracle、RL、planning、Diffusion 或更多任务。

## Simplicity Check

- 唯一贡献仍是 sequential identification contract。
- Round-2 的三个改动全部删除在线依赖或数据复用：offline nuisance-orthogonal basis、五折职责分离、horizon-aware budget。
- 删除 B 的 discarded shadow VJP 与 Kronecker notation；B 只保留 identical frozen future forward/loss logging。

## Changes Made

1. **部署闭合：** P/Q 从 offline nuisance-residualized data 学习，但 rollout 只需 A/B adapter 的 raw centered mean delta。无需 online DINO、progress 或 demonstrated action。
2. **维度闭合：** whitening 只作用 2560-D mean delta；inverse 只应用线性 scale，不重新加 mean；同一个 2560-D removal vector 施加到八个 token。
3. **最终 fold 闭合：** D_post folds 0–1 fit、2 rank validation、3 Q calibration、4 locked final gate。Fold 4 打开后任何 artifact 不得修改。
4. **预算闭合：** rollout upper bound 使用 screen 中完整失败 horizon 与 instrumented Stage-2 wrapper 的较大值；P/Q cost 显式乘 seed 数。

## Revised Proposal

# PGR-Audit：预测梯度在 frozen VLA action interface 中的顺序识别

## 1. Claim and Scope

主问题：

> 对一个从预注册集合中 treatment-blind 选择的 deterministic StarVLA checkpoint，一个通过 held-out predictive-validity gate 的 future-latent loss，其正确 correspondence gradient 是否相对 stop-gradient 和一个严格匹配的错配 gradient algorithm 产生局部闭环收益；若有，该收益是否依赖一个预先冻结、placebo-relative 的 treatment-associated predictive component？

最多支持 behavior-policy association 与 controlled reliance；不支持 causal action dynamics、natural mediation、physical causality 或 general VLA conclusion。

## 2. Frozen Host and Minimal Trainable Parts

- clean StarVLA HEAD '3422b9f2387b6f682cf02802904a77b23ab13afd'；
- frozen Qwen3-VL-4B；
- frozen deterministic MLPResNet action head；
- hidden '[B,8,2560]'，eight actions × seven dimensions；
- DINOv2 ViT-S/14 仅作离线 frozen teacher；
- rank-32 shared identity adapter：

\[
m_\phi(h)=h+U_\phi V_\phi\operatorname{LN}(h).
\]

'V' Kaiming，'U=0'，LN 无 affine。Initial/cache/hot-switch normalized-action max error 均须 < \(10^{-6}\)。

唯一 trainable components：future decoder（仅 head phase），adapter（仅 A/B/C phase）。

## 3. Episode Isolation

按 task 分层，以 'SHA256(task_id|episode_id|1701)' 排序：

- D_head 50%；
- D_adapter 30%；
- D_post 20%。

每部分每 task 至少三个 episodes，否则 stop。所有 't+8' 越界样本删除；禁止 terminal-frame padding。

D_head：70% train / 15% val / 15% strict-test。  
D_post 固定五 folds：

- folds 0–1: nuisance/mechanism fit and cross-fitting；
- fold 2: ridge/rank validation；
- fold 3: Q candidate calibration/matching；
- fold 4: locked final offline gate。

Manifests 在 strict-test 前 hash。Fold 4 在 A/B/C/P/Q 全部冻结并 hash 前不得打开；打开一次后不得改变任何 artifact。

## 4. Nuisance-Residualized Future Target

对 main 与 wrist camera：

\[
d_t^c=E_c(o_{t+8})-E_c(o_t),\quad c\in\{main,wrist\}.
\]

Whitening 仅在 D_head-train 拟合。使用 seed 1701 的 two fixed orthonormal Gaussian projections \(R_c:384\rightarrow32\)，拼成 64-D target y。

Current nuisance：

\[
z_t=[E_{main}(o_t),E_{wrist}(o_t),onehot(task),progress],\qquad
r_t=y_t-b(z_t).
\]

Linear ridge b 在 head-train 做 five-fold episode cross-fitting后 refit；grid \(\{10^{-4},10^{-3},10^{-2},10^{-1},1,10\}\)，val nMSE 最低，tie 取更强 regularization。相同 frozen b/whitening/R 用于所有后续数据。

该 residual target 明确只是在 behavior-policy support 上超越 current visual/task-progress nuisance 的 future association。

## 5. Frozen Future Decoder and Predictive Gate

Decoder：

- mean-pooled parameter-free-LN m → Linear 2560→256 + GELU；
- normalized 56-D demonstrated action chunk → Linear 56→128 + GELU；
- concatenate → Linear 384→256 + GELU → Linear 256→64；
- no dropout。

Seed 1701；AdamW lr \(3\times10^{-4}\)，wd \(10^{-4}\)，batch 256，max 100 epochs；val patience 10，min delta \(10^{-4}\)，best val nMSE，tie earliest epoch。完成后 decoder、preprocessing、target、nuisance、split 和 config 全部 hash，decoder eval/frozen。

Separately trained schedule-matched controls：

- full q(m,a)；
- state-only q(m,0)；
- action-only q(0,a)；
- current-DINO-plus-action；
- additive \(q_s(m)+q_a(a)\)；
- nuisance/task-progress/zero。

在 D_head strict-test，full 必须在 joint 64-D 与 main-camera 32-D 分别：

- 比最强 control nMSE 低 ≥5%；
- episode-bootstrap one-sided 95% lower bound >0；
- stratified action derangement 使 nMSE 恶化 ≥5%、lower bound >0；
- cross-episode representation derangement使 nMSE 恶化 ≥5%、lower bound >0。

任一失败即 NO-RUN。

## 6. Fixed C Derangement

在 D_adapter 内，donor 必须 different episode、future windows nonoverlap、no fixed point，并匹配 task × progress decile × action-norm tercile。每 stratum 以 standardized target norm 与 identity-head Huber loss distance 做 fixed minimum-cost derangement；不可行时按固定顺序合并相邻 action-norm bin，再合并 progress bin。

训练前 C/A 必须满足：

- target norm ratio [0.9,1.1]；
- identity-head loss ratio [0.9,1.1]；
- Huber saturated-coordinate rate difference ≤5pp。

所有 donor/merge/hash 固定；不允许 outcome-driven resampling。

## 7. Exact Paired A/B/C Algorithms

每 seed 三臂共享 identity initialization、batch order、500 steps、batch 256。Adapter optimizer 为 plain SGD lr \(10^{-3}\)，momentum 0，wd 0，total-gradient clip 1.0。

FP32、'create_graph=False'、detached scale：

\[
g_j^{act}=\nabla_{\phi_j}L_{action},
\quad
g_A^{fut}=\nabla_{\phi_A}L_{future}(q(m_A,a),r),
\quad
g_C^{fut}=\nabla_{\phi_C}L_{future}(q(m_C,a),\pi(r)).
\]

\[
\rho=0.30\lVert g_B^{act}\rVert_2,
\qquad
s_j=\operatorname{clip}\left(
\frac{\rho}{\lVert g_j^{fut}\rVert_2+10^{-12}},
10^{-3},10^3\right).
\]

\[
g_A=g_A^{act}+s_Ag_A^{fut},\qquad
g_B=g_B^{act},\qquad
g_C=g_C^{act}+s_Cg_C^{fut}.
\]

B 执行相同 frozen future forward/loss logging，但不做无效 shadow backward。A/C pre-clip auxiliary norm 对 rho 的误差 ≤1%。任何 nonfinite stop；cap/zero fallback ≤1% batches；≥99% batches pass dose gate。Log loss、raw/scaled norm、action/aux cosine、total norm、clip rate、SGD update、adapter residual。

只能解释为 A 相对这个 fixed C algorithm 的差异。

## 8. Checkpoint/Task Screen

Preregistered exact checkpoints：

- steps 1000:  
  '<PERSONAL_RESEARCH_ROOT>/checkpoints/cf-dynalign/cf_dynalign_baseline_libero_all_20260727_185501/checkpoints/steps_1000_pytorch_model.pt'  
  9,785,060,316 B；SHA256 '6e2f52758054f0da6d76640dfcfc3dd324b0a14f2cf24d4626262781fd1d4735'
- steps 5000:  
  '<PERSONAL_RESEARCH_ROOT>/checkpoints/cf-dynalign/cf_dynalign_baseline_libero_all_20260727_185501/checkpoints/steps_5000_pytorch_model.pt'  
  9,785,060,316 B；SHA256 '4b0067d806a321065d1521f4940d34920de234902ae4fe83a2a642ab984b277a'
- steps 10000:  
  '<PERSONAL_RESEARCH_ROOT>/checkpoints/cf-dynalign/cf_dynalign_baseline_libero_all_20260727_185501/checkpoints/steps_10000_pytorch_model.pt'  
  9,785,061,050 B；SHA256 '1687afbdcab4f4593c6261d64ac478fd151a0ebd7b641236b60ce1a01fbdee7b'

Fixed LIBERO-10 tasks：

- ID 3：put the black bowl in the bottom drawer of the cabinet and close it；
- ID 6：put the white mug on the plate and put the chocolate pudding to the right of the plate。

Screen states 0..4，env/NumPy seed 7，10 dummy settle actions，520 policy actions，8-action open-loop chunks；only done=True is success，horizon exhaustion failure。Exception before first policy action gets one logged retry；second or post-action exception makes screen incomplete and gate fail。

30 baseline-only rollouts。每 task SR separately in [0.2,0.8]。合格 checkpoint pooled SR closest to .5，tie earlier step。Final states：10-seed path 5..9；5-seed path 5..14。

## 9. Post-Training Builder Before Any Treatment Outcome

Train seed 0 triplet first for timing and builder calibration，仍不得运行或打开 A/B/C LIBERO outcomes。

### 9.1 Raw rollout-available delta

\[
\bar\delta(x)=\frac1{8}\sum_{k=1}^8(m_A^k(h_x)-m_B^k(h_x))\in\mathbb R^{2560}.
\]

At rollout，h、m_A、m_B 均可直接计算。No online DINO、progress、demonstrated action 或 nuisance inference。

### 9.2 Offline nuisance-orthogonal predictive basis

在 D_post folds 0–1，offline covariates \(z=[current\ DINO, demonstrated\ action,task,progress]\) 只用于学习 nuisance-predictable delta subspace N 和 cross-fitted residuals：

\[
\tilde\delta=\bar\delta-\widehat E[\bar\delta|z],
\qquad
\tilde r=r-\widehat E[r|z].
\]

PCA/whitening W 只由 \(\tilde\delta\) 拟合，retain 95% variance、cap 128 dims。Ridge-RRR grids：ridge \(\{10^{-4},10^{-3},10^{-2},10^{-1},1\}\)，rank \(\{4,8,16,32\}\)。Fold 2 选 OOF nMSE lowest，tie lower rank / stronger ridge。

把 predictive basis 在 whitened empirical space 中正交投影到 nuisance-predictable subspace N 的 complement，再重新 orthonormalize，得到 \(T_{pred}\)。要求 fold-2 incremental \(R^2\ge0.02\) 且 1,000 episode-block target permutations one-sided \(p<0.05\)。

### 9.3 Deployment map

定义 \(\mu_\delta\) 为 folds 0–1 raw mean delta；W 只包含 centering 后的 linear PCA rotation/scaling。Rollout removal：

\[
x=W(\bar\delta-\mu_\delta),\qquad
v_{pred}=W_{scale}^{+}T_{pred}x,
\qquad
m_{A,-pred}^k=m_A^k-v_{pred}\quad\forall k.
\]

\(W_{scale}^{+}\) 是 linear pseudoinverse；绝不重新加入 \(\mu_\delta\)。维度均为 2560；同一 v 施加到八 token。This is the explicit token-shared operator。

### 9.4 Q placebo

Generate 100 fixed-seed Q bases in the same whitened empirical delta span，orthogonal to T_pred and N，same rank。Fold 3 only selects candidates satisfying：

- removed latent energy ratio [0.9,1.1]；
- per-task/per-token frozen-action-output perturbation ratio [0.9,1.1]；
- fold-3 target incremental \(R^2\le0.005\)，permutation \(p\ge0.10\)。

Q deployment uses the same centered raw delta and linear pseudoinverse。No candidate → no Stage 2。

After Q selection，freeze/hash A/B/C, mu, W, N, T_pred, Q, grids, thresholds, P/Q code and all manifests。Then and only then open fold 4 once。

### 9.5 Locked fold-4 gate

On fold 4：

- correct-target joint/main nMSE of A beats identity、B、C by ≥5%，one-sided episode lower bound >0；
- T_pred incremental \(R^2\ge0.02\)、permutation \(p<0.05\)；
- Q incremental \(R^2\le0.005\)、\(p\ge0.10\)；
- rank/energy/action-output matching remains within [0.9,1.1]；
- adapter residual RMS ≤10% of h RMS；
- cache/direct/hot-switch action parity < \(10^{-6}\)。

No choices may change after fold 4。Failure forbids Stage 1。

### 9.6 A→B positive control and support

\[
m_A^k-(m_A^k-m_B^k)=m_B^k.
\]

Cached normalized-action error < \(10^{-6}\)。Two reserved deterministic trace checks also require per-chunk parity < \(10^{-6}\)。For α∈{0,.5,1}，P/Q intervention PCA Mahalanobis distance must stay below fold-4 99th percentile and normalized actions inside training range。

## 10. Horizon-Aware GPU Ledger

Every physical GPU occupied contributes wall time to GPUh。Every launch rechecks 0–3；default only 2/3；0/1 only if all four freshly idle。

Measured before seed decision：

- full cache/head/control work；
- 30 screen rollouts；
- one 500-step lockstep triplet；
- one seed P/Q builder through fold 3；
- screen failed-rollout full-horizon time；
- instrumented Stage-2 wrapper overhead on 65 cached action-chunk calls；
- loads/failures/retries already incurred。

Let：

- \(t_{fail}\): maximum physical-GPU seconds among screen failures that reach 520 policy steps；
- \(t_{screen,max}\): maximum observed screen rollout GPU seconds；
- \(t_{wrap}\): measured incremental GPU seconds for A+B adapter plus P/Q over 65 chunks；
- \(u_{roll}=1.10\max(t_{fail},t_{screen,max}+t_{wrap})/3600\) GPUh；
- \(u_{triplet}=1.10\times\) measured full triplet GPUh；
- \(u_{PQ}=1.10\times\) measured one-seed builder GPUh。

If no screen failure reaches full horizon，run one timing-only forced 520-step inference/simulator trace whose success outcome is discarded and never used for selection。

\[
H_n=H_{spent}+(n-1)u_{triplet}+n\,u_{PQ}
    +300u_{roll}+200u_{roll}+H_{future-load/retry}+H_{reserve},
\]

where \(n\in\{10,5\}\)，\(H_{future-load/retry}\ge0.2\) GPUh，and
\(H_{reserve}=\max(0.10\times H_{pre-reserve},0.3)\) GPUh。Screen 30 and seed-0 measurements are already in H_spent；two parity traces and all GPU-side analysis are included explicitly。

Choose 10 iff \(H_{10}\le7.2\)；else 5 iff \(H_5\le7.2\)；else stop。Decision hash occurs before remaining seed training and before any treatment rollout。Actual cumulative cap 8 GPUh。

## 11. Stage 1

10-seed preferred：10×2 tasks×3 arms×5 states=300。5-seed exploratory：5×2×3×10=300。

Per seed equal-weight tasks。Both A−B and A−C must satisfy：

- 10-seed: ≥9 positive among all 10，ties non-positive，one-sided exact p=.0107；
- 5-seed: 5/5 positive，p=.03125；
- pooled gain ≥10pp；
- each task mean ≥0；
- C no more than 5pp below B and all C optimization gates pass。

Failure forbids Stage 2。Output diversity/effective rank/cosine are reported as competing diagnostics，not substitute endpoints。

## 12. Stage 2

Only after Stage 1 pass：

- \(m_{A,-pred}^k=m_A^k-v_{pred}\)；
- \(m_{A,-orth}^k=m_A^k-v_Q\)。

10-seed：10×2×2×5=200。5-seed：5×2×2×10=200。

Primary contrast SR(A_orth)−SR(A_pred)：

- ≥9/10 positive or 5/5 fallback；
- mean ≥10pp；
- each task mean ≥0；
- A_orth harm from intact A ≤5pp；
- A_pred erases ≥50% A−B gap；
- A_pred not more than 10pp below B。

Passing supports only controlled, task-local, placebo-relative reliance on one preregistered linear treatment-associated predictive subspace。

## 13. Immutable Order and Remote Safety

Order：

1. isolated personal source and dependency hashes；
2. split/cache/target/nuisance/head artifacts；
3. D_head strict gate；
4. C map/matching；
5. seed-0 triplet + P/Q calibration + parity；
6. baseline screen and horizon timing；
7. seed-count decision；
8. remaining triplets；
9. freeze/hash all P/Q using folds 0–3；
10. locked fold-4 gate；
11. Stage 1；
12. conditional Stage 2；
13. integrity audit and claim mapping。

Remote:

- only SSH user liu_meng；
- read/write only '<PERSONAL_RESEARCH_ROOT>'；
- all source/env/cache/tmp/log/checkpoint/metric/video/W&B offline/result personal；
- never root/sudo/su/.bashrc/global Conda/system CUDA/shared dirs；
- never modify dirty CF-DynAlign tree；
- never kill/overwrite unrelated process；
- GPU 2/3 first and rechecked each launch。

## 14. Claim Ceiling and Negative Outcomes

If all gates pass：

> 对一个从预注册集合中 treatment-blind 选择的 deterministic StarVLA checkpoint、两个预注册 LIBERO tasks 和一个 frozen future decoder，valid-target gradient algorithm 相对 stop-gradient 与一个 stratified、scalar-dose-matched deranged-target algorithm 产生了 training-seed-consistent closed-loop gain；一个在 offline nuisance-orthogonal empirical delta span 中学习、随后只用 rollout-available raw A−B delta 计算的 predictive component，其移除比 matched orthogonal component 更伤害性能，提供 task-local、placebo-relative reliance evidence。

If only Stage 1 passes：只报告 controlled algorithmic effect。  
If predictive/fold/PQ gate fails：不运行环境主实验或不做 mechanism claim。  
If Stage 1 fails：只说明没有观察到大且跨 seed 一致的 local effect，不排除小效应。  
If budget fails：evidence-gated NO-RUN，不删 controls。  
不得声称 causal mediation、causal dynamics、Qwen reshaping、新 WAM/objective/adapter、generic-regularization exclusion、SOTA、LIBERO/VLA generality 或 real-robot transfer。

