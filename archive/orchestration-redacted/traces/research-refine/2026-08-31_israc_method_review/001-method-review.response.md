CALIBRATION: none

未提供可用于事先定标的 known-good / known-bad 历史 proposal；以下分数是独立顶会 reviewer 判断。此前已经产出的 24 pairs，以及正在运行但尚未完成的 random/contact baseline，只计作工程可行性证据，不计作方法成立、效率优势或新颖性证据。

## Scores

| Dimension | Score | Review |
|---|---:|---|
| Problem Fidelity | 9/10 | Problem Anchor 保持得很好。方法始终针对“同一 factual feedback 无法识别另一 candidate 的正确物理修正”这一瓶颈，没有漂移成新 WAM、一般安全验证或 VLA robustness benchmark。 |
| Method Specificity | 6/10 | 输入、输出和阶段顺序已经明确，但真正决定 ISRAC 是否是“方法”而不是 contact-aware rejection sampling 的算法仍不够精确。`I_f/I_c` 是定义，不是尚可区分于 baseline 的搜索算法；参数块如何从 simulator graph 得到、一次 probe 如何计费、`D` 如何跨异质 state 字段聚合、candidate effect 如何避免任务手写、`θ⁺/θ⁻` 如何唯一选出，仍有多种未定实现。 |
| Contribution Quality | 6/10 | 单一主贡献和零新训练模块值得肯定，但当前贡献边界仍容易被审稿人压缩成“为 VLA/WAM 写了一个新的 metamorphic relation，再用接触信息加速 fuzzing”。只有把 action-conditioned influence set difference 明确定义成可复现的搜索原语，并证明收益来自该原语而非一般约束搜索，才是机制级贡献。 |
| Frontier Leverage | 8/10 | 冻结 VLA 只负责提供 policy-supported candidates，角色自然且克制。这里不需要额外 LLM、RL、视频生成或可训练 critic；不堆现代模块反而是优点。 |
| Feasibility | 7/10 | 现有四任务、六个通过边界和 24 pairs 说明 rollback、参数干预和证书链路基本可实现。但它们尚未证明独立边界覆盖、搜索效率、第二机制泛化或 blind WAM audit。 |
| Validation Focus | 8/10 | 两个 claim、先 C1 后 C2、硬停机门槛都合理。主要风险不是实验太少，而是当前 pair 计数可能由同一 boundary/block 的多个相关 `θ` 端点膨胀，以及 matched-call 成本核算尚未完全锁死。 |
| Venue Readiness | 6/10 | 故事清楚、及时且简洁，但顶会目前会问两个致命问题：它和 candidate-contact / constraint-guided fuzzing 的算法差异到底是什么，以及 2× yield 是否在公平计入 graph/probe/certification 成本后仍成立。当前 proposal 还不能回答。 |

**Weighted OVERALL SCORE: 6.95/10**

计算：

\[
0.15(9)+0.25(6)+0.25(6)+0.15(8)+0.10(7)+0.05(8)+0.05(6)=6.95.
\]

## GAP

距离 READY 的核心差距不是更多任务、更多模型或更多 benchmark，而是三个定义与方法身份问题尚未封闭：第一，`dynamic state equality` 与静态 physics difference 必须成为严格、枚举字段的证书规范，而不是自然语言排除项；第二，compiler artifact 与 WAM-dependent residual audit 必须在接口和数据流上物理隔离，不能只靠“尚未加载”的日志声明；第三，必须给出一个 candidate-contact baseline 不具备的、明确降低搜索调用的 influence-separation 算法。目前的“先做 factual/candidate sensitivity probes，再筛选”可能已经花掉与黑盒 baseline 相同甚至更多的调用，并且 candidate-contact baseline 很可能实现几乎相同的筛选。若不解决这一点，即使找到很多 pair，贡献仍会停留在精心设计的 MT/fuzzing 工程。

## 低于 7 分项的具体修复

### Method Specificity — 6/10

**具体弱点**

`I_f(b)` 与 `I_c(b)` 只描述合格条件，没有定义 ISRAC 特有的计算路径。当前 recipe 同时保留“小网格或约束求解”，使核心算法不唯一；参数块发现又混合 graph/contact trace 与有限差分 probes，无法判断效率来自何处。

**方法级修复 — CRITICAL**

把核心算法收敛为唯一的四步算子：

1. 在 nominal `θ₀` 下分别只回放一次 `a_f` 和 `a_c`，记录 simulator-native dependency/activation trace。
2. 定义候选参数集合  
   \[
   B^\star=\operatorname{Ancestors}(E_c,a_c)\setminus
   \operatorname{Ancestors}(X_f,a_f),
   \]
   即 candidate-effect 的物理祖先减去 factual-transcript 的物理祖先。
