# WitnessWAM v2 第 3 轮严格方法复审

**评审角色：** research-refine senior reviewer  
**日期：** 2026-08-31  
**CALIBRATION:** none  
**Verdict:** **REVISE**

## 结论先行

v2 已经成为一份聚焦、可实现、claim 边界诚实的方法方案。Round 2 的主要逻辑错误基本被修复：同一个 post-event prefix 对所有 verifier 只执行一次，predicate truth trajectory 被逐步检查，FSM 不再重复 event-producing prompt，oracle utility endpoint 不再用 `tau_protocol` 自己定义错误，action necessity 也加入了 within-lineage effect size 与 held-out prediction gate。三种 producer 均改成自然物理分支，`on-target-support` 不再依赖 unstable hovering 或 solver transient。

但仍有三个 reading-robust blockers，故不能 READY：

1. **Predicate-preserving contract 目前通过 privileged future truth 进行样本过滤，而部署时无法知道实际 prefix 是否会改变 predicate。** 它消除了受控评估中的免费 retry/真值转移，却可能只对 oracle-selected easy subset 成立。需要把“保持真值”升级为 skill-level、部署可知的 continuation contract，并对所有 pre-prefix eligible states 报告 violation，而不是先看未来 truth 再筛样本。
2. 三种 producer 的 passive opportunity 大多由 hand/gripper withdrawal 暴露对象。现有 suffix-aware vs suffix-free gate 能证明 action matters，但不能排除更简单的 **action-conditioned visibility forecast**。若一个接收同一 action prefix、只预测目标区域未来可见性的 capacity-matched baseline 能匹配结果，WitnessWAM 仍退化为 visibility gate。
3. **“Prefix executed once regardless of verifier”与“FSM may transition early”在动作语义上矛盾。** 若 early transition 立即切换 next-subtask prompt 或清空当前 action queue，不同 verifier 仍执行不同动作；只有把 early decision 缓存、并把所有 action/subtask side effect 延迟到 step-5 boundary，固定 prefix 才真正成立。

这三个问题都可用最小局部修复解决，不需要增加新模型主线、benchmark 或 horizon。

## 同一七维评分

| 维度 | Round 2 | Round 3 | 评语 |
|---|---:|---:|---|
| Problem | 9.2 | **9.4** | 仍直接解决“证据出现前不应 commit/retract”，没有漂移到 recovery、reranking 或新 action head。 |
| Novel mechanism | 8.1 | **8.6** | predicate-preserving passive continuation + single opportunity hazard + fixed FSM 是清晰单贡献；仍需排除 action-conditioned visibility 的更小解释。 |
| Causal identifiability | 6.7 | **8.0** | 同动作、同 continuation、truth trajectory、非循环 endpoint 已显著改善；privileged post-outcome filtering 仍造成 deployment-selection gap。 |
| Data producer | 7.5 | **8.5** | 三个 family 均有自然分支、future-blind denominator、K-prefix paired design 和完整 replay/ledger；需冻结 seed replacement 与 preservation denominator。 |
| Implementability | 7.3 | **8.2** | 4×A100、五步 π0.5 prefix 与单 hazard 可实现；decode seed 需 server-side control，runtime eligibility 不能依赖 privileged truth。 |
| Evaluation | 6.9 | **8.2** | 总 FSM endpoint、固定 operating point、effect-size gates 均合理；缺 action-conditioned visibility baseline，OR-metric 与 CI clustering 仍需冻结。 |
| Claim honesty | 9.1 | **9.4** | nonclaims、五步 kill、PointMap 上界和外部 FSM 边界都清楚。 |

**OVERALL SCORE: 8.6 / 10**（七维等权，与前两轮一致）  
**Verdict: REVISE**（overall < 9，且存在两个可修复 blocker）

## GAP

Proposal 已不缺主机制，只缺最后一层 deployment-valid identification：**continuation 应在调用前由固定 skill semantics 被视为 predicate-preserving，而不是在看到两 branch 的 privileged future 后才进入评估集；action-conditioned opportunity 还必须优于接收同一 prefix 的 action-conditioned visibility predictor。** 解决这两点后，剩余不确定性主要是诚实的 E0 yield 风险，而非 proposal 逻辑缺口。

## R1–R6 核验

