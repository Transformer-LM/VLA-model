# Research Proposal: ISRAC——影响分离的残差别名反事实编译器

## Problem Anchor

- **Bottom-line problem**：反馈式 WAM 会利用一次已执行动作的预测残差，去修正、排序或拒绝另一个尚未执行的候选动作；但同一段 factual 反馈并不一定能识别不同候选动作所需的物理修正方向。我们需要自动构造可审计的具身反例，判断这种跨动作残差迁移何时在信息上不充分、何时会伤害 VLA 的动作选择。
- **Must-solve bottleneck**：现有 WAM 纠错与 VLA 测试缺少一种同时满足以下条件的反例生成器：factual 动态转录在两个合法物理世界中相同；候选动作由冻结策略真实提出；候选动作的物理结果发生可定位分叉；编译过程不读取被测 WAM 的 score；每个样本附带机器可验的 equality–activation–first-divergence 证书。
- **Non-goals**：不训练新的 RGB/Depth/PointMap WAM；不提出新的 VLA action head；不把一般 world-model exploitation、一般 metamorphic testing 或 two-point 不可辨识性定理包装成新贡献；当前不启动真实机器人；不使用触觉。
- **Constraints**：远端无外网；所有资产与结果仅位于 `<PERSONAL_RESEARCH_ROOT>`；冻结现有 StarVLA/π0.5 类策略；第一阶段以 LIBERO/robosuite rollback 为主；仅在编译器门槛通过后使用空闲 A100 做 WAM 审计；所有搜索与证书必须报告完整失败样本和 simulator-call 预算。
- **Success condition**：在相同 simulator calls、相同物理参数范围和相同证书下，ISRAC 相对最强 random/grid/CMA-ES/BO 类搜索至少获得稳健的 2× certified-pair yield，并跨多个任务、至少两个物理机制族复现；随后这些冻结并哈希的 pairs 在至少两个未参与编译的反馈 WAM 接口上显著提高 correction-harm 或 ranking-regret，相对普通强度匹配扰动具有特异性。

## Technical Gap

反馈式 WAM、执行验证和候选动作重排序已经有大量工作；WAM 被 planner 利用错误、VLA metamorphic testing、控制器 falsification 也都有明确先例。因此，“发现 WAM 会错”或“对动作做反事实 rollout”都不是这里的创新。

尚缺的是一种**模型盲、动作支持内、物理原生且有证书的反例编译机制**。普通随机化或黑盒优化会在整个物理空间搜索，绝大多数样本要么已经改变 factual 历史，要么没有在 candidate 后激活，要么依赖宽松阈值。目标 WAM 导向的 adversarial search 又容易针对单一模型过拟合并发生 score leakage。最小充分干预不是再训练一个预测器，而是先用动作诱导的物理影响结构缩小搜索空间，再在冻结 pair 后审计任意 WAM。

候选路线比较：

- **Route A（采用）**：模型盲的 influence-separated compiler。优点是贡献单一、证书独立于被测模型、可迁移到多个 WAM；风险是可能退化为 contact-aware fuzzing，必须靠匹配调用预算实验排除。
- **Route B（拒绝为主方法）**：直接最大化目标 WAM 的 ranking inversion 或 correction harm。它更容易找到反例，但会泄漏目标模型、降低跨方法解释力，只保留为“过拟合上界”对照。

## Method Thesis

- **One-sentence thesis**：从冻结 VLA 的自然轨迹中分离“对 factual 动作零影响、对 policy-supported candidate 有激活”的 simulator-native 物理参数块，可以在不读取目标 WAM 的情况下高效编译 feedback-interface-preserving、candidate-effect-diverging 的可审计反事实 twins。
- **Why this is the smallest adequate intervention**：唯一新增机制是参数块的动作条件影响筛选与证书生成；策略、任务、观测接口和后续 WAM 全部冻结或复用。
- **Why timely**：WAM 正从生成未来转向反馈纠错、候选选择和运行时干预，错误残差是否能跨动作迁移已直接影响控制；因此需要专门测这一接口，而不只是测视频质量。

## Contribution Focus

- **Dominant contribution**：ISRAC 编译算法与机器可验的 equality–activation–first-divergence 证书。
- **Optional supporting contribution**：一个严格隔离、post-hoc 的反馈 WAM correction-harm audit protocol；只有编译器主张通过后才启动。
- **Explicit non-contributions**：一般不可辨识性理论、新 WAM 架构、新策略训练、Depth/PointMap 表征、真实机器人安全保证。

