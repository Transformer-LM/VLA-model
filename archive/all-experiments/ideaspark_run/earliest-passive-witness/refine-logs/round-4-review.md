# WitnessWAM v3 第 4 轮独立严格复审

**评审角色：** research-refine senior reviewer  
**日期：** 2026-08-31  
**CALIBRATION:** none  
**Verdict:** **REVISE**

## 结论先行

Round 4 已关闭上一轮三个直接 blocker 的大部分：truth-transition 不再被事后静默筛掉，而计入 full denominator 和闭环失败；五步 action queue/prompt 完全 immutable，early belief 只 staged、边界原子生效；action-conditioned visibility hazard 得到同输入、同容量和两个数值胜出门槛；四个 server-side keys、无 replacement、missing rule、physical-command tolerance、单一 IBS 和 per-family lineage bootstrap 都已具体化。

不过尚不能 READY，原因是两个新的、但很小的 reading-robust gaps：

1. **Structural envelope 仍未完全 deployment-valid。** “EEF 到 named object/container/support 的距离非递减”若使用 simulator body pose 或 metric scene geometry，就与 RGB+proprio primary、无 deployable PointMap/depth 的约束冲突。Envelope 必须能仅由 checkpoint EEF/proprio + queued physical commands判定，或明确一个已存在且所有方法共享的 deployable object-pose source；后者当前没有。
2. **Boundary-only action semantics 暴露了一个更小的强 baseline。** 所有方法在 step 0–5 物理轨迹相同，FSM side effect 只在边界发生，那么一个 capacity-matched verifier 可以缓存完整五步 RGB/proprio/action history，并仅在 boundary 做一次 relation decision。它能利用 transient witness，却不需要事先预测 `tau_protocol`。当前 final-frame-only baseline不能替代该 full-history boundary verifier。若它匹配 WitnessWAM，timing hazard 的系统 utility 就只是显式时间监督/缓存策略，而非必要机制。

这两项都是同一 E0 内的局部 contract/baseline 修复，不需要延长 horizon、增加数据族或训练新主模块。

## 同一七维评分

| 维度 | Round 3 | Round 4 | 评语 |
|---|---:|---:|---|
| Problem | 9.4 | **9.5** | 完整保留“证据未出现前不应污染 progress memory”的锚点。 |
| Novel mechanism | 8.6 | **8.5** | 与 visibility baseline 的边界已清楚；但 boundary-history verifier 可能吸收 transient-witness收益，仍需证明 explicit opportunity scheduling 必要。 |
| Causal identifiability | 8.0 | **9.0** | Immutable chunk、staged decision、atomic apply 和 full-denominator violation accounting 基本消除 verifier-induced trajectory confounding。 |
| Data producer | 8.5 | **9.0** | 三个自然 producer、结构 envelope、完整 ledger 与 prefix-attempt accounting 足够具体。 |
| Implementability | 8.2 | **8.5** | Decode-key 和 action command接口已落地；named-body envelope 可能依赖未声明的部署几何。 |
| Evaluation | 8.2 | **8.2** | IBS、lineage bootstrap、visibility baseline都正确；缺 full-history boundary verifier 这一决定性更小系统 baseline。 |
| Claim honesty | 9.4 | **9.5** | Claim ceiling 和所有 stop rules仍然严格。 |

**OVERALL SCORE: 8.9 / 10**（七维等权，与前轮一致）  
**Verdict: REVISE**（overall < 9，且有两个局部 blocker）

## GAP

当前 proposal 与 READY 之间只差“部署可检查”和“机制不可约”两件事：把 continuation envelope 改成不读取 privileged body pose 的 checkpoint-relative command rule；加入一个读取整个固定五步 trace、只在边界决策的 capacity-matched history verifier。前者验证 contract 能真实部署，后者验证 earliest-opportunity hazard 的收益不是普通 temporal evidence aggregation。

## 指定五项核验

### 1. Structural envelope + ≥95% full-denominator audit

**对 privileged future selection 的统计问题已修复，但 envelope 输入仍有部署可得性问题。**

本轮正确地把以下集合先冻结为 pre-prefix denominator：physical validity、replay determinism、time-zero ambiguity、paired-action agreement、safety 和 structural-envelope membership。随后对该完整集合的所有 rollout audit predicate truth；truth transitions 留在 denominator、计为 contract violation 和 closed-loop failure，仅不用于 `tau_protocol` supervision。≥95% gate 对每个 retained family 单独成立，且至少两 family通过。这样不再能通过删除困难未来来抬高 preservation 或 opportunity yield。