3. 只对 `B*` 中的 block 做预注册合法端点 probes；选择规则固定为 deterministic endpoint sweep 或固定层数二分，不能在主方法中继续“grid 或 solver 二选一”。
4. 对所得 pair 运行完整 certificate；graph false negative 可以接受并计入 coverage，但不得事后用 WAM score 回补。

这样 ISRAC 的机制是“action-conditioned dependency-set difference 先验剪枝”，而不是“找到符合两个不等式的任何优化器”。

同时必须明确：

- 每种 simulator 的 block schema 如何从 body–joint–surface–contact graph 自动导出；
- `D` 是逐字段 hard predicate，而不是把 metre、quaternion、contact bit 混成一个标量；
- `E_c` 优先使用 task-independent physical event vector，例如对象 SE(3)、joint displacement、contact onset/impulse、collision bit；task success 只能作后验标签；
- 所有 nominal traces、endpoint probes、失败 certificate replay 都计入 simulator-call budget。

### Contribution Quality — 6/10

**具体弱点**

当前 dominant contribution 仍可被等价描述为“candidate-active 且 factual-invariant 的 metamorphic relation + constrained fuzzing”。此外，raw pair yield 容易因同一 boundary/block 产生多个相近 `θ⁺/θ⁻` 而被人为放大。

**方法级修复 — CRITICAL**

把论文主张收窄成：

> Action-conditioned dependency-set subtraction is a simulator-native search primitive that increases the discovery rate of independently supported factual aliases under an identical certificate and call budget.

相应修改：

- 主指标不用未经约束的 raw pair count，而使用唯一的 certified `(boundary, parameter block, effect-signature)` 数量；同一 boundary/block 的多个 `θ` 变体最多计一次主结果，其余只作强度曲线。
- candidate-contact baseline 必须只拥有 candidate activation 信息，不拥有 factual dependency subtraction；否则它已经是 ISRAC。
- 再设置“相同 certificate objective、相同 endpoint solver、但无 dependency pre-screen”的 constrained-search baseline，单独隔离 set subtraction 的贡献。
- 不把 correction-harm audit 写成第二个方法贡献。它只是证明编译产物对目标问题有用的 consequence test。

若删除 influence subtraction 后 matched-call yield 不降，核心机制即不成立；不能靠 downstream WAM harm 挽救。

### Venue Readiness — 6/10

**具体弱点**

当前 novelty 仍依赖未来结果，且 matched-call 公平性没有完全定义。第二 simulator 或更多 WAM 不能修复这一机制缺口。

**方法级修复 — IMPORTANT**

预注册一个审稿人无法轻易攻击的成本与对照协议：

- 所有方法共享完全相同的 boundary、candidate、parameter blocks、合法范围、effect predicate、certificate 和 pair 去重规则。
- ISRAC 的 nominal graph construction、factual/candidate trace、所有 probes、拒绝样本和最终 certificate replay 全部计入 calls。
- random、candidate-contact、无 influence subtraction 的 constrained search、CMA-ES/BO 使用相同总调用预算；调参预算也必须相同或独立报告。
- 主要统计单位是独立 boundary，而不是 `θ` pair；报告 paired seed/boundary bootstrap CI。
- 当前 24 pairs 只放在“system feasibility”栏。在 baseline 完成前，不得写“efficient compiler”“2×”或“method works”。

达到这些条件后，一台 simulator 上的两种真实机制族已经足以判断核心方法是否成立；不要用增加 benchmark 掩盖未隔离的算法贡献。第二 simulator 只用于确认 abstraction transfer，不是修复 C1 的手段。

## 两个定义隔离问题

### 1. Dynamic state 与 static physics hash

当前修正方向正确，但“完整动态 state”仍需降格为一个显式 schema，否则“full”不可审计。

建议将世界写成：

\[
W=(Z_t,\eta),\qquad
Z_t=(q_t,\dot q_t,\text{body poses},\text{joint states},
\text{contacts},\text{controller state},\text{sensor/RNG state}),
\]

其中两个世界只允许目标 block 的静态配置满足
\(\eta_b^+\neq\eta_b^-\)，其余 \(\eta_{\neg b}\) 必须逐字段相等。证书验证的是：

\[
Z_{0:T}^{+}=Z_{0:T}^{-},\quad
O_{0:T}^{+}=O_{0:T}^{-},\quad
A_{0:T}^{+}=A_{0:T}^{-}
\]

至 repeat-noise 上界，并分别哈希完整的 `η+` 和 `η−`。

