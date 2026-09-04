# 研究方案：PGR-Audit——VLA 动作接口中的预测梯度路由诊断

## Problem Anchor

- **Bottom-line problem：** 判断 action-conditioned predictive world objective 是否会把一个 VLA 的共享动作接口表征塑造成对闭环控制真正有用的 future-sensitive representation，而不只是改善一个 auxiliary latent loss。
- **Must-solve bottleneck：** 既有 future-objective 工作通常把“有效未来对应关系”“任意辅助梯度带来的正则化”“action-output diversity/seed lottery”和“表征被策略实际使用”混在一起；单看 world loss、probe 或平均成功率不能回答 H1。
- **Non-goals：** 不提出新的 future objective、adapter、WAM 或 VLA；不重塑 frozen Qwen/VLM backbone；不做 planning、MBRL、视频生成、SOTA、真机或跨架构泛化；不声称 natural causal mediation、物理因果或排除了所有辅助正则化。
- **Constraints：** frozen Qwen3-VL-4B 与 frozen deterministic MLPResNet action head；个人离线 LIBERO 数据、DINOv2 和 StarVLA checkpoint；所有远程产物仅在 `<PERSONAL_RESEARCH_ROOT>`；物理 GPU 2/3 优先，0/1 仅在四卡均空闲时使用；总计不超过 8 GPUh，完整路径投影不超过 7.2 GPUh；不得接触团队/共享目录或脏 CF-DynAlign 树。
- **Success condition：** 一个严格 held-out 的 action-conditioned future target 先通过 model gate；随后有效 future gradient 相对 stop-gradient 和 matched deranged-future placebo 产生跨训练 seed 一致、至少 10pp 的 paired closed-loop gain；若继续做机制层，cross-fitted predictive-component removal 必须比 action-output-matched orthogonal placebo 更明显地消除该 gain。

## 技术缺口

### 当前 pipeline 的失败点

PFD、VLA-JEPA、VLAFlow 等工作已表明 future branch 或 predictive objective 可以与 policy performance 同时改善，但相邻研究也指出 latent/world metrics 未必预测闭环成功，output collapse 与 seed lottery 可以主导结果。普通 `action-only vs action+future` 消融至少有三种不可分解释：

1. future correspondence 真正提供了状态依赖的预测信息；
2. 任意额外梯度改变优化、输出多样性或局部 Jacobian；
3. future head 学会了任务阶段、动作或当前状态捷径，而 shared action representation 并未承载有效动态信息。

probe 只能说明可解码，head 在推理时删除也只说明部署不依赖 head；二者都不能证明被改变的 representation 对行为承重。

### 两条候选路线

- **Route A — 最小诊断路线（采用）：** 在 frozen action-token 接口插入一个 identity low-rank adapter，通过 A/B/C 三臂只随机化 future gradient 的路由与 correspondence，再用受控 representation intervention 检验 necessity-like evidence。
- **Route B — PFD-style output correction（拒绝）：** 直接训练 future-conditioned residual correction 或新的 action head。它更像一个方法，但与 PFD 高度重叠，并把 representation shaping、额外容量和 output correction 再次混在一起。

Route A 不追求更大的方法故事；它以更窄但可证伪的识别问题换取可解释性和当前资源适配。

## Method Thesis

- **一句话 thesis：** 在固定 deterministic StarVLA 中，只有当通过严格 world-validity gate 的 future correspondence 梯度相对 stop-gradient 和 support/gradient-norm-matched deranged placebo 都带来一致闭环收益，并且该收益对 treatment-induced predictive interface component 的受控移除具有特异性，才能说这个 world objective 塑造了被策略使用的 action-interface representation。
- **最小充分干预：** 一个低秩 identity adapter、一个预训练后冻结的 future decoder、三个锁步训练臂；不更新 4B backbone 或原 action head。
- **foundation-model-era 角色：** Qwen3-VL 只提供 frozen VLA action-token representation，DINOv2 只作为 frozen latent target teacher。没有必要强行加入 Diffusion、RL 或 LLM planning。

## 贡献焦点

- **Dominant contribution：** 一个对 future-gradient correspondence specificity 和 representation necessity-like use 进行双重识别的、预注册三臂机制诊断协议。
- **Supporting contribution：** 在 deterministic frozen-VLA host 上实现可缓存、锁步、低成本的 action-interface intervention，并明确 model–policy–environment 三层证据。
- **明确非贡献：** low-rank adapter、DINO residual、future head 和 sign test 均不是算法创新；贡献不能建立在这些部件本身。

## Proposed Method

### Complexity Budget