因此 Round 3 的“privileged after-the-fact easy subset”选择偏差已实质消除。剩余问题不是 denominator，而是 envelope 本身写成：

- EEF distance from object–container interaction region nondecreasing；
- EEF distance from object and named support nondecreasing。

若这些距离通过 simulator body pose计算，runtime contract仍使用 privileged geometry。Proposal 的 primary部署输入只有 RGB+proprio，且 PointMap/depth明确非部署假设。`named body` 查询本身不等于拥有其 metric pose。

最小修复：把三类 envelope 统一写成 **checkpoint-EEF-relative retreat cone**，只使用部署已知量：

- initial EEF pose/orientation来自 proprio；
- queued denormalized actions累积得到 command-space desired path；
- gripper mode固定；
- translation 对 registered retreat axis 的投影单调非负，横向/旋转幅度和速度有界；
- 不允许 command reversal。

Retreat axis可以作为固定 skill parameter，在 event-producing phase结束时由控制器记录，不需要对象/支撑面的未来或 privileged pose。Truth-preservation audit仍保留≥95%，用来验证这个 pre-rollout rule在每 family 的物理precision。若坚持 body-relative距离，则必须明确其部署来源，并把同一 source提供给所有方法；当前引入新 RGB→geometry模块会造成不必要 sprawl。

还需把 denominator unit写成 **lineage–decode-key attempt** 用于 preservation/opportunity yield，并以 parent lineage bootstrap。当前一条 lineage可能有3–4 valid prefixes；若只按 lineage计数，会不清楚“一个 key transition、三个 key preserve”算一次成功还是四次尝试。所有 keys均进入 attempt denominator正是最干净定义。

### 2. Immutable queue + staged first-accepted belief + atomic apply

**轨迹分叉已消除；但非人为 utility 仍需一个更强 baseline来证明。**

本轮 action-lock语义清晰且自洽：action 1–5、timing、current/next prompt在 chunk开始后不可改变；early verifier只能写带timestamp的 staged belief；first accepted decision在chunk内冻结；FSM memory/advance/retract只在 boundary原子生效。不同 verifier 的 step 0–5 物理轨迹完全相同，因此免费 retry、提前 next-subtask action和 truth-change confounding都不再由 verifier引入。

Transient witness 在 step 2出现、step 5再次遮挡时，scheduler可以缓存它，说明方法不是形式上无用。但由于任何控制或 memory side effect都延迟到 step 5，系统并不需要在 step 2采取动作。一个普通 sequence verifier可缓存全部五步 observation/action history，在step 5一次判断；attention/RNN/temporal pooling都能恢复step 2证据，而无需预测 first opportunity。

当前 `final-boundary-only verifier` 若只看final frame，是偏弱 baseline；它不能回答“timing supervision是否优于完整历史聚合”。必须加入：

> **Capacity-matched full-history boundary verifier**：接收与WitnessWAM相同的initial/current history、完整实际五步RGB/proprio/action trace和object/relation query；不接收`t​​au_protocol`，只在step-5输出relation belief；使用相同encoder capacity、evidence budget和validation tuning。

WitnessWAM必须在相同 unit-cost FSM endpoint、coverage与timeout规则下对它有预注册实质增益，建议≥10% relative、每 retained family 的 lineage-bootstrap CI排除零。若history verifier匹配，honest结论应是“buffered temporal verification suffices”；oracle timing label仍可作为diagnostic，但不能保留 scheduling mechanism claim。

这个 baseline不是新增研究问题，而是当前 action-lock设计后不可回避的最小替代解释。

### 3. Action-conditioned visibility hazard

**对 visibility-only解释而言，它是公平且决定性的 baseline。**

它接收与WitnessWAM相同的RGB、proprio、query、predicate type和exact prefix，encoder容量/hazard head相同，只把target/reference visibility threshold time作为监督；没有pairwise projected separation或predicate truth。这样不会通过剥夺action information人为削弱visibility route。

要求 WitnessWAM 同时在 `tau_protocol` IBS 和 fixed-FSM total error上提升≥10%，且每family CI排除零，是合适的双门槛：前者证明relation-aware opportunity timing更准，后者证明差异进入progress memory utility。如果失败，收缩为action-conditioned visibility scheduling是诚实stop。

