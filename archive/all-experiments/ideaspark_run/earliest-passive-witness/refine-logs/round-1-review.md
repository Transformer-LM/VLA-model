# WitnessWAM v0 第 1 轮严格方法评审

**评审角色：** research-refine senior reviewer  
**日期：** 2026-08-31  
**CALIBRATION:** none  
**Verdict:** **REVISE**

## 结论先行

WitnessWAM 保留了正确的问题锚点，而且“不要在证据原则上尚不可见时强制做二元进度判断”是自然、重要、适合 WAM 的问题。当前 dominant contribution 也基本聚焦：用 matched hidden-state twins 和 policy-supported passive continuation，监督一个 protocol-conditional first-witness time，再让该时机约束 progress commit。

但 v0 尚未形成可识别且可实现的单一统计对象。最严重的三处错位是：

1. `matched twin` 目前只是传感器近似匹配，并未保证谓词之外的物理状态和模拟器隐变量匹配；对 `grasped`、`supported_by` 这类由接触几何和动力学派生的谓词，甚至不存在一个可独立翻转的“truth bit”。
2. M3 定义的是一个 pair-level distinguishability time `tau*`，M4 却拟合 `lambda+` 与 `lambda-` 两个 competing risks；目前没有两个带 cause mark 的 event-time 标签，标准 competing-risk likelihood 因而没有对应的观测数据生成过程。
3. “same suffix”只在冻结 π0.5 从共同当前观测生成、并实际执行的当前短 action chunk 内具有部署语义；超过 deployed `h_exec=5` 后，π0.5 会根据已分叉的观测重新规划。长 open-loop suffix 与真实 receding-horizon policy 不是同一 estimand。

此外，`PENDING` 目前可能退化为“可见性 gate + 普通 verifier + abstention”。除非 suffix/action conditioning 在相同当前观测下真正改变 witness schedule，并在相同等待预算下优于 capacity-matched visibility gate，否则 WAM 和 observability-hazard 机制都不是必要的。

## 评分

| 维度 | 分数 /10 | 评语 |
|---|---:|---|
| Problem | **9.0** | 直接针对遮挡/别名状态下的过早完成、错误回滚和进度记忆污染；没有漂移到 generic recovery 或 WAM reranking。 |
| Novel mechanism | **7.4** | twin + same passive suffix + first-witness censoring + commit semantics 是聚焦组合，但若 action conditioning 不必要，就退化为 POMDP observability、visibility gating 与三值 runtime monitoring 的机器人实例。 |
| Causal identifiability | **5.2** | twin 的“只差谓词”不可由当前匹配测试保证；`tau*` 依赖标签器、窗口、特征和 nuisance 分布；M3/M4 event definition 不一致。 |
| Data producer | **5.5** | 说明了 accepted-pair 条件，但没有 family-specific state edit、完整 clone contract、有效样本独立单位、acceptance yield 或 sequential-testing 控制。 |
| Implementability | **5.7** | oracle compiler 可做；但标准 π0.5 不是 WAM、无 action-support density、部署只知当前短 chunk，PointMap 依赖的 mask/depth 和 progress-memory 接口都未落地。 |
| Evaluation | **6.6** | kill gates 和强 baseline 方向正确，但 ambiguity ceiling、matched pending budget、fixed-time baseline、`tau*` ground truth 与 closed-loop integration 均未冻结。 |
| Claim honesty | **8.5** | 明确承认 policy/sensor/suffix conditional、right-censoring 和 PointMap 证据边界；仍需把“earliest”限定为 frozen protocol-relative，而非原则上的最早证据。 |

**OVERALL SCORE: 6.8 / 10**（七维等权；用户未指定其他权重）  
**Verdict: REVISE**（按规则，overall < 9 不能 READY）

## GAP