若 simulator 暴露不了 solver warm-start、contact cache 或内部随机状态，就不要声称 “full simulator state”；应称“完整枚举的 replay-relevant dynamic state”，并列出不可见字段。否则静态参数不同与 full-state equality 会继续形成表述矛盾。

### 2. Model-free compiler 与 post-hoc WAM audit

目前的“WAM 尚未加载的证明性运行元数据”不够强，因为它仍是过程性声明。

需要硬接口隔离：

```text
Compiler inputs:
  snapshot, VLA-supported actions, simulator schema,
  legal parameter ranges, certificate thresholds

Compiler output:
  immutable pair manifest + all accepted/rejected candidates
  （绝不含 residual、ranking、WAM embedding 或 WAM ID）

Audit inputs:
  frozen manifest hash + independently loaded target WAM

Audit output:
  residual equality, false transport, ranking regret, correction harm
```

必须禁止：

- 看过任何 WAM 结果后删除、重排或重新选择 pairs；
- 用 WAM-dependent residual 作为 compiler certificate 字段；
- 只报告伤害某个 WAM 的子集。

如果 WAM 是确定性的，equal observation/action input 可在 audit 阶段导出 equal residual；若 WAM 有 recurrent/cache state，则该内部状态必须在 audit 中同步克隆，不能假定 residual 自动相同。

另外，“model-free”容易误导，因为编译器仍使用冻结 VLA。建议统一写成 **target-WAM-blind compiler**。

## Matched-call baseline 是否足够区分 fuzzing / MT

**目前还不够；按上述协议重构后才够。**

单独证明 ISRAC 比 random/grid/CMA/BO 多找到 pair，只能说明搜索启发式更高效，不能自动建立新的测试范式。真正可区分的证据必须同时满足：

1. 所有方法求解完全相同的 metamorphic relation 和 certificate；
2. 唯一改变的是是否使用 factual-vs-candidate dependency-set subtraction；
3. 所有用于构建该 subtraction 的 simulator calls 都被计费；
4. 删除 subtraction 后 yield 显著下降；
5. candidate-contact baseline 不能偷偷包含 factual-zero screening；
6. 结果以独立 boundary/block-effect signature 去重。

若最强无 subtraction baseline 等效，ISRAC 应明确降级为一个有用的 WAM/VLA metamorphic benchmark generator，而不是新的 compiler method。

## Evidence Calibration

当前四任务和 24 pairs 只支持以下一句话：

> 所提出的证书和参数干预流程在 LIBERO 上能够生成非空的 candidate-diverging factual aliases。

它们不支持：

- influence separation 提高 yield；
- ISRAC 优于 contact-aware fuzzing；
- 2× efficiency；
- 跨 simulator 泛化；
- feedback WAM correction harm；
- 目标 WAM 特异性；
- 顶会方法贡献成立。

正在运行的 random/contact baseline 在结果冻结前同样不能计分，也不能根据其早期趋势修改 ISRAC 阈值、参数范围或 pair 去重规则。

## Simplification Opportunities

1. **只保留一个 canonical endpoint solver。** 主方法固定 deterministic endpoint sweep/二分；CMA-ES、BO、通用 constraint optimizer 全部只作为 baseline，避免“贡献到底是 influence filter 还是 optimizer”。
2. **把 Claim 2 降为 downstream utility test。** 不为 WAM audit 增加新模块、训练损失或第二套方法故事；C1 不通过时直接停止。
3. **暂不扩 benchmark。** 先在现有 simulator 用独立 boundaries 和两个机制族完成严格 matched-call falsifier；更多任务、第二平台和更多 WAM 不能替代核心消融。

## Modernization Opportunities

NONE。

冻结 foundation VLA 作为支持内 candidate source 已经是合适且足够的现代接口。加入 LLM searcher、learned influence predictor、RL curriculum、video WAM generator 或新的 critic 都会增加复杂度并削弱 target-WAM blindness。当前需要的是更严格的 simulator-native algorithm definition，而不是更多现代模块。

## Drift Warning

NONE。

proposal 仍忠实解决原始 feedback residual 跨动作不可识别问题。唯一需要防止的未来漂移是：若 C1 不显著，就把论文重心转成“反馈 WAM correction harm benchmark”来回避 compiler 失败；这会从方法论文漂移成测试集/诊断论文，必须明确降级而不能当作同一主张继续。

## Verdict

**REVISE**

方向集中、实现可行、没有模块膨胀，也没有问题漂移；但核心搜索原语尚未被定义到足以区别 candidate-contact/constrained fuzzing 的程度，blind compiler 与 post-hoc audit 仍需接口级隔离，pair yield 的独立统计单位也未锁定。修复这些方法身份问题并完成公平 matched-call gate 后再评审；当前远未达到 READY 所要求的 overall ≥9。