## Proposed Method

### Complexity Budget

- **Frozen/reused**：StarVLA 或 π0.5 类策略、LIBERO/robosuite 任务、自然成功轨迹、候选 action chunks、渲染器和 simulator rollback。
- **New trainable components**：0。当前编译器是离线算法，不训练网络。
- **Intentionally excluded**：新视频生成器、几何 head、LLM planner、RL、端到端联合训练、触觉输入。

### System Overview

```text
冻结 VLA 成功轨迹
  └─ snapshot + factual chunk a_f + policy-supported candidate a_c
       └─ simulator-native 参数块/接触激活图
            └─ factual 零影响筛选 ∩ candidate 激活筛选
                 └─ 合法参数端点 θ⁺, θ⁻
                      ├─ factual twin replay → 完整动态转录必须相同
                      └─ candidate twin replay → 物理效果必须分叉
                           └─ 冻结、哈希、输出证书
                                └─ [后验阶段] 加载 held-out WAM 测纠错伤害
```

### Core Mechanism

给定可恢复 snapshot `s0`、factual 动作块 `a_f`、候选动作块 `a_c` 和 simulator-native 参数块 `b`，定义参数微扰下的动作条件影响：

```text
I_f(b) = D(X_f(θ+δ_b), X_f(θ-δ_b))
I_c(b) = D(E_c(θ+δ_b), E_c(θ-δ_b))
```

`X_f` 是 factual rollout 的逐帧**动态 simulator state**与观测转录；它不包含故意不同的静态物理参数。静态配置另行序列化和哈希。`E_c` 是候选动作后的任务相关物理效果，如对象位姿、接触事件、关节状态或碰撞状态。

ISRAC 只保留 `I_f` 不超过同参数重复回放噪声上界、且 `I_c` 大于预注册激活阈值的参数块。随后在同一个预注册合法参数区间中选择 `θ⁺/θ⁻`，最大化 candidate effect separation，同时强制 factual transcript equality。目标 WAM 的 residual、ranking 或 score 不进入筛选或求解目标。

每个 pair 输出：

1. snapshot、动作和静态参数配置哈希；
2. factual RGB、depth、proprio、动作与动态状态逐帧差异；
3. 同参数 repeat-noise 上界；
4. candidate 参数块激活帧；
5. candidate 首次物理分叉帧；
6. 合法参数范围与所有拒绝原因；
7. 目标 WAM 尚未加载的证明性运行元数据。

只有当 factual equality、candidate activation、first divergence 和 policy-support 四项同时成立时，才计为 certified pair。

### Modern Primitive Usage

- **Primitive**：冻结的大规模 VLA 仅作为 policy-supported action proposal source。
- **Exact role**：保证 candidate 来自真实策略支持，而非手写破坏动作；不训练、不微调，也不把语言模型用作搜索器。
- **Why appropriate**：研究对象是部署中实际由 VLA 提出的候选动作，而不是任意控制输入。编译器本身保持模型无关，避免用“更大模型”掩盖可辨识性问题。

### Integration and Inference

ISRAC 完全离线运行。它不会修改部署时策略：

1. 从冻结策略轨迹缓存选择可恢复边界和相邻候选；
2. 在 simulator 中编译并认证 pairs；
3. 在 pair 列表冻结、排序并哈希后才加载被测 WAM；
4. 对每个 world 使用同一 factual feedback，再评价同一 candidate bundle 的 corrected ranking、regret 和 harm；
5. 用真实 simulator rollback 作为环境级 ground truth。

### Training / Compilation Recipe

1. 预注册参数块、物理合法区间、动态状态字段、repeat-noise 阈值和 candidate effect 指标；
2. 对每个 snapshot 运行 factual/candidate sensitivity probes；
3. 依据 influence separation 选择参数块；
4. 使用固定小网格或约束求解生成 `θ⁺/θ⁻`；
5. 运行完整证书；失败样本与原因也落盘；
6. 与 random scene、candidate-contact、grid、CMA-ES/BO 在**相同 simulator calls**下比较；
7. 只有 matched-call gate 通过，才进行 GPU WAM audit。

### Failure Modes and Diagnostics