它仍不是**全部机制空间**里的最终 decisive baseline，因为full-history boundary verifier解决的是“是否根本需要提前schedule”，不是“schedule是否只预测visibility”。两者回答不同 objection，均为核心最小baseline。

### 4. Exact four keys / no replacement / missing rule / physical command tolerance

**已修复，设计现实。**

- 四个server-side paired flow-decode PRNG keys在rollout前冻结；
- paired aliases使用相同decode noise；
- raw normalized与denormalized clipped commands均缓存；
- agreement在deployment physical command space逐维检查translation、rotation、gripper及environment actuators；
- 至少3/4 keys有效才进入K-prefix necessity analysis；
- missing keys记录且不replacement；
- all four attempts留在yield ledger。

这避免seed shopping，也不需要不存在的policy density。每个canonical prefix对source observation是policy-sampled；对cross-replay alias只声称action agreement，不声称formal support。4×A100下K=4 compute不是风险。

唯一需要在experiment plan冻结的是physical tolerances的数值与source branch平衡随机表；这不是method blocker。

### 5. 单一 IBS 与 lineage bootstrap

**已修复。** Integrated time-dependent Brier score是唯一primary predictive metric，C-index仅diagnostic，消除了metric OR。五步离散event time有ties/censoring，IBS比C-index自然。

不再把2–3个families当统计clusters，而是在每个family内重采样common-parent lineages，并要求每个retained family的CI单独排除零。该独立单位正确。需要在experiment plan冻结censoring weights、time-grid integration与paired model comparison bootstrap，但这些属于正常实现细节。

## 其余完整性判断

### 三类 producer

三者仍是自然的 simulator producers：stable grasp/natural miss、settled inside/rim-outside miss、settled target/adjacent support。禁止weld、hovering、solver transient、camera-only edit与retry，且至少两family必须独立过全部gate，足以避免单一easy event支撑claim。

`grasp-coupled`比两种placement family提供不同的co-motion witness；inside/support更多依赖withdrawal visibility。Action-conditioned visibility baseline已覆盖后一种简化解释。自然性剩余风险属于真实E0 yield，不是proposal blocker。

### Fixed FSM endpoint

Unit-cost composite不使用oracle timing定义错误，且明确允许wrong belief与wrong transition双计为两个不同downstream state；timeout也固定unit cost。Operating point在validation冻结，full curve仅secondary，已经非循环。Oracle schedule不再结构性因“等待到oracle time”在primary endpoint必胜。

需要确保同一boundary-history baseline也遵循first/only boundary decision和相同coverage constraint。除此之外，endpoint定义已足够。

## 剩余 reading-robust blockers

### Q1. Envelope可能读取部署不可得的named-body metric geometry（CRITICAL）

若无现成deployable body pose source，body-relative distance rule违反RGB+proprio primary contract。改成checkpoint-EEF-relative action-space retreat envelope即可，不新增模型。

### Q2. 缺capacity-matched full-history boundary verifier（CRITICAL for mechanism necessity）

在所有side effects延迟到step 5后，缓存完整trace并在boundary一次分类是比hazard更小的自然解。必须证明earliest-opportunity supervision在系统endpoint上超过它，否则timing mechanism不可约性不成立。

## 最小局部修复

1. 将structural envelope改成仅依赖initial EEF proprio、fixed skill retreat axis与queued denormalized commands的action-space rule；truth-preservation仍对complete lineage-key denominator做≥95% audit。
2. 加capacity-matched full-history boundary relation verifier，并要求WitnessWAM在固定FSM endpoint上≥10% relative improvement、每family lineage-bootstrap CI排除零；失败即收缩为buffered temporal verification。
3. 明确preservation/opportunity percentages的统计单位是lineage–key attempts，CI仍按parent lineage resample。

完成这三项后，当前proposal没有明显reading-robust逻辑 blocker；五步yield、95% preservation、visibility与history baselines能否通过属于应由E0决定的真实风险。

## Simplification opportunities

1. 不新增geometry/localizer；用checkpoint-relative command envelope解决deployment contract。
2. 保持single hazard、single IBS、immutable chunk和fixed FSM；不增加multi-chunk或recovery。
3. Full-history verifier仅作为同容量baseline，不形成新组件或平行贡献。

## Modernization opportunities

**NONE.** 当前方法已经自然使用frozen VLA prefix与action-conditioned WAM；缺口是不可约性验证，不是现代模块。

## Drift warning

**NONE.** 若为envelope加入新的RGB→3D geometry stack会造成drift/sprawl；action-space envelope是更小修复。

