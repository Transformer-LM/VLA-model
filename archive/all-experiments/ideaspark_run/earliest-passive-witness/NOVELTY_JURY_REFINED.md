# WitnessWAM v4（Earliest Passive Witness）严格查新复审

**审查日期：** 2026-08-31  
**唯一方法输入：** `refine-logs/round-5-proposal.md`  
**严格门槛：** novelty 必须 **> 7.0**；`7.0` 仍为 FAIL  
**最终分数：** **6.9 / 10**  
**Naturalness：** **7.8 / 10**  
**最终判定：** **FAIL — 不授权 E0 或 GPU 实验**

## 1. 结论先行

WitnessWAM v4 找到了一个真实且重要的问题：VLA 已经执行了某个关系事件，但当前传感器尚不能可靠判断 `grasped`、`inside` 或 `on-target-support` 的真假；若此时立即写入或回滚进度记忆，会造成错误完成、错误恢复和后续规划污染。

但是，READY 版本的剩余新意不足以跨过严格 `>7.0` 门槛。没有发现一篇论文完整复制其联合机制，但这不能自动产生高 novelty。其机制可被审稿人自然地拆成下列已有部件：

1. action-chunk boundary 的对象关系谓词验证、`uncertain` 状态与 re-observation/recovery；
2. committed action chunk 条件下的执行期预测—观测监控与 first-crossing trigger；
3. 部分可观测系统中的三值 runtime monitoring；
4. 标准 discrete survival / interval-censored hazard；
5. 用 privileged simulator rule 标注“应关注哪一帧”的辅助监督。

真正未被单篇工作覆盖的是：在自然 matched relation aliases 上执行同一不可修改的五步 VLA suffix，监督“两个关系真值第一次可被被动 RGB/proprio 区分的时刻”，并只把该时刻的证据暂存给边界级外部关系记忆。这个 delta 是连贯的，但由于最终消费者与 capacity-matched full-history boundary verifier 拥有相同完整轨迹、在同一边界更新同一 FSM，显式 `tau_protocol` 不增加可用信息或决策能力；它主要是一种 frame-selection / temporal-attention supervision。严格 novelty 因而为 **6.9**。

## 2. 被审查的 exact mechanism

### Observation

- 检查点时的 RGB、proprioception、对象—关系 query；
- π0.5 已经排队、不可修改的精确五步低层 action prefix；
- 执行期间产生的 RGB/proprio 证据；
- 部署时不允许 body pose、分割、深度、PointMap、模拟器几何或未来真值。

### Intervention

- **没有诊断动作、主动感知、reranking 或 suffix repair**；
- 两个隐藏关系别名执行相同冻结 suffix；
- WitnessWAM 的判断不能改变五步物理轨迹，只能暂存一次关系 belief。

### Supervision

- 从相同可见检查点构造 `relation=true/false` 的自然物理别名；
- 用 family-specific privileged protocol，根据关系几何、查询区域可见性、投影分离超过噪声阈值及两帧 persistence，标注 `tau_protocol in {1,...,5,censored}`；
- 学习离散 interval-censored opportunity hazard；
- 证据正负 likelihood 与 timing 模型分离、冻结且 lineage-disjoint。

### Consumer

- `tau_protocol` 之前外部关系记忆保持 `PENDING`；
- 机会到达后，冻结证据模型可暂存正或负 belief；
- 五步边界才原子地 commit/withhold，并由同一个 FSM advance、retract 或 fallback。

## 3. 最强先行工作逐项对照