- **退化为 contact-aware fuzzing**：用 candidate-contact baseline 在相同参数值、块数、证书和 calls 下比较；再加 CMA-ES/BO 强基线。
- **动态状态定义偷换**：只把 rollout 动态量纳入 equality；故意变化的静态参数单独哈希并显式报告。
- **目标 WAM 泄漏**：pair manifest 在任何 WAM 加载前冻结；搜索日志不得包含 WAM score。
- **低支持候选动作**：候选必须由冻结策略生成，并通过控制限、工作空间和 rollback 可执行性检查。
- **阈值制造结果**：阈值来自同参数重复回放噪声；报告阈值扫描、连续效应和原始差异，不只报告 pass/fail。
- **任务脚本化**：参数块发现只依赖 simulator graph/contact trace；跨任务不允许手写 action index 条件。
- **第二平台失败**：若只能在 LIBERO 成立，论文主张降级为 benchmark engineering，不进入 WAM 泛化主张。

### Novelty and Elegance Argument

与 VLA metamorphic testing 相比，ISRAC 不对成功 rollout 施加预定义视觉/场景变换后检查整段行为，而是自动寻找“历史动态等价、未来 candidate 物理分叉”的原生物理 twin。与控制器 BO falsification/BEACON 相比，ISRAC 的搜索空间由 factual-zero/candidate-active 的动作条件影响结构定义，并输出适配反馈 WAM 接口的严格转录证书。与 Feedback WAM/CheckVLA 类方法相比，它不是另一个纠错器，而是独立于纠错器的反例编译与审计工具。

这一区别目前只是**条件新颖**：若匹配 calls 的 grid/CMA-ES/BO 达到相同 yield，或者影响筛选不提供稳定收益，ISRAC 不成立为方法贡献。

## Claim-Driven Validation Sketch

### Claim 1（主）：影响分离能高效编译合法 residual-alias twins

- **Minimal experiment**：LIBERO 中 8 个冻结策略边界、至少两个任务和两个机制族；ISRAC 与 random-scene、candidate-contact、grid/CMA-ES/BO 使用相同参数区间、证书和 simulator calls，3 个搜索种子。
- **Metric**：certified pairs / 1k rollouts、calls/pair、passing-block rate、首分叉与激活同帧率、失败原因分布；paired bootstrap 95% CI。
- **Decisive gate**：相对最强 baseline 的 yield ratio ≥2，95% CI 不跨 1；不是仅由单一任务或单一参数块贡献。第二 simulator 复现后才给 novelty >7 的最终判断。

### Claim 2（支持）：这些 pairs 对反馈 WAM 有特异性诊断价值

- **Minimal experiment**：在冻结、哈希的 pairs 上评价至少两个未参与编译的反馈 WAM 接口，以及 severity-matched 普通物理扰动负对照。
- **Metric**：false-transfer rate、candidate pairwise ranking accuracy、top-1 rollback regret、correction-harm rate、最终闭环成功率；未来预测误差只作辅助指标。
- **Decisive gate**：至少两种方法在 alias set 上的 harm/regret 显著高于普通扰动，且 uncorrected baseline 不出现等幅人为退化。

## Experiment Handoff Inputs

- **Must-prove claims**：C1 编译效率；C2 反馈纠错特异性（仅 C1 通过后）。
- **Must-run ablations**：去掉 influence-zero 筛选；candidate-contact；random/grid；CMA-ES/BO；宽松 equality 阈值；target-WAM-aware 过拟合上界。
- **Critical tasks/metrics**：多任务自然成功轨迹、接触/关节/几何至少两类机制；pair yield、证书违规率、ranking regret、correction harm。
- **Highest-risk assumptions**：物理参数块可跨 simulator 抽象；自然策略候选能激活足够多的零历史影响参数；本地可用的 feedback WAM checkpoint 与 LIBERO 接口兼容。

## Compute & Timeline Estimate

- **编译器 E0**：CPU 约 24–48 小时，GPU 0 小时；现有 4×A100 不会加速 MuJoCo/OSMesa rollback。
- **通过后 WAM audit**：预计 1–4 张 A100 共 24–72 GPUh，取决于是否已有兼容 checkpoint；每次启动前重新检查 GPU 空闲条件。
- **数据/标注**：复用冻结策略轨迹和 simulator state，无人工动作标注；所有资产留在个人目录。
- **阶段停机**：matched-call 最强 baseline 等效或更好、第二机制/平台无法复现、或 target-WAM leakage 无法排除时停止该 Idea。
