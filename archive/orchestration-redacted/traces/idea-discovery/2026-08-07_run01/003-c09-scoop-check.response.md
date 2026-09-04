# Verdict

**PARTIAL；对应 Level 2 — High Overlap（高重叠，未完全被抢）**。

截至 2026-08-07，没有发现论文完整覆盖以下链条：

> 在独立 episode/temporal holdout 上先验证 action-conditioned predictor 超过 persistence 与同容量 action-agnostic predictor，并通过 action-shuffle 检验；冻结阈值后，才允许该 world objective 进入等预算 VLA policy co-training；再用受控 validity strata 检验该严格有效性是否预测闭环策略迁移。

但组成思想已有强先例。尤其是：

- `Hallucination in World Models` 已同时采用重复末帧基线、action-shuffle ratio、held-out trajectories 和 downstream MPC。
- `dWorldEval` 已用可控 action corruption strata 证明 action adherence 与真实 policy-ranking reliability 同步下降，并明确称其为可靠评估的前提。
- `ForkMerge` 已占据“验证后将有害 auxiliary 权重置零”的通用机制。
- 世界模型 checkpoint selection 与 Objective Mismatch 已占据“离线 world metric 是否预测 downstream control”的科学问题。

因此，C09 唯一仍清楚存活的轴是：**这些诊断是否能预测 predictive auxiliary 对 VLA 参数更新的迁移，而不是 world model 自身作为 simulator/evaluator/planner 的效用。**

# Delta

不同于 `Hallucination in World Models` 和 `dWorldEval` 用 action sensitivity、持久性/视觉误差来判断世界模型能否可靠地执行 MPC 或代理评估，C09 在等预算 VLA 辅助训练前冻结一个 action-specific strict-validity 准入规则，并跨独立构造的 predictor-quality strata 检验该规则是否预测闭环策略迁移的方向与幅度。

# Decomposed claim

- **Problem framing：** 决定预测性 world objective 何时有资格进入离线 VLA policy training，并检验严格 world validity 与 policy transfer 的关系。

- **Core mechanism：** episode/temporal holdout；相对 persistence 和同容量 action-agnostic predictor 的增益；same-task/stage-matched action shuffle；bootstrap 下界超过预注册阈值；数据量、checkpoint maturity、horizon corruption 等产生 validity strata。

- **Key insight：** world loss 下降或标准 split 性能并不能证明模型学习了 action-specific dynamics，也不能保证该监督对 action policy 有正迁移；需要把 action-conditioned generalization 与 downstream transfer 显式关联。

- **Application domain：** 机器人 manipulation 中训练时使用、部署时移除的 VLA/WAM predictive auxiliary supervision。

# Search queries and sources

核心查询：

1. `action-conditioned world predictor strict temporal holdout persistence action-agnostic action shuffle policy transfer`
2. `world model reliability model selection auxiliary task validation gating`
3. `predictor validity auxiliary task admission transfer action shuffle sensitivity vision-language-action`

定向补充查询包括：

- `"persistence" "action-agnostic" "action shuffle" world model`
- `"world validity" "policy transfer" predictor`
- `world model predictive accuracy downstream policy performance objective mismatch`
- `ForkMerge safe auxiliary learning validation gating`
- `PCGrad CAGrad auxiliary negative transfer`
- `world model uncertainty trust gating offline RL`
- `VLA WAM action perturbation action-sensitive future prediction`

跨索引发现阶段得到 83 个去重结果；Semantic Scholar 三次请求均因 HTTP 429 失败，OpenReview/DBLP 在宽查询中为零命中。最终判断只采用已在 arXiv 全文、OpenReview、PMLR、NeurIPS proceedings 上重新核实的一手来源。

# Structured papers

