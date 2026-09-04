# WAM Route Card：PointMap 几何进度信念

**Date:** 2026-08-30  
**Status:** selected idea / pre-experiment contract

## Falsifiable question

在长时操作中，已经建立的对象关系随后因滑落、碰撞、移出、坍塌或遮挡而失效。相较 RGB-only memory、proprio/action-only memory 与匹配容量的直接 relation classifier，是否只有把对象可寻址的 PointMap/对象相对几何作为动作条件证据写入可撤销 progress belief，才能减少 false completion 并改善恢复决策？

## WAM taxonomy

- **Representation:** task-centric structured 3D latent；稀疏对象 PointMap、相对位姿、clearance 与关系概率，不生成完整 Depth 视频。
- **Observation:** 当前 RGB/RGB-D、历史对象地址、执行 action chunk、语言目标与 proprioception。
- **Prediction target:** `p(Δg, Δr | b_t, a_chunk)`，其中 `g` 是对象/容器/末端相对几何，`r` 是 `inside/on/grasp/open` 的建立、保持与失效。
- **Control use:** execution-time progress verification、belief invalidation、继续/停止/重新观察/恢复的决策；首版不做候选动作大规模 MPC。
- **Policy relation:** 冻结 VLA；先用已安装 StarVLA/LIBERO 形成 policy-conditioned pilot，通过后再迁移到 π0.5。
- **World-model update:** 离线训练、部署时冻结；belief state 在线递推但不在线改参数。
- **Evaluation level:** model-level relation calibration，decision-level false-completion/invalidation，environment-level recovery/closed-loop success。

## Closest-work boundary

- OA-WAM 已覆盖 persistent object address，但不以候选/执行动作后的几何证据撤销长期关系。
- EvoScene-VLA 与 ChainVLA 已覆盖可修正的跨 chunk scene/progress state；仅“加长期 memory”不新。
- PointAction、X-WAM、WAM4D、POT-VLA 已覆盖 3D/Depth/PointMap 对控制或 predicate verification；仅“RGB 加 PointMap”不新。
- CheckVLA、HELM 已覆盖动作条件验证、rollback/replan；仅“检测后恢复”不新。
- EA-WM 已覆盖 task-grounded predicate/event rollout；仅“关系事件 WAM”不新。
- ReViP 已覆盖 LIBERO false-completion 与 Object-Drop；仅“做 false-completion benchmark”不新。

因此，当前只保留一个窄命题：**动作条件的对象相对 metric geometry 是否为持久关系的精确撤销提供 RGB/event memory 无法替代的增量证据。** 这仍属高重叠、待实验裁决命题，而不是已确认的新方法。

## Gates

1. Oracle geometry 不改善 false-completion/recovery：立即停止。
2. PointMap 只改善 pose/depth 误差而不改变决策：停止。
3. 匹配容量 RGB 或直接 relation classifier 持平：WAM/PointMap necessity claim 失败。
4. 去掉 action conditioning 或 object address 后不降：收缩对应贡献。
5. geometry-negative control 也同幅提升：怀疑容量/数据混杂。

## Open implementation choices

- LIBERO 中可可靠复现的关系与扰动任务子集。
- simulator instance segmentation 生成对象 PointMap，或使用 object pose 构造 oracle sparse geometry。
- learned head 是 PointNet/Set Transformer 还是更小的统计量 MLP；由 matched-capacity pilot 决定。
- π0.5 暂无本地 LIBERO finetuned checkpoint，首轮使用现有 StarVLA；后续迁移不影响 representation-level gate。

## Constraints

远程只使用个人目录；无远程下载；优先 GPU 2/3；本轮真实机器人 trials 为 0；pilot 上限 32 GPUh，总计 400 GPUh。