- **Frozen / reused：**
  - clean StarVLA HEAD `3422b9f2387b6f682cf02802904a77b23ab13afd`;
  - Qwen3-VL-4B action-token encoder；
  - 8-token、7D deterministic MLPResNet action head；
  - DINOv2 ViT-S/14 teacher；
  - LIBERO demonstrations、simulator 和 existing early checkpoints。
- **New trainable components：**
  1. shared identity low-rank interface adapter；
  2. future head（仅预训练阶段 trainable，A/B/C 阶段冻结）。
- **有意排除：** backbone LoRA、action-head finetuning、视频 decoder、planner、value head、RL、多个 horizon、多个 latent teachers、CF-DynAlign predictor/cache。

### System Overview

```text
current dual-view observation + language + proprio
                 │
                 ▼
        frozen Qwen3-VL / StarVLA
                 │
        h_t ∈ R^[B,8,2560]
                 │
        identity low-rank adapter m_φ
            ┌────┴────┐
            ▼         ▼
 frozen action head   frozen valid future head q(m,a*)
            │         │
       8×7 action     64-D future residual
            │         │
        L_action      L_future
            └────┬────┘
                 ▼
          only φ is updated
```

Inference discards the future head. A resident base model hot-switches only small adapter/intervention artifacts.

### Shared Interface Adapter

For each action token:

\[
m_\phi(h)=h+U_\phi V_\phi \operatorname{LN}(h),
\]

where `rank r=32`, `V∈R^{32×2560}`, `U∈R^{2560×32}`, and the same adapter is shared across eight action tokens. Use parameter-free layer normalization, Kaiming initialization for `V`, and `U=0` so the initial map is numerically identity. The frozen action head still backpropagates action loss into `φ`.

Primary adapter settings are fixed before environment outcomes: AdamW, 500 cached-feature steps, identical batches across A/B/C, no weight decay on `U,V`, and identical action L1. Exact batch size and learning rate are chosen only by a tiny-cache overfit/stability gate, never by rollout success, then frozen for all seeds.

### Future Target and Frozen Head

For each valid sample, retrieve both cameras at `t` and `t+8`; exclude any sample crossing an episode boundary. Use deterministic DINOv2 preprocessing and concatenate the primary/wrist CLS differences:

\[
d_t=[E(o^{main}_{t+8})-E(o^{main}_{t});
     E(o^{wrist}_{t+8})-E(o^{wrist}_{t})]\in \mathbb{R}^{768}.
\]

Fit whitening statistics on train episodes only, then apply a seed-independent fixed Gaussian/JL projection `R∈R^{64×768}` with orthonormalized rows:

\[
y_t=R\,\mathrm{Whiten}(d_t).
\]

The demonstrated normalized action chunk `a^*_{t:t+7}∈R^{56}` is the action condition.

The future head uses:

- mean-pooled, normalized eight-token `m`;
- a 256-D state projection and 128-D action projection;
- a two-layer GELU MLP to a 64-D output;
- Huber loss on `y_t`.

Train it once on identity-adapter cached features. Select by episode-disjoint validation, then freeze and clone the exact head, target projection, and normalization state to every A/B/C arm.

### Strict World-Validity Gate

Use deterministic episode-hash train/validation/strict-test splits with no overlapping future window. The strict test is untouched until architecture and hyperparameters are frozen.

Compare equal-capacity heads or masked-input variants:

- full `q(m,a)`;
- state-only `q(m,0)`;
- action-only `q(0,a)`;
- current-DINO-only;
- task×progress-bin mean;
- zero/persistence.

Pass only if, on strict test:

1. full head has at least 5% lower normalized MSE than the strongest learned/nonlearned baseline, with an episode-bootstrap one-sided 95% lower confidence bound above zero;
2. within task×progress-bin action derangement increases normalized MSE by at least 5%, lower bound above zero;
3. cross-episode representation derangement increases normalized MSE by at least 5%, lower bound above zero;
4. no leakage, invalid `t+8`, padding, or preprocessing nondeterminism is found.

Failure ends H1 before policy treatment.

### Three-Arm Gradient-Routing Treatment

For seed `s`, clone the same adapter initialization and optimizer settings and train all arms lockstep on identical cached minibatches.

- **A / valid:** `L_A=L_action+λ_A L_future(q(m_A,a),y)`.
- **B / stop-grad:** compute the identical future forward/loss on `sg(m_B)`; only `L_action` updates the adapter.
- **C / deranged placebo:** `L_C=L_action+λ_C L_future(q(m_C,a),π(y))`.

`π` is fixed before training. It is a no-fixed-point donor mapping across different episodes and nonoverlapping future windows inside task × episode-progress decile × action-norm tercile. Sparse strata are merged by a fixed nearest-bin rule; donor identity and bin error are persisted.