| 工作 | 核心重叠 | 决定性差异 | 轴重叠 | 分类 |
|---|---|---|---:|---|
| [Hallucination in World Models is Predictable and Preventable](https://arxiv.org/abs/2606.27326), 2026-06 | held-out trajectories；重复末帧基线；action-shuffle ratio；多种训练/数据质量；downstream MPC | world model 直接用于 MPC；没有 VLA auxiliary admission、action-agnostic predictor 或预注册 gate | 3/4 | 强 partial collision |
| [dWorldEval](https://arxiv.org/abs/2604.22152), 2026-04 | action shuffle、连续 corruption strata、world diagnostic 与真实 policy-ranking correlation | 研究代理 policy evaluation，而不是 world gradient 对 policy learning 的迁移；没有 persistence/action-agnostic 双基线 | 3/4 | 强 partial collision |
| [Predicting Closed-Loop Performance of Latent World Models](https://arxiv.org/abs/2607.01736), 2026-07 | 100 个 checkpoints；离线结构指标预测 MPC/A2C；普通 validation/RMSE 失效 | 单一 LunarLander；使用 CROF/ROF；没有 VLA auxiliary co-training 或 action-shuffle gate | 2/4 | partial collision |
| [ForkMerge](https://openreview.net/forum?id=vZHk1QlBQW), NeurIPS 2023 | 根据 target validation performance 在 auxiliary-only/joint 分支间合并，强负迁移时令权重为零 | gate 看的是 target validation，而非先验 world validity；训练中动态分叉，不是预训练 predictor 准入 | 3/4 | 通用机制强近邻 |
| [Adaptive Auxiliary Task Weighting for RL](https://proceedings.neurips.cc/paper/2019/hash/0e900ad84f63618452210ab8baae0218-Abstract.html), NeurIPS 2019 | 用 auxiliary gradient 的长期主任务效应动态学习权重；含机器人 RL | 需要先实际施加 auxiliary；不验证 predictive semantics | 2/4 | partial/adjacent |
| [Auto-Lambda](https://arxiv.org/abs/2202.03091), 2022 | validation meta-loss 自动调节 auxiliary 权重；含 robotics | 是通用 bi-level weighting，不定义 world-model validity | 2/4 | adjacent |
| [Objective Mismatch in Model-based RL](https://proceedings.mlr.press/v120/lambert20a.html), L4DC 2020 | 明确证明 one-step likelihood 与 downstream control 可能不相关 | MBRL simulator/planning；无 admission gate 和 VLA auxiliary | 2/4 | foundational precedent |
| [SelfWAM](https://arxiv.org/abs/2608.00725), 2026-08 | action-unconditioned control、方向性 action perturbation、future metric 与 policy ablation | RoboTwin future analysis明确不是 held-out generalization；action-conditioning alone 的 policy 平均值反而从 91.84 降至 90.80；无 validity strata/gate | 2/4 | WAM 强近邻 |
| [WorldArena](https://arxiv.org/abs/2602.08971), 2026-02 | 系统揭示 perceptual quality 与 functional utility 的 gap | 是 benchmark，不测试预测监督进入 VLA 后的参数迁移 | 2/4 | adjacent |
| [World Action Verifier](https://arxiv.org/abs/2604.01985), 2026-04 | 用 forward/inverse asymmetry 验证 action-conditioned world predictions，并报告 downstream policy 改善 | verifier 用于主动收集和修复 world model，不是 auxiliary admission | 2/4 | adjacent |
| [Fast-WAM](https://arxiv.org/abs/2603.16666), 2026-03 | future-video 只在训练期作为辅助监督、部署时移除 | 默认接纳 world objective，没有严格 validity gate | 1/4 | WAM precedent |
| [PCGrad](https://proceedings.neurips.cc/paper/2020/hash/3fe78a8acf5fda99de95303940a2420c-Abstract.html), NeurIPS 2020 | 防止多任务梯度冲突 | 局部梯度几何不能证明 auxiliary 的语义有效性或长期迁移 | 1/4 | adjacent |
| [CAGrad](https://proceedings.neurips.cc/paper/2021/hash/9d27fdf2477ffbff837d73ef7ae23db9-Abstract.html), NeurIPS 2021 | conflict-averse 多目标优化 | 优化平均任务损失，不做 predictor validity 或准入 | 1/4 | adjacent |
| [MOPO](https://proceedings.neurips.cc/paper/2020/hash/a322852ce0df73e204b7e67cbbef0d0a-Abstract.html) / [MOReL](https://proceedings.neurips.cc/paper/2020/hash/f7efa4f864ae9b88d43527f4b14f750f-Abstract.html), NeurIPS 2020 | uncertainty/pessimism 限制不可信 model rollouts | 按 state-action 区域局部限制 model use，不决定 auxiliary gradient 是否进入 VLA | 1/4 | uncertainty-gating precedent |
| [MACURA](https://proceedings.mlr.press/v235/frauenknecht24a.html), ICML 2024 | 根据模型 uncertainty 自适应 rollout length，回答“哪里可信” | 在线局部 rollout gating；无严格 holdout transfer study | 1/4 | adjacent |

# Comparison result

- **Proposed work**
  - Problem framing: predictive objective 进入 VLA policy training 前的严格准入与 validity-transfer 检验。
  - Core mechanism: persistence/action-agnostic/shuffle 三重诊断、严格 holdout、冻结阈值、受控 validity strata。
  - Key insight: action-specific strict validity 可能是辅助监督正迁移的必要但非充分条件。
  - Application domain: 离线机器人 VLA predictive auxiliary co-training。

- **Hallucination in World Models**
  - Problem framing: 检测 world-model hallucination 并判断其 downstream MPC utility。
  - Core mechanism: last-frame repetition、action-shuffle ratio、held-out sequences、data/finetuning strata。
  - Key insight:视觉流畅不等于 action-controllable dynamics。
  - Application domain: 210 个连续控制与 manipulation 任务。
  - Comparison: **3 axes match → Level 2, High Overlap；仅 auxiliary-to-VLA transfer 轴不同。**

- **dWorldEval**
  - Problem framing: 判断 world model 能否可靠代理机器人 policy evaluation。
  - Core mechanism: same-test-set action permutation、连续 swap probability、真实/估计 success ranking correlation。
  - Key insight: action adherence 是可靠 downstream use 的前提。
  - Application domain: LIBERO、RoboTwin、真实机器人。
  - Comparison: **3 axes match → Level 2, High Overlap；policy evaluation 与 policy training 不同。**

- **ForkMerge**
  - Problem framing: 防止 auxiliary-task negative transfer。
  - Core mechanism: target-only/joint 分支，验证集选择合并系数，严重负迁移时令辅助权重为零。
  - Key insight: gradient conflict 不足以判断 auxiliary-target generalization。
  - Application domain: 通用 auxiliary learning。
  - Comparison: **3 axes match → Level 2, High Overlap；gate 的证据变量不同。**

- **Predicting Closed-Loop Performance of Latent World Models**
  - Problem framing: 从 validation diagnostics 预测 closed-loop performance。
  - Core mechanism: 100 checkpoints、40 个指标、CROF checkpoint selection。
  - Key insight: validation loss/RMSE 可持续改善而 control 崩溃。
  - Application domain: LunarLander RSSM/MPC/A2C。
  - Comparison: **2 axes match → Level 3, Medium Overlap。**

- **SelfWAM**
  - Problem framing: 让 WAM future prediction 真正依赖 action，并改善 policy。
  - Core mechanism: clean-action condition、self-mask target、directional perturbation。
  - Key insight: action conditioning 和 action-relevant target 不等价于普通 future RGB。
  - Application domain: RoboTwin 与真实机器人。
  - Comparison: **2 axes match → Level 3, Medium Overlap。**

- **Adaptive Auxiliary Task Weighting**
  - Problem framing: 选择真正帮助 RL 主任务的 auxiliary。
  - Core mechanism: 在线 meta-gradient/long-term main-loss effect。
  - Key insight: auxiliary usefulness 应由主任务长期效应定义。
  - Application domain: Atari 与模拟机器人 manipulation。
  - Comparison: **2 axes match → Level 3, Medium Overlap。**

- **Objective Mismatch**
  - Problem framing: prediction objective 与 downstream control objective 的失配。
  - Core mechanism: 对多种 dynamics models 比较 likelihood 与 control performance，并重加权模型训练。
  - Key insight:更准确的全局模型不一定带来更好控制。
  - Application domain: continuous-control MBRL。
  - Comparison: **2 axes match → Level 3, Medium Overlap。**

最坏情况为 **Level 2 — High Overlap**，因此映射到用户要求的结论是 **PARTIAL，而非 NOVEL 或 SCOOPED**。

# Narrowest defensible claim

最窄且仍可辩护的表述是：

> 在等初始化、数据、参数、步数和近似 FLOPs 的离线 VLA auxiliary co-training 中，一个预注册的 action-specific strict-generalization score——由 episode/temporal holdout 上相对 persistence、同容量 action-agnostic predictor 的增益及 same-task action-shuffle sensitivity 共同构成——能否跨独立生成的 predictor-quality strata 预测闭环 policy transfer 的符号和幅度，而普通 validation loss 不能。

不要声称：

- 首次提出 action shuffle、persistence baseline 或 world-model reliability；
- 世界有效性普遍保证正迁移；
- gate 是充分条件或通用安全保证；
- 仅凭一次“过门 predictor 优于 action-only”证明 validity-transfer 关系。

# Method or diagnostic finding?

应定位为 **诊断性科学发现 + 预注册评估/准入协议**，不是新的优化方法。

硬 `if score > threshold: λ>0` 本身已被通用 validation gating、ForkMerge、模型选择和 uncertainty gating 包围。除非引入有理论校准、风险控制或跨任务可迁移阈值的非平凡算法，否则将其包装为“新方法”很脆弱。

# Minimum evidence needed

1. **独立阈值校准。** predictor training、gate calibration、locked strict test、final policy evaluation 至少逻辑上四分；现有 strict cache 不能同时选阈值和充当最终证据。

2. **至少 4 个 predictor strata。** 只做 valid/invalid 两点不能支持关系或 threshold effect。应至少有 4–6 个 predictor instances，并由不少于两种正交手段构造，例如 checkpoint maturity 与 horizon corruption，避免 validity 只代理训练时长。

3. **真正的 action-agnostic control。** 与 action-conditioned predictor 同架构、容量、数据、优化和 target；不是简单移除 action 后得到一个更弱模型。

4. **policy treatment 完全匹配。** 初始化、训练样本顺序、action loss、auxiliary target tokens、参数量、更新步数和 FLOPs 都需一致；同时报告 dummy-head/random-target control。

5. **检验连续关系而不只二值过门。** 预注册 validity→transfer 的斜率、符号或单调趋势，以及标准 split/world loss 的竞争解释；统计单位是 predictor checkpoint/stratum，而不是把大量 episode 当作独立 predictor 样本。

6. **至少一个独立有效 predictor。** 如果没有 predictor 同时超过 persistence、action-agnostic 且表现 shuffle sensitivity，则必须终止正向 policy 实验。

7. **多任务、seed 和闭环结果。** 单任务单 seed 只够 pilot；最低可信结果需要多个任务、每个 policy arm 多 seed，并对 rollout success 做 paired/clustered uncertainty。

8. **prospective gate test。** 在阈值冻结后，对未参与阈值制定的新 predictor 或新任务预测“接纳/拒绝”，再观察 downstream transfer；否则只是事后相关分析。

# Fatal risks

- **内部识别矛盾：** 如果 invalid predictor 永远令 `λ=0`，则 downstream 差异同时改变了 predictor validity 和 treatment intensity，无法检验“validity 是否预测 transfer”。要研究该关系，必须在隔离的诊断臂中让若干 invalid/low-validity predictors 以相同非零权重进入 policy；它们可以标为负控，不能当正方法。若坚持完全不训练 invalid branch，只能测试 gate 的操作性，不能建立 validity-transfer 曲线。

- **通用性/新颖性：** `Hallucination` 已占据 persistence + action shuffle + downstream control，`dWorldEval` 已占据 action corruption→policy reliability，ForkMerge 已占据 auxiliary validation rejection。C09 必须把贡献压缩到 **VLA auxiliary-gradient transfer**。

- **validation overfit：** 反复使用 strict holdout 选择 predictor、阈值、strata 和论文 claim 会把“strict”变成新的训练集。需要 nested/locked holdout 和 predictor-level multiple-testing 控制。

- **有效 predictor 依赖：** 当前本地 F 严格失败；若无法得到一个真实过门 predictor，不能验证正迁移，只能报告资产/设定下的失败性诊断。

- **混杂：** data amount、maturity、corruption 同时改变 representation quality、optimization stability、output variance 和 target difficulty。必须做 within-family、matched corruption 或多种独立构造，否则相关性无法归因于 validity。

- **必要但非充分：** Objective Mismatch、WorldArena 和 2026 checkpoint-selection 工作均说明预测质量与控制可能脱钩。即使严格 validity 有必要性，也可能无法预测 auxiliary transfer。

- **阈值脆弱：** 小样本 bootstrap 下界、metric scaling、horizon 和 task mix 都可改变过门结果；硬二值化还会丢失连续关系。

- **预算：** 8 GPUh 也许足够做一个“是否存在过门 predictor”的 falsification pilot，但不足以同时覆盖 4–6 strata、matched policy arms、多 seed 和闭环 rollouts。当前预算下很难支撑 paper-level validity-transfer claim。

结论：C09 未被完全 scoop，但现有表述过宽。若不能解决“invalid strata 不能进入 policy、却又要估计 transfer relationship”的识别矛盾，它会退化成通用工程 gate；解决后，最有价值的产物仍是一个 VLA-specific diagnostic finding，而不是新优化算法。