| Round-2 risk | 状态 | 第 3 轮判断 |
|---|---|---|
| R1 Predicate truth 在 witness window 内不保证不变 | **评估内修复，部署层部分未修复** | Producer 逐 action 记录 truth，并拒绝任何 truth transition，已保证训练标签不把 repair/destruction 当 witness。但该 eligibility 依赖 privileged future，runtime 无法先知 actual prefix 是否属于这一子集。 |
| R2 FSM waiting 与重复 event action 混杂 | **修复** | Post-event continuation 只执行一次、所有方法共享、绝不重复 event-producing prompt；五步边界统一 fallback。免费 retry 被去除。需明确 early decision 不会取消/替换剩余已发出的低层动作。 |
| R3 Oracle endpoint 循环 | **大部分修复** | Primary utility 改为 wrong FSM transitions + boundary belief errors + timeout penalties，并在冻结 coverage/delay 规则下比较，不再由 `tau_protocol` 定义。Composite 权重与 operating-point tie rule 仍需预注册。 |
| R4 Action necessity 只有显著性 | **大部分修复** | 已加入 K=4 within-lineage ≥1-step/status effect 与 suffix-aware Brier/C-index 增益、shuffle erase。缺少 action-conditioned visibility baseline；Brier-or-C-index 的 `OR` 也给了选择自由度。 |
| R5 Opportunity denominator 污染 | **修复** | Future-blind denominator 在查看 opportunity 前冻结，且 opportunity yield 对该分母计算。必须进一步区分“pre-prefix denominator”与用未来 truth preservation筛后的 denominator。 |
| R6 Supported-by settled 冲突 | **修复** | 改成 named target support versus adjacent ordinary support/table，两 branch 均 settled，不依赖 hovering/transient。 |

## 重点审查

### 1. Predicate-preserving contract 是否消除免费 retry/真值转移？

**免费 retry 已消除；评估集内的真值转移已消除；部署条件下尚未完全消除。**

固定的两阶段 skill 和单次 post-event continuation 是正确设计。所有 verifier 执行同一个五步 prefix，随后统一 fallback，因此决策器不会通过多等待而获得额外抓取/放置尝试。逐步检查 `p+(0:5)=true`、`p-(0:5)=false` 也保证已接受训练样本上的视觉差异确实对应 checkpoint relation。

剩余问题在于这项检查发生在未来 rollout 之后。部署时只有一个未知 branch，没有 privileged predicate truth，系统无法知道某个 grasp transport 是否会掉落、某次 withdrawal 是否会碰动 rim object。若 evaluation 只保留 preservation 成功的 lineages，closed-loop claim 变成：在事后知道 action 不会改变 truth 的 subset 上，schedule 有效。该 subset 可能排除了最困难、最重要的 failure states。

最小修复应避免新增 deployable eligibility classifier：

- 对每个 family 冻结一个 **结构化 post-event continuation envelope**，例如 release 后沿注册远离对象/容器的 withdrawal，且后续不得再闭夹爪、接近或接触 target/reference bodies；
- future truth preservation 只作为该 envelope 的 audit，不作为逐样本进入 denominator 的后验筛选；
- 从所有 physically valid + replay-deterministic + time-zero ambiguous + paired-action-agree + safe 的 pre-prefix lineages 报告 preservation rate；每个 retained family 应预注册高 preservation gate，例如 ≥95%；
- truth transition 样本仍不能用于 `tau_protocol` supervision，但必须计入失败/yield 分母和闭环 failure，而不能静默删除。

若无法达到高 preservation rate，应删除该 family 或把 claim 明确限制为离线 oracle-filtered analysis；后者不足以支撑当前 long-horizon system claim。

另需写死：即使 verifier 在 step 2 commit，step 3–5 的已发出低层 prefix 仍完整执行；subtask prompt 只在五步边界更新。否则“may transition early”仍可能让不同方法执行不同动作。

### 2. 随机 source-balanced prefixes 是否仍有 policy-support/interface 问题？

**Policy-support 主张已足够诚实；接口上有一个局部实现缺口。**

每个 canonical prefix 都由冻结 π0.5 在某一真实 alias observation 上采样，因此它对 source branch 是 policy-sampled。另一 branch 上不声称 density support，而以同 seed 输出 agreement + source-balanced cross replay 约束近似部署等价；这比无法计算的 “close to support” 表述更可靠。随机 source branch 也避免总用 true 或 false branch 产生 prefix 的标签偏差。

但标准 policy client 通常只提供 `infer(observation) -> action chunk`，不一定暴露 per-request flow decode seed。K=4 需要在本地 policy server 侧冻结 PRNG keys、用相同 noise key 成对查询两个 aliases，并缓存原始/normalized outputs。Proposal 应明确是 **server-side paired decode keys**，不是假设 client API 已有 seed 参数。