Set A's auxiliary adapter-gradient norm to a fixed `κ=0.30` of its action-gradient norm each batch. Scale C so its auxiliary adapter-gradient norm is within `[0.9,1.1]` of A on that same batch. Log raw/scaled auxiliary norms, action norm, their cosine, total unclipped/clipped norm, clip rate, Adam first/second moments, update norm, adapter residual norm, and all nonfinite events.

C is invalid if leakage occurs, the 0.9–1.1 norm gate fails systematically, its update/clip diagnostics differ systematically by more than 10%, or it shows optimization collapse. A>C is then not interpretable.

### Treatment-Blind Checkpoint and Task Screen

No early-checkpoint environment result exists. Freeze two faster final-checkpoint LIBERO-10 tasks from the existing personal log:

1. eval task 3 / dataset task index 8: `put the black bowl in the bottom drawer of the cabinet and close it`;
2. eval task 6 / dataset task index 1: `put the white mug on the plate and put the chocolate pudding to the right of the plate`.

Before any treatment is trained, evaluate checkpoints 1k, 5k, and 10k on screen initial-state indices `0..4` for both tasks: 30 baseline-only rollouts. Select the checkpoint whose pooled success lies in `[0.2,0.8]` and is closest to 0.5; ties select the earlier checkpoint. Final treatment evaluation uses only indices `5..` and never reuses screen states.

If no checkpoint lies in the admissible interval, record the preregistered checkpoint-screen failure and stop rather than choose a task/checkpoint after seeing treatment outcomes. These 30 rollouts also provide the required wall-time calibration and count toward total GPUh.

### Seed Count Rule and Stage 1

After cache/head/triplet timing but before any A/B/C environment outcome:

- choose **10 paired training seeds** if the full worst-case screen + Stage 1 + conditional Stage 2 projection is at most 7.2 GPUh;
- otherwise choose the predeclared **5 paired-seed exploratory design** only if its full projection is at most 7.2 GPUh;
- otherwise stop.

Use seeds `0..9` (or `0..4` for fallback), with A/B/C paired within seed.

Preferred design: 10 seeds × 2 tasks × 3 arms × 5 common final initial states = 300 Stage-1 rollouts. Per seed, equal-weight both tasks and compute `d_AB` and `d_AC`.

The intersection-union gate passes only if:

- at least 9/10 non-tied seed differences are positive for both A−B and A−C (one-sided exact sign `p=0.0107` for 9/10);
- each pooled gain is at least 10pp;
- neither task has a negative mean contrast;
- C is not more than 5pp worse than B and its optimization audit passes;
- action-output diversity/effective-rank changes do not alone account for the effect.

For the 5-seed fallback, all five non-tied differences must be positive for both contrasts (`p=0.03125`), with the same effect and stability gates. Its result is explicitly exploratory/provisional.

### Predictive Component and Stage 2

For each seed, compute on episode-disjoint mechanism data:

\[
\delta_s(x)=\operatorname{vec}(m_A(h_x)-m_B(h_x)).
\]

Residualize the future target against frozen baseline covariates, then fit ridge reduced-rank regression from `δ_s` to the residual target. Select rank from a fixed set `{4,8,16,32}` using nested episode cross-validation only; freeze the selected row-space projector `P_s` before any Stage-2 rollout.

Interventions:

- predictive removal: `m_{A,-pred}=m_A-\operatorname{unvec}(P_s\delta_s)`;
- orthogonal placebo: remove a pre-generated complementary rank-matched direction whose latent energy and initial frozen-action-head output perturbation match predictive removal within 10% on an independent calibration fold;
- positive control: `m_A-\delta_s=m_B` must reproduce B action outputs numerically.

Pre-generate 100 orthogonal bases from a fixed seed and select the closest match using only offline energy/action-output criteria. Persist all candidates and the deterministic selection score. Check interpolation `α∈{0,0.5,1}` and reject out-of-support interventions.

Only if Stage 1 passes, run 10 seeds × 2 tasks × 2 removal conditions × 5 common states = 200 rollouts. The single primary contrast is `SR(A_orth)-SR(A_pred-remove)`. Require at least 9/10 positive seed differences, mean at least 10pp, and at least 50% attenuation of the Stage-1 A−B gap. The fallback 5-seed design requires 5/5 positive.

This supports only task-local, placebo-relative necessity-like evidence.

### Inference Integration

Strictly load the vanilla base checkpoint first, then the small adapter/subspace artifact. Keep one base model resident per evaluator and hot-switch `adapter_id` and `intervention`; never save or reload a full 9.78 GB checkpoint per arm. Disable rollout video by default and specify exact task IDs and initial-state indices.

### Implementation Isolation

Create only after this proposal passes review:

