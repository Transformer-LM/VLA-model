# Idea Report：GeoRetract

**Date:** 2026-08-30  
**Decision status:** selected for falsification pilot, not accepted as novel paper claim

## One-sentence idea

**GeoRetract** 使用对象可寻址的稀疏 PointMap 与对象相对几何，学习执行 action chunk 后关系如何变化；它不生成完整 Depth 视频，而把新的几何证据与持久 progress belief 对齐，在 inside/on/grasp/open 关系失效时精确撤销对应进度并触发继续、重新观察或恢复。

## Why this idea exists

普通长期 memory 容易把“曾经成立”误写成“仍然成立”。RGB-only verifier 可以检测明显外观变化，但在相似对象、相机变化、遮挡和共运动中难以稳定判断是哪一个关系失效。完整 RGB-D WAM 成本高，而且已有大量重叠工作。需要先验证更小的问题：对象相对 metric geometry 是否真的改变进度决策。

## Minimal state and update

\[
b_t(i,j)=\{q_i,q_j,p(r_{ij}),u_{ij},e_{ij}\}
\]

- \(q_i,q_j\)：语言绑定的 persistent object addresses；
- \(r_{ij}\)：inside/on/grasp/open 等任务关系；
- \(u_{ij}\)：关系不确定性；
- \(e_{ij}\)：支持当前 belief 的观测/动作证据。

执行动作块 \(a_t\) 后，几何模型预测：

\[
p_\theta(\Delta g_{ij},\Delta r_{ij}\mid P_t^i,P_t^j,a_t,b_t),
\]

再与新观测 PointMap \(P_{t+1}\) 比较，输出 established / preserved / invalidated / unobservable。只有 invalidated 撤销进度；unobservable 触发重观察而非盲目回滚。

## What is new trainable code

最多两个小组件：

1. sparse PointMap/object-relative encoder；
2. action-conditioned relation-transition head。

VLA、RGB encoder、segment/depth teacher 均冻结或使用 simulator truth。首轮不训练 video diffusion、对象检测器、planner 或 policy。

## Nearest-work collision

Broad claim 与 POT-VLA、EA-WM、CheckVLA、EvoScene-VLA、ChainVLA 高度重叠。可检验的剩余 delta 不是“3D object memory”，而是：

> 在 persistent relation 被写入后，action-conditioned metric transition 是否比静态 3D predicate、RGB verifier 和隐式 progress memory 更可靠地执行 **typed relation retraction**，尤其在 co-motion、camera shift 与 partial observability 下。

如果 direct current-geometry predicate checker 持平，则 GeoRetract 的 WAM 部分没有必要；应把结果降级为 3D verifier 工程结论。

## Causal comparisons

1. **Memory-only:** 关系一旦写入便保持，直到任务结束。
2. **RGB verifier:** 当前/前后 RGB + memory + action。
3. **Direct geometry predicate:** 当前对象相对 PointMap，不预测 transition。
4. **GeoRetract:** 前后 PointMap + prior relation + executed action。
5. **No-action ablation:** 打乱或删除 action chunk。
6. **No-address ablation:** 对象 slot permutation / pooled geometry。
7. **GT relation oracle:** simulator predicate upper bound。

所有 learned variants 匹配参数、数据、优化步数和 latency report。

## Experiment ladder

### M0 — simulator capability

确认 LIBERO 可以从同一状态输出 RGB、depth、instance segmentation、camera matrix、object body pose 与 relation ground truth；确认可保存/恢复 state，并能在个人目录生成扰动样本。

### M1 — oracle decision headroom

在 StarVLA 成功完成后注入 Object-Drop、Object-Remove、Stack-Collapse 或 Relation-Swap。比较：

- memory-only controller 停止；
- GT geometry oracle 撤销 progress 并重新调用同一冻结 policy。

主要指标：post-perturbation final success、recovery success、false completion。若 oracle 也无法恢复，停止 learned verifier。

### M2 — representation necessity

收集可见失效、共运动保持、camera shift、遮挡/不可观察与 geometry-negative control。训练 matched RGB、direct geometry、GeoRetract。主要指标：

- typed relation state macro-F1；
- invalidation recall at fixed false-retraction rate；
- Brier/ECE 与 risk–coverage；
- decision error: stop / continue / reobserve / recover；
- object/relation-specific retraction precision。

### M3 — closed-loop learned pilot

只有 M2 中 GeoRetract 明显超过 direct geometry 与 RGB 才运行。把 learned gate 接到冻结 StarVLA，使用独立 seeds 与 perturbation placements，测 final success、recovery、错误回滚、停滞和 latency。

## Preregistered stop rules

- M1 oracle recovery gain < 5 percentage points，或被恢复 policy 的成功率 < 20%：停止。
- M2 GeoRetract 相对 best matched baseline 的 invalidation recall 提升 < 5 points 且 decision error 相对下降 < 10%：WAM necessity 失败。
- direct geometry 与 GeoRetract 差异在 CI 内：停止 action-conditioned WAM claim。
- gain 只存在于 simulator instance segmentation/GT pose：不能推广 learned PointMap。
- geometry-negative control 同幅获益：判为容量/regularization confound。
- PointMap geometry 指标改善但 M3 final success 不升：控制 claim 失败。

## Resource estimate

- M0/M1：约 0.5–4 GPUh，主要为 StarVLA inference；可先用 GPU 2。
- M2：小模型三种子，预计 2–8 GPUh，可用 GPU 2/3。
- M3：预计 4–16 GPUh，需 M2 通过才启动。
- 总 pilot 不超过 32 GPUh；无真实机器人、无远程下载。

