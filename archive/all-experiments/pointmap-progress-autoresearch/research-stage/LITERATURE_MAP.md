# Focused Literature Map：PointMap × Correctable Progress Belief

**Search date:** 2026-08-30  
**Scope:** 2025–2026 VLA/WAM object address、3D/4D geometry、persistent memory、execution verification、false completion 与 recovery。  
**Search queries:** object-addressable WAM；action-updated scene belief；PointMap robot action；persistent 3D object token predicate verification；WAM execution verification；false completion VLA；event-aware world model；revisable execution state。

## Evidence table

| ID | Work | Already established | Boundary for this run |
|---|---|---|---|
| P1 | [OA-WAM](https://arxiv.org/abs/2605.06481) | persistent object address/content slots；object binding；joint next-slot prediction and 16-step action generation | 不能把 object address 或 object-slot world head 当创新；未直接研究几何证据对持久关系的撤销 |
| P2 | [EvoScene-VLA](https://arxiv.org/abs/2605.21862) | recurrent action-updated scene prior；new observation corrects prior；training uses frozen depth/3D teachers | 不能把 action-updated/correctable scene belief 当创新；其几何 teacher 在部署时移除，未把 metric predicate evidence 作为显式 runtime veto |
| P3 | [PointAction](https://arxiv.org/abs/2606.03943) | jointly predicts future RGB and dynamic 3D pointmaps；point dynamics decode to actions | 不能把 PointMap 作为 video–action interface 当创新；未建立长期 relation belief 的精确撤销命题 |
| P4 | [X-WAM](https://arxiv.org/abs/2604.26694) | multi-view RGB-D future、state/action joint modeling | 完整 RGB-D WAM 已拥挤且计算重，不是本轮目标 |
| P5 | [WAM4D](https://arxiv.org/abs/2606.14048) | training-time future-depth register supervision；inference removes geometry branch | 仅加 depth auxiliary/register 不新；本轮必须证明 runtime geometry changes decisions |
| P6 | [Mem-World](https://arxiv.org/abs/2606.18960) | action-conditioned 4D surfel memory for persistent world rollouts；policy evaluation/improvement | geometry-aware memory retrieval 已有；本轮不能只声称“3D memory 更持久” |
| P7 | [CheckVLA](https://arxiv.org/abs/2607.26789) | action-conditioned execution verification、conformal intervention、repair and keyframe progress evidence | “WAM 发现偏差后纠错”已占；剩余问题是对象级 metric relation evidence 是否带来可归因的增量 |
| P8 | [ReViP](https://arxiv.org/abs/2601.16667) | false-completion diagnosis；LIBERO Object-Drop 等受控扰动；vision–proprioception rebalance | false-completion benchmark/视觉重新检查不新；需对比它代表的 RGB/task-stage observer |
| P9 | [HELM](https://arxiv.org/abs/2604.18791) | episodic memory、learned verifier、rollback/replan；LIBERO-Recovery | memory–verification–recovery 系统组合已占；不能以模块堆叠作贡献 |
| P10 | [EA-WM](https://arxiv.org/abs/2606.13053) | task-spec grounded predicate/event prediction and verification over feature dynamics | “event-aware relational WAM”高度重叠；只剩 metric object-relative geometry 对 invalidation 的 necessity |
| P11 | [EventVLA](https://arxiv.org/abs/2606.20092) | sparse visual evidence memory for long-horizon non-Markovian tasks | 视觉事件记忆不是空白 |
| P12 | [ChainVLA](https://arxiv.org/abs/2608.02326) | joint and revisable execution state with progress context and motion tail | “revisable progress state”不是空白；本轮需证明显式 geometry veto 不可被隐式 working state 替代 |
| P13 | [POT-VLA](https://arxiv.org/abs/2607.18016) | persistent role-indexed 3D object records from RGB-D；same records condition action and geometric predicate checks | **最直接碰撞**：broad persistent-3D-object + predicate verification claim 基本被覆盖；application/robot difference 不足以构成 novelty |

## Synthesis

### What is fully occupied

1. RGB WAM 加 Depth/PointMap auxiliary supervision。
2. 以 PointMap 作为动作接口或从 3D future 解码动作。
3. object address + persistent object record。
4. long-horizon memory + verifier + rollback/replan。
5. task predicate/event prediction。
6. persistent 3D object state + geometric predicate checks。

### Remaining empirical question

未被上述摘要与已核查方法明确回答的，是一个更窄、可被否证的问题：

> 当持久 progress belief 已写入某个对象关系，且该关系随后因动作或外部扰动失效时，显式的 **action-conditioned object-relative metric geometry transition** 是否比 RGB/event memory、当前帧 direct predicate classifier 与 deterministic 3D predicate check 更好地判断“应该撤销哪一个关系、撤销后采取什么恢复决策”？

这里“哪一个关系的精确撤销”与“是否发生了某种失败”不同；但它仍可能被 reviewer 视为 POT-VLA + CheckVLA/EA-WM 的自然组合，所以 novelty 状态只能是 **high-overlap / unproven**。

## Evidence gaps and experiment consequences

- 先做 oracle headroom，不能先训练大 WAM。
- 必须包含 direct 3D predicate baseline；否则相对 POT-VLA 无法解释 WAM necessity。
- 必须包含 RGB/task-stage observer；否则相对 ReViP/HELM 无法解释 PointMap necessity。
- 必须包含 action-shuffled/no-action ablation；否则相对静态 geometry checker 无法解释 action conditioning。
- 必须按 object/relation 报告精确 retraction，不只报告二分类 failure detection。
- 必须有 geometry-negative control，排除一般容量或正则化收益。
- 只有 closed-loop decision/recovery 改善才能支持控制 claim；PointMap/pose RMSE 不能单独支持。

## Search blind spots

- 多数 2026 工作仍为最新 arXiv preprint；未必完成同行评审。
- 没有远程下载新代码；方法细节主要通过官方 arXiv 页面与本地已保存的论文/报告核对。
- POT-VLA、EA-WM、ChainVLA 非常新，未发现公开复现资产；“未发现更近工作”不等于不存在。
- 当前服务器没有本地 π0.5-LIBERO finetuned checkpoint；首轮 StarVLA policy-conditioned pilot 不直接证明 π0.5-specific gain。

## Gate verdict

**Evidence-map gate: WARN.** 问题重要且可实验，但 broad method novelty 已被 P7/P10/P13 严重包围。允许进入 idea/pilot 的理由是进行低成本 falsification；在 direct-predicate 与 RGB verifier 未被击败前，不得宣称新 WAM 方法成立。