| 工作 | Exact observation | Intervention | Supervision | Consumer | 与 WitnessWAM 的关系 |
|---|---|---|---|---|---|
| [POT-VLA](https://arxiv.org/abs/2607.18016) | RGB-D 刷新的 persistent 3D object records；含 visibility、confidence、containment/support/grasp 等 relation fields | 每个 chunk 后可 continue、retry、reobserve、reground、replan | 手工几何谓词、阈值和 stability window | `{in_progress, done, blocked, failed, uncertain}` 更新任务进度并触发恢复 | **消费者与问题最接近。** 已有 relation-level、uncertain、chunk-boundary progress gating。缺少同 suffix matched aliases、被动可辨识时机与 censor hazard；且依赖 RGB-D。 |
| [CheckVLA](https://arxiv.org/abs/2607.26789) | 最新观测、剩余 committed actions、action-conditioned world-model feature prediction 与实际观测 discrepancy | first-crossing 风险触发后修改 action suffix | 成功/失败与时序风险监督、校准阈值 | 执行中验证、修复 suffix，并维护 episodic keyframe evidence | **最强 WAM/VLA execution-verification 近邻。** 已覆盖 committed chunk、action-conditioned future、到达中的证据和 first-crossing；没有关系机会标签，消费者是 repair 而非外部 predicate memory。 |
| [Foresight](https://arxiv.org/abs/2606.23085) | action-conditioned world-model latents、实际视觉轨迹和因果历史 | 不改变用于打分的过去轨迹；first threshold crossing 发出 failure alarm | trajectory-level terminal success/failure；functional conformal threshold | 长时失败监测/报警 | 已覆盖 action-conditioned history 与“首次越阈”执行监控，但检测的是失败风险，不是某关系第一次原则上可辨识的时机。 |
| [PATCH](https://arxiv.org/abs/2606.16690) | 顶视/腕视 RGB、proprio/effort、active policy identity 与 action chunk；chunk 投影 execution corridor | latch 后 hold/self-recovery/peer/human intervention | corridor 内 persistent external innovation 窗口标签 | 局部证据、hysteresis、intervention/resume router | 已覆盖 action chunk 指定证据区域、时间 persistence、遮挡/瞬态过滤和 latch。没有 predicate-truth twins 或 earliest passive witness。 |
| [ConditionNET](https://arxiv.org/abs/2502.01167) | 当前 RGB 与语言动作，逐帧查看 precondition/effect | 可 retry 或继续 | preparation/core/post temporal segmentation 与动作结果标签 | 在线动作条件验证 | 已有逐观测的 precondition/effect 检验；不预测冻结 suffix 下的未来证据机会。 |
| [Embedding Temporal Logic (ETL)](https://arxiv.org/abs/2605.12651) | 视觉 embedding trace 上的感知谓词 | 无 WitnessWAM 式物理干预 | embedding predicate 与 temporal logic/calibration | trace-prefix runtime verdict | 已覆盖视觉谓词的时序监控；未学习 action-conditioned opportunity time。 |
| [Runtime Verification for LTL and TLTL](https://www.isp.uni-luebeck.de/research/publications/runtime-verification-ltl-and-tltl-0)；[ABRV](https://link.springer.com/chapter/10.1007/978-3-030-32079-9_10) | 有限观测前缀，以及部分可观测系统的假设模型 | runtime monitor/reset | 形式化系统模型与 LTL 语义 | `true/false/inconclusive`，在足够短前缀上尽早给出结论 | `PENDING`、证据不足不下结论、最早可确定 verdict 都不是新的语义原语；WitnessWAM 的差别是 learned RGB/proprio、固定 VLA suffix 与 simulator-compiled relation opportunity。 |
| [How Visible Are Silent Manipulation Failures?](https://arxiv.org/abs/2606.03134) | 完整 episode 的 proprio summary 与 final-image features | 无 | privileged final outcome | 仅做 post-hoc observability analysis | **最强问题证据。** 证明成功/失败的可感知性依赖 modality，但不提出在线 detector、witness time、matched predicate twins 或 memory consumer。 |
| [IntentVLA / AliasBench](https://arxiv.org/abs/2605.14712) | 当前相似观测与近期历史；冻结 VGGT history representation | 由 policy 生成动作 | matched observation aliasing 与 imitation | history-conditioned action generation | 证明同一外观可对应不同隐藏进度；消费者和监督都与 WitnessWAM 不同。 |
| [EvoScene-VLA](https://arxiv.org/abs/2605.21862)；[Mem-World](https://arxiv.org/abs/2606.18960) | action-updated recurrent scene prefix；或 4D wrist-centered surfel memory | 影响下一 action chunk 或 imagined rollout | scene/video/3D consistency teachers | policy 内 scene belief 或 WAM rollout | 已覆盖遮挡后的持久 scene memory；不做 relation witness hazard 或外部 progress commit。 |

### 单篇重叠等级

- POT-VLA：**Level 3 / Medium**。problem 与 consumer 高度重叠，observation 和 supervision 不同。
- CheckVLA：**Level 3 / Medium**。application 与 action-conditioned monitoring 高度重叠，intervention、label、consumer 不同。
- Foresight、PATCH、ConditionNET、ETL：各为 **Level 3 / Medium** 的部分机制重叠。
- 未发现 Level 1/2 的单篇 exact duplicate。

### 组合重叠

最强组合反方是：

`POT-VLA 的 relation/uncertain/boundary progress gate`

`+ CheckVLA/Foresight/PATCH 的 action-chunk-conditioned temporal monitoring`

`+ LTL3/ABRV 的 inconclusive-until-observable semantics`

`+ 标准 interval-censored survival objective`。

该组合不逐字等同于 WitnessWAM，但从现有机制到 READY 方案的工程路径短且自然。剩余贡献主要是 simulator compiler 和显式 opportunity label，而不是新的控制、推理或观测原理。

## 4. 不可约的剩余 delta

唯一可以诚实保留的 delta 必须同时包含：

1. **自然 matched relation-truth aliases：** 当前 RGB/proprio 相同或不可分，但目标关系真值不同；
2. **同一 policy-supported、不可修改 suffix：** 两个别名执行相同普通五步 π0.5 prefix；
3. **first relation-discriminating passive opportunity：** 标注的不是对象可见，而是关系真假第一次超过注册噪声门限、可被 sensor 区分的时机，并允许 censor；
4. **timing 与 evidence likelihood 分离：** hazard 不直接宣告 predicate truth；
5. **外部 relation-memory consumer：** opportunity 前 `PENDING`，证据只暂存，边界原子提交；
6. **必须战胜 action-conditioned visibility 与 full-history boundary verifier。**

这个联合 delta 没有被已核验单篇工作完整覆盖，但它的独立方法含量有限：matched aliases 是数据设计，interval-censored hazard 是标准统计工具，`PENDING` 是经典 monitor 语义，边界 consumer 已被 POT-VLA 类系统占据。新意集中在“为被动关系证据机会编译显式监督”。

## 5. 最强致命反对意见

> `tau_protocol` 不是新发现的物理事件，而是由 privileged relation geometry、visibility、projected separation、sensor-noise threshold 与 two-frame persistence 共同定义的规则交叉点。因为 WitnessWAM 与完整历史 verifier 在同一五步边界、使用同一实际轨迹、更新同一 FSM，显式 `tau` 不增加信息集或行动选择；它只是告诉模型应注意哪一帧。POMDP/三值 runtime monitoring、POT-VLA 的 uncertain predicate gate、以及 CheckVLA/Foresight/PATCH 的 action-conditioned temporal monitoring 已覆盖原则性组成。因此，该工作更像“手工 opportunity 标签辅助的 temporal-attention supervision”，而不是新的 WAM 或执行验证机制。

这条反对意见即使最终实验胜过 full-history verifier 也不会完全消失：实验最多证明这种监督是有效 inductive bias；不会自动把它提升为新的 observability 原理。若 full-history verifier 持平，方法 claim 则被 proposal 自己的 kill gate 完整否定。

另一个严重问题是 protocol-dependence：`tau_protocol` 随相机、suffix、关系阈值、噪声模型和 persistence 规则变化。它不是 predicate 的固有属性，也不是 Bayes-optimal distinguishability。论文若把它写成“真实 earliest witness”而非“预注册 protocol 下的 opportunity label”，主张会越界。

## 6. Naturalness 判断

**7.8 / 10。** 问题动机自然，且冻结动作、相同边界、强 history baseline、无人工 latency 优势都是很好的设计。扣分来自研究对象的工程化：固定五步、command-only envelope、family-specific 几何/可见性/分离阈值与 two-frame persistence 共同制造 `tau_protocol`。方法需要大量合同和筛选规则才能形成干净监督，因此不像一个自然出现、可跨任务直接迁移的新 verification primitive。

## 7. Claim ceiling

如果未来只把它作为一个已知主线中的机制 ablation，最高可声称：

> 在预注册、关系保持的五步模拟 continuation contract 内，显式 earliest relation-opportunity supervision 是外部 relation-memory verification 的一种有效归纳偏置；它在相同动作和边界消费者下，降低了 fixed-time、visibility-only 与 capacity-matched buffered-history verification 的 FSM 错误。

不得声称：

- 新的部分可观测性或 monitorability 原理；
- 通用三值 runtime monitor；
- 新 WAM 范式或通用 VLA execution-verification 框架；
- 对关系物理真值的认证；
- 对未建模相机、真实域偏移或任意 horizon 的保证；
- 改善 π0.5 内部记忆、动作生成或恢复策略。

## 8. 严格评分与判定

| 维度 | 判断 |
|---|---|
| 问题重要性 | 高：直接对应长时任务错误完成与错误回滚 |
| 单篇 exact duplicate | 未发现 |
| 机制不可约性 | 中低：核心是显式 opportunity supervision，其他部件均有强先例 |
| 与最强组合的距离 | 近：relation gate + action-conditioned monitoring + 三值 monitor + survival objective |
| 方法自然性 | 中上，但 protocol 工程依赖明显 |
| Reviewer-defensibility | 不足以稳定守住 `>7.0` |
| **Novelty** | **6.9 / 10** |
| **Verdict** | **FAIL** |

## 9. 实验授权

按本轮明确规则，novelty `<=7.0` 必须立即停止，因此：

- **不授权 non-GPU compiler/oracle E0；**
- **不授权 frozen-feature 小实验；**
- **不授权 GPU 训练或真实机器人实验。**

该方案可以保留为未来其他主方法中的验证/监督 ablation，但不应以当前 exact claim 独立推进成主论文。若继续寻找方向，必须先引入一个会改变信息、决策或可证明能力的不可约机制，而不能只继续细化 `tau_protocol` 或增加 baseline。

## 10. 检索完整性说明

审查使用截至 2026-08-31 可访问的 primary sources，并按 observation / intervention / supervision / consumer 四轴核验。搜索包含三组独立 query：earliest/passive visual witness、VLA/WAM progress-memory verification、interval-censored/action-conditioned observability。项目 paper-search 的 arXiv full-text connector 在本轮多次出现 SSL EOF，Semantic Scholar 出现 429；因此关键论文均回退到官方 arXiv HTML 或作者/出版社 primary page 深读。Fresh reviewer 提出的 POT-VLA、Foresight 和 PATCH 均由主审再次核验后纳入结论。

“未发现 exact duplicate”仅表示已检索 primary corpus 中未找到完整单篇碰撞，不等于证明不存在先行工作；本判定也没有依赖该否定性结论，而是基于强组合重叠与剩余 delta 的机制含量给出 FAIL。
