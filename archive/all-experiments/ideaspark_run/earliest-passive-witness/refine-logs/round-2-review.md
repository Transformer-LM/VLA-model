# WitnessWAM v1 第 2 轮严格方法复审

**评审角色：** research-refine senior reviewer  
**日期：** 2026-08-31  
**CALIBRATION:** none  
**Verdict:** **REVISE**

## 结论先行

Round 2 是实质性收敛，而非文字修补。Proposal 已完成四项关键简化：不再声称 perfect causal twins；把 label、learning target 和 runtime quantity 统一成一个 protocol-relative opportunity time；把 suffix 限定到部署实际执行的五步 prefix；用固定外部 FSM 明确了 `PENDING` 的消费者。PointMap 也退回 privileged upper bound/teacher，没有继续外推既有 E0。

但尚不能 READY。当前最严重的剩余问题是：**five-step continuation 和 FSM 等待动作可能改变正在验证的 predicate truth。** `PENDING` 时继续同一个 event-producing subtask，可能让 missed grasp 变成 successful grasp、让 failed placement 被重新放置，或破坏已经成功的 placement。此时 later observation 不是对 checkpoint hidden truth 的被动 witness，而是新动作造成的新 truth。由于不同 verifier 会等待不同时间并执行不同数量的重复动作，closed-loop gain 同时混入“重复动作次数”和“被动验证时机”，共享同一 FSM 并不能消除该混杂。

另外，oracle gate 6 的 primary endpoint 由 oracle opportunity 自己定义，因而近乎结构性获胜；action-conditioning gate 8 只有显著性、没有 effect-size 和 held-out prediction threshold。这两项仍不足以证明机制必要性。

## 同一七维评分

| 维度 | Round 1 | Round 2 | 评语 |
|---|---:|---:|---|
| Problem | 9.0 | **9.2** | 锚点完整保留，且 claim 已收窄为 protocol-relative passive verifiability。 |
| Novel mechanism | 7.4 | **8.1** | single opportunity hazard + exact deployed prefix + commit semantics 更聚焦；仍需排除 visibility gate 与 ordinary delayed verifier。 |
| Causal identifiability | 5.2 | **6.7** | 不再声称 perfect twin，label estimand 已一致；但 suffix/FSM 可改变谓词真值，closed-loop treatment 尚不可分解。 |
| Data producer | 5.5 | **7.5** | family edit、clone contract、ledger、lineage split 明显改进；`supported-by` edit 与 acceptance denominator 仍不严密。 |
| Implementability | 5.7 | **7.3** | 五步 π0.5 接口、RGB primary、固定 FSM 均可落地；predicate-preserving continuation 和 evidence-likelihood训练接口仍缺。 |
| Evaluation | 6.6 | **6.9** | baseline 和 gates 更聚焦；gate 6 部分 tautological，gate 8 缺 effect size，closed-loop 重复动作混杂未控制。 |
| Claim honesty | 8.5 | **9.1** | policy/action/camera/sensor/label protocol 条件化边界写得诚实，PointMap 证据没有被滥用。 |

**OVERALL SCORE: 7.8 / 10**（七维等权，与 Round 1 一致）  
**Verdict: REVISE**（overall < 9，且仍有 reading-robust blocker）

## GAP

现在缺的不是模型结构，而是一条 **predicate-preserving observation contract**：从 checkpoint 到 `tau_protocol`，同一五步 prefix 必须只揭示 predicate，而不能改变 predicate。若 prefix 可能改变 truth，则 producer 应在首次 truth transition 处 censor/reject；FSM 也不能在 `PENDING` 时无限重复 event-producing prompt。完成这一点后，oracle headroom、action necessity 和闭环作用才共享同一个可解释 estimand。

## B1–B7 修复审计