```text
<PERSONAL_RESEARCH_ROOT>/workspace/h1-predictive-aux-starvla/
  h1/cache_features.py
  h1/models.py
  h1/train_paired.py
  h1/build_predictive_subspace.py
  h1/policy_wrapper_h1.py
  h1/eval_libero_h1.py
```

All caches, manifests, environments, tmp files, logs, incremental checkpoints, metrics, W&B offline files, and results remain beneath `<PERSONAL_RESEARCH_ROOT>`. The dirty CF-DynAlign tree and all team/shared paths are untouchable.

## Failure Modes and Diagnostics

- **Future head uses shortcuts：** strict state-only/action-only/shuffle gates fail → stop before adapter training.
- **Cache changes the policy：** direct online versus cached-hidden action parity fails → repair cache; no training.
- **C is simply harmful：** B−C exceeds 5pp or optimization diagnostics mismatch → invalidate specificity claim.
- **Seed lottery/output collapse：** report per-seed action diversity, effective rank, cosine and losses; if these explain outcomes without predictive specificity, downgrade/stop.
- **Ceiling/floor checkpoint：** baseline screen outside 20–80% → stop.
- **Intervention leaves support：** parity/interpolation/support check fails → no mechanism rollout.
- **Budget drift：** cumulative worst-case projection exceeds 7.2 GPUh → stop without deleting controls.
- **GPU conflict：** physical GPU 2/3 not idle at launch → wait; use 0/1 only if all four are freshly verified idle.

## Novelty and Elegance Argument

The design is intentionally not a new world-model architecture. PFD already studies future-conditioned output correction with pure-finetune and shuffled-future controls; VLA-JEPA/VLAFlow already use future objectives; mechanistic VLA work already performs representation interventions; Output-Level Regularization already exposes frozen-VLA seed instability. The narrow remaining delta is their conjunction under a randomized gradient-routing treatment:

- a correct future objective versus its stop-gradient version;
- the same gradient magnitude with correspondence destroyed;
- a treatment-induced predictive component versus an action-output-matched orthogonal intervention.

This is focused because every component exists to remove one named alternative explanation. Removing any one of B, C, or the matched intervention lowers the allowed claim rather than merely reducing benchmark coverage.

## Claim-Driven Validation Sketch

### Claim 1：future-correspondence-specific gradient routing has a local closed-loop effect

- **Minimal experiment：** strict world gate, then paired A/B/C Stage 1.
- **Baselines/ablations：** stop-gradient B and support/norm-matched deranged C.
- **Primary endpoint：** training-seed-level paired LIBERO success contrasts A−B and A−C.
- **Decisive evidence：** preregistered sign and ≥10pp gates, no task reversal, valid C audit.
- **Negative interpretation：** no evidence for a large, seed-consistent effect in this checkpoint/tasks/adapter; not proof that future objectives are generally ineffective.

### Claim 2：the treatment-induced predictive interface component carries necessity-like evidence

- **Minimal experiment：** Stage-2 predictive removal versus rank/energy/action-output-matched orthogonal removal.
- **Baselines/ablations：** full A→B replacement positive control; interpolation/support controls.
- **Primary endpoint：** seed-level `SR(A_orth)-SR(A_pred-remove)`.
- **Decisive evidence：** preregistered sign/10pp gate and ≥50% A−B attenuation.
- **Negative interpretation：** Stage-1 total effect may remain, but the proposed representation mechanism is unsupported.

## Experiment Handoff Inputs

- **Must-prove claims：** Claim 1; Claim 2 only after Claim 1.
- **Must-run controls：** full world baseline ladder, cache parity, B, C, gradient audit, action diversity, patch positive control, action-output-matched orthogonal placebo.
- **Critical data/metrics：** episode-disjoint `t/t+8`, normalized MSE and shuffle sensitivity; paired SR; per-seed/task outcomes; exact GPUh.
- **Highest-risk assumptions：** action information adds held-out predictive value beyond state/task phase; early checkpoint screen enters 20–80%; C remains non-collapsed; 10-seed full path fits 7.2 GPUh.

## Compute & Timeline Estimate

- **Storage：** approximately 1.2 GiB shared cache plus <0.1 GiB incremental artifacts.
- **Baseline screen：** 30 rollouts, approximately 0.33–0.75 GPUh.
- **500 treatment/mechanism rollouts：** approximately 5.06 GPUh at historical task timing before failure-length adjustment.
- **Cache/head/triplet training：** five-seed estimate 0.5–1.2 GPUh; ten-seed version must be measured.
- **Hard rule：** every pilot counts; full worst-case projection must be ≤7.2 GPUh and actual total ≤8 GPUh.
- **Real robot / paid API：** none.
- **Timeline：** method review → isolated implementation → interface/world/timing gates → Stage 1 → conditional Stage 2 → audit.