还需预注册：

- exactly four seeds 在任何 rollout 前固定；
- 不因某 seed 不 preservation 或不产生 opportunity 而补抽 replacement seed；
- “eligible lineage”需要至少四个符合 action-agreement/safety 的 prefixes，还是允许 prefix-level missingness；二者必须二选一；
- action tolerance 在 normalized 7-D chunk 上还是 denormalized physical command 上计算。应优先用 deployment 后的 physical command distance。

K=4 的 policy inference/compute 本身完全现实，四卡不是限制。主要风险是四个 paired prefixes 同时满足 agreement + safety + preservation 的 lineage yield 过低；这应由完整 ledger kill，而不是扩大 seed pool。

### 3. Fixed FSM 总 endpoint 是否非循环？

**是，已基本非循环。** Wrong FSM transition、五步边界 wrong belief 与 timeout 都由 privileged relation truth/FSM outcome判断，不以 `tau_protocol` 作为错误定义。Oracle schedule 仍是 upper bound，但不再因为“在 oracle time 前不决策”而自动在 primary endpoint 获胜。Coverage ≥90%、max wait=5 和 delay tolerance 也限制了纯 abstention。

剩余是可局部冻结的统计细节：

1. 一个错误 commit 同时造成 wrong transition 和 boundary wrong belief 时是否双计；
2. timeout penalty 的单位/权重；
3. baseline 若无法同时匹配 90% coverage 与 mean delay tolerance时如何判定；
4. full curve 与 one fixed point 不能事后择优，必须预注册一个 primary、另一个 secondary。

建议 fixed operating point 作为 primary，完整 curve 作为诊断。三个 component 分别为 primary family-wise reports；若必须合成总 endpoint，权重在看到 test 前冻结。当前问题不再是 reading-robust blocker。

### 4. Within-lineage K=4 是否现实？

**计算和采样现实，统计设计也基本合理。** 同一 observation stratum 用四个 coupled flow noise keys生成 normal π0.5 prefixes，可以产生同状态下的 action variation；paired cross replay isolating prefix effect 是合适的 core necessity test。数据规模远低于四卡瓶颈。

风险有三点：

- 五步只有少数离散 `tau` bins，C-index 会有大量 ties/censoring；integrated Brier score 更适合作唯一 primary metric。
- `K=4` 只在每 lineage 内给六对比较，足以估 effect distribution，但不能靠单 lineage significance；应以 lineage 为独立单位做分层 bootstrap。
- “family-clustered 95% interval”若意味着以 2–3 个 family 为 clusters，统计上无效。应在每个 family 内按 common-parent lineage bootstrap，再要求每个 retained family 的 CI 单独排除零。

只要 seeds 不替换、missingness 规则冻结、以 lineage 为独立单位，K=4 是合理的最小设计。

### 5. 三种 producer 是否足够自然？

**三者都可以自然生成，但共享一个更简单的显露机制。**

- `grasp-coupled`: 稳定抓持 vs natural miss，随后 ordinary transport/withdrawal；物理自然，最可能在五步内通过 co-motion 暴露。主要风险是 true grasp during transport 的 preservation rate。
- `inside`: settled inside vs settled rim/outside miss，随后 hand withdrawal；自然且符合 native occlusion，但机会多半由手移开带来的 visibility。
- `on-target-support`: named target vs adjacent ordinary support/table 的两个 settled placement，随后 hand withdrawal；消除了 unstable-state 造假，但要避免专门挑选能被手完全遮住的相邻位置。完整 acceptance yield 应暴露其自然性。

至少两类 relation 在物理语义上不同，足以支撑首轮 claim。然而三者的 opportunity 都可能由同一个 occluder-withdrawal dynamics 解释。这并不让数据 producer 人工，但它使 **action-conditioned visibility predictor** 成为必须击败的最小机制 baseline。

### 6. Action-conditioning necessity gate 是否足够？

**比 Round 2 强很多，但仍缺一个决定性 baseline。**

Producer gate 证明 normal prefix 的变化能改变 `tau_protocol`；model gate 证明 hazard 使用 action prefix，而非 family/scene prior。数值 effect、held-out prefix、shuffle erase 与 per-family CI 都是正确的。

但 suffix-aware 模型相对 suffix-free 模型的优势也可能完全来自“prefix 告诉模型手何时移开目标区域”。现有 visibility-only baseline若不接收 action prefix，会不公平地把 action information advantage归因于 WitnessWAM。