| Round-1 blocker | 状态 | 本轮判断 |
|---|---|---|
| B1 Twin 不是真正 causal match | **大部分修复** | 已改称 common-parent compiled sensor aliases，允许 family-specific 物理差异，禁止 truth bit/weld/人工黑屏，claim 不再依赖“只差谓词”。但 `supported-by` 的“settled stable vs unstable”不物理一致，且 locked non-descendants 仍需 family-specific 数值化。 |
| B2 `tau*` circularity / earliest bias | **修复** | `tau_protocol` 由冻结的几何/投影/持久性协议产生，sensor model 只做独立翻译验证且不能改 label；不再扫描 learned encoder/classifier。由于 label rule 是确定协议而非逐帧统计检验，两窗口 persistence 已足够控制本轮所指的 earliest-selection 问题。 |
| B3 Pair-level time vs competing risks | **修复** | 已删除 dual competing-risk head，统一成 single pair-level discrete opportunity hazard；两 hypothesis likelihood 只在机会到来后更新 belief。M3–M5 的统计对象现已基本一致。 |
| B4 Same suffix 超出部署语义 | **当前五步修复；滚动运行仍有问题** | 同观测、同 seed 查询一次冻结 VLA，只执行 deployed `h_exec=5`，边界 right-censor，定义清晰。但 FSM 后续继续同一 subtask 的新五步 calls 会改变 predicate，不能自动视为同一 hidden fact 的 rolling witness process。 |
| B5 `PENDING` 退化为 visibility gate | **部分修复** | 加入 capacity-matched visibility-only、suffix-free、prefix shuffle 和 stop rule，方向正确；gate 8 只要求 reject invariance，没有最小效应量或 suffix-aware 模型的 held-out improvement 门槛。 |
| B6 π0.5 无 progress-memory consumer | **接口修复；因果混杂未修复** | 固定外部 FSM 是正确的最小 consumer，且没有谎称 π0.5 获得内部 memory API。但 pending 时重复当前 subtask 会产生真实额外动作，使验证策略与动作干预纠缠。 |
| B7 PointMap evidence overreach | **修复** | RGB+proprio 是 primary，PointMap 仅 upper bound/teacher，明确不假设 depth/mask/segmentation，旧 E0 WARN 保留。 |

## 指定重点审查

### 1. Family edits 是否真实可生成？

**Grasp-coupled：有条件可生成。** 自然 missed grasp 与稳定 grasp 可以来自共同 pre-grasp parent 和小物理 offset，允许 contact/object pose 差异且不声称完美因果匹配是正确的。Acceptance test 必须在 checkpoint 前确认两 branch 均物理稳定；不能把“test prefix 后的 object velocity”写成 checkpoint permitted difference。真正风险是 yield，而不是定义上的不可能，pilot gate 可以诚实证伪。

**Inside：可生成。** container rim/hand 的原生遮挡可以形成 time-zero alias，成功 release 与 rim/outside miss 有自然的 pose/contact 差异。必须禁止用 camera crop 或容器材质专门为匹配服务；当前 native-occlusion 约束已经覆盖主要风险。

**Supported-by：当前定义不自洽。** Proposal 同时要求 branch settle，又要求 false branch “unstable/off-support”。真正 unstable/off-support 物体在 settle 后通常已经掉落、滑开或形成新的稳定接触；若它仍保持同位置，多半依赖 solver 暂态或不可见约束。最小修复是：

- 将第三 family 限定为两种都已 settle 的 stable support relation，例如正确 support 与相邻错误 support；或
- 明确使用 checkpoint 后短时动力学，并取消该 branch 的 settled 要求，但这会引入 velocity/state mismatch；或
- 直接把 supported-by 留作 pilot candidate，若无法满足 replay/ambiguity/predicate-preservation gates 就删除，不影响“至少两 family”的 claim。

因此 B1 已不再是 perfect-twin blocker，但第三 family 仍不是 reading-robust producer。

### 2. Single opportunity hazard 与 label producer 是否一致？

**一致。** `tau_protocol` 是 pair-level first accepted opportunity，模型输出 pair-level discrete hazard 与 survival/censoring mass，hypothesis likelihood 不再被误称为 event causes。这是本轮最重要、最成功的修复。

还需在 experiment plan 冻结两个小接口：

1. hazard interval 的风险集如何处理 camera sampling 与 two-window persistence；
2. 两个 frozen likelihood 是一个共享模型的 `q(z|p=±, opportunity)`，还是两个独立密度，并且必须与 opportunity labeler 使用 disjoint parent lineages。

这两点是实现细节，不再是概念 blocker。

### 3. 五步内 delayed opportunity 是否可能有足够覆盖？

**可能，但高度不确定；这是合格的 oracle E0 风险，不应靠论证假定通过。** 在 10 Hz 类控制下，五步约半秒，grasp 后的 co-motion 或 placement 后手部撤离有时会出现证据，但许多 lift-away、drawer motion 或重新显露需要更长时间。two-window persistence 又将有效 first time 压缩到前四个采样位置。

