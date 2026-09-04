# ISRAC 文献证据图（2026-08-31）

## 检索问题与边界

ISRAC 不是新的 residual correction 算法。它要检验的是：当反馈式 WAM 把已执行动作的预测残差迁移到另一个尚未执行的候选动作时，单一 factual feedback interface 是否足以决定候选动作下的正确修正方向。拟保留的新颖性只限于：

> 从冻结 VLA 的自然成功轨迹出发，自动寻找对 factual action 的完整可观测反馈完全相同、但对 future candidate 的物理效果不同的 simulator-native twin worlds，并输出逐帧一致性、影响激活和首次分歧的机器证书。

不主张以下内容是新的：世界模型会出错、模型可被 planner 利用、反事实分支、metamorphic testing、随机 simulator fuzzing、two-point non-identifiability lower bound、在线 residual correction 或候选动作重排序。

检索覆盖 2018--2026，近期重点为 2023--2026。证据来源包括：项目本地 48 篇 PDF 中与本问题最相关的原文首页/摘要/方法段；2026-08-31 的 OpenAlex、Crossref 和 Semantic Scholar 查询；项目同日保存的查新快照。arXiv API 在本轮因 TLS EOF 失败，Semantic Scholar 部分查询出现 HTTP 429，因此“未发现精确同构工作”只能是条件性结论，不能写成绝对不存在。

## 直接近邻：反馈、验证、修复与 exploitation