从 v0 到可审的核心缺口不是更多实验或更大 WAM，而是冻结一个一致的数据生成与统计 estimand：**common-parent twin 在当前可执行 π0.5 chunk 下，首次达到预注册、独立 sensor-test 可分条件的 protocol-relative opportunity time**。当前 proposal 同时在讲“谓词造成的未来差异”“两假设各自的证据 hazard”“visibility opportunity”和“在线 likelihood update”，但它们没有共享同一套标签、censoring 与部署动作语义。若不先统一，模型可以在训练指标上成功，却无法说明它学到的是被动 witness timing，而不是 compiler artifact、可见性或普通 progress classification。

## Problem Anchor 与 drift

**Anchor preserved。** 方法仍解决长时 VLA 中“证据尚未出现却必须做 progress 决策”的核心痛点。

潜在 drift 是把研究问题从“何时可以被动验证”改成“学习一个更好的 PointMap/WAM dynamics model”。PointMap 只能是表示选项，不能成为平行贡献。另一个 drift 是把 `PENDING` 包装成 recovery；当前没有 recovery 机制，也不应在本轮增加。

## Reading-robust blockers

### B1. Twin 不是真正 causal match（CRITICAL）

“当前 RGB/proprio 接近且 time-zero classifier 不可分”只说明某个有限判别器没有发现差异，不能证明两条状态只差谓词。后续 witness 可能来自对象速度、接触 solver warm-start、约束 bit、微小几何穿透、控制器内部状态或人工 occlusion，而不是谓词真假。

这对派生谓词尤其严重：

- `grasped(o)` 通常由夹爪几何、接触和持久共运动定义，不能在完全相同物理状态下单独翻转；用 weld/constraint bit 制造 true twin 会形成 simulator artifact。
- `supported_by(o,s)` 的 false twin 往往需要不同间隙、速度或接触状态；这些本身会决定后续下落。
- `inside(o,c)` 和 drawer state 可以依赖自然遮挡形成 alias pair，但匹配的是观测分布，不是“除谓词外完全相同”的状态。

因此可识别的主张只能是 **common-parent compiled alias pair 的条件可分性**，而不是谓词的独立 causal effect。每个 predicate family 必须给出允许改变的最小状态变量、必须锁定的非后代状态、settling/velocity 条件以及被禁止的 simulator-only latent toggle。否则 reviewer 无法排除 compiler fingerprint。

### B2. `tau*` 是标签协议的输出，当前存在 circularity 与 earliest-selection bias（CRITICAL）

`tau*` 同时要求 privileged opportunity 和 held-out feature separability。即使 cross-fitting，也只是避免同一样本直接拟合；它没有消除以下依赖：固定 encoder、classifier class、窗口长度、nuisance replica 分布、separability threshold 与每帧重复检验都会改变 `tau*`。

“earliest”在跨多个未来窗口选第一次过阈值时会系统性提前，除非预注册 sequential error control 或要求连续若干窗口成立。若后续 evaluation 仍使用同一 feature family 或 labeler，模型可能只是复现标签器。

必须把 claim 改为 **在冻结 sensor/label protocol 下的 earliest accepted witness opportunity**。标签器、region/margin 规则、窗口、α 或 FDR 控制、持续性规则、nuisance 分布和 cross-fit group 必须在模型训练前冻结；hazard 模型不得共享或更新标签器参数。

### B3. M3 的一个 `tau*` 无法识别 M4 的两个 competing risks（CRITICAL）

M3 为 twin pair 定义“两个未来观测分布首次可分”的一个事件时间。它没有给每个样本产生 mutually exclusive 的 `+ witness` / `− witness` cause mark，也未定义两个不同的 `tau+*`、`tau-*`。因此 `lambda+` 和 `lambda-` 的 competing-risk likelihood 没有完整监督对象。

而且 positive-supporting 与 negative-supporting evidence 可能同一窗口同时出现，或只是同一 likelihood ratio 的两个方向，并不自然构成 competing risks。安全终止、任务结束和 suffix 结束还是 hypothesis-dependent informative censoring，不能直接当普通 right-censoring。

最小局部修复不是增加 cause head，而是二选一并冻结：

- 一个 pair-level **opportunity hazard**，到机会后用两个 hypothesis-conditional feature likelihood 做 Bayes update；或
- 明确定义两个 branch-specific marked event times、cause labels与 censoring process，并证明它们与 runtime update 一致。