Gate 4 的 25% 阈值原则上足以做 kill test，但 denominator 必须修正。当前“25% accepted aliases that ... gain opportunity”存在选择循环，因为 `later-opportunity` 已出现在 acceptance ledger。分母必须是：

> 所有 **physically valid + replay-deterministic + time-zero ambiguous + five-step-safe** lineages，且在查看 future opportunity 前已进入 eligible set。

每个 retained family 都单独达到 ≥25%；不能只报告 accepted-after-opportunity yield。若两 family 不通过，五步 estimand本身即失败，不应延长 H 来挽救，因为那会重新破坏部署语义。

### 4. Fixed FSM 是否赋予 PENDING 真实闭环作用且没有重复动作混杂？

**有真实闭环作用，但当前有严重混杂。** FSM 明确决定何时 advance/retract，因此 `PENDING` 不再是离线标签。然而“while pending ... continues the current subtask through ordinary five-step VLA calls”会让不同 verifier 执行不同数量的 event-producing动作：

- missed grasp 可被下一 chunk 重新抓成功；
- failed inside placement 可被重复动作纠正；
- correct placement 可被再次接触而破坏；
- 两 alias 的 predicate truth 可能在 `tau_protocol` 前收敛、互换或失效。

这既破坏 label 的固定 hypothesis，也使 closed-loop success gain 无法归因于 witness timing。所有 baseline 共用 FSM 并不能解决，因为 gate 的等待时间正决定重复动作次数。

最小修复是预注册 **predicate-preserving prefix eligibility**：在 oracle producer 中，只有 `p+` 与 `p−` 在整个五步 prefix 内保持各自 truth、且 prefix 不重新执行 relation-establishing动作的 lineage 才用于 witness label；首次 truth transition 立即作 competing event/reject，而不能当 witness。Runtime 上，`PENDING` 只能消费当前已经发出的 post-event continuation chunk；若边界仍 censored，进入所有方法共享的 fallback，而不能无限重发 event-producing prompt。若要跨多个 chunks 等待，则必须给 FSM 一个固定、普通、predicate-preserving continuation subtask，而非“继续当前 subtask”。

这不是新增实验，而是使已有 oracle/closed-loop block 可解释的必要 contract。

### 5. Oracle gate 6 是否逻辑可计算？

**可计算，但当前指标近乎 tautological，不能作为机制必要性门槛。** 在保存的 privileged trace 上，可以计算每种 rule 的 decision time、predicate truth、coverage 和 delay；所以不是不可实现。然而 oracle gate 按定义在 `tau_protocol` 前禁止 decision，其 pre-opportunity wrong-decision risk 结构性接近零。再要求它相对会提前判断的 baseline 降低 30%，主要是在验证定义本身，而不是 passive opportunity 的实际效用。

同时“matched coverage and mean/P95 delay”是三个约束，baseline 未必存在完全匹配的 operating point；若事后选最近点，会产生自由度。

Gate 6 应作为 **oracle headroom**，但要用一个非循环 endpoint：在 validation 上预先固定 operating point，或比较完整 risk–coverage–delay Pareto curve；在相同 coverage、固定最大 timeout 和预注册 delay tolerance 下，比较 **全部错误 FSM transitions + 最终 predicate error + timeout**。Oracle schedule 还必须优于 privileged/learned visibility-only gate，而不是只在用 `tau_protocol` 定义的 pre-opportunity risk 上获胜。30% relative 可以保留，但错误分母和 matching rule 必须冻结。

### 6. Action-conditioning necessity gate 是否足够？

**不足。** Gate 8 证明“不同 prefix 能改变 oracle label”至多说明 estimand 对动作敏感；permutation test 在样本大时可对极小差异显著。它没有证明：

- action prefix 对 held-out opportunity prediction 有实质增益；
- 增益超出当前可见性、手臂运动幅度或 time index；
- trained WitnessWAM 真正在使用 prefix，而不是依赖 family/scene prior。

最小而充分的两级 gate 是：