| 工作 | 它真正解决的问题 | 与 ISRAC 的重叠 | ISRAC 必须守住的差异 | 证据 |
|---|---|---|---|---|
| [Feedback World Model](https://arxiv.org/abs/2605.15705) (2026, preprint) | 把真实观测与传播状态的 latent residual 作为在线反馈，修正当前 world-model state/velocity，并引导动作生成 | **最高机制威胁**：factual residual 被用于后续动作决策；generic residual correction 已被占据 | ISRAC 不提出另一个 correction head；它生成 action-separated counterexamples，检查同一 residual 对不同 candidate 的迁移是否可识别 | 项目同日原文机制核验：Sec. 4.2--4.3 / Eqs. 8--16 |
| [ReDRAW](https://arxiv.org/abs/2504.02252) (2025, preprint) | 用少量目标域数据训练 `delta(z,a)` 修正冻结 source latent dynamics，再在修正后的 imagined dynamics 中优化 actor--critic | residual dynamics adaptation 已有；动作条件 residual 也不是新点 | ISRAC 的对象是测试/证伪样本编译器，不学习 `delta`，且必须在编译时看不到被测 WAM score | 项目同日原文机制核验 |
| [When to Trust Imagination](https://arxiv.org/abs/2605.06222) (Wang et al., 2026, preprint) | 用 FFDC 比较预测未来、真实观察、动作和语言，决定继续执行还是提前 replanning | 使用 prediction--reality discrepancy 触发反馈控制 | 它不检验“相同 factual discrepancy 对另一个候选动作是否意味着相同修正”；ISRAC 也不把 replan 本身当创新 | 本地 PDF 原文 |
| [CheckVLA](https://arxiv.org/abs/2607.26789) (Liu et al., 2026, preprint) | 冻结 action-conditioned WM 做在线风险检测、conformal 触发、action suffix rewrite 和 re-anchor | execution-time verification/correction 已被直接占据 | ISRAC 只可声称生成 matched residual-alias stress tests，并测 unnecessary/wrong interventions；不能声称首个 WAM 纠错 VLA | 本地 PDF 原文 |
| [DREAM-Chunk](https://arxiv.org/abs/2606.18589) (Chen et al., 2026, preprint) | 采样多个 action chunks，用 latent futures 与真实 rollout 对齐，运行时切换 chunk | 候选动作 + latent WM + 真实反馈接口已有 | ISRAC 不提出 chunk switching；检查 feedback 是否错误地跨 candidate 泛化 | 本地 PDF 原文 |
| [tau0-WM](https://arxiv.org/abs/2606.01027) (Zhou et al., 2026, preprint) | 联合 video-action model、action-conditioned simulator、progress scorer，用 re-denoising 选择/rectify candidates | WAM rollout 排序与 rectification 已被占据 | ISRAC 的 novelty 不得写成 candidate reranking；它是 WAM-blind counterexample compiler | 本地 PDF 原文 |
| [World Action Verifier](https://arxiv.org/abs/2604.01985) (Liu et al., 2026, preprint) | 用 state plausibility 与 action reachability 的 forward--inverse asymmetry 自验证和自改进 WM | “修正 WAM 预测错误”和 under-explored actions 已被占据 | ISRAC 不修复模型；其证书要求真实 simulator action effect divergence，而非 cycle consistency | 本地 PDF 原文 |
| [Imperfect World Models are Exploitable](https://arxiv.org/abs/2605.15960) (Bhamidipaty et al., 2026, preprint) | 形式化 model-induced policy preference reversal，并证明大 policy set 上 exploitation 基本不可避免 | 直接占据 ranking inversion / exploitation 的一般理论 | ISRAC 只能贡献自动产生 embodied、matched、可复现的 witness；不能把 preference reversal 当理论新颖性 | 本地 PDF 原文 |
| [RENEW](https://arxiv.org/abs/2607.14180) (Bhamidipaty et al., 2026, workshop preprint) | 用 human preferences 直接修复 imagined dynamics 中可利用的错误，并用 epistemic uncertainty 选 query | 自动寻找/修复 exploitable region 相邻 | RENEW 的目标读 world-model uncertainty/preferences；ISRAC 编译过程禁止读取目标 WAM，并验证 held-out feedback methods | 本地 PDF 原文 |
| [Uncertainty-aware Latent Safety Filters](https://arxiv.org/abs/2505.00779) (Seo et al., CoRL 2025) | ensemble epistemic uncertainty + conformal OOD threshold + latent reachability filter | “对不可信 imagination 做安全过滤”已被占据 | ISRAC 不提出 uncertainty gate；其 paired worlds专门检验同一可观测反馈下的 action-dependent ambiguity | 本地 PDF 原文 |
| [Planning and Execution using Inaccurate Models with Provable Guarantees](https://www.roboticsproceedings.org/rss16/p001.html) (Vemula et al., RSS 2020) / [CMAX++](https://doi.org/10.1609/aaai.v35i7.16765) (AAAI 2021) | 在线发现 model discrepancies 后绕开不准确 transition；后者跨重复任务利用经验 | 历史 discrepancy 的跨时间使用与 inaccurate-model control 已成熟 | ISRAC 必须实证 residual 的错误跨动作运输，而不是泛称“历史误差不能泛化” | 本地 PDF 原文 |

## 直接近邻：测试、反例生成与物理 paired worlds

| 工作族 | 已有能力 | 对 ISRAC 的威胁 | 尚未在本轮证据中发现的组合 |
|---|---|---|---|
| [Metamorphic Testing: Testing the Untestable](https://doi.org/10.1109/MS.2018.2875968) (Segura et al., IEEE Software 2018) 及 adaptive / feedback-directed MT | 通过 source/follow-up inputs 与 metamorphic relations 在无完整 oracle 时发现错误；已有自动/自适应 MR 搜索 | “成对世界 + 关系证书”本身不是新测试范式 | 针对反馈式 WAM 的 **factual-interface equality + candidate-only physical influence activation + first-divergence certificate** |
| [Metamorphic Testing of Vision--Language Action--Enabled Robots](https://arxiv.org/abs/2602.22579) (2026, preprint) | 固定 seed，对任务/环境做 controlled transformations，检查成功率和轨迹应保持或应变化 | VLA paired testing 已几乎直接占据；若其补充材料已有 snapshot restore、native physics parameter blocks 和跨 action equality，ISRAC 新颖性会显著下降 | 当前已核验材料显示它比较 transformation 下的 VLA behavior，不保持一个 action 的完整反馈接口后再让另一个 candidate 分歧 |
| [Verifying Controllers Against Adversarial Examples with Bayesian Optimization](https://doi.org/10.1109/ICRA.2018.8460635) (Ghosh et al., ICRA 2018) | 用 Bayesian optimization 寻找控制器反例 | 自动反例搜索、simulator falsification 不新 | WAM-blind influence-zero screening 是否能在匹配 calls 下优于 BO/CMA/grid 必须实验，而不能靠定义取胜 |
| [BEACON](https://doi.org/10.1109/ACCESS.2024.3436515) (Yancosek & Baheri, IEEE Access 2024) | Bayesian evolutionary counterexample generation for control systems | evolutionary counterexample generation 是强 baseline | ISRAC 必须用相同 simulator calls 比较 yield/calls-per-pair |
| [Counterexample-Guided Synthesis of Perception Models and Control](https://doi.org/10.23919/ACC50511.2021.9482896) (Ghosh et al., ACC 2021) | 反例驱动地联合 perception/control synthesis | 反例可用于改进感知和控制并不新 | ISRAC 当前只允许 diagnostic compiler claim；后续若训练模型需与 CEGIS 区分 |
| [Using Constraint Solvers to Support Metamorphic Testing](https://doi.org/10.1109/MET.2019.00013) (de Castro-Cabrera et al., MET 2019) | 用约束求解生成/支持 metamorphic tests | “compiler + constraint”措辞不能自动构成新颖性 | 物理 influence graph、factual zero-effect 与 candidate activation 必须是不可被 random/solver baseline 替代的核心 |
| [Automated Inference of Expressive Metamorphic Relations](https://doi.org/10.1109/ICST69053.2026.00016) (Nolasco, ICST 2026) | 自动推断 metamorphic relations | 自动关系发现削弱“自动生成测试关系”的广义 claim | ISRAC 应冻结 relation schema，只自动定位物理参数块和边界；不要声称首个自动 MR inference |

## 支持性但不构成新颖性的证据

| 工作 | 支持的事实 | 不能据此声称什么 |
|---|---|---|
| [WorldEval](https://arxiv.org/abs/2505.19017) (Li et al., 2025, preprint) | learned world simulator 可用于 policy/checkpoint 排序，但 action following 是关键难点 | 不能推出 learned ranking 对 counterfactual candidates 可靠 |
| [Foundational World Models Accurately Detect Bimanual Manipulator Failures](https://arxiv.org/abs/2603.06987) (Ward et al., 2026, preprint) | latent WM uncertainty 可用于 failure monitoring | failure detection 不等于 error attribution 或跨动作 residual identifiability |
| [Foresight](https://arxiv.org/abs/2606.23085) (Zhang et al., 2026, preprint) | action-conditioned WM latents + conformal calibration 可做长时 failure detection | 不能证明 residual 可迁移到另一个候选动作 |
| [Efficient Imitation Learning with Conservative World Models](https://proceedings.mlr.press/v242/kolev24a.html) (Kolev et al., L4DC 2024) | model bias 与额外 distribution shift 需要保守目标 | 不能把保守/uncertainty penalty 当 ISRAC 方法贡献 |

## 证据综合与条件性 novelty verdict

1. **普通的 WAM 纠错已经被做了。** FWM、ReDRAW、CheckVLA、DREAM-Chunk、tau0-WM 和 WAV 分别覆盖了 residual feedback、offline dynamics adaptation、runtime verification/suffix repair、chunk switching、pre-execution rectification 与 self-verification。因此 ISRAC 不能再以“修正 WAM 错误”为主贡献。
2. **model exploitation 与 ranking inversion 也不是空白。** 2026 的理论和实证工作已经明确讨论 optimizer 利用不完美模型。ISRAC 的价值只能是构造目前方法难以逃避的、物理上配对且可审计的 embodied witnesses。
3. **paired testing / counterexample generation 是成熟领域。** Metamorphic testing、Bayesian/evolutionary falsification、constraint-supported testing 都是强先例。ISRAC 是否超过“为 VLA/WAM 写了一个新的 metamorphic relation”，完全取决于 influence separation 在同等 simulator-call 预算下能否显著提高严格合格 pair 的产率，并能否暴露未参与编译的多个反馈方法的 correction harm。
4. **本轮没有找到精确包含全部四项的已验证工作：** (a) 冻结自然 VLA 轨迹；(b) factual 完整反馈接口逐帧相等；(c) future candidate 才激活的 simulator-native physical parameter；(d) 机器可验的 activation/first-divergence 证书。但数据库访问受限，两个 2026 年被提名的理论近邻未获得可核验全文，因此这不是“确定没人做过”的结论。

当前严格判断：**条件性可做，provisional novelty 7.1/10（合理区间 6.4--7.7）**。只有当下面三个门同时通过，才能维持大于 7 的主张：

- matched-call ISRAC yield 至少为最强 random/grid/CMA/BO baseline 的 2 倍；
- 至少两个 simulator-native mechanism family、多个任务、无任务专用代码；
- 至少两个未参与编译的 feedback-WAM 接口在 alias set 上呈现显著高于普通 perturbation set 的 correction harm / ranking inversion。

若 matched baseline 等效，ISRAC 应降级为 **WAM/VLA metamorphic benchmark engineering（约 6.3--6.7）**；若 feedback methods 不受这些 pairs 影响，则保留 simulator diagnostic artifact，放弃 WAM correction-harm 主张。

## 下一证据门

先运行匹配预算的 compiler baselines。此门只使用缓存的冻结 StarVLA 成功轨迹和 MuJoCo rollback，不训练 5B WAM。通过后才启动 GPU WAM 推理/最小接口复现；未通过则停止当前 Idea，避免用算力掩盖方法贡献不足。