必须加入一个 capacity-matched **action-conditioned visibility hazard**：输入与 WitnessWAM 相同的 RGB/proprio、object queries、exact five-step prefix，只监督 target/reference region 何时达到 visibility threshold，不使用 pairwise projected-separation/relation opportunity label。WitnessWAM 应在 held-out lineages上相对它达到预注册的非微小增益，例如 integrated Brier score再改善 ≥10% relative，或在固定 FSM endpoint 上改善 ≥10%，且每个 retained family 的 lineage-bootstrap CI 排除零。若二者相当，正确结论是 method 收缩为 action-conditioned visibility scheduling，而不是保留 WitnessWAM claim。

同时把 model gate 的 “Brier ≥10% **or** C-index ≥0.05” 改成预注册单一 primary metric；五步离散 tied data 下建议 integrated Brier score。

## 剩余 reading-robust blockers

### Q1. Privileged preservation filtering 造成 runtime selection gap（CRITICAL）

当前 truth-preserving subset 是 rollout 后才能识别的。必须用部署前可知的 family-level continuation envelope，并把所有 truth transitions计入 violation/yield，而不是从 denominator 删除。

### Q2. 缺 action-conditioned visibility baseline（CRITICAL for mechanism claim）

Suffix-aware vs suffix-free 只能证明 action information 有用，不能证明 relation-opportunity modeling 超过未来可见性预测。三种 producer 都以 hand withdrawal 为主要显露路径，因此该 objection 会被 reviewer 直接提出。

### Q3. Early FSM transition 与 fixed prefix 矛盾（CRITICAL for closed-loop identification）

Proposal 一处规定 post-event continuation “executed once regardless of which verifier”，另一处允许 FSM “transition early”。若 transition 包括立即 advance prompt、启动 next subtask 或停止剩余 action queue，则不同 verifier 的物理轨迹再次分叉，fixed-continuation control 失效。必须规定：early evidence 只更新缓存的 belief/decision；step 0–5 的 action queue 对所有方法不可取消且完全相同；FSM advance/retract 与 prompt change 只在五步边界原子生效。

## 可局部修复项

1. 将 predicate preservation 从 per-rollout acceptance filter 改成 skill-level continuation envelope + family preservation-rate gate；transition 样本计入失败分母。
2. 明确早 commit 不改变已发出的五步动作，prompt 只在 chunk boundary切换。
3. 加 capacity-matched action-conditioned visibility hazard，并给 WitnessWAM 相对它的数值门槛。
4. 选择 integrated Brier score 为 action-necessity primary；不保留 post-hoc `Brier OR C-index`。
5. CI 在每个 family 内按 common-parent lineage bootstrap；不要用 2–3 family clusters。
6. 固定四个 server-side paired decode keys、无 replacement、physical-command agreement tolerance 和 missing-prefix rule。

## 最小下一步修复

下一轮只需两项，不要扩展 benchmark或模型：

1. **部署有效的 preservation/action-lock contract：** 用 family-level predicate-preserving continuation envelope替代 privileged after-the-fact inclusion；每 family 报告全 eligible pool 的 preservation rate并设 kill threshold；early decision 只缓存，action queue和prompt必须锁到五步边界。
2. **最小替代机制对照：** 增加接收同一 exact prefix 的 action-conditioned visibility hazard；WitnessWAM 必须在统一的 integrated Brier/FSM endpoint 上有预注册实质增益。

若这两项（其中第一项包含 action lock）冻结，R1–R6 将无未解决逻辑 blocker。之后五步 opportunity yield、K=4 preservation yield 和相对 visibility baseline 的实际结果属于 E0 falsification risk，不应在 proposal 阶段要求预先成功。

## Simplification opportunities

1. 保持 single opportunity hazard、固定 FSM 与五步 horizon；不恢复 competing risks、multi-chunk waiting 或 recovery。
2. 将 action necessity 的 primary metric固定为 integrated Brier score，删除 metric OR。
3. 若某 family 的 structural preservation rate 不过门，直接删 family，不增加 eligibility model。

## Modernization opportunities

**NONE.** 现有 π0.5 prefix + compact WAM 已自然；缺口是 identification，不是模型新旧。

## Drift warning

**NONE.** 若为处理 truth transitions 新增 recovery或eligibility classifier，则会重新引入 contribution sprawl；应通过固定 continuation envelope和诚实 kill解决。