前者更小、更贴合 M3，也更不容易造成贡献膨胀。

### B4. Same suffix 的物理语义只在一个执行块内成立（CRITICAL）

在共同当前观测上固定随机种子查询 π0.5，可以得到同一个 policy-sampled chunk；把同一 low-level prefix 执行在两 twins 上，是清晰的有限时域 intervention。但 OpenPI 的官方 LIBERO 路径在每个动作块只执行前 `replan_steps=5` 后重规划，并只返回 action chunks；它不提供动作 density 或“距 support 多近”的数值。因此：

- “expert suffix close to π0.5 support”目前不可操作；
- `H>5` 的固定 open-loop suffix 不是 deployed π0.5 normally executes next；
- 若每五步闭环重规划，两 twin 的观测已不同，动作也会不同，便不再是 same suffix；
- 如果用 recorded expert suffix，false twin 上的安全性和 policy support 不能由 true twin 保证。

首轮必须选择明确 estimand：用共同当前观测、共同 policy seed 生成的**当前 5-step executed prefix**，到边界即 censor/滚动重估；或改称固定 open-loop intervention，不再声称 closed-loop policy conditional。两者不能混写。官方接口证据见 [OpenPI LIBERO client](https://github.com/Physical-Intelligence/openpi/blob/main/examples/libero/main.py)。

### B5. `PENDING` 尚未证明不是 visibility gate（IMPORTANT，机制存亡项）

M4 同时预测 object region、sensor channel 和 opportunity；M5 只在机会 mass 过阈值后运行普通 likelihood update。最容易的解是学习“目标何时无遮挡”，这就是 visibility gate。若当前帧/历史加 region visibility 足以决定等待时机，action-conditioned WAM 没有机制必要性。

必须预注册一个同容量 visibility-only three-state gate，并在**相同当前 twin、至少两个普通 policy suffix**上验证 suffix 改变会稳定改变 witness ordering；action-suffix shuffle 应破坏该 ordering。若 suffix-free gate 在相同 pending/coverage/delay 预算下匹配结果，应删除 WAM/hazard 主张，而不是增加模块。

### B6. 标准 π0.5 没有 proposal 所假定的 progress-memory 接口（CRITICAL for closed-loop claim）

官方 OpenPI LIBERO 输入是双 RGB、EEF/夹爪 state 和 task prompt，输出 action chunk；没有离散 predicate memory 或 `PENDING/commit/retract` API。Proposal 没说明 symbolic state 的消费者是谁、commit 如何改变 subtask transition、retract 如何影响下一次 π0.5 调用。若只是修改 prompt，冻结 π0.5 是否理解新增状态 token 也未知且可能 OOD。

因此 oracle/neural verifier E0 可实现，但“improves long-horizon execution”当前不可实现。必须明确一个外部、非学习的 subtask controller 接口，或限定到一个已有显式 progress memory 的 policy；不能把标准 π0.5 当作已具备该接口。

### B7. PointMap 证据不能外推到 action-conditioned WAM（IMPORTANT）

`CLAIMS_FROM_RESULTS.md` 只支持：360 个受控 LIBERO 样本、simulator instance masks + metric depth 下，38-D two-frame PointMap 对关系事件分类有 headroom。它明确不支持 action-conditioned dynamics、WAM necessity、learned/deployed masks、VLA improvement 或 closed-loop correction。

标准 LIBERO/OpenPI 观测并不提供部署所需的 instance mask 和 metric depth；见 [LIBERO default data config](https://github.com/Lifelong-Robot-Learning/LIBERO/blob/master/libero/configs/data/default.yaml)。所以“predict PointMap latent”必须说明：PointMap 是 privileged teacher target、RGB 预测 target，还是 deployment input。若需要新增 monocular depth + instance association，便增加至少一个未经验证的 trainable subsystem。当前最诚实的路线是把既有结果仅作为 representation headroom，不作为 WAM feasibility evidence，并保留全部 E0 integrity WARN。

## Data producer 审查

当前“每 family 300 accepted twins”不是有效的样本量定义。Nuisance replicas 和相邻 snapshots 不是独立样本；单位必须是 common-parent episode/object/seed lineage。完整 producer 至少要记录：

- common parent 与 family-specific state edit；
- 所有 simulator/controller/RNG state 的 clone hash；
- edit 前后 robot/object pose、velocity、contact、constraint 和渲染 residual；
- time-zero ambiguity test score及置信上界；
- suffix 来源、policy seed、action clipping、五步执行与 safety rejection；
- 每个 family 的 attempted / physically valid / visually matched / time-zero ambiguous / same-prefix-safe / later-distinguishable 数量；
- 所有拒绝原因，且 split 按 parent lineage 而非 replica/frame。

在接触类状态上，仅保存 MuJoCo qpos/qvel 通常不足以保证 controller state、mocap target、actuator state、contact warm-start 与 RNG 完整恢复。Producer 的 duplicate replay 必须先证明同一 snapshot、同一 action 的未来一致性，否则 `tau*` 可能是 restore noise。

## Implementability reality check

| 组件 | 当前状态 | 判断 |
|---|---|---|
| Frozen π0.5 suffix producer | 官方 client 可从双 RGB + state 产生 action chunk并执行前五步 | **可行，但只有当前短 prefix；无 support likelihood。** |
| Arbitrary twin clone/restore | Proposal 未给 controller/RNG/constraint clone contract | **需实现；接触状态高风险。** |
| Matched twin compiler | 有接受条件，无 family-specific causal edit | **尚不可实现为可识别 producer。** |
| First-witness labeler | 有高层双条件，无冻结 feature/statistical protocol | **尚不可复现。** |
| Action-conditioned WAM | 无现成同域 PointMap/object-latent dynamics 接口 | **需新训练；π0.5 不是 WAM。** |
| RGB→PointMap/object region | 既有 E0 使用 GT mask + metric depth | **部署链缺失。** |
| `PENDING` runtime memory | 标准 π0.5 无该接口 | **closed-loop blocker。** |
| 4×A100 | compact WAM/head 资源足够 | **算力不是 blocker。** |

因此现有数据/模型足以做 compiler/oracle feasibility audit，但**不足以直接训练和部署 WitnessWAM v0**。

## 可局部修复项

1. **合并 hazard（CRITICAL）：** 将 M4 简化为单一 opportunity hazard + opportunity-time hypothesis likelihood；除非 producer 明确生成 cause marks，不使用 competing-risk 表述。
2. **缩短 suffix（CRITICAL）：** 初版固定为 π0.5 同观测、同 seed 生成的 deployed 5-step prefix，窗口末端 right-censor；不要混入 expert suffix 或无法度量的 “close to support”。
3. **冻结 label protocol（CRITICAL）：** 独立 encoder/region rule、group cross-fitting、sequential multiplicity correction、连续窗口条件与 censor cause，全部先于模型训练注册。
4. **限定 twin claim（IMPORTANT）：** 改称 common-parent compiled sensor aliases；报告完整 state residual 和 compiler fingerprint controls，不声称“只差谓词”的完美 causal twin。
5. **删除 PointMap 必要性暗示（IMPORTANT）：** PointMap 先作为 privileged/representation upper bound；RGB-only WAM 是否需要它由 necessity comparison 决定。
6. **明确外部 controller（CRITICAL）：** 写清 PENDING/commit/retract 如何控制 subtask advance、repeat 或 abort，以及这是否改变 π0.5 prompt。该接口应为固定规则，不再增加一个 trainable planner。
7. **把 abstention cost 写成选择性风险（IMPORTANT）：** 比较同 coverage、同平均/尾部等待、同 timeout budget，而不是只报 wrong-decision reduction。

## 必须预注册的决策

在任何 compiler E0 前，以下项目必须冻结；否则 reader 可以合理怀疑 researcher degrees of freedom：

1. 三个 predicate family 各自的 truth definition、common-parent edit、禁止编辑的状态变量、physical-stability 条件和人工 occlusion 禁令。
2. Twin matching 的 raw-pixel/geometry/proprio tolerance、固定 time-zero classifier/encoder、group split、ambiguity ceiling及其置信区间判据。
3. 独立样本单位、lineage split、nuisance replica 数、完整 acceptance ledger 与 family-level minimum yield。
4. π0.5 checkpoint、observation transform、sampling seed、action normalization、`h_exec=5`、suffix horizon、clipping 与 safety rejection。
5. Witness opportunity 的 privileged geometry/visibility规则、deployable feature labeler、窗口长度、连续窗口数、sequential α/FDR 与 tie/interval-censor规则。
6. 一个 event time 还是两个 marked event times；对应 likelihood、risk set、cause label 和 informative censor causes。当前 competing-risk 版本不能保持未定义。
7. `PENDING` 的最大步数、fallback、posterior commit/retract threshold、coverage、平均与 P95 delay、timeout budget。
8. Capacity-matched visibility gate、fixed-delay、framewise verifier 与 suffix-free hazard 的输入、参数量和 tuning budget。
9. 证明 action conditioning 的 minimum effect：同状态多 suffix 的 `tau*` ordering、suffix-shuffle degradation 和预注册 kill threshold。
10. PointMap 是 input、teacher target 还是 output；测试时 mask/depth/association的来源；既有 38-D E0 与新 representation 严格隔离。
11. Symbolic state 如何进入外部 task controller/π0.5；若没有真实消费者，则删除 closed-loop improvement claim。
12. 所有 kill rules 的 family aggregation方式；不能用一个易 family 补偿两个失败 family。

## Evaluation focus

不需要扩大 benchmark。核心证据只需三个相互依赖的 block：

1. **Compiler validity:** common-parent replay、time-zero ambiguity、later passive distinguishability、acceptance/yield、无 compiler fingerprint。
2. **Mechanism necessity:** suffix-conditioned opportunity model相对 visibility-only/suffix-free/fixed-delay baseline，在 matched selective-risk/coverage/delay budget 下有效；suffix shuffle 必须破坏 timing。
3. **Closed-loop relevance:** 只有在显式 progress-memory consumer 上，oracle opportunity gate 和 learned gate分别减少 premature commit/retract 且不以长期 PENDING 换取表面收益。

如果 block 1 不成立，不应训练 WAM；如果 block 2 不成立，方法应收缩为 visibility-aware three-state verifier；如果 block 3 没有明确 integration point，只能主张 offline scheduling/calibration，不能主张 long-horizon execution improvement。

## Simplification opportunities

1. 删除未被标签支持的 dual competing-risk head，保留一个 opportunity hazard 与一个两假设 likelihood update。
2. 首版只覆盖一个 deployed 5-step π0.5 prefix并滚动重估，不引入 expert suffix 或长期开环计划。
3. PointMap 只做 frozen representation/teacher upper bound；不要同时发明 RGB→PointMap、object association 和 WAM dynamics。

## Modernization opportunities

**NONE required.** 当前问题不需要额外 LLM、diffusion head、RL 或 inference-time search。π0.5 的自然作用是提供真实部署 action prefix；WAM 的自然作用是预测 suffix-conditioned observation opportunity。继续加现代模块只会掩盖 identifiability 缺口。

## Drift warning

**NONE at present.** 但若后续把主要工作量转成 PointMap architecture、通用视频生成或 recovery planner，即发生 drift。最小论文必须仍以 protocol-relative passive witness timing 改变 progress commit semantics 为唯一主贡献。

## 最重要的下一轮修复

下一轮不要扩写实验菜单。先统一 M1–M5 的 estimand：给出一个可复现的 common-parent twin compiler；把 suffix 限定为 π0.5 当前部署的五步 chunk；用独立、冻结、带 sequential error control 的 protocol-relative `tau*` 标签；再决定是单 opportunity hazard，还是有真实 cause marks 的 competing risks。最后明确 `PENDING` 的外部 progress-memory consumer。完成这四点后，才有必要评估模型结构。