1. **Producer-level effect size：** 对同一 common-parent/current-observation，使用至少 3–4 个由冻结 π0.5 不同注册 seeds 产生的正常五步 prefixes；至少预注册比例的 eligible lineages 出现 ≥1 step 的 `tau_protocol` 改变，并报告 within-lineage effect，而不只报 permutation p-value。
2. **Model-level necessity：** suffix-aware hazard 在 held-out prefix/object/parent 上相对 suffix-free gate达到预注册的实质增益，例如 time-dependent Brier score ≥10% relative improvement 或 C-index ≥0.05，并且 prefix shuffle 将性能降回 suffix-free 区间。95% family-clustered CI 必须排除零，每个 retained family 单独成立。

这仍是同一个 mechanism-necessity block，不增加 benchmark 或模块。

## 剩余 reading-robust blockers

### R1. Predicate truth 在 witness window 内不保证不变（CRITICAL）

Opportunity label默认未来差异是对 checkpoint relation 的 evidence，但 prefix 可改变 relation。必须增加 predicate-preserving eligibility 或把 truth-transition作为单独 censor/competing event；最小方案是前者。

### R2. FSM waiting 与重复 event action 混杂（CRITICAL）

不同 verifier 的 waiting duration导致不同数量的 grasp/place重复动作。闭环增益可能来自免费 retry，而非验证。Pending continuation 必须固定为 predicate-preserving policy continuation，或只允许当前一个 chunk后统一 fallback。

### R3. Oracle gate 6 的 endpoint 由 oracle schedule 自己定义（IMPORTANT）

30% pre-opportunity reduction 近乎结构性成立；需要总错误 transition/最终错误/timeout与冻结的 risk–coverage–delay matching rule。

### R4. Action necessity 只有 p-value、无 effect size（IMPORTANT）

至少需要 within-lineage multi-prefix effect 和 held-out suffix-aware vs suffix-free prediction gain两个数值门槛。

### R5. Gate 4 denominator 可被 opportunity-based acceptance 污染（IMPORTANT）

`later-opportunity` 不能参与 eligible denominator。25% 必须相对于 future-blind、time-zero eligible pool计算。

### R6. Supported-by producer 与 settled 条件冲突（MINOR if optional, IMPORTANT if retained）

若第三 family 不能自然通过，直接删除；不要用 solver transient 或 hidden constraint 挽救。

## 可局部修复项

1. 在每个 prefix 上记录 privileged predicate truth trajectory，要求 truth 在 `0:5` 保持；否则 reject/censor。
2. 把 FSM 的 pending 行为从“继续当前 subtask”改成一个预注册 predicate-preserving continuation，或在当前 chunk结束即统一 fallback。
3. 将 gate 6 改成非循环的 overall decision/FSM error at fixed coverage-delay-timeout operating point。
4. 给 gate 8 加 within-lineage action effect size与 held-out suffix-aware prediction improvement；不能只看 permutation significance。
5. 冻结 gate 4 的 future-blind denominator；drop supported-by if it cannot settle naturally。

## 最小下一步修复

下一轮只需修一个核心 contract 和两个 gate，不必增加模型：

1. **Predicate-preserving contract：** 明确 producer 与 runtime 的五步 prefix 在 opportunity 前不得改变 predicate；FSM 不重复 event-producing prompt。
2. **Oracle utility gate：** 用冻结 operating point 下的总错误 transition、最终错误和 timeout替代由 `tau_protocol` 自定义的 pre-opportunity优势。
3. **Action necessity gate：** 加入同 lineage 多 prefix 的最小 effect size，以及 suffix-aware 对 suffix-free 的 held-out 数值增益。

完成后，B1–B7 中只会剩下五步覆盖率这个诚实的 oracle E0 风险；若两 family 的 ≥25% yield 通过，方法才接近可执行且可归因。

## Simplification opportunities

1. 保持 single hazard，不恢复 competing risks 或 cause heads。
2. 若 supported-by 无自然 producer，删除第三 family；两种物理不同的 family 足以做首轮机制验证。
3. 不增加 learned recovery、PointMap deployment 或长 horizon；先让一个 predicate-preserving five-step contract 成立。

## Modernization opportunities

**NONE.** 当前缺口是数据生成与因果/统计 contract，不是模型年代问题。

## Drift warning

**NONE.** Proposal 仍直接解决“证据出现前不要错误 commit/retract”。但若用 retry/recovery 行为解释闭环增益，就会漂移成 recovery wrapper；必须先去除重复动作混杂。

